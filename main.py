from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
import requests
import os
import sys
import datetime
import random
import time
from pyromod import listen
from pymongo import MongoClient
import helper
import asyncio
import subprocess


# Initialize Pyrogram bot with api_id and api_hash
app = Client(
    "bot",
    #bot_token="6178250261:AAGx5Z-uofPm2AASeFpvlx_zEQj0PAy99n0",
    bot_token="7442398712:AAHG4b6EPw7GwoN4Bs-u2Q1Y3AsyiXFBUyU",
    api_id= 24798261,
    api_hash="fef280037f5759eccc540c6d7a279a14"
)

# MongoDB setup
mongo_uri = "mongodb+srv://successspark09:tushar@filestore12.dnbo7vb.mongodb.net/?retryWrites=true&w=majority&appName=filestore12"
client = MongoClient(mongo_uri)
db = client["bot_database"]
user_collection = db["user_details"]

# Global variables
owner_id = 6155478725
auth_users = [6155478725]
token = ""
batch_ids = {}
batch_name_dict = {}
qual = ""
count = 0
processing_request = False
user_data = {}
thumb="no"
# quals = 480
#pwurl = "https://pw.romeoo.workers.dev/?v="
#pwurl = os.environ.get("pwurl")



image_urls = [
    "https://mallucampaign.in/images/img_1720447475.jpg",
]

keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                text="👨🏻‍💻 Developer",
                url="https://t.me/HKOWNER0",
            ),
            InlineKeyboardButton(
                text="❣️ KINDNESS",
                url="https://t.me/love4allxd",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🪄 Main Channel",
                url="https://t.me/+gX6tWR1VWvUwOTRl",
            ),
        ],
    ]
)

Busy = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                text="👨🏻‍💻 Developer",
                url="https://t.me/HKOWNER0",
            ),
        ],
    ]
)

# Define /start command handler
@app.on_message(filters.command("start"))
async def start_command(client, message):
    random_image_url = random.choice(image_urls)
    caption = "**Hi! 👋🏼 I am your Penpencil bot. \n✌🏼 Use /today to Get Today shedule Class \n✌🏼 Use /weekly to get Weekly Shedule Lec  [in beta stage ] \n↪ If new Use /save_details 1st \n↪ Use /edit_details to edit stored data  **"
    await client.send_photo(chat_id=message.chat.id, photo=random_image_url, caption=caption, reply_markup=keyboard)

@app.on_message(filters.command(["logs"]))
async def send_logs(Client, message):
    try:
        with open("Assist.txt", "rb") as file:
            sent = await Client.send_message(message.chat.id, "**📤 Sending you ....**")
            await Client.send_document(message.chat.id, document=file)
            await sent.delete(True)
    except Exception as e:
        await Client.send_message(message.chat.id, f"Error sending logs: {e}")

@app.on_message(filters.command("stop"))
async def stop_handler(_, m):
    await m.reply_text("🤖**Stopping Bot **🤖", True)
    os.execl(sys.executable, sys.executable, *sys.argv)

def is_subscription_expired(user_id):
    with open("Subscription_data.txt", "r") as file:
        for line in file:
            data = line.strip().split(", ")
            stored_user_id = int(data[0].split(",")[0])  # Extract and convert the user ID
            start_date = datetime.datetime.strptime(data[1], "%d-%m-%Y")
            end_date = datetime.datetime.strptime(data[2], "%d-%m-%Y")
            today = datetime.datetime.today()
            if stored_user_id == user_id and start_date <= today <= end_date:
                return False  # Subscription is active for this user
    return True  # No active subscription found or subscription expired

# Define the add_subscription command handler

# Define the myplan command handler
@app.on_message(filters.command("myplan"))
async def myplan_command_handler(bot, message):
    user_id = message.from_user.id
    with open("Subscription_data.txt", "r") as file:
        for line in file:
            data = line.strip().split(", ")
            if int(data[0]) == user_id:
                if user_id in auth_users:
                    await message.reply("**YOU HAVE LIFE TIME ACCESS :) **")
                    return
                subscription_start = data[1]
                expiration_date = data[2]
                today = datetime.datetime.today()
                if today > datetime.datetime.strptime(expiration_date, "%d-%m-%Y"):
                    plan = "EXPIRED "
                    response_text = f"**✨ User ID: {user_id}\n📊 PLAN STAT : {plan}\n\n🔰 Activated on : {subscription_start}\n🧨 Expiration Date: {expiration_date} \n\n 🫰🏼 ACTIVATE YOUR PLAN NOW ! \n⚡️ TO ACTIVATE MESSAGE : @ITS_NOT_ROMEO :D **"
                    await message.reply(response_text, reply_markup=Busy)
                else:
                    plan = "ALIVE!"  
                    response_text = f"**✨ User ID: {user_id}\n📊 PLAN STAT : {plan}\n🔰 Activated on : {subscription_start}\n🧨 Expiration Date: {expiration_date}**"
                    await message.reply(response_text)
                return
    await message.reply("** Opps :( , No subscription data found for you.**", reply_markup=Busy)



async def extract_video_id(url, res, token, schedule):
    key = None  # Initialize key as None
    
    # Quality mapping
    qual_map = {
        "240": "4",
        "360": "3",
        "480": "2",
        "720": "1"
    }
    
    # Get the mapped quality, default to "3" if not found
    mapped_qual = qual_map.get(res, "3")
    
    if "youtube" in url or "embed" in url:
        return url, key, res  # Return the URL itself, None for key, and original quality for YouTube

    if "master.mpd" in url:
        if "https://sec1.pw.live/" in url:
            url = url.replace("https://sec1.pw.live/", "https://d1d34p8vz63oiq.cloudfront.net/")
            print(url)
        else: 
            url = url   
        print("mpd check")
        print(token)
        key = await helper.get_drm_keys(url, token)
        print(key)
    
    if "index.m3u8" in url:
        start_time = schedule.get('startTime')
        end_time = schedule.get('endTime')
        
        if start_time and end_time:
            # Convert to Unix timestamp (UTC)
            start_unix = int(datetime.datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=datetime.timezone.utc).timestamp())
            end_unix = int(datetime.datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=datetime.timezone.utc).timestamp())
            
            # Construct the new URL
            url = f"https://shed-ext12drm.onrender.com?v={url}&quality={res}&start={start_unix}&end={end_unix}&token={token}"
            print(f"Constructed URL: {url}")
    
    return url, key, mapped_qual  # Return URL, key, and mapped quality for non-YouTube links



                       
# Define /tod_schedule command handler
@app.on_message(filters.command("today"))
async def tod_schedule_command(client, message):
    user_id = message.from_user.id
    global token
    global count
    global thumb
    global batch_name_dict
    global processing_request

    if is_subscription_expired(user_id):
        await message.reply("📊 Your subscription has expired. Please renew to access this feature.")
        return

    if processing_request:
        await message.reply_text("**🫨 I'm currently processing another request.\n Please try again later.**", reply_markup=Busy)
        return

    # Check if the user has stored details in the database
    user_details = user_collection.find_one({"user_id": user_id})
    if user_details:
        token = user_details["token"]
        quals = user_details["video_qualities"]
        editable = await client.send_message(message.chat.id, "📍 **Using your stored token and video quality.**")
    else:
        editable = await client.send_message(message.chat.id, "🎫**PROVIDE AUTH TOKEN**")
        input0: Message = await client.listen(message.chat.id)
        token = input0.text
        await input0.delete(True)

        await editable.edit("🎞**PROVIDE VIDEO QUALITY (e.g., 240,360,480,720,)**")
        input1: Message = await client.listen(message.chat.id)
        qual = input1.text
        await input1.delete(True)

    processing_request = True

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("https://api.penpencil.co/v3/batches/all-purchased-batches?page=1&mode=1&sort=TAG_LIST", headers=headers)

    if response.status_code == 200:
        data = response.json().get("data", [])
        if data:
            batch_info_list = []
            for batch in data:
                batch_id = batch['batch']['_id']
                batch_name = batch['batch']['name']
                batch_name_dict[batch_id] = batch_name  # Store batch name and ID in dictionary
                batch_info_list.append(f"📦 **Batch Name: {batch_name}** \n✨ Batch ID: `{batch_id}`")
            batch_info = "\n\n".join(batch_info_list)
            await message.reply(f"**🔰 Here are your batches:**\n{batch_info}")
        else:
            await message.reply("😿 No batches found.")
    else:
        await message.reply("Failed to fetch batches. Please check your token and try again.")
        processing_request = False
        return

    editable2 = await client.send_message(message.chat.id, "**✨ NOW SEND BATCH ID TO FETCH TODAY'S SCHEDULE. **\n\n ⚡️ __SEND NOW !__")
    input1: Message = await client.listen(message.chat.id)
    batch_id = input1.text
    await input1.delete(True)
    time.sleep(0.5)
    
    await editable2.edit("**🪄 Want To Add To Vid Thumbnail ? \n📍 Send : `yes` to add thumb sored in db   \n📍 Send : `no` to skip adding\n📍 Send `Custom` to add new thumb except stored in my db if saved  **")
    input5: Message = await client.listen(message.chat.id)
    thumbc = input5.text
    await input5.delete(True)
    if thumbc == "yes" or thumbc == "Yes" or thumbc == "YES":
        user_id = message.from_user.id
        user_details = user_collection.find_one({"user_id": user_id})
        if user_details:
            apply_thumbnail = user_details.get("apply_thumbnail", False)
            thumb = user_details.get("thumbnail", "no")
            await editable2.edit("**Getting thumbnail from my DB **")
            time.sleep(0.5)
        else:
            await editable2.edit("**Send Thumbnail URL **")
            input6: Message = await client.listen(message.chat.id)
            thumb = input6.text
            await input6.delete(True)
    elif thumbc == "custom" or thumbc == "Custom" or thumbc == "CUSTOM":   
            await editable2.edit("**Send Thumbnail Custom URL **")
            input6: Message = await client.listen(message.chat.id)
            thumb = input6.text
            await input6.delete(True)
    else:
        thumb = "no"
    time.sleep(0.5)
    await editable2.delete(True)
    await editable.delete(True)


    batch_name = batch_name_dict.get(batch_id, 'NONE')
    await send_schedule_as_text_file(client, message, batch_id, batch_name, quals)

# Function to send the schedule as a text file with selective download options
async def send_schedule_as_text_file(client, message, batch_id, batch_name, quals):
    global token
    global processing_request
    user_id = message.from_user.id

    if is_subscription_expired(user_id):
        await client.send_message(message.chat.id, "Your subscription has expired. Please renew to access this feature.")
        processing_request = False
        return

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"https://api.penpencil.co/v1/batches/{batch_id}/todays-schedule/", headers=headers)

    if response.status_code == 200:
        data = response.json().get("data", [])
        if data:
            inline_buttons = []
            user_data_dict = user_data.get(user_id, {"notes_selected": [], "videos_selected": []})
            notes_selected = user_data_dict.get("notes_selected", [])
            videos_selected = user_data_dict.get("videos_selected", [])

            # Notes section
            inline_buttons.append([InlineKeyboardButton(text="📝 Notes + Dpp soln 👇🏽", callback_data="notes_section")])
            for idx, schedule in enumerate(data):
                topic = schedule.get('topic', 'No Topic')
                is_notes = any(keyword.lower() in topic.lower() for keyword in ['dpp', 'Notes', 'paper', 'pdf'])
                if is_notes:
                    checkbox = InlineKeyboardButton(
                        text=f"{'✅' if idx in notes_selected else '⬜️'} {topic[:50]}...",
                        callback_data=f"notes_toggle_{idx}"
                    )
                    inline_buttons.append([checkbox])

            # Videos section
            inline_buttons.append([InlineKeyboardButton(text="📹 Videos + Notes👇🏽", callback_data="videos_section")])
            for idx, schedule in enumerate(data):
                topic = schedule.get('topic', 'No Topic')
                is_notes = any(keyword.lower() in topic.lower() for keyword in ['dpp', 'Notes', 'paper', 'pdf'])
                if not is_notes:
                    checkbox = InlineKeyboardButton(
                        text=f"{'✅' if idx in videos_selected else '⬜️'} {topic[:50]}...",
                        callback_data=f"videos_toggle_{idx}"
                    )
                    inline_buttons.append([checkbox])

            # Download buttons
            inline_buttons.append([InlineKeyboardButton(
                text="✨ Start Download",
                callback_data="start_download"
            )])
            inline_buttons.append([InlineKeyboardButton(
                text="Download All 📥",
                callback_data="download_all"
            )])

            reply_markup = InlineKeyboardMarkup(inline_buttons)
            await message.reply("**⚡️ Alright Now Select the video/notes topic you need to Download :\n 1. IN NOTES YOU WILL GET DPP AND SOLUTION LEC \n 2. IN VIDEOS SELECT LEC NOTES WILL BE DOWNLODED AUTOMATICALLY**", reply_markup=reply_markup)

            user_data[user_id] = {
    "schedule": data,
    "batch_name": batch_name,
    "quals": quals,  # Store the list of qualities
    "notes_selected": notes_selected,
    "videos_selected": videos_selected
}
        else:
            await message.reply("No schedule found for the provided batch ID.")
    else:
        await message.reply("Failed to fetch today's schedule. Please check the batch ID and try again.")
        processing_request = False
        return

    processing_request = False

@app.on_callback_query()
async def handle_callback_query(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    data = callback_query.data
    global thumb
    CR = f"[{callback_query.from_user.first_name}](tg://user?id={callback_query.from_user.id})"

    if data.startswith("notes_toggle_") or data.startswith("videos_toggle_"):
        _, toggle_type, idx = data.split("_")
        idx = int(idx)
        user_data_dict = user_data.get(user_id, {"notes_selected": [], "videos_selected": []})
        schedule_data = user_data_dict.get("schedule", [])
        notes_selected = user_data_dict.get("notes_selected", [])
        videos_selected = user_data_dict.get("videos_selected", [])

        is_notes = data.startswith("notes_toggle_")
        selected_items = notes_selected if is_notes else videos_selected
        toggle_type_text = "Notes" if is_notes else "Videos"

        if idx in selected_items:
            selected_items.remove(idx)
        else:
            selected_items.append(idx)

        if is_notes:
            user_data[user_id]["notes_selected"] = notes_selected
        else:
            user_data[user_id]["videos_selected"] = videos_selected

        inline_buttons = []

        # Notes section
        inline_buttons.append([InlineKeyboardButton(text="📝 Notes + Dpp soln 👇🏽", callback_data="notes_section")])
        for i, schedule in enumerate(schedule_data):
            topic = schedule.get('topic', 'No Topic')
            is_note = any(keyword.lower() in topic.lower() for keyword in ['(of lec', 'Notes', 'paper', 'pdf'])
            if is_note:
                checkbox = InlineKeyboardButton(
                    text=f"{'✅' if i in notes_selected else '⬜️'} {topic[:50]}...",
                    callback_data=f"notes_toggle_{i}"
                )
                inline_buttons.append([checkbox])

        # Videos section
        inline_buttons.append([InlineKeyboardButton(text="📹 Videos + Notes👇🏽", callback_data="videos_section")])
        for i, schedule in enumerate(schedule_data):
            topic = schedule.get('topic', 'No Topic')
            is_note = any(keyword.lower() in topic.lower() for keyword in ['(of lec', 'Notes', 'paper', 'pdf'])
            if not is_note:
                checkbox = InlineKeyboardButton(
                    text=f"{'✅' if i in videos_selected else '⬜️'} {topic[:50]}...",
                    callback_data=f"videos_toggle_{i}"
                )
                inline_buttons.append([checkbox])

        # Download buttons
        inline_buttons.append([InlineKeyboardButton(
            text="✨ Start Download",
            callback_data="start_download"
        )])
        inline_buttons.append([InlineKeyboardButton(
            text="Download All 📥",
            callback_data="download_all"
        )])

        reply_markup = InlineKeyboardMarkup(inline_buttons)
        await callback_query.edit_message_reply_markup(reply_markup=reply_markup)

        # Show selected items to the user in the callback query answer
        if is_notes:
            if idx in notes_selected:
                selected_topic = schedule_data[idx]['topic']
                await callback_query.answer(f"Selected Topic: {selected_topic}", show_alert=True)
            else:
                deselected_topic = schedule_data[idx]['topic']
                await callback_query.answer(f"Deselected Topic: {deselected_topic}", show_alert=True)
        else:
            if idx in videos_selected:
                selected_topic = schedule_data[idx]['topic']
                await callback_query.answer(f"Selected Topic: {selected_topic}", show_alert=True)
            else:
                deselected_topic = schedule_data[idx]['topic']
                await callback_query.answer(f"Deselected Topic: {deselected_topic}", show_alert=True)

    elif data == "start_download":
        user_data_dict = user_data.get(user_id, {})
        schedule_data = user_data_dict.get("schedule", [])
        batch_name = user_data_dict.get("batch_name", "Unknown Batch")
        quals = user_data_dict.get("quals", ["480"])
        notes_selected = user_data_dict.get("notes_selected", [])
        videos_selected = user_data_dict.get("videos_selected", [])
        await callback_query.message.delete()

        for idx in notes_selected:
            schedule = schedule_data[idx]
            homework_ids = [hw_id['_id'] for hw_id in schedule.get('homeworkIds', [])]

            if not homework_ids:
                print(f"No homeworkIds found for schedule: {schedule}")
                continue

            for homework_id in homework_ids:
                homework = next((hw for hw in schedule.get('homeworkIds', []) if hw['_id'] == homework_id), None)
                if not homework:
                    print(f"No homework found for homeworkId {homework_id} in schedule: {schedule}")
                    continue

                attachment_ids = [att['_id'] for att in homework.get('attachmentIds', [])]
                if not attachment_ids:
                    print(f"No attachmentIds found for homeworkId {homework_id} in schedule: {schedule}")
                    continue

                for attachment_id in attachment_ids:
                    attachment = next((att for att in homework.get('attachmentIds', []) if att['_id'] == attachment_id), None)
                    if not attachment:
                        print(f"No attachment found for attachmentId {attachment_id} in homeworkId {homework_id}")
                        continue

                    name = attachment.get('name', '')
                    if not name:
                        print(f"No name found for attachmentId {attachment_id} in homeworkId {homework_id}")
                        continue

                    if "pdf" not in name.lower():
                        print(f"pdf : {name} ")
                        await download_schedule_item(client, callback_query.message, schedule, batch_name, [""], thumb, CR)
                    else:
                        for qual in quals:
                            print(f"pdf : {name}")
                            print(f"qual of dpp lec  : {qual}")
                            await download_schedule_item(client, callback_query.message, schedule, batch_name, [qual], thumb, CR)


        for idx in videos_selected:
            schedule = schedule_data[idx]
            for qual in quals:
                print(f"qual of lec  : {qual}")
                await download_schedule_item(client, callback_query.message, schedule, batch_name, [qual], thumb, CR)

        # Reset the selected lists after the download process
        user_data[user_id]["notes_selected"] = []
        user_data[user_id]["videos_selected"] = []

        await client.send_message(callback_query.message.chat.id, "Download process completed for selected items.")

    elif data == "download_all":
        user_data_dict = user_data.get(user_id, {})
        schedule_data = user_data_dict.get("schedule", [])
        batch_name = user_data_dict.get("batch_name", "Unknown Batch")
        quals = user_data_dict.get("quals", ["480"])

        await callback_query.message.delete()

        for idx, schedule in enumerate(schedule_data):
            #print(schedule)
            topic = schedule.get('topic', 'No Topic')
            is_notes = any(keyword.lower() in topic.lower() for keyword in ['(of lec', 'Notes', 'paper', 'pdf'])
            homework_ids = [hw_id['_id'] for hw_id in schedule.get('homeworkIds', [])]

            if is_notes and not homework_ids:
                print(f"pdf VID : {topic}")
                for qual in quals:
                    await download_schedule_item(client, callback_query.message, schedule, batch_name, [qual], thumb, CR)

            elif is_notes and homework_ids:
                for homework_id in homework_ids:
                    homework = next((hw for hw in schedule.get('homeworkIds', []) if hw['_id'] == homework_id), None)
                    if not homework:
                        print(f"No homework found for homeworkId {homework_id} in schedule: {schedule}")
                        continue

                    attachment_ids = [att['_id'] for att in homework.get('attachmentIds', [])]
                    if not attachment_ids:
                        print(f"No attachmentIds found for homeworkId {homework_id} in schedule: {schedule}")
                        continue

                    for attachment_id in attachment_ids:
                        attachment = next((att for att in homework.get('attachmentIds', []) if att['_id'] == attachment_id), None)
                        if not attachment:
                            print(f"No attachment found for attachmentId {attachment_id} in homeworkId {homework_id}")
                            continue

                        name = attachment.get('name', '')
                        if not name:
                            print(f"No name found for attachmentId {attachment_id} in homeworkId {homework_id}")
                            continue

                        if "pdf" in name.lower():
                            print(f"pdf : {name} \n schedule : {schedule}")
                            await download_schedule_item(client, callback_query.message, schedule, batch_name, [""], thumb, CR)
                        else:
                            for qual in quals:
                                print(f"pdf : {name}")
                                print(f"qual of dpp lec  : {qual} \n schedule : {schedule}")
                                await download_schedule_item(client, callback_query.message, schedule, batch_name, [qual], thumb, CR)

            if not is_notes:
                print(f"vid  not notes : {topic}")
                for qual in quals:
                    await download_schedule_item(client, callback_query.message, schedule, batch_name, [qual], thumb, CR)

        # Reset the selected lists after the download process
        user_data[user_id]["notes_selected"] = []
        user_data[user_id]["videos_selected"] = []

        await client.send_message(callback_query.message.chat.id, "Download process completed for all items.")


async def download_schedule_item(client, message, schedule, batch_name, quals, thumb, CR):
    topic = schedule.get('topic', '')
    subject = schedule.get('subjectId').get('name','ND')
    if 'url' in schedule:
        url = schedule['url']
        for qual in quals:
            qual = qual.strip() 
            url, key, mapped_qual = await extract_video_id(url, qual, token, schedule)
            if url:
                if ".pdf" not in url and url != '':
                    try:
                        name1 = topic.replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
                        topic = f'{name1[:60]}'
                        prog = await client.send_message(message.chat.id, f"📥 **Downloading **\n\n**➭ File » ** `{name1}`\n**➭ Link »** `{url}`\n✨ **Bot Made by HARE KRISHNA**\n**━━━━━━━✦✗✦━━━━━━━**")
                        
                        if "youtube" in url or "embed" in url or "index.m3u8" in url:
                            ytf = f"b[height<={qual}]/bv[height<={qual}]+ba/b/bv+ba"
                            cmd = f'yt-dlp -f "{ytf}" --no-keep-video --remux-video mkv "{url}" -o "{topic}.%(ext)s"'
                            file = await helper.download_video(url, topic, cmd)
                        else:
                              #cmd = f" -f bestvideo.{mapped_qual} --fixup never {url} "
                              file = await helper.drm_download_video(url,qual, topic, key)
                        await prog.delete(True)
                        cc1 = f'**➭ Title » {name1}** \n**➭ Batch » {batch_name}**\n**➭ Subject » {subject} **\n**➭ Quality » {qual}**\n\n✨ **Downloaded by: @HKOWNER0**\n**━━━━━━━✦✗✦━━━━━━━**'
                        #cc1 = f'**➭ Title » {name1}** \n**➭ Batch » {batch_name}**\n**➭ Quality » {qual}**\n✨ **Downloaded by: {CR}**\n**━━━━━━━✦✗✦━━━━━━━**'
                        video = await helper.send_vid(bot=client, m=message, cc=cc1, filename=file, name=name1,thumb=thumb)
                        time.sleep(1)
                    except Exception as e:
                        await client.send_message(message.chat.id, f"**This #Failed File is not Counted**\n**Name** =>> `{name1}`\n**Link** =>> `{url}`\n **Fail reason »** {e}")

    if 'homeworkIds' in schedule:
        homeworks = schedule['homeworkIds']
        for homework in homeworks:
            if 'attachmentIds' in homework:
                attachments = homework['attachmentIds']
                for attachment in attachments:
                    pname = attachment.get('name', 'No Name')
                    key = attachment.get('key', 'No Key')
                    nurl = f'https://d2bps9p1kiy4ka.cloudfront.net/{key}'
                    try:
                        prog = await client.send_message(message.chat.id, f"📥 **Downloading **\n**➭ File » ** `{pname}`\n**➭ Link »** `{nurl}`\n✨ **Bot Made by HK**\n**━━━━━━━✦✗✦━━━━━━━**")
                        cmd = f'yt-dlp "{nurl}" -o "{pname}" --allow-unplayable-formats'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        await prog.delete(True)
                        cc1 = f'**➭ Title » {pname}** \n**➭ Batch » {batch_name}**\n**➭ Subject » {subject} **\n\n✨ **Downloaded by: @HKOWNER0 **\n**━━━━━━━✦✗✦━━━━━━━**'
                        #cc1 = f'**➭ Title » {pname}** \n**➭ Batch » {batch_name}**\n✨ **Downloaded by: {CR}**\n**━━━━━━━✦✗✦━━━━━━━**'
                        await client.send_document(message.chat.id, pname, caption=cc1)
                        os.remove(f'{pname}')
                        time.sleep(1)
                    except Exception as e:
                        await client.send_message(message.chat.id, f"**This #Failed File is not Counted**\n**Name** =>> `{pname}`\n**Link** =>> `{nurl}`\n **Fail reason »** {e}")


@app.on_message(filters.command("weekly"))
async def tod_schedule_command(client, message):
    user_id = message.from_user.id
    global token
    global count
    global thumb
    global batch_name_dict
    global processing_request

    if is_subscription_expired(user_id):
        await message.reply("📊 Your subscription has expired. Please renew to access this feature.")
        return

    if processing_request:
        await message.reply_text("**🫨 I'm currently processing another request.\n Please try again later.**", reply_markup=Busy)
        return

    # Check if the user has stored details in the database
    user_details = user_collection.find_one({"user_id": user_id})
    if user_details:
        token = user_details["token"]
        quals = user_details["video_qualities"]
        editable = await client.send_message(message.chat.id, "📍 **Using your stored token and video quality.**")
    else:
        editable = await client.send_message(message.chat.id, "🎫**PROVIDE AUTH TOKEN**")
        input0: Message = await client.listen(message.chat.id)
        token = input0.text
        await input0.delete(True)

        await editable.edit("🎞**PROVIDE VIDEO QUALITY (e.g., 240,360,480,720,)**")
        input1: Message = await client.listen(message.chat.id)
        qual = input1.text
        await input1.delete(True)

    processing_request = True

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("https://api.penpencil.co/v3/batches/all-purchased-batches?page=1&mode=1&sort=TAG_LIST", headers=headers)

    if response.status_code == 200:
        data = response.json().get("data", [])
        if data:
            batch_info_list = []
            for batch in data:
                batch_id = batch['batch']['_id']
                batch_name = batch['batch']['name']
                batch_name_dict[batch_id] = batch_name  # Store batch name and ID in dictionary
                batch_info_list.append(f"📦 **Batch Name: {batch_name}** \n✨ Batch ID: `{batch_id}`")
            batch_info = "\n\n".join(batch_info_list)
            bach_msg1 = await client.send_message(message.chat.id,f"**🔰 Here are your batches:**\n{batch_info}")
        else:
            await message.reply("😿 No batches found.")
    else:
        await message.reply("Failed to fetch batches. Please check your token and try again.")
        processing_request = False
        return

    # editable2 = await client.send_message(message.chat.id, "**✨ NOW SEND BATCH ID TO FETCH TODAY'S SCHEDULE. **\n\n ⚡️ __SEND NOW !__")
    bach_msg = await client.send_message(message.chat.id, "**✨ NOW SEND BATCH ID TO FETCH WEEKLY SHEDULE. **\n\n ⚡️ __SEND NOW !__")
    input1: Message = await client.listen(message.chat.id)
    batch_id = input1.text
    await input1.delete(True)
    time.sleep(0.5)

    await bach_msg.edit("**SEND OF WHICH DATE YOU WANT TO EXTREACT \n FORMAT : YYYY-MM-DD** \n Example : 2024-06-03")
    input5: Message = await client.listen(message.chat.id)
    weekly_date = input5.text
    await input5.delete(True)

    
    await bach_msg.edit("**🪄 Want To Add To Vid Thumbnail ? \n📍 Send : `yes` to add thumb sored in db   \n📍 Send : `no` to skip adding\n📍 Send `Custom` to add new thumb except stored in my db if saved  **")
    input6: Message = await client.listen(message.chat.id)
    thumbc = input6.text
    await input6.delete(True)
    if thumbc == "yes" or thumbc == "Yes" or thumbc == "YES":
        user_id = message.from_user.id
        user_details = user_collection.find_one({"user_id": user_id})
        if user_details:
            apply_thumbnail = user_details.get("apply_thumbnail", False)
            thumb = user_details.get("thumbnail", "no")
            await bach_msg.edit("**Getting thumbnail from my DB **")
            time.sleep(0.5)
        else:
            await bach_msg.edit("**Send Thumbnail URL **")
            input7: Message = await client.listen(message.chat.id)
            thumb = input7.text
            await input7.delete(True)
    elif thumbc == "custom" or thumbc == "Custom" or thumbc == "CUSTOM":   
            await bach_msg.edit("**Send Thumbnail Custom URL **")
            input8: Message = await client.listen(message.chat.id)
            thumb = input8.text
            await input8.delete(True)
    else:
        thumb = "no"
    time.sleep(0.5)
    await bach_msg.delete(True)
    await bach_msg1.delete(True)
    await editable.delete(True)

    batch_name = batch_name_dict.get(batch_id, 'NONE')
    await weekly_dl(client, message, batch_id, batch_name, quals,weekly_date)

# Function to send the schedule as a text file with selective download options
async def weekly_dl(client, message, batch_id, batch_name, quals,weekly_date):
    global token
    global processing_request
    user_id = message.from_user.id

    if is_subscription_expired(user_id):
        await client.send_message(message.chat.id, "Your subscription has expired. Please renew to access this feature.")
        processing_request = False
        return
    processing_request = True
    headers = {"Authorization": f"Bearer {token}"}
    #response = requests.get(f"https://api.penpencil.co/v1/batches/{batch_id}/todays-schedule/", headers=headers)
    response = requests.get(f"https://api.penpencil.co/v1/batches/{batch_id}/weekly-schedules?limit=50&startDate={weekly_date}&endDate={weekly_date}&batchSubjectId=&page=1", headers=headers)

    if response.status_code == 200:
        data = response.json().get("data", [])
        if data:
            inline_buttons = []
            user_data_dict = user_data.get(user_id, {"notes_selected": [], "videos_selected": []})
            notes_selected = user_data_dict.get("notes_selected", [])
            videos_selected = user_data_dict.get("videos_selected", [])

            # Notes section
            inline_buttons.append([InlineKeyboardButton(text="📝 Notes + Dpp soln 👇🏽", callback_data="notes_section")])
            for idx, schedule in enumerate(data):
                topic = schedule.get('topic', 'No Topic')
                is_notes = any(keyword.lower() in topic.lower() for keyword in ['dpp', 'Notes', 'paper', 'pdf'])
                if is_notes:
                    checkbox = InlineKeyboardButton(
                        text=f"{'✅' if idx in notes_selected else '⬜️'} {topic[:50]}...",
                        callback_data=f"notes_toggle_{idx}"
                    )
                    inline_buttons.append([checkbox])

            # Videos section
            inline_buttons.append([InlineKeyboardButton(text="📹 Videos + Notes👇🏽", callback_data="videos_section")])
            for idx, schedule in enumerate(data):
                topic = schedule.get('topic', 'No Topic')
                is_notes = any(keyword.lower() in topic.lower() for keyword in ['dpp', 'Notes', 'paper', 'pdf'])
                if not is_notes:
                    checkbox = InlineKeyboardButton(
                        text=f"{'✅' if idx in videos_selected else '⬜️'} {topic[:50]}...",
                        callback_data=f"videos_toggle_{idx}"
                    )
                    inline_buttons.append([checkbox])

            # Download buttons
            inline_buttons.append([InlineKeyboardButton(
                text="✨ Start Download",
                callback_data="start_download"
            )])
            inline_buttons.append([InlineKeyboardButton(
                text="Download All 📥",
                callback_data="download_all"
            )])

            reply_markup = InlineKeyboardMarkup(inline_buttons)
            await message.reply("**⚡️ Alright Now Select the video/notes topic you need to Download :\n 1. IN NOTES YOU WILL GET DPP AND SOLUTION LEC \n 2. IN VIDEOS SELECT LEC NOTES WILL BE DOWNLODED AUTOMATICALLY**", reply_markup=reply_markup)

            user_data[user_id] = {
                "schedule": data,
                "batch_name": batch_name,
                "quals": quals,  # Store the list of qualities
                "notes_selected": notes_selected,
                "videos_selected": videos_selected
            }
        else:
            await message.reply("No schedule found for the provided batch ID.")
            processing_request = False
    else:
        await message.reply("Failed to fetch today's schedule. Please check the batch ID and try again.")
        processing_request = False
        return


# Define /save_details command handler
@app.on_message(filters.command("save_details"))
async def save_details_command(client, message):
    user_id = message.from_user.id
    editable = await client.send_message(message.chat.id, "🎫**PROVIDE AUTH TOKEN**")
    input0: Message = await client.listen(editable.chat.id)
    token = input0.text
    await input0.delete(True)

    await editable.edit("**🎞PROVIDE VIDEO QUALITIES (e.g., 240,360,480,720, separated by commas)**")
    input1: Message = await client.listen(message.chat.id)
    quals = input1.text.split(",")  # Split the input string by comma
    await input1.delete(True)

    await editable.edit("🖼 **PROVIDE THUMBNAIL URL**")
    input2: Message = await client.listen(message.chat.id)
    thumbnail = input2.text
    await input2.delete(True)

    await editable.edit("**🖼 DO YOU WANT TO APPLY THE THUMBNAIL? (yes/no)**")
    input3: Message = await client.listen(message.chat.id)
    apply_thumbnail = input3.text.lower() == "yes"
    await input3.delete(True)
    time.sleep(0.5)
    await editable.delete(True)
    user_details = {
    "user_id": user_id,
    "token": token,
    "video_qualities": quals,
    "thumbnail": thumbnail,
    "apply_thumbnail": apply_thumbnail
    }
    user_collection.insert_one(user_details)
    await client.send_message(message.chat.id, "** ✌🏼 Your details have been saved successfully!**")

# Define /edit_details command handler
@app.on_message(filters.command("edit_details"))
async def edit_details_command(client, message):
    user_id = message.from_user.id
    # Check if the user already has saved details
    user_details = user_collection.find_one({"user_id": user_id})
    if not user_details:
        await client.send_message(message.chat.id, "🥲 **No details found to edit. Please use /save_details first.**")
        return

    # Send the current details to the user
    await client.send_message(message.chat.id, "**Current Details:**\n\n**🎫 Token:** `{}`\n\n**🎞 Video Quality:** `{}`\n**🖼 Thumbnail URL:** `{}`\n**🖼 Apply Thumbnail:** `{}`".format(user_details['token'], ",".join(user_details['video_qualities']), user_details['thumbnail'], user_details['apply_thumbnail']))
    time.sleep(0.5)
    # Prompt for new details
    editable= await client.send_message(message.chat.id, "**✨PROVIDE NEW AUTH TOKEN**")
    input0: Message = await client.listen(editable.chat.id)
    token = input0.text
    await input0.delete(True)

    await editable.edit("**⚡️ PROVIDE NEW VIDEO QUALITIES (e.g., 240,360,480,720, separated by commas)**")
    input1: Message = await client.listen(message.chat.id)
    quals = input1.text.split(",")  # Split the input string by comma
    await input1.delete(True)
    
    await editable.edit("**🖼 PROVIDE NEW THUMBNAIL URL**")
    input2: Message = await client.listen(message.chat.id)
    thumbnail = input2.text
    await input2.delete(True)
    await editable.edit("**🖼 DO YOU WANT TO APPLY THE NEW THUMBNAIL? (yes/no)**")
    input3: Message = await client.listen(message.chat.id)
    apply_thumbnail = input3.text.lower() == "yes"
    await input3.delete(True)

    # Update the user details in the database
    user_collection.update_one(
        {"user_id": user_id},
        {"$set": {
            "token": token,
            "video_qualities": quals,
            "thumbnail": thumbnail,
            "apply_thumbnail": apply_thumbnail
        }}
    )
    time.sleep(0.5)
    await editable.edit(f"**🔥Your details have been updated successfully!**")
# Run the bot
app.run()
