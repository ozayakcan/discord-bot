import discord
from discord.ext import commands

from extensions.extensions import get_extensions
from settings.settings import get_lang_string

settings_current_id = 0
settings_current_group = "guilds"

class MyHelpCommand(commands.DefaultHelpCommand):
  def __init__(self, prefix):
    self.prefix = prefix
    super().__init__(
      command_attrs={
        'name': "xcvsad",
        'hidden': True,
      },
      no_category = get_lang_string(id=settings_current_id, group=settings_current_group, key="no_category"),
      default_argument_description = get_lang_string(id=settings_current_id, group=settings_current_group, key="help_arg_desc"),
      arguments_heading = get_lang_string(id=settings_current_id, group=settings_current_group, key="arguments_heading"),
      commands_heading = get_lang_string(id=settings_current_id, group=settings_current_group, key="commands_heading"),
      width = 150
    )
  def get_ending_note(self):
    return get_lang_string(id=settings_current_id, group=settings_current_group, key="help_ending_note").format(self.prefix, self.prefix)

class Help(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  async def cog_before_invoke(self, ctx: commands.Context):
    global settings_current_group, settings_current_id
    if isinstance(ctx.channel, discord.channel.DMChannel):
      settings_current_group = "users"
      settings_current_id = ctx.message.author.id
    else:
      settings_current_group = "guilds"
      settings_current_id = ctx.guild.id
    for extension in get_extensions():
      await self.bot.unload_extension(extension)
      await self.bot.load_extension(extension)

  @commands.command(name='help', aliases=get_lang_string(id=settings_current_id, group=settings_current_group, key="help_aliases"), brief=get_lang_string(id=settings_current_id, group=settings_current_group, key="help_desc"), description=get_lang_string(id=settings_current_id, group=settings_current_group, key="help_desc_full"))
  async def _help(self, ctx: commands.Context, *, input: str = commands.parameter(default=None, description=get_lang_string(id=settings_current_id, group=settings_current_group, key="help_input_desc"))):

    async with ctx.typing():
      self.bot.help_command = MyHelpCommand(ctx.clean_prefix)
      if input:
        command_def = self.bot.get_cog(input) or self.bot.get_command(input)
        if command_def is None:
          await ctx.send(get_lang_string(id=settings_current_id, group=settings_current_group, key="help_not_found").format(input))
        else:
          await ctx.send_help(command_def)
      else:
        await ctx.send_help()

async def setup(bot):
  await bot.add_cog(Help(bot))