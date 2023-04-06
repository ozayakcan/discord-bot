import discord
from discord.ext import commands
from utils import settings
from utils.music import SongList

__all__ = [
  "ButtonsSong",
]

class ButtonsSong(discord.ui.View):
  def __init__(self, on_select, ctx: commands.Context, song_list: SongList):
    super().__init__()
    self.on_select = on_select
    self.__song_list__ = song_list
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
    value = self.__song_list__.sources[0]
    if await self.is_requester(interaction, value):
      if len(self.__song_list__.sources) < 1:
        await self.on_select(self.__ctx__, None, interaction)
      else:
        await self.on_select(self.__ctx__, value, interaction)

  @discord.ui.button(label='2', style=discord.ButtonStyle.primary)
  async def song2(self, interaction: discord.Interaction, button: discord.ui.Button):
    value = self.__song_list__.sources[1]
    if await self.is_requester(interaction, value):
      if len(self.__song_list__.sources) < 2:
        await self.on_select(self.__ctx__, None, interaction)
      else:
        await self.on_select(self.__ctx__, value, interaction)

  @discord.ui.button(label='3', style=discord.ButtonStyle.primary)
  async def song3(self, interaction: discord.Interaction, button: discord.ui.Button):
    value = self.__song_list__.sources[2]
    if await self.is_requester(interaction, value):
      if len(self.__song_list__.sources) < 3:
        await self.on_select(self.__ctx__, None, interaction)
      else:
        await self.on_select(self.__ctx__, value, interaction)

  @discord.ui.button(label='4', style=discord.ButtonStyle.primary)
  async def song4(self, interaction: discord.Interaction, button: discord.ui.Button):
    value = self.__song_list__.sources[3]
    if await self.is_requester(interaction, value):
      if len(self.__song_list__.sources) < 4:
        await self.on_select(self.__ctx__, None, interaction)
      else:
        await self.on_select(self.__ctx__, value, interaction)

  @discord.ui.button(label='5', style=discord.ButtonStyle.primary)
  async def song5(self, interaction: discord.Interaction, button: discord.ui.Button):
    value = self.__song_list__.sources[4]
    if await self.is_requester(interaction, value):
      if len(self.__song_list__.sources) < 5:
        await self.on_select(self.__ctx__, None, interaction)
      else:
        await self.on_select(self.__ctx__, value, interaction)