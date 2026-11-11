#!/usr/bin/env python3
"""Thin wrapper: build Table VII (E1) and Table VIII (E2) LaTeX skeletons from LOCAL metrics.

Calls ``experiments/E1/generate_table_vii.py`` and ``experiments/E2/generate_table_viii.py``.
Nothing is computed here and no scores are embedded; outputs go below ``--out-dir``
(default: each generator's own git-ignored ``latex_generated/`` directory).
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _load(rel: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate Table VII and VIII LaTeX skeletons from local metrics JSON.")
    ap.add_argument("--e1-metrics-dir", nargs="+", default=None, help="E1 metrics dir(s) (default experiments/E1/outputs/metrics/)")
    ap.add_argument("--e2-metrics-dir", nargs="+", default=None, help="E2 metrics dir(s) (default experiments/E2/outputs/metrics/)")
    ap.add_argument("--out-dir", default=None, help="write table_vii.tex and table_viii.tex here (git-ignored location)")
    ap.add_argument("--only", choices=("e1", "e2"), default=None, help="generate just one table")
    args = ap.parse_args(argv)
    rc = 0
    for key, rel, name, mdirs in (
        ("e1", "experiments/E1/generate_table_vii.py", "_gen_table_vii", args.e1_metrics_dir),
        ("e2", "experiments/E2/generate_table_viii.py", "_gen_table_viii", args.e2_metrics_dir),
    ):
        if args.only and args.only != key:
            continue
        sub: list[str] = []
        if mdirs:
            sub += ["--metrics-dir", *mdirs]
        if args.out_dir:
            sub += ["--out-dir", args.out_dir]
        rc = max(rc, _load(rel, name).main(sub))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
