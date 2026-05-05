# Morning Digest

Automated daily morning briefing delivered via Discord DM.

## How to run

```bash
pip install -r requirements.txt --quiet
python generate_digest.py | python send_digest.py
```

## Environment variables

All secrets come from environment variables. Never hardcode tokens or keys.

- `ANTHROPIC_API_KEY` — Anthropic API key for Claude
- `DISCORD_BOT_TOKEN` — Discord bot token with DM permissions
- `DISCORD_USER_ID` — Discord user ID to receive the digest

## Architecture

- `generate_digest.py` — Calls Claude API with web search to produce a 7-section digest. Outputs a JSON array of strings to stdout.
- `send_digest.py` — Reads the JSON array from stdin, opens a Discord DM channel, and sends each section as a separate message with 1-second delays.
