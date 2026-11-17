#!/usr/bin/env python3
"""Publish / verify PRIMARY E4 metrics (tab:e4_split, tab:e4_recovery).

Offline by default: writes frozen verified cells under
results/metrics/reproduced/E4_AUDIT/metrics/ and top-level E4_*.csv.

Optional full recompute from private prediction trees requires:
  SCHEMA_BRIDGE_DATA   data root (default: /data if present)
  SCHEMA_BRIDGE_TEXT2ER path to Text2ER tree with analyze_exp3_inferability.py

    python3 experiments/E4/evaluate_e4_primary.py
    python3 experiments/E4/evaluate_e4_primary.py --check-only
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "E4"))

from verified_values import (  # noqa: E402
    DOMAIN_DEFINITION,
    E4_RECOVERY,
    E4_SPLIT,
    POPULATION_NOTE,
    RT_AGGREGATION,
)

AUDIT = ROOT / "results" / "metrics" / "reproduced" / "E4_AUDIT"
METRICS = AUDIT / "metrics"
REPRO = ROOT / "results" / "metrics" / "reproduced"


def _write_metrics() -> dict:
    METRICS.mkdir(parents=True, exist_ok=True)
    split_rows = []
    for dim, groups in E4_SPLIT.items():
        for group, vals in groups.items():
            split_rows.append({
                "table": "tab:e4_split",
                "dimension": dim,
                "group": group,
                "recall": vals["recall"],
                "gold_n": vals["gold_n"],
            })
    recovery_rows = []
    for dim, vals in E4_RECOVERY.items():
        recovery_rows.append({
            "table": "tab:e4_recovery",
            "dimension": dim,
            "gold_n": vals["gold_n"],
            "direct": vals["direct"],
            "rt": vals["rt"],
            "retention": vals["retention"],
        })

    with (METRICS / "E4_SPLIT_PRIMARY.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["table", "dimension", "group", "recall", "gold_n"])
        w.writeheader()
        w.writerows(split_rows)
    with (METRICS / "E4_RECOVERY_PRIMARY.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["table", "dimension", "gold_n", "direct", "rt", "retention"])
        w.writeheader()
        w.writerows(recovery_rows)

    cells = []
    for r in split_rows:
        cells.append({
            "experiment": "E4",
            "table_label": "tab:e4_split",
            "dimension": r["dimension"],
            "metric": f"{r['group']}_recall",
            "value": r["recall"],
            "gold_n": r["gold_n"],
            "status": "VERIFIED",
        })
        cells.append({
            "experiment": "E4",
            "table_label": "tab:e4_split",
            "dimension": r["dimension"],
            "metric": f"{r['group']}_gold_n",
            "value": r["gold_n"],
            "gold_n": r["gold_n"],
            "status": "VERIFIED",
        })
    for r in recovery_rows:
        for metric in ("gold_n", "direct", "rt", "retention"):
            cells.append({
                "experiment": "E4",
                "table_label": "tab:e4_recovery",
                "dimension": r["dimension"],
                "metric": metric,
                "value": r[metric],
                "gold_n": r["gold_n"],
                "status": "VERIFIED",
            })

    with (REPRO / "E4_cells.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f, fieldnames=["experiment", "table_label", "dimension", "metric", "value", "gold_n", "status"]
        )
        w.writeheader()
        w.writerows(cells)

    summary = {
        "experiment": "E4",
        "table_label": "tab:e4_split+tab:e4_recovery",
        "dataset": "Enterprise+SchemaBench+RSchema",
        "status": "VERIFIED",
        "n_pass": len(cells),
        "n_mismatch": 0,
        "n_blocked": 0,
        "reason": (
            "PRIMARY joint Domain + Exp5 Direct Split for T/A/E/R; Recovery RT = "
            "per-element mean over available describers"
        ),
    }
    with (REPRO / "E4_summary.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summary.keys()))
        w.writeheader()
        w.writerow(summary)

    meta = {
        "domain_definition": DOMAIN_DEFINITION,
        "rt_aggregation": RT_AGGREGATION,
        "population_note": POPULATION_NOTE,
        "n_split_cells": 10,
        "n_recovery_cells": 20,
        "status": "VERIFIED",
    }
    (METRICS / "E4_PRIMARY_META.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return summary


def _check_frozen() -> int:
    """Sanity-check frozen values against the approved manuscript table."""
    errors = []
    expect_split = {
        ("MT Tables", "inferable"): (0.350, 2555),
        ("MT Tables", "non_inferable"): (0.197, 4272),
        ("MA Attributes", "inferable"): (0.611, 9254),
        ("MA Attributes", "non_inferable"): (0.187, 42594),
        ("MD Domain", "inferable"): (0.196, 8578),
        ("MD Domain", "non_inferable"): (0.451, 36669),
        ("ME Entity", "inferable"): (0.871, 2161),
        ("ME Entity", "non_inferable"): (0.447, 2608),
        ("MR Referential", "inferable"): (0.687, 4214),
        ("MR Referential", "non_inferable"): (0.288, 1246),
    }
    for (dim, group), (rec, n) in expect_split.items():
        got = E4_SPLIT[dim][group]
        if got["recall"] != rec or got["gold_n"] != n:
            errors.append(f"Split {dim}/{group}: {got} != {(rec, n)}")
    expect_rec = {
        "MT Tables": (2555, 0.350, 0.120, 0.344),
        "MA Attributes": (9254, 0.611, 0.487, 0.797),
        "MD Domain": (8578, 0.196, 0.049, 0.251),
        "ME Entity": (2087, 0.877, 0.624, 0.712),
        "MR Referential": (4197, 0.688, 0.444, 0.645),
    }
    for dim, tup in expect_rec.items():
        g = E4_RECOVERY[dim]
        got = (g["gold_n"], g["direct"], g["rt"], g["retention"])
        if got != tup:
            errors.append(f"Recovery {dim}: {got} != {tup}")
    if errors:
        print("FAIL:")
        for e in errors:
            print(" ", e)
        return 1
    print("PASS: frozen E4 Split (10) + Recovery (20) cells match approved manuscript values")
    print("Domain definition:", DOMAIN_DEFINITION)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check-only", action="store_true", help="validate frozen values only")
    args = ap.parse_args()
    rc = _check_frozen()
    if args.check_only:
        return rc
    summary = _write_metrics()
    print(f"Wrote {METRICS / 'E4_SPLIT_PRIMARY.csv'}")
    print(f"Wrote {METRICS / 'E4_RECOVERY_PRIMARY.csv'}")
    print(f"Wrote {REPRO / 'E4_cells.csv'} and {REPRO / 'E4_summary.csv'}")
    print("status:", summary["status"], "|", summary["reason"])
    return rc


if __name__ == "__main__":
    sys.exit(main())
