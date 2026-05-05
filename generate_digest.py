import os
import sys
import json
from datetime import datetime

import anthropic


def generate_digest() -> list[str]:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    now = datetime.now()
    weekday = now.strftime("%A").upper()
    month_day_year = now.strftime("%B %d, %Y").upper()
    weekday_title = now.strftime("%A")

    system_prompt = f"""You are a morning briefing generator for an ML engineer who works in computer vision at Flock Safety and is pursuing an OMSCS ML specialization at Georgia Tech.

Your job: produce a daily digest split into exactly 7 discrete sections. Each section will be sent as a separate Discord message, so each MUST be under 1900 characters.

TONE: Sharp, technical, direct. Written for someone who reads papers daily. No fluff, no filler sentences, no "exciting" or "groundbreaking" hedging.

FORMAT RULES:
- Use Discord markdown: **bold** for headers, <url> for links (angle brackets so Discord doesn't embed previews)
- Each section after the header starts with a divider line: ─────────────────────────────

SECTIONS (output as a JSON array of 7 strings):

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
arXiv: <arXiv ID> · <link>

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
- Output ONLY a JSON array of exactly 7 strings. No other text before or after.
- Each string is one Discord message. Keep each under 1900 characters.
- Use real, current arXiv papers found via web search. Do not fabricate paper titles, authors, or arXiv IDs.
- Use real news found via web search. Do not fabricate news items.
- The challenge answer must include where the approach breaks down.
- For the whitespace gap in the challenge, use the Braille blank character (U+2800) on separate lines — this creates visible space in Discord."""

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=8000,
            system=system_prompt,
            tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 10}],
            messages=[
                {
                    "role": "user",
                    "content": f"Generate today's morning briefing for {weekday_title}, {now.strftime('%B %d, %Y')}. Search arXiv for 3 recent papers (one CV, one DL, one RL), find a recent paleontology discovery or dinosaur fact, and find the latest notable AI/ML industry news. Then compile everything into the 7-section JSON array format specified in your instructions."
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
        sections = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse API response as JSON: {e}", file=sys.stderr)
        print(f"Raw response:\n{result_text}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(sections, list) or len(sections) != 7:
        print(f"ERROR: Expected a JSON array of 7 strings, got {type(sections).__name__} with {len(sections) if isinstance(sections, list) else 'N/A'} items.", file=sys.stderr)
        sys.exit(1)

    return sections


if __name__ == "__main__":
    sections = generate_digest()
    print(json.dumps(sections))
