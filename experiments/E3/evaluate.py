#!/usr/bin/env python3
"""E3 offline evaluation: Masked-DDL structural imputation, describer stage (inferred semantics).

Thin wrapper around scripts/reproduce_tables.py --experiment E3 (archived artefacts only).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import evaluate_main  # noqa: E402

if __name__ == "__main__":
    sys.exit(evaluate_main("E3", extra_flags=False))
