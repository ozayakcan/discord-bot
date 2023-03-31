import io
import os
import json

from discord.ext import commands

class Settings:
  def __init__(self):
    self.message_delete_delay = 5

  async def send_cog_error(self, group: str, id: int, ctx: commands.Context, error: commands.CommandError):
    
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

# Database
use_replit_db = os.environ.get("USE_REPLIT_DB")
if use_replit_db is not None:
  if str(use_replit_db).lower() == "true":
    use_replit_db = True
  else:
    use_replit_db = False
else:
  use_replit_db = False
settings_file = "./src/settings/settings.json"

lang_folder = "./src/lang"
if not use_replit_db:
  if not os.path.isfile(settings_file) and not os.access(settings_file, os.R_OK):
    with io.open(settings_file, 'w') as settings_file_object:
      settings_file_object.write(json.dumps({}))
default_lang_code = "en"

def get_settings():
  if use_replit_db:
    from replit import db
    return db
  else:
    with open(settings_file, 'r+') as json_file:
      data = json.load(json_file)
      return data

def get_key(group: str, id: int, key: str, default: any):
  settings_model = get_settings()
  try:
    return settings_model[group][str(id)][key]
  except:
    return default

def set_key(data, group: str, id: int, key: str, value: any):
  if group not in data:
    data.update({
      f"{group}" : {
        f"{id}": {
          f"{key}": value
        }
      }
    })
  elif str(id) not in data[group]:
    key_data = data[group]
    key_data.update({
      f"{id}": {
        f"{key}": value
      }
    })
    data[group] = key_data
  elif f"{key}" not in data[group][str(id)]:
    id_data = data[group][str(id)]
    id_data.update({
      f"{key}": value
    })
    data[group][str(id)] = id_data 
  else:
    data[group][str(id)][f"{key}"] = value
  return data

def update_settings(group: str, id: int, key: str, value: any):
  if use_replit_db:
    settings_model = get_settings()
    settings_model = set_key(data=settings_model, group=group, id=id, key=key, value=value)
  else:
    with open(settings_file, 'r+') as json_file:
      data = json.load(json_file)
      data = set_key(data=data, group=group, id=id, key=key, value=value)
      json_file.seek(0)
      json.dump(data, json_file, indent=4, sort_keys=False)
      json_file.truncate()

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