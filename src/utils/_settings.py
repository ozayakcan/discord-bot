import os
import json
import lxml.etree
import xmltodict as xd

import discord
from discord.ext import commands

from .env import getenv

__all__ = [
  "settings",
  "Settings",
]

class Settings:
  def __init__(self):
    self.message_delete_delay = 5
    self.__current_group__ = "guilds"
    self.__current_id__ = 0

    # Settings files
    self.__settings_file__ = "./src/configs/settings/{0}/{1}.json"
    # Localization
    self.__lang_folder__ = "./src/configs/langs"
    self.__default_lang_code__ = getenv("DEFAULT_LANGUAGE")
    if self.__default_lang_code__ is None or self.__default_lang_code__ == "":
      self.__default_lang_code__ = "en-US"
    
    #Settings
    self.__lang_str__ = "lang"
    self.__translate_str__ = "translate"
    self.__debug_str__ = "debug"

  async def send_cog_error(self, ctx: commands.Context, error: commands.CommandError):
    await ctx.send(f"{ctx.message.author.mention}, {str(error)}")
    #if get_debug(group=group, id=id):
    #  await ctx.send(str(error), delete_after=self.message_delete_delay)
    #else:
    #  await ctx.send(get_lang_string(group=group, id=id, key="an_error_ocurred").format(ctx.clean_prefix, ctx.invoked_with), delete_after=self.message_delete_delay)

  @property
  def current_group(self):
    return self.__current_group__

  @current_group.setter
  def current_group(self, value: str):
    self.__current_group__ = value

  @property
  def current_id(self):
    return self.__current_id__

  @current_id.setter
  def current_id(self, value: id):
    self.__current_id__ = value

  def update_currents(self, ctx: commands.Context = None, message: discord.Message = None, interaction: discord.Interaction = None):
    if ctx is None and message is None and interaction is None:
      return
    if message is not None:
      is_guild = message.guild
    elif ctx is not None:
      is_guild = ctx.guild
    else:
      is_guild = interaction.guild
    if is_guild:
      settings.current_group = "guilds"
      if message is not None:
        settings.current_id = message.guild.id
      elif ctx is not None:
        settings.current_id = ctx.guild.id
      else:
        settings.current_id = interaction.guild.id
    else:
      settings.current_group = "users"
      if message is not None:
        settings.current_id = message.author.id
      elif ctx is not None:
        settings.current_id = ctx.message.author.id
      else:
        settings.current_id = interaction.message.author.id
    
  # Guild
  def is_guild(self, ctx: commands.Context):
    if not ctx.guild:
      return False
    else:
      return True

  # Settings
  def get(self):
    file = self.__settings_file__.format(self.__current_group__, str(self.__current_id__))
    if not os.path.isfile(file) and not os.access(file, os.R_OK):
      os.makedirs(os.path.dirname(file), exist_ok=True)
      with open(file, 'w') as file_object:
        file_object.write(json.dumps({}))
        file_object.close()
    with open(file, 'r+') as json_file:
      data = json.load(json_file)
      json_file.close()
      return data
  
  def set(self, key: str, value: any):
    settings_model = self.get()
    if f"{key}" not in settings_model:
      settings_model.update({
        f"{key}": value
      })
    else:
      settings_model[f"{key}"] = value
    dumped = json.dumps(settings_model, indent=4)
    with open(self.__settings_file__.format(self.__current_group__, str(self.__current_id__)), "w") as _data:
      _data.write(dumped)
      _data.close()

  def get_key(self, key: str, default: any):
    settings_model = self.get()
    try:
      return settings_model[key]
    except:
      return default

  # Localizations

  def lang_dict(self, lang_code):
    if lang_code is None:
      lang_code = self.__default_lang_code__
    with open(self.__lang_folder__+"/"+lang_code+".xml",'r') as f:
      dict = xd.parse(f.read())
      return dict["langs"]

  @property
  def supported_langs(self):
    supported_langs = []
    for filename in os.listdir(self.__lang_folder__):
      if filename.endswith(".xml"):
        supported_langs.append(filename[:-4])
    return supported_langs

  def lang_from_text(self, text: str):
    try:
      lang = self.lang_dict(self.__default_lang_code__)
      keys = [k for k, v in lang.items() if v == text]
      if len(keys) > 0:
        lang_string = self.lang_string(keys[0])
        if lang_string == keys[0]:
          return text
        else:
          return lang_string
      else:
        return text
    except Exception as e:
      print("Could not get lang key: "+str(e))
      return text

  def lang_string(self, key: str, lang_code: str = None, is_default = False):
    try:
      if is_default:
        lang = self.lang_dict()
      else:
        if lang_code is None:
          lang = self.lang_dict(self.lang_code)
        else:
          lang = self.lang_dict(lang_code)
      return lang[key]
    except Exception as e:
      print("Could not get lang string: "+str(e))
      return key

  @property
  def lang_code(self):
    return self.get_key(self.__lang_str__, self.__default_lang_code__)

  @lang_code.setter
  def lang_code(self, lang: str):
    self.set(self.__lang_str__, lang)
  
  @property
  def translate(self):
    return self.get_key(self.__translate_str__, False)
  
  @translate.setter
  def translate(self, translate: bool):
    self.set(self.__translate_str__, translate)
    
  # Debug
  @property
  def debug(self):
    return self.get_key(self.__debug_str__, False)
    
  @debug.setter
  def debug(self, debug: bool):
    self.set(self.__debug_str__, debug)

settings = Settings()