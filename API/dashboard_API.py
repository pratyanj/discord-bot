from fastapi import APIRouter,HTTPException
from starlette.responses import RedirectResponse
from pydantic import BaseModel
from database.connection import *
from discord.ext import commands
bot = commands.bot
import config
import requests
import json

router = APIRouter( 
                    prefix="/dashboard",
                    tags=["dashboard"],
                    responses={404: {"description": ""}},
                    )
CLIENT_ID = config.CLIENT_ID
CLIENT_SECRET = config.CLIENT_SECRET
REDIRECT_URL = config.REDIRECT_URL
LOGIN_URL = config.LOGIN_URL
# ------------------------------------------------------------

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    id: int
    username: str

# ------------------------------------------------------------
@router.get("/available_users", tags=["dashboard"])
async def available_users(user_id: int):
    print("User ID:",user_id)
    try:
        try:
            await db_connect1()
            server = await db.dashboarduser.find_first(where={"user_id": user_id})
            print(server)
            await db_disconnect()
            print(server)
            user_json ={
                'user':json.loads(server.users),
                'guild':json.loads(server.guilds)
            }
            return user_json
        except:
            raise HTTPException(status_code=401, detail="User not found")
    except Exception as e:
        print("Error in database connection:", e)
        return {"error": str(e)}
# ------------------------------------------------------------

@router.get("/login", tags=["dashboard"])
async def login():
    return RedirectResponse(url=config.LOGIN_URL)

@router.get("/callback/", tags=["dashboard"])
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
        "https://discord.com/api/oauth2/token", data=data, headers=headers)
    print("dicord api response:", response.status_code)
    response.raise_for_status()

    token_response = TokenResponse(**response.json())
    # print(token_response)

    # Store token in local storage
    # This part cannot be directly implemented in FastAPI as it's a server-side framework.
    # You can send the token back to the client and store it in the browser's local storage using JavaScript.

    # Fetch user
    user_response = requests.get("https://discord.com/api/users/@me", headers={
                                    "Authorization": f"Bearer {token_response.access_token}"})
    user_response.raise_for_status()
    user_data = user_response.json()

    # Fetch Guilds
    guilds_response = requests.get("https://discord.com/api/users/@me/guilds", headers={
                                    "Authorization": f"Bearer {token_response.access_token}"})
    guilds_response.raise_for_status()
    guilds_data = guilds_response.json()

    guilds = [
        guild for guild in guilds_data if guild["permissions"] == 2147483647]

    data = {"user": user_data, "guilds": guilds}
    try:
        await db_connect1()
        database = await db.dashboarduser.find_unique(where={"user_id": int(user_data["id"])})
        if database is None:
            update = await db.dashboarduser.create(data={
            'user_id': int(user_data["id"]),
            'guilds': json.dumps(guilds),  # Ensure guilds is stored as JSON string if required
            'users': json.dumps(user_data) # Ensure users is stored as JSON string if required
                })
            print("update:",update)
            await db_disconnect()
        else:
            update = await db.dashboarduser.update(where={'user_id': int(user_data["id"])}, data={
            'guilds': json.dumps(guilds),
            'users': json.dumps(user_data)
            })
            print("update:",update)
            await db_disconnect()
    except Exception as e:
        print("Error in database connection:", e)

    return data
