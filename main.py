import os
from keep_alive import keep_alive
import asyncio
import discord
import json
from ai_message import ai_message
from discord.ext import commands

command_prefix = os.environ.get("COMMAND_PREFIX")
if command_prefix is None:
  command_prefix = "!"
  
FFMPEG_PATH = '/home/runner/Discord-Chat-Bot/node_modules/ffmpeg-static/ffmpeg'
discord.opus.load_opus("./libopus.so.0.8.0")

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix,intents=intents, description='Chat bot.')

@bot.event
async def on_ready():
  print(f'We have logged in as {bot.user}')
  await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name=command_prefix+"play"))

channel_ids = json.loads(os.environ.get("CHANNEL_IDS"))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if not message.content.startswith(command_prefix):
      if str(message.channel.id) in channel_ids or not message.guild:
        await ai_message(message, mention = message.guild)
    await bot.process_commands(message)

async def load_extensions():
    for filename in os.listdir("./commands"):
        if filename.endswith(".py"):
            await bot.load_extension(f"commands.{filename[:-3]}")
          
token = os.environ.get("DISCORD_BOT_SECRET") 
async def main():
  async with bot:
    await load_extensions()
    await bot.start(token)
keep_alive()
#bot.run(token)
asyncio.run(main())