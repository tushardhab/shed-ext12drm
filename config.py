import os

API_ID = API_ID =  24798261

API_HASH = os.environ.get("API_HASH", "fef280037f5759eccc540c6d7a279a14")

BOT_TOKEN = os.environ.get("BOT_TOKEN", "7442398712:AAHG4b6EPw7GwoN4Bs-u2Q1Y3AsyiXFBUyU")

PASS_DB = int(os.environ.get("PASS_DB", "721"))

OWNER = int(os.environ.get("OWNER", 6155478725))

LOG = -1002249382208,

# UPDATE_GRP = -1002140332321, # bot sat group

# auth_chats = [5219193259,1327415906]

try:
    ADMINS=[]
    for x in (os.environ.get("ADMINS", "6155478725").split()):
        ADMINS.append(int(x))
except ValueError:
        raise Exception("Your Admins list does not contain valid integers.")
ADMINS.append(OWNER)


