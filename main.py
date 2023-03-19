import os
from keep_alive import keep_alive
import discord
import json
from ai_message import ai_message

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

channel_ids = json.loads(os.environ.get("CHANNEL_IDS"))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if str(message.channel.id) in channel_ids:
      await ai_message(message)
    else:
      return

keep_alive()
token = os.environ.get("DISCORD_BOT_SECRET") 
client.run(token)