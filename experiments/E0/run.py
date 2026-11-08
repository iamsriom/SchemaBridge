#!/usr/bin/env python3
"""E0 generation entry point -- refuses online runs by default.

SchemaBridge is an offline reproducibility package: no API calls, no model loading.
This script only prints how to use the archived predictions.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import refuse_online  # noqa: E402

HINT = """  ls results/predictions/e0/   # rschema_exp4_*, schemabench_exp2_*, *_papermethods (symlinks)"""

if __name__ == "__main__":
    sys.exit(refuse_online("E0", HINT))
