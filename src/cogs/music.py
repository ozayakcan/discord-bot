import math

import discord
from discord.ext import commands

from utils import music, settings, views

class Music(commands.Cog, description= settings.lang_string("music_cog_desc")):
  def __init__(self, bot: commands.Bot):
    self.bot = bot
    self.voice_states = {}
    self.display_join_message = True

  def get_voice_state(self, ctx: commands.Context):
    state = self.voice_states.get(ctx.guild.id)
    if not state:
      state = music.VoiceState(self.bot, ctx)
      self.voice_states[ctx.guild.id] = state

    return state

  async def clear_music(self, ctx: commands.Context):
    if not ctx.voice_state.voice:
      await ctx.send(settings.lang_string("not_connected_voice_ch"))
      return False
    try:
      ctx.voice_state.songs.clear()
      if ctx.voice_state.is_playing:
        await ctx.voice_state.stop()
      else:
        await ctx.voice_state.voice.disconnect()
      del self.voice_states[ctx.guild.id]
      await ctx.send(settings.lang_string("stop_leave_success"))
    except Exception as e:
      print("Stop/Leave failed: "+str(e))
      await ctx.send(settings.lang_string("stop_leave_failed"))
      return False
    return True

  def cog_unload(self):
    for state in self.voice_states.values():
      self.bot.loop.create_task(state.stop())

  def cog_check(self, ctx: commands.Context):
    if not settings.is_guild(ctx):
      raise commands.NoPrivateMessage(settings.lang_string("command_dm"))
    # Disable commands for now
    #raise commands.CommandError('Music commands not available right now.')
    #return False # return True
    return True

  async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
    settings.update_currents(ctx=ctx)
    await settings.send_cog_error(ctx=ctx, error=error)

  async def cog_before_invoke(self, ctx: commands.Context):
    ctx.voice_state = self.get_voice_state(ctx)
    settings.update_currents(ctx=ctx)

  @commands.hybrid_command(name='join', aliases=['j'], invoke_without_subcommand=True, brief=settings.lang_string("join_desc"), description=settings.lang_string("join_desc"))
  async def _join(self, ctx: commands.Context):

    destination = ctx.author.voice.channel
    if ctx.voice_state.voice:
      await ctx.voice_state.voice.move_to(destination)
      return

    ctx.voice_state.voice = await destination.connect()
    if self.display_join_message:
      await ctx.send(settings.lang_string("join_success"))

  @commands.hybrid_command(name='summon', aliases=['sum'], brief=settings.lang_string("summon_desc"), description=settings.lang_string("summon_desc_full"))
  @commands.has_permissions(manage_guild=True)
  async def _summon(self, ctx: commands.Context, *, channel: discord.VoiceChannel = commands.parameter(default=None, description=settings.lang_string("summon_channel_desc"))):

    if not channel and not ctx.author.voice:
      raise music.VoiceError(settings.lang_string("not_connected_voice_ch_or_not_specified"))

    destination = channel or ctx.author.voice.channel
    if ctx.voice_state.voice:
      await ctx.voice_state.voice.move_to(destination)
      return await ctx.send(settings.lang_string("summon_success").format(f"<#{destination.id}>"))

    ctx.voice_state.voice = await destination.connect()
    await ctx.send(settings.lang_string("summon_success").format(f"<#{destination.id}>"))

  @commands.hybrid_command(name='leave', aliases=['l', 'disconnect', 'd'], brief=settings.lang_string("stop_leave_desc"), description=settings.lang_string("stop_leave_desc"))
  @commands.has_permissions(manage_guild=True)
  async def _leave(self, ctx: commands.Context):

    #if not ctx.voice_state.voice:
    #    return await ctx.send(settings.lang_string("not_connected_voice_ch"))

    #await ctx.voice_state.stop()
    #del self.voice_states[ctx.guild.id]
    #await ctx.message.add_reaction('✅')
    leave_status = await self.clear_music(ctx)
    if leave_status:
      await ctx.message.add_reaction('✅')
      

  @commands.hybrid_command(name='volume', aliases=['v', 'vol'], brief=settings.lang_string("volume_desc"), description=settings.lang_string("volume_desc"))
  async def _volume(self, ctx: commands.Context, *, volume: commands.Range[int, 1, 100] = commands.parameter(description=settings.lang_string("volume_level_desc"))):

    if volume is None:
      volume = -1

    if not ctx.voice_state.is_playing:
      return await ctx.send(settings.lang_string("not_playing"))

    if 0 > volume or volume > 100:
      return await ctx.send(settings.lang_string("vol_err"))

    ctx.voice_state.volume = volume / 100
    await ctx.send(settings.lang_string("vol_set").format(volume))

  @commands.hybrid_command(name='now', aliases=['current', 'playing', 'n', 'c'], brief=settings.lang_string("now_desc"), description=settings.lang_string("now_desc"))
  async def _now(self, ctx: commands.Context):
    if not ctx.voice_state.is_playing:
      return await ctx.send(settings.lang_string("not_playing"))

    await ctx.send(embed=ctx.voice_state.current.create_embed())

  @commands.hybrid_command(name='pause', brief=settings.lang_string("pause_desc"), description=settings.lang_string("pause_desc"))
  @commands.has_permissions(manage_guild=True)
  async def _pause(self, ctx: commands.Context):

    if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
      ctx.voice_state.voice.pause()
      await ctx.message.add_reaction('⏯')
      await ctx.send(settings.lang_string("pause_success"))
    else:
      await ctx.send(settings.lang_string("pause_fail"))

  @commands.hybrid_command(name='resume', aliases=['res', 'r'], brief=settings.lang_string("resume_desc"), description=settings.lang_string("resume_desc"))
  @commands.has_permissions(manage_guild=True)
  async def _resume(self, ctx: commands.Context):

    if ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
      ctx.voice_state.voice.resume()
      await ctx.message.add_reaction('⏯')
      await ctx.send(settings.lang_string("resume_success"))
    else:
      await ctx.send(settings.lang_string("resume_fail"))

  @commands.hybrid_command(name='stop', brief=settings.lang_string("stop_leave_desc"), description=settings.lang_string("stop_leave_desc"))
  @commands.has_permissions(manage_guild=True)
  async def _stop(self, ctx: commands.Context):
    #ctx.voice_state.songs.clear()

    #if ctx.voice_state.is_playing:
    #    ctx.voice_state.voice.stop()
    #    await ctx.message.add_reaction('⏹')
    stop_status = await self.clear_music(ctx)
    if stop_status:
      await ctx.message.add_reaction('⏹')


  @commands.hybrid_command(name='skip', aliases=['s'], brief=settings.lang_string("skip_desc"), description=settings.lang_string("skip_desc"))
  async def _skip(self, ctx: commands.Context):

    if not ctx.voice_state.is_playing:
      return await ctx.send(settings.lang_string("not_playing"))

    voter = ctx.message.author
    if voter == ctx.voice_state.current.requester:
      await ctx.message.add_reaction('⏭')
      ctx.voice_state.skip()
      await ctx.send(settings.lang_string("skip_success"))
    elif voter.id not in ctx.voice_state.skip_votes:
      ctx.voice_state.skip_votes.add(voter.id)
      total_votes = len(ctx.voice_state.skip_votes)

      if total_votes >= 3:
        await ctx.message.add_reaction('⏭')
        ctx.voice_state.skip()
        await ctx.send(settings.lang_string("skip_success"))
      else:
        await ctx.send(settings.lang_string("skip_vote_added").format(total_votes))

    else:
      await ctx.send(settings.lang_string("skip_already_voted"))

  @commands.hybrid_command(name='queue', aliases=['q'], brief=settings.lang_string("queue_desc"), description=settings.lang_string("queue_desc"))
  async def _queue(self, ctx: commands.Context, *, page: int = commands.parameter(default=1, description=settings.lang_string("queue_page_desc"))):

    if ctx.voice_state.songs.len_all() == 0:
      return await ctx.send(settings.lang_string("empty_queue"))

    items_per_page = 10
    pages = math.ceil(ctx.voice_state.songs.len_all() / items_per_page)

    start = (page - 1) * items_per_page
    end = start + items_per_page

    queue = ''
    for i, song in enumerate(ctx.voice_state.songs.get_all(slice(start, end)), start=start):
      queue += settings.lang_string("queue_pattern").format(i + 1, song, settings.lang_string("queue_current") if song == ctx.voice_state.songs.current else "")

    embed = (discord.Embed(description=settings.lang_string("tracks").format(ctx.voice_state.songs.len_all(), queue))
             .set_footer(text=settings.lang_string("viewing_page").format(page, pages)))
    await ctx.send(embed=embed)

  @commands.hybrid_command(name='shuffle', aliases=['shuf'], brief=settings.lang_string("shuffle_desc"), description=settings.lang_string("shuffle_desc"))
  async def _shuffle(self, ctx: commands.Context):

    if ctx.voice_state.songs.len_all() == 0:
      return await ctx.send(settings.lang_string("empty_queue"))

    ctx.voice_state.songs.shuffle()
    await ctx.message.add_reaction('✅')

  @commands.hybrid_command(name='remove', aliases=['rem'], brief=settings.lang_string("remove_desc"), description=settings.lang_string("remove_desc"))
  async def _remove(self, ctx: commands.Context, index: commands.Range[int, 1] = commands.parameter(description=settings.lang_string("remove_index_desc"))):
    
    if index is None:
      index = 0

    if index <= 0:
      return await ctx.send(settings.lang_string("remove_index_err"))
    if ctx.voice_state.songs.len_all() == 0:
      return await ctx.send(settings.lang_string("empty_queue"))

    removed_song = ctx.voice_state.songs.remove(index - 1, ctx.voice_state)
    await ctx.message.add_reaction('✅')
    await ctx.send(settings.lang_string("track_removed").format(f"**{str(removed_song.source.title)}**"))

  #@commands.hybrid_command(name='loop',  aliases=['repeat', 'rep'], brief=settings.lang_string("loop_desc"), description=settings.lang_string("loop_desc_full"))
  #async def _loop(self, ctx: commands.Context):

  #  if not ctx.voice_state.is_playing:
  #    return await ctx.send(settings.lang_string("not_playing"))

    # Inverse boolean value to loop and unloop.
  #  ctx.voice_state.loop = not ctx.voice_state.loop
  #  if ctx.voice_state.loop:
  #    await ctx.send(settings.lang_string("loop_enabled"))
  #  else:
  #    await ctx.send(settings.lang_string("loop_disabled"))

  async def put_songs(self, ctx: commands.Context, song_list, interaction: discord.Interaction = None):
    settings.update_currents(interaction=interaction)
    ctx.voice_state = self.get_voice_state(ctx)
    if isinstance(song_list, music.SongList):
      for source in song_list.sources:
        await ctx.voice_state.songs.put(source)
      if song_list.is_playlist:
        await ctx.send(settings.lang_string("enqueued").format(song_list.playlist_title))
      else:
        await ctx.send(settings.lang_string("enqueued").format(str(song_list.sources[0].source)))
    else:
      await ctx.voice_state.songs.put(song_list)
      await ctx.send(settings.lang_string("enqueued").format(str(song_list.source)))
    if interaction is not None:
      await interaction.message.delete()
  
  @commands.hybrid_command(name='play', aliases=['p'], brief=settings.lang_string("play_desc"), description=settings.lang_string("play_desc"))
  async def _play(self, ctx: commands.Context, *, link_or_query: str = commands.parameter(description=settings.lang_string("play_search_desc"))):
    try:
      if link_or_query is not None:
        if not ctx.voice_state.voice:
          self.display_join_message = False
          await ctx.invoke(self._join)
          self.display_join_message = True
    
        async with ctx.typing():
          try:
            song_list = await music.YTDLSource.create_source(ctx, link_or_query, loop=self.bot.loop)
          except music.YTDLError as e:
            await ctx.send(settings.lang_string("an_error_ocurred").format(ctx.clean_prefix, "play", str(e)))
          else:
            if len(song_list.sources) > 0:
              if song_list.is_playlist:
                await self.put_songs(ctx, song_list)
              elif len(song_list.sources) == 1:
                await self.put_songs(ctx, song_list.sources[0])
              else:
                view = views.ButtonsSong(
                  on_select = self.put_songs,
                  song_list = song_list,
                  ctx = ctx
                )
                s_list = ''
                s_index = 0
                for song in song_list.sources[0:5]:
                  s_index += 1
                  s_list += settings.lang_string("queue_pattern").format(s_index, song, "")
                embed = (discord.Embed(description=settings.lang_string("choose_song").format(s_list)))
                await ctx.send(embed=embed, view=view, delete_after=60)
            else:
              await ctx.send(settings.lang_string("yt_could_not_find").format(link_or_query))
      else:
        async with ctx.typing():
          await ctx.send(settings.lang_string("play_search_req_desc"))
    except Exception as e:
      print(str(e))
      await ctx.send(settings.lang_string("an_error_ocurred").format(ctx.clean_prefix, 'play', str(e)))

  @_join.before_invoke
  @_play.before_invoke
  async def ensure_voice_state(self, ctx: commands.Context):
    if not ctx.author.voice or not ctx.author.voice.channel:
      raise commands.CommandError(settings.lang_string("not_connected_voice_ch"))

    if ctx.voice_client:
      if ctx.voice_client.channel != ctx.author.voice.channel:
        raise commands.CommandError(settings.lang_string("already_in_voice_channel"))
            
  @_summon.after_invoke
  @_join.after_invoke
  @_play.after_invoke
  async def deaf_itself(self, ctx: commands.Context):
    if settings.is_guild(ctx):
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