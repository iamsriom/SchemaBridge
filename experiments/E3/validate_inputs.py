#!/usr/bin/env python3
"""Verify E3 constructor isolation: every constructor received the same fixed description.

Checks, for each gold schema id:

1. A GPT-5.4-mini Detailed description exists (``--descriptions-dir``).
2. Each constructor reconstruction (when present) carries the same ``nl_text`` SHA-256.
3. Schema ids are not silently mis-paired.

Exits non-zero on any mismatch.  Purely offline; no network, no LLM calls.

    python experiments/E3/validate_inputs.py --dataset rschema \\
        --descriptions-dir experiments/E1/outputs/rschema_detailed_gpt54mini \\
        --pred-parent experiments/E3/outputs
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
from src import inference_clients as ic  # noqa: E402
from src import repro_io as rio  # noqa: E402

FIXED_DESCRIBER = "gpt54mini"
FIXED_PROMPT = "detailed"
DEFAULT_DESC_PARENT = ROOT / "experiments" / "E1" / "outputs"
DEFAULT_PRED_PARENT = ROOT / "experiments" / "E3" / "outputs"
CONSTRUCTOR_CHOICES = tuple(ic.E3_CONSTRUCTOR_KEYS) + ("all",)


def e3_combo_name(dataset: str, constructor: str) -> str:
    return f"{dataset}_{FIXED_PROMPT}_{constructor}"


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Verify identical fixed descriptions across E3 constructors.")
    ap.add_argument("--dataset", choices=rio.DATASET_CHOICES, required=True)
    ap.add_argument("--constructor", choices=CONSTRUCTOR_CHOICES, default="all",
                    help="constructors to check (default: all five)")
    ap.add_argument("--descriptions-dir", default=None,
                    help="fixed GPT-5.4-mini Detailed description directory "
                         f"(default experiments/E1/outputs/<dataset>_{FIXED_PROMPT}_{FIXED_DESCRIBER}/)")
    ap.add_argument("--pred-parent", default=None,
                    help="parent of <dataset>_detailed_<constructor>/ dirs "
                         "(default experiments/E3/outputs/)")
    ap.add_argument("--data-root", default=None)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--require-all-constructors", action="store_true",
                    help="fail if any selected constructor is missing a reconstruction for a gold id")
    return ap


def check_dataset(dataset: str, constructors: list[str], desc_dir: Path, pred_parent: Path,
                  *, data_root, limit, require_all: bool, strict: bool = True) -> list[str]:
    errors: list[str] = []
    gold = dio.load_dataset(dataset, data_root, strict=strict)
    gold = gold[:limit] if limit else gold
    if not desc_dir.is_dir():
        return [f"{dataset}: descriptions directory not found: {desc_dir}"]
    desc_preds = rio.load_prediction_dir(desc_dir)
    desc_aligned = {rec.schema_id: (rec, entry, reason)
                    for rec, entry, reason in rio.align_predictions(gold, desc_preds)}

    ctor_maps: dict[str, dict[str, tuple]] = {}
    for c in constructors:
        pdir = pred_parent / e3_combo_name(dataset, c)
        if not pdir.is_dir():
            if require_all:
                errors.append(f"{dataset}/{c}: prediction directory missing: {pdir}")
            continue
        aligned = rio.align_predictions(gold, rio.load_prediction_dir(pdir))
        ctor_maps[c] = {rec.schema_id: (rec, entry, reason) for rec, entry, reason in aligned}

    for rec in gold:
        sid = rec.schema_id
        _, desc_entry, desc_reason = desc_aligned[sid]
        if desc_reason or rio.nl_failure(desc_entry) is not None:
            errors.append(f"{dataset}/{sid}: missing/invalid fixed description "
                          f"({desc_reason or rio.nl_failure(desc_entry)})")
            continue
        expected = rio.description_hash(desc_entry)
        assert expected is not None
        for c, cmap in ctor_maps.items():
            _, entry, reason = cmap[sid]
            if reason is not None or entry is None:
                if require_all:
                    errors.append(f"{dataset}/{c}/{sid}: missing reconstruction ({reason})")
                continue
            # Prefer stored nl_sha256; fall back to hashing nl_text.
            got = entry.get("nl_sha256") if isinstance(entry.get("nl_sha256"), str) else None
            if not got:
                if rio.nl_failure({"nl_text": entry.get("nl_text")}) is not None:
                    errors.append(f"{dataset}/{c}/{sid}: reconstruction has no nl_text / nl_sha256")
                    continue
                got = rio.sha256_text(entry["nl_text"])
            if got != expected:
                errors.append(
                    f"{dataset}/{c}/{sid}: description hash mismatch "
                    f"(expected {expected[:12]}…, got {got[:12]}…)"
                )
            pid = entry.get("id")
            if pid and str(pid) != sid:
                errors.append(f"{dataset}/{c}/{sid}: id field {pid!r} does not match gold")
    return errors


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    datasets = rio.expand(args.dataset, rio.DATASETS)
    constructors = rio.expand(args.constructor, ic.E3_CONSTRUCTOR_KEYS)
    multi = len(datasets) > 1
    all_errors: list[str] = []
    for d in datasets:
        desc_combo = rio.combo_name(d, FIXED_PROMPT, FIXED_DESCRIBER)
        desc_dir = rio.combo_dir(args.descriptions_dir, DEFAULT_DESC_PARENT, desc_combo, multi=multi)
        pred_parent = Path(args.pred_parent) if args.pred_parent else DEFAULT_PRED_PARENT
        if multi and args.pred_parent:
            # When validating several datasets, --pred-parent is the shared parent.
            pass
        errs = check_dataset(d, constructors, desc_dir, pred_parent,
                             data_root=args.data_root, limit=args.limit,
                             require_all=args.require_all_constructors)
        all_errors.extend(errs)
        if not errs:
            print(f"[ok] {d}: fixed-description hashes match across "
                  f"{len(constructors)} constructor(s) (where reconstructions exist)")
        else:
            print(f"[FAIL] {d}: {len(errs)} isolation error(s)", file=sys.stderr)
            for e in errs[:20]:
                print(f"  - {e}", file=sys.stderr)
            if len(errs) > 20:
                print(f"  ... and {len(errs) - 20} more", file=sys.stderr)
    if all_errors:
        print(f"total isolation errors: {len(all_errors)}", file=sys.stderr)
        return 1
    print("constructor isolation verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
