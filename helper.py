import logging
import subprocess
import datetime
import asyncio
import os
import requests
import time
from p_bar import progress_bar
from config import LOG
import aiohttp
import tgcrypto
import aiofiles
from pyrogram.types import Message
from pyrogram import Client, filters
import base64
import urllib.parse
import threading
import httpx
import re


async def get_pssh_kid(mpd_url: str, headers: dict = {}, cookies: dict = {}):
    """
    Get pssh, kid from mpd url
    headers: Headers if needed
    """
    pssh = ""
    kid = ""
    for i in range(3):
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(mpd_url, headers=headers, cookies=cookies)
                mpd_res = res.text
        except Exception as e:
            print("Error fetching MPD:", e)
            continue
        try:
            matches = re.finditer("<cenc:pssh>(.*)</cenc:pssh>", mpd_res)
            pssh = next(matches).group(1)
            kid = re.findall(r'default_KID="([\S]+)"', mpd_res)[0].replace("-", "")
        except Exception as e:
            print("Error extracting PSSH or KID:", e)
            continue
        else:
            break
    return pssh, kid


class Penpencil:
    otp_url = "https://api.penpencil.xyz/v1/videos/get-otp?key="

    def __init__(self, token: str):
        #self.token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjAwOTY5OTkuODczLCJkYXRhIjp7Il9pZCI6IjYwY2UxMzU0ZDdlMjNjMDAxMTBkYzU1OCIsInVzZXJuYW1lIjoiOTk2NzI2MzMwMyIsImZpcnN0TmFtZSI6IkRldmFuc2giLCJsYXN0TmFtZSI6IkJoYW51c2hhbGkiLCJvcmdhbml6YXRpb24iOnsiX2lkIjoiNWViMzkzZWU5NWZhYjc0NjhhNzlkMTg5Iiwid2Vic2l0ZSI6InBoeXNpY3N3YWxsYWguY29tIiwibmFtZSI6IlBoeXNpY3N3YWxsYWgifSwiZW1haWwiOiJkZXZhbnNoYmhhbnVzaGFsaTEyQGdtYWlsLmNvbSIsInJvbGVzIjpbIjViMjdiZDk2NTg0MmY5NTBhNzc4YzZlZiJdLCJ0eXBlIjoiVVNFUiJ9LCJpYXQiOjE3MTk0OTIxOTl9.T4p_zzFHmL1FYIh7ZddaytjQuvImofVluswVPF1_GFM"
        self.token = token
        self.headers = {
            "Host": "api.penpencil.xyz",
            "content-type": "application/json",
            "authorization": f"Bearer {self.token}",
            "client-version": "11",
            "user-agent": "Mozilla/5.0 (Linux; Android 10; PACM00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.98 Mobile Safari/537.36",
            "Client-Type": "WEB",
            "accept-encoding": "gzip",
        }

    @staticmethod
    def encode_utf16_hex(input_string: str) -> str:
        hex_string = ''.join(f"{ord(char):04x}" for char in input_string)
        return hex_string

    def get_otp_key(self, kid: str):
        xor_bytes = bytes(
            [
                ord(kid[i]) ^ ord(self.token[i % len(self.token)])
                for i in range(len(kid))
            ]
        )
        f = base64.b64encode(xor_bytes).decode("utf-8")
        print(f"Generated OTP Key: {f}")
        return f

    def get_key(self, otp: str):
        a = base64.b64decode(otp)
        b = len(a)
        c = [int(a[i]) for i in range(b)]
        d = "".join(
            [
                chr(c[j] ^ ord(self.token[j % len(self.token)]))
                for j in range(b)
            ]
        )
        print(f"Decoded Key: {d}")
        return d

    async def get_keys(self, kid: str):
        otp_key = self.get_otp_key(kid)
        encoded_hex = self.encode_utf16_hex(otp_key)
        #print(f"Encoded Hex: {encoded_hex}")

        keys = []
        for i in range(3):
            try:
                async with httpx.AsyncClient(headers=self.headers) as client:
                    otp_url = f"{self.otp_url}{encoded_hex}&isEncoded=true"
                    resp = await client.get(otp_url)
                    otp_dict = resp.json()
            except Exception as e:
                print("Error fetching OTP:", e)
                continue
            try:
                otp = otp_dict["data"]["otp"]
                #print(f"Received OTP: {otp}")
                key = self.get_key(otp)
                keys = f"{kid}:{key}"
            except Exception as e:
                print("Error extracting key:", e)
                continue
            else:
                break
        return keys

    @staticmethod
    async def get_mpd_title(url: str):
        return url

    async def get_mpd_keys_title(self, url: str, keys: list = []):
        mpd_url = await self.get_mpd_title(url)
        if keys:
            return mpd_url
        if mpd_url:
            pssh, kid = await get_pssh_kid(mpd_url)
            print("PSSH:", pssh)
            print("KID:", kid)

            key = await self.get_keys(kid)
            print("Key:", key)
        return mpd_url, key

async def get_drm_keys(url: str, token: str):
    penpencil_instance = Penpencil(token)
    mpd_url, key = await penpencil_instance.get_mpd_keys_title(url)
    return key



#     # Function to download audio asynchronously
# def download_audio(audio_cmd):
#         subprocess.run(audio_cmd, shell=True)
#         print("Audio download done")

#     # Function to download video asynchronously
# def download_vvideo(download_cmd):
#         subprocess.run(download_cmd, shell=True)
#         print("Video download done")


# async def drm_download_video(url, name,cmd, keys):
#     time.sleep(1)
#     print(name)
#     download_cmd = f'yt-dlp {cmd} -k --allow-unplayable-formats --external-downloader aria2c --external-downloader-args "-x 16 -s 16 -k 1M" -o "{name}.mp4"'
#     audio_cmd = f'yt-dlp -k --allow-unplayable-formats -f ba --fixup never {url} --external-downloader aria2c --external-downloader-args "aria2c: -x 16 -s 16 -k 1M" -o "{name}_audio.m4a"'
#     print(download_cmd)
#     logging.info(download_cmd)
#     subprocess.run(audio_cmd, shell=True)
#     print("Audio download done")
#     subprocess.run(download_cmd, shell=True)
#     print("Video download done")

#     # Split keys
#     keys = keys.split(":")
#     if len(keys) != 2:
#         print("Error: Two keys must be provided separated by a colon.")
#         return None

#     key1, key2 = keys

#     try:
#         # Check if the video file exists
#         if os.path.isfile(name):
#             video_file = name
#         elif os.path.isfile(f"{name}.webm"):
#             video_file = f"{name}.webm"
#         else:
#             name_without_extension = os.path.splitext(name)[0]
#             if os.path.isfile(f"{name_without_extension}.mkv"):
#                 video_file = f"{name_without_extension}.mkv"
#             elif os.path.isfile(f"{name_without_extension}.mp4"):
#                 video_file = f"{name_without_extension}.mp4"
#             elif os.path.isfile(f"{name_without_extension}.mp4.webm"):
#                 video_file = f"{name_without_extension}.mp4.webm"
#             else:
#                 video_file = None

#         # Run the audio download command
#         audio_file = f"{name}_audio.m4a" if os.path.isfile(f"{name}_audio.m4a") else None

#         # Decrypt video with either key1 or key2
#         decrypted_video_file = f"decrypted_{os.path.basename(video_file)}"
#         decrypted_audio_file = f"decrypted_{os.path.basename(audio_file)}"

#         if not decrypted_video_file.endswith(('.mkv', '.mp4', '.webm')):
#             decrypted_video_file += ".mp4"
#         if not decrypted_audio_file.endswith('.m4a'):
#             decrypted_audio_file += ".m4a"

#         video_decryption_successful = False
#         for video_key in [key2, key1]:
#             decrypt_video_cmd = f'ffmpeg -decryption_key {video_key} -i "{video_file}" -c:v copy "{decrypted_video_file}"'
#             decrypt_video_process = subprocess.run(decrypt_video_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#             if decrypt_video_process.returncode == 0:
#                 print(f"Video decryption successful with key {video_key}.")
#                 video_decryption_successful = True
#                 successful_video_key = video_key
#                 break
#             else:
#                 print(f"Video decryption failed with key {video_key}: {decrypt_video_process.stderr.decode()}")

#         if not video_decryption_successful:
#             print("Video decryption failed with both keys.")
#             return video_file, audio_file

#         # Decrypt audio with the other key
#         audio_decryption_successful = False
#         for audio_key in [key2, key1]:
#             #if audio_key != successful_video_key:
#                 decrypt_audio_cmd = f'ffmpeg -decryption_key {audio_key} -i "{audio_file}" -c:a copy "{decrypted_audio_file}"'
#                 print(decrypt_audio_cmd)
#                 decrypt_audio_process = subprocess.run(decrypt_audio_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#                 if decrypt_audio_process.returncode == 0:
#                     print(f"Audio decryption successful with key {audio_key}.")
#                     audio_decryption_successful = True
#                     break
#                 else:
#                     print(f"Audio decryption failed with key {audio_key}: {decrypt_audio_process.stderr.decode()}")

#         if not audio_decryption_successful:
#             print("Audio decryption failed with both keys.")
#             return video_file, audio_file

#         # Merge decrypted video and audio
#         output_file = f"{os.path.splitext(decrypted_video_file)[0]}.mkv"
#         merge_cmd = f'ffmpeg -i "{decrypted_video_file}" -i "{decrypted_audio_file}" -c copy -threads 4 "{output_file}"'
#         merge_process = subprocess.run(merge_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
#         if merge_process.returncode == 0:
#             # Delete intermediate files
#             os.remove(video_file)
#             os.remove(audio_file)
#             os.remove(decrypted_video_file)
#             os.remove(decrypted_audio_file)
#             return output_file
#         else:
#             print(f"Merging failed: {merge_process.stderr.decode()}")
#             return decrypted_video_file, decrypted_audio_file

#     except FileNotFoundError as exc:
#         print(f"File not found: {exc}")
#         return os.path.splitext(name)[0] + ".mp4", None


async def drm_download_video(url, qual, name, keys):

    print(keys)
    keys = keys.split(":")
    if len(keys) != 2:
        print("Error: Two keys must be provided separated by a colon.")
        return None
    key1, key2 = keys


    if qual =="1":
        nqual="720"

    elif qual=="2":
        nqual= "480" 

    elif qual =="3":
        nqual="360"

    elif qual=="4":
        nqual="240"
    else :
        nqual="480"                
  
    try:
        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Path to N_m3u8DL-RE
        n_m3u8dl_re_path = os.path.join(current_dir, "N_m3u8DL-RE")
        
                # Add execute permission
        current_permissions = os.stat(n_m3u8dl_re_path).st_mode
        os.chmod(n_m3u8dl_re_path, current_permissions | stat.S_IEXEC)



        # Use N_m3u8DL-RE for decryption
        nurl = url.replace("master",f"master_{nqual}")
        subprocess.run([
            n_m3u8dl_re_path,
            "--auto-select",
            "--key", f"{key1}:{key2}",
            nurl,
            "-mt",  # Enable multi-threading
            "--thread-count", "16",  
            "-M", "format=mkv",  
            "--save-name", name
        ], check=True)
        
        mkv_file = f"{name}.mkv"
        
        print(f"Decryption and download to MKV successful with key {keys}.")
        return mkv_file
    except subprocess.CalledProcessError as e:
        print(f"Error in download or conversion process: {e}")
        return None

def duration(name):
    result = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
        "default=noprint_wrappers=1:nokey=1", name
    ],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    return float(result.stdout)


async def download(url, name):
    ka = f'{name}.pdf'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(ka, mode='wb')
                await f.write(await resp.read())
                await f.close()
    return ka



async def run(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

    print(f'[{cmd!r} exited with {proc.returncode}]')
    if proc.returncode == 1:
        return False
    if stdout:
        return f'[stdout]\n{stdout.decode()}'
    if stderr:
        return f'[stderr]\n{stderr.decode()}'


def old_download(url, file_name, chunk_size=1024 * 10):
    if os.path.exists(file_name):
        os.remove(file_name)
    r = requests.get(url, allow_redirects=True, stream=True)
    with open(file_name, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            if chunk:
                fd.write(chunk)
    return file_name


def human_readable_size(size, decimal_places=2):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if size < 1024.0 or unit == 'PB':
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"


def time_name():
    date = datetime.date.today()
    now = datetime.datetime.now()
    current_time = now.strftime("%H%M%S")
    return f"{date} {current_time}.mp4"



async def download_video(url, name, cmd):
    # ytf = f"b[height<={qual}]/bv[height<={qual}]+ba/b/bv+ba"
    # if ".pdf" in url :
    #     cmd = f'yt-dlp -o "{name}.pdf" "{url}"'    
    # else:
    #     cmd = f'yt-dlp -f "{ytf}" --no-keep-video --remux-video mkv "{url}" -o "{name}.%(ext)s"'
    time.sleep(0.5)
    download_cmd = f'{cmd} -R infinite --fragment-retries 25 --socket-timeout 20 --external-downloader aria2c --downloader-args "aria2c: -x 16 -j 32"'
    global failed_counter
    print(download_cmd)
    logging.info(download_cmd)
    k = subprocess.run(download_cmd, shell=True)
    if "visionias" in cmd and k.returncode != 0 and failed_counter <= 10:
        failed_counter += 1
        await asyncio.sleep(5)
        await download_video(url, cmd, name)
    failed_counter = 0
    try:
        if os.path.isfile(name):
            return name
        elif os.path.isfile(f"{name}.webm"):
            return f"{name}.webm"
        name = name.split(".")[0]
        if os.path.isfile(f"{name}.mkv"):
            return f"{name}.mkv"
        elif os.path.isfile(f"{name}.mp4"):
            return f"{name}.mp4"
        elif os.path.isfile(f"{name}.mp4.webm"):
            return f"{name}.mp4.webm"
        return name
    except FileNotFoundError as exc:
        return os.path.isfile.splitext[0] + "." + "mp4"


    
    
    
async def send_vid(bot: Client, m: Message, cc, filename,name, thumb):
    reply = await m.reply_text(f"**⚡️ Starting Uploading ...** - `{name}`")
    try:
        if thumb != "no":
            print(thumb)
            subprocess.run(['wget', thumb, '-O', 'thumb1.jpg'], check=True)  # Fixing this line
            thumbnail = "thumb1.jpg"
        else:
            subprocess.run(f'ffmpeg -i "{filename}" -ss 00:00:12 -vframes 1 "thumb1.jpg"', shell=True)
            thumbnail = "thumb1.jpg"
   
    except Exception as e:
        await m.reply_text(str(e))

    dur = int(duration(filename))

    start_time = time.time()

    try:
        await m.reply_video(filename, caption=cc, supports_streaming=True, height=720, width=1280, thumb=thumbnail, duration=dur, progress=progress_bar, progress_args=(reply, start_time))
    except Exception:
        await m.reply_document(filename, caption=cc, thumb=thumbnail, progress=progress_bar, progress_args=(reply, start_time))

    os.remove(filename)
    os.remove("thumb1.jpg")
    await reply.delete(True)
