#!/usr/bin/env python3
"""E2 offline evaluation: Round trip Schema -> Text -> Schema (Table VIII, `tab:e2_roundtrip`).

Thin wrapper around scripts/reproduce_tables.py --experiment E2 (archived artefacts only).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import evaluate_main  # noqa: E402

if __name__ == "__main__":
    sys.exit(evaluate_main("E2", extra_flags=False))
