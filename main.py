import discord
from discord.ext import commands, tasks
import asyncio
import config
import os

from method import all_task, image_channel, link_channel, welcomeleave, addRole, myCommands, levelmain, api
from prisma import Prisma
from fastapi import FastAPI
import uvicorn
import threading


class DiscordBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=discord.Intents.all())
        self.db = Prisma()

    async def db_connect(self):
        if not self.db.is_connected():
            print("Connecting to database...")
            await self.db.connect()

    async def db_disconnect(self):
        if self.db.is_connected():
            await self.db.disconnect()
            print("Disconnected from database")

    async def on_ready(self):
        print(f'Logged in as {self.user.name} ({self.user.id})')
        

    async def setup_hook(self) -> None:
      await self.load_cogs()
    #   await self.updateMemberCount.start()

    async def load_cogs(self) -> None:
        """
        The code in this function is executed whenever the bot will start.
        """
        for file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/cogs"):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    await self.load_extension(f"cogs.{extension}")
                    print(f"Loaded extension '{extension}'")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    print(
                        f"Failed to load extension {extension}\n{exception}"
                    )

    #-------------make cog---------
    async def on_member_join(self, member):
        await welcomeleave.welcome(member)
        await welcomeleave.join_role(member, self)

    async def on_member_remove(self, member):
        await welcomeleave.Goodbye(member)
    #-------------make cog---------

    async def on_guild_join(self, guild):
        await self.import_server(guild)

    async def on_guild_remove(self, guild):
        await self.db_connect()
        try:
            await self.db.server.delete(where={'server_id': guild.id})
            await self.db.status.delete(where={'server_id': guild.id})
            await self.db.welcome.delete(where={'server_id': guild.id})
            await self.db.goodbye.delete(where={'server_id': guild.id})
            await self.db.levelsetting.delete(where={'server_id': guild.id})
            await self.db.youtubesetting.delete(where={'server_id': guild.id})
            await self.db.reactionverificationrole.delete(where={'server_id': guild.id})
            await self.db.noxpchannel.delete_many(where={'server_id': guild.id})
            await self.db.noxprole.delete_many(where={'server_id': guild.id})
            await self.db.imagesonly.delete_many(where={'server_id': guild.id})
            await self.db.linksonly.delete_many(where={'server_id': guild.id})
            await self.db.youtubesubchannel.delete_many(where={'server_id': guild.id})
            await self.db.youtubevideos.delete_many(where={'server_id': guild.id})
        except Exception as e:
            print(f"Could not found the server in the database: {e}")
        await self.db_disconnect()

    async def on_message(self, message):
        if not message.author.bot:
            print(f"User: {message.author}\nMessage: {message.content}")
        #-------------make cog---------
        await image_channel.del_msg(message, self)
        await link_channel.del_link_msg(message, self)
        await levelmain.level_on_message(message)
        #-------------make cog---------
        await self.process_commands(message)
        
    #-------------make cog---------
    async def on_raw_reaction_add(self, payload):
        await addRole.TO_member(payload)
    #-------------make cog---------

    async def get_prefix(self, message):
        default_prefix = "$"
        await self.db_connect()
        server_doc = await self.db.server.find_unique({"server_id": message.guild.id})
        await self.db_disconnect()
        if server_doc is not None:
            return server_doc.prefix
        else:
            return default_prefix

    async def import_server(self, guild):
        category_name = "Bot-Config"
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),
        }

        category = await guild.create_category(category_name, overwrites=overwrites)
        log = await guild.create_text_channel('Bot-logs', overwrites=overwrites, category=category)
        setup = await guild.create_text_channel('Bot-setup', overwrites=overwrites, category=category)

        await self.db_connect()
        await self.db.server.create(data={"server_id": guild.id, 'server_name': guild.name, 'prefix': '$', 'log_channel': str(log.id)})
        await self.db.welcome.create(data={'server_id': guild.id, "channel_id": 0, "channel_name": '', "message": "", "status": False})
        await self.db.goodbye.create(data={"server_id": guild.id, "channel_id": 0, "channel_name": '', "message": "", "status": False})
        await self.db.levelsetting.create(data={"server_id": guild.id, "status": False, "level_up_channel_id": 0, "level_up_channel_name": ''})
        await self.db.youtubesetting.create(data={"server_id": guild.id, "status": False, "channel_id": 0, "channel_name": ''})
        await self.db.status.create(data={"server_id": guild.id, "IMAGES_ONLY": False, "LINKS_ONLY": False})
        await self.db.reactionverificationrole.create(data={
            "server_id": guild.id,
            "channel_id": 0,
            "channel_name": '',
            "dm_message": False,
            "reaction": '',
            "role_id": 0,
            "role_name": ''
        })
        await self.db_disconnect()


# Create the bot instance
intents = discord.Intents.all()
bot = DiscordBot(command_prefix="$", intents=intents)

# Bot commands
@bot.hybrid_command(name='sync', description='Sync all slash commands')
async def sync(ctx: commands.Context):
    await ctx.send("Syncing...")
    await bot.tree.sync()

@bot.command(name='clear', help='The number of messages to delete.')
async def clear(ctx, amount: int):
    await myCommands.clear(ctx, amount)

@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'This command is on cooldown. Please try again in {round(error.retry_after, 2)} seconds.')

@bot.hybrid_command(name="check", description="Check bot permissions", with_app_command=True)
async def check_bot_permissions(ctx):
    await myCommands.check_bot_permissions(ctx)

@bot.hybrid_command(name="lvl", description="Check your level", with_app_command=True)
async def lvl(ctx):
    await myCommands.level(ctx, ctx.author)

# @bot.command(name="status_setup", help="Add member count to your server")
# async def server_setup(ctx):
#     await myCommands.setup_member_count(ctx)

@bot.group()
async def lvlsys(ctx):
    return

@lvlsys.command(aliases=["e", "en"])
@commands.has_permissions(manage_messages=True)
async def enable(ctx):
    await myCommands.enable_lvl(ctx)

@lvlsys.command(aliases=["d", "dis"])
@commands.has_permissions(manage_messages=True)
async def disable(ctx):
    await myCommands.disable_lvl(ctx)

@lvlsys.command(aliases=["sr", "lvlrole"])
@commands.has_permissions(manage_roles=True)
async def set_role(ctx, level: int, role: discord.Role):
    await myCommands.setrole(ctx, role, level)

@bot.command(name='rank', help='Check your rank')
async def rank(ctx):
    await myCommands.rank(ctx)

@bot.command(name='add_join_role', help='Add role on join')
async def add_join_role(ctx, channel: discord.TextChannel, role: discord.Role):
    await myCommands.add_join_role(ctx, channel, role)

@bot.command(name='setwelcomechannel', help='Set the welcome channel.')
async def set_welcomechannel(ctx, welcome_channel: discord.TextChannel):
    await myCommands.setwelcomechannel(ctx, welcome_channel)

@bot.command(name='setleavechannel', help='Set the leave channel.')
async def set_leavechannel(ctx, leave_channel: discord.TextChannel):
    await myCommands.setleavechannel(ctx, leave_channel)

@bot.hybrid_command(name='setprefix', description='Set the prefix for this server.', with_app_command=True)
async def setprefix(ctx: commands.Context, new_prefix):
    await bot.db_connect()
    server = await bot.db.server.find_unique(where={"server_id": ctx.guild.id})
    await bot.db.server.update(where={"ID": server.ID}, data={"prefix": new_prefix})
    await bot.db_disconnect()
    await ctx.send(f'Prefix set to `{new_prefix}` for this server.')

@bot.command(name="createCAT", help="Create a category")
async def createCAT(ctx, category_name):
    await myCommands.create_category(ctx, bot.db, category_name)

# FastAPI setup and run
def run_fastapi_app():
    import uvicorn
    uvicorn.run(api.myAPI(bot), host="0.0.0.0", port=8000)

def run_discord_bot():
    bot.run(config.TOKEN)

# Create threads for Discord bot and FastAPI app
discord_thread = threading.Thread(target=run_discord_bot)
fastapi_thread = threading.Thread(target=run_fastapi_app)

# Start both threads
discord_thread.start()
fastapi_thread.start()

# Wait for both threads to finish
discord_thread.join()
fastapi_thread.join()
