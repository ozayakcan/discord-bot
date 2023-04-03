import asyncio
from async_timeout import timeout
from discord.ext import commands

from ._queue import SongQueue
from utils import settings

def parse_duration(duration: int):
    minutes, seconds = divmod(duration, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    duration = []
    if days > 0:
      duration.append(settings.lang_string("days").format(days))
    if hours > 0:
      duration.append(settings.lang_string("hours").format(hours))
    if minutes > 0:
      duration.append(settings.lang_string("minutes").format(minutes))
    if seconds > 0:
      duration.append(settings.lang_string("seconds").format(seconds))

    return ', '.join(duration)

class VoiceError(Exception):
  pass

class YTDLError(Exception):
  pass

class VoiceState:
  def __init__(self, bot: commands.Bot, ctx: commands.Context):
    self.bot = bot
    self._ctx = ctx

    settings.update_currents(ctx=self._ctx)

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
    while True:
      self.next.clear()

      # Try to get the next song within 3 minutes.
      # If no song will be added to the queue in time,
      # the player will disconnect due to performance
      # reasons.
      try:
        timeout_val = 180 # 3 minutes
        async with timeout(timeout_val):
          if self.get_mem_count() == 0:
            self.bot.loop.create_task(self.stop())
            await self._ctx.send(settings.lang_string("no_user_leave_msg").format(parse_duration(timeout_val)))
            return
          self.current = await self.songs.get()
      except asyncio.TimeoutError:
        self.bot.loop.create_task(self.stop())
        await self.current.source.channel.send(settings.lang_string("no_track_leave_msg").format(parse_duration(timeout_val)))
        return
      except:
        pass

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
