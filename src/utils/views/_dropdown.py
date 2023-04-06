import discord
from discord.ext import commands

__all__ = (
    'DropdownView',
)

class Dropdown(discord.ui.Select):
  def __init__(self, ctx: commands.Context, options: list[discord.SelectOption], placeholder, on_select, min_values: int = 1, max_values: int = 1):
    self.on_select = on_select
    self.__ctx__ = ctx
    super().__init__(placeholder=placeholder, min_values=min_values, max_values=max_values, options=options)

  async def callback(self, interaction: discord.Interaction):
    await self.on_select(interaction, self.__ctx__, self.values)


class DropdownView(discord.ui.View):
  def __init__(self, ctx: commands.Context, options: list[discord.SelectOption], placeholder, on_select, min_values: int = 1, max_values: int = 1):
    super().__init__()
    self.add_item(Dropdown(ctx=ctx,options=options, placeholder=placeholder, on_select=on_select, min_values=min_values, max_values=max_values))

  