from discord.ext.commands import DefaultHelpCommand
from lang.lang import lang

class MyHelpCommand(DefaultHelpCommand):
    def __init__(self, prefix):
      self.prefix = prefix
      super().__init__(
        command_attrs={
          'name': "help",
          'aliases': lang["help_aliases"],
          'brief': lang["help_desc"],
          'description': lang["help_desc_full"],
        },
        no_category = lang["no_category"],
        default_argument_description = lang["help_arg_desc"],
        arguments_heading = lang["arguments_heading"],
        commands_heading = lang["commands_heading"]
      )
    def get_ending_note(self):
        return lang["help_ending_note"].format(self.prefix, self.prefix)