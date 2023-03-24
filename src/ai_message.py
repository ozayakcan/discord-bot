import os
import requests
import translators as ts
from cogs.lang import get_lang_code, get_translate
import discord

lang_current_id = 0
lang_current_group = "guilds"

def brainshop(message, userid, token):
  resp = requests.get("http://api.brainshop.ai/get?bid=173774&key=" + token + "&uid="+str(userid)+"&msg="+message)
  resp = resp.json()
  return resp['cnt']

apis = {
  "brainshop" : {
    "token": os.environ.get("AI_BRAINSHOP_TOKEN"),
    "function": brainshop
  }
}
async def ai_message(message, api = "brainshop", mention = True):
  global lang_current_group, lang_current_id
  if isinstance(message.channel, discord.channel.DMChannel):
    lang_current_group = "users"
    lang_current_id = message.author.id
  else:
    lang_current_group = "guilds"
    lang_current_id = message.guild.id
  async with message.channel.typing():
    resp = ""
    try:
      if api in apis:
        resp = apis[api]["function"](message.content, message.author.id, apis[api]["token"])
      if get_lang_code(id=lang_current_id, group=lang_current_group) != "en" and get_translate(id=lang_current_id, group=lang_current_group):
        resp = ts.translate_text(resp, translator= "google", to_language=get_lang_code(id=lang_current_id, group=lang_current_group)) 
      #for resp in resps['choices']:
        #await message.channel.send(resp['message']['content'])
    except Exception as e:
      print(str(e))
      resp = "An error occurred please contact with my developer!"
    resp = resp.replace("<tips> enJoke </tips>", "")
    if mention:
      await message.channel.send(f"{message.author.mention}, {resp}")
    else:
      await message.channel.send(f"{resp}")