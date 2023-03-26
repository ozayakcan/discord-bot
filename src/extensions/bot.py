import asyncio
import os

import discord
from discord.ext import commands

from chat.message import chat_message
from extensions.extensions import get_extensions
from settings.settings import get_chat_channels

settings_current_group = "guilds"
settings_current_id = 0

command_prefix = os.environ.get("COMMAND_PREFIX")
if command_prefix is None:
  command_prefix = "!"

class MyBot(commands.Bot):

  def __init__(self):
    intents = discord.Intents.all()
    intents.message_content = True
            
    self.mytoken = os.environ.get("DISCORD_BOT_SECRET") 
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
    print(f"We have logged in as {self.user}")
    await self.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name=command_prefix+"play - "+command_prefix+"p"))

  async def on_message(self, message):
    if message.author == self.user:
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
    await super().process_commands(message)