import io
import os
import json

import discord
from discord.ext import commands

settings_file = "./src/settings/settings.json"

lang_folder = "./src/lang"
if not os.path.isfile(settings_file) and not os.access(settings_file, os.R_OK):
  with io.open(settings_file, 'w') as settings_file_object:
    settings_file_object.write(json.dumps({}))
default_lang_code = "en"

def get_settings():
  with open(settings_file, 'r+') as json_file:
    data = json.load(json_file)
    return data

def get_key(id: int, group: str, key: str, default: any):
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

def update_settings(id: int, group: str, key: str, value: any):
  with open(settings_file, 'r+') as json_file:
    data = json.load(json_file)
    data = set_key(data=data, group=group, id=id, key=key, value=value)
    json_file.seek(0)
    json.dump(data, json_file, indent=4, sort_keys=False)
    json_file.truncate()

# Localizations

def get_lang_code(id: int, group: str):
  return get_key(id=id, group=group, key="lang", default=default_lang_code)

def get_supported_langs():
  supported_langs = []
  for filename in os.listdir(lang_folder):
    if filename.endswith(".json"):
      supported_langs.append(filename[:-5])
  return supported_langs

def get_lang_string(id: int, group: str, key:str):
  langs = {}
  supported_langs = get_supported_langs()
  for supported_lang in supported_langs:
    file = open(lang_folder+"/"+supported_lang+".json")
    langs[supported_lang] = json.load(file)
    file.close()
  return langs[get_lang_code(id=id, group=group)][key]

def get_translate(id: int, group: str):
  return get_key(id=id, group=group, key="translate", False)
