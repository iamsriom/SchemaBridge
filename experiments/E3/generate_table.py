#!/usr/bin/env python3
"""Regenerate tab:e3_overall LaTeX from E3_PRIMARY_FINAL.csv."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "results" / "metrics" / "reproduced" / "E3_AUDIT"
FINAL = AUDIT / "metrics" / "E3_PRIMARY_FINAL.csv"
OUT = AUDIT / "latex" / "tab_e3_overall_verified.tex"

MODELS = [
    "CodeLlama-13B",
    "Llama-3.1-8B",
    "DeepSeek-Coder",
    "Claude Sonnet 4.6",
    "GPT-5.4-mini",
]
DATASETS = ["Enterprise-145", "RSchema", "SchemaBench"]
METRICS = [
    ("nGED", True),
    ("Hall", True),
    ("T", False),
    ("A", False),
    ("D", False),
    ("E", False),
    ("R", False),
]


def main() -> None:
    rows = list(csv.DictReader(FINAL.open()))
    by_ds: dict[str, list] = {ds: [] for ds in DATASETS}
    for r in rows:
        by_ds[r["Dataset"]].append(r)

    def fmt(ds_rows, metric, lower_better=False):
        vals = [float(r[f"{metric}_3dec"]) for r in ds_rows]
        best = min(vals) if lower_better else max(vals)
        out = []
        for r in ds_rows:
            v = float(r[f"{metric}_3dec"])
            s = f"{v:.3f}"
            if v == best:
                s = f"\\textbf{{{s}}}"
            out.append(s)
        return out

    lines = [
        "% Verified E3 PRIMARY (765 = 145/381/239). Evaluator: experiments/E3/evaluate_e3_primary.py",
        "\\begin{table*}[t]",
        "\\centering",
        "\\caption{Constructor isolation with frozen GPT-5.4-mini detailed descriptions.",
        "Mean nGED and four-dimensional hallucination (T/A/E/R; Domain excluded);",
        "micro-averaged structural $F_1$ for Tables (T), Attributes (A), Domain (D),",
        "Entity (E), and Referential integrity (R). Lower is better for nGED/Hall.;",
        "higher is better for $F_1$. Bold = best within each dataset (ties shared).}",
        "\\label{tab:e3_overall}",
        "\\resizebox{\\textwidth}{!}{%",
        "\\begin{tabular}{llccccccc}",
        "\\toprule",
        "Dataset & Constructor & nGED $\\downarrow$ & Hall. $\\downarrow$ & T & A & D & E & R \\\\",
        "\\midrule",
    ]
    for ds in DATASETS:
        ds_rows = sorted(by_ds[ds], key=lambda r: MODELS.index(r["Constructor"]))
        cols = {m: fmt(ds_rows, m, low) for m, low in METRICS}
        for i, r in enumerate(ds_rows):
            ds_cell = ds if i == 0 else ""
            lines.append(
                f"{ds_cell} & {r['Constructor']} & {cols['nGED'][i]} & {cols['Hall'][i]} & "
                f"{cols['T'][i]} & {cols['A'][i]} & {cols['D'][i]} & {cols['E'][i]} & {cols['R'][i]} \\\\"
            )
        if ds != DATASETS[-1]:
            lines.append("\\midrule")
    lines.extend(
        [
            "\\bottomrule",
            "\\end{tabular}%",
            "}",
            "\\end{table*}",
            "",
        ]
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
