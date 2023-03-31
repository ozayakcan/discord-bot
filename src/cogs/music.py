import asyncio
import functools
import itertools
import math
import random
from async_timeout import timeout
import collections

import yt_dlp as youtube_dl
import discord
from discord.ext import commands

from settings.settings import default_settings, is_guild, get_lang_string

settings_current_group = "guilds"
settings_current_id = 0

def set_global_defs(ctx: commands.Context):
  global settings_current_group, settings_current_id
  if is_guild(ctx):
    settings_current_group = "guilds"
    settings_current_id = ctx.guild.id
  else:
    settings_current_group = "users"
    settings_current_id = ctx.message.author.id

def parse_duration(duration: int):
    minutes, seconds = divmod(duration, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    duration = []
    if days > 0:
      duration.append(get_lang_string(group=settings_current_group, id=settings_current_id, key="days").format(days))
    if hours > 0:
      duration.append(get_lang_string(group=settings_current_group, id=settings_current_id, key="hours").format(hours))
    if minutes > 0:
      duration.append(get_lang_string(group=settings_current_group, id=settings_current_id, key="minutes").format(minutes))
    if seconds > 0:
      duration.append(get_lang_string(group=settings_current_group, id=settings_current_id, key="seconds").format(seconds))

    return ', '.join(duration)
# Silence useless bug reports messages
youtube_dl.utils.bug_reports_message = lambda: ''

class VoiceError(Exception):
  pass

class YTDLError(Exception):
  pass

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
    set_global_defs(ctx)
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
    return get_lang_string(group=settings_current_group, id=settings_current_id, key="yt_uploader").format(self)

  @classmethod
  async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
    loop = loop or asyncio.get_event_loop()

    partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
    data = await loop.run_in_executor(None, partial)

    if data is None:
      raise YTDLError(get_lang_string(group=settings_current_group, id=settings_current_id, key="yt_could_not_find").format(search))

    if 'entries' not in data:
      process_info = data
    else:
      process_info = None
      for entry in data['entries']:
        if entry:
          process_info = entry
          break

      if process_info is None:
        raise YTDLError(get_lang_string(group=settings_current_group, id=settings_current_id, key="yt_could_not_find").format(search))

    webpage_url = process_info['webpage_url']
    partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
    processed_info = await loop.run_in_executor(None, partial)

    if processed_info is None:
      raise YTDLError(get_lang_string(group=settings_current_group, id=settings_current_id, key="yt_could_not_fetch").format(webpage_url))

    if 'entries' not in processed_info:
      info = processed_info
    else:
      info = None
      while info is None:
        try:
          info = processed_info['entries'].pop(0)
        except IndexError:
          raise YTDLError(get_lang_string(group=settings_current_group, id=settings_current_id, key="yt_could_not_retrieve").format(webpage_url))

    return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)

class Song:
  __slots__ = ('source', 'requester')

  def __init__(self, source: YTDLSource):
    self.source = source
    self.requester = source.requester

  def create_embed(self):
    embed = (discord.Embed(title=get_lang_string(group=settings_current_group, id=settings_current_id, key="now_playing"),
                           description='```css\n{0.source.title}\n```'.format(self),
                           color=discord.Color.blurple())
             .add_field(name=get_lang_string(group=settings_current_group, id=settings_current_id, key="duration"), value=self.source.duration)
             .add_field(name=get_lang_string(group=settings_current_group, id=settings_current_id, key="requested_by"), value=self.requester.mention)
             .add_field(name=get_lang_string(group=settings_current_group, id=settings_current_id, key="uploader"), value='[{0.source.uploader}]({0.source.uploader_url})'.format(self))
             .add_field(name=get_lang_string(group=settings_current_group, id=settings_current_id, key="url"), value=get_lang_string(group=settings_current_group, id=settings_current_id, key="url_content").format(self))
             .set_thumbnail(url=self.source.thumbnail))

    return embed

class SongQueue(asyncio.Queue):

  def __init__(self):
    self._queue_all = collections.deque()
    self.current = None
    super().__init__()
  
  def __getitem__(self, item):
    if isinstance(item, slice):
      return list(itertools.islice(self._queue, item.start, item.stop, item.step))
    else:
      return self._queue[item]

  def _get(self):
    if self.__len__() > 0:
      self.current = self._queue[0]
    return super()._get()
  
  def __iter__(self):
    return self._queue.__iter__()

  def __len__(self):
    return self.qsize()

  def len_all(self):
    return len(self._queue_all)
  
  def get_all(self, item):
    if isinstance(item, slice):
      return list(itertools.islice(self._queue_all, item.start, item.stop, item.step))
    else:
      return self._queue_all[item]

  async def put(self, item):
    self._queue_all.append(item)
    await super().put(item)
  
  def clear(self):
    self._queue.clear()
    self._queue_all.clear()

  def shuffle(self):
    random.shuffle(self._queue_all)
    first_item = None
    for i, sng in enumerate(self._queue_all):
      if self._queue_all[i] == self.current:
        first_item = self._queue_all.copy()[i]
        del self._queue_all[i]
        break
    self._queue = self._queue_all.copy()
    if first_item is not None:
      self._queue_all.append(first_item)

  def remove(self, index: int, vc):
    song = self._queue_all.copy()[index]
    for i, sng in enumerate(self._queue):
      if self._queue[i] == song:
        del self._queue[i]
        break
    del self._queue_all[index]
    if self.current == song:
      vc.skip()
    return song

class VoiceState:
  def __init__(self, bot: commands.Bot, ctx: commands.Context):
    self.bot = bot
    self._ctx = ctx

    self.current = None
    self.voice = None
    self.next = asyncio.Event()
    self.songs = SongQueue()

    self._loop = False
    self._volume = 0.5
    self.skip_votes = set()

    self.audio_player = bot.loop.create_task(self.audio_player_task())

  def __del__(self):
    self.audio_player.cancel()

  @property
  def loop(self):
    return self._loop

  @loop.setter
  def loop(self, value: bool):
    self._loop = value

  @property
  def volume(self):
    return self._volume

  @volume.setter
  def volume(self, value: float):
    self._volume = value

  @property
  def is_playing(self):
    return self.voice and self.current

  async def audio_player_task(self):
    set_global_defs(self._ctx)
    while True:
      self.next.clear()

      if not self.loop:
        # Try to get the next song within 3 minutes.
        # If no song will be added to the queue in time,
        # the player will disconnect due to performance
        # reasons.
        try:
          timeout_val = 180 # 3 minutes
          async with timeout(timeout_val):
            if self.get_mem_count() == 0:
              self.bot.loop.create_task(self.stop())
              await self._ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="no_user_leave_msg").format(parse_duration(timeout_val)))
              return
            self.current = await self.songs.get()
        except asyncio.TimeoutError:
          self.bot.loop.create_task(self.stop())
          await self.current.source.channel.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="no_track_leave_msg").format(parse_duration(timeout_val)))
          return
        except Exception as e:
          print("src/cogs/music.py find: async with timeout(timeout_val) see this error codes: "+ str(e))

      self.current.source.volume = self._volume
      self.voice.play(self.current.source, after=self.play_next_song)
      await self.current.source.channel.send(embed=self.current.create_embed())

      await self.next.wait()

  def play_next_song(self, error=None):
    if error:
      raise VoiceError(str(error))

    self.next.set()

  def skip(self):
    self.skip_votes.clear()

    if self.is_playing:
      self.voice.stop()

  async def stop(self):
    self.songs.clear()

    if self.voice:
      await self.voice.disconnect()
      self.voice = None

  def get_mem_count(self):
    member_count = 0
    for voice_member in self._ctx.voice_client.channel.members:
      if self.bot.user.id != voice_member.id:
        member_count += 1
    return member_count

class Music(commands.Cog, name= get_lang_string(group=settings_current_group, id=settings_current_id, key="music")):
  def __init__(self, bot: commands.Bot):
    self.bot = bot
    self.voice_states = {}
    self.display_join_message = True

  def get_voice_state(self, ctx: commands.Context):
    state = self.voice_states.get(ctx.guild.id)
    if not state:
      state = VoiceState(self.bot, ctx)
      self.voice_states[ctx.guild.id] = state

    return state

  async def clear_music(self, ctx: commands.Context):
    if not ctx.voice_state.voice:
      await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="not_connected_voice_ch"), delete_after=default_settings.message_delete_delay)
      return False
    try:
      ctx.voice_state.songs.clear()
      if ctx.voice_state.is_playing:
        await ctx.voice_state.stop()
      else:
        await ctx.voice_state.voice.disconnect()
      del self.voice_states[ctx.guild.id]
      await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="stop_leave_success"), delete_after=default_settings.message_delete_delay)
    except Exception as e:
      print("Stop/Leave failed: "+str(e))
      await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="stop_leave_failed"), delete_after=default_settings.message_delete_delay)
      return False
    return True

  def cog_unload(self):
    for state in self.voice_states.values():
      self.bot.loop.create_task(state.stop())

  def cog_check(self, ctx: commands.Context):
    if not is_guild(ctx):
      raise commands.NoPrivateMessage(get_lang_string(group=settings_current_group, id=settings_current_id, key="command_dm"))
    # Disable commands for now
    #raise commands.CommandError('Music commands not available right now.')
    #return False # return True
    return True

  async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
    set_global_defs(ctx)
    await default_settings.send_cog_error(group=settings_current_group, id=settings_current_id, ctx=ctx, error=error)

  async def cog_before_invoke(self, ctx: commands.Context):
    ctx.voice_state = self.get_voice_state(ctx)
    set_global_defs(ctx)

  async def cog_after_invoke(self, ctx: commands.Context):
    if is_guild(ctx):
      member = ctx.message.guild.get_member(self.bot.user.id)
      if member.guild_permissions.manage_messages:
        try:
          await ctx.message.delete(delay=default_settings.message_delete_delay)
        except Exception as e:
          print(e)

  @commands.hybrid_command(name='join', aliases=['j'], invoke_without_subcommand=True, brief=get_lang_string(group=settings_current_group, id=settings_current_id, key="join_desc"), description=get_lang_string(group=settings_current_group, id=settings_current_id, key="join_desc"))
  async def _join(self, ctx: commands.Context):

    destination = ctx.author.voice.channel
    if ctx.voice_state.voice:
      await ctx.voice_state.voice.move_to(destination)
      return

    ctx.voice_state.voice = await destination.connect()
    if self.display_join_message:
      await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="join_success"), delete_after=default_settings.message_delete_delay)

  @commands.hybrid_command(name='summon', aliases=['sum'], brief=get_lang_string(group=settings_current_group, id=settings_current_id, key="summon_desc"), description=get_lang_string(group=settings_current_group, id=settings_current_id, key="summon_desc_full"))
  @commands.has_permissions(manage_guild=True)
  async def _summon(self, ctx: commands.Context, *, channel: discord.VoiceChannel = commands.parameter(default=None, description=get_lang_string(group=settings_current_group, id=settings_current_id, key="summon_channel_desc"))):

    if not channel and not ctx.author.voice:
      raise VoiceError(get_lang_string(group=settings_current_group, id=settings_current_id, key="not_connected_voice_ch_or_not_specified"))

    destination = channel or ctx.author.voice.channel
    if ctx.voice_state.voice:
      await ctx.voice_state.voice.move_to(destination)
      return await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="summon_success").format(f"<#{destination.id}>"), delete_after=default_settings.message_delete_delay)

    ctx.voice_state.voice = await destination.connect()
    await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="summon_success").format(f"<#{destination.id}>"), delete_after=default_settings.message_delete_delay)

  @commands.hybrid_command(name='leave', aliases=['l', 'disconnect', 'd'], brief=get_lang_string(group=settings_current_group, id=settings_current_id, key="stop_leave_desc"), description=get_lang_string(group=settings_current_group, id=settings_current_id, key="stop_leave_desc"))
  @commands.has_permissions(manage_guild=True)
  async def _leave(self, ctx: commands.Context):

    #if not ctx.voice_state.voice:
    #    return await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="not_connected_voice_ch"), delete_after=default_settings.message_delete_delay)

    #await ctx.voice_state.stop()
    #del self.voice_states[ctx.guild.id]
    #await ctx.message.add_reaction('✅')
    leave_status = await self.clear_music(ctx)
    if leave_status:
      await ctx.message.add_reaction('✅')
      

  @commands.hybrid_command(name='volume', aliases=['v', 'vol'], brief=get_lang_string(group=settings_current_group, id=settings_current_id, key="volume_desc"), description=get_lang_string(group=settings_current_group, id=settings_current_id, key="volume_desc"))
  async def _volume(self, ctx: commands.Context, *, volume: commands.Range[int, 1, 100] = commands.parameter(description=get_lang_string(group=settings_current_group, id=settings_current_id, key="volume_level_desc"))):

    if volume is None:
      volume = -1

    if not ctx.voice_state.is_playing:
      return await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="not_playing"), delete_after=default_settings.message_delete_delay)

    if 0 > volume or volume > 100:
      return await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="vol_err"), delete_after=default_settings.message_delete_delay)

    ctx.voice_state.volume = volume / 100
    await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="vol_set").format(volume), delete_after=default_settings.message_delete_delay)

  @commands.hybrid_command(name='now', aliases=['current', 'playing', 'n', 'c'], brief=get_lang_string(group=settings_current_group, id=settings_current_id, key="now_desc"), description=get_lang_string(group=settings_current_group, id=settings_current_id, key="now_desc"))
  async def _now(self, ctx: commands.Context):
    if not ctx.voice_state.is_playing:
      return await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="not_playing"), delete_after=default_settings.message_delete_delay)

    await ctx.send(embed=ctx.voice_state.current.create_embed())

  @commands.hybrid_command(name='pause', brief=get_lang_string(group=settings_current_group, id=settings_current_id, key="pause_desc"), description=get_lang_string(group=settings_current_group, id=settings_current_id, key="pause_desc"))
  @commands.has_permissions(manage_guild=True)
  async def _pause(self, ctx: commands.Context):

    if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
      ctx.voice_state.voice.pause()
      await ctx.message.add_reaction('⏯')
      await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="pause_success"), delete_after=default_settings.message_delete_delay)
    else:
      await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="pause_fail"), delete_after=default_settings.message_delete_delay)

  @commands.hybrid_command(name='resume', aliases=['res', 'r'], brief=get_lang_string(group=settings_current_group, id=settings_current_id, key="resume_desc"), description=get_lang_string(group=settings_current_group, id=settings_current_id, key="resume_desc"))
  @commands.has_permissions(manage_guild=True)
  async def _resume(self, ctx: commands.Context):

    if ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
      ctx.voice_state.voice.resume()
      await ctx.message.add_reaction('⏯')
      await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="resume_success"), delete_after=default_settings.message_delete_delay)
    else:
      await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="resume_fail"), delete_after=default_settings.message_delete_delay)

  @commands.hybrid_command(name='stop', brief=get_lang_string(group=settings_current_group, id=settings_current_id, key="stop_leave_desc"), description=get_lang_string(group=settings_current_group, id=settings_current_id, key="stop_leave_desc"))
  @commands.has_permissions(manage_guild=True)
  async def _stop(self, ctx: commands.Context):
    #ctx.voice_state.songs.clear()

    #if ctx.voice_state.is_playing:
    #    ctx.voice_state.voice.stop()
    #    await ctx.message.add_reaction('⏹')
    stop_status = await self.clear_music(ctx)
    if stop_status:
      await ctx.message.add_reaction('⏹')


  @commands.hybrid_command(name='skip', aliases=['s'], brief=get_lang_string(group=settings_current_group, id=settings_current_id, key="skip_desc"), description=get_lang_string(group=settings_current_group, id=settings_current_id, key="skip_desc"))
  async def _skip(self, ctx: commands.Context):

    if not ctx.voice_state.is_playing:
      return await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="not_playing"), delete_after=default_settings.message_delete_delay)

    voter = ctx.message.author
    if voter == ctx.voice_state.current.requester:
      await ctx.message.add_reaction('⏭')
      ctx.voice_state.skip()
      await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="skip_success"), delete_after=default_settings.message_delete_delay)
    elif voter.id not in ctx.voice_state.skip_votes:
      ctx.voice_state.skip_votes.add(voter.id)
      total_votes = len(ctx.voice_state.skip_votes)

      if total_votes >= 3:
        await ctx.message.add_reaction('⏭')
        ctx.voice_state.skip()
        await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="skip_success"), delete_after=default_settings.message_delete_delay)
      else:
        await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="skip_vote_added").format(total_votes), delete_after=default_settings.message_delete_delay)

    else:
      await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="skip_already_voted"), delete_after=default_settings.message_delete_delay)

  @commands.hybrid_command(name='queue', aliases=['q'], brief=get_lang_string(group=settings_current_group, id=settings_current_id, key="queue_desc"), description=get_lang_string(group=settings_current_group, id=settings_current_id, key="queue_desc"))
  async def _queue(self, ctx: commands.Context, *, page: int = commands.parameter(default=1, description=get_lang_string(group=settings_current_group, id=settings_current_id, key="queue_page_desc"))):

    if ctx.voice_state.songs.len_all() == 0:
      return await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="empty_queue"), delete_after=default_settings.message_delete_delay)

    items_per_page = 10
    pages = math.ceil(ctx.voice_state.songs.len_all() / items_per_page)

    start = (page - 1) * items_per_page
    end = start + items_per_page

    queue = ''
    for i, song in enumerate(ctx.voice_state.songs.get_all(slice(start, end)), start=start):
      queue += get_lang_string(group=settings_current_group, id=settings_current_id, key="queue_pattern").format(i + 1, song)

    embed = (discord.Embed(description=get_lang_string(group=settings_current_group, id=settings_current_id, key="tracks").format(ctx.voice_state.songs.len_all(), queue))
             .set_footer(text=get_lang_string(group=settings_current_group, id=settings_current_id, key="viewing_page").format(page, pages)))
    await ctx.send(embed=embed)

  @commands.hybrid_command(name='shuffle', aliases=['shuf'], brief=get_lang_string(group=settings_current_group, id=settings_current_id, key="shuffle_desc"), description=get_lang_string(group=settings_current_group, id=settings_current_id, key="shuffle_desc"))
  async def _shuffle(self, ctx: commands.Context):

    if len(ctx.voice_state.songs) == 0:
      return await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="empty_queue"), delete_after=default_settings.message_delete_delay)

    ctx.voice_state.songs.shuffle()
    await ctx.message.add_reaction('✅')

  @commands.hybrid_command(name='remove', aliases=['rem'], brief=get_lang_string(group=settings_current_group, id=settings_current_id, key="remove_desc"), description=get_lang_string(group=settings_current_group, id=settings_current_id, key="remove_desc"))
  async def _remove(self, ctx: commands.Context, index: commands.Range[int, 1] = commands.parameter(description=get_lang_string(group=settings_current_group, id=settings_current_id, key="remove_index_desc"))):
    
    if index is None:
      index = 0

    if index <= 0:
      return await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="remove_index_err"), delete_after=default_settings.message_delete_delay)
    if len(ctx.voice_state.songs) == 0:
      return await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="empty_queue"), delete_after=default_settings.message_delete_delay)

    removed_song = ctx.voice_state.songs.remove(index - 1, ctx.voice_state)
    await ctx.message.add_reaction('✅')
    await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="track_removed").format(f"**{str(removed_song.source.title)}**"), delete_after=default_settings.message_delete_delay)

  #@commands.hybrid_command(name='loop',  aliases=['repeat', 'rep'], brief=get_lang_string(group=settings_current_group, id=settings_current_id, key="loop_desc"), description=get_lang_string(group=settings_current_group, id=settings_current_id, key="loop_desc_full"))
  #async def _loop(self, ctx: commands.Context):

  #  if not ctx.voice_state.is_playing:
  #    return await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="not_playing"), delete_after=default_settings.message_delete_delay)

    # Inverse boolean value to loop and unloop.
  #  ctx.voice_state.loop = not ctx.voice_state.loop
  #  if ctx.voice_state.loop:
  #    await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="loop_enabled"), delete_after=default_settings.message_delete_delay)
  #  else:
  #    await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="loop_disabled"), delete_after=default_settings.message_delete_delay)

  @commands.hybrid_command(name='play', aliases=['p'], brief=get_lang_string(group=settings_current_group, id=settings_current_id, key="play_desc"), description=get_lang_string(group=settings_current_group, id=settings_current_id, key="play_desc"))
  async def _play(self, ctx: commands.Context, *, link_or_query: str = commands.parameter(description=get_lang_string(group=settings_current_group, id=settings_current_id, key="play_search_desc"))):
    if link_or_query is not None:
      if not ctx.voice_state.voice:
        self.display_join_message = False
        await ctx.invoke(self._join)
        self.display_join_message = True
  
      async with ctx.typing():
        try:
          source = await YTDLSource.create_source(ctx, link_or_query, loop=self.bot.loop)
        except YTDLError as e:
          await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="an_error_ocurred").format(str(e)), delete_after=default_settings.message_delete_delay)
        else:
          song = Song(source)
  
          await ctx.voice_state.songs.put(song)
          await ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="enqueued").format(str(source)), delete_after=default_settings.message_delete_delay)
    else:
      async with ctx.typing():
        ctx.send(get_lang_string(group=settings_current_group, id=settings_current_id, key="play_search_req_desc"))

  @_join.before_invoke
  @_play.before_invoke
  async def ensure_voice_state(self, ctx: commands.Context):
    if not ctx.author.voice or not ctx.author.voice.channel:
      raise commands.CommandError(get_lang_string(group=settings_current_group, id=settings_current_id, key="not_connected_voice_ch"))

    if ctx.voice_client:
      if ctx.voice_client.channel != ctx.author.voice.channel:
        raise commands.CommandError(get_lang_string(group=settings_current_group, id=settings_current_id, key="already_in_voice_channel"))
            
  @_summon.after_invoke
  @_join.after_invoke
  @_play.after_invoke
  async def deaf_itself(self, ctx: commands.Context):
    if is_guild(ctx):
      try:
        member = ctx.message.guild.get_member(self.bot.user.id)
        if member.guild_permissions.deafen_members:
          await member.edit(deafen=True)
        else:
          await ctx.guild.change_voice_state(channel=ctx.voice_client.channel, self_deaf=True)
      except Exception as e:
        print(str(e))

async def setup(bot):
  await bot.add_cog(Music(bot))