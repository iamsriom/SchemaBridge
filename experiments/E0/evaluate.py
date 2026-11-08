#!/usr/bin/env python3
"""E0 offline evaluation: Text -> Schema from gold NL (Table V, `tab:e0_overall`).

Thin wrapper around scripts/reproduce_tables.py --experiment E0 (archived artefacts only).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import evaluate_main  # noqa: E402

if __name__ == "__main__":
    sys.exit(evaluate_main("E0", extra_flags=True))
