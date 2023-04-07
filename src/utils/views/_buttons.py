import os,sys

import discord
from discord.ext import commands
from utils import settings, music

__all__ = [
  "ButtonsSong",
]

class ButtonsSong(discord.ui.View):
  def __init__(self, on_select, ctx: commands.Context, song_list: list):
    super().__init__()
    self.on_select = on_select
    self.__song_list__ = song_list
    self.__ctx__ = ctx

  async def send_val(self,interaction: discord.Interaction, index):
    try:
      if len(self.__song_list__) < (index + 1):
        await self.on_select(self.__ctx__, None, interaction)
      else:
        value = self.__song_list__[index]
        settings.update_currents(interaction=interaction)
        is_reqstr = interaction.user.id == value["requester"].id
        if not is_reqstr:
          await interaction.response.send_message(settings.lang_string("only_requester_warning").format(interaction.user.mention))
          return
        s_list = await music.YTDLSource.create_source(self.__ctx__, value["url"], loop=self.__ctx__.bot.loop)
        if len(s_list.sources) == 0:
          await interaction.response.send_message(settings.lang_string("error_msg"))
          return
        await self.on_select(self.__ctx__, s_list.sources[0], interaction)
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      print(exc_type, fname, exc_tb.tb_lineno)
      print(e)
      await interaction.response.send_message(settings.lang_string("error_msg"))
    
  @discord.ui.button(label='1', style=discord.ButtonStyle.primary)
  async def song1(self, interaction: discord.Interaction, button: discord.ui.Button):
    await self.send_val(interaction, 0)

  @discord.ui.button(label='2', style=discord.ButtonStyle.primary)
  async def song2(self, interaction: discord.Interaction, button: discord.ui.Button):
    await self.send_val(interaction, 1)

  @discord.ui.button(label='3', style=discord.ButtonStyle.primary)
  async def song3(self, interaction: discord.Interaction, button: discord.ui.Button):
    await self.send_val(interaction, 2)

  @discord.ui.button(label='4', style=discord.ButtonStyle.primary)
  async def song4(self, interaction: discord.Interaction, button: discord.ui.Button):
    await self.send_val(interaction, 3)

  @discord.ui.button(label='5', style=discord.ButtonStyle.primary)
  async def song5(self, interaction: discord.Interaction, button: discord.ui.Button):
    await self.send_val(interaction, 4)