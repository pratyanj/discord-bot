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
      # print(guild.id)
      # servers[guild.name] = guild.id
      server_info = {
              "name": str(guild.name),
              "id": str(guild.id),
              "icon_url": str(guild.icon)
          }
      servers[guild.name] = server_info
      # print(servers)
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
  @app.get("/GET_status/")
  async def GET_status(guild:int):
    Guild = bot.get_guild(guild)
    if Guild:
      Welcome = db.collection("servers").document(str(guild)).collection("Welcome_Leave").document("welcome").get()
      Welcome_status = Welcome.to_dict()['status']
      print("Welcome_status:",Welcome_status)
      Leave = db.collection("servers").document(str(guild)).collection("Welcome_Leave").document("leave").get()
      Leave_status = Leave.to_dict()['status']
      print("Leave_status:",Leave_status)
      Join_Member_Role = db.collection("servers").document(str(guild)).collection("moderation").document("Join_Member_Role").get()
      Join_Member_Role_status = Join_Member_Role.to_dict()['status']
      print("Join_Member_Role_status:",Join_Member_Role_status)
      image_share = db.collection("servers").document(str(guild)).collection("moderation").document("image_share").get()
      image_share_status = image_share.to_dict()['status']
      print("IMG_Only_status:",image_share_status)
      link_share = db.collection("servers").document(str(guild)).collection("moderation").document("link_share").get()
      link_share_status = link_share.to_dict()['status']
      print("Link_Only_status:",link_share_status)
      member_count = db.collection("servers").document(str(guild)).collection("moderation").document("member_count").get()
      member_count_status = member_count.to_dict()['status']
      print("Memeber_Count_status:",member_count_status)
      Levels = db.collection("servers").document(str(guild)).collection("Levels").document("levelsetting").get()
      Levels_status = Levels.to_dict()['status']
      youtube_notification = db.collection("servers").document(str(guild)).collection("moderation").document("Youtube_Notification").get()
      youtube_notification_status = youtube_notification.to_dict()['status']
      
      print("Levels_status:",Levels_status)
      
      data = {
        "img_only_status": image_share_status,
        "link_only_status": link_share_status,
        "memeber_count_status": member_count_status,
        "welcome_status": Welcome_status,
        "leave_status": Leave_status,
        "levelsetting_status": Levels_status,
        "join_member_role_status": Join_Member_Role_status,
        "youtube_notification_status": youtube_notification_status,
      }
      return data
    else:
      return f"{guild} is not a valid server id"
    

      
      
  # ---------------------------POST METOD---------------------------------

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
      # print(guild, role)
      Guild = bot.get_guild(guild)
      Channel = bot.get_channel(channel)
      if Guild:
        for rol in Guild.roles:
            # print("Role_id:",rol.id)
            if rol.id == role:
                server = db.collection("servers").document(str(Guild.id)).collection("moderation").document("Join_Member_Role") 
                sevrer_data = server.get()
                # print("sevrer_data:",sevrer_data.to_dict())
                data = {"status":True,"channel_id":f'{Channel.id}','channel_name':f'{Channel.name}','role_id':f"{rol.id}",'role_name':f"{rol.name}"}
                # print('DATA:',data)
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
      doc_ref = db.collection("servers").document(str(guild)).collection("moderation").document("image_share")
      doc_ref.update({'status': status})
      return {"status": status}
    else:
      return f"{guild} is not a valid server id"
  
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
  # --------------------------------------------------------------------------------
  # ----------------------------LEVEL SYSTEM----------------------------------------
  # @app.post("/LVLsystem_status/",dependencies=[Depends(check_api_key)])
  @app.post("/LVLsystem_status/")
  async def LVLsystem_status(guild:int,status:bool):
    Guild = bot.get_guild(guild)
    if Guild:
      doc_ref = db.collection("servers").document(str(guild)).collection("Levels").document("levelsetting")
      doc_ref.update({'status': status})
      return {"status": status}
    else:
      return f"{guild} is not a valid server id"
    
  # @app.post("/LVLsystem_status/",dependencies=[Depends(check_api_key)])
  @app.post("/LVL_role_set/")
  async def LVL_role_set(guild:int,role:int,lvl:int):
    Guild = bot.get_guild(guild)
    if Guild:
      for rol in Guild.roles:
        if rol.id == role:
  #         lvlsys = {
  #     "status": True,
  #     "role_id": {},
  #     "role_set":{}
  # }
          doc_ref = db.collection("servers").document(str(guild)).collection("Levels").document("levelsetting")
          doc_ref.update({'role_id': {str(rol.id): rol.name}})
          doc_ref.update({'role_set': {str(lvl): str(rol.id)}})
      return {"message": f"Level role set to {rol.name} ({rol.id})"}
    else:
      return f"{guild} is not a valid server id"
    
  # @app.post("/youtube_notification_status/",dependencies=[Depends(check_api_key)])
  @app.post("/youtube_notification_status/")
  async def youtube_notification_status(guild:int,status:bool):
    Guild = bot.get_guild(guild)
    if Guild:
      doc_ref = db.collection("servers").document(str(guild)).collection("moderation").document("Youtube_Notification")
      doc_ref.update({'status': status})
      return {"status": status}
    else:
      return f"{guild} is not a valid server id"
    
  # @app.post("/youtube_notification/",dependencies=[Depends(check_api_key)])
  @app.post("/youtube_notification/")
  async def youtube_notification(guild:int,channel:int):
    Guild = bot.get_guild(guild)
    if Guild:
      Channel = bot.get_channel(channel)
      if Channel:
        doc_ref = db.collection("servers").document(str(guild)).collection("moderation").document("Youtube_Notification")
        doc = doc_ref.get()
        data_update = { "status":True,
                        "channel_id":str(Channel.id),
                        "channel_name":str(Channel.name),
                        }
        doc_ref.update(data_update)
        return {"message": f" Youtube notification set to |**{Channel.name}**|**({Channel.id})**|"}
      
      else:
        return f"{channel} is not a valid channel id"
    else:
      return f"{guild} is not a valid server id"
    
  # @app.post("/Set_YT_channel/",dependencies=[Depends(check_api_key)])
  @app.post("/Set_YT_channel/")
  async def Set_YT_channel(guild:int,YT_channel_usr:str):
    Guild = bot.get_guild(guild)
    if Guild:
      doc_ref = db.collection("servers").document(str(guild)).collection("moderation").document("Youtube_Notification")
      doc = doc_ref.get()
      data_set = {"youtube_channels":[YT_channel_usr]}
      all_YT_channels = doc.to_dict()["youtube_channels"]
      if YT_channel_usr in all_YT_channels:
          return {"message": f"Youtube notification is already set to |**{YT_channel_usr}**|"}
      else:
          all_YT_channels.append(YT_channel_usr)
          doc_ref.update({"youtube_channels":all_YT_channels})
      return {"message": f" Youtube notification set for |**{YT_channel_usr}**|"}
      
    else:
      return f"{guild} is not a valid server id"
    
  # @app.post("/remove_YT_channel/",dependencies=[Depends(check_api_key)])
  @app.post("/remove_YT_channel/")
  async def remove_YT_channel(guild:int,YT_channel_usr:str):
    Guild = bot.get_guild(guild)
    if Guild:
      doc_ref = db.collection("servers").document(str(guild)).collection("moderation").document("Youtube_Notification")
      doc = doc_ref.get()
      all_YT_channels = doc.to_dict()["youtube_channels"]
      print(all_YT_channels)
      YT_video = doc.to_dict()["videos"]
      print(YT_video)
      if YT_channel_usr in all_YT_channels:
        print("yes")
        all_YT_channels.remove(YT_channel_usr)
        del YT_video[YT_channel_usr]
        print(YT_video)
        doc_ref.update({"youtube_channels":all_YT_channels,"videos":YT_video})
        return {"message": f" Youtube notification removed for |**{YT_channel_usr}**|"}
      else:
        return {"message": f" Youtube notification is already removed for |**{YT_channel_usr}**|"}
    else:
      return f"{guild} is not a valid server id"
  # --------------------------------------------------------------------------------
  # --------------------------------------------------------------------------------
  return app