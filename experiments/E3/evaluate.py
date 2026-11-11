#!/usr/bin/env python3
"""E3 offline evaluation entry point (constructor isolation / tab:e3_overall).

Recomputes PRIMARY metrics from original Exp4 predictions + frozen GPT-5.4-mini
detailed descriptions. Requires local /data prediction trees (not shipped in git).

    PYTHONHASHSEED=0 python3 experiments/E3/evaluate.py
"""
from __future__ import annotations

import os
import runpy
import sys
from pathlib import Path

os.environ.setdefault("PYTHONHASHSEED", "0")

HERE = Path(__file__).resolve().parent
TARGET = HERE / "evaluate_e3_primary.py"

if __name__ == "__main__":
    if not TARGET.exists():
        print(f"Missing {TARGET}", file=sys.stderr)
        sys.exit(2)
    sys.argv[0] = str(TARGET)
    runpy.run_path(str(TARGET), run_name="__main__")
