import discord

from os import system

from utils import MyBot, keep_alive, getenv

# Comment this two lines if not running in replit
FFMPEG_PATH = getenv("FFMPEG_PATH")
discord.opus.load_opus("./src/assets/opus/libopus.so.0.8.0")

bot = MyBot()

keep_alive()
try:
  bot.run_async()
except discord.errors.HTTPException:
    print("\n\n\nBLOCKED BY RATE LIMITS\nRESTARTING NOW\n\n\n")
    system("python3 ./src/utils/restarter.py")
    system('kill 1')