import discord
from discord.ext import commands
from prisma import Prisma
import asyncio

class Image_Link_only(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.db = Prisma()
    
    async def db_connect(self):
        if not self.db.is_connected():
            print("Connecting to database...")
            await self.db.connect()

    async def db_disconnect(self):
        if self.db.is_connected():
            await self.db.disconnect()
            print("Disconnected from database")
       
    async def on_message(self, message:discord.Message):
        if not message.author.bot or self.bot:
            return
        await self.image_channel(message, self)
        # await self.link_channel(message, self)

    async def image_channel(self, message:discord.Message):
        await self.db_connect()
        database = await self.db.imagesonly.find_first(where={"channel_id":message.channel.id,"server_id":message.guild.id})
        # print("del_msg channel_name:",database)
        await  self.db_disconnect()
        if database == None:
            # print("No table found for del_msg database not found")
            return
        if not message.author.bot:
        # if message.channel.id in monitored_channel_ids and not message.author.bot:
            if not message.attachments:
                # print("Message without attachments")
                # Delete the message if it doesn't have attachments (images)
                await message.delete()

                # Send a warning message
                warning_message = f'{message.author.mention}, messages are not allowed here. Please only send your work images.'
                warning = await message.channel.send(warning_message)
                # print("warning:",warning)
                # Schedule the deletion of the warning message after 1 second
                await asyncio.sleep(5)
                # print("Deleting warning message")
                # print("warning.author:",warning.author)
                # print(bot.user)
                # Check if the bot is not the author before attempting to delete
                if warning.author == self.bot.user:
                    await warning.delete()
                return

    async def link_channel(self, message:discord.Message):
        Guild = self.bot.get_guild(message.guild.id)
        await self.db_connect()
        database = await self.db.linksonly.find_first(where={"server_id":message.guild.id,"channel_id":message.channel.id})
        await self.db_disconnect()
        if database == None:
            # print("database not found for del_link_msg")
            return

        if not message.content.startswith("http") and not message.content.startswith("https"):
            if not message.author.bot:   
                    # print("valid link")
                    # Delete the message if it has attachments or doesn't contain a valid link
                    await message.delete()

                    # Send a warning message
                    warning_message = f'{message.author.mention}, messages are not allowed here. Please only send valid links.'
                    warning = await message.channel.send(warning_message)
                    # Schedule the deletion of the warning message after 5 seconds
                    await asyncio.sleep(5)
                    # print("Deleting warning message")
                    # Check if the bot is not the author before attempting to delete
                    if warning.author == self.bot.user:
                        await warning.delete()
                    return
                        
                    
        else:
            print("Message without a valid link")
            return
async def setup(bot:commands.Bot):
    await bot.add_cog(Image_Link_only(bot))