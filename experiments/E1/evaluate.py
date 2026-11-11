#!/usr/bin/env python3
"""E1 offline evaluation entry point (Table VII, ``tab:e1_s2t``).

Scores authoritative prediction trees (never SchemaBridge stale schemabench_*):

* Basic  → Exp1 / Schema2Text1
* Detailed → Experiment2 / Schema2Text2 / SchemaBench/Experiment

Uses correct SacreBLEU layout ``corpus_bleu(hyps, [refs])``, RSchema N=381,
SchemaBench N=239, Enterprise SCR-only.

Writes comparison CSV under ``experiments/E1/outputs/verified/``.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "audit"))

from e1_independent_reproduce import main as offline_main  # noqa: E402


if __name__ == "__main__":
    # Default: BLEU/ROUGE/SCR; pass --bert to include BERTScore (GPU recommended).
    sys.exit(offline_main())
