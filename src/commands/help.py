import os
from discord.ext import commands
from commands.lang import get_lang_string, set_current_lang_infos
from extensions import get_extensions

class MyHelpCommand(commands.DefaultHelpCommand):
    def __init__(self, prefix):
      self.prefix = prefix
      super().__init__(
        command_attrs={
          'name': "xcvsad",
          'hidden': True,
        },
        no_category = get_lang_string("no_category"),
        default_argument_description = get_lang_string("help_arg_desc"),
        arguments_heading = get_lang_string("arguments_heading"),
        commands_heading = get_lang_string("commands_heading"),
        width = 150
      )
    def get_ending_note(self):
        return get_lang_string("help_ending_note").format(self.prefix, self.prefix)

class Help(commands.Cog):
  def __init__(self, bot: commands.Bot):
        self.bot = bot

  async def cog_before_invoke(self, ctx: commands.Context):
      set_current_lang_infos(guild=ctx.guild, author=ctx.message.author)
      for extension in get_extensions():
          await self.bot.unload_extension(extension)
          await self.bot.load_extension(extension)

  @commands.command(name='help', aliases=get_lang_string("help_aliases"), brief=get_lang_string("help_desc"), description=get_lang_string("help_desc_full"))
  async def _help(self, ctx: commands.Context, *, input: str = commands.parameter(default=None, description=get_lang_string("help_input_desc"))):
    async with ctx.typing():
      self.bot.help_command = MyHelpCommand(ctx.clean_prefix)
      if input:
        command_def = self.bot.get_cog(input) or self.bot.get_command(input)
        if command_def is None:
          await ctx.send(get_lang_string("help_not_found").format(input))
        else:
          await ctx.send_help(command_def)
      else:
        await ctx.send_help()

async def setup(bot):
  await bot.add_cog(Help(bot))