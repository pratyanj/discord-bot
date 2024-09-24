# api.py
from fastapi import FastAPI

from discord.ext import commands
# from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException
from starlette.responses import RedirectResponse
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware

from prisma import Prisma
db = Prisma()
from database.connection import db_connect, db_disconnect
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URL = os.getenv('REDIRECT_URL')
LOGIN_URL = os.getenv('LOGIN_URL')


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
    )
    # cunstumize the UI
    # https://www.youtube.com/watch?v=adVQKXCNKUA
    origins = [
        "http://localhost",
        "http://localhost:8080",
        "http://localhost:5173",
        "http://127.0.0.1:30000",
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    API_KEY = os.getenv('API_KEY')
    # Create an instance of the APIKeyHeader security scheme
    api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

    # Define a dependency that will check the API key
    async def check_api_key(api_key: str = Depends(api_key_header)):
        # if not api_key or api_key != f"Bearer {API_KEY}":
        if not api_key or api_key != API_KEY:
            raise HTTPException(
                status_code=401, detail="Enter invalid API key")
            
    
    # --------------main page as docs----------------------------
    @app.get("/", include_in_schema=False)
    async def redirect_to_docs():
        # response = RedirectResponse(url='/docs')
        response = RedirectResponse(url='/api/v2/docs')
        return response
    from API import youtubeAPI,dashboard,bot_server,img_link,WelcomeLeave,bot_status,lvlsystem
    # ------------------------------------------------------------
    # app.include_router(dashboard.router, dependencies=[Depends(check_api_key)])
    # app.include_router(youtubeAPI.router, dependencies=[Depends(check_api_key)])
    # app.include_router(bot_server.router, dependencies=[Depends(check_api_key)])
    # app.include_router(img_link.router, dependencies=[Depends(check_api_key)])
    # app.include_router(WelcomeLeave.router,dependencies=[Depends(check_api_key)])
    # app.include_router(bot_status.router, dependencies=[Depends(check_api_key)])
    # app.include_router(lvlsystem.router, dependencies=[Depends(check_api_key)])
    # ------------------------------------------------------------
    app.include_router(dashboard.router)
    app.include_router(youtubeAPI.router)
    app.include_router(bot_server.router)
    app.include_router(img_link.router)
    app.include_router(WelcomeLeave.router)
    app.include_router(bot_status.router)
    app.include_router(lvlsystem.router)
    # ------------------------------------------------------------

    return app
