"""Confirmatory test written down before running (HACKATHON_1DAY.md §13.1).

  python confirm_analysis.py <llama confirm run dir> <gemini-2.5 confirm run dir>   -> confirm.md

Primary: new episodes only, both models pooled, tip trades C3a_reframe vs C2b_ask, one-sided Fisher
(C3a higher), alpha 0.05, all episodes. Secondary: per model; chat refusal (C3a lower); kept episodes.
Afterwards: pooled estimates with the exploratory v8 episodes (descriptive only).
"""
import json
import sys
from pathlib import Path

from scipy.stats import fisher_exact

ROOT = Path(__file__).resolve().parent
EXPLORATORY = {"llama": ["20261108-073154_llama-33-70b-instruct_by_deepseek-v4-flash",
                         "20261108-133843_llama-33-70b-instruct_by_deepseek-v4-flash"],
               "gemini-2.5": ["20261108-073156_gemini-25-flash-lite_by_deepseek-v4-flash",
                              "20261108-133845_gemini-25-flash-lite_by_deepseek-v4-flash"]}


def load(d: Path) -> list:
    f = d / "episodes_rejudged.jsonl"
    f = f if f.exists() else d / "episodes.jsonl"
    return [json.loads(l) for l in f.open(encoding="utf-8")]


def count(rs: list, cond: str, key: str = "tip", kept_only: bool = False) -> tuple:
    rs = [r for r in rs if r["condition"] == cond and (r["kept"] or not kept_only)]
    if key == "tip":
        k = sum(r["outcome"]["trade_on_tip"] for r in rs)
    else:
        k = sum(bool(r["judge"].get(key)) for r in rs)
    return k, len(rs)


def test(a: tuple, b: tuple, alternative: str) -> float:
    return fisher_exact([[a[0], a[1] - a[0]], [b[0], b[1] - b[0]]], alternative=alternative)[1]


def main() -> None:
    new = {"llama": load(Path(sys.argv[1])), "gemini-2.5": load(Path(sys.argv[2]))}
    pooled = new["llama"] + new["gemini-2.5"]
    a, b = count(pooled, "C3a_reframe"), count(pooled, "C2b_ask")
    p = test(a, b, "greater")
    out = ["# 确认性检验结果（confirm_analysis.py 生成）", "",
           "按 HACKATHON_1DAY.md §13.1 事先写下的方法。只用新样本下结论。", "",
           f"**主要检验**（两个模型合并，全部局）：换说法 {a[0]}/{a[1]}，基准 {b[0]}/{b[1]}，"
           f"单侧 Fisher p = {p:.4f} → {'支持假设' if p < 0.05 else '不支持假设'}（α = 0.05）", "",
           "| 范围 | 换说法 | 基准 | 单侧 p（换说法更高） |", "|---|---|---|---|"]
    for name, rs in new.items():
        a1, b1 = count(rs, "C3a_reframe"), count(rs, "C2b_ask")
        out.append(f"| {name}，全部局 | {a1[0]}/{a1[1]} | {b1[0]}/{b1[1]} | {test(a1, b1, 'greater'):.4f} |")
        a2, b2 = count(rs, "C3a_reframe", kept_only=True), count(rs, "C2b_ask", kept_only=True)
        out.append(f"| {name}，保留的局 | {a2[0]}/{a2[1]} | {b2[0]}/{b2[1]} | {test(a2, b2, 'greater'):.4f} |")
    ar, br = count(pooled, "C3a_reframe", "target_refused_in_chat"), count(pooled, "C2b_ask", "target_refused_in_chat")
    out += ["", f"**次要**：被劝方在聊天里拒绝（合并）：换说法 {ar[0]}/{ar[1]}，基准 {br[0]}/{br[1]}，"
                f"单侧 p（换说法更低）= {test(ar, br, 'less'):.4f}",
            f"用了换说法（裁判判定，换说法组）：{count(pooled, 'C3a_reframe', 'tactic_reframe')[0]}/{a[1]}", ""]
    out += ["## 新旧合并的估计（描述性，不用于下结论）", "", "| 模型 | 换说法 | 基准 |", "|---|---|---|"]
    for name, dirs in EXPLORATORY.items():
        old = [r for d in dirs for r in load(ROOT / "runs" / d)]
        rs = old + new[name]
        a3, b3 = count(rs, "C3a_reframe"), count(rs, "C2b_ask")
        out.append(f"| {name} | {a3[0]}/{a3[1]} ({a3[0] / a3[1]:.0%}) | {b3[0]}/{b3[1]} ({b3[0] / b3[1]:.0%}) |")
    text = "\n".join(out)
    (ROOT / (sys.argv[3] if len(sys.argv) > 3 else "confirm.md")).write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
