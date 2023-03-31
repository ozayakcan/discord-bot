import os
import json

from discord.ext import commands

class Settings:
  def __init__(self):
    self.message_delete_delay = 5

  async def send_cog_error(self, group: str, id: int, ctx: commands.Context, error: commands.CommandError):
    await ctx.send(f"{ctx.message.author.mention}, {str(error)}")
    #if get_debug(group=group, id=id):
    #  await ctx.send(str(error), delete_after=self.message_delete_delay)
    #else:
    #  await ctx.send(get_lang_string(group=group, id=id, key="an_error_ocurred").format(ctx.clean_prefix, ctx.invoked_with), delete_after=self.message_delete_delay)

default_settings = Settings()


# Guild
def is_guild(ctx: commands.Context):
  if not ctx.guild:
    return False
  else:
    return True

# Settings files
settings_file = "./src/settings/{0}/{1}.json"

lang_folder = "./src/lang"

default_lang_code = "en"

def get_settings(group:str, id: int):
  file = settings_file.format(group, str(id))
  if not os.path.isfile(file) and not os.access(file, os.R_OK):
    os.makedirs(os.path.dirname(file), exist_ok=True)
    with open(file, 'w') as file_object:
      file_object.write(json.dumps({}))
      file_object.close()
  with open(file, 'r+') as json_file:
    data = json.load(json_file)
    json_file.close()
    return data

def get_key(group: str, id: int, key: str, default: any):
  settings_model = get_settings(group, id)
  try:
    return settings_model[key]
  except:
    return default

def set_key(data, key: str, value: any):
  if f"{key}" not in data:
    data = data
    data.update({
      f"{key}": value
    })
  else:
    data[f"{key}"] = value
  return data

def update_settings(group: str, id: int, key: str, value: any):
  settings_model = get_settings(group, id)
  settings_model = set_key(settings_model, key=key, value=value)
  dumped = json.dumps(settings_model, indent=4)
  with open(settings_file.format(group, str(id)), "w") as _data:
    _data.write(dumped)
    _data.close()

# Chat
    
chat_channels_str = "chat_channels"

def set_chat_channels(group: str, id: int, channel_ids: list = []):
  update_settings(group=group, id=id, key=chat_channels_str, value=channel_ids)

def get_chat_channels(group: str, id: int):
  return get_key(group=group, id=id, key=chat_channels_str, default=[])
    
# Localizations

def get_supported_langs():
  supported_langs = []
  for filename in os.listdir(lang_folder):
    if filename.endswith(".json"):
      supported_langs.append(filename[:-5])
  return supported_langs

def get_lang_string(group: str, id: int, key:str):
  langs = {}
  supported_langs = get_supported_langs()
  for supported_lang in supported_langs:
    file = open(lang_folder+"/"+supported_lang+".json")
    langs[supported_lang] = json.load(file)
    file.close()
  return langs[get_lang_code(group=group, id=id)][key]

lang_str = "lang"

def set_lang_code(group: str, id: int, lang: str):
  update_settings(group=group, id=id, key=lang_str, value=lang)

def get_lang_code(group: str, id: int):
  return get_key(group=group, id=id, key=lang_str, default=default_lang_code)

translate_str = "translate"

def set_translate(group: str, id: int, translate: bool):
  update_settings(group=group, id=id, key=translate_str, value=translate)

def get_translate(group: str, id: int):
  return get_key(group=group, id=id, key=translate_str, default=False)

# Debug

debug_str = "debug"

def set_debug(group: str, id: int, debug: bool):
  update_settings(group=group, id=id, key=debug_str, value=debug)

def get_debug(group: str, id: int):
  return get_key(group=group, id=id, key=debug_str, default=False)