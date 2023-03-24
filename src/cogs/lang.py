import discord
from discord.ext import commands
import io
import os
import json

lang_file = "./src/lang/lang.json"
lang_folder = "./src/lang"
if not os.path.isfile(lang_file) and not os.access(lang_file, os.R_OK):
  with io.open(lang_file, 'w') as lang_file_object:
    lang_file_object.write(json.dumps({}))
default_lang_code = "en"

lang_current_id = 0
lang_current_group = "guilds"

def get_supported_langs():
  supported_langs = []
  for filename in os.listdir(lang_folder):
    if filename.endswith(".json") and filename != "lang.json":
      supported_langs.append(filename[:-5])
  return supported_langs

def update_lang_dict(data, key: str, id: int, value: any, sub_key: str):
  if key not in data:
    data.update({
      f"{key}" : {
        f"{id}": {
          f"{sub_key}": value
        }
      }
    })
  elif str(id) not in data[key]:
    key_data = data[key]
    key_data.update({
      f"{id}": {
        f"{sub_key}": value
      }
    })
    data[key] = key_data
  elif f"{sub_key}" not in data[key][str(id)]:
    id_data = data[key][str(id)]
    id_data.update({
      f"{sub_key}": value
    })
    data[key][str(id)] = id_data 
  else:
    data[key][str(id)][f"{sub_key}"] = value
  return data

def update_lang_settings(ctx: commands.Context, value: any, sub_key="lang"):
  with open(lang_file, 'r+') as json_file:
    data = json.load(json_file)
    if isinstance(ctx.channel, discord.channel.DMChannel):
      data = update_lang_dict(data=data, key="users", id=ctx.message.author.id, value=value, sub_key=sub_key)
    else:
      data = update_lang_dict(data=data, key="guilds", id=ctx.guild.id, value=value, sub_key=sub_key)
    json_file.seek(0)
    json.dump(data, json_file, indent=4, sort_keys=False)
    json_file.truncate()


def get_lang():
  with open(lang_file, 'r+') as json_file:
    data = json.load(json_file)
    return data
    
def get_lang_code(id: int, group: str):
  lang_settings = get_lang()
  try:
    return lang_settings[group][str(id)]["lang"]
  except:
    return default_lang_code
def get_lang_string(id: int, group: str, key:str):
  langs = {}
  supported_langs = get_supported_langs()
  for supported_lang in supported_langs:
    file = open(lang_folder+"/"+supported_lang+".json")
    langs[supported_lang] = json.load(file)
    file.close()
  return langs[get_lang_code(id=id, group=group)][key]

def get_translate(id: int, group: str):
  lang_settings = get_lang()
  try:
    return lang_settings[group][str(id)]["translate"]
  except:
    return False
class Lang(commands.Cog):
  def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.delete_delay = 5

  async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send(get_lang_string(id=lang_current_id, group=lang_current_group, key="an_error_ocurred").format(str(error)), delete_after=self.delete_delay)

  async def cog_before_invoke(self, ctx: commands.Context):
    global lang_current_group, lang_current_id
    if isinstance(ctx.channel, discord.channel.DMChannel):
      lang_current_group = "users"
      lang_current_id = ctx.message.author.id
    else:
      lang_current_group = "guilds"
      lang_current_id = ctx.guild.id
  async def cog_after_invoke(self, ctx: commands.Context):
        member = ctx.message.guild.get_member(self.bot.user.id)
        if member.guild_permissions.manage_messages:
          try:
            await ctx.message.delete(delay=self.delete_delay)
          except Exception as e:
            print(e)
  @commands.command(name='lang', brief=get_lang_string(id=lang_current_id, group=lang_current_group, key="lang_desc"), description=get_lang_string(id=lang_current_id, group=lang_current_group, key="lang_desc_full").format(", ".join(get_supported_langs())))
  async def _lang(self, ctx: commands.Context, *, lang_code: str = commands.parameter(default=None, description=get_lang_string(id=lang_current_id, group=lang_current_group, key="lang_code_desc"))):
    supported_langs = get_supported_langs()
    if lang_code:
      if not isinstance(ctx.channel, discord.channel.DMChannel):
        if not ctx.message.author.guild_permissions.manage_messages:
          return await ctx.send(get_lang_string(id=lang_current_id, group=lang_current_group, key="manage_messages"), delete_after=self.delete_delay)
      if lang_code in supported_langs:
        try:
          update_lang_settings(ctx=ctx, value=lang_code)
          await ctx.send(get_lang_string(id=lang_current_id, group=lang_current_group, key="lang_changed"), delete_after=self.delete_delay)
        except Exception as e:
          print(str(e))
          await ctx.send(get_lang_string(id=lang_current_id, group=lang_current_group, key="lang_not_changed"), delete_after=self.delete_delay)
      else:
        await ctx.send(get_lang_string(id=lang_current_id, group=lang_current_group, key="lang_not_supported").format(lang_code, ctx.clean_prefix, "supported_langs"), delete_after=self.delete_delay)
    else:
      await ctx.send(get_lang_string(id=lang_current_id, group=lang_current_group, key="lang_current"), delete_after=self.delete_delay)

  @commands.command(name='supported_langs', brief=get_lang_string(id=lang_current_id, group=lang_current_group, key="supported_langs_desc"), description=get_lang_string(id=lang_current_id, group=lang_current_group, key="supported_langs_desc"))
  async def _supported_langs(self, ctx: commands.Context):
      await ctx.send(get_lang_string(id=lang_current_id, group=lang_current_group, key="supported_langs").format(", ".join(get_supported_langs())), delete_after=self.delete_delay)

  @commands.command(name='translate', brief=get_lang_string(id=lang_current_id, group=lang_current_group, key="translate_desc"), description=get_lang_string(id=lang_current_id, group=lang_current_group, key="translate_desc"))
  async def _translate(self, ctx: commands.Context):
    if not isinstance(ctx.channel, discord.channel.DMChannel):
      if not ctx.message.author.guild_permissions.manage_messages:
        return await ctx.send(get_lang_string(id=lang_current_id, group=lang_current_group, key="manage_messages"), delete_after=self.delete_delay)
    translate = not get_translate(id=lang_current_id, group=lang_current_group)
    update_lang_settings(ctx=ctx, value=translate, sub_key="translate")
    if translate:
      await ctx.send(get_lang_string(id=lang_current_id, group=lang_current_group, key="translate_enabled"), delete_after=self.delete_delay)
    else:
      await ctx.send(get_lang_string(id=lang_current_id, group=lang_current_group, key="translate_disabled"), delete_after=self.delete_delay)

async def setup(bot):
  await bot.add_cog(Lang(bot))