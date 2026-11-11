#!/usr/bin/env python3
"""E1 dataset preparation: validate population sizes and derive the RSchema eligibility list.

Validates 145 (Enterprise-145) / 239 (SchemaBench) / 381 (RSchema, DDL-matched) / 518 (RSchema
logical), writes ``RSCHEMA_381_ELIGIBLE.csv`` (schema_id, serial_in_518, eval_index, database)
below ``--out-dir`` (git-ignored ``outputs/`` by default) and explains how the 518 logical
annotations differ from the 381 schemas that have genuine DDL.  No model is run, no text is
generated; only identifiers are written (no DDL, no gold text).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import datasets_io as dio  # noqa: E402
from src import repro_io as rio  # noqa: E402

DEFAULT_OUT_DIR = ROOT / "experiments" / "E1" / "outputs" / "datasets"
ELIGIBLE_FIELDS = ("schema_id", "serial_in_518", "eval_index", "database")
ELIGIBLE_FILE = "RSCHEMA_381_ELIGIBLE.csv"


def eligible_rows(records: Sequence[dio.GoldRecord]) -> list[dict]:
    """Rows for the DDL-matched RSchema schemas: eval_index is the 1-based rank among them."""
    return [
        {"schema_id": r.schema_id, "serial_in_518": r.serial, "eval_index": i, "database": r.database}
        for i, r in enumerate(records, start=1)
    ]


def validate_counts(data_root: str | None, *, strict: bool) -> tuple[dict[str, int], list[str]]:
    """``({name: n}, problems)``; problems list every count that differs from the expected size."""
    counts: dict[str, int] = {}
    for name in ("enterprise145", "schemabench", "rschema"):
        counts[name] = len(dio.load_dataset(name, data_root, strict=False))
    counts["rschema_logical"] = len(dio.load_rschema_logical_518(data_root, strict=False))
    problems = [f"{k}: expected {dio.EXPECTED_COUNTS[k]}, found {n}" for k, n in counts.items()
                if n != dio.EXPECTED_COUNTS[k]]
    return counts, problems


def explain_518_vs_381(data_root: str | None) -> dict:
    logical = dio.load_rschema_logical_518(data_root, strict=False)
    matched = [r for r in logical if r.has_ddl]
    logical_only = [r for r in logical if not r.has_ddl]
    ddl_ids = set(dio.load_rschema_ddl_by_id(data_root))
    ann_ids = {r.schema_id for r in logical}
    return {
        "n_logical": len(logical),
        "n_ddl_matched": len(matched),
        "n_logical_only": len(logical_only),
        "n_ddl_without_annotation": len(ddl_ids - ann_ids),
        "n_duplicate_logical_ids": len(logical) - len(ann_ids),
        "serial_gaps": len(logical) - len(matched),
    }


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-root", default=None,
                    help=f"dataset root (overrides ${dio.DATA_ROOT_ENV}; packaged datasets/ is the fallback)")
    ap.add_argument("--out-dir", default=None,
                    help="directory for RSCHEMA_381_ELIGIBLE.csv (default experiments/E1/outputs/datasets/; "
                         "must be outside the repo or below a git-ignored path)")
    ap.add_argument("--no-write", action="store_true", help="validate and print only; write nothing")
    ap.add_argument("--no-strict", action="store_true", help="do not fail (exit 1) on count mismatches")
    return ap


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        counts, problems = validate_counts(args.data_root, strict=not args.no_strict)
        info = explain_518_vs_381(args.data_root)
        rschema = dio.load_rschema_381(args.data_root, strict=False)
        out_dir = rio.assert_ignored_out_dir(args.out_dir or DEFAULT_OUT_DIR)
    except (FileNotFoundError, ValueError, KeyError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    print("Dataset populations (found / expected):")
    for k, n in counts.items():
        print(f"  {k:16s} {n:4d} / {dio.EXPECTED_COUNTS[k]}")
    print()
    print("RSchema: 518 logical annotations vs 381 DDL-matched schemas")
    print(f"  annotation.jsonl      : {info['n_logical']} logical annotations (serials 0001..{info['n_logical']:04d})")
    print(f"  annotation_ddl.jsonl  : genuine DDL for {info['n_ddl_matched']} of them (matched by id)")
    print(f"  logical-only          : {info['n_logical_only']} annotations have NO genuine DDL "
          "(only a synthetic varchar(255) DDL could be derived from the logical annotation)")
    print(f"  E1 / E2 population    : the {info['n_ddl_matched']} DDL-matched schemas; serials are the 1-based positions "
          f"in the {info['n_logical']}-record file, hence NOT contiguous (gaps: {info['serial_gaps']})")
    print("  eval_index            : 1..381 rank among the DDL-matched schemas (use serial_in_518 for NNNN file names)")
    if info["n_ddl_without_annotation"] or info["n_duplicate_logical_ids"]:
        print(f"  note: {info['n_ddl_without_annotation']} DDL ids without annotation, "
              f"{info['n_duplicate_logical_ids']} duplicate logical ids")

    if not args.no_write:
        path = out_dir / ELIGIBLE_FILE
        rio.write_csv(path, eligible_rows(rschema), ELIGIBLE_FIELDS)
        print(f"\nwrote {len(rschema)} rows -> {path}")
    else:
        print("\n--no-write: nothing written")

    if problems:
        print("\nCOUNT MISMATCH:\n  " + "\n  ".join(problems), file=sys.stderr)
        return 0 if args.no_strict else 1
    print("\nOK: all populations match the expected sizes (145 / 239 / 381 / 518).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
