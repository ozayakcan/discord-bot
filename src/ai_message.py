import os
import requests
import translators as ts
from cogs.lang import get_lang_code

def brainshop(message, userid, token):
  resp = requests.get("http://api.brainshop.ai/get?bid=173774&key=" + token + "&uid="+str(userid)+"&msg="+message)
  resp = resp.json()
  return resp['cnt']

language_code = get_lang_code()
translate = os.environ.get("TRANSLATE")
if translate == "True" or translate == "true":
  translate = True
else:
  translate = False

apis = {
  "brainshop" : {
    "token": os.environ.get("AI_BRAINSHOP_TOKEN"),
    "function": brainshop
  }
}
async def ai_message(message, api = "brainshop", mention = True):
  resp = ""
  try:
    if api in apis:
      resp = apis[api]["function"](message.content, message.author.id, apis[api]["token"])
    if language_code is not None and translate:
      resp = ts.translate_text(resp, translator= "google", to_language=language_code) 
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