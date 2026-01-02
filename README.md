# Constrained Toasts Bot

A Telegram bot that picks words from configurable whitelist and blacklist collections. Perfect for creating unconventional, humorous, or constrained word combinations for toasts, games, or creative writing prompts. Originally used for a toasting new year game, where people need to make a toast without saying picked blacklisted words, but mentioning picked whitelisted ones (hence, the naming).

## Features

- **Word Management**: Add and remove words from whitelist and blacklist collections
- **Random Toast Generation**: Generate toasts with specified numbers of words from each list
- **Persistent Storage**: Words are stored in text files that persist between bot restarts
- **Docker Support**: Easy deployment with Docker and Docker Compose
- **Telegram Integration**: Fully featured Telegram bot with command-based interface

## Commands

- `/start` - Show help and available commands
- `/add_whitelist <word>` - Add a word to the whitelist
- `/add_blacklist <word>` - Add a word to the blacklist
- `/remove_whitelist <word>` - Remove a word from the whitelist
- `/remove_blacklist <word>` - Remove a word from the blacklist
- `/get_toast b <N> w <M>` - Generate a toast with N blacklist words and M whitelist words

## Example Usage

```
/add_whitelist sunshine
/add_blacklist storm
/get_toast b 2 w 3
```

Output:
```
Blacklist (2): storm, chaos
Whitelist (3): sunshine, happiness, friendship
```

## Setup

### Prerequisites

- Python 3.13+
- A Telegram Bot Token (obtain from [@BotFather](https://t.me/BotFather))
- [uv](https://docs.astral.sh/uv/) package manager (recommended) or pip

### Local Development

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd constrained-toasts
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Set your Telegram bot token:
   ```bash
   export TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```

4. Run the bot:
   ```bash
   uv run python src/bot.py
   ```

### Docker Deployment

1. Set your bot token in a `.env` file:
   ```bash
   echo "TELEGRAM_BOT_TOKEN=your_bot_token_here" > .env
   ```

2. Build and run with Docker Compose:
   ```bash
   docker-compose up -d
   ```

### Environment Variables

- `TELEGRAM_BOT_TOKEN` (required): Your Telegram bot token
- `TOAST_DATA_DIR` (optional): Custom directory for storing word lists (defaults to `data/`)

## Project Structure

```
constrained-toasts/
├── src/
│   └── bot.py              # Main bot application
├── data/
│   ├── whitelist.txt       # Whitelist words (one per line)
│   └── blacklist.txt       # Blacklist words (one per line)
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Docker build configuration
├── pyproject.toml          # Python project configuration
└── README.md               # This file
```

## How It Works

The bot maintains two word collections.

When generating a toast with `/get_toast b <N> w <M>`, the bot randomly selects:
- N words from the blacklist
- M words from the whitelist

Words are normalized (lowercased, whitespace cleaned) and deduplicated automatically.
