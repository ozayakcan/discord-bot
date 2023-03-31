import discord
from discord import app_commands
from discord.ext import commands

from settings.settings import default_settings, is_guild, get_lang_string, get_supported_langs, set_lang_code, set_translate, get_translate, set_chat_channels, get_chat_channels, set_debug, get_debug

settings_current_group = "guilds"
settings_current_id = 0

class Settings(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
    await default_settings.send_cog_error(group=settings_current_group, id=settings_current_id, ctx=ctx, error=error)

  async def cog_before_invoke(self, ctx: commands.Context):
    global settings_current_group, settings_current_id
    if is_guild(ctx):
      settings_current_group = "guilds"
      settings_current_id = ctx.guild.id
    else:
      settings_current_group = "users"
      settings_current_id = ctx.message.author.id

  async def cog_after_invoke(self, ctx: commands.Context):
    if is_guild(ctx):
      member = ctx.message.guild.get_member(self.bot.user.id)
      if member.guild_permissions.manage_messages:
        try:
          await ctx.message.delete(delay=default_settings.message_delete_delay)
        except Exception as e:
          print(e)

  @commands.hybrid_command(name='lang', brief=get_lang_string(group=settings_current_group, id=settings_current_id, key="lang_desc"), description=get_lang_string(group=settings_current_group, id=settings_current_id, key="lang_desc"))
  async def _lang(self, ctx: commands.Context, *, lang_code: str = commands.parameter(default=None, description=get_lang_string(group=settings_current_group, id=settings_current_id, key="lang_code_desc"))):

    supported_langs = get_supported_langs()
    if lang_code:
      if is_guild(ctx):
        if not ctx.message.author.guild_permissions.manage_messages:
          return await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="manage_messages"), delete_after=default_settings.message_delete_delay)
      if lang_code in supported_langs:
        try:
          set_lang_code(group=settings_current_group, id=settings_current_id, lang=lang_code)
          await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="lang_changed"), delete_after=default_settings.message_delete_delay)
        except Exception as e:
          print(str(e))
          await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="lang_not_changed"), delete_after=default_settings.message_delete_delay)
      else:
        await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="lang_not_supported").format(lang_code, ctx.clean_prefix, "supported_langs"), delete_after=default_settings.message_delete_delay)
    else:
      await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="lang_current"), delete_after=default_settings.message_delete_delay)
      
  @_lang.autocomplete('lang_code')
  async def _lang_autocomplete(self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
    langs = get_supported_langs()
    return [
        app_commands.Choice(name=lang, value=lang)
        for lang in langs if current.lower() in lang.lower()
    ]
  @commands.hybrid_command(name='supported_langs', brief=get_lang_string(group=settings_current_group, id=settings_current_id, key="supported_langs_desc"), description=get_lang_string(group=settings_current_group, id=settings_current_id, key="supported_langs_desc"))
  async def _supported_langs(self, ctx: commands.Context):

    await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="supported_langs").format(", ".join(get_supported_langs())), delete_after=default_settings.message_delete_delay)

  @commands.hybrid_command(name='chat_translate', brief=get_lang_string(group=settings_current_group, id=settings_current_id, key="chat_translate_desc"), description=get_lang_string(group=settings_current_group, id=settings_current_id, key="chat_translate_desc"))
  async def _translate(self, ctx: commands.Context):

    if is_guild(ctx):
      if not ctx.message.author.guild_permissions.manage_messages:
        return await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="manage_messages"), delete_after=default_settings.message_delete_delay)

    translate = not get_translate( group=settings_current_group, id=settings_current_id)
    set_translate(group=settings_current_group, id=settings_current_id, translate=translate)

    if translate:
      await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="chat_translate_enabled"), delete_after=default_settings.message_delete_delay)
    else:
      await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="chat_translate_disabled"), delete_after=default_settings.message_delete_delay)

  @commands.hybrid_command(name='chat', brief=get_lang_string(group=settings_current_group, id=settings_current_id, key="chat_desc"), description=get_lang_string(group=settings_current_group, id=settings_current_id, key="chat_desc"))
  async def _chat(self, ctx: commands.Context):

    if isinstance(ctx.channel, discord.channel.DMChannel):
      return await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="chat_in_dm"), delete_after=default_settings.message_delete_delay)
    channel_ids = get_chat_channels(group=settings_current_group, id=settings_current_id)
    channel_id = ctx.channel.id
    is_removed = False
    if channel_id in channel_ids:
      channel_ids.remove(channel_id)
      is_removed = True
    else:
      channel_ids.append(channel_id)
      is_removed = False
    set_chat_channels(group=settings_current_group, id=settings_current_id, channel_ids = channel_ids)
    if is_removed:
      await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="chat_bot_disabled"), delete_after=default_settings.message_delete_delay)
    else:
      await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="chat_bot_enabled"), delete_after=default_settings.message_delete_delay)

  #@commands.hybrid_command(name='debug', brief=get_lang_string(group=settings_current_group, id=settings_current_id, key="debug_desc"), description=get_lang_string(group=settings_current_group, id=settings_current_id, key="debug_desc"))
  #async def _debug(self, ctx: commands.Context):

  #  debug = not get_debug(group=settings_current_group, id=settings_current_id)
  #  set_debug(group=settings_current_group, id=settings_current_id, debug=debug)
  #  if debug:
  #    await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="debug_enabled"), delete_after=default_settings.message_delete_delay)
  #  else:
  #    await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="debug_disabled"), delete_after=default_settings.message_delete_delay)

  @commands.command(name='sync', hidden=True, brief=get_lang_string(group=settings_current_group, id=settings_current_id, key="sync_desc"), description=get_lang_string(group=settings_current_group, id=settings_current_id, key="sync_desc"))
  async def _sync(self, ctx: commands.Context):
    async with ctx.typing():
      if is_guild(ctx):
        if ctx.message.author.guild_permissions.administrator:
          return await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="admin_permission_err"), delete_after=default_settings.message_delete_delay)
      try:
        await ctx.bot.tree.sync()
        await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="sync_success"), delete_after=default_settings.message_delete_delay)
      except Exception as e:
        print(str(e))
        raise commands.CommandError(str(e))

async def setup(bot):
  await bot.add_cog(Settings(bot))