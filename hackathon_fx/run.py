"""Run the pilot.

  python run.py --mock --n 5                     # no API calls, no cost
  python run.py --conditions C0_earned C2_persuade --n 10 --model deepseek/deepseek-v4-flash

Every episode is checked by an LLM judge (judge.py); the summary is printed for all episodes
and for "kept" episodes only (persuader followed its instructions).
Logs go to runs/<timestamp>/episodes.jsonl and summary.txt.
"""
import argparse
import json
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import scenario as S
from episode import run_episode
from judge import MockJudge, finish, judge_episode
from llm import DEFAULT_PINS, DEFAULT_REASONING, LLM, MockLLM, Usage

PRICES = {  # USD per 1M tokens, OpenRouter list prices checked 2026-11-08
    "deepseek/deepseek-v4-flash": (0.091, 0.182),
    "deepseek/deepseek-v4.1-flash": (0.051, 0.567),
    "deepseek/deepseek-v3.2": (0.260, 0.380),
}


def table(title: str, conds: list, by: dict) -> list:
    lines = [f"\n== {title}",
             f"{'condition':16s} n   tip  split report other | chat: refused rule_arg says_report | err"]
    for c in conds:
        rs = by.get(c, [])
        k = lambda key: sum(r["outcome"][key] for r in rs)
        jk = lambda key: sum(bool(r.get("judge", {}).get(key)) for r in rs)
        lines.append(f"{c:16s} {len(rs):<3d} {k('trade_on_tip'):<4d} {k('split'):<5d} {k('report'):<6d} "
                     f"{k('other_trade'):<5d} |       {jk('target_refused_in_chat'):<7d} {jk('target_rule_argument'):<8d} "
                     f"{jk('target_said_will_report'):<11d} | {sum(bool(r['errors']) for r in rs)}")
    # Reports by object, per condition (user, 11-08: never pool across conditions or objects)
    lines.append(f"  reports by object: tip_itself / persuader_past_trade / persuader_solicitation")
    for c in conds:
        rs = by.get(c, [])
        objs = Counter(o for r in rs for o in r.get("judge", {}).get("report_objects", []))
        lines.append(f"  {c:20s} {objs['tip_itself']} / {objs['persuader_past_trade']} / "
                     f"{objs['persuader_solicitation']}")
    return lines


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--conditions", nargs="+", default=S.ABLATION)
    ap.add_argument("--n", type=int, default=10, help="episodes per condition")
    ap.add_argument("--model", default="deepseek/deepseek-v4-flash", help="target model")
    ap.add_argument("--persuader-model", default=None, help="defaults to --model")
    ap.add_argument("--judge-model", default=None, help="defaults to --model")
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--cap-tokens", type=int, default=3_000_000)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--pin", default="", help="extra or overriding pins, e.g. 'model=deepinfra/fp8;model2=...'")
    ap.add_argument("--no-pin", action="store_true", help="do not pin providers (runs before 11-08 14:30)")
    ap.add_argument("--no-reasoning", action="store_true", help="do not request reasoning explicitly")
    ap.add_argument("--reasoning-on", default="", help="extra models to run with reasoning enabled, ';'-separated")
    ap.add_argument("--tag", default="", help="suffix for the run directory name")
    a = ap.parse_args()

    pins = {} if a.no_pin else dict(DEFAULT_PINS)
    pins.update(dict(x.split("=", 1) for x in a.pin.split(";") if "=" in x))
    prov = lambda m: [pins[m]] if m in pins else None
    reas = {} if a.no_reasoning else dict(DEFAULT_REASONING)
    reas.update({m: {"enabled": True} for m in a.reasoning_on.split(";") if m})
    rsn = lambda m: reas.get(m)
    pin, pout = PRICES.get(a.model, (1.0, 2.0))
    usage = Usage(pin, pout, a.cap_tokens)
    pm, jm = a.persuader_model or a.model, a.judge_model or a.model
    if a.mock:
        mk = lambda i: (MockLLM(usage, seed=i), MockLLM(usage, seed=10_000 + i), MockJudge(i))
        host = "mock"
    else:
        mk = lambda i: (LLM(pm, usage, a.temperature, providers=prov(pm), reasoning=rsn(pm)),
                        LLM(a.model, usage, a.temperature, providers=prov(a.model), reasoning=rsn(a.model)),
                        LLM(jm, usage, 0.0, max_tokens=6000, providers=prov(jm), reasoning=rsn(jm)))
        host = mk(0)[1].host()
    print(f"endpoint={host} target={a.model} persuader={pm} judge={jm} conditions={a.conditions} n={a.n}")

    slug = lambda m: m.split("/")[-1].replace(".", "")[:24]
    tag = slug(a.model) if pm == a.model else f"{slug(a.model)}_by_{slug(pm)}"
    tag += f"_{a.tag}" if a.tag else ""
    out_dir = Path(__file__).resolve().parent / "runs" / f"{time.strftime('%Y%m%d-%H%M%S')}_{tag}"
    out_dir.mkdir(parents=True, exist_ok=False)
    (out_dir / "config.json").write_text(json.dumps(
        {"target": a.model, "persuader": pm, "judge": jm, "conditions": a.conditions, "n": a.n,
         "temperature": a.temperature, "mock": a.mock,
         "scenario_version": S.SCENARIO_VERSION, "pins": pins,
         "reasoning": reas}, indent=1), encoding="utf-8")
    jobs = [(c, i) for c in a.conditions for i in range(a.n)]

    def job(ci):
        c, i = ci
        lp, lt, lj = mk(a.conditions.index(c) * 1000 + i)
        rec = run_episode(c, lp, lt, f"{c}-{i:03d}")
        if not S.has_chat(c):        # C0 control without chat: nothing to judge
            rec.update({"judge": {"skipped": "no chat"}, "oversteps": [], "kept": True})
            return rec
        rec["judge"] = judge_episode(rec, lj)
        return finish(rec)

    results = []
    with ThreadPoolExecutor(max_workers=a.workers) as ex, \
            (out_dir / "episodes.jsonl").open("w", encoding="utf-8") as f:
        for rec in ex.map(job, jobs):
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()
            results.append(rec)
            j = rec["judge"]
            print(f"{rec['episode']}: {rec['outcome']['category']}  kept={rec['kept']}  "
                  f"oversteps={rec['oversteps']}  ask={j.get('ask')}"
                  + (f"  ERR {rec['errors'][0]}" if rec["errors"] else ""))

    by_all, by_kept = defaultdict(list), defaultdict(list)
    for r in results:
        by_all[r["condition"]].append(r)
        if r["kept"]:
            by_kept[r["condition"]].append(r)
    # User, 11-08: reports mean different things per condition; never pool across conditions.
    lines = table("all episodes (per condition; do not pool)", a.conditions, by_all)
    lines += table("kept (persuader followed instructions)", a.conditions, by_kept)
    lines.append("\n" + usage.summary())
    if getattr(usage, "by", None):
        lines.append("cost by model and provider:\n" + usage.breakdown())
    text = "\n".join(lines)
    print(text)
    (out_dir / "summary.txt").write_text(text, encoding="utf-8")
    print(f"logs: {out_dir}")


if __name__ == "__main__":
    main()
