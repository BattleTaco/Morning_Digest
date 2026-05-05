import os
import sys
import json
import time

import httpx

DISCORD_API_BASE = "https://discord.com/api/v10"


def get_env_or_fail(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        print(f"ERROR: {name} environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    return value


def open_dm_channel(token: str, user_id: str) -> str:
    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json",
    }
    payload = {"recipient_id": user_id}

    with httpx.Client() as client:
        resp = client.post(f"{DISCORD_API_BASE}/users/@me/channels", headers=headers, json=payload)

    if resp.status_code != 200:
        print(f"ERROR: Failed to open DM channel. Status {resp.status_code}: {resp.text}", file=sys.stderr)
        sys.exit(1)

    return resp.json()["id"]


def send_message(token: str, channel_id: str, content: str, section_label: str) -> None:
    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json",
    }
    payload = {"content": content}

    with httpx.Client() as client:
        resp = client.post(f"{DISCORD_API_BASE}/channels/{channel_id}/messages", headers=headers, json=payload)

    if resp.status_code != 200:
        print(f"ERROR: Failed to send {section_label}. Status {resp.status_code}: {resp.text}", file=sys.stderr)
        sys.exit(1)

    print(f"Sent: {section_label}")


def main():
    token = get_env_or_fail("DISCORD_BOT_TOKEN")
    user_id = get_env_or_fail("DISCORD_USER_ID")

    raw = sys.stdin.read().strip()
    if not raw:
        print("ERROR: No input received on stdin.", file=sys.stderr)
        sys.exit(1)

    try:
        sections = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse stdin as JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(sections, list):
        print(f"ERROR: Expected a JSON array, got {type(sections).__name__}.", file=sys.stderr)
        sys.exit(1)

    section_labels = [
        "Header",
        "Paper 1 (CV)",
        "Paper 2 (DL)",
        "Paper 3 (RL)",
        "Dino Fact",
        "AI/ML News",
        "Daily Challenge",
    ]

    channel_id = open_dm_channel(token, user_id)
    print(f"DM channel opened: {channel_id}")

    for i, section in enumerate(sections):
        label = section_labels[i] if i < len(section_labels) else f"Section {i + 1}"
        send_message(token, channel_id, section, label)
        if i < len(sections) - 1:
            time.sleep(1)

    print(f"\nDigest delivered successfully. {len(sections)} messages sent.")


if __name__ == "__main__":
    main()
