"""Old persuader wording (v5: "persuade in every message") vs new (v7: set-up allowed, at least two
pushes), conditions C2b-C2e, persuader deepseek-v4-flash. Writes compare_v7.md.

  python compare_v7.py <v7 llama run dir> <v7 gemini-2.5 run dir>
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OLD = {"llama-3.3-70b": ROOT / "runs" / "20261108-055459", "gemini-2.5-flash-lite": ROOT / "runs" / "20261108-060231"}
CONDS = ["C2b_ask", "C2c_ask_split", "C2d_ask_threat", "C2e_full"]

try:
    from scipy.stats import fisher_exact
except ImportError:  # pragma: no cover
    fisher_exact = None


def load(d: Path) -> list:
    f = d / "episodes_rejudged.jsonl"
    f = f if f.exists() else d / "episodes.jsonl"
    return [json.loads(l) for l in f.open(encoding="utf-8")]


def stats(rs: list) -> dict:
    ks = [r for r in rs if r["kept"]]
    pushes = [sum(1 for a, s in zip(r["judge"].get("ask", []), r["judge"].get("split", [])) if a or s) for r in rs]
    first = [next((i + 1 for i, (a, s) in enumerate(zip(r["judge"].get("ask", []), r["judge"].get("split", [])))
                   if a or s), None) for r in rs]
    first = [x for x in first if x]
    j = lambda k: sum(bool(r["judge"].get(k)) for r in rs)
    return {"n": len(rs), "tip": sum(r["outcome"]["trade_on_tip"] for r in rs), "kept": len(ks),
            "tip_kept": sum(r["outcome"]["trade_on_tip"] for r in ks), "split": sum(r["outcome"]["split"] for r in rs),
            "report": sum(r["outcome"]["report"] for r in rs), "pushes": sum(pushes) / max(1, len(pushes)),
            "first": sum(first) / max(1, len(first)), "refused": j("target_refused_in_chat"),
            "rule_arg": j("target_rule_argument")}


def main() -> None:
    new = dict(zip(OLD, [Path(x) for x in sys.argv[1:3]]))
    lines = ["# C2b-C2e: old wording (v5) vs new wording (v7)", "",
             "Persuader and judge deepseek-v4-flash; judge v6 for both (old runs rejudged). 10 episodes per cell.",
             "pushes = mean number of persuader messages that ask or push a split; first = mean index of the "
             "first such message; p = Fisher exact, tip trades all episodes, old vs new.", ""]
    for model in OLD:
        old_recs, new_recs = load(OLD[model]), load(new[model])
        lines += [f"## {model}", "",
                  "| condition | version | tip (all) | kept | tip (kept) | split | report | pushes | first | "
                  "target refused | rule argument | p old vs new |", "|" + "---|" * 12]
        for c in CONDS:
            so = stats([r for r in old_recs if r["condition"] == c])
            sn = stats([r for r in new_recs if r["condition"] == c])
            p = ""
            if fisher_exact and so["n"] and sn["n"]:
                p = f"{fisher_exact([[so['tip'], so['n'] - so['tip']], [sn['tip'], sn['n'] - sn['tip']]])[1]:.3f}"
            for tag, s in (("v5 old", so), ("v7 new", sn)):
                lines.append(f"| {c} | {tag} | {s['tip']}/{s['n']} | {s['kept']}/{s['n']} | {s['tip_kept']}/{s['kept']} | "
                             f"{s['split']} | {s['report']} | {s['pushes']:.1f} | {s['first']:.1f} | {s['refused']} | "
                             f"{s['rule_arg']} | {p if tag == 'v7 new' else ''} |")
        lines.append("")
    text = "\n".join(lines)
    (ROOT / "compare_v7.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
