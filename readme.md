Here is a draft README.md file for your Discord bot repository:

# Discord Bot

This is a Discord bot written in Python using the discord.py library. 

## Features

- Welcome and leave messages
- Delete image/link messages in specific channels  
- Leveling system
- Custom prefixes per server
- Create categories
- Clear messages
- Check bot permissions

## Setup

1. Clone the repository
2. Install requirements: `pip install -r requirements.txt`
3. Add your bot token in `config.py`
4. Run the bot: `python bot.py`

## Commands

- `$setwelcomechannel` - Set the welcome channel
- `$setleavechannel` - Set the leave channel  
- `$setprefix` - Set custom prefix
- `$createCAT` - Create a category
- `$clear` - Clear messages
- `$checkpermissions` - Check bot permissions
- `$lvl` - Check your level
- `$rank` - Check your rank
- `$lvlsys enable` - Enable leveling system
- `$lvlsys disable` - Disable leveling system

## Database

The bot uses Firestore for:

- Storing server prefixes
- Level system data
- Welcome/leave channels

## Deployment

The bot can be deployed to Heroku or any other hosting platform that supports Python applications.

## Credits

- [discord.py](https://discordpy.readthedocs.io/en/stable/)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)

Let me know if you would like me to expand or modify anything in this README draft. I'd be happy to help further polish it for your repository!