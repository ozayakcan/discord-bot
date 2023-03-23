from discord.ext import commands
import os
import json

lang_file = "./src/lang/lang.json"
default_lang_code = "en"
lang_settings = {}
langs = {}
lang_current_id = 0
lang_current_group = "guilds"

def set_current_lang_infos(ctx: commands.Context):
  global lang_current_group, lang_current_id
  if ctx.guild:
    lang_current_group = "guilds"
    lang_current_id = ctx.guild.id
  else:
    lang_current_group = "users"
    lang_current_id = ctx.message.author.id

def get_supported_langs(ret: bool = True):
  global langs
  supported_langs = []
  lang_folder = "./src/lang"
  for filename in os.listdir(lang_folder):
    if filename.endswith(".json") and filename != "lang.json":
      supported_langs.append(filename[:-5])
      if not ret:
        file = open(lang_folder+"/"+filename)
        langs[filename[:-5]] = json.load(file)
        file.close()
  if ret:
    return supported_langs
get_supported_langs(False)

def update_lang_dict(data, key: str, id: int, lang_code: str):
  global lang_settings
  if key not in data:
    data.update({
      f"{key}" : {
        f"{id}": {
          "lang": f"{lang_code}"
        }
      }
    })
  elif str(id) not in data[key]:
    key_data = data[key]
    key_data.update({
      f"{id}": {
        "lang": f"{lang_code}"
      }
    })
    data[key] = key_data
  elif "lang" not in data[key][str(id)]:
    id_data = data[key][str(id)]
    id_data.update({
      "lang": f"{lang_code}"
    })
    data[key][str(id)] = id_data 
  else:
    data[key][str(id)]["lang"] = f"{lang_code}"
  lang_settings.update(data) 
  return data

async def set_lang(ctx: commands.Context, lang_code: str = default_lang_code):
    try:
      with open(lang_file, 'r+') as json_file:
        data = json.load(json_file)
        if not ctx.guild:
          data = update_lang_dict(data, "users", ctx.message.author.id, lang_code)
        else:
          data = update_lang_dict(data, "guilds", ctx.guild.id, lang_code)
        json_file.seek(0)
        json.dump(data, json_file, indent=4, sort_keys=False)
        json_file.truncate()
        await ctx.send(get_lang_string("lang_changed"), delete_after=self.delete_delay)
    except Exception as e:
      print(str(e))
      await ctx.send(get_lang_string("lang_not_changed"), delete_after=self.delete_delay)
def get_lang():
  global lang_settings
  try:
    with open(lang_file, 'r+') as json_file:
      data = json.load(json_file)
      lang_settings = data
  except Exception as e:
    print(str(e))
get_lang()
def get_lang_code():
  try:
    return lang_settings[lang_current_group][str(lang_current_id)]["lang"]
  except Exception as e:
    return default_lang_code
def get_lang_string(key):
  return langs[get_lang_code()][key]

class Lang(commands.Cog):
  def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.delete_delay = 5

  async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send(get_lang_string("an_error_ocurred").format(str(error)), delete_after=self.delete_delay)

  async def cog_before_invoke(self, ctx: commands.Context):
        set_current_lang_infos(ctx=ctx)

  @commands.command(name='lang', brief=get_lang_string("lang_desc"), description=get_lang_string("lang_desc_full").format(", ".join(get_supported_langs())))
  async def _lang(self, ctx: commands.Context, *, lang_code: str = commands.parameter(default=None, description=get_lang_string("lang_code_desc"))):
    langs = get_supported_langs()
    if lang_code:
      if lang_code in langs:
        await set_lang(ctx, lang_code)
      else:
        await ctx.send(get_lang_string("lang_not_supported").format(lang_code, ctx.clean_prefix, "supported_langs"), delete_after=self.delete_delay)
    else:
      await ctx.send(get_lang_string("lang_current"), delete_after=self.delete_delay)

  @commands.command(name='supported_langs', brief=get_lang_string("supported_langs_desc"), description=get_lang_string("supported_langs_desc"))
  async def _supported_langs(self, ctx: commands.Context):
      await ctx.send(get_lang_string("supported_langs").format(", ".join(get_supported_langs())), delete_after=self.delete_delay)

async def setup(bot):
  await bot.add_cog(Lang(bot))