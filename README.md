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
COMMAND_PREFIX = '!'

AI_BRAINSHOP_TOKEN = 'VG......W1' // Brainshop.ai api token. Get it from https://brainshop.ai/

DISCORD_BOT_SECRET = 'MTA.......86CQ' // Discord bot secret token
```

### Music Bot

- To download ffmpef, open shell (ctrl+shift+s):
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