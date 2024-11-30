import discord
from discord.ext import commands, tasks
from prisma import Prisma
import random
from easy_pil import *
from typing import Final, ClassVar
from database.connection import db_connect, db_disconnect

LEVELS_AND_XP: Final = {
            '0': 0,
            '1': 100,
            '2': 255,
            '3': 475,
            '4': 770,
            '5': 1150,
            '6': 1625,
            '7': 2205,
            '8': 2900,
            '9': 3720,
            '10': 4675,
            '11': 5775,
            '12': 7030,
            '13': 8450,
            '14': 10045,
            '15': 11825,
            '16': 13800,
            '17': 15980,
            '18': 18375,
            '19': 20995,
            '20': 23850,
            '21': 26950,
            '22': 30305,
            '23': 33925,
            '24': 37820,
            '25': 42000,
            '26': 46475,
            '27': 51255,
            '28': 56350,
            '29': 61770,
            '30': 67525,
            '31': 73625,
            '32': 80080,
            '33': 86900,
            '34': 94095,
            '35': 101675,
            '36': 109650,
            '37': 118030,
            '38': 126825,
            '39': 136045,
            '40': 145700,
            '41': 155800,
            '42': 166355,
            '43': 177375,
            '44': 188870,
            '45': 200850,
            '46': 213325,
            '47': 226305,
            '48': 239800,
            '49': 253820,
            '50': 268375,
            '51': 283475,
            '52': 299130,
            '53': 315350,
            '54': 332145,
            '55': 349525,
            '56': 367500,
            '57': 386080,
            '58': 405275,
            '59': 425095,
            '60': 445550,
            '61': 466650,
            '62': 488405,
            '63': 510825,
            '64': 533920,
            '65': 557700,
            '66': 582175,
            '67': 607355,
            '68': 633250,
            '69': 659870,
            '70': 687225,
            '71': 715325,
            '72': 744180,
            '73': 773800,
            '74': 804195,
            '75': 835375,
            '76': 867350,
            '77': 900130,
            '78': 933725,
            '79': 968145,
            '80': 1003400,
            '81': 1039500,
            '82': 1076455,
            '83': 1114275,
            '84': 1152970,
            '85': 1192550,
            '86': 1233025,
            '87': 1274405,
            '88': 1316700,
            '89': 1359920,
            '90': 1404075,
            '91': 1449175,
            '92': 1495230,
            '93': 1542250,
            '94': 1590245,
            '95': 1639225,
            '96': 1689200,
            '97': 1740180,
            '98': 1792175,
            '99': 1845195,
            '100': 1899250
        }
MAX_XP: Final = LEVELS_AND_XP['100']
MAX_LEVEL: Final = 100        

class Level_System(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = Prisma()
        self.Mcolor = discord.Colour.from_rgb(0, 97, 146)
    from database.connection import db_connect, db_disconnect
    
    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        
        # print("_____________________LVLsystem______________________")
        await db_connect(self)
        ss = await self.db.server.find_unique(where={"server_id": message.guild.id})
        if ss == None:
            await db_disconnect()
            print("No server found")
            return
        
        if ss.prefix in message.content or message.author.bot:
            await db_disconnect()
            # print("Message is a command or a bot")
            return
        # -------------On xp role-------------------
        no_xp = await self.db.noxprole.find_many(where={"server_id": message.guild.id})
        if no_xp!= None:
            for i in no_xp:
                print("role id: ",i.role_id)
                print("message author roles: ",message.author.roles)
                if i.role_id in [role.id for role in message.author.roles]:                    
                    print("User has xp role")
                    await db_disconnect()
                    return
        # -------------On xp role-------------------
        # -------------on xp channel-------------------
        no_xp_channel_db = await self.db.noxpchannel.find_many(where={"server_id": message.guild.id})
        if no_xp_channel_db!= None:
            for i in no_xp_channel_db:
                if i.channel_id == message.channel.id:
                    await db_disconnect()
                    print("User has xp channel")
                    return
        # -------------on xp channel-------------------
        author = message.author
        guild = message.guild
        print("user:", author)
        print("Server_name:", guild)
        user = await self.db.userslevel.find_first(where={"user_id": author.id, "server_id": message.guild.id})
        print(f"user lvl data:/n{user}")
        sys = await self.db.levelsetting.find_unique(where={"server_id": message.guild.id})
        print(f"Lvl system:/n{sys}")
        
        # iF SRVER HAS NO LEVEL SYSTEM THEN CREATE ONE
        if sys == None:
            create_sys = await self.db.levelsetting.create(data={"server_id": message.guild.id, "status": True, "level_up_channel_id": 0, "level_up_channel_name": ''})
            embed = discord.Embed(
                title="Level System", description=f"A new level system has been created for {message.guild.name}", color=discord.Color.green())
            await message.guild.get_channel(ss.log_channel).send(embed=embed)
            await db_disconnect()
            return

        # IF USER IS NOT IN DATABASE THEN CREATE ONE
        if user == None:
            create_user = await self.db.userslevel.create(data={"server_id": message.guild.id, "user_id": author.id, "user_name": author.name, "level": 0, "xp": 1})
            em = discord.Embed(title="Level system",description=f"New user add to lvl system:`{author.id}`", color=self.Mcolor)
            await message.guild.get_channel(ss.log_channel).send(embed=em)
            await db_disconnect()
            # print(f"New member add to lvl system:{author.id}")
            return
        
        # IF LEVEL SYSTEM IS OFF THEN RETURN
        if sys.status == False:
            # print("Level system is off")
            # print(f"serverlogchannel:{ss.log_channel}")
            embed = discord.Embed(
                title="Level system", description=f"Level system is off", color=discord.Color.green())
            await message.guild.get_channel(ss.log_channel).send(embed=embed)
            await db_disconnect()
            # print("Level system is off")
            return

        try:
            xp = int(user.xp)
            level = int(user.level)
        except:
            xp = 0
            level = 0
        if user.xp >= MAX_XP:
            print("Max xp reached")
            await db_disconnect()
            return
        
        if level < 5:
            print("Level is less than 5")
            xp += random.randint(1, 5)
            await self.db.userslevel.update(where={"ID": user.ID}, data={"xp": xp})
            await db_disconnect()
        else:
            print("Level is more than 5")
            rand = random.randint(1, (level//2))
            print(rand)
            if rand == 1:
                xp += random.randint(1, 3)
                print(f"xp is increased to {xp}")
                await self.db.userslevel.update(where={"ID": user.ID}, data={"xp": xp})
                await db_disconnect()
            else:
                xp += int(rand)
                print(f"xp is increased to {xp}")
                await self.db.userslevel.update(where={"ID": user.ID}, data={"xp": xp})
                await db_disconnect()
                
        print(f"XP: {xp}, Level: {level}")

        if xp >= LEVELS_AND_XP[str(level)]:
            await db_connect(self)
            level += 1
            await self.db.userslevel.update(where={"ID": user.ID}, data={"level": level, "xp": 0})
            msg = f"{author.mention} leveled up to {level}"
            print('msg:', msg)
            dataa = await self.db.levelrole.find_many(where={"server_id": message.guild.id})
            await db_disconnect()
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
                print("|Level stting|**Level up channel is not set**")
                await message.channel.send(embed=em1)
            else:
                print("|Level stting|**Level up channel is set**")
                await message.guild.get_channel(sys.level_up_channel_id).sent(embed=em1)

    
    
    @commands.hybrid_command(name="lvl", description="Check your level", with_app_command=True)
    async def lvl(self,ctx:commands.Context):
        await db_connect(self)
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
                "next_level_xp": LEVELS_AND_XP[str(level)],
                "percent":(xp/LEVELS_AND_XP[str(1 if level == 0 else level)])*100,            }
            if userdata["percent"] < 1:
                userdata["percent"] = 2
            print("persontage:",userdata["percent"])
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

            
            poppins1 = Font('cogs\\src\\levelfont.otf', size=30)
            poppins2 = Font('cogs\\src\\levelfont.otf', size=50)
            poppins3 = Font('cogs\\src\\levelfont.otf', size=65)
            
            
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
            await db_disconnect()
            await ctx.send(file=file)

        else:
            userLVL = await self.db.userslevel.create(data={"server_id": ctx.guild.id, "user_id": ctx.author.id, "user_name": ctx.author.name, "xp": 1, "level": 0})
            print("New user created", userLVL)
            await db_disconnect()
            return

    @commands.hybrid_command(name="lvlsys_enable", description="Enable leveling system")
    @commands.has_permissions(manage_messages=True)
    @commands.has_permissions(administrator=True)
    async def enable(self, ctx: commands.Context):
        await db_connect(self)
        lvldb = await self.db.levelsetting.find_unique(where={"server_id": ctx.guild.id})
        ss = await self.db.server.find_unique(where={"server_id": ctx.guild.id})
        if lvldb == None:
            print("No leveling settings found for this server, creating new...(CMD for enable_lvl)")
            await self.db.levelsetting.create(data={"server_id": ctx.guild.id, "status": False,"level_up_channel_id":0,"level_up_channel_name":""})
            await db_disconnect()
            em = discord.Embed(
                title="CMD",
                description="No leveling settings found for this server!",
                color=discord.Color.red()
            )
            await ctx.guild.get_channel(int(ss.log_channel)).send(embed=em)
            await ctx.send(embed=em)

        if lvldb.status == True:
            await db_disconnect()
            
            em = discord.Embed(
                description="The leveling system is already enabled.",
                color=self.Mcolor
            )
            await ctx.send(embed=em)
        else:
            update = await self.db.levelsetting.update(where={"ID": lvldb.ID}, data={"status": True})
            await db_disconnect()
            em = discord.Embed(
                description="Leveling system has been enabled",
                color=self.Mcolor)
            await ctx.send(embed=em)

    @commands.hybrid_command(name="lvlsys_disable",description="Disable leveling system")
    @commands.has_permissions(manage_messages=True)
    @commands.has_permissions(administrator=True)
    async def disable(self, ctx: commands.Context):
        await db_connect(self)
        ss = await self.db.server.find_unique(where={"server_id": ctx.guild.id})
        lvldb = await self.db.levelsetting.find_unique(where={"server_id": ctx.guild.id})
        if lvldb == None:
            print("No leveling settings found for this server, creating new...(CMD for enable_lvl)")
            await self.db.levelsetting.create(data={"server_id": ctx.guild.id, "status": False,"level_up_channel_id":0,"level_up_channel_name":""})
            await db_disconnect()
            em = discord.Embed(
                title="CMD",
                description="No leveling settings found for this server!",
                color=discord.Color.red()
            )
            await ctx.guild.get_channel(int(ss.log_channel)).send(embed=em)
            await ctx.send(embed=em)
            return

        if lvldb.status == False:
            await db_disconnect()
            embed = discord.Embed(description="Leveling system is already disabled",color=self.Mcolor)
            await ctx.send(embed=embed)
        else:
            update = await self.db.levelsetting.update(where={"ID": lvldb.ID}, data={"status": False})
            await db_disconnect()
            em = discord.Embed(description="Leveling system has been disabled",color=self.Mcolor)
            await ctx.send(embed=em)

    @commands.hybrid_command(name="lvlrole",description="Set a role for a level")
    @commands.has_permissions(manage_roles=True)
    @commands.has_permissions(administrator=True)
    async def set_role(self, ctx: commands.Context, level: int, role: discord.Role):
        await db_connect(self)
        ss = await self.db.server.find_unique(where={"server_id": ctx.guild.id})
        lvldb = await self.db.levelsetting.find_unique(where={"server_id": ctx.guild.id})
        roledb = await self.db.levelrole.find_first(where={"server_id": ctx.guild.id, "role_id": role.id})
        if lvldb.status == False:
            await db_disconnect()
            em = discord.Embed(description="Leveling system is disabled plz emable it for this feature.",color=self.Mcolor)
            await ctx.send(embed=em)
            return
        if roledb != None:
            print("Role already exists")
            await db_disconnect()
            em = discord.Embed(description="Role already exists",color=self.Mcolor)
            await ctx.send(embed=em)
            return
        update = await self.db.levelrole.create(data={"server_id": ctx.guild.id, "role_id": role.id, "role_name": role.name, "level": level})
        print("Role set for {role} from {level}".format(
            role=role.name, level=level))
        em = discord.Embed(description=f"Role has been set for Level({level} to role `{role.name}`)",color=self.Mcolor)
        await db_disconnect()
        await ctx.send(embed=em)

    @commands.hybrid_command(name='rank', description='Check your rank')
    async def rank(self, ctx: commands.Context):
        await db_connect(self)
        server = await self.db.server.find_unique(where={"server_id": ctx.guild.id})
        lvl = await self.db.levelsetting.find_unique(where={"server_id": ctx.guild.id})
        if lvl.status == False:
            await db_disconnect()
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
        await db_disconnect()

    @commands.hybrid_command(name='lvlsys_set_channel', description='Set channel for level up messages')
    @commands.has_permissions(administrator=True)
    async def set_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        await db_connect(self)
        lvl = await self.db.levelsetting.find_unique(where={"server_id": ctx.guild.id})
        if lvl == None :
            em = discord.Embed(description="Leveling system table not found in database",color=self.Mcolor)
            await ctx.send(embed=em)
            await db_disconnect()
        if lvl.level_up_channel_id == channel.id:
            em = discord.Embed(description=f"Channel is already setted to `{channel.name}`", color=self.Mcolor)
            await ctx.send(embed=em)
            await db_disconnect()
        else:
            update = await self.db.levelsetting.update(where={"server_id": ctx.guild.id}, data={"level_up_channel_id": channel.id,"level_up_channel_name": channel.name})
            em = discord.Embed(description=f"Level system Channel has been set to `{channel.name}`",color=self.Mcolor)
            await db_disconnect()
            await ctx.send(embed=em)
            
    @commands.hybrid_command(name='reduse_level', description='Set status of level system')
    @commands.has_permissions(administrator=True)
    async def reduce_lvl(self, ctx: commands.Context,member:discord.Member,amount: int):
        '''
        Reduse Level of user. This also changes their xp to 0 so it matches the associated Level
        '''
        if amount <= 0:
            raise ctx.send('Parameter "amount" was less than or equal to zero. The minimum value is 1')
        
        await db_connect(self)
        md = await self.db.userslevel.find_first(where={"server_id": ctx.guild.id, "user_id": member.id})
        if md != None:
            if md.level >= MAX_LEVEL:
                    em = discord.Embed(description="Max xp reached",color=self.Mcolor)
                    await ctx.send(embed=em)
                    await db_disconnect()
                    return
            else:
                await self.db.userslevel.update(where={"ID": md.ID}, data={"xp": 0, "level":amount})
                await db_disconnect()
                em = discord.Embed(description=f"User {member.mention} has now `level {amount}`",color=self.Mcolor)
                await ctx.send(embed=em)
    
    @commands.hybrid_command(name='add_xp',description='Add xp to a user')
    @commands.has_permissions(administrator=True)
    async def add_xp(self, ctx: commands.Context,member:discord.Member,amount: int) -> None:
        """
        Give XP to a member. This also changes their level so it matches the associated XP
        """
        if amount <= 0:
            raise ctx.send('Parameter "amount" was less than or equal to zero. The minimum value is 1')
        
        await db_connect(self)
        md = await self.db.userslevel.find_first(where={"server_id": ctx.guild.id, "user_id": member.id})
        if md != None:
            if md.xp >= MAX_XP:
                em = discord.Embed(description="Max xp reached",color=self.Mcolor)
                await ctx.send(embed=em)
                await db_disconnect()
                return
            else:
                new_total_xp = md.xp + amount
                new_total_xp = new_total_xp if new_total_xp <= MAX_XP else MAX_XP
                
                if new_total_xp in LEVELS_AND_XP.values():
                    for level, xp_needed in LEVELS_AND_XP.items():
                        if new_total_xp == xp_needed:
                            maybe_new_level = int(level)
                else:
                    for level, xp_needed in LEVELS_AND_XP.items():
                        if 0 <= new_total_xp <= xp_needed:
                            level = int(level)
                            level -= 1
                            if level < 0:
                                level = 0
                            maybe_new_level = level
                            new_total_xp = 0
                            break
                
                update = await self.db.userslevel.update(where={"ID": md.ID}, data={"xp": new_total_xp, "level":maybe_new_level})
                await db_disconnect()
                em = discord.Embed(description=f"User {member.mention} has been given `{amount}` xp and is now level `{maybe_new_level}`",color=self.Mcolor)
                await ctx.send(embed=em)
      
    @commands.hybrid_command(name='set_no_xp_role',description='role with this user will not gain XP')
    @commands.has_permissions(administrator=True)
    async def add_no_xp_role(self, ctx: commands.Context,role:discord.Role):
        '''
        Set role with this user will not gain XP
        '''
        await db_connect(self)
        DB = await self.db.noxprole.find_first(where={"server_id":ctx.guild.id, "role_id": role})
        if DB == None:
            await self.db.noxprole.create(data={"server_id": ctx.guild.id, "role_id": role, "role_name": role.name})
            await self.db.disconnect()
            embed = discord.Embed(description=f"Role {role.name} added to no xp role list", color=self.Mcolor)
            await ctx.send(embed=embed)        
        else:
            await db_disconnect()
            ctx.send(f"Role {role.name} already in no xp role list")
    
    @commands.hybrid_command(name='remove_no_xp_role',description='remove role from no xp role list')
    @commands.has_permissions(administrator=True)
    async def remove_no_xp_role(self, ctx: commands.Context,role:discord.Role):
        '''
        Remove role from no xp role list
        '''
        await db_connect(self)
        DB = await self.db.noxprole.find_first(where={"server_id":ctx.guild.id, "role_id": role})
        if DB == None:
            await db_disconnect()
            ctx.send(f"Role {role.name} not in no xp role list")
        else:
            await self.db.noxprole.delete(where={"ID": DB.ID})
            await db_disconnect()
            ctx.send(f"Role {role.name} removed from no xp role list")
    
    @commands.hybrid_command(name='add_no_xp-channel',description='In this channel user will not gain XP')
    @commands.has_permissions(administrator=True)
    async def add_no_xp_channel(self, ctx: commands.Context,channel:discord.TextChannel):
        '''
        Set channel with this user will not gain XP
        '''
        await db_connect(self)
        DB = await self.db.noxpchannel.find_first(where={"server_id":ctx.guild.id, "channel_id": channel.id})
        if DB == None:
            await self.db.noxpchannel.create(data={"server_id": ctx.guild.id, "channel_id": channel.id, "channel_name": channel.name})
            await self.db.disconnect()
            embed = discord.Embed(description=f"Channel {channel.name} added to on xp channel list", color=self.Mcolor)
            await ctx.send(embed=embed)
        else:
            await db_disconnect()
            ctx.send(f"Channel {channel.name} already in on xp channel list")

    @commands.hybrid_command(name='remove_no_xp_channel',description='remove channel from no xp channel list')
    @commands.has_permissions(administrator=True)
    async def remove_no_xp_channel(self, ctx: commands.Context,channel:discord.TextChannel):
        '''
        Remove channel from no xp channel list
        '''
        await db_connect(self)
        DB = await self.db.noxpchannel.find_first(where={"server_id":ctx.guild.id, "channel_id": channel.id})
        if DB == None:
            await db_disconnect()
            ctx.send(f"Channel {channel.name} not in no xp channel list")
        else:
            await self.db.noxpchannel.delete(where={"ID": DB.ID})
            await db_disconnect()
            ctx.send(f"Channel {channel.name} removed from no xp channel list")

async def setup(bot: commands.Bot):
    await bot.add_cog(Level_System(bot))

class MemberGuildInfo:
    """Helper class for :class:`AnnouncementMember`
    
        .. added:: v1.1.0 (moved from :class:`AnnouncementMember`, was just :class:`Guild`)
    """
    icon_url: ClassVar[str] = '[$g_icon_url]'
    id: ClassVar[str] = '[$g_id]'
    name: ClassVar[str] = '[$g_name]'

class MemberInfo:
    """Helper class for :class:`LevelUpAnnouncement`
    
        .. added:: v0.0.2
        .. changes::
            v1.1.0
                Replaced the guild class. Added it as a variable instead (Guild class is now separate)
                Added :attr:`display_avatar_url`
                Added :attr:`banner_url`
    """
    avatar_url: ClassVar[str] = '[$avatar_url]'
    banner_url: ClassVar[str] = '[$banner_url]'
    created_at: ClassVar[str] = '[$created_at]'
    default_avatar_url: ClassVar[str] = '[$default_avatar_url]'
    discriminator: ClassVar[str] = '[$discriminator]'
    display_avatar_url: ClassVar[str] = '[$display_avatar_url]' # Guild avatar if they have one set
    display_name: ClassVar[str] = '[$display_name]'
    id: ClassVar[str] = '[$id]'
    joined_at: ClassVar[str] = '[$joined_at]'
    mention: ClassVar[str] = '[$mention]'
    name: ClassVar[str] = '[$name]'
    nick: ClassVar[str] = '[$nick]'
    
    Guild: ClassVar[MemberGuildInfo] = MemberGuildInfo()


'''TO-DO
-add no xp role 
-add no xp channel 
-add no_xp_role api/cmd
-add no_xp_channel api/cmd
- stack_awards(If this is True, when the member levels up the assigned role award will be applied. If False, the previous role award will be removed and the level up assigned role will also be applied)
-announce_level_up(If True, level up messages will be sent when a member levels up)
'''