# Morning Digest

Automated daily morning briefing delivered to a Discord channel.

## How to run

```bash
pip install -r requirements.txt --quiet
python generate_digest.py | python send_digest.py
```

## Environment variables

All secrets come from environment variables. Never hardcode tokens or keys.

- `ANTHROPIC_API_KEY` — Anthropic API key for Claude
- `DISCORD_BOT_TOKEN` — Discord bot token with message send permissions
- `DISCORD_CHANNEL_ID` — Discord channel ID to post the digest in

## Architecture

- `generate_digest.py` — Calls Claude API with web search to produce a 7-section digest. Checks `digest_history.json` to avoid repeating past content. Outputs a JSON array of strings to stdout and updates the history file.
- `send_digest.py` — Reads the JSON array from stdin and sends each section as a separate message to the configured Discord channel with 1-second delays.
- `digest_history.json` — Tracks previously sent papers (arXiv IDs), dino species, news headlines, and challenge topics. Keeps the last 30 entries. Commit this file so history persists across cloud runs.
