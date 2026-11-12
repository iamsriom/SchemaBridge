#!/usr/bin/env python3
"""E4 offline evaluation entry point (masking / inferability).

Publishes verified PRIMARY metrics for tab:e4_split and tab:e4_recovery.
Full prediction recompute is optional and requires private artifacts
(see docs/REPRODUCE_E4.md).

    python3 experiments/E4/evaluate.py
    python3 experiments/E4/generate_tables.py
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / "evaluate_e4_primary.py"

if __name__ == "__main__":
    if not TARGET.exists():
        print(f"Missing {TARGET}", file=sys.stderr)
        sys.exit(2)
    sys.argv[0] = str(TARGET)
    runpy.run_path(str(TARGET), run_name="__main__")
