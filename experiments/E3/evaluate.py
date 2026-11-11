#!/usr/bin/env python3
"""E3 offline evaluation: constructor isolation structural fidelity (Table IX inputs).  No API.

Gold = the genuine DDL of the dataset (RSchema: the 381 DDL-matched schemas of
``annotation_ddl.jsonl``, NOT the 518 logical annotations with synthetic varchar DDL).
Fixed descriptions are GPT-5.4-mini Detailed (E1).  Each reconstructed schema
(``NNNN.json`` with ``ddl`` / ``metadata``) is scored with ``src.evaluator.evaluate_schema_pair``
and aggregated with ``aggregate_schemas``:

* micro-F1 for Tables / Attributes / Domain / Entity / Referential (summed counts),
* mean nGED (macro over schemas); empty-gold + empty-reconstruction => nGED = 0,
* mean Hallucination = unweighted mean of *five* dimension-wise micro FP rates
  (T/A/D/E/R), ``(R−M)/R`` with ``R=0 → 0`` (historical Exp4 / Table IX convention).

Failed, missing, unreadable or malformed reconstructions follow ``--fail-policy``:
``score`` (default) -> ``empty_prediction_against_gold`` (nGED = 1, recreations = 0);
``skip`` drops them from aggregates.  Files are written ONLY below ``--out-dir``:

    <out-dir>/<dataset>_detailed_<constructor>/metrics.json
    <out-dir>/<dataset>_detailed_<constructor>/per_schema.csv
    <out-dir>/e3_summary.csv
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
from src import prompt_assets as pa  # noqa: E402
from src import repro_io as rio  # noqa: E402
from src.evaluator import (  # noqa: E402
    aggregate_schemas,
    empty_prediction_against_gold,
    evaluate_schema_pair,
)
from src.metrics import ELEMENTS, aggregate_hallucination_micro_5dim  # noqa: E402
from src.schema_parser import metadata_from_ddl  # noqa: E402

DEFAULT_PRED_PARENT = ROOT / "experiments" / "E3" / "outputs"
DEFAULT_OUT_DIR = ROOT / "experiments" / "E3" / "outputs" / "metrics"
FIXED_DESCRIBER = "gpt54mini"
FIXED_PROMPT = "detailed"
CONSTRUCTOR_CHOICES = tuple(ic.E3_CONSTRUCTOR_KEYS) + ("all",)
SUMMARY_FIELDS = ("dataset", "constructor", "n_gold", "n_scored", "n_failed", "fail_policy",
                  *(f"f1_{e}" for e in ELEMENTS), "mean_nged", "mean_hall")
RECORD_FIELDS = ("serial", "schema_id", "status", "failure_reason", "nged", "nl_sha256",
                 *(f"{e}_{k}" for e in ELEMENTS for k in ("gold", "recreated", "matched")))


def e3_combo_name(dataset: str, constructor: str) -> str:
    return f"{dataset}_{FIXED_PROMPT}_{constructor}"


def evaluate_combo(
    dataset: str,
    constructor: str,
    pred_dir: Path,
    *,
    data_root: str | None,
    fail_policy: str,
    strict: bool = True,
) -> tuple[dict, list[dict]]:
    """Return ``(metrics_json, per_schema_rows)`` for one reconstructed-schema directory."""
    gold = dio.load_dataset(dataset, data_root, strict=strict)
    aligned = rio.align_predictions(gold, rio.load_prediction_dir(pred_dir))
    items: list[dict] = []
    rows: list[dict] = []
    n_failed = 0
    for rec, entry, align_reason in aligned:
        g_meta = metadata_from_ddl(rec.ddl, database=rec.database)
        tc = len(g_meta.get("tables") or [])
        cc = sum(len(v or []) for v in (g_meta.get("columns_by_table") or {}).values())
        reason = align_reason or rio.e3_reconstruction_failure(
            entry, gold_ddl=rec.ddl, gold_meta=g_meta,
        )
        nl_hash = ""
        if entry and isinstance(entry.get("nl_sha256"), str):
            nl_hash = entry["nl_sha256"]
        elif entry and isinstance(entry.get("nl_text"), str) and entry["nl_text"].strip():
            nl_hash = rio.sha256_text(entry["nl_text"])

        if reason is not None:
            n_failed += 1
            if fail_policy == "skip":
                rows.append({"serial": rec.serial, "schema_id": rec.schema_id, "status": "skipped",
                             "failure_reason": reason, "nl_sha256": nl_hash})
                continue
            res = empty_prediction_against_gold(g_meta, rec.ddl, table_count=tc, column_count=cc,
                                                failure_reason=reason)
            status = "scored_empty"
        else:
            res = evaluate_schema_pair(g_meta, rec.ddl, entry.get("metadata") or {}, entry.get("ddl") or "",
                                       table_count=tc, column_count=cc)
            # Empty-gold + empty-pred is an exact structural success (nGED=0).
            if rio.gold_is_empty(rec.ddl, g_meta) and rio.pred_is_structurally_empty(
                entry.get("ddl") or "", entry.get("metadata") or {},
            ):
                res["normalized_graph_edit_distance"] = 0.0
                res["exact_match"] = True
                res["empty_gold_empty_pred"] = True
            status = "ok"
        res["id"] = rec.schema_id
        items.append(res)
        row = {"serial": rec.serial, "schema_id": rec.schema_id, "status": status,
               "failure_reason": reason or "", "nged": res["normalized_graph_edit_distance"],
               "nl_sha256": nl_hash}
        for e in ELEMENTS:
            row.update({f"{e}_{k}": res[e][k] for k in ("gold", "recreated", "matched")})
        rows.append(row)

    agg = aggregate_schemas(items)
    micro = {e: agg["five_elements"][e]["f1"] for e in ELEMENTS}
    # Table IX Hall. uses the historical five-dimensional micro mean (includes Domain).
    mean_hall = aggregate_hallucination_micro_5dim(items)
    out = {
        "experiment": "E3", "dataset": dataset, "constructor": constructor,
        "fixed_describer": FIXED_DESCRIBER, "fixed_prompt": FIXED_PROMPT,
        "prompt_style": rio.PROMPT_STYLE[FIXED_PROMPT],
        "constructor_model_id": ic.MODELS[constructor].model_id,
        "describer_prompt_sha256": pa.EXPECTED_SHA256[FIXED_PROMPT],
        "constructor_prompt_sha256": pa.EXPECTED_SHA256["constructor"],
        "gold_source": "annotation_ddl (genuine DDL)" if dataset != "enterprise145" else "enterprise145 .sql files",
        "fail_policy": fail_policy, "n_gold": len(gold), "n_scored": len(items), "n_failed": n_failed,
        "metrics": {
            "micro_f1": micro,
            "mean_nged": agg["mean_normalized_graph_edit_distance"],
            "mean_hall": mean_hall,
        },
        "five_elements": agg["five_elements"],
        "exact_match_count": agg["exact_match_count"],
        "hallucination_micro_5dim": mean_hall,
        "hallucination_micro_4dim_e0": agg["mean_hallucination_rate_micro"],
        "pred_dir": str(pred_dir),
    }
    return out, rows


def summary_row(m: dict) -> dict:
    return {"dataset": m["dataset"], "constructor": m["constructor"],
            "n_gold": m["n_gold"], "n_scored": m["n_scored"], "n_failed": m["n_failed"],
            "fail_policy": m["fail_policy"],
            **{f"f1_{e}": m["metrics"]["micro_f1"][e] for e in ELEMENTS},
            "mean_nged": m["metrics"]["mean_nged"], "mean_hall": m["metrics"]["mean_hall"]}


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description="E3 offline constructor-isolation evaluation "
                    "(micro-F1 x5 + mean nGED + 5-dim micro Hall.).",
    )
    ap.add_argument("--dataset", choices=rio.DATASET_CHOICES, required=True)
    ap.add_argument("--constructor", choices=CONSTRUCTOR_CHOICES, required=True)
    ap.add_argument("--pred-dir", default=None,
                    help="directory with reconstructed NNNN.json (default experiments/E3/outputs/"
                         "<dataset>_detailed_<constructor>/ ; PARENT when several combinations)")
    ap.add_argument("--data-root", default=None,
                    help=f"dataset root (overrides ${dio.DATA_ROOT_ENV}; packaged datasets/ is the fallback)")
    ap.add_argument("--out-dir", default=None,
                    help="metrics output directory (default experiments/E3/outputs/metrics/, git-ignored)")
    ap.add_argument("--fail-policy", choices=("score", "skip"), default="score",
                    help="failed/missing reconstructions: score = F1 counts 0 with gold counts kept "
                         "and nGED=1 (default), skip = drop the schema")
    return ap


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    datasets = rio.expand(args.dataset, rio.DATASETS)
    constructors = rio.expand(args.constructor, ic.E3_CONSTRUCTOR_KEYS)
    multi = len(datasets) * len(constructors) > 1
    try:
        out_dir = rio.assert_ignored_out_dir(args.out_dir or DEFAULT_OUT_DIR)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    summary: list[dict] = []
    n_missing = 0
    for d in datasets:
        for c in constructors:
            combo = e3_combo_name(d, c)
            pred_dir = rio.combo_dir(args.pred_dir, DEFAULT_PRED_PARENT, combo, multi=multi)
            if not pred_dir.is_dir():
                n_missing += 1
                print(f"[skip] {combo}: prediction directory not found: {pred_dir}")
                continue
            try:
                metrics, rows = evaluate_combo(d, c, pred_dir, data_root=args.data_root,
                                               fail_policy=args.fail_policy)
            except (FileNotFoundError, ValueError, KeyError) as e:
                print(f"error: {e}", file=sys.stderr)
                return 2
            rio.write_json(out_dir / combo / "metrics.json", metrics)
            rio.write_csv(out_dir / combo / "per_schema.csv", rows, RECORD_FIELDS)
            summary.append(summary_row(metrics))
            f1 = metrics["metrics"]["micro_f1"]
            print(f"[{combo}] gold={metrics['n_gold']} scored={metrics['n_scored']} "
                  f"failed={metrics['n_failed']} "
                  + " ".join(f"F1_{e[:3]}={f1[e]:.4f}" for e in ELEMENTS)
                  + f" nGED={metrics['metrics']['mean_nged']:.4f}"
                  + f" Hall={metrics['metrics']['mean_hall']:.4f}")
    if summary:
        rio.upsert_csv(out_dir / "e3_summary.csv", summary, SUMMARY_FIELDS, ("dataset", "constructor"))
        print(f"wrote metrics under {out_dir}")
    elif n_missing:
        print("no prediction directory found; nothing evaluated", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
