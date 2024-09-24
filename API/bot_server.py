from fastapi import APIRouter,HTTPException
from database.connection import db_connect, db_disconnect,db
from discord.ext import commands
bot = commands.bot
import discord

router = APIRouter( 
                    prefix="/bot_server",
                    tags=["bot_server"],
                    responses={404: {"description": ""}},
                    )

    # List of server
    # @router.get("/server_List/",dependencies=[Depends(check_api_key)])
@router.get("/server_List/", tags=["bot sevrver"])
async def server_List():
    servers = {"ServerList": []}
    for guild in bot.guilds:
        # print(guild.id)
        # servers[guild.name] = guild.id
        server_info = {
            "name": str(guild.name),
            "id": str(guild.id),
            "icon_url": str(guild.icon)
        }
        servers["ServerList"].routerend(server_info)
        # servers[guild.name] = server_info
        # print(servers)
    return servers

# List of channenels according to server id
# @router.get("/server_Channels_List/{guild}",dependencies=[Depends(check_api_key)])
@router.get("/server_Channels_List/", tags=["bot sevrver"])
async def server_Channels_List(guild: int):
    channelList = {}
    Guild = bot.get_guild(guild)
    for channel in Guild.channels:
        if isinstance(channel, discord.TextChannel):
            channelList[channel.name] = str(channel.id)
    return channelList

# List of roles according to server id
# @router.get("/server_Roles_List/",dependencies=[Depends(check_api_key)])
@router.get("/server_Roles_List/", tags=["bot sevrver"])
async def server_Roles_List(guild: int):
    Roles_List = {}
    Guild = bot.get_guild(guild)
    if Guild:
        for role in Guild.roles:
            Roles_List[role.name] = str(role.id)
        return Roles_List
    else:
        return f"{guild} is not a valid server id"
        # @router.post("/welcome_status_GET/",dependencies=[Depends(check_api_key)])

# Server all status
# @router.get("/GET_status/",dependencies=[Depends(check_api_key)])
@router.get("/GET_status/", tags=["bot sevrver"])
async def GET_status(guild: int):
    Guild = bot.get_guild(guild)
    # print("Guild:", Guild)
    if Guild:
        await db_connect()
        Welcome = await db.welcome.find_unique(where={"server_id": guild})
        Welcome_status = False if Welcome is None else Welcome.status
        # print("Welcome_status:", Welcome_status)

        Leave = await db.goodbye.find_unique(where={"server_id": guild})
        Leave_status = False if Leave is None else Leave.status
        # print("Leave_status:", Leave_status)

        Join_Member_Role = await db.joinrole.find_unique(where={"server_id": guild})
        Join_Member_Role_status = False if Join_Member_Role is None else Join_Member_Role.status
        # print("Join_Member_Role_status:", Join_Member_Role_status)

        status = await db.status.find_unique(where={"server_id": guild})
        image_share_status = False if status is None else status.IMAGES_ONLY
        # print("IMG_Only_status:", image_share_status)

        link_share_status = False if status is None else status.LINKS_ONLY
        # print("Link_Only_status:", link_share_status)

        try:
            member_count = await db.membercount.find_unique(where={"server_id": guild})
        except:
            member_count = await db.membercount.find_first(where={"server_id": guild})
        member_count_status = False if member_count is None else member_count.status
        # print("Memeber_Count_status:", member_count_status)

        Levels = await db.levelsetting.find_unique(where={"server_id": guild})
        Levels_status = False if Levels is None else Levels.status

        youtube_notification = await db.youtubesetting.find_unique(where={"server_id": guild})
        youtube_notification_status = False if youtube_notification is None else youtube_notification.status

        verification = await db.reactionverificationrole.find_unique(where={"server_id": guild})
        verification_status = False if verification is None else verification.status
        # print("Levels_status:", Levels_status)
        await db_disconnect()
        data = [{
            "img_only_status": image_share_status,
            "link_only_status": link_share_status,
            "memeber_count_status": member_count_status,
            "welcome_status": Welcome_status,
            "leave_status": Leave_status,
            "levelsetting_status": Levels_status,
            "join_member_role_status": Join_Member_Role_status,
            "youtube_notification_status": youtube_notification_status,
            "verification_status": verification_status,
        }]
        return data
    else:
        return f"{guild} is not a valid server id"

# Change server prefix
# @router.post("/change_prefix/",dependencies=[Depends(check_api_key)])
@router.post("/change_prefix", tags=["bot sevrver"])
async def change_prefix(guild, new_prefix):
    await db_connect()
    prefix = await db.server.find_unique(where={"server_id": guild})
    if prefix != None:
        await db.server.update(where={"ID": prefix.ID}, data={"prefix": new_prefix})
        await db_disconnect()
        return {"message": f"Prefix changed to |** {new_prefix} **|"}
    else:
        return HTTPException(status_code=404, detail=f"{guild} not found in database")

# join member role
# @router.post("/set_join_role/",dependencies=[Depends(check_api_key)])
@router.post("/set_join_role/", tags=["bot sevrver"])
async def set_join_role(guild: int, role: int):
    Guild = bot.get_guild(guild)
    if Guild:
        role_id = Guild.get_role(role)
        if role_id:
            await db_connect()
            server = await db.server.find_first(where={"server_id": Guild.id})
            if server == None:
                dd = {"server_id": Guild.id, "role_id": role_id.id, "role_name": role_id.name, "status": True}
                await db.joinrole.create(data=dd)
                await db_disconnect()
                return dd
            else:
                up = await db.joinrole.update(where={"ID": server.ID}, data={"role_id": role_id.id, "role_name": role_id.name, "status": True})
                await db_disconnect()
                return {"message": f"Join member role set to |**{role_id.name}**| for |**{Guild.name}**|"}
        else:
            return HTTPException(status_code=404, detail=f"|**{role}**| is not a valid role id for |**{Guild.name}**|")
    else:
        return HTTPException(status_code=404, detail=f"{guild} not found in Bot server list")

# Verify to main server
# @router.post("/verify_member_through_role/",dependencies=[Depends(check_api_key)])
@router.post("/verify_member_through_role/", tags=["bot sevrver"])
async def verify_member_through_role(guild: int, channel: int, role: int):
    # print(guild, role)
    Guild = bot.get_guild(guild)
    Channel = bot.get_channel(channel)
    if Guild:
        for rol in Guild.roles:
            # print("Role_id:",rol.id)
            if rol.id == role:
                await db_connect()
                server = await db.reactionverificationrole.find_first(where={"server_id": Guild.id})
                DD = {
                        "server_id": f'{Guild.id}',
                        "status": True, 
                        "channel_id": f'{Channel.id}',
                        "channel_name": f'{Channel.name}',
                        "role_id": f'{rol.id}',
                        "role_name": f'{rol.name}',
                        }
                if server == None:
                    cr = await db.reactionverificationrole.create(data=DD)
                    await db_disconnect()
                    return DD
                else:   
                    update = await db.reactionverificationrole.update(where={"ID": server.ID}, data=DD)
                    await db_disconnect()
                    return DD
        else:
            return f"|**{role}**| is not a valid role"

    else:
        return f"{guild} is not a valid server id"

