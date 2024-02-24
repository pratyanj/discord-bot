import discord
import asyncio

print("Link_channel.py")
async def del_link_msg(message, link_channel_list, bot):
    if not message.content.startswith("http") and not message.content.startswith("https"):
        if message.channel.id in link_channel_list and not message.author.bot:   
                print("valid link")
                # Delete the message if it has attachments or doesn't contain a valid link
                await message.delete()

                # Send a warning message
                warning_message = f'{message.author.mention}, messages are not allowed here. Please only send valid links.'
                warning = await message.channel.send(warning_message)
                # Schedule the deletion of the warning message after 5 seconds
                await asyncio.sleep(5)
                print("Deleting warning message")
                # Check if the bot is not the author before attempting to delete
                if warning.author == bot.user:
                    await warning.delete()
    else:
        print("Message without a valid link")

        # Process commands after the cleanup logic
    await bot.process_commands(message)