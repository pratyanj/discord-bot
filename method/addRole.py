import discord
# print("addRole.py")
async def TO_member(payload,db):
  # Check if the reaction was added in the correct channel
  guild_id = str(payload.member.guild.id)  # Convert guild.id to a string

  print(guild_id)
  print(f'Member: {payload.member}')

  server = db.collection("servers").document(guild_id).collection("moderation").document("Join_Member_Role") 
  sevrer_data = server.get()
  print(sevrer_data.to_dict())
  if sevrer_data.to_dict()["status"]  == False :
    print("Role adding system is off")
    return
  print(sevrer_data.to_dict())
  if sevrer_data.to_dict()["channel_id"] == '':
    print('Channel ID not configured. Returning.')
    return 
  if sevrer_data.to_dict()["role_id"] == '':
    print('Role ID not configured. Returning.')
    return
  rule_channel_id = sevrer_data.to_dict()['channel_id']
  role_id = sevrer_data.to_dict()['role_id']
  print(payload.channel_id)
  print(rule_channel_id)
  if int(payload.channel_id) == int(rule_channel_id):
    # Replace 'YOUR_ROLE_ID' with the actual ID of the role to give
    role_id = int(role_id)
    role = discord.utils.get(payload.member.guild.roles, id=role_id)

    print(f'Role: {role}')
    print(f'Member: {payload.member}')
    print(f'Emoji: {payload.emoji}')
    print(f'Role ID: {role_id}') 
    print(f"player_role_id: {payload.member.roles}")
    if role and str(payload.emoji) == '\U00002705':
      if role not in payload.member.roles:# white_check_mark emoji
        try:
          # Give the role to the user who added the reaction
          await payload.member.add_roles(role)
        except discord.Forbidden:
          print('Bot does not have the required permissions.')
  else:
    print('Reaction added in the wrong channel.')

async def TO_member1(payload,db):
  # Check if the reaction was added in the correct channel
  guild_id = str(payload.member.guild.id)  # Convert guild.id to a string

  print(guild_id)
  print(f'Member: {payload.member}')

  server = await db.reactionverificationrole.find_unique(where={"server_id": payload.member.guild.id})
  ss = await db.server.find_unique(where={"id": payload.member.guild.id})
  if server == None:
    print(f"Server {payload.member.guild.name} not found in DB")
    await payload.member.guild.get_channe(int(ss.log_channel)).send(f"{payload.member.guild.id} is not found in our database!\nFor Join Role") 
    return
  print(server)
  if server.status  == False :
    print("Role adding system is off")
    await payload.member.guild.get_channe(int(ss.log_channel)).send(f"Role adding system is off\nFor Join Role")
    return
  if server.channel_id  == '' or 0 or None:
    print('Channel ID not configured. Returning.')
    await payload.member.guild.get_channel(int(ss.log_channel)).send(f"Channel ID not configured for {payload.member.guild.name}!\nFor Join Role")
    return 
  if server.role_id  == '' or 0 or None:
    print('Role ID not configured. Returning.')
    await payload.member.guild.get_channel(int(ss.log_channel)).send(f"Role ID not configured for {payload.member.guild.name}! \nFor Join Role")
    return
  rule_channel_id = server.channel_id
  role_id = server.role_id
  print(payload.channel_id)
  print(rule_channel_id)
  if int(payload.channel_id) == int(rule_channel_id):
    # Replace 'YOUR_ROLE_ID' with the actual ID of the role to give
    role_id = int(role_id)
    role = discord.utils.get(payload.member.guild.roles, id=role_id)

    print(f'Role: {role}')
    print(f'Member: {payload.member}')
    print(f'Emoji: {payload.emoji}')
    print(f'Role ID: {role_id}') 
    print(f"player_role_id: {payload.member.roles}")
    if role and str(payload.emoji) == '\U00002705':
      if role not in payload.member.roles:# white_check_mark emoji
        try:
          # Give the role to the user who added the reaction
          await payload.member.add_roles(role)
        except discord.Forbidden:
          print('Bot does not have the required permissions.')
          await payload.member.guild.get_channel(int(ss.log_channel)).send(f"Bot does not have the required permissions.\nFor Join Role ")
  else:
    await payload.member.guild.get_channel(int(ss.log_channel)).send(f"Reaction added in wrong channel {payload.channel_id} instead of {rule_channel_id} for {payload.member.guild.name}\nFor Join Role")
    print('Reaction added in the wrong channel.')
