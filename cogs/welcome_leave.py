import discord
from discord import ui
from discord.ui import Button, View
from discord.ext import commands
from h11 import Data
from prisma import Prisma

class WelcomeLeaveCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = Prisma()
        self.Mcolor = discord.Colour.from_rgb(0, 97, 146)
        option = [
            discord.SelectOption(label='Welcome', )
        ]

    from database.connection import db_connect, db_disconnect

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.welcome(member)
        await self.join_role(member)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.goodbye(member)
    
    @commands.Cog.listener()
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
                color=self.Mcolor
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
                color=self.Mcolor
            )
            await member.guild.get_channel(int(ss.log_channel)).send(embed=em)
            return

        if server.channel_id == 0:
            print(f"Welcome channel not set for {member.guild.name}. Please set welcome channel.")
            await self.db_disconnect()
            em = discord.Embed(
                title="Welcome",
                description=f"Welcome channel not set for {member.guild.name}. Please set welcome channel.",
                color=self.Mcolor
            )
            await member.guild.get_channel(ss.log_channel).send(embed=em)
            return

        welcome_channel_id = server.channel_id
        message =  server.message if server.message == "" else f"Welcome to the server, {member.mention}! We are glad to have you."
        print("welcome_channel_id:", welcome_channel_id)

        welcome_channel = member.guild.get_channel(int(welcome_channel_id))
        print(welcome_channel)
        welcome_message = discord.Embed(
            title="Welcome",
            description=message,
            color=self.Mcolor)
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
                color=discord.Colour.red()
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
                color=self.Mcolor
            )
            await member.guild.get_channel(ss.log_channel).send(embed=em)
            return

        if not server.status:
            print(f"{member.guild.name} Goodbye message system is not enabled.")
            await self.db_disconnect()
            em = discord.Embed(
                title="Goodbye",
                description="Goodbye message system is not enabled.",
                color=self.Mcolor
            )
            await member.guild.get_channel(ss.log_channel).send(embed=em)
            return

        if server.channel_id == 0:
            print(f"Goodbye channel not set for {member.guild.name}. Please set Goodbye channel.")
            leave_message = discord.Embed(
                title="Goodbye",
                description=f"Goodbye channel not set for {member.guild.name}. Please set goodbye channel.",
                color=self.Mcolor)
            await member.guild.get_channel(ss.log_channel).send(embed=leave_message)
            await self.db_disconnect()
            return

        leave_channel_id = server.channel_id
        message = server.message if server.message ==  "" else f"Goodbye, {member.name}! We will miss you."

        leave_channel = member.guild.get_channel(int(leave_channel_id))
        leave_message = discord.Embed(
            title="Goodbye",
            description=message,
            color=self.Mcolor)
        await self.db_disconnect()
        await leave_channel.send(embed=leave_message)
    
    @commands.hybrid_command(name='add_join_role', description='Add role on join')
    @commands.has_permissions(administrator=True)
    async def add_join_role(self,ctx:commands.Context, role: discord.Role):
        await self.db_connect()
        ss = await self.db.server.find_unique(where={"server_id": ctx.guild.id})
        server = await self.db.joinrole.find_unique(where={"server_id": ctx.guild.id})
        if server == None:
            embed = discord.Embed(description=f"Table not found in database for join role:`{ctx.guild.id}`")
            embed.color = self.Mcolor
            embed.title = "Database"
            
            await ctx.guild.get_channel(ss.log_channel).send(embed=embed)
            await self.db_disconnect()
            return
        print("sevrer_data:", server)
        update = await self.db.joinrole.update(where={"ID":server.ID}, data={"status": True, "role_id": f"{role.id}", "role_name": f"{role.name}"})
        print("add_join_role:", update)
        await self.db_disconnect()
        message = discord.Embed(
            description=f"Join role has been set to:`{role.name}`",
            color=self.Mcolor)
        await ctx.send(embed=message)

    @commands.hybrid_command(name='setwelcomechannel', description='Set the welcome channel.')
    @commands.has_permissions(administrator=True)
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
                        em = discord.Embed(title="Database", description=f"Table not found in database for welcome channel:`{ctx.guild.id}`", color=self.Mcolor)
                        await ctx.guild.get_channel(ss.log_channel).send(embed=em)
                        await self.db_disconnect()
                        return
                    update = await self.db.welcome.update(where={"ID":doc_ref.ID}, data={"status": True, "channel_id": f"{chann.id}", "channel_name": f"{chann.name}"})
                    print("setwelcomechannel:", update)
                    await self.db_disconnect()
                    embed = discord.Embed( description=f"The welcome channel has been set to `{chann.name}`!", color=self.Mcolor)
                    await ctx.send(embed=embed)
        else:
            await self.db_disconnect()
            em = discord.Embed(
                title="Database",
                description=f"{Guild} is not a valid server id",
                color=self.Mcolor
            )
            await ctx.send(embed=em)

    @commands.hybrid_command(name='setleavechannel', description='Set the leave channel.')
    @commands.has_permissions(administrator=True)
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
                        em = discord.Embed(
                            title="Database", 
                            description=f"Table not found in database for leave channel:`{ctx.guild.id}`", 
                            color=self.Mcolor)
                        await ctx.guild.get_channel(ss.log_channel).send(embed=em)
                        await self.db_disconnect()
                        return
                    update = await self.db.goodbye.update(where={"ID":doc_ref.ID}, data={"status": True, "channel_id": f"{chann.id}", "channel_name": f"{chann.name}"})
                    print("setleavechannel:", update)
                    await self.db_disconnect()
                    em = discord.Embed(description=f"The leave channel has been set to `{chann.name}`!", color=self.Mcolor)
                    await ctx.send(embed=em)

    # -------------Enable------------
    @commands.hybrid_command(name='welcome_enable', description='Enable welcome System.')
    @commands.has_permissions(administrator=True)
    async def welcome_enable(self,ctx:commands.Context):
        await self.db_connect()
        ss = await self.db.server.find_unique(where={"server_id": ctx.guild.id})
        doc_ref = await self.db.welcome.find_unique(where={"server_id": ctx.guild.id})
        if doc_ref == None:
            print("Table not found in database for welcome channel")
            em = discord.Embed(description=f"Welcome table not found in database for Server:`{ctx.guild.id}`", color=self.Mcolor)
            await self.db_disconnect()
            await ctx.guild.get_channel(ss.log_channel).send(embed=em)
        if doc_ref.status == True:
            print("Welcome System is already enabled")
            em = discord.Embed(description=f"Welcome System is already `enabled`", color=self.Mcolor)
            await self.db_disconnect()
            await ctx.send(embed=em)
        else:
            update = await self.db.welcome.update(where={"ID":doc_ref.ID}, data={"status": True})
            print("welcome_enable:", update)
            await self.db_disconnect()
            em = discord.Embed(description=f"Welcome System has been enabled",color=self.Mcolor)
            await ctx.send(embed=em)
            
    @commands.hybrid_command(name='leave_enable', description='Enable leave System.')
    @commands.has_permissions(administrator=True)
    async def leave_enable(self,ctx:commands.Context):
        await self.db_connect()
        ss = await self.db.server.find_unique(where={"server_id": ctx.guild.id})
        doc_ref = await self.db.goodbye.find_unique(where={"server_id": ctx.guild.id})
        if doc_ref == None:
            print("Table not found in database for leave channel")
            em = discord.Embed(description=f"Leave table not found in database for Server:`{ctx.guild.id}`", color=self.Mcolor)
            await self.db_disconnect()
            await ctx.guild.get_channel(ss.log_channel).send(embed=em)
        if doc_ref.status == True:
            print("Leave System is already enabled")
            em = discord.Embed(description=f"Leave System is already `enabled`", color=self.Mcolor)
            await self.db_disconnect()
            await ctx.send(embed=em)
        else:
            update = await self.db.goodbye.update(where={"ID":doc_ref.ID}, data={"status": True})
            print("leave_enable:", update)
            await self.db_disconnect()
            await ctx.send(embed=em)
            
    @commands.hybrid_command(name='join_role_enable', description='Enable join role System.')
    @commands.has_permissions(administrator=True)
    async def join_role_enable(self,ctx:commands.Context):
        await self.db_connect()
        ss = await self.db.server.find_unique(where={"server_id": ctx.guild.id})
        doc_ref = await self.db.joinrole.find_unique(where={"server_id": ctx.guild.id})
        if doc_ref == None:
            print("Table not found in database for join role")
            em = discord.Embed(description=f"Join role table not found in database for Server:`{ctx.guild.id}`", color=self.Mcolor)
            await self.db_disconnect()
            await ctx.guild.get_channel(ss.log_channel).send(embed=em)
        if doc_ref.status == True:
            print("Join role System is already enabled")
            em = discord.Embed(description=f"Join role System is already `enabled`", color=self.Mcolor)
            await self.db_disconnect()
            await ctx.send(embed=em)
        else:
            update = await self.db.joinrole.update(where={"ID":doc_ref.ID}, data={"status": True})
            print("join_role_enable:", update)
            await self.db_disconnect()
            em = discord.Embed(description=f"Join role System has been enabled",color=self.Mcolor)
            await ctx.send(embed=em)
    
    # ------------Disable------------
    @commands.hybrid_command(name='welcome_disable', description='Disable welcome System.')
    @commands.has_permissions(administrator=True)
    async def welcome_disable(self,ctx:commands.Context):
        await self.db_connect()
        ss = await self.db.server.find_unique(where={"server_id": ctx.guild.id})
        doc_ref = await self.db.welcome.find_unique(where={"server_id": ctx.guild.id})
        if doc_ref == None:
            print("Table not found in database for welcome channel")
            em = discord.Embed(description=f"Welcome table not found in database for Server:`{ctx.guild.id}`", color=self.Mcolor)
            await self.db_disconnect()
            await ctx.guild.get_channel(ss.log_channel).send(embed=em)
        if doc_ref.status == False:
            print("Welcome System is already disabled")
            em = discord.Embed(description=f"Welcome System is already `disabled`", color=self.Mcolor)
            await self.db_disconnect()
            await ctx.send(embed=em)
        else:
            update = await self.db.welcome.update(where={"ID":doc_ref.ID}, data={"status": False})
            print("welcome_disable:", update)
            await self.db_disconnect()
            em = discord.Embed(description=f"Welcome System has been `disabled`",color=self.Mcolor)
            await ctx.send(embed=em)
            
    @commands.hybrid_command(name='leave_disable', description='Disable leave System.')
    @commands.has_permissions(administrator=True)
    async def leave_disable(self,ctx:commands.Context):
        self.db_connect()
        ss = await self.db.server.find_unique(where={"server_id": ctx.guild.id})
        doc_ref = await self.db.goodbye.find_unique(where={"server_id": ctx.guild.id})
        if doc_ref == None:
            print("Table not found in database for leave channel")
            em = discord.Embed(description=f"Leave table not found in database for Server:`{ctx.guild.id}`", color=self.Mcolor)
            await self.db_disconnect()
            await ctx.guild.get_channel(ss.log_channel).send(embed=em)
        if doc_ref.status == False:
            print("Leave System is already disabled")
            em = discord.Embed(description=f"Leave System is already `disabled`", color=self.Mcolor)
            await self.db_disconnect()
            await ctx.send(embed=em)
        else:
            update = await self.db.goodbye.update(where={"ID":doc_ref.ID}, data={"status": False})
            print("leave_disable:", update)
            await self.db_disconnect()
            em = discord.Embed(description=f"Leave System has been `disabled`",color=self.Mcolor)
            await ctx.send(embed=em)
    
    @commands.hybrid_command(name='join_role_disable', description='Disable join role System.')
    @commands.has_permissions(administrator=True)
    async def join_role_disable(self,ctx:commands.Context):
        self.db_connect()
        ss = await self.db.server.find_unique(where={"server_id": ctx.guild.id})
        doc_ref = await self.db.joinrole.find_unique(where={"server_id": ctx.guild.id})
        if doc_ref == None:
            print("Table not found in database for join role")
            em = discord.Embed(description=f"Join role table not found in database for Server:`{ctx.guild.id}`", color=self.Mcolor) 
            await self.db_disconnect()
            await ctx.guild.get_channel(ss.log_channel).send(embed=em)
        if doc_ref.status == False:
            print("Join role System is already disabled")
            em = discord.Embed(description=f"Join role System is already `disabled`", color=self.Mcolor)
            await self.db_disconnect()
            await ctx.send(embed=em)
        else:
            update = await self.db.joinrole.update(where={"ID":doc_ref.ID}, data={"status": False})
            print("join_role_disable:", update)
            await self.db_disconnect()
            em = discord.Embed(description=f"Join role System has been `disabled`",color=self.Mcolor)
            await ctx.send(embed=em)
            
    @commands.hybrid_command(name='disable_system', description='Disable a system (welcome, leave, or join_role).')
    @commands.has_permissions(administrator=True)
    async def disable_system(self, ctx: commands.Context):
        await self.db_connect()
        ss = await self.db.server.find_unique(where={"server_id": ctx.guild.id})
        await self.db_disconnect()

        if not ss:
            await ctx.send("Server not found in the database.")
            return

        # Create buttons with custom IDs
        buttons = [
            Button(label="Welcome", style=discord.ButtonStyle.primary, custom_id="welcome"),
            Button(label="Leave", style=discord.ButtonStyle.primary, custom_id="leave"),
            Button(label="Join Role", style=discord.ButtonStyle.primary, custom_id="join_role")
        ]

        # Create view and add buttons
        view = View()
        for button in buttons:
            button.callback = self.button_callback  # Assign the callback to each button
            view.add_item(button)

        # Send message with buttons
        emm = discord.Embed(description="Select the system you want to disable.", color=self.Mcolor)
        await ctx.send(embed=emm, view=view)

    async def button_callback(self, interaction: discord.Interaction):
        print("Button clicked:", interaction.data)
        ctx = await self.bot.get_context(interaction.message)

        if interaction.user != ctx.author:
            await interaction.response.send_message("You cannot interact with this button.", ephemeral=True)
            return

        button_label = interaction.data['custom_id']
        print(button_label)

        system_map = {
            "welcome": "welcome",
            "leave": "leave",
            "join_role": "joinrole"
        }

        system = system_map.get(button_label)
        if system:
            await self.disable_system_helper(ctx, system)
            await interaction.response.send_message(f"{button_label.capitalize()} system disabled.", ephemeral=True)
        else:
            await interaction.response.send_message("Invalid system.", ephemeral=True)

    async def disable_system_helper(self, ctx: commands.Context, system: str):
        await self.db_connect()
        ss = await self.db.server.find_unique(where={"server_id": ctx.guild.id})

        if system == "welcome":
            doc_ref = await self.db.welcome.find_unique(where={"server_id": ctx.guild.id})
            table_name = "Welcome"
        elif system == "leave":
            doc_ref = await self.db.goodbye.find_unique(where={"server_id": ctx.guild.id})
            table_name = "Leave"
        elif system == "join_role":
            doc_ref = await self.db.joinrole.find_unique(where={"server_id": ctx.guild.id})
            table_name = "Join Role"
        else:
            await self.db_disconnect()
            await ctx.send("Invalid system name. Please use 'welcome', 'leave', or 'join_role'.")
            return

        if doc_ref is None:
            print(f"Table not found in database for {table_name} system")
            em = discord.Embed(description=f"{table_name} table not found in database for Server: `{ctx.guild.id}`", color=self.Mcolor)
            await ctx.guild.get_channel(ss.log_channel).send(embed=em)
            await self.db_disconnect()
            return

        if not doc_ref.status:
            print(f"{table_name} System is already disabled")
            em = discord.Embed(description=f"{table_name} System is already `disabled`", color=self.Mcolor)
            await ctx.send(embed=em)
            await self.db_disconnect()
            return

        update = await getattr(self.db, system).update(where={"server_id": ctx.guild.id}, data={"status": False})
        print(f"{system}_disable:", update)
        await self.db_disconnect()

        em = discord.Embed(description=f"{table_name} System has been `disabled`", color=self.Mcolor)
        await ctx.send(embed=em)

    # @commands.hybrid_command(name='enable_system', description='Enable system for (welcome, leave, or join_role).')
    # async def enable_system(self, ctx: commands.Context):
    #     await self.db_connect()
    #     ss = await self.db.server.find_unique(where={"server_id": ctx.guild.id})

    #     # Create buttons
    #     welcome_button = Button(label="Welcome", style=discord.ButtonStyle.primary, custom_id="welcome")
    #     leave_button = Button(label="Leave", style=discord.ButtonStyle.primary, custom_id="leave")
    #     join_role_button = Button(label="Join Role", style=discord.ButtonStyle.primary, custom_id="join_role")

    #     # Create view with buttons
    #     view = View()
    #     view.add_item(welcome_button)
    #     view.add_item(leave_button)
    #     view.add_item(join_role_button)

    #     # Send message with buttons
    #     emm = discord.Embed(description="Select the system you want to Enable.", color=self.Mcolor)
    #     await ctx.send(embed=emm, view=view)

    #     # Define the button interaction handling
    #     async def button_callback(interaction: discord.Interaction):
    #         print("Button clicked:", interaction.data)
    #         if interaction.user != ctx.author:
    #             await interaction.response.send_message("You cannot interact with this button.", ephemeral=True)
    #             return
    #         # Handle button click
    #         button_label = interaction.data['custom_id']
    #         print(button_label)
    #         if button_label == "welcome":
    #             print("Welcome")
    #             await self.enable_system_helper(ctx, "welcome")
    #         elif button_label == "leave":
    #             print("Leave")
    #             await self.enable_system_helper(ctx, "leave")
    #         elif button_label == "join_role":
    #             print("Join Role")
    #             await self.enable_system_helper(ctx, "joinrole")

    #     # Assign the callback to buttons
    #     welcome_button.callback = button_callback
    #     leave_button.callback = button_callback
    #     join_role_button.callback = button_callback

    #     await self.db_disconnect()

    # async def enable_system_helper(self, ctx: commands.Context, system: str):
    #     await self.db_connect()
    #     ss = await self.db.server.find_unique(where={"server_id": ctx.guild.id})
    #     if system.lower() == "welcome":
    #         doc_ref = await self.db.welcome.find_unique(where={"server_id": ctx.guild.id})
    #         table_name = "Welcome"
    #     elif system.lower() == "leave":
    #         doc_ref = await self.db.goodbye.find_unique(where={"server_id": ctx.guild.id})
    #         table_name = "Leave"
    #     elif system.lower() == "join_role":
    #         doc_ref = await self.db.joinrole.find_unique(where={"server_id": ctx.guild.id})
    #         table_name = "Join Role"
    #     else:
    #         await self.db_disconnect()
    #         await ctx.send(f"Invalid system name. Please use 'welcome', 'leave', or 'join_role'.")
    #         return
    #     await self.db_disconnect()
    #     if doc_ref is None:
    #         print(f"Table not found in database for {table_name} system")
    #         em = discord.Embed(description=f"{table_name} table not found in database for Server:`{ctx.guild.id}`", color=self.Mcolor)
    #         await ctx.guild.get_channel(ss.log_channel).send(embed=em)
    #         return

    #     if doc_ref.status is True:
    #         print(f"{table_name} System is already Enabled")
    #         em = discord.Embed(description=f"{table_name} System is already `Enabled`", color=self.Mcolor)
    #         await ctx.send(embed=em)
    #         return
        
    #     if system.lower() in ("welcome", "leave", "join_role"):
    #         print(f"{system} system")
    #         await self.db_connect()
    #         update = await getattr(self.db, system.lower()).update(where={"server_id": ctx.guild.id},data={"status": True})
    #         await self.db_disconnect()
    #         print(f"{system}_disable:", update)
        
    #     em = discord.Embed(description=f"{table_name} System has been `Enabled`", color=self.Mcolor)
    #     await ctx.send(embed=em)


async def setup(bot:commands.Bot):
    await bot.add_cog(WelcomeLeaveCog(bot))
