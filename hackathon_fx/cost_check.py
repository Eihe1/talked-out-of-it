"""Per-episode tokens and provider-reported cost for runs with a Llama-3.3 or Gemini-2.5 target."""
import json
import os
import re
from pathlib import Path

PAT = re.compile(r"prompt_tokens=(\d+) completion_tokens=(\d+).*provider_reported_cost=\$([\d.]+)")
LEGACY = {"20261108-052648": "llama-3.3-70b-instruct", "20261108-055459": "llama-3.3-70b-instruct",
          "20261108-051530": "llama-3.3-70b-instruct", "20261108-053013": "gemini-2.5-flash-lite",
          "20261108-060231": "gemini-2.5-flash-lite", "20261108-051309": "gemini-2.5-flash-lite"}
for d in sorted(Path("runs").iterdir()):
    s = d / "summary.txt"
    if not s.exists():
        continue
    m = PAT.search(s.read_text(encoding="utf-8"))
    if not m or float(m[3]) == 0:
        continue
    cfg = json.loads((d / "config.json").read_text(encoding="utf-8")) if (d / "config.json").exists() else {}
    tgt = cfg.get("target", LEGACY.get(d.name, "?")).split("/")[-1]
    per = cfg.get("persuader", "deepseek-v4-flash").split("/")[-1]
    if not ("llama-3.3" in tgt or "gemini-2.5" in tgt):
        continue
    n = sum(1 for _ in (d / "episodes.jsonl").open(encoding="utf-8"))
    pt, ct, c = int(m[1]), int(m[2]), float(m[3])
    print(f"{d.name[:15]} target={tgt:22s} persuader={per:22s} n={n:3d} prompt/ep={pt // n:6d} "
          f"compl/ep={ct // n:5d} cost/ep=${c / n:.4f}")
