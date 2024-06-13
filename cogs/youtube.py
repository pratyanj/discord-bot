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
            # print("Connecting to database...")
            await self.db.connect()

    async def db_disconnect(self):
        if self.db.is_connected():
            await self.db.disconnect()
            # print("Disconnected from database")
    
    @tasks.loop(minutes=10)
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
                    await self.youtube_main(self, guild.id)
            except Exception as e:
                print(
                    f"Error handling YouTube notifications for {guild.name}: {e}\n")
            finally:
                await self.db_disconnect()
    
    async def youtube_main(self, server_id):
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
        
    @commands.hybrid_command(name="get_yt_sub_channels", description="Get YouTube subscribed channels for the guild", with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def get_yt_sub_channels(self, ctx: commands.Context):
        await self.db_connect()
        guild_id = ctx.guild.id
        guild = await self.db.youtubesubchannel.find_many(where={"server_id": guild_id})
        await self.db_disconnect()
        
        if guild:
            channels = [entry.channel for entry in guild]
            await ctx.send(f"Subscribed YouTube channels: {', '.join(channels)}")
        else:
            await ctx.send(f"No YouTube channels found for {ctx.guild.name}.")
        
    @commands.hybrid_command(name="yt_system_status", description="Set the YouTube notification system status", with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def yt_system_status(self, ctx: commands.Context, status: bool):
        await self.db_connect()
        guild_id = ctx.guild.id
        yt = await self.db.youtubesetting.find_unique(where={"server_id": guild_id})
        
        if yt is None:
            await self.db.youtubesetting.create(data={"server_id": guild_id, "status": status, "channel_id": 0, "channel_name": ""})
            message = f"YouTube notification status created and set to {status}."
        else:
            await self.db.youtubesetting.update(where={"ID": yt.ID}, data={"status": status})
            message = f"YouTube notification status updated to {status}."
        
        await self.db_disconnect()
        await ctx.send(message)

    @commands.hybrid_command(name="set_yt_notification_channel", description="Set the YouTube notification channel", with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def set_yt_notification_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        await self.db_connect()
        guild_id = ctx.guild.id
        yt = await self.db.youtubesetting.find_unique(where={"server_id": guild_id})
        
        if yt is None:
            await self.db.youtubesetting.create(data={"server_id": guild_id, "status": True, "channel_id": channel.id, "channel_name": channel.name})
            message = f"YouTube notification created and set to {channel.name} ({channel.id})."
        else:
            await self.db.youtubesetting.update(where={"ID": yt.ID}, data={"channel_id": channel.id, "channel_name": channel.name})
            message = f"YouTube notification channel updated to {channel.name} ({channel.id})."
        
        await self.db_disconnect()
        await ctx.send(message)

    @commands.hybrid_command(name="subscribe_yt_channel", description="Subscribe to a YouTube channel by name", with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def subscribe_yt_channel(self, ctx: commands.Context, yt_channel_usr: str):
        await self.db_connect()
        guild_id = ctx.guild.id
        yt_channels = await self.db.youtubesubchannel.find_many(where={"server_id": guild_id})
        
        if any(channel.channel == yt_channel_usr for channel in yt_channels):
            message = f"YouTube notification is already set for {yt_channel_usr}."
        else:
            await self.db.youtubesubchannel.create(data={"server_id": guild_id, "channel": yt_channel_usr})
            message = f"You subscribe to {yt_channel_usr} the YouTube channel successfully."
        
        await self.db_disconnect()
        await ctx.send(message)

    @commands.hybrid_command(name="remove_yt_channel", description="Remove a YouTube channel subscription", with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def remove_yt_channel(self, ctx: commands.Context, yt_channel_usr: str):
        await self.db_connect()
        guild_id = ctx.guild.id
        yt_channel = await self.db.youtubesubchannel.find_first(where={"server_id": guild_id, "channel": yt_channel_usr})
        
        if yt_channel:
            await self.db.youtubesubchannel.delete(where={"ID": yt_channel.ID})
            message = f"{yt_channel_usr} unsubscribe the YouTube channel successfully."
        else:
            message = f"{yt_channel_usr} is not found in the subscription list."
        
        await self.db_disconnect()
        await ctx.send(message)
        
async def setup(bot:commands.Bot):
    await bot.add_cog(youtube(bot))