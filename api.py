# api.py
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
from fastapi import FastAPI, Request
import discord
from discord.ext import commands
from pydantic import BaseModel

# from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException
from starlette.responses import RedirectResponse
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware

from prisma import Prisma
import json
import requests
from cogs import lvlsystem

db = Prisma()
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URL = os.getenv("REDIRECT_URL")
LOGIN_URL = os.getenv("LOGIN_URL")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to database on startup
    await db.connect()
    yield
    # Disconnect from database on shutdown
    await db.disconnect()

def myAPI(bot: commands.Bot):
    # print("API started")
    # ---------------------api------------------------
    app = FastAPI(
        docs_url="/api/v2/docs",
        redoc_url="/api/v2/redoc",
        title="TO Bot API",
        description="TO Bot all feature API",
        version="2.0",
        openapi_url="/api/v2/openapi.json",
        lifespan=lifespan,
    )

    # cunstumize the UI
    # https://www.youtube.com/watch?v=adVQKXCNKUA
    origins = [
        "http://localhost",
        "http://localhost:8080",
        "http://localhost:8081",
        "http://localhost:5173",
        "http://127.0.0.1:30000",
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    API_KEY = os.getenv("API_KEY")
    # Create an instance of the APIKeyHeader security scheme
    api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

    # Define a dependency that will check the API key
    async def check_api_key(api_key: str = Depends(api_key_header)):
        # if not api_key or api_key != f"Bearer {API_KEY}":
        if not api_key or api_key != API_KEY:
            raise HTTPException(status_code=401, detail="Enter invalid API key")

    def get_bot():
        return bot

    # --------------main page as docs----------------------------

    @app.get("/", include_in_schema=False)
    async def redirect_to_docs():
        # response = RedirectResponse(url='/docs')
        response = RedirectResponse(url="/api/v2/docs")
        return response

    # ------------------------------------------------------------
    # @app.get("/server_List/",dependencies=[Depends(check_api_key)])
    @app.get("/server_List/", tags=["bot sevrver"])
    async def server_List():
        servers = {"ServerList": []}
        for guild in bot.guilds:
            # print(guild.id)
            # servers[guild.name] = guild.id
            server_info = {
                "name": str(guild.name),
                "id": str(guild.id),
                "icon_url": str(guild.icon),
            }
            servers["ServerList"].append(server_info)
            # servers[guild.name] = server_info
            # print(servers)
        return servers

    # List of channenels according to server id
    # @app.get("/server_Channels_List/{guild}",dependencies=[Depends(check_api_key)])
    @app.get("/server_Channels_List/", tags=["bot sevrver"])
    async def server_Channels_List(guild: int):
        channelList = {}
        Guild = bot.get_guild(guild)
        for channel in Guild.channels:
            if isinstance(channel, discord.TextChannel):
                channelList[channel.name] = str(channel.id)
        return channelList

    # List of roles according to server id
    # @app.get("/server_Roles_List/",dependencies=[Depends(check_api_key)])
    @app.get("/server_Roles_List/", tags=["bot sevrver"])
    async def server_Roles_List(guild: int):
        Roles_List = {}
        Guild = bot.get_guild(guild)
        if Guild:
            for role in Guild.roles:
                Roles_List[role.name] = str(role.id)
            return Roles_List
        else:
            return f"{guild} is not a valid server id"
            # @app.post("/welcome_status_GET/",dependencies=[Depends(check_api_key)])

    # Server all status
    # @app.get("/GET_status/",dependencies=[Depends(check_api_key)])
    @app.get("/GET_status/", tags=["bot sevrver"])
    async def GET_status(guild: int):
        Guild = bot.get_guild(guild)
        # print("Guild:", Guild)
        if Guild:
            Welcome = await db.welcome.find_unique(where={"server_id": guild})
            Welcome_status = False if Welcome is None else Welcome.status
            # print("Welcome_status:", Welcome_status)

            Leave = await db.goodbye.find_unique(where={"server_id": guild})
            Leave_status = False if Leave is None else Leave.status
            # print("Leave_status:", Leave_status)

            Join_Member_Role = await db.joinrole.find_unique(where={"server_id": guild})
            Join_Member_Role_status = (
                False if Join_Member_Role is None else Join_Member_Role.status
            )
            # print("Join_Member_Role_status:", Join_Member_Role_status)

            status = await db.status.find_unique(where={"server_id": guild})
            image_share_status = False if status is None else status.IMAGES_ONLY
            # print("IMG_Only_status:", image_share_status)

            link_share_status = False if status is None else status.LINKS_ONLY
            # print("Link_Only_status:", link_share_status)

            try:
                member_count = await db.membercount.find_unique(
                    where={"server_id": guild}
                )
            except:
                member_count = await db.membercount.find_first(
                    where={"server_id": guild}
                )
            member_count_status = False if member_count is None else member_count.status
            # print("Memeber_Count_status:", member_count_status)

            Levels = await db.levelsetting.find_unique(where={"server_id": guild})
            Levels_status = False if Levels is None else Levels.status

            youtube_notification = await db.youtubesetting.find_unique(
                where={"server_id": guild}
            )
            youtube_notification_status = (
                False if youtube_notification is None else youtube_notification.status
            )

            verification = await db.reactionverificationrole.find_unique(
                where={"server_id": guild}
            )
            verification_status = False if verification is None else verification.status
            # print("Levels_status:", Levels_status)

            data = [
                {
                    "img_only_status": image_share_status,
                    "link_only_status": link_share_status,
                    "memeber_count_status": member_count_status,
                    "welcome_status": Welcome_status,
                    "leave_status": Leave_status,
                    "levelsetting_status": Levels_status,
                    "join_member_role_status": Join_Member_Role_status,
                    "youtube_notification_status": youtube_notification_status,
                    "verification_status": verification_status,
                }
            ]
            return data
        else:
            return f"{guild} is not a valid server id"

    # Change server prefix
    # @app.post("/change_prefix/",dependencies=[Depends(check_api_key)])
    @app.post("/change_prefix", tags=["bot sevrver"])
    async def change_prefix(guild, new_prefix):

        prefix = await db.server.find_unique(where={"server_id": guild})
        if prefix != None:
            await db.server.update(where={"ID": prefix.ID}, data={"prefix": new_prefix})

            return {"message": f"Prefix changed to |** {new_prefix} **|"}
        else:
            return HTTPException(
                status_code=404, detail=f"{guild} not found in database"
            )

    # join member role
    # @app.post("/set_join_role/",dependencies=[Depends(check_api_key)])
    @app.post("/set_join_role/", tags=["bot sevrver"])
    async def set_join_role(guild: int, role: int):
        Guild = bot.get_guild(guild)
        if Guild:
            role_id = Guild.get_role(role)
            if role_id:
                server = await db.server.find_first(where={"server_id": Guild.id})
                if server == None:
                    dd = {
                        "server_id": Guild.id,
                        "role_id": role_id.id,
                        "role_name": role_id.name,
                        "status": True,
                    }
                    await db.joinrole.create(data=dd)
                    return dd
                else:
                    up = await db.joinrole.update(
                        where={"ID": server.ID},
                        data={
                            "role_id": role_id.id,
                            "role_name": role_id.name,
                            "status": True,
                        },
                    )
                    return {
                        "message": f"Join member role set to |**{role_id.name}**| for |**{Guild.name}**|"
                    }
            else:
                return HTTPException(
                    status_code=404,
                    detail=f"|**{role}**| is not a valid role id for |**{Guild.name}**|",
                )
        else:
            return HTTPException(
                status_code=404, detail=f"{guild} not found in Bot server list"
            )

    # Verify to main server
    # @app.post("/verify_member_through_role/",dependencies=[Depends(check_api_key)])
    @app.post("/verify_member_through_role/", tags=["bot sevrver"])
    async def verify_member_through_role(guild: int, channel: int, role: int):
        # print(guild, role)
        Guild = bot.get_guild(guild)
        Channel = bot.get_channel(channel)
        if Guild:
            for rol in Guild.roles:
                # print("Role_id:",rol.id)
                if rol.id == role:
                    server = await db.reactionverificationrole.find_first(
                        where={"server_id": Guild.id}
                    )
                    DD = {
                        "server_id": f"{Guild.id}",
                        "status": True,
                        "channel_id": f"{Channel.id}",
                        "channel_name": f"{Channel.name}",
                        "role_id": f"{rol.id}",
                        "role_name": f"{rol.name}",
                    }
                    if server == None:
                        cr = await db.reactionverificationrole.create(data=DD)
                        return DD
                    else:
                        update = await db.reactionverificationrole.update(
                            where={"ID": server.ID}, data=DD
                        )
                        return DD
            else:
                return f"|**{role}**| is not a valid role"

        else:
            return f"{guild} is not a valid server id"

    # ------------------------------------------------------------
    # @app.post("/link_channel_switch/",dependencies=[Depends(check_api_key)])
    @app.post("/link_channel_status/", tags=["bot status"])
    async def link_channel_switch(guild: int, status: bool):
        Guild = bot.get_guild(guild)
        if Guild:
            link = await db.status.find_unique(where={"server_id": guild})
            if link == None:
                cr = await db.status.create(
                    data={
                        "server_id": guild,
                        "IMAGES_ONLY": False,
                        "LINKS_ONLY": status,
                    }
                )
                return {
                    "status": f"Link channel status created and set to |**{status}**|"
                }
            else:
                up = await db.status.update(
                    where={"ID": link.ID}, data={"LINKS_ONLY": status}
                )
                return {"message": f"Link channel status set to |**{status}**|"}
        else:
            return f"{guild} is not a valid server id"

    # @app.post("/IMG_channel_switch/",dependencies=[Depends(check_api_key)])
    @app.post("/IMG_channel_status/", tags=["bot status"])
    async def IMG_channel_switch(guild: int, status: bool):
        Guild = bot.get_guild(guild)
        if Guild:
            link = await db.status.find_unique(where={"server_id": guild})
            if link == None:
                cr = await db.status.create(
                    data={
                        "server_id": guild,
                        "IMAGES_ONLY": status,
                        "LINKS_ONLY": False,
                    }
                )
                return {
                    "message": f"Image channel status created and set to |**{status}**|"
                }
            else:
                up = await db.status.update(
                    where={"ID": link.ID}, data={"IMAGES_ONLY": status}
                )
                return {"message": f"Image channel status set to |**{status}**|"}
        else:
            return HTTPException(
                status_code=404, detail=f"{guild} is not a valid server id"
            )

    # server welcome message
    # @app.post("/welcome_status/",dependencies=[Depends(check_api_key)])
    @app.post("/welcome_status/", tags=["bot status"])
    async def welcome_status(guild: int, status: bool):
        Guild = bot.get_guild(guild)
        if Guild:
            welcome = await db.welcome.find_unique(where={"server_id": guild})
            if welcome == None:
                cr = await db.welcome.create(
                    data={
                        "server_id": guild,
                        "channel_id": 0,
                        "channel_name": "",
                        "message": "",
                        "status": False,
                    }
                )
                return {"message": f"Welcome status created and set to |**{status}**|"}
            else:
                up = await db.welcome.update(
                    where={"ID": welcome.ID}, data={"status": status}
                )
                return {"message": f"Welcome status set to |**{status}**|"}
        else:
            return HTTPException(
                status_code=404, detail=f"{guild} is not a valid server id"
            )

    @app.post("/leave_status/", tags=["bot status"])
    async def leave_status(guild: int, status: bool):
        Guild = bot.get_guild(guild)
        if Guild:

            leave = await db.goodbye.find_unique(where={"server_id": guild})
            if leave == None:
                cr = await db.goodbye.create(
                    data={
                        "server_id": guild,
                        "channel_id": 0,
                        "channel_name": "",
                        "message": "",
                        "status": False,
                    }
                )

                return {"message": f"Leave status set to |**{status}**|"}
            else:
                up = await db.goodbye.update(
                    where={"ID": leave.ID}, data={"status": status}
                )

                return {"message": f"Leave status set to |**{status}**|"}
        else:
            return f"{guild} is not a valid server id"

    # --------------------------------------------------------------------------------
    # ------------------------------------------------------------

    class TokenResponse(BaseModel):
        access_token: str
        token_type: str

    class User(BaseModel):
        id: int
        username: str

    # ------------------------------------------------------------
    @app.get("/available_users", tags=["dashboard"])
    async def available_users(user_id: int):
        print("User ID:", user_id)
        try:
            try:

                server = await db.dashboarduser.find_first(where={"user_id": user_id})
                print(server)

                print(server)
                user_json = {
                    "user": json.loads(server.users),
                    "guild": json.loads(server.guilds),
                }
                return user_json
            except:
                raise HTTPException(status_code=401, detail="User not found")
        except Exception as e:
            print("Error in database connection:", e)
            return {"error": str(e)}

    # ------------------------------------------------------------

    @app.get("/login", tags=["dashboard"])
    async def login():
        return RedirectResponse(url=os.getenv("DASHBOARD_URL"))

    @app.get("/callback/", tags=["dashboard"])
    async def callback(code: str):
        # print('code:-',code)
        if not code:
            # print('code not provided')
            raise HTTPException(status_code=400, detail="Code not provided")

        data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URL,
        }
        # print('data:-',data)

        headers = {
            "Content-Type": "routerlication/x-www-form-urlencoded",
            "Accept-Encoding": "routerlication/x-www-form-urlencoded",
        }

        response = requests.post(
            "https://discord.com/api/oauth2/token", data=data, headers=headers
        )
        print("dicord api response:", response.status_code)
        response.raise_for_status()

        token_response = TokenResponse(**response.json())
        # print(token_response)

        # Store token in local storage
        # This part cannot be directly implemented in FastAPI as it's a server-side framework.
        # You can send the token back to the client and store it in the browser's local storage using JavaScript.

        # Fetch user
        user_response = requests.get(
            "https://discord.com/api/users/@me",
            headers={"Authorization": f"Bearer {token_response.access_token}"},
        )
        user_response.raise_for_status()
        user_data = user_response.json()

        # Fetch Guilds
        guilds_response = requests.get(
            "https://discord.com/api/users/@me/guilds",
            headers={"Authorization": f"Bearer {token_response.access_token}"},
        )
        guilds_response.raise_for_status()
        guilds_data = guilds_response.json()

        guilds = [guild for guild in guilds_data if guild["permissions"] == 2147483647]

        data = {"user": user_data, "guilds": guilds}
        try:

            database = await db.dashboarduser.find_unique(
                where={"user_id": int(user_data["id"])}
            )
            if database is None:
                update = await db.dashboarduser.create(
                    data={
                        "user_id": int(user_data["id"]),
                        "guilds": json.dumps(
                            guilds
                        ),  # Ensure guilds is stored as JSON string if required
                        "users": json.dumps(
                            user_data
                        ),  # Ensure users is stored as JSON string if required
                    }
                )
                print("update:", update)

            else:
                update = await db.dashboarduser.update(
                    where={"user_id": int(user_data["id"])},
                    data={"guilds": json.dumps(guilds), "users": json.dumps(user_data)},
                )
                print("update:", update)

        except Exception as e:
            print("Error in database connection:", e)

        return data

    # -----------------------Img / Link ------------------------------
    # @appget("/Image_channel_lst/",dependencies=[Depends(check_api_key)])
    @app.get("/Image_channel_lst", tags=["img_link"])
    async def Image_channel_lst(guild: int):
        Guild = bot.get_guild(guild)
        if Guild:
            data = {}

            img = await db.imagesonly.find_many(where={"server_id": guild})

            if img != None:
                for i in img:
                    data.update({i.channel_name: i.channel_id})
                return data
            else:
                return data
        else:
            return HTTPException(
                status_code=404,
                detail=f"{guild} is not a valid server id or not found in database",
            )

    # @apppost("/add_img_chhannel/",dependencies=[Depends(check_api_key)])
    @app.post("/add_img_chhannel", tags=["img_link"])
    async def add_img_chhannel(guild: int, channel_id: int):
        Guild = bot.get_guild(guild)
        if Guild:
            channel_ids = bot.get_channel(int(channel_id))
            if channel_ids:

                img_update = await db.imagesonly.create(
                    data={
                        "server_id": guild,
                        "channel_name": channel_ids.name,
                        "channel_id": channel_ids.id,
                    }
                )

                print(img_update)
                return {
                    "message": f"Channel |**{channel_ids.name}**| with id |**{channel_ids.id}**| added successfully"
                }
            else:
                return HTTPException(
                    status_code=404, detail=f"{channel_id} is not a valid channel id"
                )
        else:
            return HTTPException(
                status_code=404, detail=f"{guild} not found in database"
            )

    # @apppost("/remove_img_channel/",dependencies=[Depends(check_api_key)])
    @app.post("/remove_img_channel", tags=["img_link"])
    async def remove_img_channel(guild: int, channel_id: int):
        Guild = bot.get_guild(guild)
        if Guild:
            channel_ids = bot.get_channel(int(channel_id))
            if channel_ids:

                img = await db.imagesonly.find_first(
                    where={"server_id": guild, "channel_id": channel_ids.id}
                )
                img_update = await db.imagesonly.delete(where={"ID": img.ID})

                return {
                    "message": f"Channel |**{channel_ids.name}**| with id |**{channel_ids.id}**| removed successfully"
                }
            else:
                return HTTPException(
                    status_code=404, detail=f"{channel_id} is not a valid channel id"
                )
        else:
            return HTTPException(
                status_code=404, detail=f"{guild} not found in database"
            )

    # @appget("/Link_channel_lst/",dependencies=[Depends(check_api_key)])
    @app.get("/Link_channel_lst", tags=["img_link"])
    async def Link_channel_lst(guild: int):
        Guild = bot.get_guild(guild)
        if Guild:
            data = {}

            link = await db.linksonly.find_first(where={"server_id": guild})

            if link != None:
                for i in link:
                    data.update({i.channel_name: i.channel_id})
                return data
            else:
                return data
        else:
            return HTTPException(
                status_code=404,
                detail=f"{guild} is not a valid server id or not found in database",
            )

    # @apppost("/add_link_chhannel/",dependencies=[Depends(check_api_key)])
    @app.post("/remove_link_channel", tags=["img_link"])
    async def remove_link_channel(guild: int, channel_id: int):
        Guild = bot.get_guild(guild)
        if Guild:
            channel_ids = bot.get_channel(int(channel_id))
            if channel_ids:

                link = await db.linksonly.find_first(
                    where={"server_id": guild, "channel_id": channel_ids.id}
                )
                rm = await db.linksonly.delete(where={"ID": link.ID})

                return {
                    "message": f"Channel |**{channel_ids.name}**| with id |**{channel_ids.id}**| removed successfully"
                }
            else:
                return HTTPException(
                    status_code=404, detail=f"{channel_id} is not a valid channel id"
                )
        else:
            return HTTPException(
                status_code=404, detail=f"{guild} not found in database"
            )

    # @apppost("/remove_link_channel/",dependencies=[Depends(check_api_key)])
    @app.post("/add_link_chhannel", tags=["img_link"])
    async def add_link_chhannel(
        guild: int,
        channel_id: int,
    ):
        Guild = bot.get_guild(guild)
        if Guild:
            channel_ids = bot.get_channel(int(channel_id))
            if channel_ids:

                update = await db.linksonly.create(
                    data={
                        "server_id": guild,
                        "channel_name": channel_ids.name,
                        "channel_id": channel_ids.id,
                    }
                )
                print("add_link_chhannel:", update)

                return {
                    "message": f"Channel |**{channel_ids.name}**| with id |**{channel_ids.id}**| added successfully"
                }
            else:
                return HTTPException(
                    status_code=404,
                    detail=f"|**{channel_id}**| is not a valid channel id",
                )
        else:
            return HTTPException(
                status_code=404, detail=f"{guild} not found in database"
            )

    # -----------------------Img / Link ------------------------------
    # ----------------------------LEVEL SYSTEM----------------------------------------
    # @app.post("/LVLsystem_status/",dependencies=[Depends(check_api_key)])

    @app.post("/LVLsystem_status/", tags=["Level system"])
    async def LVLsystem_status(guild: int, status: bool):
        Guild = bot.get_guild(guild)
        if Guild:

            lvl = await db.levelsetting.find_unique(where={"server_id": guild})
            if lvl == None:
                cr = await db.levelsetting.create(
                    data={
                        "server_id": guild,
                        "status": status,
                        "level_up_channel_id": 0,
                        "level_up_channel_name": "",
                    }
                )

                return {
                    "message": f"Level system status created and set to |**{status}**|"
                }
            else:
                up = await db.levelsetting.update(
                    where={"ID": lvl.ID}, data={"status": status}
                )

                return {"message": f"Level system status set to |**{status}**|"}
        else:
            return f"{guild} is not a valid server id"

    # @app.post("/LVLsystem_status/",dependencies=[Depends(check_api_key)])
    @app.post("/LVL_role_set/", tags=["Level system"])
    async def LVL_role_set(guild: int, role: int, lvl: int):
        Guild = bot.get_guild(guild)
        if Guild:
            for rol in Guild.roles:
                if rol.id == role:

                    lvls = await db.levelrole.find_first(
                        where={"server_id": guild, "level": lvl}
                    )
                    if lvls == None:
                        dd = {
                            "level": lvl,
                            "role_id": rol.id,
                            "role_name": rol.name,
                            "server_id": guild,
                        }
                        print(dd)
                        cr = await db.levelrole.create(
                            data={
                                "level": lvl,
                                "role_id": rol.id,
                                "role_name": rol.name,
                                "server_id": guild,
                            }
                        )
                        print(cr)

                        return {
                            "message": f"Level role created for |**{rol.name}**| to  Level({lvl})"
                        }
                    else:
                        up = await db.levelrole.update(
                            where={"ID": lvl.ID},
                            data={"role_id": role, "role_name": rol.name},
                        )

                        return {
                            "message": f"Level role updated for |**{rol.name} to  Level({lvl})"
                        }
            return {"message": f"Level role set to |**{rol.name}**|**{rol.id})**|"}
        else:
            return f"{guild} is not a valid server id"

    # @app.post("/LVL_set_channel/",dependencies=[Depends(check_api_key)])
    @app.post("/LVL_set_channel/", tags=["Level system"])
    async def LVL_set_channel(guild: int, channel: int):
        Guild = bot.get_guild(guild)
        if Guild:
            lvl = await db.levelsetting.find_unique(where={"server_id": guild})
            if lvl == None:
                return {"message": f"Level setting not found in database"}

            if lvl.level_up_channel_id == channel.id:
                return {"message": f"Level up channel already set to {channel.name}"}
            else:
                update = await db.levelsetting.update(
                    where={"ID": lvl.ID},
                    data={
                        "level_up_channel_id": channel.id,
                        "level_up_channel_name": channel.name,
                    },
                )
                return {"message": f"Level up channel set to {channel.name}"}
        else:
            return f"{guild} is not a valid server id"

    # @app.post("add_xp",dependencies=[Depends(check_api_key)])
    @app.post("/add_xp", tags=["Level system"])
    async def add_xp(guild: int, user: int, xp: int):
        Guild = bot.get_guild(guild)
        if Guild:
            amount = xp
            if amount <= 0:
                return {
                    "message": 'Parameter "amount" was less than or equal to zero. The minimum value is 1'
                }

            userdb = await db.userslevel.find_first(
                where={"server_id": guild, "user_id": user}
            )
            if userdb == None:

                return HTTPException(
                    status_code=404, detail=f"User not found in database"
                )
            else:

                if userdb.xp >= lvlsystem.MAX_XP:
                    print("Max xp reached")

                    return
                else:
                    new_total_xp = userdb.xp + amount
                    new_total_xp = (
                        new_total_xp
                        if new_total_xp <= lvlsystem.MAX_XP
                        else lvlsystem.MAX_XP
                    )
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

                    update = await db.userslevel.update(
                        where={"ID": userdb.ID},
                        data={"xp": new_total_xp, "level": maybe_new_level},
                    )

                    return {
                        "message": f"User {user} has {new_total_xp} xp and is now level {maybe_new_level}"
                    }

    # @app.post("/remove_level",dependencies=[Depends(check_api_key)])
    @app.post("/remove_level", tags=["Level system"])
    async def remove_level(guild: int, user: int, level: int):
        Guild = bot.get_guild(guild)
        if Guild:
            amount = level
            if amount <= 0:
                return {
                    "message": 'Parameter "Level" was less than or equal to zero. The minimum value is 1'
                }

            userdb = await db.userslevel.find_first(
                where={"server_id": guild, "user_id": user}
            )
            if userdb == None:

                return HTTPException(
                    status_code=404, detail=f"User not found in database"
                )
            else:
                if userdb.level >= lvlsystem.MAX_LEVEL:

                    return {"message": f"Max xp reached"}
                else:
                    await db.userslevel.update(
                        where={"ID": userdb.ID}, data={"xp": 0, "level": amount}
                    )

                    return {
                        "message": f"User {user} has {userdb.xp} xp and is now level {userdb.level}"
                    }

        else:
            return HTTPException(
                status_code=404, detail=f"{guild} is not a valid server id"
            )

    # @app.post("/remove_no_xp_role",dependencies=[Depends(check_api_key)])
    @app.post("/remove_no_xp_role", tags=["Level system"])
    async def remove_no_xp_role(guild: int, role: int):
        Guild = bot.get_guild(guild)
        if Guild:
            no_xp_role_db = await db.noxprole.find_first(
                where={"server_id": guild, "role_id": role}
            )
            if no_xp_role_db == None:
                return HTTPException(
                    status_code=404, detail=f"Role not found in database"
                )
            else:
                await db.noxprole.delete(where={"ID": no_xp_role_db.ID})
                return {"message": f"Role {role} removed from no xp role list"}

    # @app.post("/add_no_xp_role",dependencies=[Depends(check_api_key)])
    @app.post("/add_no_xp_role", tags=["Level system"])
    async def add_no_xp_role(guild: int, role: int):
        Guild = bot.get_guild(guild)
        if Guild:
            rolle = Guild.get_role(role)
            DB = await db.noxprole.find_first(
                where={"server_id": guild, "role_id": role}
            )
            if DB == None:
                await db.noxprole.create(
                    data={"server_id": guild, "role_id": role, "role_name": rolle.name}
                )
                return {"message": f"Role {role} added to no xp role list"}
            else:

                return {"message": f"Role {role} already in no xp role list"}
        else:
            return HTTPException(
                status_code=404, detail=f"{guild} is not a valid server id"
            )

    # @app.post("/remove_no_xp_role",tags = ["Level system"])
    @app.post("/remove_no_xp_role", tags=["Level system"])
    async def remove_no_xp_rolez(guild: int, role: int):
        Guild = bot.get_guild(guild)

        if Guild:

            DB = await db.noxprole.find_first(
                where={"server_id": guild, "role_id": role}
            )
            if DB == None:

                return {"message": f"Role {role} not found in database"}
            else:
                await db.noxprole.delete(where={"ID": DB.ID})

                return {"message": f"Role {role} already in no xp role list"}
        else:
            return HTTPException(
                status_code=404, detail=f"{guild} is not a valid server id"
            )

    @app.post("/add_noxpchannel", tags=["Level system"])
    async def add_noxpchannel(guild: int, channel: int):
        Guild = bot.get_guild(guild)
        if Guild:
            chann = Guild.get_channel(channel)

            DB = await db.noxpchannel.find_first(
                where={"server_id": guild, "channel_id": channel}
            )
            if DB == None:
                await db.noxpchannel.create(
                    data={
                        "server_id": guild,
                        "channel_id": channel,
                        "channel_name": chann.name,
                    }
                )

                return {"message": f"Channel {channel} added to no xp channel list"}
            else:

                return {"message": f"Channel {channel} already in no xp channel list"}
        else:
            return HTTPException(
                status_code=404, detail=f"{guild} is not a valid server id"
            )

    # @app.post("/remove_noxpchannel",tags = ["Level system"])
    @app.post("/remove_noxpchannel", tags=["Level system"])
    async def remove_noxpchannel(guild: int, channel: int):
        Guild = bot.get_guild(guild)
        if Guild:

            DB = await db.noxpchannel.find_first(
                where={"server_id": guild, "channel_id": channel}
            )
            if DB == None:

                return {"message": f"Channel {channel} not found in database"}
            else:
                await db.noxpchannel.delete(where={"ID": DB.ID})

                return {"message": f"Channel {channel} already in no xp channel list"}
        else:
            return HTTPException(
                status_code=404, detail=f"{guild} is not a valid server id"
            )

    # --------------------------------------------------------------------------------
    # ------------------------welcome_leave------------------------
    # @app.post("/welcome_message/",dependencies=[Depends(check_api_key)])
    @app.post("/welcome_message/", tags=["welcome_leave"])
    async def welcome_message(guild: int, message: str):
        Guild = bot.get_guild(guild)
        if Guild:

            welcome = await db.welcome.find_unique(where={"server_id": guild})
            if welcome == None:
                update = await db.welcome.create(
                    data={"server_id": guild, "message": message}
                )

                return {"message": f"Welcome message set to |**{message}**|"}
            else:
                up = await db.welcome.update(
                    where={"ID": welcome.ID}, data={"message": message}
                )

                return {"message": f"Welcome message set to |**{message}**|"}
        else:
            return {"message": f"{guild} is not a valid server id"}

    # @app.post("/leave_message/",dependencies=[Depends(check_api_key)])
    @app.post("/leave_message/", tags=["welcome_leave"])
    async def leave_message(guild: int, message: str):
        Guild = bot.get_guild(guild)
        if Guild:

            leave = await db.goodbye.find_first(where={"server_id": guild})
            if leave == None:
                cr = await db.goodbye.create(
                    data={
                        "server_id": guild,
                        "channel_id": 0,
                        "channel_name": "",
                        "status": True,
                        "message": message,
                    }
                )

                return {"message": f"leave message set to |**{message}**|"}
            else:
                up = await db.goodbye.update(
                    where={"ID": leave.ID}, data={"message": message}
                )

                return {"message": f"leave message set to |**{message}**|"}
        else:
            return {"message": f"{guild} is not a valid server id"}

    # @app.post("/welcome_channel_set/",dependencies=[Depends(check_api_key)])
    @app.post("/welcome_channel_set/", tags=["welcome_leave"])
    async def welcome_channel_set(guild: int, channel: int):
        Guild = bot.get_guild(guild)
        if Guild:
            for chann in Guild.channels:
                if chann.id == channel:

                    doc_ref = await db.welcome.find_first(where={"server_id": guild})
                    if doc_ref is None:
                        cr = await db.welcome.create(
                            data={
                                "server_id": guild,
                                "channel_id": channel,
                                "channel_name": chann.name,
                                "message": "",
                                "status": False,
                            }
                        )

                        return {
                            "message": f"Welcome channel created and set to |**{chann.name}**||**{chann.id}**|"
                        }
                    else:
                        up = await db.welcome.update(
                            where={"ID": doc_ref.ID},
                            data={"channel_id": channel, "channel_name": chann.name},
                        )

                        return {
                            "message": f"Welcome channel set to |**{chann.name}**||**{chann.id}**|"
                        }

            return {"message": f"{channel}Channel not fount"}
        else:
            return {"message": f"{guild} is not a valid server id"}

    # @app.post("/leave_channel_set/",dependencies=[Depends(check_api_key)])
    @app.post("/leave_channel_set/", tags=["welcome_leave"])
    async def leave_channel_set(guild: int, channel: int):
        Guild = bot.get_guild(guild)
        if Guild:
            for chann in Guild.channels:
                if chann.id == channel:

                    leave = await db.goodbye.find_first(where={"server_id": guild})
                    if leave == None:
                        cr = await db.goodbye.create(
                            data={
                                "server_id": guild,
                                "channel_id": channel,
                                "channel_name": chann.name,
                                "message": "",
                                "status": False,
                            }
                        )

                        return {
                            "message": f"Leave channel created and set to |**{chann.name}**||**{chann.id}**|"
                        }
                    else:
                        up = await db.goodbye.update(
                            where={"ID": leave.ID},
                            data={"channel_id": channel, "channel_name": chann.name},
                        )

                        return {
                            "message": f"Leave channel set to |**{chann.name}**||**{chann.id}**|"
                        }

            return {"message": f"{channel}Channel not fount"}
        else:
            return {"message": f"{guild} is not a valid server id"}

    # ------------------------WELCOME_LEAVE------------------------
    # --------------------------------------------------------------------------------
    # ----------------------------YOUTUBE-------------------------------------------
    @app.get("/GET_YT_SUB_channels_lst/", tags=["youtube"])
    async def GET_YT_SUB_channels_lst(guild: int):

        Guild = bot.get_guild(guild)
        guild = await db.youtubesubchannel.find_many(where={"server_id": guild})

        if Guild:
            if guild != None:
                lst = []
                for i in guild:
                    lst.append(i.channel)

                return lst
            else:
                return HTTPException(
                    status_code=404, detail=f"{guild} not found in database"
                )
        else:
            return HTTPException(
                status_code=404, detail=f"{guild} is not a valid server id"
            )

    # @app.post("/youtube_notification_status/",dependencies=[Depends(check_api_key)])
    @app.post("/youtube_system_status/", tags=["youtube"])
    async def youtube_system_status(guild: int, status: bool):
        Guild = bot.get_guild(guild)
        if Guild:

            yt = await db.youtubesetting.find_unique(where={"server_id": guild})
            if yt == None:
                cr = await db.youtubesetting.create(
                    data={
                        "server_id": guild,
                        "status": status,
                        "channel_id": 0,
                        "channel_name": "",
                    }
                )

                return {
                    "message": f"Youtube notification status created and set to |**{status}**|"
                }
            else:
                up = await db.youtubesetting.update(
                    where={"ID": yt.ID}, data={"status": status}
                )

                return {"message": f"Youtube notification status set to |**{status}**|"}
        else:
            return HTTPException(
                status_code=404, detail=f"{guild} is not a valid server id"
            )

    # @app.post("/youtube_notification/",dependencies=[Depends(check_api_key)])
    @app.post("/youtube_notification/", tags=["youtube"])
    async def youtube_video_bot_channel_setup(guild: int, channel: int):
        Guild = bot.get_guild(guild)
        if Guild:
            Channel = bot.get_channel(channel)
            if Channel:

                yt = await db.youtubesetting.find_unique(where={"server_id": guild})
                if yt == None:
                    cr = await db.youtubesetting.create(
                        data={
                            "server_id": guild,
                            "status": True,
                            "channel_id": Channel.id,
                            "channel_name": Channel.name,
                        }
                    )

                    return {
                        "message": f" Youtube notification created and set to |**{Channel.name}**|**({Channel.id})**|"
                    }
                else:
                    up = await db.youtubesetting.update(
                        where={"ID": yt.ID},
                        data={"channel_id": Channel.id, "channel_name": Channel.name},
                    )

                    return {
                        "message": f" Youtube notification set to |**{Channel.name}**|**({Channel.id})**|"
                    }

            else:
                return f"{channel} is not a valid channel id"
        else:
            return f"{guild} is not a valid server id"

    # @app.post("/Set_YT_channel/",dependencies=[Depends(check_api_key)])
    @app.post("/Set_YT_channel/", tags=["youtube"])
    async def subscribe_youtube_channel_by_name(guild: int, YT_channel_usr: str):
        Guild = bot.get_guild(guild)
        if Guild:
            data_set = {"youtube_channels": [YT_channel_usr]}

            yt_channels = await db.youtubesubchannel.find_many(
                where={"server_id": guild}
            )
            for i in yt_channels:
                if i.channel == YT_channel_usr:

                    return {
                        "message": f"Youtube notification is already set to |**{YT_channel_usr}**|"
                    }
            cr = await db.youtubesubchannel.create(
                data={"server_id": guild, "channel": YT_channel_usr}
            )

            return {"message": f" Youtube notification set for |**{YT_channel_usr}**|"}

        else:
            return f"{guild} is not a valid server id"

    # @app.post("/remove_YT_channel/",dependencies=[Depends(check_api_key)])
    @app.post("/remove_YT_channel/", tags=["youtube"])
    async def remove_YT_channel(guild: int, YT_channel_usr: str):
        Guild = bot.get_guild(guild)
        if Guild:

            try:
                yt = await db.youtubesubchannel.find_first(
                    where={"server_id": guild, "channel": YT_channel_usr}
                )
                await db.youtubesubchannel.delete(where={"ID": yt.ID})

                return {
                    "message": f" Youtube channel ubsubscribe removed for |**{YT_channel_usr}**|"
                }
            except:
                yt = await db.youtubesetting.find_many(where={"server_id": guild})
                for i in yt:
                    if i.channel_id == YT_channel_usr:
                        await db.youtubesubchannel.delete(
                            where={"server": guild, "channel": YT_channel_usr}
                        )

                        return {
                            "message": f" Youtube notification is already removed for |**{YT_channel_usr}**|"
                        }

        else:
            return f"{guild} is not a valid server id"

    # ----------------------------YOUTUBE-------------------------------------------
    # --------------------------------------------------------------------------------
    return app
