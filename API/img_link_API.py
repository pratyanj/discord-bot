from fastapi import APIRouter,HTTPException
from database.connection import *
from discord.ext import commands
bot = commands.bot

router = APIRouter( 
                    prefix="/img_link",
                    tags=["img_link"],
                    responses={404: {"description": ""}},
)

# -----------------------Img / Link ------------------------------
# @router.get("/Image_channel_lst/",dependencies=[Depends(check_api_key)])
@router.get("/Image_channel_lst", tags=["img_link"])
async def Image_channel_lst(guild: int):
    Guild = bot.get_guild(guild)
    if Guild:
        data = {}
        await db_connect1()
        img = await db.imagesonly.find_many(where={"server_id": guild})
        await db_disconnect()
        if img != None:
            for i in img:
                data.update({i.channel_name: i.channel_id})
            return data
        else:
            return data
    else:
        return HTTPException(status_code=404, detail=f"{guild} is not a valid server id or not found in database")

# @router.post("/add_img_chhannel/",dependencies=[Depends(check_api_key)])
@router.post("/add_img_chhannel", tags=["img_link"])
async def add_img_chhannel(guild: int, channel_id: int):
    Guild = bot.get_guild(guild)
    if Guild:
        channel_ids = bot.get_channel(int(channel_id))
        if channel_ids:
            await db_connect1()
            img_update = await db.imagesonly.create(data={"server_id": guild, "channel_name": channel_ids.name, "channel_id": channel_ids.id})
            await db_disconnect()
            print(img_update)
            return {"message": f"Channel |**{channel_ids.name}**| with id |**{channel_ids.id}**| added successfully"}
        else:
            return HTTPException(status_code=404, detail=f"{channel_id} is not a valid channel id")
    else:
        return HTTPException(status_code=404, detail=f"{guild} not found in database")

# @router.post("/remove_img_channel/",dependencies=[Depends(check_api_key)])
@router.post("/remove_img_channel", tags=["img_link"])
async def remove_img_channel(guild: int, channel_id: int):
    Guild = bot.get_guild(guild)
    if Guild:
        channel_ids = bot.get_channel(int(channel_id))
        if channel_ids:
            await db_connect1()
            img = await db.imagesonly.find_first(where={"server_id": guild, "channel_id": channel_ids.id})
            img_update = await db.imagesonly.delete(where={"ID": img.ID})
            await db_disconnect()
            return {"message": f"Channel |**{channel_ids.name}**| with id |**{channel_ids.id}**| removed successfully"}
        else:
            return HTTPException(status_code=404, detail=f"{channel_id} is not a valid channel id")
    else:
        return HTTPException(status_code=404, detail=f"{guild} not found in database")

# @router.get("/Link_channel_lst/",dependencies=[Depends(check_api_key)])
@router.get("/Link_channel_lst", tags=["img_link"])
async def Link_channel_lst(guild: int):
    Guild = bot.get_guild(guild)
    if Guild:
        data = {}
        await db_connect1()
        link = await db.linksonly.find_first(where={"server_id": guild})
        await db_disconnect()
        if link != None:
            for i in link:
                data.update({i.channel_name: i.channel_id})
            return data
        else:
            return data
    else:
        return HTTPException(status_code=404, detail=f"{guild} is not a valid server id or not found in database")

# @router.post("/add_link_chhannel/",dependencies=[Depends(check_api_key)])
@router.post("/remove_link_channel", tags=["img_link"])
async def remove_link_channel(guild: int, channel_id: int):
    Guild = bot.get_guild(guild)
    if Guild:
        channel_ids = bot.get_channel(int(channel_id))
        if channel_ids:
            await db_connect1()
            link = await db.linksonly.find_first(where={"server_id": guild, "channel_id": channel_ids.id})
            rm = await db.linksonly.delete(where={"ID": link.ID})
            await db_disconnect()
            return {"message": f"Channel |**{channel_ids.name}**| with id |**{channel_ids.id}**| removed successfully"}
        else:
            return HTTPException(status_code=404, detail=f"{channel_id} is not a valid channel id")
    else:
        return HTTPException(status_code=404, detail=f"{guild} not found in database")

# @router.post("/remove_link_channel/",dependencies=[Depends(check_api_key)])
@router.post("/add_link_chhannel", tags=["img_link"])
async def add_link_chhannel(guild: int, channel_id: int,):
    Guild = bot.get_guild(guild)
    if Guild:
        channel_ids = bot.get_channel(int(channel_id))
        if channel_ids:
            await db_connect1()
            update = await db.linksonly.create(data={"server_id": guild, "channel_name": channel_ids.name, "channel_id": channel_ids.id})
            print("add_link_chhannel:", update)
            await db_disconnect()
            return {"message": f"Channel |**{channel_ids.name}**| with id |**{channel_ids.id}**| added successfully"}
        else:
            return HTTPException(status_code=404, detail=f"|**{channel_id}**| is not a valid channel id")
    else:
        return HTTPException(status_code=404, detail=f"{guild} not found in database")

# -----------------------Img / Link ------------------------------