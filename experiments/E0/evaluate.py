#!/usr/bin/env python3
"""Canonical E0 offline evaluation entry point (Tables V + VI).

Authoritative genuine-gold protocol::

    python experiments/E0/evaluate.py
    python experiments/E0/reproduce_genuine_tables.py

Optional historical archive comparison (old Exp4 JSON / PaperMethods)::

    python experiments/E0/evaluate.py --archive-compare
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
E0_DIR = Path(__file__).resolve().parent
EXP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(E0_DIR))
sys.path.insert(0, str(EXP))
sys.path.insert(0, str(ROOT))


def main() -> int:
    argv = sys.argv[1:]
    if "--archive-compare" in argv:
        sys.argv = [sys.argv[0]] + [a for a in argv if a != "--archive-compare"]
        from _common import evaluate_main  # noqa: E402

        return evaluate_main("E0", extra_flags=True)

    # Authoritative genuine-gold Tables V + VI.
    from reproduce_genuine_tables import main as genuine_main  # noqa: E402

    return genuine_main()


if __name__ == "__main__":
    sys.exit(main())
