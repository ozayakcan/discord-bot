import asyncio
import functools
import validators

import yt_dlp as youtube_dl
import discord
from discord.ext import commands

from utils import settings
from ._st import YTDLError, parse_duration

__all__ = (
    'YTDLSource',
    'Song',
)

# Silence useless bug reports messages
youtube_dl.utils.bug_reports_message = lambda: ''

class YTDLSource(discord.PCMVolumeTransformer):
  YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
  }

  FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
  }

  ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

  def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
    super().__init__(source, volume)
    settings.update_currents(ctx=ctx)
    self.requester = ctx.author
    self.channel = ctx.channel
    self.data = data

    self.uploader = data.get('uploader')
    self.uploader_url = data.get('uploader_url')
    date = data.get('upload_date')
    self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
    self.title = data.get('title')
    self.thumbnail = data.get('thumbnail')
    self.description = data.get('description')
    self.duration = parse_duration(int(data.get('duration')))
    self.tags = data.get('tags')
    self.url = data.get('webpage_url')
    self.views = data.get('view_count')
    self.likes = data.get('like_count')
    self.dislikes = data.get('dislike_count')
    self.stream_url = data.get('url')

  def __str__(self):
    return settings.lang_string("yt_uploader").format(self)

  @classmethod
  async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
    loop = loop or asyncio.get_event_loop()

    if validators.url(search):
      partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
    else:
      partial = functools.partial(cls.ytdl.extract_info, f"ytsearch5:{search}", download=False, process=False)

    data = await loop.run_in_executor(None, partial)
    if data is None:
      raise YTDLError(settings.lang_string("yt_could_not_find").format(search))

    webpage_url = data['webpage_url']
    partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
    
    processed_info = await loop.run_in_executor(None, partial)

    if processed_info is None:
      raise YTDLError(settings.lang_string("yt_could_not_fetch").format(webpage_url))

    sources = []
    if 'entries' not in processed_info:
      sources.append(Song(cls(ctx, discord.FFmpegPCMAudio(processed_info['url'], **cls.FFMPEG_OPTIONS), data=processed_info)))
    else:
      #entries = list(data["entries"])
      for source in processed_info["entries"]:
        sources.append(Song(cls(ctx, discord.FFmpegPCMAudio(source['url'], **cls.FFMPEG_OPTIONS), data=source)))

    if len(sources) == 0:
      raise YTDLError(settings.lang_string("yt_could_not_fetch").format(search))
    return sources

class Song:
  __slots__ = ('source', 'requester')

  def __init__(self, source: YTDLSource):
    self.source = source
    self.requester = source.requester

  def create_embed(self):
    embed = (discord.Embed(title=settings.lang_string("now_playing"),
                           description='```css\n{0.source.title}\n```'.format(self),
                           color=discord.Color.blurple())
             .add_field(name=settings.lang_string("duration"), value=self.source.duration)
             .add_field(name=settings.lang_string("requested_by"), value=self.requester.mention)
             .add_field(name=settings.lang_string("uploader"), value='[{0.source.uploader}]({0.source.uploader_url})'.format(self))
             .add_field(name=settings.lang_string("url"), value=settings.lang_string("url_content").format(self))
             .set_thumbnail(url=self.source.thumbnail))

    return embed