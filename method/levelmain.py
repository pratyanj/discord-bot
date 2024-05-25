import discord
from discord.ext import commands
import os
import random
from prisma import Prisma
db = Prisma()

async def level_on_message(message:discord.Message):
    await db.connect()
    ss = await db.server.find_unique(where={"server_id":message.guild.id})
    log = message.guild.get_channel(ss.log_channel)
    if log is None:
        print(f"Channel with ID {ss.log_channel} not found.")
        await db.disconnect()
        return
    if ss == None:
        await db.disconnect()
        print("No server found")
        return
    if ss.prefix in message.content or message.author.bot :
        await db.disconnect()
        # print("Message is a command or a bot")
        return
    author = message.author
    guild = message.guild
    print("user:",author)
    print("Server_name:",guild)
    user = await db.userslevel.find_first(where={"user_id":author.id,"server_id":message.guild.id})
    print(f"user lvl data:\n{user}")
    sys = await db.levelsetting.find_unique(where={"server_id":message.guild.id})
    print(f"Lvl system:\n{sys}")
    if sys == None:
        create_sys = await db.levelsetting.create(data={"server_id":message.guild.id,"status":True,"level_up_channel_id":0,"level_up_channel_name":''})
        embed = discord.Embed(title="Level System", description=f"A new level system has been created for {message.guild.name}", color=discord.Color.green())
        await log.send(embed=embed)
        await db.disconnect()
        return
    
    if user == None:
        create_user = await db.userslevel.create(data={"server_id":message.guild.id,"user_id":author.id,"user_name":author.name,"level":0,"xp":1})
        await log.send(f"New user add to lvl system:{author.id}")
        await db.disconnect()
        # print(f"New member add to lvl system:{author.id}")
        return
    
    if sys.status == False:
        # print("Level system is off")
        # print(f"serverlogchannel:{ss.log_channel}")
        embed = discord.Embed(title="Level system",description=f"Level system is off",color=discord.Color.green())
        await log.send(embed=embed)
        await db.disconnect()
        # print("Level system is off")
        return
    
    try:
        xp = int(user.xp)
        level = int(user.level)
    except:
        xp = 0
        level = 0
                
    if level <5:
        print("Level is less than 5")
        xp += random.randint(1,5)
        await db.userslevel.update(where={"ID":user.ID},data={"xp":xp})
        await db.disconnect()
    else:
        print("Level is more than 5")
        rand= random.randint(1,(level//2))
        print(rand)
        if rand == 1:
            xp += random.randint(1,3)
            print(f"xp is increased to {xp}")
            await db.userslevel.update(where={"ID":user.ID},data={"xp":xp})
            await db.disconnect()
    print(f"XP: {xp}, Level: {level}")
                    
    if xp >= 100:
        await db.connect()
        level += 1
        await db.userslevel.update(where={"ID":user.ID},data={"level":level,"xp":0})
        msg = f"{author.mention} leveled up to {level}"
        print('msg:',msg)
        dataa = await db.levelrole.find_many(where={"server_id":message.guild.id})
        await db.disconnect()
        if len(dataa) == 0 or dataa == None:
            return
        for i in dataa:
            if int(i.level) == level:
                role = guild.get_role(int(i.role_id))
                try:
                    await author.add_roles(role)
                    await message.channel.send(f'🏆{author.mention} has just level upto **{level}** and reworded with {role.name}✨')
                    return
                except discord.HTTPException:
                    await message.channel.send(f'{author.mention} I couldn\'t add the role {role.name} to you.')
        await message.channel.send(f'{msg}')
            
        
    