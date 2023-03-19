import os
import requests


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
async def ai_message(message, api = "brainshop"):
  resp = ""
  if api in apis:
    resp = apis[api]["function"](message.content, message.author.id, apis[api]["token"])
  await message.channel.send(f"{message.author.mention}, {resp}")
  #for resp in resps['choices']:
    #await message.channel.send(resp['message']['content'])
