import discord
from discord.ext import commands
from prisma import Prisma

class WelcomeLeaveCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Prisma()

    async def db_connect(self):
        if not self.db.is_connected():
            print("Connecting to database...")
            await self.db.connect()

    async def db_disconnect(self):
        if self.db.is_connected():
            await self.db.disconnect()
            print("Disconnected from database")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.welcome(member)
        await self.join_role(member)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.goodbye(member)

    async def welcome(self, member:discord.Member):
        await self.db_connect()
        server = await self.db.welcome.find_unique(where={"server_id": member.guild.id})
        ss = await self.db.server.find_unique(where={"server_id": member.guild.id})
        if server is None:
            print(f"Server {member.guild.name} not found in database.")
            await self.db_disconnect()
            em = discord.Embed(
                title="Welcome",
                description=f"Server {member.guild.name} not found in database.",
                color=discord.Colour.red()
            )
            await member.guild.get_channel(int(ss.log_channel)).send(embed=em)
            return
        print("channel:", server.channel_id)

        if not server.status:
            print(f"{member.guild.name} welcome message system is not enabled.")
            await self.db_disconnect()
            em = discord.Embed(
                title="Welcome",
                description=f"{member.guild.name} welcome message system is not enabled.",
                color=discord.Colour.dark_blue()
            )
            await member.guild.get_channel(ss.log_channel).send(embed=em)
            return

        if server.channel_id == 0:
            print(f"Welcome channel not set for {member.guild.name}. Please set welcome channel.")
            await self.db_disconnect()
            em = discord.Embed(
                title="Welcome",
                description=f"Welcome channel not set for {member.guild.name}. Please set welcome channel.",
                color=discord.Colour.dark_blue()
            )
            await member.guild.get_channel(ss.log_channel).send(embed=em)
            return

        welcome_channel_id = server.channel_id
        message = server.message or f"Welcome to the server, {member.mention}! We are glad to have you."
        print("welcome_channel_id:", welcome_channel_id)

        welcome_channel = member.guild.get_channel(int(welcome_channel_id))
        print(welcome_channel)
        welcome_message = discord.Embed(
            title="Welcome to",
            description=message,
            color=discord.Colour.from_rgb(0, 96, 154))
        await welcome_channel.send(embed=welcome_message)
        await self.db_disconnect()

    async def join_role(self, member:discord.Member):
        await self.db_connect()
        join_role = await self.db.joinrole.find_unique(where={"server_id": member.guild.id})
        ss = await self.db.server.find_unique(where={"server_id": member.guild.id})
        if join_role is None:
            print("No data found in database for join role")
            await self.db_disconnect()
            em = discord.Embed(
                title="Join Role",
                description="No data found in database for join role",
                color=discord.Colour.red()
            )
            await member.guild.get_channel(ss.log_channel).send(embed=em)
            return

        role = discord.utils.get(member.guild.roles, id=join_role.role_id)
        if role is None:
            print("Role not found in server")
            await self.db_disconnect()
            em = discord.Embed(
                title="Join Role",
                description="Role not found in server",
                color=discord.Colour.magenta()
            )
            await member.guild.get_channel(ss.log_channel).send(embed=em)
            return

        await self.db_disconnect()
        await member.add_roles(role)

    async def goodbye(self, member:discord.Member):
        await self.db_connect()
        server = await self.db.goodbye.find_unique(where={"server_id": member.guild.id})
        ss = await self.db.server.find_unique(where={"server_id": member.guild.id})
        if server is None:
            print(f"Server {member.guild.name} not found in database.")
            await self.db_disconnect()
            em = discord.Embed(
                title="Database",
                description=f"Server {member.guild.name} not found in database.",
                color=discord.Colour.red()
            )
            await member.guild.get_channel(ss.log_channel).send(embed=em)
            return

        if not server.status:
            print(f"{member.guild.name} Goodbye message system is not enabled.")
            await self.db_disconnect()
            em = discord.Embed(
                title="Goodbye",
                description="Goodbye message system is not enabled.",
                color=discord.Colour.red()
            )
            await member.guild.get_channel(ss.log_channel).send(embed=em)
            return

        if server.channel_id == 0:
            print(f"Goodbye channel not set for {member.guild.name}. Please set Goodbye channel.")
            leave_message = discord.Embed(
                title="Goodbye",
                description=f"Goodbye channel not set for {member.guild.name}. Please set goodbye channel.",
                color=discord.Colour.from_rgb(0, 96, 154))
            await member.guild.get_channel(ss.log_channel).send(embed=leave_message)
            await self.db_disconnect()
            return

        leave_channel_id = server.channel_id
        message = server.message or f"Goodbye, {member.name}! We will miss you."

        leave_channel = member.guild.get_channel(int(leave_channel_id))
        leave_message = discord.Embed(
            title="Goodbye",
            description=message,
            color=discord.Colour.from_rgb(0, 96, 154))
        await self.db_disconnect()
        await leave_channel.send(embed=leave_message)
    
    @commands.hybrid_command(name='add_join_role', description='Add role on join')
    async def add_join_role(self,ctx:commands.Context, channel: discord.TextChannel, role: discord.Role):
        await self.db_connect()
        server = await self.db.joinrole.find_unique(where={"server_id": ctx.guild.id})
        if server == None:
            print(f"Table not found in database for join role:{ctx.guild.id}")
            await ctx.guild.get_channel(channel.id).send(f"Table not found in database for join role:{ctx.guild.id}")
            await self.db_disconnect()
            return
        print("sevrer_data:", server)
        update = await self.db.joinrole.update(where={"ID":server.ID}, data={"status": True, "role_id": f"{role.id}", "role_name": f"{role.name}"})
        print("add_join_role:", update)
        await self.db_disconnect()
        await ctx.send(f'Join role has been set to {role.name}!')

    @commands.hybrid_command(name='setwelcomechannel', description='Set the welcome channel.')
    async def set_welcomechannel(self,ctx:commands.Context, welcome_channel: discord.TextChannel):
        await self.db_connect()
        Guild = ctx.guild
        channel = welcome_channel.id
        ss = await self.db.server.find_unique(where={"server_id": ctx.guild.id})
        if Guild:
            for chann in Guild.channels:
                if chann.id == channel:
                    doc_ref = await self.db.welcome.find_unique(where={"server_id": ctx.guild.id})
                    if doc_ref == None:
                        print(f"Table not found in database for welcome channel:{ctx.guild.id}")
                        await ctx.guild.get_channel(ss.log_channel).send(f"Table not found in database for welcome channel:{ctx.guild.id}")
                        await self.db_disconnect()
                        return
                    update = await self.db.welcome.update(where={"ID":doc_ref.ID}, data={"status": True, "channel_id": f"{chann.id}", "channel_name": f"{chann.name}"})
                    print("setwelcomechannel:", update)
                    await self.db_disconnect()
                    await ctx.send(f'Welcome channel has been set to {chann.name}!')
        else:
            await self.db_disconnect()
            await ctx.send(f"{Guild} is not a valid server id")


    @commands.hybrid_command(name='setleavechannel', description='Set the leave channel.')
    async def set_leavechannel(self,ctx:commands.Context, leave_channel: discord.TextChannel):
        await self.db_connect()
        ss = await self.db.server.find_unique(where={"server_id": ctx.guild.id})
        Guild = ctx.guild
        channel = leave_channel.id
        if Guild:
            for chann in Guild.channels:
                if chann.id == channel:
                    doc_ref = await self.db.goodbye.find_unique(where={"server_id": ctx.guild.id})
                    if doc_ref == None:
                        print("Table not found in database for leave channel")
                        await ctx.guild.get_channel(ss.log_channel).send(f"Table not found in database for leave channel:{ctx.guild.id}")
                        await self.db_disconnect()
                        return
                    update = await self.db.goodbye.update(where={"ID":doc_ref.ID}, data={"status": True, "channel_id": f"{chann.id}", "channel_name": f"{chann.name}"})
                    print("setleavechannel:", update)
                    await self.db_disconnect()
                    await ctx.send(f'Leave channel has been set to {chann.name}!')

async def setup(bot:commands.Bot):
    await bot.add_cog(WelcomeLeaveCog(bot))
