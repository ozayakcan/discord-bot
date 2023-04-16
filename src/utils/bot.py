import asyncio
import difflib
import json

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
        test_guild = getenv("TEST_GUILD")
        if test_guild is not None:
          await self.tree.sync(guild=discord.Object(int(test_guild)))
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
      if self.user.mentioned_in(message) or isinstance(message.channel, discord.channel.DMChannel):
        await chat_bot(bot=self, message=message, settings=settings, mention = not isinstance(message.channel, discord.channel.DMChannel))
    else:
      try:
        command_name = message.content.split('!', 1)[1].split(' ', 1)[0]
        command_found = False
        excluded_commands = getenv("EXCLUDED_COMMANDS") or "[]"
        excluded_commands = json.loads(excluded_commands)
        command_names = []
        for cmd in self.commands:
          if command_name == cmd.name or command_name in excluded_commands or command_name in cmd.aliases:
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
    
  
  async def on_raw_message_delete(self, payload):
    try:
      guild = self.get_guild(payload.guild_id)
      settings.update_currents(guild=guild)
      if settings.log_channel == payload.channel_id or settings.log_channel == 0:
        return
      log_channel = self.get_channel(settings.log_channel)
      channel = self.get_channel(payload.channel_id)
      async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.message_delete):
        if entry.user.bot:
          break
        print(f"{entry.target}")
        embed = discord.Embed(title= settings.lang_string("message_deleted"))
        embed.add_field(name=settings.lang_string("deleted_by"), value=f"{entry.user.mention}")
        embed.add_field(name=settings.lang_string("channel"), value=f"<#{channel.id}>")
        message = payload.cached_message
        if message is not None:
          content = message.content
          if len(content) >= 1010:
            content = settings.lang_string("message_short").format(content[0:1005])
          embed.add_field(name=settings.lang_string("message"), value=settings.lang_string("message_content_with_user").format(f"{entry.target.mention}", content) , inline=False)
        await log_channel.send(embed=embed)
    except Exception as e:
      print("on_raw_message_delete(): "+str(e))

  async def on_raw_message_edit(self, payload):
    try:
      guild = self.get_guild(payload.guild_id)
      settings.update_currents(guild=guild)
      if settings.log_channel == payload.channel_id or settings.log_channel == 0:
        return
      log_channel = self.get_channel(settings.log_channel)
      channel = self.get_channel(payload.channel_id)
      message = await channel.fetch_message(payload.message_id)
      if message.author.bot:
        return
      embed = discord.Embed(title= settings.lang_string("message_updated"))
      embed.add_field(name=settings.lang_string("updated_by"), value=f"{message.author.mention}")
      embed.add_field(name=settings.lang_string("channel"), value=f"<#{channel.id}>")
      embed.add_field(name=settings.lang_string("url"), value=settings.lang_string("click").format(message.jump_url), inline=False)
      cached_m = payload.cached_message
      if cached_m is not None:
        old_content = cached_m.content
        if len(old_content) >= 1010:
          old_content = settings.lang_string("message_short").format(old_content[0:1005])
        new_content = message.content
        if len(new_content) >= 1010:
          new_content = settings.lang_string("message_short").format(new_content[0:1005])
        embed.add_field(name=settings.lang_string("old_message"), value=old_content)
        embed.add_field(name=settings.lang_string("new_message"), value=new_content)
      await log_channel.send(embed=embed)
    except Exception as e:
      print("on_raw_message_edit(): "+str(e))