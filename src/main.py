import os
import asyncio

import discord
from discord.ext import commands

from chat.message import chat_message
from extensions.extensions import get_extensions
from extensions.keep_alive import keep_alive
from settings.settings import get_chat_channels

command_prefix = os.environ.get("COMMAND_PREFIX")
if command_prefix is None:
  command_prefix = "!"
  
FFMPEG_PATH = os.environ.get("FFMPEG_PATH")
discord.opus.load_opus("./src/extensions/libopus.so.0.8.0")

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix,intents=intents, help_command=None)

@bot.event
async def on_ready():
  print(f"We have logged in as {bot.user}")
  await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name=command_prefix+"play - "+command_prefix+"p"))

settings_current_group = "guilds"
settings_current_id = 0

@bot.event
async def on_message(message):
  if message.author == bot.user:
    return
  global settings_current_group, settings_current_id
  if not message.content.startswith(command_prefix):
    if isinstance(message.channel, discord.channel.DMChannel):
      settings_current_group = "users"
      settings_current_id = message.author.id
    else:
      settings_current_group = "guilds"
      settings_current_id = message.guild.id
    if message.channel.id in get_chat_channels( group=settings_current_group, id=settings_current_id) or isinstance(message.channel, discord.channel.DMChannel):
      await chat_message(message=message, group=settings_current_group, id=settings_current_id , mention = not isinstance(message.channel, discord.channel.DMChannel))
  await bot.process_commands(message)

async def load_extensions():
  for extension in get_extensions():
    await bot.load_extension(extension)
          
token = os.environ.get("DISCORD_BOT_SECRET") 
async def main():
  async with bot:
    await load_extensions()
    await bot.start(token)

keep_alive()

#bot.run(token)
asyncio.run(main())