import translators as ts
from discord.ext import commands

from utils import settings

class Translate(commands.Cog, description=settings.lang_string("translate_desc")):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
    await settings.send_cog_error(ctx=ctx, error=error)
    
  async def cog_before_invoke(self, ctx: commands.Context):
    settings.update_currents(ctx=ctx)

  @commands.hybrid_command(name='translate', aliases=["tr"], brief=settings.lang_string("translate_desc"), description=settings.lang_string("translate_desc"))
  async def _translate(self, ctx: commands.Context, *, translate: str = commands.parameter( description=settings.lang_string("translate_arg_desc"))):

    async with ctx.typing():
      resp = ts.translate_text(translate, translator= "google", to_language=settings.lang_code) 
      await ctx.send(resp)

async def setup(bot):
  await bot.add_cog(Translate(bot))