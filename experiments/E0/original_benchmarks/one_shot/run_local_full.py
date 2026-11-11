#!/usr/bin/env python3
"""Compatibility wrapper — delegates to the packaged standalone baseline runner.

Historical entry point retained for provenance. Prefer::

    python3 experiments/E0/original_benchmarks/run_baselines.py \\
        --model codellama-13b --method one_shot --dry-run
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.argv[0] = str(ROOT / "run_baselines.py")
# Default method for this directory if not provided.
if "--method" not in sys.argv:
    sys.argv.extend(["--method", "one_shot"])
from run_baselines import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
