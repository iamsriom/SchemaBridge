#!/usr/bin/env python3
"""Build audit/E0_PAPER_COMPARISON.csv against locked manuscript targets.

Modes:
  diagnostic (default)  — always exit 0; record PASS/MISMATCH/… for inspection
  --verify              — exit nonzero when any required check fails

Uses:
  * results/metrics/reproduced/E0_TABLE_V_FINAL.csv
  * results/metrics/reproduced/E0_TABLE_VI_FINAL.csv
  * audit/E0_CURRENT_MANUSCRIPT_VALUES.json  (locked manuscript reference)

Does not invent metrics. Tolerance for 3dp PASS: abs(diff) <= 0.0005 or
rounded-to-3dp equals the manuscript cell.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOL = 0.0005
PAPER = json.loads((ROOT / "audit/E0_CURRENT_MANUSCRIPT_VALUES.json").read_text())
OUT = ROOT / "audit/E0_PAPER_COMPARISON.csv"

METRICS = ["nged", "halluc", "tables", "attributes", "domain", "entity", "referential"]

# SourceStatus values that mean "not a full per-schema prediction recompute".
ARCHIVE_ONLY = {"ARCHIVE_AGGREGATE"}
BLOCKED_STATUSES = {"BLOCKED"}


def r3(x: float) -> float:
    return float(f"{x:.3f}")


def status_for(paper, recomputed) -> tuple[str, float | None, float | None]:
    """Compare one cell. ``None`` / ``"--"`` means not-applicable Domain."""
    paper_na = paper is None or paper == "--"
    rec_na = recomputed is None
    if paper_na and rec_na:
        return "PASS", None, None
    if paper_na and not rec_na:
        return "MISMATCH", None, recomputed
    if (not paper_na) and rec_na:
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


def annotate_archive(st: str, src: str) -> str:
    if src in ARCHIVE_ONLY:
        if st == "PASS":
            return "PASS_ARCHIVE"
        if st == "MISMATCH":
            return "MISMATCH_ARCHIVE"
    return st


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--verify",
        action="store_true",
        help="Exit nonzero on Direct incompleteness, missing numerics, "
        "manuscript mismatch, archive-only false COMPLETE, or V↔VI Direct drift.",
    )
    ap.add_argument(
        "--allow-archive",
        action="store_true",
        help="In --verify mode, treat PASS_ARCHIVE as acceptable for prompting rows "
        "(still fails if SourceStatus claims COMPLETE without per-schema trees).",
    )
    ap.add_argument(
        "--lock-file",
        type=Path,
        default=ROOT / "audit/E0_CURRENT_MANUSCRIPT_VALUES.json",
        help="Locked manuscript reference JSON.",
    )
    args = ap.parse_args()
    paper = json.loads(args.lock_file.read_text(encoding="utf-8"))

    tv_path = ROOT / "results/metrics/reproduced/E0_TABLE_V_FINAL.csv"
    tvi_path = ROOT / "results/metrics/reproduced/E0_TABLE_VI_FINAL.csv"
    if not tv_path.is_file() or not tvi_path.is_file():
        print(f"Missing reproduced tables: {tv_path} / {tvi_path}", file=sys.stderr)
        return 2 if args.verify else 0

    tv = load_csv(tv_path)
    tvi = load_csv(tvi_path)
    rows: list[dict] = []
    failures: list[str] = []

    # ---- Table V
    for r in tv:
        key = f"{r['dataset']}|{r['model']}"
        if key not in paper["tab:e0_overall"]:
            failures.append(f"unexpected Table V row {key}")
            continue
        paper_row = paper["tab:e0_overall"][key]
        src = r.get("status") or ""
        if src in ("INCOMPLETE", "INVALID", "BLOCKED"):
            failures.append(f"Table V Direct incomplete: {key} status={src}")
        for m in METRICS:
            paper_v = paper_row[m]
            recomputed = num_or_none(r.get(m))
            st, p, rec = status_for(paper_v, recomputed)
            if st == "MISMATCH":
                failures.append(
                    f"V {r['dataset']} {r['model']} {m}: paper={paper_v} got={recomputed}"
                )
            elif st == "BLOCKED":
                failures.append(f"V {r['dataset']} {r['model']} {m}: missing recomputed")
            diff = "" if rec is None or p is None else f"{rec - p:+.6f}"
            rows.append(
                {
                    "Table": "V",
                    "Dataset": r["dataset"],
                    "Model": r["model"],
                    "Method": "Direct",
                    "Metric": m,
                    "Paper": "" if paper_v is None else paper_v,
                    "Recomputed": "" if recomputed is None else f"{recomputed:.6f}",
                    "Round3": "" if recomputed is None else f"{r3(recomputed):.3f}",
                    "Difference": diff,
                    "Status": st,
                    "SourceStatus": src,
                }
            )

    # ---- Table VI (RSchema manuscript rows only)
    tv_by_model = {
        r["model"]: r for r in tv if r["dataset"] == "RSchema"
    }
    for r in tvi:
        if r["dataset"] != "RSchema":
            continue
        if r["method"] == "Direct":
            key = f"{r['model']}|Direct"
        else:
            key = f"{r['model']}|{r['method']}"
        if key not in paper["tab:e0_baselines"]:
            continue
        paper_row = paper["tab:e0_baselines"][key]
        src = (r.get("status") or "").strip()
        is_direct = r["method"] == "Direct"
        is_prompting = not is_direct

        # Archive-only must never be reported as COMPLETE.
        if src == "COMPLETE" and is_prompting:
            # COMPLETE for prompting requires per-schema trees.
            failures.append(
                f"VI {key}: SourceStatus=COMPLETE for prompting row without verified trees"
            )
        if src in ARCHIVE_ONLY and is_prompting and not args.allow_archive:
            failures.append(
                f"VI {key}: ARCHIVE_AGGREGATE is not full reproduction "
                f"(use --allow-archive to accept for verify)"
            )
        if src in BLOCKED_STATUSES and is_prompting:
            failures.append(f"VI {key}: BLOCKED (no predictions / no archive)")

        for m in METRICS:
            paper_v = paper_row[m]
            recomputed = num_or_none(r.get(m))

            # Domain: Direct compares numbers; prompting baselines are --/--.
            if m == "domain":
                if is_prompting:
                    st, p, rec = status_for(None, None)  # both N/A
                    paper_disp = "--"
                    recomputed_disp = "--"
                else:
                    st, p, rec = status_for(paper_v, recomputed)
                    paper_disp = "--" if paper_v is None else paper_v
                    recomputed_disp = (
                        "--" if recomputed is None else f"{recomputed:.6f}"
                    )
            elif src in BLOCKED_STATUSES and not is_direct:
                st, p, rec = "BLOCKED", (None if paper_v is None else float(paper_v)), None
                paper_disp = "--" if paper_v is None else paper_v
                recomputed_disp = ""
            else:
                st, p, rec = status_for(paper_v, recomputed)
                st = annotate_archive(st, src)
                paper_disp = "--" if paper_v is None else paper_v
                recomputed_disp = "" if recomputed is None else f"{recomputed:.6f}"

            if st in ("MISMATCH", "MISMATCH_ARCHIVE"):
                failures.append(
                    f"VI {r['model']} {r['method']} {m}: paper={paper_v} got={recomputed} ({st})"
                )
            elif st == "BLOCKED" and m != "domain":
                failures.append(f"VI {r['model']} {r['method']} {m}: blocked")

            diff = "" if rec is None or p is None else f"{rec - p:+.6f}"
            rows.append(
                {
                    "Table": "VI",
                    "Dataset": r["dataset"],
                    "Model": r["model"],
                    "Method": r["method"],
                    "Metric": m,
                    "Paper": paper_disp,
                    "Recomputed": recomputed_disp,
                    "Round3": (
                        "--"
                        if recomputed_disp == "--"
                        else ("" if recomputed is None else f"{r3(recomputed):.3f}")
                    ),
                    "Difference": diff,
                    "Status": st,
                    "SourceStatus": src,
                }
            )

        # Table VI Direct must equal Table V RSchema for the same model.
        if is_direct and r["model"] in tv_by_model:
            tv_row = tv_by_model[r["model"]]
            for m in METRICS:
                a = num_or_none(tv_row.get(m))
                b = num_or_none(r.get(m))
                if a is None and b is None:
                    continue
                if a is None or b is None or abs(a - b) > 1e-12:
                    failures.append(
                        f"V↔VI Direct drift {r['model']} {m}: V={a} VI={b}"
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

    c = Counter(r["Status"] for r in rows)
    print(f"Wrote {OUT} ({len(rows)} cells)")
    for k, v in sorted(c.items()):
        print(f"  {k}: {v}")

    if args.verify:
        # Deduplicate while preserving order
        seen = set()
        uniq = []
        for msg in failures:
            if msg not in seen:
                seen.add(msg)
                uniq.append(msg)
        if uniq:
            print(f"\nVERIFY FAILED ({len(uniq)} issues):", file=sys.stderr)
            for msg in uniq[:80]:
                print(f"  - {msg}", file=sys.stderr)
            if len(uniq) > 80:
                print(f"  … {len(uniq) - 80} more", file=sys.stderr)
            return 1
        print("VERIFY PASS")
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
