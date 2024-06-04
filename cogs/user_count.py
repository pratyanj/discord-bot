import discord
from discord.ext import commands, tasks
from prisma import Prisma
# when member jion raise the count ot total member
# If member remove from the guild then dercrese the number of member
class User_Member_Count(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = Prisma()
        self.Mcolor = discord.Colour.from_rgb(0, 97, 146)
        # self.member_counts.start()

    async def db_connect(self):
        if not self.db.is_connected():
            # print("Connecting to database...")
            await self.db.connect()

    async def db_disconnect(self):
        if self.db.is_connected():
            await self.db.disconnect()
            # print("Disconnected from database")
    
    
    async def update_member_count(self, server_id):
        print(f"Updating member count for server: {server_id}")
        await self.db_connect()
        try:
            guild = self.bot.get_guild(server_id)
            if not guild:
                print('Guild not found.')
                await self.db_disconnect()
                return
            
            server = await self.db.membercount.find_first(where={"server_id": server_id})
            if server is None:
                print(f"Server {guild.name} not found in database.")
                await self.db_disconnect()
                return
            
            member_count_channel = self.bot.get_channel(server.Total_Members)
            bot_count_channel = self.bot.get_channel(server.Bots)
            online_members_channel = self.bot.get_channel(server.Online_Members)
            
            if guild and (member_count_channel and bot_count_channel and online_members_channel):
                member_count = guild.member_count
                bot_count = len([m for m in guild.members if m.bot])
                online_members = len(list(filter(lambda m: m.status == discord.Status.online, guild.members)))
    
                await member_count_channel.edit(name=f'😁Total Members: {member_count}')
                await bot_count_channel.edit(name=f'🤖Bots: {bot_count}')
                await online_members_channel.edit(name=f'😎Online Members: {online_members}')
                print(f'Member count updated successfully for {guild.name}')
            else:
                print('Guild or channel not found.')
        except Exception as e:
            print(f'Error updating member count: {e}')
        finally:
            await self.db_disconnect()

    @tasks.loop(minutes=1)
    async def member_counts(self):
        print("--------- Update Member Count ---------")
        for guild in self.bot.guilds:
            # print(f"Processing guild: {guild.name} ({guild.id})")
            try:
                await self.db_connect()
                member_count = await self.db.membercount.find_first(where={"server_id": guild.id})

                if member_count is None:
                    print(f"{guild.name} not found in database")
                elif member_count.status:
                    # print(f"Updating member count for {guild.name}")
                    await self.update_member_count(guild.id)
            except Exception as e:
                print(f"Error updating member count for {guild.name}: {e}")
            finally:
                await self.db_disconnect()

    @member_counts.before_loop
    async def before_tasks(self):
        # print("Waiting until bot is ready...")
        await self.bot.wait_until_ready()
        # print("Bot is ready. Starting member count task.")

    @commands.hybrid_command(name="setup", description="Add member count to your server")
    async def setup_member_count(self, ctx: commands.Context) -> None:
        await self.db_connect()
        guild = ctx.guild

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),
        }
        category_name = "📊SERVER STATS"
        category = await guild.create_category(category_name, overwrites=overwrites)
        member_count = await guild.create_voice_channel('😁Total Members', overwrites=overwrites, category=category)
        online_member_count = await guild.create_voice_channel('😎Online Members', overwrites=overwrites, category=category)
        bot_count = await guild.create_voice_channel('🤖Bots', overwrites=overwrites, category=category)

        await self.db.membercount.create(data={
            "server_id": ctx.guild.id,
            "Total_Members": member_count.id,
            "Online_Members": online_member_count.id,
            "Bots": bot_count.id,
            "status": True
        })
        await self.db_disconnect()
        em = discord.Embed(description="Your server has been setup with server stats", color=self.Mcolor)
        await ctx.send(embed=em)

    @commands.hybrid_command(name="enable", description="Enable member count updates")
    async def enable_member_count(self, ctx: commands.Context):
        server_id = ctx.guild.id
        await self.db_connect()
        check = await self.db.membercount.find_first(where={"server_id": server_id})
        await self.db_disconnect()
        if check is None:
            emm = discord.Embed(description=f"Server `{ctx.guild.name}` not found in database", color=self.Mcolor)
            await ctx.send(embed = emm)
            
        elif check.status:
            em = discord.Embed(description=f"Member count already enabled for `{ctx.guild.name}`", color=self.Mcolor)
            await ctx.send(embed = em)
            
        else:
            await self.db_connect()
            await self.db.membercount.update(where={"server_id": server_id},data={"status": True})
            await self.db_disconnect()
        em = discord.Embed(description=f"Member count updates enabled for `{ctx.guild.name}`", color=self.Mcolor)
        await ctx.send(embed=em)
    
    @commands.hybrid_command(name="disable", description="Disable member count updates")
    async def disable_member_count(self, ctx: commands.Context):
        server_id = ctx.guild.id
        await self.db_connect()
        check = await self.db.membercount.find_first(where={"server_id": server_id})
        await self.db_disconnect()
        if check is None:
            em  = discord.Embed(description=f"Server `{ctx.guild.name}` not found in database", color=self.Mcolor)
            await ctx.send(embed=em)
            
        elif not check.status:
            em = discord.Embed(description=f"Member count already disabled for `{ctx.guild.name}`", color=self.Mcolor)
            await ctx.send(embed=em)
        else:
            await self.db_connect()  
            await self.db.membercount.update(where={"server_id": server_id},data={"status": False})
            await self.db_disconnect()
            em = discord.Embed(description=f"Member count updates disabled for `{ctx.guild.name}`", color=self.Mcolor)
            await ctx.send(embed=em)

    @commands.hybrid_command(name="status", description="Check the status of member count updates")
    async def status_member_count(self, ctx: commands.Context):
        server_id = ctx.guild.id
        await self.db_connect()
        server = await self.db.membercount.find_first(where={"server_id": server_id})
        await self.db_disconnect()
        if server is None:
            em = discord.Embed(description = f"Server `{ctx.guild.name}` not found in database", color=self.Mcolor)
            await ctx.send(embed=em)
        else:
            status_msg = "enabled" if server.status else "disabled"
            em = discord.Embed(description=f"Member count updates are currently {status_msg} for {ctx.guild.name}", color=self.Mcolor)
            await ctx.send(embed=em)

    @commands.hybrid_command(name="force_update_member_count", description="Force an immediate member count update")
    async def force_update_member_count(self, ctx: commands.Context):
        await self.update_member_count(ctx.guild.id)
        em = discord.Embed(description=f"Member count updated for {ctx.guild.name}", color=self.Mcolor)
        await ctx.send(embed=em)

async def setup(bot: commands.Bot):
    await bot.add_cog(User_Member_Count(bot))
