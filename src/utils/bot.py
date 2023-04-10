import asyncio
import difflib

import discord
from discord.ext import commands

from ._extensions import get_extensions
from ._settings import settings
from .chat_bot import chat_bot
from .env import getenv

__all__ = (
    'MyBot',
)

command_prefix = getenv("COMMAND_PREFIX")
if command_prefix is None:
  command_prefix = "!"

class MyBot(commands.Bot):

  def __init__(self):
    intents = discord.Intents.all()
    intents.message_content = True
            
    self.mytoken = getenv("DISCORD_BOT_SECRET")
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
      await self.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name=command_prefix+"help"))
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
    else:
      try:
        command_name = message.content.split('!', 1)[1].split(' ', 1)[0]
        command_found = False
        command_names = []
        for cmd in self.commands:
          if command_name == cmd.name:
            command_found = True
            break
          command_names.append(cmd.name)
        if not command_found:
          settings.update_currents(message=message)
          close_matches = difflib.get_close_matches(command_name, command_names)
          if len(close_matches) > 0:
            close_matches = [command_prefix + c_m for c_m in close_matches]
            await message.channel.send(settings.lang_string("command_not_found").format(command_prefix, command_name, settings.lang_string("did_you_mean").format(", ".join(close_matches))))
          else:
            await message.channel.send(settings.lang_string("command_not_found").format(command_prefix, command_name, ""))
      except Exception as e:
        print(str(e))
        
    await super().process_commands(message)