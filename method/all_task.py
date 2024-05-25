# update_member_count.py
from discord.ext import tasks
import scrapetube
import discord
from prisma import Prisma
db = Prisma()
# print("update_member_count.py")

# async def updateMemberCount1(bot, server_id,db):
async def updateMemberCount(bot, server_id):
    await db.connect()
    try:
        guild = bot.get_guild(server_id)
        if not guild:
            print('Guild not found.')
            await db.disconnect()
            return
        server = await db.membercount.find_first(where={"server_id": server_id})
        if server == None:
            print(f"Server {guild.name} not found in database.")
            await db.disconnect()
            return
        member_count_channel = bot.get_channel(server.Total_Members)
        bot_count_channel = bot.get_channel(server.Online_Members)
        Online_Members_channel = bot.get_channel(server.Bots)
        
        if guild and (member_count_channel and bot_count_channel and Online_Members_channel):
            member_count = guild.member_count
            bot_count = len([m for m in guild.members if m.bot])
            Online_Members = len(list(filter(lambda m: m.status == discord.Status.online, guild.members)))
 
            await member_count_channel.edit(name=f'😁Total Members: {member_count}')
            await bot_count_channel.edit(name=f'😎Online Members: {Online_Members}')
            await Online_Members_channel.edit(name=f'🤖Bots: {bot_count}')
            # print(f'Member count updated successfully: {bot_count}')
        else:
            print('Guild or channel not found.')
    except Exception as e:
        print(f'Error updating member count: {e}')
    await db.disconnect() 
    
async def youtube(bot, server_id):
    print("------------------youtube------------------")
    await db.connect()
    print("server: ", server_id)
    youtube = await db.youtubesetting.find_first(where={"server_id": server_id})
    print("dataTable:",youtube)
    ss = await db.server.find_first(where={"server_id": server_id})
    print("dataTable:",ss)
    if youtube == None:
        print("Not data found in database for youtube")
        await db.disconnect()
        await bot.get_channel(ss.log_channel).send("Not data found in database for youtube")
        return
    # .set({"status":False,"channel_id":'',"channel_name":"","youtube_channels":[]})
    youtube_data = youtube
    youtube_channels = await db.youtubesubchannel.find_many(where={"server_id": server_id})
    if youtube_channels == None:
        print("No youtube channel found in database")
        await bot.get_channel(ss.log_channel).send("No youtube channel found in database")
        await db.disconnect()
        return
    stored_videos = await db.youtubevideos.find_many(where={"server_id": server_id})
    if stored_videos == None:
        print("No video found in database")
        await bot.get_channel(ss.log_channel).send("No video found in database")
        await db.disconnect()
        return
    channel_id = youtube.channel_id
    discord_channel = bot.get_channel(int(channel_id))

    if discord_channel is None:
        print(f"Could not access channel with ID: {channel_id}.")
    else:
        print(f"Notification channel: {discord_channel.name}")
        for channel in youtube_channels:
            print(f"Checking channel: {channel.channel}")
            videos = scrapetube.get_channel(channel_username=channel.channel, limit=3)

            for video in videos:
                video_id = video['videoId']
                vid = await db.youtubevideos.find_first(where={"server_id":server_id,"video_id":video_id})
                if vid == None:
                    await db.youtubevideos.create({"server_id":server_id,"channel":channel.channel,"video_id":video_id})
                    print(f"New video found: {video_id}")
                    url = f"https://youtube.com/watch?v={video_id}"
                    print(f"New video: \n{url}")
                    await discord_channel.send(f"Hey @everyone, **{channel.channel}** just posted a video! Go check it out!\n\n{url}")
    await db.disconnect()
