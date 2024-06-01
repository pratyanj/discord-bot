import platform
import random

import aiohttp
from click import Command
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
from prisma import Prisma
import config

class General(commands.Cog, name="general"):
    def __init__(self, bot:commands.bot) -> None:
        self.bot = bot
        self.db = Prisma()
        self.Mcolor = discord.Colour.from_rgb(0, 97, 146)
        self.context_menu_user = app_commands.ContextMenu(
            name="Grab ID", callback=self.grab_id
        )
        self.bot.tree.add_command(self.context_menu_user)
        self.context_menu_message = app_commands.ContextMenu(
            name="Remove spoilers", callback=self.remove_spoilers
        )
        self.bot.tree.add_command(self.context_menu_message)

    # Message context menu command
    async def remove_spoilers(
        self, interaction: discord.Interaction, message: discord.Message
    ) -> None:
        """
        Removes the spoilers from the message. This command requires the MESSAGE_CONTENT intent to work properly.

        :param interaction: The application command interaction.
        :param message: The message that is being interacted with.
        """
        spoiler_attachment = None
        for attachment in message.attachments:
            if attachment.is_spoiler():
                spoiler_attachment = attachment
                break
        embed = discord.Embed(
            title="Message without spoilers",
            description=message.content.replace("||", ""),
            color=self.Mcolor,
        )
        if spoiler_attachment is not None:
            embed.set_image(url=attachment.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # User context menu command
    async def grab_id(
        self, interaction: discord.Interaction, user: discord.User
    ) -> None:
        """
        Grabs the ID of the user.

        :param interaction: The application command interaction.
        :param user: The user that is being interacted with.
        """
        embed = discord.Embed(
            description=f"The ID of {user.mention} is `{user.id}`.",
            color=self.Mcolor,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.hybrid_command(
        name="botinfo",
        description="Get some useful (or not) information about the bot.",
    )
    async def botinfo(self, context: Context) -> None:
        """
        Get some useful (or not) information about the bot.

        :param context: The hybrid command context.
        """
        await self.db.connect()
        prifix = await self.db.server.find_first(where={"server_id": context.guild.id})
        await self.db.disconnect()
        embed = discord.Embed(
            description="Stil in development, but here is some information about the bot.",
            color=self.Mcolor,
        )
        embed.set_author(name="Bot Information")
        embed.add_field(name="Owner:", value="Pratyanj", inline=True)
        embed.add_field(
            name="Python Version:", value=f"{platform.python_version()}", inline=True
        )
        embed.add_field(
            name="Prefix:",
            value=f"/ (Slash Commands) or {prifix.prefix} for normal commands",
            inline=False,
        )
        embed.set_footer(text=f"Requested by {context.author}")
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="serverinfo",
        description="Get some useful (or not) information about the server.",
    )
    async def serverinfo(self, context: Context) -> None:
        """
        Get some useful (or not) information about the server.

        :param context: The hybrid command context.
        """
        roles = [role.name for role in context.guild.roles]
        num_roles = len(roles)
        if num_roles > 50:
            roles = roles[:50]
            roles.append(f">>>> Displaying [50/{num_roles}] Roles")
        roles = ", ".join(roles)

        embed = discord.Embed(
            title="**Server Name:**", description=f"{context.guild}", color=self.Mcolor
        )
        if context.guild.icon is not None:
            embed.set_thumbnail(url=context.guild.icon.url)
        embed.add_field(name="Server ID", value=context.guild.id)
        embed.add_field(name="Member Count", value=context.guild.member_count)
        embed.add_field(
            name="Text/Voice Channels", value=f"{len(context.guild.channels)}"
        )
        embed.add_field(name=f"Roles ({len(context.guild.roles)})", value=roles)
        embed.set_footer(text=f"Created at: {context.guild.created_at}")
        await context.send(embed=embed)

    @commands.hybrid_command(name='sync', description='Sync all slash commands')
    async def sync(self, ctx: commands.Context):
        await ctx.send("Syncing...")
        await self.bot.tree.sync()
    
    @commands.hybrid_command(
        name="ping",
        description="Check if the bot is alive.",
    )
    async def ping(self, context: Context) -> None:
        """
        Check if the bot is alive.

        :param context: The hybrid command context.
        """
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"The bot latency is {round(self.bot.latency * 1000)}ms.",
            color=self.Mcolor,
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="invite",
        description="Get the invite link of the bot to be able to invite it.",
    )
    async def invite(self, context: Context) -> None:
        """
        Get the invite link of the bot to be able to invite it.

        :param context: The hybrid command context.
        """
        embed = discord.Embed(
            description=f"Invite me by clicking [here]({config.invite_link}).",
            color=self.Mcolor,
        )
        try:
            await context.author.send(embed=embed)
            await context.send("I sent you a private message!")
        except discord.Forbidden:
            await context.send(embed=embed)

    # @commands.hybrid_command(
    #     name="server",
    #     description="Get the invite link of the discord server of the bot for some support.",
    # )
    # async def server(self, context: Context) -> None:
    #     """
    #     Get the invite link of the discord server of the bot for some support.

    #     :param context: The hybrid command context.
    #     """
    #     embed = discord.Embed(
    #         description=f"Join the support server for the bot by clicking [here](https://discord.gg/mTBrXyWxAF).",
    #         color=self.Mcolor,
    #     )
    #     try:
    #         await context.author.send(embed=embed)
    #         await context.send("I sent you a private message!")
    #     except discord.Forbidden:
    #         await context.send(embed=embed)
    @commands.hybrid_command(name='setprefix', description='Set the prefix for this server.', with_app_command=True)
    @app_commands.describe(new_prefix="The new prefix for this server.")
    async def setprefix(self,ctx: commands.Context, new_prefix):
        await self.db.connect()
        server = await self.db.server.find_unique(where={"server_id": ctx.guild.id})
        await self.db.server.update(where={"ID": server.ID}, data={"prefix": new_prefix})
        await self.db.disconnect()
        em = discord.Embed(
            title="Prefix Changed",
            description=f"Prefix changed to `{new_prefix}` for this server.",
            color=self.Mcolor,
        )
        await ctx.send(embed=em)
    
    @commands.hybrid_command(name="check", description="Check bot permissions", with_app_command=True)
    async def check_bot_permissions(self,ctx:commands.Context):
        print("Checking bot permissions...")
        # Check permissions in the channel where the command was invoked
        channel = ctx.channel
        bot_permissions = channel.permissions_for(ctx.me)

        # Prepare a formatted message with permissions
        permissions_message = '\n'.join(
            [f'{permission}: {value}' for permission, value in bot_permissions])

        # Respond with the permissions message
        embed = discord.Embed(title=f'Bot permissions in {channel.name}', description=permissions_message)
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="8ball",
        description="Ask any question to the bot.",
    )
    @app_commands.describe(question="The question you want to ask.")
    async def eight_ball(self, context: Context, *, question: str) -> None:
      
        answers = [
            "It is certain.",
            "It is decidedly so.",
            "You may rely on it.",
            "Without a doubt.",
            "Yes - definitely.",
            "As I see, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again later.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful.",
        ]
        embed = discord.Embed(
            title="**My Answer:**",
            description=f"{random.choice(answers)}",
            color=self.Mcolor,
        )
        embed.set_footer(text=f"The question was: {question}")
        await context.send(embed=embed)


async def setup(bot) -> None:
    await bot.add_cog(General(bot))
