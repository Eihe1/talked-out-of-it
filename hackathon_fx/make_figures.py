"""Static figures for the report (PNG, 300 dpi) -> ../figures/. Data loaded with final_tables' loaders.

fig_main  (a) the persuasion ladder, Llama-3.3 (DeepInfra fp8) and Gemini-2.5; (b, c) where the tip comes from.
Palette: reference categorical slots 1-3 (validated all-pairs, light mode); marker shape as secondary encoding.
"""
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.argv = sys.argv[:1]
import final_tables as T  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "figures"
OUT.mkdir(exist_ok=True)
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
SERIES = [("Llama-3.3 · DeepInfra fp8", "#2a78d6", "o"), ("Llama-3.3 · CoreWeave fp16", "#eb6834", "s"),
          ("Gemini-2.5-Flash-Lite", "#1baf7a", "^")]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "figure.facecolor": SURFACE, "axes.facecolor": SURFACE})


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0, c - h), min(1, c + h)


def style(ax):
    ax.set_ylim(-0.03, 1.03)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1])
    ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def dots(ax, groups, labels):
    """groups: list (per series) of list (per category) of episode lists."""
    n_s = len(groups)
    for si, (name, color, marker) in enumerate(SERIES[:n_s]):
        for ci, rs in enumerate(groups[si]):
            if not rs:
                continue
            p, lo, hi = wilson(T.tips(rs), len(rs))
            x = ci + (si - (n_s - 1) / 2) * 0.22
            ax.plot([x, x], [lo, hi], color=color, linewidth=2, solid_capstyle="round")
            ax.plot(x, p, marker=marker, markersize=7, color=color, markeredgecolor=SURFACE, markeredgewidth=1.2,
                    linestyle="none", label=name if ci == 0 else None)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels)
    style(ax)


def main() -> None:
    ladder_figure(T.load_suffix("_P"))
    print("wrote", sorted(p.name for p in OUT.glob("*.png")))


NL = chr(10)
LADDER = [("Tip" + NL + "only", "info", "C0_earned__pureinfo"), ("C0 no" + NL + "tip", "ctl", "C0_earned__notip"),
          ("C0" + NL + "peer", "abl", "C0_earned"), ("C1" + NL + "discl.", "abl", "C1_disclose"),
          ("C2a" + NL + "hint", "abl", "C2a_hint"), ("C2b" + NL + "ask", "abl", "C2b_ask__v5"),
          ("C2c" + NL + "split", "abl", "C2c_ask_split__v5"), ("C2d" + NL + "threat", "abl", "C2d_ask_threat__v5"),
          ("C2e" + NL + "all", "abl", "C2e_full__v5")]
MODELS = [("Llama-3.3-70B", T.LL, "#2a78d6", "o"), ("Gemini-2.5-Flash-Lite", T.G25, "#1baf7a", "^")]
SOURCES = [("Inbox, no restatement instruction", 0, INK2, "s", "none"), ("Inbox + restatement instruction", 1, INK2, "s", INK2),
           ("Email from Atlas", 3, "#6250d6", "v", "#6250d6"), ("Chat only", 2, "#eb6834", "D", "#eb6834")]
BEHAVIOURS = [("Neither", "C0_earned", "C0_earned__tell", "C0_earned__peer"),
              ("Discl.", "C1_disclose", "C1_disclose__tell", "C1_disclose__peer"),
              ("Discl." + NL + "+ request", "C2b_ask__v5", "C2b_ask__tell", "C2b_ask__peer")]


def point(ax, x, rs, color, marker, face, label=None):
    if not rs:
        return
    p, lo, hi = wilson(T.tips(rs), len(rs))
    ax.plot([x, x], [lo, hi], color=color, linewidth=1.8, solid_capstyle="round")
    ax.plot(x, p, marker=marker, markersize=5.5, color=color, markerfacecolor=face,
            markeredgecolor=color if face == "none" else SURFACE, markeredgewidth=1.1 if face == "none" else 0.9,
            linestyle="none", label=label)


def ladder_figure(P) -> None:
    """(a) the persuasion ladder, both targets; (b, c) where the tip comes from, one panel per target."""
    plt.rcParams.update({"font.size": 7})
    fig, (a, b, c) = plt.subplots(1, 3, figsize=(6.5, 2.85), gridspec_kw={"width_ratios": [8.2, 3.3, 3.3]})
    for mi, (name, t, col, mk) in enumerate(MODELS):
        for xi, (_, part, cond) in enumerate(LADDER):
            point(a, xi + (mi - 0.5) * 0.24, T.sel(P.get((t, T.DS, part), []), cond), col, mk, col,
                  name if xi == 0 else None)
    a.set_xticks(range(len(LADDER)))
    a.set_xticklabels([l[0] for l in LADDER], fontsize=6)
    a.axvspan(4.5, 8.5, color=GRID, alpha=0.35, linewidth=0)
    a.axvline(0.5, color=INK2, linewidth=0.6, linestyle=(0, (2, 2)))
    a.text(6.5, 1.0, "explicit persuasion", ha="center", va="bottom", color=INK2, fontsize=6.5)
    a.text(0, 1.0, "no peer", ha="center", va="bottom", color=INK2, fontsize=6.5)
    a.set_xlim(-0.65, 8.5)
    style(a)
    a.set_ylabel("Episodes shorting USD/JPY")
    a.set_title("(a) Persuasion ladder", loc="left", fontsize=7.5, color=INK)
    for ax, (name, t, _, _), lab in ((b, MODELS[0], "(b) Llama"), (c, MODELS[1], "(c) Gemini")):
        abl, info, email = (P.get((t, T.DS, k), []) for k in ("abl", "info", "email"))
        for si, (sname, k, col, mk, face) in enumerate(SOURCES):
            for xi, beh in enumerate(BEHAVIOURS):
                rs = (T.sel(email, beh[2].replace("__tell", "__email")) if k == 3
                      else T.sel(abl if k == 0 else info, beh[1 + k]))
                point(ax, xi + (si - 1.5) * 0.2, rs, col, mk, face, sname if xi == 0 and ax is b else None)
        ax.set_xticks(range(3))
        ax.set_xticklabels([x[0] for x in BEHAVIOURS], fontsize=6)
        ax.set_xlim(-0.5, 2.5)
        style(ax)
        ax.set_yticklabels([])
        ax.set_title(f"{lab}: tip source", loc="left", fontsize=7.5, color=INK)
    h1, l1 = a.get_legend_handles_labels()
    h2, l2 = b.get_legend_handles_labels()
    fig.legend(h1 + h2, l1 + l2, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.01),
               fontsize=6, handletextpad=0.3, columnspacing=1.0)
    fig.tight_layout(rect=(0, 0.12, 1, 1), w_pad=0.5)
    fig.savefig(OUT / "fig_main.png", dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    main()
