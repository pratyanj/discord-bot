import discord
from discord.ext import commands
from yt_dlp import YoutubeDL
import asyncio

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.Mcolor = discord.Colour.from_rgb(0, 97, 146)
        
        self.is_playing = False
        self.is_paused = False
        
        self.music_queue = []
        self.YDL_OPTIONS = {
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
        }
        self.FFMPEG_OPTIONS = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", 
            "options": "-vn"
        }
        
        self.vc = None
        self.ytdl = YoutubeDL(self.YDL_OPTIONS)
        
    def search_yt(self, item: str):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try: 
                info = ydl.extract_info(item, download=False)
                if 'entries' in info:
                    info = info['entries'][0]
                return {'source': info['formats'][0]['url'], 'title': info['title']}
            except Exception as e:
                print(f"Error: {e}")
                return False
        
    async def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0]['source']
            self.music_queue.pop(0)
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(m_url, download=False))
            song = data['url']
            self.vc.play(discord.FFmpegPCMAudio(song, **self.FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(), self.bot.loop))
        else:
            self.is_playing = False
    
    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0]['source']
            if self.vc is None or not self.vc.is_connected():
                try:
                    self.vc = await self.music_queue[0]['voice_channel'].connect()
                except Exception as e:
                    await ctx.send("```Could not connect to the voice channel. Make sure PyNaCl is installed.```")
                    print(f"Connection error: {e}")
                    return
            else:
                await self.vc.move_to(self.music_queue[0]['voice_channel'])
            
            self.music_queue.pop(0)
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(m_url, download=False))
            song = data['url']
            self.vc.play(discord.FFmpegPCMAudio(song, **self.FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(), self.bot.loop))
        else:
            self.is_playing = False
    
    @commands.command(name="play", aliases=["p","playing"], help="Plays a selected song from youtube")
    async def play(self, ctx: commands.Context, *args):
        query = " ".join(args)
        try:
            voice_channel = ctx.author.voice.channel
        except AttributeError:
            await ctx.send("```You need to connect to a voice channel first!```")
            return
        if self.is_paused:
            self.vc.resume()
            self.is_paused = False
        else:
            song = self.search_yt(query)
            if song is False:
                await ctx.send("```Could not download the song. Incorrect format try another keyword. This could be due to playlist or a livestream format.```")
            else:
                if self.is_playing:
                    await ctx.send(f"**#{len(self.music_queue) + 1} - '{song['title']}'** added to the queue")
                else:
                    await ctx.send(f"**'{song['title']}'** added to the queue")  
                self.music_queue.append({'source': song['source'], 'title': song['title'], 'voice_channel': voice_channel})
                if not self.is_playing:
                    await self.play_music(ctx)

    @commands.command(name="pause", help="Pauses the current song being played")
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()

    @commands.command(name="resume", aliases=["r"], help="Resumes playing with the discord bot")
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    @commands.command(name="skip", aliases=["s"], help="Skips the current song being played")
    async def skip(self, ctx):
        if self.vc is not None and self.vc.is_playing():
            self.vc.stop()
            await self.play_music(ctx)

    @commands.command(name="queue", aliases=["q"], help="Displays the current songs in queue")
    async def queue(self, ctx):
        retval = ""
        for i, song in enumerate(self.music_queue):
            retval += f"#{i + 1} - {song['title']}\n"

        if retval != "":
            await ctx.send(f"```Queue:\n{retval}```")
        else:
            await ctx.send("```No music in queue```")

    @commands.command(name="clear", aliases=["c", "bin"], help="Stops the music and clears the queue")
    async def clear(self, ctx):
        if self.vc is not None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        self.is_playing = False
        self.is_paused = False
        await ctx.send("```Music queue cleared```")

    @commands.command(name="stop", aliases=["disconnect", "l", "d"], help="Kick the bot from VC")
    async def dc(self, ctx):
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()

    @commands.command(name="remove", help="Removes last song added to queue")
    async def remove(self, ctx):
        if self.music_queue:
            removed_song = self.music_queue.pop()
            await ctx.send(f"```Removed: {removed_song['title']}```")
        else:
            await ctx.send("```No song to remove```")
        
async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
