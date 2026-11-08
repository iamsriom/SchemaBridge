#!/usr/bin/env python3
"""E1 offline evaluation: Schema -> Text (Table VII, `tab:e1_s2t`).

Thin wrapper around scripts/reproduce_tables.py --experiment E1 (archived artefacts only).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import evaluate_main  # noqa: E402

if __name__ == "__main__":
    sys.exit(evaluate_main("E1", extra_flags=False))
