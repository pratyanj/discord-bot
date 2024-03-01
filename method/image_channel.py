import discord
import asyncio

# print("image_channel.py")
async def del_msg(message, monitored_channel_ids, bot):
    if message.channel.id in monitored_channel_ids and not message.author.bot:
        if not message.attachments:
            print("Message without attachments")
            # Delete the message if it doesn't have attachments (images)
            await message.delete()

            # Send a warning message
            warning_message = f'{message.author.mention}, messages are not allowed here. Please only send your work images.'
            warning = await message.channel.send(warning_message)
            print("warning:",warning)
            # Schedule the deletion of the warning message after 1 second
            await asyncio.sleep(5)
            print("Deleting warning message")
            print("warning.author:",warning.author)
            print(bot.user)
            # Check if the bot is not the author before attempting to delete
            if warning.author == bot.user:
                await warning.delete()

