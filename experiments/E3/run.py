#!/usr/bin/env python3
"""E3 generation entry point — refuses online / paid inference.

SchemaBridge publishes offline evaluation of original Exp4 constructor
predictions. Re-running constructors requires private artifacts and API keys
that are intentionally not shipped.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import refuse_online  # noqa: E402

HINT = """  # Offline evaluation only (no generation):
  PYTHONHASHSEED=0 python3 experiments/E3/evaluate.py
  # Predictions + frozen NL live on the evaluation host (see docs/REPRODUCE_E3.md).
  # Checksums: results/metrics/reproduced/E3_AUDIT/provenance/artifact_checksums_summary.json
"""

if __name__ == "__main__":
    sys.exit(refuse_online("E3", HINT))
