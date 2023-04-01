import asyncio
import os

import discord
from discord.ext import commands

from ._extensions import get_extensions
from ._settings import settings
from .message import bot as chat_bot

command_prefix = os.environ.get("COMMAND_PREFIX")
if command_prefix is None:
  command_prefix = "!"

class MyBot(commands.Bot):

  def __init__(self):
    intents = discord.Intents.all()
    intents.message_content = True
            
    self.mytoken = os.environ.get("DISCORD_BOT_SECRET")
    self.synced = False
    
    super().__init__(command_prefix,intents=intents, help_command=None)

  async def load_my_extensions(self):
    for extension in get_extensions():
      await super().load_extension(extension)

  async def _main_run(self):
    async with self:
      await self.load_my_extensions()
      await self.start(self.mytoken)

  def run_async(self):
    asyncio.run(self._main_run())

  async def on_ready(self):
    try:
      await self.wait_until_ready()
      if not self.synced:
        await self.tree.sync()
        self.synced = True
      await self.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name=command_prefix+"play - "+command_prefix+"p"))
      print(f"We have logged in as {self.user}")
    except Exception as e:
      print("on_ready error: "+str(e))
  async def on_message(self, message):
    if message.author == self.user:
      return
    if not message.content.startswith(command_prefix):
      settings.update_currents(message=message)
      if message.channel.id in settings.chat_channels or isinstance(message.channel, discord.channel.DMChannel):
        await chat_bot(message=message, settings=settings, mention = not isinstance(message.channel, discord.channel.DMChannel))
    await super().process_commands(message)