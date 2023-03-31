## Info

- This repo only tested in [https://replit.com/](https://replit.com/)

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
// Command prefix for using commands instead of slash.
COMMAND_PREFIX = '!'

// Requires for chat bot.
// Brainshop.ai api token. Get it from https://brainshop.ai/
AI_BRAINSHOP_TOKEN = 'VG......W1'

// Discord bot secret token
DISCORD_BOT_SECRET = 'MTA.......86CQ'
```

## Music Bot

- See [supported sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)
- Playlists not supported for now.

### Known Bugs

- Sometimes after bot restarted, if it's in a voice channel before restart, music commands not working properly. After you kick bot from voice channel, commands works again.

- loop command disabled. (Not working)

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