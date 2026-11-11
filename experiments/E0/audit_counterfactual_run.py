#!/usr/bin/env python3
"""Counterfactual genuine-protocol re-score with diagnostic parser patches (audit only).

Usage: python3 experiments/E0/audit_counterfactual_run.py {none|apos|apos_unterm|all|all5} [out.csv]

Runs the *unchanged* ``reproduce_genuine_tables.evaluate_direct_*`` functions after
monkey-patching ``src.schema_parser`` in-process (see ``audit_cf_parser_patch.py``).
Offline; no predictions are regenerated; ``src/`` on disk is untouched.
"""
from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

import audit_cf_parser_patch as cf  # noqa: E402

spec = importlib.util.spec_from_file_location("rgt", HERE / "reproduce_genuine_tables.py")
rgt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rgt)

VARIANTS = {
    "none": (False, False, False, False),
    "apos": (True, False, False, False),          # F1
    "apos_unterm": (True, True, False, False),    # F1 + F2
    "all": (True, True, True, False),             # F1 + F2 + F3
    "all5": (True, True, True, True),             # F1 + F2 + F3 + F5
}


def main() -> int:
    variant = sys.argv[1] if len(sys.argv) > 1 else "none"
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(f"cf_{variant}.csv")
    flags = VARIANTS[variant]
    if any(flags):
        cf.apply(*flags)
    from src.evaluator import load_jsonl

    logical = [r for r in load_jsonl(rgt.GOLD_LOGICAL["RSchema"]) if r.get("id")]
    ddl_by_id = {r["id"]: r for r in load_jsonl(rgt.GOLD_DDL["RSchema"]) if r.get("id")}
    sb = [r for r in load_jsonl(rgt.GOLD_DDL["SchemaBench"]) if r.get("id")]
    rows = []
    for ds in ("RSchema", "SchemaBench"):
        for model, pdir in rgt.DIRECT[ds].items():
            res = (rgt.evaluate_direct_rschema(pdir, logical, ddl_by_id) if ds == "RSchema"
                   else rgt.evaluate_direct_schemabench(pdir, sb))
            row = {"variant": variant, "dataset": ds, "model": model}
            for k in ("nged", "halluc", "tables", "attributes", "domain", "entity", "referential"):
                row[k] = f"{res[k]:.6f}"
            for d, c in res["struct_counts"].items():
                row[d + "_GPM"] = f"{c['gold']}/{c['recreated']}/{c['matched']}"
            dc = res["domain_counts"]
            row["domain_GPM"] = f"{dc['gold']}/{dc['recreated']}/{dc['matched']}"
            rows.append(row)
            print(ds, model, row["nged"], row["tables"], flush=True)
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
