"""Which providers served our calls? Uses OpenRouter's activity endpoint (daily, per endpoint).

  python provider_activity.py [YYYY-MM-DD ...]

Prints only aggregates by model and provider (requests, tokens, cost). The API key is read from
../pilot/.env by llm.load_env() and never printed.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from collections import defaultdict

from llm import load_env


def fetch(date: str | None) -> list:
    url = "https://openrouter.ai/api/v1/activity" + (f"?date={date}" if date else "")
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {os.environ['PILOT_API_KEY']}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8")).get("data", [])


def main() -> None:
    load_env()
    dates = sys.argv[1:] or [None]
    agg = defaultdict(lambda: [0, 0, 0.0])
    for d in dates:
        try:
            rows = fetch(d)
        except urllib.error.HTTPError as e:
            print(f"{d or 'last 30 days'}: HTTP {e.code} {e.read().decode('utf-8', 'ignore')[:200]}")
            continue
        for x in rows:
            key = (x.get("date", "")[:10], x.get("model", "?"), x.get("provider_name", "?"))
            agg[key][0] += int(x.get("requests", 0) or 0)
            agg[key][1] += int(x.get("prompt_tokens", 0) or 0)
            agg[key][2] += float(x.get("usage", 0) or 0)
    for (day, model, prov), (n, pt, cost) in sorted(agg.items()):
        if any(k in model for k in ("llama", "deepseek", "gemini", "claude")):
            print(f"{day} {model:40s} {prov:20s} requests={n:6d} prompt_tokens={pt:9d} cost=${cost:.4f}")


if __name__ == "__main__":
    main()
