import discord
from discord.ext import commands
import asyncio
import config
import os

from method import  addRole, api
from prisma import Prisma
from fastapi import FastAPI
import threading


class DiscordBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=discord.Intents.all(),help_command=None)
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
        await bot.tree.sync()
        
        print(f'Logged in as {self.user.name} ({self.user.id})')
        print("------------")
        

    async def setup_hook(self) -> None:
      await self.load_cogs()

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

    async def on_guild_join(self, guild):
        await self.import_server(guild)

    async def on_guild_remove(self, guild: discord.Guild):
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

    async def on_message(self, message: discord.Message):
        if not message.author.bot:
            print(f"User: {message.author}\nMessage: {message.content}")
        await self.process_commands(message)
        
    #-------------make cog---------
    async def on_raw_reaction_add(self, payload):
        await addRole.TO_member(payload)
    #-------------make cog---------

    async def get_prefix(self, message:discord.Message):
        default_prefix = "$"
        await self.db_connect()
        server_doc = await self.db.server.find_unique({"server_id": message.guild.id})
        await self.db_disconnect()
        if server_doc is not None:
            return server_doc.prefix
        else:
            await self.db_connect()
            await self.import_server(discord.Guild())
            await self.db_disconnect()
            return default_prefix

    async def import_server(self, guild:discord.Guild):
        
        category_name = "Bot-Config"
        log_c = "Bot-logs"
        setup_c = "Bot-setup"
        try:
            category = await discord.utils.get(guild.categories, name=category_name)
            log = await discord.utils.get(guild.text_channels, name=log_c)
            setup = await discord.utils.get(guild.text_channels, name=setup_c)
        except:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True),
            }

            category = await guild.create_category(category_name, overwrites=overwrites)
            log = await guild.create_text_channel(log_c, overwrites=overwrites, category=category)
            setup = await guild.create_text_channel(setup_c, overwrites=overwrites, category=category)
        
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

# FastAPI setup and run
def run_fastapi_app():
    import uvicorn
    uvicorn.run(api.myAPI(bot), host="0.0.0.0", port=8001)

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
