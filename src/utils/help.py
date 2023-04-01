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
