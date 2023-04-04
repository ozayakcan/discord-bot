from discord.ext import commands

#from extensions.extensions import get_extensions
from utils import settings, HelpCommand

class Help(commands.Cog, description=settings.lang_string("help_cog_desc")):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  
  async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
    await settings.send_cog_error(ctx=ctx, error=error)
    
  async def cog_before_invoke(self, ctx: commands.Context):
    settings.update_currents(ctx=ctx)
    #for extension in get_extensions():
    #  await self.bot.unload_extension(extension)
    #  await self.bot.load_extension(extension)

  @commands.hybrid_command(name='help', aliases=["h"], brief=settings.lang_string("help_desc"), description=settings.lang_string("help_desc_full"))
  async def _help(self, ctx: commands.Context, *, command_name_or_category: str = commands.parameter(default=None, description=settings.lang_string("help_command_name_or_category_desc"))):

    async with ctx.typing():
      self.bot.help_command = HelpCommand(ctx.clean_prefix, settings)
      if command_name_or_category:
        command_def = self.bot.get_cog(command_name_or_category) or self.bot.get_command(command_name_or_category)
        if command_def is None:
          await ctx.send(settings.lang_string("help_not_found").format(command_name_or_category))
        else:
          await ctx.send_help(command_def)
      else:
        await ctx.send_help()

async def setup(bot):
  await bot.add_cog(Help(bot))