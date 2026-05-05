# Morning Digest

Automated morning briefing that gets delivered straight to my Discord DMs every day. I built this because I was tired of manually checking arXiv, scrolling through AI Twitter, and losing track of papers that were actually relevant to my work. Now I wake up and it's just there.

The whole thing runs headlessly through a Claude Code routine on Anthropic's cloud.

## What it sends me

Every morning I get a sequence of Discord messages with:

- **3 arXiv papers** — one computer vision, one deep learning, one reinforcement learning. Each paper gets a quick breakdown: what the problem was before this paper, how it works, concrete results (actual numbers, not vibes), and why I should care given what I'm working on at Flock Safety or studying in OMSCS.
- **A dinosaur fact** — because I like dinosaurs and it's my digest so I can put whatever I want in it. Recent discoveries, specific species, actual publications.
- **An AI/ML industry news item** — one thing that actually matters from the last few days, with a real metric attached.
- **A daily challenge question** — hard CV or ML question with the answer hidden behind a wall of whitespace so I don't accidentally spoil it while scrolling. The answer includes where the approach falls apart, because knowing the limitations matters more than knowing the textbook answer.

The tone is technical and to the point. No "In this exciting new development..." filler. Written the way I'd actually want to read it at 7am.

## How it works

Two scripts piped together:

```
python generate_digest.py | python send_digest.py
```

`generate_digest.py` hits the Anthropic API with web search enabled so it can pull real, current papers and news — not hallucinated ones. It returns the digest as a JSON array of 7 strings, one per Discord message (Discord has a 2000 char limit per message, so it has to be split up).

`send_digest.py` reads that JSON from stdin, opens a DM channel with me through the Discord API, and fires off each section with a 1-second delay between messages to avoid rate limits. No discord.py, just raw HTTP calls with httpx.

## Setup

### Prerequisites

- Python 3.10+
- An Anthropic API key
- A Discord bot token (the bot needs to share a server with you and have DM permissions)
- Your Discord user ID (enable Developer Mode in Discord settings, right-click your name, Copy User ID)

### Install

```bash
git clone https://github.com/BattleTaco/Morning_Digest.git
cd Morning_Digest
pip install -r requirements.txt
```

### Environment variables

Copy `.env.example` and fill in your values:

```bash
cp .env.example .env
```

```
ANTHROPIC_API_KEY=your-key-here
DISCORD_BOT_TOKEN=your-bot-token-here
DISCORD_USER_ID=your-user-id-here
```

Don't commit your `.env` — it's already in `.gitignore`.

### Run it manually

```bash
python generate_digest.py | python send_digest.py
```

### Run it on a schedule

I use a Claude Code routine so it fires automatically every morning without any local machine running. Set the three environment variables in the routine's cloud environment and point it at this repo.

## Project structure

```
├── CLAUDE.md            # Instructions for Claude Code on how to run the project
├── generate_digest.py   # Calls Anthropic API w/ web search, outputs JSON to stdout
├── send_digest.py       # Reads JSON from stdin, sends to Discord DM
├── requirements.txt     # anthropic, httpx
├── .env.example         # Template for required env vars
└── .gitignore           # Keeps .env out of version control
```

## Error handling

Both scripts fail loudly. If the API call fails, you'll see exactly what went wrong. If a Discord message fails to send, it tells you which section broke. Nothing gets silently swallowed — if something's wrong I want to know about it, not find out hours later that I just didn't get a digest.
