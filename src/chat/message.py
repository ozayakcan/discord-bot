import os
import requests

import translators as ts
import discord

from settings.settings import get_lang_code, get_translate

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
async def chat_message(message: discord.Message, group: str, id: int, api = "brainshop", mention = True):
  async with message.channel.typing():
    resp = ""
    try:
      if api in apis:
        resp = apis[api]["function"](message.content, message.author.id, apis[api]["token"])
      if get_lang_code(id=id, group=group) != "en" and get_translate(id=id, group=group):
        resp = ts.translate_text(resp, translator= "google", to_language=get_lang_code(id=id, group=group)) 
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