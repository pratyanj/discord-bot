from fastapi import APIRouter,HTTPException
from database.connection import db_connect, db_disconnect,db
from discord.ext import commands
bot = commands.bot

router = APIRouter( 
                    prefix="/welcome_leave",
                    tags=["welcome_leave"],
                    responses={404: {"description": ""}},
)
# ------------------------welcome_leave------------------------
# @router.post("/welcome_message/",dependencies=[Depends(check_api_key)])
@router.post("/welcome_message/", tags=["welcome_leave"])
async def welcome_message(guild: int, message: str):
    Guild = bot.get_guild(guild)
    if Guild:
        await db_connect()
        welcome = await db.welcome.find_unique(where={"server_id": guild})
        if welcome == None:
            update = await db.welcome.create(data={"server_id": guild, "message": message})
            await db_disconnect()
            return {"message": f"Welcome message set to |**{message}**|"}
        else:
            up = await db.welcome.update(where={"ID":welcome.ID},data= {"message":message})
            await db_disconnect()
            return {"message": f"Welcome message set to |**{message}**|"}
    else:
        return {"message": f"{guild} is not a valid server id"}  

# @router.post("/leave_message/",dependencies=[Depends(check_api_key)])
@router.post("/leave_message/", tags=["welcome_leave"])
async def leave_message(guild: int, message: str):
    Guild = bot.get_guild(guild)
    if Guild:
        await db_connect()
        leave = await db.goodbye.find_first(where={"server_id": guild})
        if leave == None:
            cr = await db.goodbye.create(data={"server_id": guild,"channel_id":0,"channel_name":'',"status":True,"message": message})
            await db_disconnect()
            return {"message": f"leave message set to |**{message}**|"}
        else:
            up = await db.goodbye.update(where={"ID":leave.ID},data= {"message":message})
            await db_disconnect()
            return {"message": f"leave message set to |**{message}**|"}
    else:
        return {"message": f"{guild} is not a valid server id"}
    
# @router.post("/welcome_channel_set/",dependencies=[Depends(check_api_key)])
@router.post("/welcome_channel_set/", tags=["welcome_leave"])
async def welcome_channel_set(guild: int, channel: int):
    Guild = bot.get_guild(guild)
    if Guild:
        for chann in Guild.channels:
            if chann.id == channel:
                await db_connect()
                doc_ref = await db.welcome.find_first(where={"server_id": guild})
                if doc_ref is None:
                    cr = await db.welcome.create(data={"server_id": guild, "channel_id": channel, "channel_name": chann.name,"message":"","status":False})
                    await db_disconnect()
                    return {"message": f"Welcome channel created and set to |**{chann.name}**||**{chann.id}**|"}
                else:
                    up = await db.welcome.update(where={"ID":doc_ref.ID},data= {"channel_id": channel, "channel_name": chann.name})
                    await db_disconnect()
                    return {"message": f"Welcome channel set to |**{chann.name}**||**{chann.id}**|"}
                    
        return {'message': f'{channel}Channel not fount'}
    else:
        return {"message":f"{guild} is not a valid server id"}

# @router.post("/leave_channel_set/",dependencies=[Depends(check_api_key)])
@router.post("/leave_channel_set/", tags=["welcome_leave"])
async def leave_channel_set(guild: int, channel: int):
    Guild = bot.get_guild(guild)
    if Guild:
        for chann in Guild.channels:
            if chann.id == channel:
                await db_connect()
                leave = await db.goodbye.find_first(where={"server_id": guild})
                if leave == None:
                    cr = await db.goodbye.create(data={"server_id": guild, "channel_id": channel, "channel_name": chann.name,"message":"","status":False})
                    await db_disconnect()
                    return {"message": f"Leave channel created and set to |**{chann.name}**||**{chann.id}**|"}
                else:
                    up = await db.goodbye.update(where={"ID":leave.ID},data= {"channel_id": channel, "channel_name": chann.name})
                    await db_disconnect()
                    return {"message": f"Leave channel set to |**{chann.name}**||**{chann.id}**|"}

        return {'message': f'{channel}Channel not fount'}
    else:
        return {"message":f"{guild} is not a valid server id"}

# ------------------------WELCOME_LEAVE------------------------