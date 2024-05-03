# welcome_leave.py
import discord
from prisma import Prisma
# print("welcomeleave.py")
db = Prisma()
# async def welcome(member,db):
     
async def welcome1(member):
    await db.connect()
    server = await db.welcome.find_unique(where={"server_id": member.guild.id})
    ss = await db.server.find_unique(where={"id": member.guild.id})
    if server == None:
        print(f"Server {member.guild.name} not found in database.")
        await member.guild.get_channel(int(ss.log_channel)).send(f"Server {member.guild.name} not found in database.")
        return
    print("channel:", server.channel_id)
    
    if server.status == False:
        print(f"{member.guild.name} welcome message system is not enable.")
        await member.guild.get_channel(ss.log_channel).send(f"{member.guild.name} welcome message system is not enable.")
        return 
    
    if server.channel_id == 0 or None:
        print(f"Welcome channel not set for {member.guild.name}. Please set welcome channel.")
        await member.guild.get_channel(ss.log_channel).send(f"Welcome channel not set for {member.guild.name}. Please set welcome channel.") 
        return
    
    else:
        welcome_channel_id = server.channel_id
        
    if server.message == '':
        message = f"Welcome to the server, {member.mention}! We are glad to have you."
        
    else:
        message = server.message
    print("welcome_channel_id:",welcome_channel_id)
    # gud=member.guild(member.guild.id)
    welcome_channel = member.guild.get_channel(int(welcome_channel_id))
    print(welcome_channel)
    welcome_message = discord.Embed(
        title="Welcome to",
        description=message,
        color=discord.Colour.from_rgb(0, 96, 154))
    await welcome_channel.send(embed=welcome_message)

async def welcome(member,db):
    server = db.collection("servers").document(str(member.guild.id))
    if not server.get().exists:
        print(f"Server {member.guild.name} not found in database.")
        # await member.guild.get_channel(int(member.channel.id)).send(f"Server {member.guild.name} not found in database.")
        return
    channel = server.collection("Welcome_Leave").document("welcome").get()
    print("channel:",channel.to_dict())
    if channel.to_dict()["status"] == False:
        print(f"{member.guild.name} welcome message system is not enable.")
        # await member.guild.get_channel(int(member.channel.id)).send(f"{member.guild.name.mention} welcome message system is not enable.")
        return 
    if channel.to_dict()["channel_id"] == 0:
        print(f"Welcome channel not set for {member.guild.name}. Please set welcome channel.")
        # await member.guild.get_channel(int(member.channel.id)).send(f"Welcome channel not set for {member.guild.name}. Please set welcome channel.") 
        return
    else:
        welcome_channel_id = channel.to_dict()['channel_id']

    if channel.to_dict()["message"] == '':
        message = f"Welcome to the server, {member.mention}! We are glad to have you."
    else:
        message = channel.to_dict()["message"]
    
    
    print("welcome_channel_id:",welcome_channel_id)
    # gud=member.guild(member.guild.id)
    welcome_channel = member.guild.get_channel(int(welcome_channel_id))
    print(welcome_channel)
    welcome_message = discord.Embed(
        title="Welcome to",
        description=message,
        color=discord.Colour.from_rgb(0, 96, 154))
    await welcome_channel.send(embed=welcome_message)

async def join_role(member,bot,db):
    
    join_role_id = db.collection("servers").document(str(member.guild.id)).collection("moderation").document("Join_Member_Role")
    if not join_role_id.get().exists:
        print("Not data found in database for join role")
        return
    join_role_id = int(join_role_id.get().to_dict()['role_id'])
    role = discord.utils.get(member.guild.roles, id=join_role_id)
    if role is None:
        print("Role not found in server")
        return
    await member.add_roles(role)
    
async def join_role1(member,bot):
    join_role = await db.joinrole.find_unique(where={"server_id": member.guild.id})
    ss = await db.server.find_unique(where={"id": member.guild.id})
    if join_role == None:
        print("Not data found in database for join role")
        await member.guild.get_channel(ss.log_channel).send("Not data found in database for join role")
        return
    role = discord.utils.get(member.guild.roles, id=join_role.role_id)
    if role is None:
        print("Role not found in server")
        await member.guild.get_channel(ss.log_channel).send("Role not found in server")
        return
    await db.connect()
    await member.add_roles(role)

async def Goodbye1(member):
    server = await db.goodbye.find_unique(where={"server_id": member.guild.id})
    ss = await db.server.find_unique(where={"id": member.guild.id})
    if server == None:
        print(f"Server {member.guild.name} not found in database.")
        await member.guild.get_channel(ss.log_channel).send(f"Server {member.guild.name} not found in database.")
        return
    if server.status == False:
        print(f"{member.guild.name} welcome message system is not enable.")
        return
    if server.channel_id == 0 or None:
        print(f"Welcome channel not set for {member.guild.name}. Please set welcome channel.")
        await member.guild.get_channel(ss.log_channel).send(f"Goodbye channel not set for {member.guild.name}. Please set goodbye channel.")
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
    await db.connect()
    await leave_channel.send(embed=leave_message)
    
async def Goodbye(member, db):
    server = db.collection("servers").document(str(member.guild.id))
    if not server.get().exists :
        print(f"Server {member.guild.name} not found in database.")
        return
    channel = server.collection("Welcome_Leave").document("leave").get()
    if channel.to_dict()["status"] == False:
        print(f"{member.guild.name} welcome message system is not enable.")
        return
    if channel.to_dict()["channel_id"] == 0:
        print(f"Welcome channel not set for {member.guild.name}. Please set welcome channel.")
        return
    else:
        leave_channel_id = channel.to_dict()['channel_id']
        
    if channel.to_dict()["message"] == '':
        message = f"Goodbye, {member.name}! We will miss you."
    else:
        message = channel.to_dict()["message"]

    leave_channel = member.guild.get_channel(int(leave_channel_id))
    leave_message = discord.Embed(
        title="Goodbye",
        description=message,
        color=discord.Colour.from_rgb(0, 96, 154))
    await leave_channel.send(embed=leave_message)
