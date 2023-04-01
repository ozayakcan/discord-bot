from discord.ext import commands

#from extensions.extensions import get_extensions
from utils.settings import is_guild, default_settings, get_lang_string

settings_current_group = "guilds"
settings_current_id = 0

class MyHelpCommand(commands.DefaultHelpCommand):
  def __init__(self, prefix):
    self.prefix = prefix
    super().__init__(
      command_attrs={
        'name': "xcvsad",
        'hidden': True,
      },
      no_category = get_lang_string("no_category", group=settings_current_group, id=settings_current_id),
      default_argument_description = get_lang_string("help_arg_desc", group=settings_current_group, id=settings_current_id),
      arguments_heading = get_lang_string("arguments_heading", group=settings_current_group, id=settings_current_id),
      commands_heading = get_lang_string("commands_heading", group=settings_current_group, id=settings_current_id),
      width = 150
    )
  def get_ending_note(self):
    return get_lang_string("help_ending_note", group=settings_current_group, id=settings_current_id).format(self.prefix, self.prefix)

class Help(commands.Cog):
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
    #for extension in get_extensions():
    #  await self.bot.unload_extension(extension)
    #  await self.bot.load_extension(extension)

  @commands.hybrid_command(name='help', aliases=["h"], brief=get_lang_string("help_desc"), description=get_lang_string("help_desc_full"))
  async def _help(self, ctx: commands.Context, *, command_name_or_category: str = commands.parameter(default=None, description=get_lang_string("help_command_name_or_category_desc"))):

    async with ctx.typing():
      self.bot.help_command = MyHelpCommand(ctx.clean_prefix)
      if command_name_or_category:
        command_def = self.bot.get_cog(command_name_or_category) or self.bot.get_command(command_name_or_category)
        if command_def is None:
          await ctx.send(get_lang_string("help_not_found", group=settings_current_group, id=settings_current_id).format(command_name_or_category))
        else:
          await ctx.send_help(command_def)
      else:
        await ctx.send_help()

async def setup(bot):
  await bot.add_cog(Help(bot))