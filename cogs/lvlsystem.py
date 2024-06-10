import discord
from discord.ext import commands, tasks
from prisma import Prisma
import random
from easy_pil import *


class Level_System(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = Prisma()
        self.Mcolor = discord.Colour.from_rgb(0, 97, 146)

    async def db_connect(self):
        if not self.db.is_connected():
            # print("Connecting to database...")
            await self.db.connect()

    async def db_disconnect(self):
        if self.db.is_connected():
            await self.db.disconnect()
            # print("Disconnected from database")
    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        # print("_____________________LVLsystem______________________")
        await self.db_connect()
        ss = await self.db.server.find_unique(where={"server_id": message.guild.id})
        if ss == None:
            await self.db_disconnect()
            print("No server found")
            return
        
        if ss.prefix in message.content or message.author.bot:
            await self.db_disconnect()
            # print("Message is a command or a bot")
            return
        author = message.author
        guild = message.guild
        print("user:", author)
        print("Server_name:", guild)
        user = await self.db.userslevel.find_first(where={"user_id": author.id, "server_id": message.guild.id})
        print(f"user lvl data:/n{user}")
        sys = await self.db.levelsetting.find_unique(where={"server_id": message.guild.id})
        print(f"Lvl system:/n{sys}")
        if sys == None:
            create_sys = await self.db.levelsetting.create(data={"server_id": message.guild.id, "status": True, "level_up_channel_id": 0, "level_up_channel_name": ''})
            embed = discord.Embed(
                title="Level System", description=f"A new level system has been created for {message.guild.name}", color=discord.Color.green())
            await message.guild.get_channel(ss.log_channel).send(embed=embed)
            await self.db_disconnect()
            return

        if user == None:
            create_user = await self.db.userslevel.create(data={"server_id": message.guild.id, "user_id": author.id, "user_name": author.name, "level": 0, "xp": 1})
            em = discord.Embed(title="Level system",description=f"New user add to lvl system:`{author.id}`", color=self.Mcolor)
            await message.guild.get_channel(ss.log_channel).send(embed=em)
            await self.db_disconnect()
            # print(f"New member add to lvl system:{author.id}")
            return

        if sys.status == False:
            # print("Level system is off")
            # print(f"serverlogchannel:{ss.log_channel}")
            embed = discord.Embed(
                title="Level system", description=f"Level system is off", color=discord.Color.green())
            await message.guild.get_channel(ss.log_channel).send(embed=embed)
            await self.db_disconnect()
            # print("Level system is off")
            return

        try:
            xp = int(user.xp)
            level = int(user.level)
        except:
            xp = 0
            level = 0

        if level < 5:
            print("Level is less than 5")
            xp += random.randint(1, 5)
            await self.db.userslevel.update(where={"ID": user.ID}, data={"xp": xp})
            await self.db_disconnect()
        else:
            print("Level is more than 5")
            rand = random.randint(1, (level//2))
            print(rand)
            if rand == 1:
                xp += random.randint(1, 3)
                print(f"xp is increased to {xp}")
                await self.db.userslevel.update(where={"ID": user.ID}, data={"xp": xp})
                await self.db_disconnect()
        print(f"XP: {xp}, Level: {level}")

        if xp >= 100:
            await self.db_connect()
            level += 1
            await self.db.userslevel.update(where={"ID": user.ID}, data={"level": level, "xp": 0})
            msg = f"{author.mention} leveled up to {level}"
            print('msg:', msg)
            dataa = await self.db.levelrole.find_many(where={"server_id": message.guild.id})
            await self.db_disconnect()
            if len(dataa) == 0 or dataa == None:
                return
            for i in dataa:
                if int(i.level) == level:
                    role = guild.get_role(int(i.role_id))
                    try:
                        await author.add_roles(role)
                        em  = discord.Embed(description=f'🏆{author.mention} has just level upto **{level}** and reworded with {role.name}✨', color=self.Mcolor)
        
                        if sys.level_up_channel_id == 0:
                            await message.channel.send(embed=em)
                        else:
                            await message.guild.get_channel(sys.level_up_channel_id).sent(embed=em)
    
                        return
                    except discord.HTTPException:
                        em = discord.Embed(description=f'{author.mention} Bot does not have permission for that add the role {role.name} to you.')
                        if sys.level_up_channel_id == 0:
                            await message.channel.send(embed=em)
                        else:
                            await message.guild.get_channel(sys.level_up_channel_id).sent(embed=em)
            em1 = discord.Embed(description=f"{msg}",color=self.Mcolor)
            if sys.level_up_channel_id == 0:
                await message.channel.send(embed=em1)
            else:
                await message.guild.get_channel(sys.level_up_channel_id).sent(embed=em1)

    
    
    @commands.hybrid_command(name="lvl", description="Check your level", with_app_command=True)
    async def lvl(self,ctx:commands.Context):
        await self.db_connect()
        member = ctx.author
        server = await self.db.server.find_unique(where={"server_id": ctx.guild.id})
        lvl = await self.db.levelsetting.find_unique(where={"server_id": ctx.guild.id})
        user = await self.db.userslevel.find_first(where={"server_id": ctx.guild.id, "user_id": member.id})
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
            user_lvl = await self.db.userslevel.find_many(where={"server_id": ctx.guild.id}, order=[{"level": "desc"}, {"xp": "desc"}], take=10)
            member_rank = int
            rank = 1
            # Iterate over the documents and append them to the leaderboard list
            for doc in user_lvl:
                print("counter:",rank+1)
                if doc.user_id  == member.id:
                    member_rank = rank
                    break
            print(f"member_rank:{member_rank}")
            background = Editor(Canvas((900, 200), color="#2a2a2a"))
            
            profile_pic = await load_image_async(str(member.avatar.url))
            profile = Editor(profile_pic).resize((150,150)).circle_image()
            card_right_shape=[(600,0),(750,200),(900,200),(900,0)]

            
            poppins1 = Font('cogs\src\levelfont.otf', size=30)
            poppins2 = Font('cogs\src\levelfont.otf', size=50)
            poppins3 = Font('cogs\src\levelfont.otf', size=65)
            
            
            background.polygon(card_right_shape, color="#00609a")
            background.paste(profile, (30, 30))
            # progress bar
            background.rectangle((200, 150), width=470,height=30, color="#474b4e", radius=12)
            if xp != 0:
                background.bar((200, 150), 
                               max_width=470, 
                               height=30,
                               color="#00609a", 
                               radius=12, 
                               percentage=userdata["percent"])
            # User_name:
            background.text((200, 30), userdata["name"], font=poppins3, color="#FFFFFF")
            # Level:
            # if level >= 10:
            #     background.text((715, 22), f'Level: {userdata["level"]}', font=poppins2, color="#2a2a2a")
            # else:
            #     background.text((720, 22), f'Level: {userdata["level"]}', font=poppins2, color="#2a2a2a")
            
            background.text((680, 10), f'Level:', font=poppins2, color="#2a2a2a")
            background.text((720, 60), f'{userdata["level"]}', font=poppins2, color="#FFFFFF")
            
            # Rank:
            background.text((720, 110), f'Rank:', font=poppins2, color="#2a2a2a")
            background.text((760, 160), f'{member_rank}', font=poppins2, color="#FFFFFF")
            # XP:1/100
            background.text(
                position=(200, 115), 
                text=f'XP:-{userdata["xp"]}/{userdata["next_level_xp"]}', 
                font=poppins1, color="#FFFFFF"
                )
            file = discord.File(fp=background.image_bytes,filename="levelcard.jpg")
            await self.db_disconnect()
            await ctx.send(file=file)

        else:
            userLVL = await self.db.userslevel.create(data={"server_id": ctx.guild.id, "user_id": ctx.author.id, "user_name": ctx.author.name, "xp": 1, "level": 0})
            print("New user created", userLVL)
            await self.db_disconnect()
            return

    @commands.hybrid_command(name="lvlsys_enable", description="Enable leveling system")
    @commands.has_permissions(manage_messages=True)
    async def enable(self, ctx: commands.Context):
        await self.db_connect()
        lvldb = await self.db.levelsetting.find_unique(where={"server_id": ctx.guild.id})
        ss = await self.db.server.find_unique(where={"server_id": ctx.guild.id})
        if lvldb == None:
            print("No leveling settings found for this server, creating new...(CMD for enable_lvl)")
            await self.db.levelsetting.create(data={"server_id": ctx.guild.id, "status": False,"level_up_channel_id":0,"level_up_channel_name":""})
            await self.db_disconnect()
            em = discord.Embed(
                title="CMD",
                description="No leveling settings found for this server!",
                color=discord.Color.red()
            )
            await ctx.guild.get_channel(int(ss.log_channel)).send(embed=em)
            await ctx.send(embed=em)

        if lvldb.status == True:
            await self.db_disconnect()
            
            em = discord.Embed(
                description="The leveling system is already enabled.",
                color=self.Mcolor
            )
            await ctx.send(embed=em)
        else:
            update = await self.db.levelsetting.update(where={"ID": lvldb.ID}, data={"status": True})
            await self.db_disconnect()
            em = discord.Embed(
                description="Leveling system has been enabled",
                color=self.Mcolor)
            await ctx.send(embed=em)

    @commands.hybrid_command(name="lvlsys_disable",description="Disable leveling system")
    @commands.has_permissions(manage_messages=True)
    async def disable(self, ctx: commands.Context):
        await self.db_connect()
        ss = await self.db.server.find_unique(where={"server_id": ctx.guild.id})
        lvldb = await self.db.levelsetting.find_unique(where={"server_id": ctx.guild.id})
        if lvldb == None:
            print("No leveling settings found for this server, creating new...(CMD for enable_lvl)")
            await self.db.levelsetting.create(data={"server_id": ctx.guild.id, "status": False,"level_up_channel_id":0,"level_up_channel_name":""})
            await self.db_disconnect()
            em = discord.Embed(
                title="CMD",
                description="No leveling settings found for this server!",
                color=discord.Color.red()
            )
            await ctx.guild.get_channel(int(ss.log_channel)).send(embed=em)
            await ctx.send(embed=em)
            return

        if lvldb.status == False:
            await self.db_disconnect()
            embed = discord.Embed(description="Leveling system is already disabled",color=self.Mcolor)
            await ctx.send(embed=embed)
        else:
            update = await self.db.levelsetting.update(where={"ID": lvldb.ID}, data={"status": False})
            await self.db_disconnect()
            em = discord.Embed(description="Leveling system has been disabled",color=self.Mcolor)
            await ctx.send(embed=em)

    @commands.hybrid_command(name="lvlrole",description="Set a role for a level")
    @commands.has_permissions(manage_roles=True)
    async def set_role(self, ctx: commands.Context, level: int, role: discord.Role):
        await self.db_connect()
        ss = await self.db.server.find_unique(where={"server_id": ctx.guild.id})
        lvldb = await self.db.levelsetting.find_unique(where={"server_id": ctx.guild.id})
        roledb = await self.db.levelrole.find_first(where={"server_id": ctx.guild.id, "role_id": role.id})
        if lvldb.status == False:
            await self.db_disconnect()
            em = discord.Embed(description="Leveling system is disabled plz emable it for this feature.",color=self.Mcolor)
            await ctx.send(embed=em)
            return
        if roledb != None:
            print("Role already exists")
            await self.db_disconnect()
            em = discord.Embed(description="Role already exists",color=self.Mcolor)
            await ctx.send(embed=em)
            return
        update = await self.db.levelrole.create(data={"server_id": ctx.guild.id, "role_id": role.id, "role_name": role.name, "level": level})
        print("Role set for {role} from {level}".format(
            role=role.name, level=level))
        em = discord.Embed(description=f"Role has been set for Level({level} to role `{role.name}`)",color=self.Mcolor)
        await self.db_disconnect()
        await ctx.send(embed=em)

    @commands.hybrid_command(name='rank', help='Check your rank')
    async def rank(self, ctx: commands.Context):
        await self.db_connect()
        server = await self.db.server.find_unique(where={"server_id": ctx.guild.id})
        lvl = await self.db.levelsetting.find_unique(where={"server_id": ctx.guild.id})
        if lvl.status == False:
            await self.db_disconnect()
            em = discord.Embed(description="Leveling system is disabled plz emable it for this feature.",color=self.Mcolor)
            await ctx.send(embed=em)
            return
        user_lvl = await self.db.userslevel.find_many(where={"server_id": ctx.guild.id}, order=[{"level": "desc"}, {"xp": "desc"}], take=10)
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
        await self.db_disconnect()

    @commands.hybrid_command(name='lvlsys_set_channel', help='Set channel for level up messages')
    async def set_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        await self.db_connect()
        lvl = await self.db.levelsetting.find_unique(where={"server_id": ctx.guild.id})
        if lvl == None :
            em = discord.Embed(description="Leveling system table not found in database",color=self.Mcolor)
            await ctx.send(embed=em)
            await self.db_disconnect()
        if lvl.level_up_channel_id == channel.id:
            em = discord.Embed(description=f"Channel is already setted to `{channel.name}`", color=self.Mcolor)
            await ctx.send(embed=em)
            await self.db_disconnect()
        else:
            update = await self.db.levelsetting.update(where={"server_id": ctx.guild.id}, data={"level_up_channel_id": channel.id,"level_up_channel_name": channel.name})
            em = discord.Embed(description=f"Level system Channel has been set to `{channel.name}`",color=self.Mcolor)
            await self.db_disconnect()
            await ctx.send(embed=em)
             
async def setup(bot: commands.Bot):
    await bot.add_cog(Level_System(bot))
