import os

import discord

from extensions.keep_alive import keep_alive
from extensions.bot import MyBot
  
FFMPEG_PATH = os.environ.get("FFMPEG_PATH")
discord.opus.load_opus("./src/extensions/libopus.so.0.8.0")

bot = MyBot()

keep_alive()

bot.run_async()