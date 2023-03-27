## Info

- This repo only tested in [https://replit.com/](https://replit.com/)
- Feel free to update for yourselfs

## Secrets

- For replit don't forget to remove quotes. Example:
- key
```
AI_BRAINSHOP_TOKEN
```
- value
```
VG......W1
```

```
// Command prefix for using commands without slash.
COMMAND_PREFIX = '!'

// Requires for chat bot.
// Brainshop.ai api token. Get it from https://brainshop.ai/
AI_BRAINSHOP_TOKEN = 'VG......W1'

// Discord bot secret token
DISCORD_BOT_SECRET = 'MTA.......86CQ'

// If USE_REPLIT_DB not specified default will be false. 
// If false; creates settings.json file locally and saves 
// guild/user settings in it. If true; uses replit database 
// (you have to deploy your bot in replit for this.) 
// You can check and edit "src/settings/settings.py" file for your database
USE_REPLIT_DB = true 
```

### Music Bot

- To download ffmpef, open shell in replit (ctrl+shift+s):
- Enter this commands:
```
npm install
```

- Get ffmpef location with this:
```
node -e "console.log(require('ffmpeg-static'))"
```

- add secret like this: 
```
FFMPEG_PATH='/home/runner/your_repl_name/node_modules/ffmpeg-static/ffmpeg'
```

## Installing Dependecies
- Open shell (ctrl+shift+s):
- Enter this command:
```
python3 -m poetry install
```