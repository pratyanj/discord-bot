from fastapi import APIRouter,HTTPException
from database.connection import db_connect, db_disconnect,db
from main import bot
router = APIRouter( 
                    prefix="/youtube",
                    tags=["youtube"],
                    responses={404: {"description": ""}},
                    )


# --------------------------------------------------------------------------------
# ----------------------------YOUTUBE-------------------------------------------
@router.get("/GET_YT_SUB_channels_lst/", tags=["youtube"])
async def GET_YT_SUB_channels_lst(guild: int):
    await db_connect()
    Guild = bot.get_guild(guild)
    guild = await db.youtubesubchannel.find_many(where={"server_id": guild})
    await db_disconnect()
    if Guild:
        if guild != None:
            lst = []
            for i in guild:
                lst.append(i.channel)

            return lst
        else:
            return HTTPException(status_code=404, detail=f"{guild} not found in database")
    else:
        return HTTPException(status_code=404, detail=f"{guild} is not a valid server id")

# @app.post("/youtube_notification_status/",dependencies=[Depends(check_api_key)])
@router.post("/youtube_system_status/", tags=["youtube"])
async def youtube_system_status(guild: int, status: bool):
    Guild = bot.get_guild(guild)
    if Guild:
        await db_connect()
        yt = await db.youtubesetting.find_unique(where={"server_id": guild})
        if yt == None:
            cr = await db.youtubesetting.create(data={"server_id": guild, "status": status,"channel_id":0,"channel_name":""})
            await db_disconnect()
            return {"message": f"Youtube notification status created and set to |**{status}**|"}
        else:
            up = await db.youtubesetting.update(where={"ID":yt.ID},data= {"status": status})
            await db_disconnect()
            return {"message": f"Youtube notification status set to |**{status}**|"}
    else:
        return HTTPException(status_code=404, detail=f"{guild} is not a valid server id")

# @app.post("/youtube_notification/",dependencies=[Depends(check_api_key)])
@router.post("/youtube_notification/", tags=["youtube"])
async def youtube_video_bot_channel_setup(guild: int, channel: int):
    Guild = bot.get_guild(guild)
    if Guild:
        Channel = bot.get_channel(channel)
        if Channel:
            await db_connect()
            yt= await db.youtubesetting.find_unique(where={"server_id": guild})
            if yt == None:
                cr = await db.youtubesetting.create(data={"server_id": guild, "status": True,"channel_id":Channel.id,"channel_name":Channel.name,})
                await db_disconnect()
                return {"message": f" Youtube notification created and set to |**{Channel.name}**|**({Channel.id})**|"}
            else:
                up = await db.youtubesetting.update(where={"ID":yt.ID},data= {"channel_id": Channel.id,"channel_name":Channel.name})
                await db_disconnect()
                return {"message": f" Youtube notification set to |**{Channel.name}**|**({Channel.id})**|"}
        
        else:
            return f"{channel} is not a valid channel id"
    else:
        return f"{guild} is not a valid server id"

# @app.post("/Set_YT_channel/",dependencies=[Depends(check_api_key)])
@router.post("/Set_YT_channel/", tags=["youtube"])
async def subscribe_youtube_channel_by_name(guild: int, YT_channel_usr: str):
    Guild = bot.get_guild(guild)
    if Guild:
        data_set = {"youtube_channels": [YT_channel_usr]}
        await db_connect()
        yt_channels = await db.youtubesubchannel.find_many(where={"server_id": guild})
        for i in yt_channels:
            if i.channel == YT_channel_usr:
                await db_disconnect()
                return {"message": f"Youtube notification is already set to |**{YT_channel_usr}**|"}
        cr = await db.youtubesubchannel.create(data={"server_id": guild, "channel": YT_channel_usr})
        await db_disconnect()
        return {"message": f" Youtube notification set for |**{YT_channel_usr}**|"}

    else:
        return f"{guild} is not a valid server id"

# @app.post("/remove_YT_channel/",dependencies=[Depends(check_api_key)])
@router.post("/remove_YT_channel/", tags=["youtube"])
async def remove_YT_channel(guild: int, YT_channel_usr: str):
    Guild = bot.get_guild(guild)
    if Guild:
        await db_connect()
        try:
            yt = await db.youtubesubchannel.find_first(where={"server_id": guild,"channel": YT_channel_usr})
            await db.youtubesubchannel.delete(where={"ID":yt.ID})
            await db_disconnect()
            return {"message": f" Youtube channel ubsubscribe removed for |**{YT_channel_usr}**|"}
        except:
            yt = await db.youtubesetting.find_many(where={"server_id": guild})
            for i in yt:
                if i.channel_id == YT_channel_usr:
                    await db.youtubesubchannel.delete(where={"server":guild,"channel": YT_channel_usr})
                    await db_disconnect()
                    return {"message": f" Youtube notification is already removed for |**{YT_channel_usr}**|"}
        
    else:
        return f"{guild} is not a valid server id"
# ----------------------------YOUTUBE-------------------------------------------
# --------------------------------------------------------------------------------