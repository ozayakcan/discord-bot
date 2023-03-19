import os
from wit import Wit

ai_token = os.environ.get("AI_SECRET") 

wit_client = Wit(ai_token)

async def ai_message(message):
  resp = wit_client.message(message.content)
  await message.channel.send(f"{message.author.mention}, {resp['text']}")
  #for resp in resps['choices']:
    #await message.channel.send(resp['message']['content'])
