# update_member_count.py
from discord.ext import tasks

print("update_member_count.py")
@tasks.loop(minutes=10)
async def updateMemberCount(bot, server_id, member_count_channel_id):
    try:
        guild = bot.get_guild(server_id)
        channel = guild.get_channel(member_count_channel_id)

        if guild and channel:
            member_count = guild.member_count
            await channel.edit(name=f'Member Count: {member_count}')
            print(f'Member count updated successfully: {member_count}')
        else:
            print('Guild or channel not found.')
    except Exception as e:
        print(f'Error updating member count: {e}')
