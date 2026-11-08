"""Shared helpers for experiments/E*/ entry points (offline only)."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def evaluate_main(experiment: str, extra_flags: bool = False) -> int:
    """Run the offline comparison for one experiment (wraps scripts/reproduce_tables.py)."""
    import argparse

    import reproduce_tables as rt

    ap = argparse.ArgumentParser(description=f"Offline evaluation of {experiment} from archived artefacts")
    ap.add_argument("--verbose", "-v", action="store_true")
    ap.add_argument("--out-dir", type=Path, default=rt.REPRODUCED)
    if extra_flags:
        ap.add_argument("--recompute", action="store_true", help="re-evaluate RSchema predictions with src/")
        ap.add_argument("--vendored", action="store_true",
                        help="also run third_party/evaluate_exp4_text2schema.py via subprocess "
                             "(SCHEMABRIDGE_ROOT, PYTHONHASHSEED=0) on the RSchema Exp4 predictions")
    args = ap.parse_args()
    rt.run([experiment], getattr(args, "recompute", False), args.verbose, args.out_dir)
    if getattr(args, "vendored", False):
        return run_vendored_exp4_rschema(args.out_dir / "E0_vendored_rschema")
    return 0


def run_vendored_exp4_rschema(out_dir: Path) -> int:
    """Run the vendored Exp4 evaluator on the three RSchema prediction folders (offline)."""
    base = Path(tempfile.mkdtemp(prefix="schemabridge_exp4_"))
    pred_root = ROOT / "results" / "predictions" / "e0"
    llms = []
    for llm in ("codellama13b", "llama31", "deepseek"):
        src = pred_root / f"rschema_exp4_{llm}"
        if src.exists():
            (base / f"text2schema_{llm}").symlink_to(src.resolve(), target_is_directory=True)
            llms.append(llm)
    if not llms:
        print("BLOCKED: no RSchema Exp4 prediction folders found under", pred_root)
        return 1
    env = dict(os.environ, SCHEMABRIDGE_ROOT=str(ROOT), PYTHONHASHSEED="0")
    cmd = [sys.executable, str(ROOT / "third_party" / "evaluate_exp4_text2schema.py"),
           "--base-dir", str(base), "--annotation", str(ROOT / "datasets" / "rschema" / "annotation.jsonl"),
           "--out-dir", str(out_dir)]
    for llm in llms:
        cmd += ["--llm", llm]
    print("running:", " ".join(cmd))
    return subprocess.call(cmd, env=env, cwd=str(ROOT))


def refuse_online(experiment: str, archived_hint: str, argv: list[str] | None = None) -> int:
    """Generation entry points refuse to run unless explicitly unlocked, and even then
    SchemaBridge ships no API client: this package is an offline reproducibility package."""
    argv = list(sys.argv[1:] if argv is None else argv)
    print(f"[{experiment}] run.py: generation is DISABLED by default (no API / GPU calls are made).")
    print()
    print("Use the archived predictions instead:")
    print(archived_hint)
    print()
    print(f"Then evaluate offline:  python experiments/{experiment}/evaluate.py")
    print("                        python scripts/reproduce_tables.py --experiment " + experiment)
    if "--online" in argv and os.environ.get("SCHEMABRIDGE_ALLOW_ONLINE") == "1":
        print()
        print("--online + SCHEMABRIDGE_ALLOW_ONLINE=1 were given, but this package contains no generation "
              "client. The original generation scripts live outside the package "
              "(e.g. /data/RSchema_ExpResults4/Code/, /data/SchemaBench/Code/); run them there with your own "
              "credentials/GPUs and symlink the output folders under results/predictions/.")
    elif "--online" in argv:
        print()
        print("--online ignored: set SCHEMABRIDGE_ALLOW_ONLINE=1 as well to acknowledge that online runs are "
              "outside this package.")
    return 2
