import discord
from discord.ext import commands

from utils import settings, views

class Settings(commands.Cog, description=settings.lang_string("settings_cog_desc")):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
    await settings.send_cog_error(ctx=ctx, error=error)

  async def cog_before_invoke(self, ctx: commands.Context):
    settings.update_currents(ctx=ctx)

  async def cog_after_invoke(self, ctx: commands.Context):
    if settings.is_guild(ctx):
      member = ctx.message.guild.get_member(self.bot.user.id)
      if member.guild_permissions.manage_messages:
        try:
          await ctx.message.delete(delay=settings.message_delete_delay)
        except Exception as e:
          print(e)

  async def change_language(self, interaction: discord.Interaction, ctx: commands.Context, values):
    settings.update_currents(interaction=interaction)
    if interaction.guild:
      if not interaction.message.author.guild_permissions.manage_messages:
        return await interaction.response.send_message(settings.lang_string("manage_messages"), delete_after=settings.message_delete_delay)
    try:
      settings.lang_code = values[0]
      await ctx.send(settings.lang_string("lang_change_success"), delete_after=settings.message_delete_delay)
      await interaction.message.delete()
    except Exception as e:
      print("Changing language failed: "+str(e))
      await interaction.response.send_message(settings.lang_string("lang_change_failed"), delete_after=settings.message_delete_delay)
  
  @commands.hybrid_command(name='lang', brief=settings.lang_string("lang_desc"), description=settings.lang_string("lang_desc"))
  async def _lang(self, ctx: commands.Context):
    if settings.is_guild(ctx):
      if ctx.message.author.guild_permissions.manage_messages:
        options = []
        for lang in settings.supported_langs:
          options.append(
            discord.SelectOption(
              label=settings.lang_string(
                "lang", 
                lang_code=lang
              ),
              value=lang,
              description=settings.lang_string(
                "lang_select_desc", 
                lang_code=lang
              )
            )
          )
        view = views.DropdownView(
          ctx=ctx,
          options=options,
          placeholder=settings.lang_string("lang_choose"),
          on_select=self.change_language
        )
        return await ctx.send(settings.lang_string("lang_current"), view=view)
    await ctx.send(settings.lang_string("lang_current"))

  @commands.hybrid_command(name='chat_translate', brief=settings.lang_string("chat_translate_desc"), description=settings.lang_string("chat_translate_desc"))
  async def _translate(self, ctx: commands.Context):

    if settings.is_guild(ctx):
      if not ctx.message.author.guild_permissions.manage_messages:
        return await ctx.send(settings.lang_string("manage_messages"), delete_after=settings.message_delete_delay)

    settings.translate = not settings.translate
    if settings.translate:
      await ctx.send(settings.lang_string("chat_translate_enabled"), delete_after=settings.message_delete_delay)
    else:
      await ctx.send(settings.lang_string("chat_translate_disabled"), delete_after=settings.message_delete_delay)

  @commands.hybrid_command(name='chat', brief=settings.lang_string("chat_desc"), description=settings.lang_string("chat_desc"))
  async def _chat(self, ctx: commands.Context):

    if isinstance(ctx.channel, discord.channel.DMChannel):
      return await ctx.send(settings.lang_string("chat_in_dm"), delete_after=settings.message_delete_delay)
    channel_ids = settings.chat_channels
    channel_id = ctx.channel.id
    if channel_id in channel_ids:
      channel_ids.remove(channel_id)
      settings.chat_channels = channel_ids
      await ctx.send(settings.lang_string("chat_bot_disabled"), delete_after=settings.message_delete_delay)
    else:
      channel_ids.append(channel_id)
      settings.chat_channels = channel_ids
      await ctx.send(settings.lang_string("chat_bot_enabled"), delete_after=settings.message_delete_delay)

  #@commands.hybrid_command(name='debug', brief=settings.lang_string("debug_desc"), description=settings.lang_string("debug_desc"))
  #async def _debug(self, ctx: commands.Context):

  #  settings.debug = not settings.debug
  #  if settings.debug:
  #    await ctx.send(settings.lang_string("debug_enabled"), delete_after=settings.message_delete_delay)
  #  else:
  #    await ctx.send(settings.lang_string("debug_disabled"), delete_after=settings.message_delete_delay)

  @commands.command(name='sync', hidden=True, brief=settings.lang_string("sync_desc"), description=settings.lang_string("sync_desc"))
  async def _sync(self, ctx: commands.Context):
    async with ctx.typing():
      if settings.is_guild(ctx):
        if ctx.message.author.guild_permissions.administrator:
          return await ctx.send(settings.lang_string("admin_permission_err"), delete_after=settings.message_delete_delay)
      try:
        await ctx.bot.tree.sync()
        await ctx.send(settings.lang_string("sync_success"), delete_after=settings.message_delete_delay)
      except Exception as e:
        print(str(e))
        raise commands.CommandError(str(e))

async def setup(bot):
  await bot.add_cog(Settings(bot))