# welcome_leave.py
import discord
from prisma import Prisma
db = Prisma()


async def welcome(member):
    await db.connect()
    server = await db.welcome.find_unique(where={"server_id": member.guild.id})
    ss = await db.server.find_unique(where={"server_id": member.guild.id})
    if server == None:
        print(f"Server {member.guild.name} not found in database.")
        await db.disconnect()
        em = discord.Embed(
            title="Welcome",
            description=f"Server {member.guild.name} not found in database.",
            color=discord.Colour.red()
        )
        await member.guild.get_channel(int(ss.log_channel)).send(embed=em)
        return
    print("channel:", server.channel_id)

    if server.status == False:
        print(f"{member.guild.name} welcome message system is not enable.")
        await db.disconnect()
        em = discord.Embed(
            title="Welcome",
            description=f"{member.guild.name} welcome message system is not enable.",
            color=discord.Colour.dark_blue()
        )
        await member.guild.get_channel(ss.log_channel).send(embed=em)
        return

    if server.channel_id == 0 or None:
        print(
            f"Welcome channel not set for {member.guild.name}. Please set welcome channel.")
        await db.disconnect()
        em = discord.Embed(
            title="Welcome",
            description=f"Welcome channel not set for {member.guild.name}. Please set welcome channel.",
            color=discord.Colour.dark_blue()
        )
        await member.guild.get_channel(ss.log_channel).send(embed=em)
        return

    else:
        welcome_channel_id = server.channel_id

    if server.message == '':
        message = f"Welcome to the server, {member.mention}! We are glad to have you."

    else:
        message = server.message
    print("welcome_channel_id:", welcome_channel_id)
    # gud=member.guild(member.guild.id)
    welcome_channel = member.guild.get_channel(int(welcome_channel_id))
    print(welcome_channel)
    welcome_message = discord.Embed(
        title="Welcome to",
        description=message,
        color=discord.Colour.from_rgb(0, 96, 154))
    await welcome_channel.send(embed=welcome_message)
    await db.disconnect()


async def join_role(member, bot):
    await db.connect()
    join_role = await db.joinrole.find_unique(where={"server_id": member.guild.id})
    ss = await db.server.find_unique(where={"server_id": member.guild.id})
    if join_role == None:
        print("Not data found in database for join role")
        await db.disconnect()
        em = discord.Embed(
            title="Join Role",
            description="Not data found in database for join role",
            color=discord.Colour.red()
            )
        await member.guild.get_channel(ss.log_channel).send(embed=em)
        return
    role = discord.utils.get(member.guild.roles, id=join_role.role_id)
    if role is None:
        print("Role not found in server")
        await db.disconnect()
        em = discord.Embed(
            title="Join Role",
            description="Role not found in server",
            color=discord.Colour.magenta()
        )
        await member.guild.get_channel(ss.log_channel).send(embed=em)
        await db.disconnect()
        return
    await db.disconnect()
    await member.add_roles(role)


async def Goodbye(member):
    await db.connect()
    server = await db.goodbye.find_unique(where={"server_id": member.guild.id})
    ss = await db.server.find_unique(where={"server_id": member.guild.id})
    if server == None:
        print(f"Server {member.guild.name} not found in database.")
        await db.disconnect()
        em = discord.Embed(
            title="Database", description=f"Server {member.guild.name} not found in database.", color=discord.Colour.red())
        await member.guild.get_channel(ss.log_channel).send(embed=em)
        return
    if server.status == False:
        await db.disconnect()
        print(f"{member.guild.name} Goodbye message system is not enable.")
        em = discord.Embed(
            title="Goodbye", description="Goodbye message system is not enable.", color=discord.Colour.red())
        await member.guild.get_channel(ss.log_channel).send(embed=em)
        return
    if server.channel_id == 0 or None:
        print(
            f"Goodbye channel not set for {member.guild.name}. Please set Goodbye channel.")
        leave_message = discord.Embed(
            title="Goodbye",
            description=f"Goodbye channel not set for {member.guild.name}. Please set goodbye channel.",
            color=discord.Colour.from_rgb(0, 96, 154))
        await member.guild.get_channel(ss.log_channel).send(embed=leave_message)
        await db.disconnect()
        return
    else:
        leave_channel_id = server.channel_id

    if server.message == '' or None:
        message = f"Goodbye, {member.name}! We will miss you."
    else:
        message = server.message

    leave_channel = member.guild.get_channel(int(leave_channel_id))
    leave_message = discord.Embed(
        title="Goodbye",
        description=message,
        color=discord.Colour.from_rgb(0, 96, 154))
    await db.disconnect()
    await leave_channel.send(embed=leave_message)
