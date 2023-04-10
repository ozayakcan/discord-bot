import os
import requests

import translators as ts
import discord
from discord.ext import commands

from ._settings import Settings

__all__ = (
    'chat_bot',
)

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
async def chat_bot(bot: commands.Bot, message: discord.Message, settings: Settings, api = "brainshop", mention = True):
  async with message.channel.typing():
    resp = ""
    try:
      if api in apis:
        resp = apis[api]["function"](message.content.replace(bot.user.mention, ""), message.author.id, apis[api]["token"])
      if settings.lang_code != "en" and settings.translate:
        resp = ts.translate_text(resp, translator= "google", to_language=settings.lang_code) 
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