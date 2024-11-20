from prisma import Prisma
import discord
import asyncio
db = Prisma()

async def db_connect(self):
    try:
        if not self.db.is_connected():
            await self.db.connect()
            print("Database connected successfully")
    except Exception as e:
        print(f"Database connection error: {e}")
        # Implement retry logic
        for attempt in range(3):
            try:
                await asyncio.sleep(1)  # Wait before retry
                await self.db.connect()
                print(f"Database reconnected after attempt {attempt + 1}")
                break
            except Exception:
                continue
async def db_connect1():
    try:
        if not db.is_connected():
            await db.connect()
            print("Database connected successfully")
    except Exception as e:
        print(f"Database connection error: {e}")
        # Implement retry logic
        for attempt in range(3):
            try:
                await asyncio.sleep(1)  # Wait before retry
                await db.connect()
                print(f"Database reconnected after attempt {attempt + 1}")
                break
            except Exception:
                continue
async def db_disconnect():
    '''Disconnect from the database.'''
    if db.is_connected():
        print("Disconnected from database")
        await db .disconnect()
async def on_message(self, message: discord.Message):
    if not message.author.bot:
        try:
            await self.db_connect()  # Ensure connection before database operations
            print(f"User: {message.author}\nMessage: {message.content}")
            await self.process_commands(message)
        finally:
            await db_disconnect()
