"""Retention (kept episodes) and overstep types per run, after rejudging."""
import json
import os
from collections import Counter
from pathlib import Path

for d in sorted(Path("runs").iterdir()):
    name = d.name
    if "_" not in name or name.endswith("deepseek-v4-pro") or (name.endswith("deepseek-v4-flash") and "_by_" not in name):
        continue
    f = d / "episodes_rejudged.jsonl"
    f = f if f.exists() else d / "episodes.jsonl"
    if not f.exists():
        continue
    recs = [json.loads(l) for l in f.open(encoding="utf-8")]
    if len(recs) < 20:
        continue
    old = sum(bool(r.get("kept_old")) for r in recs) if any("kept_old" in r for r in recs) else "-"
    why = Counter(o for r in recs for o in r.get("oversteps", []))
    print(f"{name:55s} kept {sum(r['kept'] for r in recs):2d}/{len(recs)} (before {old}) {dict(why)}")
