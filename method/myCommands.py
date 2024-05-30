from cgitb import grey
from turtle import update
from click import command
from discord.ext import commands
import discord
from easy_pil import *
import asyncio
from prisma import Prisma
db = Prisma()

# print("myCommands.py")


async def check_bot_permissions(ctx):
    print("Checking bot permissions...")
    # Check permissions in the channel where the command was invoked
    channel = ctx.channel
    bot_permissions = channel.permissions_for(ctx.me)

    # Prepare a formatted message with permissions
    permissions_message = '\n'.join(
        [f'{permission}: {value}' for permission, value in bot_permissions])

    # Respond with the permissions message
    await ctx.send(f'Bot permissions in {channel.name}:\n{permissions_message}')


async def add_join_role(ctx, channel: discord.channel, role: discord.role):
    await db.connect()
    server = await db.joinrole.find_unique(where={"server_id": ctx.guild.id})
    if server == None:
        print(f"Table not found in database for join role:{ctx.guild.id}")
        await ctx.guild.get_channel(channel.id).send(f"Table not found in database for join role:{ctx.guild.id}")
        await db.disconnect()
        return
    print("sevrer_data:", server)
    update = await db.joinrole.update(where={"ID":server.ID}, data={"status": True, "role_id": f"{role.id}", "role_name": f"{role.name}"})
    print("add_join_role:", update)
    await db.disconnect()
    await ctx.send(f'Join role has been set to {role.name}!')


async def clear(ctx:commands.Context, amount: int):
    # Check if the command user has the "Manage Messages" permission
    if ctx.author.guild_permissions.manage_messages:
        try:
            # Purge the specified number of messages (including the command itself)
            deleted_messages = await ctx.channel.purge(limit=amount + 1)
            # Send a confirmation message
            confirmation_message = await ctx.send(f'Successfully deleted {len(deleted_messages) - 1} messages.')
            # Delete the confirmation message after a few seconds
            # Use asyncio.sleep instead of discord.utils.sleep_until
            await asyncio.sleep(3)
            await confirmation_message.delete()
        except discord.Forbidden:
            await ctx.send('I do not have the required permissions to manage messages.')
    else:
        await ctx.send('You do not have the "Manage Messages" permission.')

# async def clear(interaction, count: int):
#     # Check if the command user has the "Manage Messages" permission
#     if interaction.author.guild_permissions.manage_messages:
#         try:
#             # Purge the specified number of messages (including the command itself)
#             deleted_messages = await interaction.channel.purge(limit=count + 1)
#             # Send a confirmation message
#             confirmation_message = await interaction.send(f'Successfully deleted {len(deleted_messages) - 1} messages.')
#             # Delete the confirmation message after a few seconds
#             await asyncio.sleep(3)  # Use asyncio.sleep instead of discord.utils.sleep_until
#             await confirmation_message.delete()
#         except discord.Forbidden:
#             await interaction.response.send_message('I do not have the required permissions to manage messages.')
#     else:
#         await interaction.response.send_message('You do not have the "Manage Messages" permission.')


async def setleavechannel(ctx, leave_channel: discord.TextChannel):
    await db.connect()
    ss = await db.server.find_unique(where={"server_id": ctx.guild.id})
    Guild = ctx.guild
    channel = leave_channel
    if Guild:
        for chann in Guild.channels:
            if chann.id == channel:
                doc_ref = await db.goodbye.find_unique(where={"server_id": ctx.guild.id})
                if doc_ref == None:
                    print("Table not found in database for leave channel")
                    await ctx.guild.get_channel(ss.log_channel).send(f"Table not found in database for leave channel:{ctx.guild.id}")
                    await db.disconnect()
                    return
                update = await db.goodbye.update(where={"ID":doc_ref.ID}, data={"status": True, "channel_id": f"{chann.id}", "channel_name": f"{chann.name}"})
                print("setleavechannel:", update)
                await db.disconnect()
                await ctx.send(f'Leave channel has been set to {chann.name}!')
    else:
        await db.disconnect()
        await ctx.send(f"{Guild} is not a valid server id")


async def setwelcomechannel(ctx, welcome_channel: discord.TextChannel):
    
    await db.connect()
    Guild = ctx.guild
    channel = welcome_channel
    ss = await db.server.find_unique(where={"server_id": ctx.guild.id})
    if Guild:
        for chann in Guild.channels:
            if chann.id == channel:
                doc_ref = await db.welcome.find_unique(where={"server_id": ctx.guild.id})
                if doc_ref == None:
                    print(
                        f"Table not found in database for welcome channel:{ctx.guild.id}")
                    await ctx.guild.get_channel(ss.log_channel).send(f"Table not found in database for welcome channel:{ctx.guild.id}")
                    await db.disconnect()
                    return
                update = await db.welcome.update(where={"ID":doc_ref.ID}, data={"status": True, "channel_id": f"{chann.id}", "channel_name": f"{chann.name}"})
                print("setwelcomechannel:", update)
                await db.disconnect()
                await ctx.send(f'Welcome channel has been set to {chann.name}!')
    else:
        await db.disconnect()
        await ctx.send(f"{Guild} is not a valid server id")

# ----------lvl system----------


async def level(ctx, member):
    await db.connect()
    if member is None:
        member = ctx.author
    server = await db.server.find_unique(where={"server_id": ctx.guild.id})
    lvl = await db.levelsetting.find_unique(where={"server_id": ctx.guild.id})
    user = await db.userslevel.find_first(where={"server_id": ctx.guild.id, "user_id": member.id})
    if user != None:
        try:
            xp = user.xp
            level = user.level
        except:
            xp = 0
            level = 0
        userdata = {
            "name": f'{member.name}',
            "xp": xp,
            "level": level,
            "next_level_xp": 100,
            "percent": xp,
        }

        background = Editor(Canvas((900, 200), color="#00609a"))

        profile_pic = await load_image_async(str(member.avatar.url))
        profile = Editor(profile_pic).resize((150, 150)).circle_image()

        poppins_small = Font.poppins(size=25)

        background.paste(profile, (30, 30))
        # progress bar
        background.rectangle((200, 160), width=650,
                             height=30, color="#474b4e", radius=20)
        if xp != 0:
            background.bar((200, 160), max_width=650, height=30,
                           color="#60d6f2", radius=20, percentage=userdata["percent"])

        background.text((200, 90), userdata["name"], font=Font.poppins(
            size=50), color="#FFFFFF")
        if level >= 10:
            background.text(
                (715, 22), f'Level:- {userdata["level"]}', font=Font.poppins(size=40), color="#FFFFFF")
        else:
            background.text(
                (720, 22), f'Level:- {userdata["level"]}', font=Font.poppins(size=40), color="#FFFFFF")
        background.text(
            (700, 130), f'XP:-{userdata["xp"]}/{userdata["next_level_xp"]}', font=poppins_small, color="#FFFFFF")

        file = discord.File(fp=background.image_bytes,
                            filename="levelcard.jpg")
        await db.disconnect()
        await ctx.send(file=file)

    else:
        userLVL = await db.userslevel.create(data={"server_id": ctx.guild.id, "user_id": ctx.author.id, "user_name": ctx.author.name, "xp": 1, "level": 0})
        print("New user created", userLVL)
        await db.disconnect()
        return


async def rank(ctx):
    await db.connect()
    server = await db.server.find_unique(where={"server_id": ctx.guild.id})
    lvl = await db.levelsetting.find_unique(where={"server_id": ctx.guild.id})
    if lvl.status == False:
        await db.disconnect()
        await ctx.send("Leveling system is disabled in this server")
        return
    user_lvl = await db.userslevel.find_many(where={"server_id": ctx.guild.id}, order=[{"level": "desc"}, {"xp": "desc"}], take=10)
    leaderboard = []
    # Iterate over the documents and append them to the leaderboard list
    for doc in user_lvl:
        leaderboard.append({
            "user_name": doc.user_name,
            "level": doc.level,
            "xp": doc.xp
        })
    y_pos = 20
    rank = 0
    display = ""
    for entry in leaderboard:
        y_pos += 10
        rank += 1
        display += f"**#{rank}** | **Level:** {entry['level']} | **XP:** {entry['xp']} | **User:** {entry['user_name']}\n"
    # Create a more beautiful embed with a white background
    em = discord.Embed(
        title="🏆 Leaderboard 🏆",
        description=display,
        color=discord.Colour.from_rgb(0, 97, 146))
    guild = ctx.bot.get_guild(ctx.guild.id)
    em.set_thumbnail(url=guild.icon)
    em.set_footer(text="Ranking of the top 10 users")
    await ctx.send(embed=em)
    await db.disconnect()

    # Iterate over the leaderboard and add the users to the image


async def enable_lvl(ctx):
    await db.connect()
    lvldb = await db.levelsetting.find_unique(where={"server_id"})
    ss = await db.server.find_unqiue(where={"server_id": ctx.guild.id})
    if lvldb == None:
        print("No leveling settings found for this server, creating new...(CMD for enable_lvl)")
        await db.disconnect()
        em = discord.Embed(
            title="CMD", 
            description="No leveling settings found for this server!",
            color=discord.Color.red()
            )
        await ctx.guild.get_channel(int(ss.log_channel)).send(embed=em)
        await ctx.send(embed=em)
        return
    
    if lvldb.status == True:
        await db.disconnect()
        await ctx.send("Leveling system is already enabled")
    else:
        update = await db.levelsetting.update(where={"ID":lvldb.ID}, data={"status": True})
        await db.disconnect()
        await ctx.send("Leveling system has been enabled")


async def disable_lvl(ctx:commands.Context):
    await db.connect()
    ss = await db.server.find_unqiue(where={"server_id": ctx.guild.id})
    lvldb = await db.levelsetting.find_unique(where={"server_id": ctx.guild.id})
    if lvldb == None:
        print("No leveling settings found for this server, creating new...(CMD for enable_lvl)")
        await db.disconnect()
        em = discord.Embed(
            title="CMD", 
            description="No leveling settings found for this server!",
            color=discord.Color.red()
            )
        await ctx.guild.get_channel(int(ss.log_channel)).send(embed=em)
        await ctx.send(embed=em)
        return
    
    if lvldb.status == False:
        await db.disconnect()
        await ctx.send("Leveling system is already disabled")
    else:
        update = await db.levelsetting.update(where={"ID":lvldb.ID}, data={"status": False})
        await db.disconnect()
        await ctx.send("Leveling system has been disabled")

# async def reward(ctx,db):
#     lvldb = db.collection("lvlsetting").document(str(ctx.guild.name)).get()
#     status=lvldb.to_dict()["lvlsys"]
#     if status == False:
#         return await ctx.send("Leveling system is disabled in this server")
#     if not lvldb:
#         return await ctx.send("No role levels have been setup yet for this server")
#     em = discord.Embed(title="Role Levels",description="Role levels are a way to reward people for getting to certain levels in a certain role")
#     for role in lvldb:
#         em.add_field(name=f"Level: {role[2]}", value=f"{ctx.guild.get_role(role[1])}",inline=False)
#     await ctx.send(embed = em)


async def setrole(ctx, bot, role: discord.role, level):
    await db.connect()
    lvldb = await db.levelsetting.find_unique(where={"server_id": ctx.guild.id})
    roledb = await db.levelrole.find_unique(where={"server_id": ctx.guild.id, "role_id": role.id})
    if lvldb.status == False:
        await db.disconnect()
        await ctx.send("Leveling system is disabled plz emable it for this feature.")
        return
    if roledb != None:
        print("Role already exists")
        await db.disconnect()
        await ctx.send("You have already set a role level")
        return
    update = await db.levelrole.create(data={"server_id": ctx.guild.id, "role_id": role.id, "role_name": role.name, "level": level})
    print("Role set for {role} from {level}".format(
        role=role.name, level=level))
    await ctx.send("Role has been set")
    print("Role has been set")
    await db.disconnect()

# -----------------------------------------------------------------------


async def create_category(ctx, category_name):
    await db.connect()
    guild = ctx.guild
    role = await guild.create_role(name=category_name, mentionable=True)
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
        role: discord.PermissionOverwrite(read_messages=True)
    }

    # Create the category
    category = await guild.create_category(category_name, overwrites=overwrites)

    # Create the role with the same name as the category
    # Assign the role to the member who executed the command
    await ctx.author.add_roles(role)
    # ctx.guild.get_role(role): discord.PermissionOverwrite(read_messages=True),
    # Create help channels within the newly created category
    link = await guild.create_text_channel(f'{category_name}_link', overwrites=overwrites, category=category)
    # print("link_id:",link.id,"link_name:",link.name)
    img = await guild.create_text_channel(f'{category_name}_img', overwrites=overwrites, category=category)
    await guild.create_text_channel(f'{category_name}_chat', overwrites=overwrites, category=category)

    # Append channel name and id to link_channel_list
    link_create = await db.linksonly.create(data={"server_id": ctx.guild.id, "channel_id": link.id, "channel_name": link.name})

    # Append channel name and id to imgl_channel_list
    img_create = await db.imagesonly.create(data={"server_id": ctx.guild.id, "channel_id": img.id, "channel_name": img.name})
    print(
        f"from command bot create the category\nlink channel:{link_create}\nimage channel:{img_create}")
    await db.disconnect()
    await ctx.send(f'Category "{category_name}" . Role assigned.')


async def setup_member_count(ctx):
    await db.connect()
    guild = ctx.guild

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
    }
    category_name = f"📊SERVER STATS"
    # Create the category
    category = await guild.create_category(category_name, overwrites=overwrites)
    # create memeber count channel
    member_count = await guild.create_voice_channel('😁Total Members', overwrites=overwrites, category=category)
    Online_member_count = await guild.create_voice_channel('😎Online Members', overwrites=overwrites, category=category)
    bot_count = await guild.create_voice_channel('🤖Bots', overwrites=overwrites, category=category)
    update = await db.membercount.create(data={"server_id": ctx.guild.id, "Total_Members": member_count.id, "Online_Members": Online_member_count.id, "Bots": bot_count.id, "status": True})
    await db.disconnect()
    await ctx.send(f'Your server has been setup with server stats')
