import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from config import *
from method import image_channel,link_channel,welcomeleave,addRole,myCommands,levelmain,update_member_count,api
import aiosqlite
import config 

# firebasre (database)
import firebase_admin
from firebase_admin import credentials,firestore

# API

from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI,Depends,Request,HTTPException
from starlette.responses import RedirectResponse
from fastapi.security import APIKeyHeader
import uvicorn
import threading

from fastapi.openapi.utils import get_openapi

cred = credentials.Certificate("TO_bot.json")
firebase_admin.initialize_app(cred)

# initializing 
db = firestore.client()
bot = commands.Bot(command_prefix='$' ,intents=discord.Intents.all())
# if you want to make your specific bot help command you need to add belove line
# bot = commands.Bot(command_prefix='$', help_command=None ,intents=discord.Intents.all())
# ---------------------api------------------------
# app = FastAPI()
# API_KEY = config.API_KEY
# # Create an instance of the APIKeyHeader security scheme
# api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

# # Define a dependency that will check the API key
# async def check_api_key(api_key: str = Depends(api_key_header)):
#     # if not api_key or api_key != f"Bearer {API_KEY}":
#     if not api_key or api_key != API_KEY:
#         raise HTTPException(status_code=401, detail="Enter invalid API key")
    
# # --------------main page as docs----------------------------
# @app.get("/", include_in_schema=False)
# async def redirect_to_docs():
#     response = RedirectResponse(url='/docs')
#     return response
  
# # ------------------------------------------------------------
# # List of server 
# # @app.get("/server_List/",dependencies=[Depends(check_api_key)])

# @app.get("/server_List/")
# async def server_List():
#   servers = {}
#   for guild in bot.guilds:
#     print(guild.id)
#     # servers[guild.name] = guild.id
#     server_info = {
#             "name": str(guild.name),
#             "id": str(guild.id),
#             "icon_url": str(guild.icon)
#         }
#     servers[guild.name] = server_info
#     print(servers)
#   return servers
# # List of channenels according to server id
# # @app.get("/server_Channels_List/{guild}",dependencies=[Depends(check_api_key)])
# @app.get("/server_Channels_List/")
# async def server_Channels_List(guild:int):
#   channelList = {}
#   Guild = bot.get_guild(guild)
#   for channel in Guild.channels:
#     if isinstance(channel, discord.TextChannel):
#       channelList[channel.name] = str(channel.id)
#   return channelList
# # List of roles according to server id
# # @app.get("/server_Roles_List/",dependencies=[Depends(check_api_key)])
# @app.get("/server_Roles_List/")
# async def server_Roles_List(guild:int):
#   Roles_List = {}
#   Guild = bot.get_guild(guild)
#   if Guild:
#     for role in Guild.roles:
#       Roles_List[role.name] = str(role.id)
#     return Roles_List
#   else:
#     return f"{guild} is not a valid server id"


# # @app.post("/welcome_status_GET/",dependencies=[Depends(check_api_key)])
# @app.get("/welcome_status_GET/")
# async def welcome_status_GET(guild:int):
#   Guild = bot.get_guild(guild)
#   if Guild:
#     doc_ref = db.collection("servers").document(str(guild)).collection("Welcome_Leave").document("welcome").get()
#     status = doc_ref.to_dict()['status']
#     return {"status": status}
#   else:
#     return f"{guild} is not a valid server id"
  
  
# # ---------------------------POST METOD---------------------------------

# # server welcome message
# # @app.post("/welcome_status/",dependencies=[Depends(check_api_key)])
# @app.post("/welcome_status/")
# async def welcome_status(guild:int,status:bool):
#   Guild = bot.get_guild(guild)
#   if Guild:
#     doc_ref = db.collection("servers").document(str(guild)).collection("Welcome_Leave").document("welcome")
#     doc_ref.update({'status': status})
#     return {"status": status}
#   else:
#     return f"{guild} is not a valid server id"
  
  
# # @app.post("/welcome_message/",dependencies=[Depends(check_api_key)])
# @app.post("/welcome_message/")
# async def welcome_message(guild:int,message:str):
#   Guild = bot.get_guild(guild)
#   if Guild:
#     doc_ref = db.collection("servers").document(str(guild)).collection("Welcome_Leave").document("welcome")
#     doc_ref.update({'message': message})
#     return {"message": message}
#   else:
#     return f"{guild} is not a valid server id"
  
# # @app.post("/welcome_channel_set/",dependencies=[Depends(check_api_key)])
# @app.post("/welcome_channel_set/")
# async def welcome_channel_set(guild:int,channel:int):
#   Guild = bot.get_guild(guild)
#   if Guild:
#     for chann in Guild.channels:
#       if chann.id == channel:
#         doc_ref = db.collection("servers").document(str(guild)).collection("Welcome_Leave").document("welcome")
#         doc_ref.update({'channel_id': str(chann.id)})
#         doc_ref.update({'channel_name': chann.name})
#     return {"message": f"Welcome channel set to {chann.name} ({chann.id})"}
#   else:
#     return f"{guild} is not a valid server id"
# #join member role
# @app.post("/join_member_role/")
# async def join_member_role(guild:int, channel:int,role:int):
#     print(guild, role)
#     Guild = bot.get_guild(guild)
#     Channel = bot.get_channel(channel)
#     if Guild:
#       for rol in Guild.roles:
#           print("Role_id:",rol.id)
#           if rol.id == role:
#               server = db.collection("servers").document(str(Guild.id)).collection("moderation").document("Join_Member_Role") 
#               sevrer_data = server.get()
#               print("sevrer_data:",sevrer_data.to_dict())
#               data = {"status":True,"channel_id":f'{Channel.id}','channel_name':f'{Channel.name}','role_id':f"{rol.id}",'role_name':f"{rol.name}"}
#               print('DATA:',data)
#               server.set(data)
#               return data
#       else:
#         return f"{role} is not a valid role"
        
#     else:
#       return f"{guild} is not a valid server id"
    
# # @app.post("/link_channel_switch/",dependencies=[Depends(check_api_key)])
# @app.post("/link_channel_status/")
# async def link_channel_switch(guild:int,status:bool):
#   Guild = bot.get_guild(guild)
#   if Guild:
#     doc_ref = db.collection("servers").document(str(guild)).collection("moderation").document("Link_Only")
#     doc_ref.update({'status': status})
#     return {"status": status}
#   else:
#     return f"{guild} is not a valid server id"
      
# # @app.post("/IMG_channel_switch/",dependencies=[Depends(check_api_key)])
# @app.post("/IMG_channel_status/")
# async def IMG_channel_switch(guild:int,status:bool):
#   Guild = bot.get_guild(guild)
#   if Guild:
#     doc_ref = db.collection("servers").document(str(guild)).collection("moderation").document("IMG_Only")
#     doc_ref.update({'status': status})
#     return {"status": status}
#   else:
#     return f"{guild} is not a valid server id"
# --------------------------------------------------------------------------------



# --------------------------------------------------------------------------------
# ---------------------------DISCORD BOT SETTINGS---------------------------------
# --------------------------------------------------------------------------------

@bot.event
async def on_member_join(member:discord.member):
    await welcomeleave.welcome(member, db)
# If member leave server
@bot.event 
async def on_member_remove(member:discord.member):
    await welcomeleave.Goodbye(member, db)

# Set the default prefix for a new server
@bot.event
async def on_guild_join(guild):
  data = {
    "name":guild.name,
    "prefix":"$"
  }
  db.collection("servers").document(int(guild.id)).set(data)
  welcome = {
    "status":False,
    "channel_id":'',
    "channel_name":None,
    "message":"" 
  }
  db.collection("servers").document(guild.id).collection("Welcome_Leave").document("welcome").set(welcome)
  db.collection("servers").document(guild.id).collection("Welcome_Leave").document("leave").set(welcome)
  lvlsys = {
      "lvlsys": True,
      "role_id": {},
      "role_set":{}
  }
  db.collection("servers").document(guild.id).collection("Levels").document("levelsetting").set(lvlsys)
  db.collection("servers").document(guild.id).collection("Levels").document("user_lvl")
  db.collection("servers").document(guild.id).collection("moderation").document("IMG_Only").set({"status":False,"role_id":[]})
  db.collection("servers").document(guild.id).collection("moderation").document("Link_Only").set({"status":False,"role_id":[]})
  db.collection("servers").document(guild.id).collection("moderation").document("Memeber_Count").set({"status":False,"role_id":0})
  db.collection("servers").document(guild.id).collection("moderation").document("Join_Member_Role").set({"status":False,"channel_id":'','channel_name':"",'role_id':"",'role_name':""})
   
@bot.event
async def on_message(message):
    if not message.author.bot:
      print("--------------------------------------------------------")
      print("User:",message.author)
      print("Message:\n",message.content)
      print("--------------------------------------------------------")
    await image_channel.del_msg(message, monitored_channel_ids, bot)
    await link_channel.del_link_msg(message,link_channel_list,bot)
    await levelmain.level_on_message(message,db)
    
@bot.event
async def on_raw_reaction_add(payload):
  await addRole.TO_member(payload,db)
# ------------------------------------------------------------------------------------
#                              My all command
# ------------------------------------------------------------------------------------
@bot.command(name='clear',help='The number of messages to delete.')
async def clear(ctx, amount: int):
  await myCommands.clear(ctx, amount)
# Add cooldown to the clear command (optional)
@clear.error
async def clear_error(self, ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'This command is on cooldown. Please try again in {round(error.retry_after, 2)} seconds.')
        
@bot.command(name="Check permissions",help="Check bot permissions")
async def check_bot_permissions(ctx):
  await myCommands.check_bot_permissions(ctx)
@bot.command(name="lvl", help="Check your level")
async def lvl(ctx):
    print(ctx.author)
    await myCommands.level(ctx,ctx.author,db)
@bot.command(name='code', help='Send a code block')
async def send_code(ctx):
    await myCommands.code(ctx)
# ----------lvl system----------
@bot.group()
async def lvlsys(ctx):
    return
@lvlsys.command(aliases=["e","en"])
@commands.has_permissions(manage_messages=True)
async def enable(ctx):
  await myCommands.enable_lvl(ctx,db)
@lvlsys.command(aliases=["d","dis"])
@commands.has_permissions(manage_messages=True)
async def disable(ctx):
  await myCommands.disable_lvl(ctx,db)

@lvlsys.command(aliases=["sr","lvlrole"])
@commands.has_permissions(manage_roles=True)
async def set_role(ctx, level:int, role: discord.Role):
  await myCommands.setrole(ctx,db,role,level)
  
@bot.command(name='rank', help='Check your rank')
async def rank(ctx):
  await myCommands.rank(ctx,db,firestore)
  
@bot.command(name='add_join_role', help='Add role on join')
async def add_join_role(ctx,channel:discord.channel,role:discord.role):
  await myCommands.add_join_role(ctx,db,channel,role)
  
# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------
@bot.command(name='setwelcomechannel', help='Set the welcome channel.')
async def setwelcomechannel(ctx,welcome_channel:discord.TextChannel):
  db.collection("servers").document(ctx.guild.id).collection("Welcome_Leave").document("welcome")
  
  channel_set = db.collection("channel_id").document("welcome_channel_id")
  channel_get = channel_set.get()
  welcome_channel_id = next(iter(channel_get.to_dict().values()), None)
  channel_set.set({welcome_channel.name:welcome_channel.id})
  print('welcome_channel_id:',welcome_channel_id)
  print('welcome_channel_name:',welcome_channel_id)
  await ctx.send(f'Welcome channel set to {welcome_channel.name}')
  
@bot.command(name='setleavechannel', help='Set the leave channel.')
async def setleavechannel(ctx,leave_channel:discord.TextChannel):
  channel_set = db.collection("channel_id").document("leave_channel_id")
  channel_get = channel_set.get()
  welcome_channel_id = channel_get.to_dict()
  print('leave_channel_id:',welcome_channel_id)
  channel_set.set({leave_channel.name:leave_channel.id})
  await ctx.send(f'Welcome channel set to {leave_channel.name}')
  
# Set the custom prefix for the server
@bot.command(name='setprefix', help='Set the prefix for this server.')
async def setprefix(ctx, new_prefix):
    prefix = db.collection("servers").document(int(ctx.guild.id))
    prefix.update({"prefix": new_prefix})
    await ctx.send(f'Prefix set to `{new_prefix}` for this server.')
    
@bot.command(name="createCAT",help="Create a category")
async def createCAT(ctx, category_name):
  await myCommands.create_category(ctx,db,category_name)
    
# ------------------------------------------------------------------------------------

# Define a function to get the prefix from Firestore
async def get_prefix(bot, message):
    # Default prefix in case the server prefix is not found
    default_prefix = "$"

    # Retrieve the prefix from Firestore based on the server ID
    server_doc = db.collection("servers").document(str(message.guild.id))
    doc = server_doc.get()
    
    # Check if the document exists and contains a prefix
    if doc.exists and "prefix" in doc.to_dict():
      return doc.to_dict()["prefix"]
    else:
      return default_prefix
    
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('--------------------------------------------------------')
    # for guild in bot.guilds:
    #   print(guild.name)
    #   print(guild.id)
    #   print(guild.icon)
    #   print('------')
    await  update_member_count.updateMemberCount(bot, server_id, member_count_channel_id)
  
bot.command_prefix = get_prefix
# Run the bot
# Run the bot and FastAPI concurrently using uvicorn
def run_discord_bot():
    bot.run(config.TOKEN)

def run_fastapi_app():
    import uvicorn
    uvicorn.run(api.myAPI(bot,db), host="192.168.0.8", port=8000)

# Create threads for Discord bot and FastAPI app
discord_thread = threading.Thread(target=run_discord_bot)
fastapi_thread = threading.Thread(target=run_fastapi_app)

# Start both threads
discord_thread.start()
fastapi_thread.start() 

# Wait for both threads to finish
discord_thread.join()
fastapi_thread.join()