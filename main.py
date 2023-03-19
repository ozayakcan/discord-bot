import os
from keep_alive import keep_alive
import discord
from ai_message import ai_message

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    await ai_message(message)

keep_alive()
token = os.environ.get("DISCORD_BOT_SECRET") 
client.run(token)