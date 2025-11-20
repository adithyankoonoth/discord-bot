# Internship News Discord Bot

A Python-based Discord bot that automatically fetches internship and early-career opportunities from multiple sources and posts them into a Discord channel.

---

## Features
- Fetches internship updates from multiple websites (scraping, RSS, APIs).
- Cleans, normalizes, and removes duplicate listings.
- Automatically posts updates on a schedule.
- Configurable sources, keywords, and polling interval.
- Admin commands for managing sources and manual posting.
- Lightweight and easy to deploy (Docker, VM, serverless, etc.).

---

## Quick Start

### Prerequisites
- Python 3.10+
- Discord bot token
- Optional: Docker

### Installation
```bash
git clone https://github.com/adithyankoonoth/discord-bot.git
cd discord-bot
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate         # Windows
pip install -r requirements.txt
