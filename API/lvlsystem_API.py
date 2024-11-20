from fastapi import APIRouter,HTTPException
from database.connection import *
from cogs import lvlsystem

router = APIRouter( 
                    prefix="/Level system",
                    tags=["Level system"],
                    responses={404: {"description": ""}},
                    )
from discord.ext import commands
bot = commands.bot
# ----------------------------LEVEL SYSTEM----------------------------------------
# @router.post("/LVLsystem_status/",dependencies=[Depends(check_api_key)])

@router.post("/LVLsystem_status/", tags=["Level system"])
async def LVLsystem_status(guild: int, status: bool):
    Guild = bot.get_guild(guild)
    if Guild:
        await db_connect1()
        lvl = await db.levelsetting.find_unique(where={"server_id": guild})
        if lvl == None:
            cr = await db.levelsetting.create(data={"server_id": guild, "status": status,"level_up_channel_id":0,"level_up_channel_name":""})
            await db_disconnect()
            return {"message": f"Level system status created and set to |**{status}**|"}
        else: 
            up = await db.levelsetting.update(where={"ID":lvl.ID},data= {"status": status})
            await db_disconnect()
            return {"message": f"Level system status set to |**{status}**|"}
    else:
        return f"{guild} is not a valid server id"

# @router.post("/LVLsystem_status/",dependencies=[Depends(check_api_key)])
@router.post("/LVL_role_set/", tags=["Level system"])
async def LVL_role_set(guild: int, role: int, lvl: int):
    Guild = bot.get_guild(guild)
    if Guild:
        for rol in Guild.roles:
            if rol.id == role:
                await db_connect1()
                lvls = await db.levelrole.find_first(where={"server_id": guild, "level": lvl})
                if lvls == None:
                    dd = {
                        "level": lvl, 
                        "role_id":rol.id,
                        "role_name":rol.name,
                        "server_id": guild
                            }
                    print(dd)
                    cr = await db.levelrole.create(data={"level": lvl, "role_id":rol.id,"role_name":rol.name,"server_id": guild})
                    print(cr)
                    await db_disconnect()
                    return {"message": f"Level role created for |**{rol.name}**| to  Level({lvl})"}
                else:
                    up = await db.levelrole.update(where={"ID":lvl.ID},data= {"role_id": role, "role_name":rol.name})
                    await db_disconnect()
                    return {"message":f"Level role updated for |**{rol.name} to  Level({lvl})"}
        return {"message": f"Level role set to |**{rol.name}**|**{rol.id})**|"}
    else:
        return f"{guild} is not a valid server id"

# @router.post("/LVL_set_channel/",dependencies=[Depends(check_api_key)])
@router.post("/LVL_set_channel/", tags=["Level system"])
async def LVL_set_channel(guild: int, channel:int):
    Guild = bot.get_guild(guild)
    if Guild:
        await db.connect()
        lvl = await db.levelsetting.find_unique(where={"server_id": guild})
        if lvl == None :
            await db.disconnect()
            return {"message": f"Level setting not found in database"}                
            
        if lvl.level_up_channel_id == channel.id:
            await db.disconnect()
            return {"message": f"Level up channel already set to {channel.name}"}
        else:
            update = await db.levelsetting.update(where={"ID": lvl.ID},data={"level_up_channel_id": channel.id,"level_up_channel_name": channel.name})
            await db.disconnect()
            return {"message": f"Level up channel set to {channel.name}"}
    else:
        return f"{guild} is not a valid server id"

# @router.post("add_xp",dependencies=[Depends(check_api_key)])
@router.post("/add_xp", tags=["Level system"])
async def add_xp(guild: int, user: int, xp: int):
    Guild = bot.get_guild(guild)
    if Guild:
        amount = xp
        if amount <= 0:
            return ({"message":'Parameter "amount" was less than or equal to zero. The minimum value is 1'})
        await db_connect1()
        userdb = await db.userslevel.find_first(where={"server_id": guild, "user_id": user})
        if userdb == None:
            await db_disconnect()
            return HTTPException(status_code=404 , detail = f"User not found in database")
        else:
            
            if userdb.xp >= lvlsystem.MAX_XP:
                print("Max xp reached")
                await db_disconnect()
                return
            else:
                    new_total_xp = userdb.xp + amount
                    new_total_xp = new_total_xp if new_total_xp <= lvlsystem.MAX_XP else lvlsystem.MAX_XP
                    if new_total_xp in lvlsystem.LEVELS_AND_XP.values():
                        for level, xp_needed in lvlsystem.LEVELS_AND_XP.items():
                            if new_total_xp == xp_needed:
                                maybe_new_level = int(level)
                    else:
                        for level, xp_needed in lvlsystem.LEVELS_AND_XP.items():
                            if 0 <= new_total_xp <= xp_needed:
                                level = int(level)
                                level -= 1
                                if level < 0:
                                    level = 0
                                maybe_new_level = level
                                break
                    
                    update = await db.userslevel.update(where={"ID": userdb.ID}, data={"xp": new_total_xp, "level":maybe_new_level})
                    await db_disconnect()
                    return ({"message": f"User {user} has {new_total_xp} xp and is now level {maybe_new_level}"})

# @router.post("/remove_level",dependencies=[Depends(check_api_key)])
@router.post("/remove_level", tags=["Level system"])
async def remove_level(guild: int, user: int, level: int):
    Guild = bot.get_guild(guild)
    if Guild:
        amount = level
        if amount <= 0:
            return ({"message":'Parameter "Level" was less than or equal to zero. The minimum value is 1'})
        await db_connect1()
        userdb = await db.userslevel.find_first(where={"server_id": guild, "user_id": user})
        if userdb == None:
            await db_disconnect()
            return HTTPException(status_code=404 , detail = f"User not found in database")
        else:
            if userdb.level >= lvlsystem.MAX_LEVEL:
                await db_disconnect()
                return ({"message": f"Max xp reached"})
            else:
                await db.userslevel.update(where={"ID": userdb.ID}, data={"xp": 0, "level":amount})
                await db_disconnect()
                return ({"message": f"User {user} has {userdb.xp} xp and is now level {userdb.level}"})
    
    else:
        return HTTPException(status_code=404, detail=f"{guild} is not a valid server id")  

# @router.post("/remove_no_xp_role",dependencies=[Depends(check_api_key)])
@router.post("/remove_no_xp_role", tags=["Level system"])
async def remove_no_xp_role(guild: int, role: int):
    Guild = bot.get_guild(guild)
    if Guild:
        await db.connect()
        no_xp_role_db = await db.noxprole.find_first(where={"server_id": guild, "role_id": role})
        if no_xp_role_db == None:
            await db.disconnect()
            return HTTPException(status_code=404 , detail = f"Role not found in database")
        else:
            await db.noxprole.delete(where={"ID": no_xp_role_db.ID})
            await db.disconnect()
            return {"message": f"Role {role} removed from no xp role list"}

# @router.post("/add_no_xp_role",dependencies=[Depends(check_api_key)])
@router.post("/add_no_xp_role", tags=["Level system"])
async def add_no_xp_role(guild: int, role: int):
    Guild = bot.get_guild(guild)
    if Guild:
        rolle = Guild.get_role(role)
        await db.connect()
        DB = await db.noxprole.find_first(where={"server_id": guild, "role_id": role})
        if DB == None:
            await db.noxprole.create(data={"server_id": guild, "role_id": role, "role_name": rolle.name})
            await db.disconnect()
            return ({"message": f"Role {role} added to no xp role list"})
        else:
            await db.disconnect()
            return {"message": f"Role {role} already in no xp role list"}
    else:
        return HTTPException(status_code=404, detail=f"{guild} is not a valid server id")

# @router.post("/remove_no_xp_role",tags = ["Level system"])
@router.post("/remove_no_xp_role", tags=["Level system"])
async def remove_no_xp_rolez(guild: int, role: int):
    Guild = bot.get_guild(guild)
    
    if Guild:
        await db.connect()
        DB = await db.noxprole.find_first(where={"server_id": guild, "role_id": role})
        if DB == None:
            await db.disconnect()
            return ({"message": f"Role {role} not found in database"})
        else:
            await db.noxprole.delete(where={"ID": DB.ID})
            await db.disconnect()
            return {"message": f"Role {role} already in no xp role list"}
    else:
        return HTTPException(status_code=404, detail=f"{guild} is not a valid server id")

@router.post("/add_noxpchannel", tags=["Level system"])
async def add_noxpchannel(guild: int, channel: int):
    Guild = bot.get_guild(guild)
    if Guild:
        chann = Guild.get_channel(channel)
        await db.connect()
        DB = await db.noxpchannel.find_first(where={"server_id": guild, "channel_id": channel})
        if DB == None:
            await db.noxpchannel.create(data={"server_id": guild, "channel_id": channel, "channel_name": chann.name})
            await db.disconnect()
            return ({"message": f"Channel {channel} added to no xp channel list"})
        else:
            await db.disconnect()
            return {"message": f"Channel {channel} already in no xp channel list"}
    else:
        return HTTPException(status_code=404, detail=f"{guild} is not a valid server id")

# @router.post("/remove_noxpchannel",tags = ["Level system"])
@router.post("/remove_noxpchannel", tags=["Level system"])
async def remove_noxpchannel(guild: int, channel: int):
    Guild = bot.get_guild(guild)
    if Guild:
        await db.connect()
        DB = await db.noxpchannel.find_first(where={"server_id": guild, "channel_id": channel})
        if DB == None:
            await db.disconnect()
            return ({"message": f"Channel {channel} not found in database"})
        else:
            await db.noxpchannel.delete(where={"ID": DB.ID})
            await db.disconnect()
            return {"message": f"Channel {channel} already in no xp channel list"}
    else:
        return HTTPException(status_code=404, detail=f"{guild} is not a valid server id")

# --------------------------------------------------------------------------------