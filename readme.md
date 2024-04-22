Here is a draft README.md file for your open source Discord bot repository:

# Discord Bot

This is an open source Discord bot written in Python using the discord.py library.

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
2. Create and activate a virtual environment
   - `python -m venv venv`
   - `source venv/bin/activate` (Linux/MacOS) or `venv\Scripts\activate` (Windows)
3. Install requirements: `pip install -r requirements.txt`
4. Add your bot token in `config.py`
5. Run the bot: `python bot.py`

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

## Contributing

Contributions are welcome! Please open an issue or submit a pull request if you would like to contribute to this open source project.

## Credits

- [discord.py](https://discordpy.readthedocs.io/en/stable/)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)

Let me know if you would like me to expand or modify anything in this open source README draft. I'd be happy to help further polish it for your repository!
