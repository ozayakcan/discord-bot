import os

import discord

from extensions.keep_alive import keep_alive
from extensions.bot import MyBot
from os import system
  
FFMPEG_PATH = os.environ.get("FFMPEG_PATH")
discord.opus.load_opus("./src/extensions/libopus.so.0.8.0")

bot = MyBot()

keep_alive()
try:
  bot.run_async()
except discord.errors.HTTPException:
    print("\n\n\nBLOCKED BY RATE LIMITS\nRESTARTING NOW\n\n\n")
    system('kill 1')
    system("python3 ./src/extensions/restarter.py")