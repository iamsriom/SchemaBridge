#!/usr/bin/env python3
"""Prepare / validate E3 fixed-description inputs (GPT-5.4-mini Detailed from E1).

Does **not** generate descriptions and does **not** call any API.  It:

1. Reuses ``experiments/E1/prepare_dataset.py`` eligibility checks (145 / 239 / 381).
2. Locates the E1 Detailed GPT-5.4-mini description directories.
3. Reports completeness (schema ids present, non-empty ``nl_text``, hash inventory).
4. Optionally writes a local *manifest* (ids + hashes only — no description text) under
   a git-ignored ``outputs/`` path for offline bookkeeping.

    python experiments/E3/prepare_inputs.py --dataset all
    python experiments/E3/prepare_inputs.py --dataset rschema \\
        --descriptions-dir experiments/E1/outputs/rschema_detailed_gpt54mini \\
        --write-manifest --out-dir experiments/E3/outputs/manifests
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import datasets_io as dio  # noqa: E402
from src import prompt_assets as pa  # noqa: E402
from src import repro_io as rio  # noqa: E402

FIXED_DESCRIBER = "gpt54mini"
FIXED_PROMPT = "detailed"
DEFAULT_DESC_PARENT = ROOT / "experiments" / "E1" / "outputs"
DEFAULT_OUT_DIR = ROOT / "experiments" / "E3" / "outputs" / "manifests"
MANIFEST_FIELDS = ("serial", "schema_id", "database", "nl_sha256", "status")


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description="Validate E3 fixed GPT-5.4-mini Detailed description directories (no generation).",
    )
    ap.add_argument("--dataset", choices=rio.DATASET_CHOICES, required=True)
    ap.add_argument("--descriptions-dir", default=None,
                    help="E1 Detailed GPT-5.4-mini directory "
                         f"(default experiments/E1/outputs/<dataset>_{FIXED_PROMPT}_{FIXED_DESCRIBER}/)")
    ap.add_argument("--data-root", default=None)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--write-manifest", action="store_true",
                    help="write id+hash CSV (no nl_text) under --out-dir")
    ap.add_argument("--out-dir", default=None,
                    help="manifest output directory (default experiments/E3/outputs/manifests/)")
    return ap


def inventory(dataset: str, desc_dir: Path, *, data_root, limit) -> tuple[dict, list[dict]]:
    gold = dio.load_dataset(dataset, data_root)
    gold = gold[:limit] if limit else gold
    preds = rio.load_prediction_dir(desc_dir) if desc_dir.is_dir() else {}
    rows: list[dict] = []
    n_ok = n_missing = n_bad = 0
    for rec, entry, reason in rio.align_predictions(gold, preds):
        why = reason or rio.nl_failure(entry)
        if why is None:
            n_ok += 1
            status, h = "ok", rio.description_hash(entry)
        elif reason is not None:
            n_missing += 1
            status, h = f"missing:{reason}", ""
        else:
            n_bad += 1
            status, h = f"invalid:{why}", ""
        rows.append({"serial": rec.serial, "schema_id": rec.schema_id, "database": rec.database,
                     "nl_sha256": h or "", "status": status})
    summary = {
        "experiment": "E3", "dataset": dataset, "fixed_describer": FIXED_DESCRIBER,
        "fixed_prompt": FIXED_PROMPT, "describer_prompt_sha256": pa.EXPECTED_SHA256[FIXED_PROMPT],
        "n_gold": len(gold), "n_ok": n_ok, "n_missing": n_missing, "n_invalid": n_bad,
        "descriptions_dir": str(desc_dir), "descriptions_dir_exists": desc_dir.is_dir(),
        "n_expected": dio.EXPECTED_COUNTS[dataset],
    }
    return summary, rows


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    datasets = rio.expand(args.dataset, rio.DATASETS)
    multi = len(datasets) > 1
    try:
        pa.verify_all_prompts()
        out_dir = None
        if args.write_manifest:
            out_dir = rio.assert_ignored_out_dir(args.out_dir or DEFAULT_OUT_DIR)
    except (pa.PromptHashError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    print(f"fixed describer={FIXED_DESCRIBER} prompt={FIXED_PROMPT} "
          f"sha256={pa.EXPECTED_SHA256[FIXED_PROMPT][:12]}…")
    rc = 0
    for d in datasets:
        combo = rio.combo_name(d, FIXED_PROMPT, FIXED_DESCRIBER)
        desc_dir = rio.combo_dir(args.descriptions_dir, DEFAULT_DESC_PARENT, combo, multi=multi)
        try:
            summary, rows = inventory(d, desc_dir, data_root=args.data_root, limit=args.limit)
        except (FileNotFoundError, ValueError, KeyError) as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
        print(f"[{d}] gold={summary['n_gold']} (expected {summary['n_expected']}) "
              f"ok={summary['n_ok']} missing={summary['n_missing']} invalid={summary['n_invalid']} "
              f"dir={'found' if summary['descriptions_dir_exists'] else 'NOT FOUND'}: {desc_dir}")
        if summary["n_ok"] != summary["n_gold"]:
            rc = 1
        if out_dir is not None:
            rio.write_json(out_dir / f"{combo}_summary.json", summary)
            rio.write_csv(out_dir / f"{combo}_hashes.csv", rows, MANIFEST_FIELDS)
            print(f"  wrote manifest -> {out_dir / (combo + '_hashes.csv')}")
    # Always remind researchers how to obtain the descriptions via E1.
    print()
    print("To generate missing fixed descriptions (paid API; disabled in this package for execute):")
    print("  python experiments/E1/run.py --dataset DATASET --model gpt54mini --prompt detailed  # dry-run")
    print("  # Then place locally generated NNNN.json under experiments/E1/outputs/"
          f"<dataset>_{FIXED_PROMPT}_{FIXED_DESCRIBER}/")
    print("Dataset eligibility (381 RSchema genuine DDL etc.):")
    print("  python experiments/E1/prepare_dataset.py --out-dir experiments/E1/outputs/datasets")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
