#!/usr/bin/env python3
"""Compatibility wrapper for One-shot+CoT → packaged ``run_baselines.py``."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.argv[0] = str(ROOT / "run_baselines.py")
if "--method" not in sys.argv:
    sys.argv.extend(["--method", "one_shot_cot"])
from run_baselines import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
