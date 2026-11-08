"""Collect the target's reasoning before its decisions, for reading (11-08 late). Writes reasoning.md.

  python -X utf8 reasoning_read.py            # all runs whose target had reasoning on (_Rthink, _Q731*)
Reasoning text is model output from our own runs. Shown per episode: outcome, trade rationale, and the
reasoning at each decision step that placed a trade or reported (trimmed).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "runs"
MARKERS = ("_Rthink", "_Xthink", "_Q731")


def main(limit: int = 900) -> None:
    L = ["# 被劝方的推理内容（reasoning_read.py 生成）", ""]
    for d in sorted(ROOT.iterdir()):
        if not any(m in d.name for m in MARKERS) or not (d / "episodes.jsonl").exists():
            continue
        recs = [json.loads(l) for l in (d / "episodes.jsonl").open(encoding="utf-8")]
        L += [f"## {d.name}", ""]
        for r in recs:
            o = r["outcome"]
            L.append(f"### {r['episode']}：照消息下单 {o['trade_on_tip']}，举报 {o['report']}，正常交易 {o['other_trade']}")
            for t in r["trades"]:
                L.append(f"- 下单 {t['side']} {t['pair']} {t.get('notional_usd')}：理由“{str(t.get('rationale', ''))[:300]}”")
            for s in r["decision_trace"]:
                names = [c["name"] for c in s.get("tool_calls") or []]
                if s.get("reasoning") and any(n in ("place_trade", "report_to_compliance") for n in names):
                    txt = " ".join(str(s["reasoning"]).split())
                    L.append(f"- 第 {s['step']} 步（{', '.join(names)}）前的推理：{txt[:limit]}{'…' if len(txt) > limit else ''}")
            L.append("")
    out = Path(__file__).resolve().parent / "reasoning.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {out} ({len(L)} lines)")


if __name__ == "__main__":
    main()
