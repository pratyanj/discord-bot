import discord
print("addRole.py")
async def TO_member(payload,rule_channel_id,member_role_id):
  # Check if the reaction was added in the correct channel
  print(payload.channel_id)
  print(rule_channel_id)
  if payload.channel_id == rule_channel_id:
    # Replace 'YOUR_ROLE_ID' with the actual ID of the role to give
    role_id = member_role_id
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
