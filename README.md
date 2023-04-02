## Info

- This repo only tested in [https://replit.com/](https://replit.com/)

## Secrets

Keys | Values | Description
--- | --- | --- 
AI_BRAINSHOP_TOKEN | VG......W1 | Get it from [https://brainshop.ai/](https://brainshop.ai/)
COMMAND_PREFIX | ! | Your command prefix.
DISCORD_BOT_SECRET | MTA.......86CQ | Your discord bot token. [https://discord.com/developers/applications](https://discord.com/developers/applications)
FFMPEG_PATH | ffmpeg path | See [installing music bot](#installing)


## Music Bot

- See [supported sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)
- Playlists not supported for now.

### Installing
- To download ffmpef, open shell in replit (ctrl+shift+s):
- Enter this commands:
```
npm install
```

- Get ffmpef location with this:
```
node -e "console.log(require('ffmpeg-static'))"
```
- And add your [secrets](#secrets)

## Installing Dependecies
- Open shell (ctrl+shift+s):
- Enter this command:
```
python3 -m poetry install
```

## Localization

- Localization files:
```
src/json/lang/
```
- Just copy en.json and rename as your desired language. Bot will automatically load on start.

### Commands

- Command localization:
  - Cog name localization not supported because discord.py not allowing later cog name changes.
- For custom commands, create .py file in src/cogs.
- See this example
```
from discord.ext import commands

from utils import settings # get settings

# settings.lang_string(...) returns default language string on start.
# And only updates when command invoked.
class MyCog(commands.Cog, description=settings.lang_string("your_description_lang_key")): 

  
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  # settings.update_currents(ctx=ctx) 
  # or settings.update_currents(message=message) in on_message function.
  # Updates settings group ("users" or "guilds") 
  # and it's id for getting user/guild settings from later.
  # Example: 
  #   For guild group (if command used in guild):
  #   loads setting from src/json/guilds/guild_id.json
  # You should use this in cog_before_invoke function 
  # or settings doesn't know which user or guild 
  # used command and only gets default settings.
  async def cog_before_invoke(self, ctx: commands.Context):
    settings.update_currents(ctx=ctx)

  # Description string updates after help command used. For help command localization.
  # hybrid_command registers both custom prefix and slash commands. 
  # If you don't want slash command replace @commands.hybrid_command with @commands.command
  # or @app_commands.command for only slash commands
  @commands.hybrid_command(
    name='mycommand',
    brief=settings.lang_string("mycommand_desc")
    description=settings.lang_string("mycommand_desc_full") 
    # brief and description not localizing slash command description. (For now.)
  ) 
  async def _mycommand(
    self,
    ctx: commands.Context,
    *,
    custom_arg: str = commands.parameter(
      default=None, # For slash commands. If it's required parameter
                    # Remove this line or set default None .
                    # Or set a default value except None if it's optional.
                    # Example: 
                    #   default= "You default value" - Optional
                    #   default= None                - Required
      description=settings.lang_string("arg_desc")
    )
  ):
    ...
    # Your command codes
    ...

async def setup(bot):
  await bot.add_cog(MyCog(bot))
```

### Known Bugs

- Sometimes after bot restarted, if it's in a voice channel before restart, music commands not working properly. After you kick bot from voice channel, commands works again.

- loop command disabled. (Not working)