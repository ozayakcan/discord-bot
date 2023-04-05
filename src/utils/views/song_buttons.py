import discord
from discord.ext import commands
from utils import settings

__all__ = [
  "SongButtons"
]

class SongButtons(discord.ui.View):
  def __init__(self, on_select, ctx: commands.Context, values):
    super().__init__()
    self.on_select = on_select
    self.__values__ = values
    self.__ctx__ = ctx

  async def is_requester(self, interaction: discord.Interaction, value):
    settings.update_currents(interaction=interaction)
    is_reqstr = interaction.user.id == value.requester.id
    if not is_reqstr:
      await interaction.response.send_message(settings.lang_string("only_requester_warning").format(interaction.user.mention))
      return False
    else:
      return True

  @discord.ui.button(label='1', style=discord.ButtonStyle.primary)
  async def song1(self, interaction: discord.Interaction, button: discord.ui.Button):
    value = self.__values__[0]
    if await self.is_requester(interaction, value):
      if len(self.__values__) < 1:
        await self.on_select(self.__ctx__, None, interaction)
      else:
        await self.on_select(self.__ctx__, value, interaction)

  @discord.ui.button(label='2', style=discord.ButtonStyle.primary)
  async def song2(self, interaction: discord.Interaction, button: discord.ui.Button):
    value = self.__values__[1]
    if await self.is_requester(interaction, value):
      if len(self.__values__) < 2:
        await self.on_select(self.__ctx__, None, interaction)
      else:
        await self.on_select(self.__ctx__, value, interaction)

  @discord.ui.button(label='3', style=discord.ButtonStyle.primary)
  async def song3(self, interaction: discord.Interaction, button: discord.ui.Button):
    value = self.__values__[2]
    if await self.is_requester(interaction, value):
      if len(self.__values__) < 3:
        await self.on_select(self.__ctx__, None, interaction)
      else:
        await self.on_select(self.__ctx__, value, interaction)

  @discord.ui.button(label='4', style=discord.ButtonStyle.primary)
  async def song4(self, interaction: discord.Interaction, button: discord.ui.Button):
    value = self.__values__[3]
    if await self.is_requester(interaction, value):
      if len(self.__values__) < 4:
        await self.on_select(self.__ctx__, None, interaction)
      else:
        await self.on_select(self.__ctx__, value, interaction)

  @discord.ui.button(label='5', style=discord.ButtonStyle.primary)
  async def song5(self, interaction: discord.Interaction, button: discord.ui.Button):
    value = self.__values__[4]
    if await self.is_requester(interaction, value):
      if len(self.__values__) < 5:
        await self.on_select(self.__ctx__, None, interaction)
      else:
        await self.on_select(self.__ctx__, value, interaction)