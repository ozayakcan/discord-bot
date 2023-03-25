import os
from keep_alive import keep_alive
import asyncio
import discord
import json
from ai_message import ai_message
from discord.ext import commands
from extensions import get_extensions

command_prefix = os.environ.get("COMMAND_PREFIX")
if command_prefix is None:
  command_prefix = "!"
  
FFMPEG_PATH = os.environ.get("FFMPEG_PATH")
discord.opus.load_opus("./src/libopus.so.0.8.0")

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix,intents=intents, help_command=None)

@bot.event
async def on_ready():
  print(f"We have logged in as {bot.user}")
  await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name=command_prefix+"play - "+command_prefix+"p"))

channel_ids = json.loads(os.environ.get("CHANNEL_IDS"))

lang_current_id = 0
lang_current_group = "guilds"

@bot.event
async def on_message(message):
  if message.author == bot.user:
    return
  global lang_current_group, lang_current_id
  if not message.content.startswith(command_prefix):
    if isinstance(message.channel, discord.channel.DMChannel):
      lang_current_group = "users"
      lang_current_id = message.author.id
    else:
      lang_current_group = "guilds"
      lang_current_id = message.guild.id
    if str(message.channel.id) in channel_ids or isinstance(message.channel, discord.channel.DMChannel):
      await ai_message(message=message, group=lang_current_group, id=lang_current_id , mention = not isinstance(message.channel, discord.channel.DMChannel))
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