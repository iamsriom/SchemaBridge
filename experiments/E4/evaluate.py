#!/usr/bin/env python3
"""E4 offline evaluation: Cases analysis on Enterprise-145 (inferred semantics).

Thin wrapper around scripts/reproduce_tables.py --experiment E4 (archived artefacts only).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import evaluate_main  # noqa: E402

if __name__ == "__main__":
    sys.exit(evaluate_main("E4", extra_flags=False))
