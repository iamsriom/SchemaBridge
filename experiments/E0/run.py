#!/usr/bin/env python3
"""E0 generation entry point.

Offline by default. Live closed-model Direct inference is delegated to
``run_direct_api.py`` and requires explicit ``--confirm-paid``.

Examples::

    # Offline guidance (no API calls)
    python experiments/E0/run.py

    # Live Direct API (paid; opt-in)
    python experiments/E0/run.py --online --confirm-paid --limit 1
    python experiments/E0/run.py --online --confirm-paid --dataset rschema --llm claude_sonnet_4_6
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

E0_DIR = Path(__file__).resolve().parent
ROOT = E0_DIR.parents[1]


HINT = """  # Evaluate archived / local Direct predictions offline:
  python experiments/E0/evaluate.py
  python experiments/E0/reproduce_genuine_tables.py

  # Live closed Direct API (Claude Sonnet 4.6 / GPT-5.4-mini) — paid, opt-in:
  python experiments/E0/run_direct_api.py --dry-run
  python experiments/E0/run_direct_api.py --limit 1 --confirm-paid
  python experiments/E0/run_direct_api.py --dataset rschema --llm claude_sonnet_4_6 --confirm-paid
  python experiments/E0/run_direct_api.py --dataset rschema --llm gpt_5_4_mini --confirm-paid

  # Open-weight Direct regeneration uses the original Exp4 scripts outside this
  # package (e.g. RSchema_ExpResults4/Code/rschema_exp4_text2schema_allLLM.py) when
  # GPU weights are available; SchemaBridge evaluates their NNNN.json dumps.
"""


def main() -> int:
    argv = sys.argv[1:]
    if "--online" in argv:
        # Forward remaining flags to the canonical Direct API runner.
        forward = [a for a in argv if a != "--online"]
        if "--confirm-paid" not in forward and "--dry-run" not in forward:
            print(
                "[E0] Live inference requires --confirm-paid (or use --dry-run).\n"
                "Example:\n"
                "  python experiments/E0/run.py --online --confirm-paid --limit 1",
                file=sys.stderr,
            )
            return 2
        cmd = [sys.executable, str(E0_DIR / "run_direct_api.py"), *forward]
        print("[E0] Delegating to experiments/E0/run_direct_api.py", flush=True)
        return subprocess.call(cmd, cwd=str(ROOT))

    print("[E0] run.py: generation is offline by default (no API / GPU calls).")
    print()
    print(HINT)
    if os.environ.get("SCHEMABRIDGE_ALLOW_ONLINE") == "1":
        print(
            "Note: SCHEMABRIDGE_ALLOW_ONLINE=1 alone is not enough; pass --online "
            "--confirm-paid to run paid Direct API inference."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
