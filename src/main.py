import os

import discord

from utils import MyBot, keep_alive
from os import system
  
FFMPEG_PATH = os.environ.get("FFMPEG_PATH")
discord.opus.load_opus("./src/assets/opus/libopus.so.0.8.0")

bot = MyBot()

keep_alive()
try:
  bot.run_async()
except discord.errors.HTTPException:
    print("\n\n\nBLOCKED BY RATE LIMITS\nRESTARTING NOW\n\n\n")
    system('kill 1')
    system("python3 ./src/utils/restarter.py")