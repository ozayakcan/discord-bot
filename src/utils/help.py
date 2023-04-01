from discord.ext import commands

from ._settings import Settings

class Command(commands.DefaultHelpCommand):
  def __init__(self, prefix: str, settings: Settings):
    self.prefix = prefix
    self.settings = settings
    super().__init__(
      command_attrs={
        'name': "xcvsad",
        'hidden': True,
      },
      no_category = self.settings.lang_string("no_category"),
      default_argument_description = self.settings.lang_string("help_arg_desc"),
      arguments_heading = self.settings.lang_string("arguments_heading"),
      commands_heading = self.settings.lang_string("commands_heading"),
      width = 150
    )
  def get_ending_note(self):
    return self.settings.lang_string("help_ending_note").format(self.prefix, self.prefix)

  def set_bot(self, bot):
    try:
      if bot.description is not None:
        if bot.description != "":
          bot.description = self.settings.lang_from_text(bot.description)
    except Exception as e:
      print("Could not localize bot: "+str(e))

  def set_cogs(self, bot):
    try:
      for cog_name in bot.cogs:
        cog = bot.get_cog(cog_name)
        if cog.description is not None:
          if cog.description != "":
            cog.description = self.settings.lang_from_text(cog.description)
    except Exception as e:
      print("Could not localize cogs: "+str(e))
  
  def set_commands(self, commands):
    try:
      for command in commands:
        self.set_command(command)
    except Exception as e:
      print("Could not localize commands: "+str(e))

  def set_command(self, command):
    try:
      if command.description is not None:
        if command.description != "":
          loc = self.settings.lang_from_text(command.description)
          command.description = loc
          command.brief = loc
    except Exception as e:
      print(f"Could not localize {command.name} command: {str(e)}")

  async def prepare_help_command(self, ctx, command):
    self.set_bot(ctx.bot)
    self.set_cogs(ctx.bot)
    self.set_commands(ctx.bot.commands)
    await super().prepare_help_command(ctx, command)
