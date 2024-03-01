# api.py
from fastapi import FastAPI

import config

import discord
# from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI,Depends,Request,HTTPException
from starlette.responses import RedirectResponse
from fastapi.security import APIKeyHeader

def myAPI(bot,db):
  print("API started")
  # ---------------------api------------------------
  app = FastAPI()
  API_KEY = config.API_KEY
  # Create an instance of the APIKeyHeader security scheme
  api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

  # Define a dependency that will check the API key
  async def check_api_key(api_key: str = Depends(api_key_header)):
      # if not api_key or api_key != f"Bearer {API_KEY}":
      if not api_key or api_key != API_KEY:
          raise HTTPException(status_code=401, detail="Enter invalid API key")
      
  # --------------main page as docs----------------------------
  @app.get("/", include_in_schema=False)
  async def redirect_to_docs():
      response = RedirectResponse(url='/docs')
      return response
    
  # ------------------------------------------------------------
  # List of server 
  # @app.get("/server_List/",dependencies=[Depends(check_api_key)])

  @app.get("/server_List/")
  async def server_List():
    servers = {}
    for guild in bot.guilds:
      print(guild.id)
      # servers[guild.name] = guild.id
      server_info = {
              "name": str(guild.name),
              "id": str(guild.id),
              "icon_url": str(guild.icon)
          }
      servers[guild.name] = server_info
      print(servers)
    return servers
  # List of channenels according to server id
  # @app.get("/server_Channels_List/{guild}",dependencies=[Depends(check_api_key)])
  @app.get("/server_Channels_List/")
  async def server_Channels_List(guild:int):
    channelList = {}
    Guild = bot.get_guild(guild)
    for channel in Guild.channels:
      if isinstance(channel, discord.TextChannel):
        channelList[channel.name] = str(channel.id)
    return channelList
  # List of roles according to server id
  # @app.get("/server_Roles_List/",dependencies=[Depends(check_api_key)])
  @app.get("/server_Roles_List/")
  async def server_Roles_List(guild:int):
    Roles_List = {}
    Guild = bot.get_guild(guild)
    if Guild:
      for role in Guild.roles:
        Roles_List[role.name] = str(role.id)
      return Roles_List
    else:
      return f"{guild} is not a valid server id"


  # @app.post("/welcome_status_GET/",dependencies=[Depends(check_api_key)])
  @app.get("/welcome_status_GET/")
  async def welcome_status_GET(guild:int):
    Guild = bot.get_guild(guild)
    if Guild:
      doc_ref = db.collection("servers").document(str(guild)).collection("Welcome_Leave").document("welcome").get()
      status = doc_ref.to_dict()['status']
      return {"status": status}
    else:
      return f"{guild} is not a valid server id"
    
    
  # ---------------------------POST METOD---------------------------------

  # server welcome message
  # @app.post("/welcome_status/",dependencies=[Depends(check_api_key)])
  @app.post("/welcome_status/")
  async def welcome_status(guild:int,status:bool):
    Guild = bot.get_guild(guild)
    if Guild:
      doc_ref = db.collection("servers").document(str(guild)).collection("Welcome_Leave").document("welcome")
      doc_ref.update({'status': status})
      return {"status": status}
    else:
      return f"{guild} is not a valid server id"
    
    
  # @app.post("/welcome_message/",dependencies=[Depends(check_api_key)])
  @app.post("/welcome_message/")
  async def welcome_message(guild:int,message:str):
    Guild = bot.get_guild(guild)
    if Guild:
      doc_ref = db.collection("servers").document(str(guild)).collection("Welcome_Leave").document("welcome")
      doc_ref.update({'message': message})
      return {"message": message}
    else:
      return f"{guild} is not a valid server id"
    
  # @app.post("/welcome_channel_set/",dependencies=[Depends(check_api_key)])
  @app.post("/welcome_channel_set/")
  async def welcome_channel_set(guild:int,channel:int):
    Guild = bot.get_guild(guild)
    if Guild:
      for chann in Guild.channels:
        if chann.id == channel:
          doc_ref = db.collection("servers").document(str(guild)).collection("Welcome_Leave").document("welcome")
          doc_ref.update({'channel_id': str(chann.id)})
          doc_ref.update({'channel_name': chann.name})
      return {"message": f"Welcome channel set to {chann.name} ({chann.id})"}
    else:
      return f"{guild} is not a valid server id"
  #join member role
  @app.post("/join_member_role/")
  async def join_member_role(guild:int, channel:int,role:int):
      print(guild, role)
      Guild = bot.get_guild(guild)
      Channel = bot.get_channel(channel)
      if Guild:
        for rol in Guild.roles:
            print("Role_id:",rol.id)
            if rol.id == role:
                server = db.collection("servers").document(str(Guild.id)).collection("moderation").document("Join_Member_Role") 
                sevrer_data = server.get()
                print("sevrer_data:",sevrer_data.to_dict())
                data = {"status":True,"channel_id":f'{Channel.id}','channel_name':f'{Channel.name}','role_id':f"{rol.id}",'role_name':f"{rol.name}"}
                print('DATA:',data)
                server.set(data)
                return data
        else:
          return f"{role} is not a valid role"
          
      else:
        return f"{guild} is not a valid server id"
      
  # @app.post("/link_channel_switch/",dependencies=[Depends(check_api_key)])
  @app.post("/link_channel_status/")
  async def link_channel_switch(guild:int,status:bool):
    Guild = bot.get_guild(guild)
    if Guild:
      doc_ref = db.collection("servers").document(str(guild)).collection("moderation").document("Link_Only")
      doc_ref.update({'status': status})
      return {"status": status}
    else:
      return f"{guild} is not a valid server id"
        
  # @app.post("/IMG_channel_switch/",dependencies=[Depends(check_api_key)])
  @app.post("/IMG_channel_status/")
  async def IMG_channel_switch(guild:int,status:bool):
    Guild = bot.get_guild(guild)
    if Guild:
      doc_ref = db.collection("servers").document(str(guild)).collection("moderation").document("IMG_Only")
      doc_ref.update({'status': status})
      return {"status": status}
    else:
      return f"{guild} is not a valid server id"
  
  return app
# --------------------------------------------------------------------------------