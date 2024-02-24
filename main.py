import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from config import *
from method import image_channel,link_channel,welcomeleave,addRole,myCommands,levelmain,update_member_count
import aiosqlite
import config 
import firebase_admin
from firebase_admin import credentials,firestore

cred = credentials.Certificate("TO_bot.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
bot = commands.Bot(command_prefix='$' ,intents=discord.Intents.all())
# if you want to make your specific bot help command you need to add belove line
# bot = commands.Bot(command_prefix='$', help_command=None ,intents=discord.Intents.all())


# Welcom member
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
    "channel_id":0,
    "channel_name":None  
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
  await addRole.TO_member(payload,rule_channel_id,member_role_id)
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
# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------
@bot.command(name='setwelcomechannel', help='Set the welcome channel.')
async def setwelcomechannel(ctx,welcome_channel:discord.TextChannel):
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
    print('------')
    
    
    await  update_member_count.updateMemberCount(bot, server_id, member_count_channel_id)
  
bot.command_prefix = get_prefix
# Run the bot
bot.run(TOKEN)