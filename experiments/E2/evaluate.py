#!/usr/bin/env python3
"""E2 offline evaluation entrypoint (Table VIII, ``tab:e2_roundtrip``).

Preferred PRIMARY path (765 schemata: 145/381/239):

    PYTHONHASHSEED=0 python3 experiments/E2/evaluate_table_viii_full.py

This wrapper also supports the legacy archived-comparison harness via
``scripts/reproduce_tables.py --experiment E2`` when ``--legacy-archive`` is passed.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRIMARY = Path(__file__).resolve().parent / "evaluate_table_viii_full.py"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--legacy-archive",
        action="store_true",
        help="Compare against archived SchemaBridge package metrics (partial coverage).",
    )
    ap.add_argument(
        "--help-primary",
        action="store_true",
        help="Show help for the PRIMARY evaluate_table_viii_full.py driver.",
    )
    args, rest = ap.parse_known_args()
    if args.help_primary:
        return subprocess.call([sys.executable, str(PRIMARY), "--help"])
    if args.legacy_archive:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from _common import evaluate_main  # noqa: E402

        return evaluate_main("E2", extra_flags=False)
    # Default: PRIMARY offline recompute from original predictions
    cmd = [sys.executable, str(PRIMARY), *rest]
    print("Running PRIMARY E2 evaluation:", " ".join(cmd), flush=True)
    return subprocess.call(cmd, cwd=str(ROOT))


if __name__ == "__main__":
    raise SystemExit(main())
