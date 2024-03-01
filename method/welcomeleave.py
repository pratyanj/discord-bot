# welcome_leave.py
import discord

# print("welcomeleave.py")
async def welcome(member, db):
    server = db.collection("servers").document(str(member.guild.id))
    if not server.get().exists:
        return
    channel = server.collection("Welcome_Leave").document("welcome").get()
    if channel.to_dict()["status"] == False or "false":
        return
    if channel.to_dict()["message"] == '':
        message = f"Welcome to the server, {member.mention}! We are glad to have you."
    else:
        message = channel.to_dict()["message"]
    if channel.to_dict()["channel_id"] == 0:
        return
    else:
        welcome_channel_id = channel.to_dict()['channel_id']
    
    print("welcome_channel_id:",welcome_channel_id)
    welcome_channel = member.guild.get_channel(welcome_channel_id)
    welcome_message = discord.Embed(
        title="Welcome to",
        description=message,
        color=discord.Colour.from_rgb(0, 96, 154))
    await welcome_channel.send(embed=welcome_message)


async def Goodbye(member, db):
    server = db.collection("servers").document(int(member.guild.id))
    if not server.get().exists :
        return
    channel = server.collection("Welcome_Leave").document("leave").get()
    if channel.to_dict()["status"] == False or "false":
        return
    channel = db.collection("channel_id").document("leave_channel_id").get()
    leave_channel_id = next(iter(channel.to_dict().values()), None)
    leave_channel = member.guild.get_channel(leave_channel_id)
    leave_message = discord.Embed(
        title="Goodbye",
        description=f"Goodbye, {member.name}! We will miss you.",
        color=discord.Colour.from_rgb(0, 96, 154))
    await leave_channel.send(embed=leave_message)
