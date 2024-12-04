'''

The `DiscordBot` class is the main entry point for the Discord bot application. It inherits from the `commands.Bot` class from the `discord.py` library and provides the following functionality:

- Initializes the bot with the specified command prefix and intents.
- Connects the bot to the Prisma database.
- Handles the `on_ready` event, which is triggered when the bot is logged in and ready to receive commands.
- Loads all the bot's cogs (extensions) during the `setup_hook` method.
- Handles the `on_guild_join` and `on_guild_remove` events, which are triggered when the bot joins or leaves a Discord server, respectively. These events are used to manage the server's data in the Prisma database.
- Handles the `on_message` event, which is triggered when a message is received. This event is used to log the message content and process any commands.
- Provides a `get_prefix` method to retrieve the server-specific prefix for the bot.
- Provides an `import_server` method to create the necessary channels and database entries when the bot joins a new server.
'''
# run if it is deploying first time
import subprocess
command = ["prisma", "db", "push"]
try:
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    print("prisma done:", result.stdout)
except subprocess.CalledProcessError as e:
    print("Failed to prisma:", e.stderr)
import discord
from discord.ext import commands
import asyncio
import api
import os

from prisma import Prisma
from fastapi import FastAPI
import threading
from database.connection import db_connect, db_disconnect


class DiscordBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=discord.Intents.all(),help_command=None)
        self.db = Prisma()

    
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
        print(f"Left {guild.name} ({guild.id})")
        await db_connect(self)
        try:
            # await self.db.server.delete(where={'server_id': guild.id})
            # await self.db.status.delete(where={'server_id': guild.id})
            # await self.db.welcome.delete(where={'server_id': guild.id})
            # await self.db.goodbye.delete(where={'server_id': guild.id})
            # await self.db.levelsetting.delete(where={'server_id': guild.id})
            # await self.db.youtubesetting.delete(where={'server_id': guild.id})
            # await self.db.reactionverificationrole.delete(where={'server_id': guild.id})
            # await self.db.noxpchannel.delete_many(where={'server_id': guild.id})
            # await self.db.noxprole.delete_many(where={'server_id': guild.id})
            # await self.db.imagesonly.delete_many(where={'server_id': guild.id})
            # await self.db.linksonly.delete_many(where={'server_id': guild.id})
            # await self.db.youtubesubchannel.delete_many(where={'server_id': guild.id})
            # await self.db.youtubevideos.delete_many(where={'server_id': guild.id})
            # Test this code later
            models = [
                        'server', 'status', 'welcome', 'goodbye', 'levelsetting',
                        'youtubesetting', 'reactionverificationrole'
                    ]
            for model in models:
                await getattr(self.db, model).delete(where={'server_id': guild.id})

            many_models = [
                'noxpchannel', 'noxprole', 'imagesonly', 'linksonly',
                'youtubesubchannel', 'youtubevideos'
            ]
            for model in many_models:
                await getattr(self.db, model).delete_many(where={'server_id': guild.id})
                print(getattr(self.db, model))
        except Exception as e:
            print(f"Could not found the server in the database: {e}")
        finally:
            await db_disconnect()

    async def on_message(self, message: discord.Message):
        if not message.author.bot:
            print(f"User: {message.author}\nMessage: {message.content}")
        await self.process_commands(message)
        

    async def get_prefix(self, message:discord.Message):
        default_prefix = "$"
        await db_connect(self)
        server_doc = await self.db.server.find_unique({"server_id": message.guild.id})
        await db_disconnect()
        if server_doc is not None:
            return server_doc.prefix
        else:
            await db_connect(self)
            await self.import_server(discord.Guild())
            await db_disconnect()
            return default_prefix

    async def on_guild_join(self, guild:discord.Guild):
        print(f"Joined a new server: {guild.name} ({guild.id})")
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
        
        await db_connect(self)
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
            "role_id": 0,
            "role_name": ''
        })
        await db_disconnect()


# Create the bot instance
intents = discord.Intents.all()
bot = DiscordBot(command_prefix="$", intents=intents)

# FastAPI setup and run
def run_fastapi_app():
    import uvicorn
    app = api.myAPI(bot)
    uvicorn.run(app, host="0.0.0.0")

def run_discord_bot():
    bot.run(os.getenv("DISCORD_TOKEN"))
    
# if __name__ == "__main__":
#     run_fastapi_app()

if __name__ == "__main__":
    # Create threads for Discord bot and FastAPI app
    discord_thread = threading.Thread(target=run_discord_bot)
    fastapi_thread = threading.Thread(target=run_fastapi_app)

    # Start both threads
    discord_thread.start()
    fastapi_thread.start()

    # Wait for both threads to finish
    discord_thread.join()
    fastapi_thread.join()