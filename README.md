# IG-tribbles (dribbles) 

A Discord bot that tracks your Instagram followers and following over time using CSV exports.

## Features

- DM support and auto-detection of CSV uploads
- Track who followed/unfollowed you between uploads
- Visualizations of trends, growth rates, and relationships
- Search for specific users in your data

## Commands

| Command | Description |
|---------|-------------|
| `/upload` | Upload your Instagram CSV file |
| `/stats` | View your dashboard |
| `/trend` | See follower count trend |
| `/growth` | View growth rate between uploads |
| `/changes` | See changes from last upload |
| `/nonfollowers` | See people you don't follow back |
| `/breakdown` | View pie chart of relationships |
| `/history` | View upload history |
| `/search` | Search for a username |

## Setup

### 1. Create Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create new application → Add Bot → Copy token
3. Enable "Message Content Intent"

### 2. Invite Bot

1. OAuth2 → URL Generator
2. Select: `bot`, `applications.commands`
3. Permissions: `Send Messages`, `Attach Files`, `Embed Links`, `Use Slash Commands`

### 3. Install & Run
```bash
pip install -r requirements.txt
cp .env.example .env
# Add your DISCORD_TOKEN to .env
python bot.py
```

## Export Instagram Data

1. Instagram → Settings → Your Activity → Download Your Information
2. Select "Followers and following" → Format: **CSV**
3. Upload the CSV to the bot

## Usage
```bash
# With nix-shell
nix-shell
bot

# With Docker
docker-compose up -d
docker-compose logs -f
```

## Data Storage

All data stored in `follower_data.db` (SQLite), isolated per user.

## License

MIT
