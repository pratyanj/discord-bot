import stat
from turtle import update
import discord
from discord import app_commands
from discord.ext import commands,tasks
import asyncio
from config import *
from method import all_task, image_channel,link_channel,welcomeleave,addRole,myCommands,levelmain,api
import aiosqlite
import config 

# firebasre (database)
import sqlite3
from prisma import Prisma
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


# cred = credentials.Certificate("TO_bot.json")
# firebase_admin.initialize_app(cred)
# # initializing 
# # db = firestore.client()


db = Prisma()
bot = commands.Bot(command_prefix='$' ,intents=discord.Intents.all())
# if you want to make your specific bot help command you need to add belove line
# bot = commands.Bot(command_prefix='$', help_command=None ,intents=discord.Intents.all())

# --------------------------------------------------------------------------------
# ---------------------------DISCORD BOT SETTINGS---------------------------------
# --------------------------------------------------------------------------------

# ----------------------Bot Join /Leave Events Completed----------------------
@bot.event
async def on_member_join(member:discord.member):
    await welcomeleave.welcome(member)
    await welcomeleave.join_role(member,bot)
# If member leave server
@bot.event 
async def on_member_remove(member:discord.member):
    await welcomeleave.Goodbye(member)

# Set the default prefix for a new server
@bot.event
async def on_guild_join(guild):
  category_name = "Bot-Config"
  role = await guild.create_role(name="TO-BOT", mentionable=True)
  overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
        role: discord.PermissionOverwrite(read_messages=True)
    }
    
  # Create the category
  category =await guild.create_category(category_name ,overwrites=overwrites)

  # Create the role with the same name as the category
  # Assign the role to the member who executed the command
  await guild.create_role(role)
  # Create help channels within the newly created category
  log = await guild.create_text_channel(f'Bot-logs', overwrites=overwrites ,category =category)
  setup = await guild.create_text_channel(f'Bot-setup', overwrites=overwrites,category=category)

  # ---------------prisma database-------------
  await db.connect()
  
  server = await db.server.create(data={"server_id":guild.id,'server_name':guild.name, 'prefix':'$','log_channel':f"{log.id}"})
  print(f'created post: {server.json(indent=2, sort_keys=True)}')
  
  welcome = await db.welcome.create(data={'server_id':guild.id, "channel_id":None, "channel_name":None, "message":"","status":False,})
  print(f'created post: {welcome.json(indent=2, sort_keys=True)}')
  
  leave = await db.goodbye.create(data={"server_id":guild.id, "channel_id":None, "channel_name":None, "message":"","status":False})
  print(f'created post: {leave.json(indent=2, sort_keys=True)}')
  
  await db.levelsetting.create(data = {"server_id":guild.id,"status":False,"level_up_channel_id":None, "level_up_channel_name":None})
  await db.youtubesetting.create(data = {"server_id":guild.id,"status":False,"channel_id":None, "channel_name":None})
  await db.reactionverificationrole.create(data={
    "server_id":guild.id,
    "channel_id":None,
    "channel_name":None,
    "dm_message":False,
    "reaction":None,
    "role_id":None,
    "role_name":None
  })
  # ---------------database-------------
  await db.disconnect()
  
  # # ---------LEVEL------

@bot.event
async def on_guild_remove(guild):
  await db.connect()
  try:
    await db.status.delete(where={'server_id':guild.id})
    await db.welcome.delete(where={'server_id':guild.id})
    await db.goodbye.delete(where={'server_id':guild.id})
    await db.levelsetting.delete(where={'server_id':guild.id})
    await db.youtubesetting.delete(where={'server_id':guild.id})
    await db.reactionverificationrole.delete(where={'server_id':guild.id})
    # list of channels type table
    await db.noxpchannel.delete_many(where={'server_id':guild.id})
    await db.noxprole.delete_many(where={'server_id':guild.id})
    await db.imagesonly.delete_many(where={'server_id':guild.id})
    await db.linksonly.delete_many(where={'server_id':guild.id})
    await db.youtubesubchannel.delete_many(where={'server_id':guild.id})
    await db.youtubevideos.delete_many(where={'server_id':guild.id})
  except:
    print("Could not found the server in the database")
  
  await db.disconnect()
# ----------------------Bot Join /Leave Events Completed----------------------
@bot.event
async def on_message(message):
    if not message.author.bot:
      print("--------------------------------------------------------")
      print("User:",message.author)
      print("Message:\n",message.content)
      print("--------------------------------------------------------")
    await image_channel.del_msg(message, bot)
    await link_channel.del_link_msg(message,bot)
    await levelmain.level_on_message(message)
    
@bot.event
async def on_raw_reaction_add(payload):
  await addRole.TO_member(payload)
# ------------------------------------------------------------------------------------
#                              My all command
# ------------------------------------------------------------------------------------
# @bot.tree.command(name='clear',description='The number of messages to delete.')
@bot.command(name='clear',help='The number of messages to delete.')
async def clear(ctx, amount: int):
  await myCommands.clear(ctx, amount)
# Add cooldown to the clear command (optional)
@clear.error
async def clear_error(self, ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'This command is on cooldown. Please try again in {round(error.retry_after, 2)} seconds.')
        
@bot.command(name="Check",help="Check bot permissions")
async def check_bot_permissions(ctx):
  await myCommands.check_bot_permissions(ctx)
  
@bot.command(name="lvl", help="Check your level")
async def lvl(ctx):
    print(ctx.author)
    await myCommands.level(ctx,ctx.author)


@bot.command(name="status_setup",help="Add memeber to your server")
async def server_setup(ctx):
  await myCommands.setup_member_count(ctx)
# ----------lvl system----------
@bot.group()
async def lvlsys(ctx):
    return
@lvlsys.command(aliases=["e","en"])
@commands.has_permissions(manage_messages=True)
async def enable(ctx):
  await myCommands.enable_lvl(ctx)
@lvlsys.command(aliases=["d","dis"])
@commands.has_permissions(manage_messages=True)
async def disable(ctx):
  await myCommands.disable_lvl(ctx)

@lvlsys.command(aliases=["sr","lvlrole"])
@commands.has_permissions(manage_roles=True)
async def set_role(ctx, level:int, role: discord.Role):
  await myCommands.setrole(ctx,role,level)
  
@bot.command(name='rank', help='Check your rank')
async def rank(ctx):
  await myCommands.rank(ctx)
  
@bot.command(name='add_join_role', help='Add role on join')
async def add_join_role(ctx,channel:discord.channel,role:discord.role):
  await myCommands.add_join_role(ctx,channel,role)
  
# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------
@bot.command(name='setwelcomechannel', help='Set the welcome channel.')
async def set_welcomechannel(ctx,welcome_channel:discord.TextChannel):
  await myCommands.setwelcomechannel(ctx,welcome_channel)
  
@bot.command(name='setleavechannel', help='Set the leave channel.')
async def set_leavechannel(ctx,leave_channel:discord.TextChannel):
  await myCommands.setleavechannel(ctx,leave_channel)
  
# Set the custom prefix for the server
@bot.command(name='setprefix', help='Set the prefix for this server.')
async def setprefix(ctx, new_prefix):
  await db.connect()
  await db.server.update(where={"server_id": 1075308453024772156},data={"prefix": new_prefix})
  await db.disconnect()
  print(f"New prefix set to:{new_prefix}")
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
    await db.connect()
    server_doc =await db.server.find_unique({"server_id": message.guild.id})
    if server_doc is not None:
      prefix = server_doc.prefix
      await db.disconnect()
      return prefix
    else:
      return default_prefix
# ------------------------------Bot all task------------------------------------------------------

@tasks.loop(minutes=10)
async def updateMemberCount():
  await db.connect()
  for guild in bot.guilds:
    memberCount = await db.membercount.find_unique(where={"server_id": guild.id})
    if memberCount is not None:
      if memberCount.status == True:
        await all_task.updateMemberCount(bot, guild.id)
  await db.disconnect()

@tasks.loop(minutes=10)
async def youtube():
  await db.connect()
  for guild in bot.guilds:
      youtube_notification = await db.youtubesetting.find_unique(where={"server_id": guild.id})
      if youtube_notification is not None:
        if youtube_notification.status == True:
          await all_task.youtube(bot,guild.id)
  await db.disconnect()
# ------------------------------------------------------------------------------------ 
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('--------------------------------------------------------')
    
    # updateMemberCount.start()
    youtube.start()
  
bot.command_prefix = get_prefix
# Run the bot
# Run the bot and FastAPI concurrently using uvicorn
def run_discord_bot():
    bot.run(config.TOKEN)

def run_fastapi_app():
    import uvicorn
    uvicorn.run(api.myAPI(bot), host="0.0.0.0", port=8000)
    # uvicorn.run(api.myAPI(bot,db), host="192.168.0.23", port=8000)

# Create threads for Discord bot and FastAPI app
discord_thread = threading.Thread(target=run_discord_bot)
fastapi_thread = threading.Thread(target=run_fastapi_app)

# Start both threads
discord_thread.start()
fastapi_thread.start() 

# Wait for both threads to finish
discord_thread.join()
fastapi_thread.join()