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

  # Logs
  def log_channel_exists(self, settings, current_channel_id: int = None):
    if current_channel_id is None:
      return settings.log_channel != 0
    else:
      return settings.log_channel != 0 and settings.log_channel != current_channel_id

  # Member Logs
  async def on_member_join(self, member):
    try:
      settings.update_currents(guild=member.guild)
      if not self.log_channel_exists(settings):
        return
      embed = discord.Embed(title=settings.lang_string("joined_guild"), description=f"{member.mention}")
      log_channel = self.get_channel(settings.log_channel)
      await log_channel.send(embed=embed)
    except Exception as e:
      print("on_member_join(): "+str(e))
      
  async def on_raw_member_remove(self, payload):
    try:
      guild = self.get_guild(payload.guild_id)
      settings.update_currents(guild=guild)
      if not self.log_channel_exists(settings):
        return
      embed = discord.Embed(title=settings.lang_string("leaved_guild"), description=f"{payload.user.mention}")
      log_channel = self.get_channel(settings.log_channel)
      await log_channel.send(embed=embed)
    except Exception as e:
      print("on_raw_member_remove(): "+str(e))
      
  async def on_member_update(self, before, after):
    try:
      guild = self.get_guild(after.guild.id)
      settings.update_currents(guild=guild)
      if not self.log_channel_exists(settings):
        return
      if before.roles == after.roles:
        return
      async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.member_update):
        description = ""
        for role_after in after.roles:
          if role_after not in before.roles:
            description = description+settings.lang_string("added_role_description").format(f"{after.mention}", f"{role_after.mention}", f"{entry.user.mention}")
        for role_before in before.roles:
          if role_before not in after.roles:
            description = description+settings.lang_string("removed_role_description").format(f"{before.mention}", f"{role_before.mention}", f"{entry.user.mention}")
        if description != "":
          embed = discord.Embed(title= settings.lang_string("role_updated"), description=description)
          log_channel = self.get_channel(settings.log_channel)
          await log_channel.send(embed=embed)
    except Exception as e:
      print("on_member_update(): "+str(e))

  async def ban_log(self, guild, user, action: discord.AuditLogAction, title: str, description: str):
    settings.update_currents(guild=guild)
    log_channel = self.get_channel(settings.log_channel)
    if not self.log_channel_exists(settings):
      return
    async for entry in guild.audit_logs(limit=1, action=action):
      embed = discord.Embed(title=settings.lang_string(title), description=settings.lang_string(description).format(f"{user.mention}", f"{entry.user.mention}"))
      if entry.reason is not None:
        embed.add_field(name=settings.lang_string("reason"), value=f"{entry.reason}", inline=False)
      await log_channel.send(embed=embed)

  async def on_member_ban(self, guild, user):
    try:
      await self.ban_log(guild, user, discord.AuditLogAction.ban, "user_banned", "banned_description")
    except Exception as e:
      print("on_member_ban(): "+str(e))

  async def on_member_unban(self, guild, user):
    try:
      await self.ban_log(guild, user, discord.AuditLogAction.unban, "user_unbanned", "unbanned_description")
    except Exception as e:
      print("on_member_unban(): "+str(e))

  # Role logs
  async def guild_role_update_log(self, role, action: discord.AuditLogAction, title: str, description: str):
    guild = role.guild
    settings.update_currents(guild=role.guild)
    if not self.log_channel_exists(settings):
      return
    async for entry in guild.audit_logs(limit=1, action=action):
      if action == discord.AuditLogAction.role_delete:
        description = settings.lang_string(description).format(f"{role.name}", f"{entry.user.mention}")
      else:
        description = settings.lang_string(description).format(f"{role.mention}", f"{entry.user.mention}")
  
      embed = discord.Embed(title=settings.lang_string(title), description=description)
      log_channel = self.get_channel(settings.log_channel)
      await log_channel.send(embed=embed)
  
  async def on_guild_role_create(self, role):
    try:
      await self.guild_role_update_log(role, discord.AuditLogAction.role_create, "role_created", "role_created_description")
    except Exception as e:
      print("on_guild_role_create(): "+str(e))

  async def on_guild_role_delete(self, role):
    try:
      await self.guild_role_update_log(role, discord.AuditLogAction.role_delete, "role_deleted", "role_deleted_description")
    except Exception as e:
      print("on_guild_role_delete(): "+str(e))

  async def on_guild_role_update(self, before, after):
    guild = after.guild
    settings.update_currents(guild=after.guild)
    if not self.log_channel_exists(settings):
      return
    if before.name == after.name:
      return
    async for entry in guild.audit_logs(limit=1, action= discord.AuditLogAction.role_update):
      embed = discord.Embed(title=settings.lang_string("role_updated"), description=settings.lang_string("role_renamed_description").format(f"{before.name}", f"{after.mention}", f"{entry.user.mention}"))
      log_channel = self.get_channel(settings.log_channel)
      await log_channel.send(embed=embed)
      