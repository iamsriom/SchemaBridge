#!/usr/bin/env python3
"""Build audit/E0_PAPER_COMPARISON.csv against current manuscript targets.

Uses:
  * results/metrics/reproduced/E0_TABLE_V_FINAL.csv  (Direct, genuine protocol)
  * results/metrics/reproduced/E0_TABLE_VI_FINAL.csv (Direct + ARCHIVE_AGGREGATE / BLOCKED)

Does not invent metrics. Tolerance for 3dp PASS: abs(diff) <= 0.0005 or
rounded-to-3dp equals the manuscript cell.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOL = 0.0005
PAPER = json.loads((ROOT / "audit/E0_CURRENT_MANUSCRIPT_VALUES.json").read_text())
OUT = ROOT / "audit/E0_PAPER_COMPARISON.csv"

METRICS_V = ["nged", "halluc", "tables", "attributes", "domain", "entity", "referential"]
METRICS_VI = METRICS_V


def r3(x: float) -> float:
    return float(f"{x:.3f}")


def status_for(paper, recomputed) -> tuple[str, float | None, float | None]:
    if paper is None and recomputed is None:
        return "PASS", None, None  # both --
    if paper == "--" or paper is None:
        if recomputed is None:
            return "PASS", None, None
        return "MISMATCH", None, recomputed
    if recomputed is None:
        return "BLOCKED", float(paper), None
    p = float(paper)
    d = recomputed - p
    if abs(d) <= TOL or abs(r3(recomputed) - p) < 1e-12:
        return "PASS", p, recomputed
    return "MISMATCH", p, recomputed


def load_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num_or_none(s: str | None):
    if s is None or s == "" or s == "--":
        return None
    return float(s)


def main() -> int:
    tv = load_csv(ROOT / "results/metrics/reproduced/E0_TABLE_V_FINAL.csv")
    tvi = load_csv(ROOT / "results/metrics/reproduced/E0_TABLE_VI_FINAL.csv")
    rows: list[dict] = []

    for r in tv:
        key = f"{r['dataset']}|{r['model']}"
        paper_row = PAPER["tab:e0_overall"][key]
        for m in METRICS_V:
            paper = paper_row[m]
            recomputed = num_or_none(r.get(m))
            st, p, rec = status_for(paper, recomputed)
            diff = "" if rec is None or p is None else f"{rec - p:+.6f}"
            rows.append(
                {
                    "Table": "V",
                    "Dataset": r["dataset"],
                    "Model": r["model"],
                    "Method": "Direct",
                    "Metric": m,
                    "Paper": "" if paper is None else paper,
                    "Recomputed": "" if recomputed is None else f"{recomputed:.6f}",
                    "Round3": "" if recomputed is None else f"{r3(recomputed):.3f}",
                    "Difference": diff,
                    "Status": st,
                    "SourceStatus": r.get("status", ""),
                }
            )

    for r in tvi:
        if r["dataset"] != "RSchema":
            continue  # manuscript Table VI is RSchema-only
        if r["method"] == "Direct":
            key = f"{r['model']}|Direct"
        else:
            key = f"{r['model']}|{r['method']}"
        if key not in PAPER["tab:e0_baselines"]:
            # Table VI manuscript lists only the three open-weight models.
            continue
        paper_row = PAPER["tab:e0_baselines"][key]
        src = r.get("status") or ""
        for m in METRICS_VI:
            paper = paper_row[m]
            paper_disp = "--" if paper is None else paper
            recomputed = num_or_none(r.get(m))
            if src == "BLOCKED" and m != "domain":
                st, p, rec = "BLOCKED", (None if paper is None else float(paper)), None
            elif m == "domain":
                st, p, rec = status_for(None if paper is None else "--", recomputed)
                if paper is None and recomputed is None:
                    st = "PASS"
            else:
                st, p, rec = status_for(paper, recomputed)
                if src == "ARCHIVE_AGGREGATE" and st == "PASS":
                    st = "PASS_ARCHIVE"
                elif src == "ARCHIVE_AGGREGATE" and st == "MISMATCH":
                    st = "MISMATCH_ARCHIVE"
            diff = "" if rec is None or p is None else f"{rec - p:+.6f}"
            rows.append(
                {
                    "Table": "VI",
                    "Dataset": r["dataset"],
                    "Model": r["model"],
                    "Method": r["method"],
                    "Metric": m,
                    "Paper": paper_disp if paper_disp != "--" or m == "domain" else "--",
                    "Recomputed": (
                        "--"
                        if m == "domain" and recomputed is None
                        else ("" if recomputed is None else f"{recomputed:.6f}")
                    ),
                    "Round3": (
                        "--"
                        if m == "domain" and recomputed is None
                        else ("" if recomputed is None else f"{r3(recomputed):.3f}")
                    ),
                    "Difference": diff,
                    "Status": st,
                    "SourceStatus": src,
                }
            )

    fields = [
        "Table",
        "Dataset",
        "Model",
        "Method",
        "Metric",
        "Paper",
        "Recomputed",
        "Round3",
        "Difference",
        "Status",
        "SourceStatus",
    ]
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    # Summary counts
    from collections import Counter

    c = Counter(r["Status"] for r in rows)
    print(f"Wrote {OUT} ({len(rows)} cells)")
    for k, v in sorted(c.items()):
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
