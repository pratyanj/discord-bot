import json
import requests
import re
import os

from discord.ext import commands, tasks

@tasks.loop(seconds=30)
async def checkforvideos():
  with open("youtubedata.json", "r") as f:
    data=json.load(f)
  
  #printing here to show
  print("Now Checking!")

  #checking for all the channels in youtubedata.json file
  for youtube_channel in data:
    print(f"Now Checking For {data[youtube_channel]['channel_name']}")
    #getting youtube channel's url
    channel = f"https://www.youtube.com/channel/{youtube_channel}"

    #getting html of the /videos page
    html = requests.get(channel+"/videos").text

    #getting the latest video's url
    #put this line in try and except block cause it can give error some time if no video is uploaded on the channel
    try:
      latest_video_url = "https://www.youtube.com/watch?v=" + re.search('(?<="videoId":").*?(?=")', html).group()
    except:
      continue

    #checking if url in youtubedata.json file is not equals to latest_video_url
    if not str(data[youtube_channel]["latest_video_url"]) == latest_video_url:

      #changing the latest_video_url
      data[str(youtube_channel)]['latest_video_url'] = latest_video_url

      #dumping the data
      with open("youtubedata.json", "w") as f:
        json.dump(data, f)

      #getting the channel to send the message
      discord_channel_id = data[str(youtube_channel)]['notifying_discord_channel']
      discord_channel = bot.get_channel(int(discord_channel_id))

      #sending the msg in discord channel
      #you can mention any role like this if you want
      msg = f"@everone {data[str(youtube_channel)]['channel_name']} Just Uploaded A Video Or He is Live Go Check It Out: {latest_video_url}"
      #if you'll send the url discord will automaitacly create embed for it
      #if you don't want to send embed for it then do <{latest_video_url}>

      await discord_channel.send(msg)