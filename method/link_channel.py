import discord
import asyncio
from prisma import Prisma
db = Prisma()
# print("Link_channel.py")
async def del_link_msg(message, bot):
    Guild = bot.get_guild(message.guild.id)
    await db.connect()
    database = await db.linksonly.find_first(where={"server_id":message.guild.id,"channel_id":message.channel.id})
    await db.disconnect()
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
                if warning.author == bot.user:
                    await warning.delete()
                return
                    
                
    else:
        print("Message without a valid link")
        return
    
        # Process commands after the cleanup logic
    # await bot.process_commands(message)