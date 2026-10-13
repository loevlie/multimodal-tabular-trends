"""
Step 2: run the keyword rule on every accepted paper and count per year.

Usage:  python count.py
Reads:  data/*.json            (from download.py)
Writes: results/flagged_papers.csv   every paper the rule flags, with a link
        results/counts_by_year.csv   the numbers behind the plots
"""
import json
from pathlib import Path

import pandas as pd

from rule import classify, is_tabular_paper

DATA = Path(__file__).parent / "data"
RESULTS = Path(__file__).parent / "results"
CONFERENCES = {"iclr": "ICLR", "icml": "ICML", "nips": "NeurIPS"}
YEARS = range(2019, 2027)

# Decisions that mean "accepted at the main conference" in the Paper Copilot files.
# Everything else (Reject, Withdraw, Desk Reject, Journal track, ...) is left out.
ACCEPTED = {"Poster", "Oral", "Spotlight", "Talk", "Top-25%", "Top-5%", "Accept",
            "ICLR 2026 ConditionalPoster", "ICLR 2026 ConditionalOral"}


def load_accepted_papers():
    rows = []
    for conf, name in CONFERENCES.items():
        for year in YEARS:
            path = DATA / f"{conf}{year}.json"
            if not path.exists():
                print(f"note: no data for {name} {year} (run download.py; NeurIPS 2026 is not in the snapshot)")
                continue
            for paper in json.loads(path.read_text(encoding="utf-8")):
                if paper.get("status") in ACCEPTED:
                    rows.append({
                        "conference": name,
                        "year": year,
                        "title": (paper.get("title") or "").strip(),
                        "abstract": (paper.get("abstract") or "").strip(),
                        "link": paper.get("site", ""),
                    })
    return pd.DataFrame(rows)


def main():
    papers = load_accepted_papers()
    print(f"{len(papers):,} accepted papers")

    labels = [classify(t, a) for t, a in zip(papers.title, papers.abstract)]
    papers["image_table"] = [x["image_table"] for x in labels]
    papers["text_table"] = [x["text_table"] for x in labels]
    papers["tabular"] = [is_tabular_paper(t, a) for t, a in zip(papers.title, papers.abstract)]
    papers["multimodal_tabular"] = papers.image_table | papers.text_table

    by_year = papers.groupby("year")
    counts = pd.DataFrame({
        "conferences": by_year.conference.apply(lambda c: " + ".join(sorted(set(c)))),
        "accepted_papers": by_year.size(),
        "tabular_papers": by_year.tabular.sum(),
        "image_table": by_year.image_table.sum(),
        "text_table_only": by_year.apply(lambda d: (d.text_table & ~d.image_table).sum()),
        "multimodal_tabular": by_year.multimodal_tabular.sum(),
    })
    counts["percent_of_tabular"] = (100 * counts.multimodal_tabular / counts.tabular_papers).round(1)

    RESULTS.mkdir(exist_ok=True)
    counts.to_csv(RESULTS / "counts_by_year.csv")
    flagged = papers[papers.multimodal_tabular].drop(columns=["abstract", "tabular", "multimodal_tabular"])
    flagged.to_csv(RESULTS / "flagged_papers.csv", index=False)
    print(counts.to_string())


if __name__ == "__main__":
    main()
