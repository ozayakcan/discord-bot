import os
import json

import discord
from discord.ext import commands

class Settings:
  def __init__(self):
    self.message_delete_delay = 5
    self.__current_group__ = "guilds"
    self.__current_id__ = 0

    # Settings files
    self.__settings_file__ = "./src/settings/{0}/{1}.json"
    # Localization
    self.__lang_folder__ = "./src/lang"
    self.__default_lang_code__ = "en"
    
    #Settings
    self.__chat_channels_str__ = "chat_channels"
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

  def update_currents(self, ctx: commands.Context = None, message: discord.Message = None):
    if ctx is None and message is None:
      return
    if message is not None:
      is_guild = message.guild
    else:
      is_guild = ctx.guild
    if is_guild:
      settings.current_group = "guilds"
      if message is not None:
        settings.current_id = message.guild.id
      else:
        settings.current_id = ctx.guild.id
    else:
      settings.current_group = "users"
      if message is not None:
        settings.current_id = message.author.id
      else:
        settings.current_id = ctx.message.author.id
    
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

  # Chat

  @property
  def chat_channels(self):
    return self.get_key(self.__chat_channels_str__, [])
    
  @chat_channels.setter
  def chat_channels(self, channel_ids: list = []):
    self.set(self.__chat_channels_str__, channel_ids)

  # Localizations

  @property
  def lang_dict(self):
    langs = {}
    supported_langs = self.supported_langs
    for supported_lang in supported_langs:
      file = open(self.__lang_folder__+"/"+supported_lang+".json")
      langs[supported_lang] = json.load(file)
      file.close()
    return langs

  @property
  def supported_langs(self):
    supported_langs = []
    for filename in os.listdir(self.__lang_folder__):
      if filename.endswith(".json"):
        supported_langs.append(filename[:-5])
    return supported_langs

  def lang_string(self, key: str, is_default = False):
    langs = self.lang_dict
    if is_default:
      return langs[self.__default_lang_code__][key]
    else:
      return langs[self.lang_code][key]

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