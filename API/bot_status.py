from fastapi import APIRouter,HTTPException
from database.connection import db_connect, db_disconnect,db
from discord.ext import commands
bot = commands.bot

router = APIRouter( 
                    prefix="/bot status",
                    tags=["bot status"],
                    responses={404: {"description": ""}},
                    )

# ------------------------------------------------------------
# @router.post("/link_channel_switch/",dependencies=[Depends(check_api_key)])
@router.post("/link_channel_status/", tags=["bot status"])
async def link_channel_switch(guild: int, status: bool):
    Guild = bot.get_guild(guild)
    if Guild:
        await db_connect()
        link = await db.status.find_unique(where={"server_id": guild})
        if link == None:
            cr = await db.status.create(data={"server_id": guild, "IMAGES_ONLY": False, "LINKS_ONLY":status})
            await db_disconnect()
            return {"status": f"Link channel status created and set to |**{status}**|"}
        else:
            up = await db.status.update(where={"ID":link.ID},data= {"LINKS_ONLY": status})
            await db_disconnect()
            return {"message": f"Link channel status set to |**{status}**|"}
    else:
        return f"{guild} is not a valid server id"

# @router.post("/IMG_channel_switch/",dependencies=[Depends(check_api_key)])
@router.post("/IMG_channel_status/", tags=["bot status"])
async def IMG_channel_switch(guild: int, status: bool):
    Guild = bot.get_guild(guild)
    if Guild:
        await db_connect()
        link = await db.status.find_unique(where={"server_id": guild})
        if link == None:
            cr = await db.status.create(data={"server_id": guild, "IMAGES_ONLY": status, "LINKS_ONLY":False})
            await db_disconnect()
            return {"message": f"Image channel status created and set to |**{status}**|"}
        else:
            up = await db.status.update(where={"ID":link.ID},data= {"IMAGES_ONLY": status})
            await db_disconnect()
            return {"message": f"Image channel status set to |**{status}**|"}    
    else:
        return HTTPException(status_code=404, detail=f"{guild} is not a valid server id")

# server welcome message
# @router.post("/welcome_status/",dependencies=[Depends(check_api_key)])
@router.post("/welcome_status/", tags=["bot status"])
async def welcome_status(guild: int, status: bool):
    Guild = bot.get_guild(guild)
    if Guild:
        await db_connect()
        welcome = await db.welcome.find_unique(where={"server_id": guild})
        if welcome == None:
            cr = await db.welcome.create(data={"server_id": guild, "channel_id": 0, "channel_name": "", "message": "", "status": False})
            await db_disconnect()
            return {"message": f"Welcome status created and set to |**{status}**|"}
        else:
            up = await db.welcome.update(where={"ID":welcome.ID},data= {"status": status})
            await db_disconnect()
            return {"message": f"Welcome status set to |**{status}**|"}
    else:
        return HTTPException(status_code=404, detail=f"{guild} is not a valid server id")

@router.post("/leave_status/", tags=["bot status"])
async def leave_status(guild: int, status: bool):
    Guild = bot.get_guild(guild)
    if Guild:
        await db_connect()
        leave = await db.goodbye.find_unique(where={"server_id": guild})
        if leave == None:
            cr = await db.goodbye.create(data={"server_id": guild, "channel_id": 0, "channel_name": "", "message": "", "status": False})
            await db_disconnect()
            return {"message": f"Leave status set to |**{status}**|"}
        else:
            up = await db.goodbye.update(where={"ID":leave.ID},data= {"status": status})
            await db_disconnect()
            return {"message": f"Leave status set to |**{status}**|"}
    else:
        return f"{guild} is not a valid server id"
# --------------------------------------------------------------------------------