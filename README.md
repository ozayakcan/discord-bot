## Music Bot

- To download ffmpef, open shell (ctrl+shift+s):
- Enter this commands:
```
npm install ffmpeg-static
```
```
node -e "console.log(require('ffmpeg-static'))"
```
- copy result to variable in main.py like this: 
```
FFMPEG_PATH = '/home/runner/your_repl_name/node_modules/ffmpeg-static/ffmpeg'
```

## Secrets

- Define in .env file. For replit define in secrets tab.

- For replit don't forget to remove quotes. Example:
- key
```
AI_BRAINSHOP_TOKEN
```
- value
```
VG......W1
```


- Remove comments or it can cause error.
```
COMMAND_PREFIX = '!'

AI_BRAINSHOP_TOKEN = 'VG......W1' // Brainshop.ai api token. Get it from https://brainshop.ai/

DISCORD_BOT_SECRET = 'MTA.......86CQ' // Discord bot secret token

CHANNEL_IDS = '["1234567890123", "1234567890456"]' // Channel ids for chat func will work. Don't forget to define inside quotes for .env file. For replit remove quotes.

LANGUAGE_CODE = 'fr' // Copy lang/en.json and rename it to your language code.
TRANSLATE = 'True' // Translates chat messages if True. If not specified or False it will not translate chat messages.
```