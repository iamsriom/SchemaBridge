#!/usr/bin/env python3
"""E2 generation entrypoint — refuses paid inference.

E2 reuses archived GPT-4o-mini reconstructions of E1 Basic/Detailed descriptions.
This script never calls an API.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import refuse_online  # noqa: E402


def main() -> int:
    return refuse_online(
        "E2",
        archived_hint=(
            "E2 round-trip reconstructions are fixed GPT-4o-mini outputs over E1 "
            "Basic/Detailed descriptions. Use experiments/E2/evaluate_table_viii_full.py "
            "with the original prediction trees documented in "
            "results/metrics/reproduced/E2_AUDIT/provenance/ "
            "(see prediction_manifest.csv and source_hashes.json)."
        ),
    )


if __name__ == "__main__":
    raise SystemExit(main())
