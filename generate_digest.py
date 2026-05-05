import os
import sys
import json
from datetime import datetime
from pathlib import Path

import anthropic

HISTORY_FILE = Path(__file__).parent / "digest_history.json"
MAX_HISTORY_ENTRIES = 30


def load_history() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    try:
        return json.loads(HISTORY_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return []


def save_history(history: list[dict]) -> None:
    if len(history) > MAX_HISTORY_ENTRIES:
        history = history[-MAX_HISTORY_ENTRIES:]
    HISTORY_FILE.write_text(json.dumps(history, indent=2))


def build_history_block(history: list[dict]) -> str:
    if not history:
        return ""

    lines = ["PREVIOUSLY COVERED — do NOT repeat any of these:\n"]
    for entry in history:
        lines.append(f"  Date: {entry.get('date', '?')}")
        for paper in entry.get("papers", []):
            lines.append(f"    Paper: {paper['title']} (arXiv: {paper['arxiv_id']})")
        if entry.get("dino_species"):
            lines.append(f"    Dino: {entry['dino_species']}")
        if entry.get("news_headline"):
            lines.append(f"    News: {entry['news_headline']}")
        if entry.get("challenge_topic"):
            lines.append(f"    Challenge: {entry['challenge_topic']}")
        lines.append("")

    return "\n".join(lines)


def generate_digest() -> list[str]:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    history = load_history()

    now = datetime.now()
    weekday = now.strftime("%A").upper()
    month_day_year = now.strftime("%B %d, %Y").upper()
    weekday_title = now.strftime("%A")

    history_block = build_history_block(history)

    system_prompt = f"""You are a morning briefing generator for an ML engineer who works in computer vision at Flock Safety and is pursuing an OMSCS ML specialization at Georgia Tech.

Your job: produce a daily digest split into exactly 7 discrete sections. Each section will be sent as a separate Discord message, so each MUST be under 1900 characters.

TONE: Sharp, technical, direct. Written for someone who reads papers daily. No fluff, no filler sentences, no "exciting" or "groundbreaking" hedging.

FORMAT RULES:
- Use Discord markdown: **bold** for headers
- Links MUST be full URLs with https:// wrapped in angle brackets, e.g. <https://arxiv.org/abs/2505.12345> — never omit https://
- Each section after the header starts with a divider line: ─────────────────────────────

{history_block}

OUTPUT FORMAT — return a JSON object (not an array) with two keys:

"sections": an array of exactly 7 strings (one per Discord message)
"metadata": an object with these fields for history tracking:
  "papers": array of 3 objects, each with "arxiv_id" (string) and "title" (string)
  "dino_species": string — the species name used in the dino fact
  "news_headline": string — short headline of the news item
  "challenge_topic": string — 3-5 word topic label for the challenge question

SECTIONS (the 7 strings in "sections"):

1. HEADER MESSAGE:
```
**BRIEFING -- {weekday}, {month_day_year}**
Golden Valley, MN · {weekday_title}
```

2. PAPER 1 — Computer Vision:
Search arXiv for a recent (last 7 days) computer vision paper. Format:
```
─────────────────────────────
**[CV]** <paper title>
<authors> · <institution>
arXiv: <arXiv ID> · <https://arxiv.org/abs/XXXX.XXXXX>

**Status quo:** <what problem existed before this paper — one line>
**How it works:** <the core method in 1-2 lines>
**Result:** <concrete numbers — accuracy, FPS, mAP, etc.>
**So what:** <tie it to work at Flock Safety (license plate recognition, vehicle detection, urban surveillance cameras, edge deployment) or OMSCS ML coursework>
```

3. PAPER 2 — Deep Learning:
Same format as above but tag is **[DL]** and topic is deep learning (architectures, training methods, optimization, generalization). Search arXiv for a recent paper.

4. PAPER 3 — Reinforcement Learning:
Same format but tag is **[RL]** and topic is reinforcement learning. Search arXiv for a recent paper.

5. DINOSAUR/PALEONTOLOGY FACT:
Search for a recent paleontology discovery or interesting dinosaur fact.
```
─────────────────────────────
**🦕 DINO FACT**
**<Species name>** — <source publication>, <date>
<3-4 sentences of detail about the discovery or fact. Be specific — measurements, time period, significance.>
```

6. AI/ML INDUSTRY NEWS:
Search for the most notable AI/ML industry news from the past few days.
```
─────────────────────────────
**📡 AI/ML NEWS**
**<Headline>**
<Source> · <Date>
<2-3 sentences. Include a concrete benchmark number or metric. Explain why it matters to practitioners.>
```

7. DAILY CHALLENGE:
```
─────────────────────────────
**🧠 DAILY CHALLENGE** — <topic area>

**Q:** <A hard computer vision or ML question. Should require genuine understanding, not just recall. Think interview-level or qualifying-exam-level.>

⠀
⠀
⠀
⠀
⠀
⠀
⠀
⠀
⠀
⠀
⠀
⠀
⠀
⠀
⠀
⠀
⠀
⠀
⠀
⠀

**A:** <Detailed answer in 3-5 sentences. End with one sentence about where this approach breaks down or its key limitation.>
```

CRITICAL INSTRUCTIONS:
- Output ONLY the JSON object. No other text before or after.
- Each section string must be under 1900 characters.
- Use real, current arXiv papers found via web search. Do not fabricate paper titles, authors, or arXiv IDs.
- Use real news found via web search. Do not fabricate news items.
- The challenge answer must include where the approach breaks down.
- For the whitespace gap in the challenge, use the Braille blank character (U+2800) on separate lines.
- Do NOT reuse any paper, species, news item, or challenge topic from the PREVIOUSLY COVERED list."""

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=8000,
            system=system_prompt,
            tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 10}],
            messages=[
                {
                    "role": "user",
                    "content": f"Generate today's morning briefing for {weekday_title}, {now.strftime('%B %d, %Y')}. Search arXiv for 3 recent papers (one CV, one DL, one RL), find a recent paleontology discovery or dinosaur fact, and find the latest notable AI/ML industry news. Then compile everything into the JSON object format specified in your instructions with both 'sections' and 'metadata' keys."
                }
            ],
        )
    except anthropic.APIError as e:
        print(f"ERROR: Anthropic API call failed: {e}", file=sys.stderr)
        sys.exit(1)

    result_text = ""
    for block in response.content:
        if block.type == "text":
            result_text += block.text

    if not result_text.strip():
        print("ERROR: No text content returned from API.", file=sys.stderr)
        sys.exit(1)

    text = result_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        result = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse API response as JSON: {e}", file=sys.stderr)
        print(f"Raw response:\n{result_text}", file=sys.stderr)
        sys.exit(1)

    if isinstance(result, list):
        sections = result
        metadata = {}
    elif isinstance(result, dict):
        sections = result.get("sections", [])
        metadata = result.get("metadata", {})
    else:
        print(f"ERROR: Unexpected response type: {type(result).__name__}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(sections, list) or len(sections) != 7:
        print(f"ERROR: Expected 7 sections, got {len(sections) if isinstance(sections, list) else 'N/A'}.", file=sys.stderr)
        sys.exit(1)

    history_entry = {
        "date": now.strftime("%Y-%m-%d"),
        "papers": metadata.get("papers", []),
        "dino_species": metadata.get("dino_species", ""),
        "news_headline": metadata.get("news_headline", ""),
        "challenge_topic": metadata.get("challenge_topic", ""),
    }
    history.append(history_entry)
    save_history(history)
    print(f"History updated: {HISTORY_FILE} ({len(history)} entries)", file=sys.stderr)

    return sections


if __name__ == "__main__":
    sections = generate_digest()
    print(json.dumps(sections))
