#!/usr/bin/env python3
"""E5 offline evaluation: Figure 5: F1 by schema size x constraint complexity (inferred semantics).

Thin wrapper around scripts/reproduce_tables.py --experiment E5 (archived artefacts only).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import evaluate_main  # noqa: E402

if __name__ == "__main__":
    sys.exit(evaluate_main("E5", extra_flags=False))
