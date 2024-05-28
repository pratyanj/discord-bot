import discord
from discord.ext import commands ,tasks
import scrapetube
from prisma import Prisma

class youtube(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.db = Prisma()
        self.check_youtube_videos.start()
        
    async def db_connect(self):
        if not self.db.is_connected():
            print("Connecting to database...")
            await self.db.connect()

    async def db_disconnect(self):
        if self.db.is_connected():
            await self.db.disconnect()
            print("Disconnected from database")
    
    @tasks.loop(minutes=1)
    async def check_youtube_videos(self):
        print("--------- YouTube Task ---------")
        for guild in self.bot.guilds:
            print(f"YouTube Processing guild: {guild.name} ({guild.id})")
            try:
                await self.db_connect()
                print(f"Querying YouTube settings from database {guild.id}...")
                youtube_notification = await self.db.youtubesetting.find_unique(where={"server_id": guild.id})

                if youtube_notification is None:
                    print(f"{guild.name} not found in database")
                    continue

                if youtube_notification.status:
                    print(
                        f"Handling YouTube notifications for {guild.name}")
                    await self.youtube(self, guild.id)
            except Exception as e:
                print(
                    f"Error handling YouTube notifications for {guild.name}: {e}\n")
            finally:
                await self.db_disconnect()
    
    async def youtube(self, server_id):
        print("------------------youtube------------------")
        await self.db_connect()
        print("server: ", server_id)
        youtube = await self.db.youtubesetting.find_first(where={"server_id": server_id})
        print("dataTable:", youtube)
        ss = await self.db.server.find_first(where={"server_id": server_id})
        print("dataTable:", ss)
        if youtube is None:
            print("No data found in database for YouTube")
            await self.db_disconnect()
            await self.bot.get_channel(ss.log_channel).send("No data found in database for YouTube")
            return
        
        youtube_channels = await self.db.youtubesubchannel.find_many(where={"server_id": server_id})
        if not youtube_channels:
            print("No YouTube channels found in database")
            await self.bot.get_channel(ss.log_channel).send("No YouTube channels found in database")
            await self.db_disconnect()
            return
        
        stored_videos = await self.db.youtubevideos.find_many(where={"server_id": server_id})
        if not stored_videos:
            print("No videos found in database")
            await self.bot.get_channel(ss.log_channel).send("No videos found in database")
            await self.db_disconnect()
            return
        
        channel_id = youtube.channel_id
        discord_channel = self.bot.get_channel(int(channel_id))

        if discord_channel is None:
            print(f"Could not access channel with ID: {channel_id}.")
        else:
            print(f"Notification channel: {discord_channel.name}")
            for channel in youtube_channels:
                print(f"Checking channel: {channel.channel}")
                videos = scrapetube.get_channel(channel_username=channel.channel, limit=3)

                for video in videos:
                    video_id = video['videoId']
                    vid = await self.db.youtubevideos.find_first(where={"server_id": server_id, "video_id": video_id})
                    if vid is None:
                        await self.db.youtubevideos.create({"server_id": server_id, "channel": channel.channel, "video_id": video_id})
                        print(f"New video found: {video_id}")
                        url = f"https://youtube.com/watch?v={video_id}"
                        print(f"New video: \n{url}")
                        await discord_channel.send(f"Hey @everyone, **{channel.channel}** just posted a video! Go check it out!\n\n{url}")
        await self.db_disconnect()

    @check_youtube_videos.before_loop
    async def before_tasks(self):
        await self.bot.wait_until_ready()
        
async def setup(bot:commands.Bot):
    await bot.add_cog(youtube(bot))