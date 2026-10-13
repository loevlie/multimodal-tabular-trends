"""
Step 3: draw the two plots.

Usage:  python plot.py
Reads:  results/counts_by_year.csv   (from count.py)
Writes: results/multimodal_tabular_papers.png
        results/share_of_tabular_papers.png
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

RESULTS = Path(__file__).parent / "results"
GREY, ORANGE, BLACK = "#868C92", "#C2410C", "#16181A"
FIRST_SHARE_YEAR = 2021  # before 2021 there are fewer than 15 tabular papers a year, too few for a percentage

counts = pd.read_csv(RESULTS / "counts_by_year.csv")
# Mark years that are missing a conference (e.g. NeurIPS 2026 not published yet in the snapshot).
counts["label"] = [str(y) + ("*" if "NeurIPS" not in c else "") for y, c in zip(counts.year, counts.conferences)]
note = ("Accepted papers at ICLR, ICML and NeurIPS. Flagged by the keyword rule in rule.py.\n"
        "* NeurIPS list for this year not yet in the data snapshot (ICLR + ICML only).")

plt.rcParams.update({"font.size": 12, "axes.spines.top": False, "axes.spines.right": False})

# Plot 1: how many papers per year, split by image vs text
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.bar(counts.label, counts.text_table_only, color=GREY, label="Table + text")
ax.bar(counts.label, counts.image_table, bottom=counts.text_table_only, color=ORANGE, label="Table + images")
for x, total in enumerate(counts.multimodal_tabular):
    ax.text(x, total + 0.15, str(total), ha="center", va="bottom")
ax.set_ylabel("Papers")
ax.set_title("Multimodal tabular papers at ICLR, ICML and NeurIPS", loc="left", fontweight="bold")
handles, names = ax.get_legend_handles_labels()
ax.legend(handles[::-1], names[::-1], frameon=False, loc="upper left")
fig.text(0.01, 0.01, note, fontsize=8, color=GREY)
fig.tight_layout(rect=(0, 0.08, 1, 1))
fig.savefig(RESULTS / "multimodal_tabular_papers.png", dpi=300)

# Plot 2: what share of tabular papers are multimodal
recent = counts[counts.year >= FIRST_SHARE_YEAR]
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.bar(recent.label, recent.percent_of_tabular, color=BLACK)
for x, (pct, n, total) in enumerate(zip(recent.percent_of_tabular, recent.multimodal_tabular, recent.tabular_papers)):
    ax.text(x, pct + 0.15, f"{pct:.0f}%\n({n} of {total})", ha="center", va="bottom", fontsize=10)
ax.set_ylim(0, recent.percent_of_tabular.max() * 1.4)
ax.set_ylabel("% of tabular papers")
ax.set_title("Share of tabular papers that are multimodal", loc="left", fontweight="bold")
fig.text(0.01, 0.01, note, fontsize=8, color=GREY)
fig.tight_layout(rect=(0, 0.08, 1, 1))
fig.savefig(RESULTS / "share_of_tabular_papers.png", dpi=300)

print("saved results/multimodal_tabular_papers.png and results/share_of_tabular_papers.png")
