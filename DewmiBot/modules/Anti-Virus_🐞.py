import os
from DewmiBot import tbot
from DewmiBot import CMD_HELP, VIRUS_API_KEY
from telethon import events
from telethon.tl import functions
from telethon.tl import types
from telethon.tl.types import MessageMediaDocument, DocumentAttributeFilename
from pymongo import MongoClient
from DewmiBot import MONGO_DB_URI
from DewmiBot.events import register
import cloudmersive_virus_api_client

client = MongoClient()
client = MongoClient(MONGO_DB_URI)
db = client["DewmiBot"]
approved_users = db.approve

async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):

        return isinstance(
            (
                await tbot(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    if isinstance(chat, types.InputPeerChat):

        ui = await tbot.get_peer_id(user)
        ps = (
            await tbot(functions.messages.GetFullChatRequest(chat.chat_id))
        ).full_chat.participants.participants
        return isinstance(
            next((p for p in ps if p.user_id == ui), None),
            (types.ChatParticipantAdmin, types.ChatParticipantCreator),
        )
    return None

configuration = cloudmersive_virus_api_client.Configuration()
configuration.api_key['Apikey'] = VIRUS_API_KEY
api_instance = cloudmersive_virus_api_client.ScanApi(cloudmersive_virus_api_client.ApiClient(configuration))
allow_executables = True 
allow_invalid_files = True 
allow_scripts = True 
allow_password_protected_files = True 

@register(pattern="^/scanit$")
async def virusscan(event):
    if event.fwd_from:
        return
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if event.is_group:
        if await is_register_admin(event.input_chat, event.message.sender_id):
            pass
        elif event.chat_id == iid and event.sender_id == userss:
            pass
        else:
            return
    if not event.reply_to_msg_id:
       await event.reply("Reply to a file to scan it.")
       return

    c = await event.get_reply_message()
    try:
       c.media.document
    except Exception:
       await event.reply("💁🏼‍♂️ This bot accepts only files.\n💬support chat👉 @slbotzone ")
       return
    h = c.media
    try:
       k = h.document.attributes
    except Exception:
       await event.reply("💁🏼‍♂️ This bot accepts only files.\n💬support chat👉 @slbotzone ")
       return
    if not isinstance(h, MessageMediaDocument):
       await event.reply("💁🏼‍♂️ This bot accepts only files.\n💬support chat👉 @slbotzone ")
       return
    if not isinstance(k[0], DocumentAttributeFilename):
       await event.reply("💁🏼‍♂️ This bot accepts only files.\n💬support chat👉 @slbotzone ")
       return
    try:
      virus = c.file.name
      await event.client.download_file(c, virus)
      gg= await event.reply("🚀 ** File initialized**.\n✅ File downloaded.\n✅ File uploaded to telegram.")
      fsize = c.file.size
      if not fsize <= 3145700: # MAX = 3MB
         await gg.edit("🔗 This file size is not supported. File size exceeds 3MB")
         return
      api_response = api_instance.scan_file_advanced(c.file.name, allow_executables=allow_executables, allow_invalid_files=allow_invalid_files, allow_scripts=allow_scripts, allow_password_protected_files=allow_password_protected_files)
      if api_response.clean_result is True:
       await gg.edit("This file is safe ✔️\n🧬 `Detections: 0 / 57`")
      else:
       await gg.edit("This file is Dangerous ☠️️\n`Virus detected 🐞`")
      os.remove(virus)
    except Exception as e:
      print(e)
      os.remove(virus)
      await gg.edit("Some error occurred.")
      return

file_help = os.path.basename(__file__)
file_help = file_help.replace(".py", "")
file_helpo = file_help.replace("_", " ")

__help__ = """
@szrosebot🇱🇰
 ❍ /scanit: Scan a file for virus (MAX SIZE = 3MB)
"""
__mod_name__ = "virus"




CMD_HELP.update({
    file_helpo: [
        file_helpo,
        __help__
    ]
})
