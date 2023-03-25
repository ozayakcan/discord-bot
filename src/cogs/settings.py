import discord
from discord.ext import commands

from settings.settings import get_lang_string, get_supported_langs, update_settings, get_translate

settings_current_id = 0
settings_current_group = "guilds"

class Settings(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot
    self.delete_delay = 5

  async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
    await ctx.send(get_lang_string(id=settings_current_id, group=settings_current_group, key="an_error_ocurred").format(str(error)), delete_after=self.delete_delay)

  async def cog_before_invoke(self, ctx: commands.Context):
    global settings_current_group, settings_current_id
    if isinstance(ctx.channel, discord.channel.DMChannel):
      settings_current_group = "users"
      settings_current_id = ctx.message.author.id
    else:
      settings_current_group = "guilds"
      settings_current_id = ctx.guild.id

  async def cog_after_invoke(self, ctx: commands.Context):
    member = ctx.message.guild.get_member(self.bot.user.id)
    if member.guild_permissions.manage_messages:
      try:
        await ctx.message.delete(delay=self.delete_delay)
      except Exception as e:
        print(e)

  @commands.command(name='lang', brief=get_lang_string(id=settings_current_id, group=settings_current_group, key="lang_desc"), description=get_lang_string(id=settings_current_id, group=settings_current_group, key="lang_desc_full").format(", ".join(get_supported_langs())))
  async def _lang(self, ctx: commands.Context, *, lang_code: str = commands.parameter(default=None, description=get_lang_string(id=settings_current_id, group=settings_current_group, key="lang_code_desc"))):

    supported_langs = get_supported_langs()
    if lang_code:
      if not isinstance(ctx.channel, discord.channel.DMChannel):
        if not ctx.message.author.guild_permissions.manage_messages:
          return await ctx.send(get_lang_string(id=settings_current_id, group=settings_current_group, key="manage_messages"), delete_after=self.delete_delay)
      if lang_code in supported_langs:
        try:
          update_settings(ctx=ctx, key="lang", value=lang_code)
          await ctx.send(get_lang_string(id=settings_current_id, group=settings_current_group, key="lang_changed"), delete_after=self.delete_delay)
        except Exception as e:
          print(str(e))
          await ctx.send(get_lang_string(id=settings_current_id, group=settings_current_group, key="lang_not_changed"), delete_after=self.delete_delay)
      else:
        await ctx.send(get_lang_string(id=settings_current_id, group=settings_current_group, key="lang_not_supported").format(lang_code, ctx.clean_prefix, "supported_langs"), delete_after=self.delete_delay)
    else:
      await ctx.send(get_lang_string(id=settings_current_id, group=settings_current_group, key="lang_current"), delete_after=self.delete_delay)

  @commands.command(name='supported_langs', brief=get_lang_string(id=settings_current_id, group=settings_current_group, key="supported_langs_desc"), description=get_lang_string(id=settings_current_id, group=settings_current_group, key="supported_langs_desc"))
  async def _supported_langs(self, ctx: commands.Context):

    await ctx.send(get_lang_string(id=settings_current_id, group=settings_current_group, key="supported_langs").format(", ".join(get_supported_langs())), delete_after=self.delete_delay)

  @commands.command(name='translate', brief=get_lang_string(id=settings_current_id, group=settings_current_group, key="translate_desc"), description=get_lang_string(id=settings_current_id, group=settings_current_group, key="translate_desc"))
  async def _translate(self, ctx: commands.Context):

    if not isinstance(ctx.channel, discord.channel.DMChannel):
      if not ctx.message.author.guild_permissions.manage_messages:
        return await ctx.send(get_lang_string(id=settings_current_id, group=settings_current_group, key="manage_messages"), delete_after=self.delete_delay)

    translate = not get_translate(id=settings_current_id, group=settings_current_group)
    update_settings(ctx=ctx, key="translate", value=translate)

    if translate:
      await ctx.send(get_lang_string(id=settings_current_id, group=settings_current_group, key="translate_enabled"), delete_after=self.delete_delay)
    else:
      await ctx.send(get_lang_string(id=settings_current_id, group=settings_current_group, key="translate_disabled"), delete_after=self.delete_delay)

async def setup(bot):
  await bot.add_cog(Settings(bot))