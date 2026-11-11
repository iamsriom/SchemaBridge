#!/usr/bin/env python3
"""E2 offline evaluation: round-trip structural fidelity (Table VIII inputs).  No API, no generation.

Gold = the genuine DDL of the dataset (RSchema: the 381 DDL-matched schemas of
``annotation_ddl.jsonl``, NOT the 518 logical annotations with synthetic varchar DDL).  Each
reconstructed schema (``NNNN.json`` with ``ddl`` / ``metadata``) is scored with
``src.evaluator.evaluate_schema_pair``; the result is aggregated with ``aggregate_schemas``:

* micro-F1 for Tables / Attributes / Domain / Entity / Referential (summed counts),
* mean nGED (macro over schemas).

Every reconstruction gets a ``status`` (``rio.ddl_outcome``; column ``status`` of ``per_schema.csv``):

* ``ok``              non-empty reconstruction, scored with ``evaluate_schema_pair``;
* ``valid_empty``     successful record (no error, ``ddl`` key present) with an empty / comment-only DDL
                      for an EMPTY gold schema: scored through ``evaluate_schema_pair`` (nGED = 0), not failed;
* ``incorrect_empty`` successful but empty DDL against a NON-empty gold: scored through
                      ``evaluate_schema_pair`` as an empty prediction (natural nGED, not forced), not failed;
* ``scored_failure``  failed / missing / unreadable / error / skipped reconstruction under ``--fail-policy
                      score`` (default) -> ``empty_prediction_against_gold``: gold counts are kept,
                      recreated/matched are 0 and nGED = 1;
* ``skipped``         the same failures under ``--fail-policy skip``: dropped from all aggregates.

A missing prediction file is never a valid empty schema.  Files are written ONLY below ``--out-dir``
(git-ignored by default):

    <out-dir>/<dataset>_<prompt>_<describer>/metrics.json
    <out-dir>/<dataset>_<prompt>_<describer>/per_schema.csv
    <out-dir>/e2_summary.csv            (rows are upserted per dataset/describer/prompt)
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
from src.evaluator import aggregate_schemas, empty_prediction_against_gold, evaluate_schema_pair  # noqa: E402
from src.metrics import ELEMENTS  # noqa: E402
from src.schema_parser import metadata_from_ddl  # noqa: E402

DEFAULT_PRED_PARENT = ROOT / "experiments" / "E2" / "outputs"
DEFAULT_OUT_DIR = ROOT / "experiments" / "E2" / "outputs" / "metrics"
DESCRIBER_CHOICES = tuple(ic.DESCRIBER_KEYS) + ("all",)
SUMMARY_FIELDS = ("dataset", "describer_model", "prompt", "n_gold", "n_scored", "n_failed", "fail_policy",
                  *(f"f1_{e}" for e in ELEMENTS), "mean_nged")
RECORD_FIELDS = ("serial", "schema_id", "status", "failure_reason", "nged",
                 *(f"{e}_{k}" for e in ELEMENTS for k in ("gold", "recreated", "matched")))


def evaluate_combo(dataset: str, describer: str, prompt: str, pred_dir: Path, *, data_root: str | None,
                   fail_policy: str, strict: bool = True) -> tuple[dict, list[dict]]:
    """Return ``(metrics_json, per_schema_rows)`` for one reconstructed-schema directory."""
    gold = dio.load_dataset(dataset, data_root, strict=strict)
    aligned = rio.align_predictions(gold, rio.load_prediction_dir(pred_dir))
    items: list[dict] = []
    rows: list[dict] = []
    n_failed = n_valid_empty = n_incorrect_empty = 0
    for rec, entry, align_reason in aligned:
        g_meta = metadata_from_ddl(rec.ddl, database=rec.database)
        tc = len(g_meta.get("tables") or [])
        cc = sum(len(v or []) for v in (g_meta.get("columns_by_table") or {}).values())
        if align_reason is not None:
            outcome, reason = "failed", align_reason
        else:
            outcome, reason = rio.ddl_outcome(entry, rec.ddl, g_meta, schema_id=rec.schema_id)
        if outcome == "failed":
            n_failed += 1
            if fail_policy == "skip":
                rows.append({"serial": rec.serial, "schema_id": rec.schema_id, "status": "skipped",
                             "failure_reason": reason})
                continue
            res = empty_prediction_against_gold(g_meta, rec.ddl, table_count=tc, column_count=cc,
                                                failure_reason=reason)
            res["normalized_graph_edit_distance"] = 1.0  # failure policy: nGED = 1 even for an empty gold
            res["failed"] = True
            status = "scored_failure"
        elif outcome in ("valid_empty", "incorrect_empty"):
            # A successful but empty reconstruction: scored naturally as an empty prediction against the
            # gold (nGED 0 if the gold is empty too; whatever the evaluator yields otherwise -- not forced 1).
            res = evaluate_schema_pair(g_meta, rec.ddl, {}, "", table_count=tc, column_count=cc)
            res["failed"] = False
            status = outcome
            n_valid_empty += outcome == "valid_empty"
            n_incorrect_empty += outcome == "incorrect_empty"
        else:
            res = evaluate_schema_pair(g_meta, rec.ddl, entry.get("metadata") or {}, entry["ddl"],
                                       table_count=tc, column_count=cc)
            res["failed"] = False
            status = "ok"
        res["id"] = rec.schema_id
        items.append(res)
        row = {"serial": rec.serial, "schema_id": rec.schema_id, "status": status,
               "failure_reason": (reason or "") if status != "valid_empty" else "",
               "nged": res["normalized_graph_edit_distance"]}
        for e in ELEMENTS:
            row.update({f"{e}_{k}": res[e][k] for k in ("gold", "recreated", "matched")})
        rows.append(row)

    agg = aggregate_schemas(items)
    micro = {e: agg["five_elements"][e]["f1"] for e in ELEMENTS}
    out = {
        "experiment": "E2", "dataset": dataset, "describer_model": describer, "prompt": prompt,
        "prompt_style": rio.PROMPT_STYLE[prompt], "constructor": ic.MODELS[rio.CONSTRUCTOR_KEY].model_id,
        "describer_prompt_sha256": pa.EXPECTED_SHA256[prompt],
        "constructor_prompt_sha256": pa.EXPECTED_SHA256["constructor"],
        "gold_source": "annotation_ddl (genuine DDL)" if dataset != "enterprise145" else "enterprise145 .sql files",
        "fail_policy": fail_policy, "n_gold": len(gold), "n_scored": len(items), "n_failed": n_failed,
        "n_valid_empty": n_valid_empty, "n_incorrect_empty": n_incorrect_empty,
        "metrics": {"micro_f1": micro, "mean_nged": agg["mean_normalized_graph_edit_distance"]},
        "five_elements": agg["five_elements"], "exact_match_count": agg["exact_match_count"],
        "hallucination_micro": agg["mean_hallucination_rate_micro"], "pred_dir": str(pred_dir),
    }
    return out, rows


def summary_row(m: dict) -> dict:
    return {"dataset": m["dataset"], "describer_model": m["describer_model"], "prompt": m["prompt"],
            "n_gold": m["n_gold"], "n_scored": m["n_scored"], "n_failed": m["n_failed"],
            "fail_policy": m["fail_policy"], **{f"f1_{e}": m["metrics"]["micro_f1"][e] for e in ELEMENTS},
            "mean_nged": m["metrics"]["mean_nged"]}


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="E2 offline round-trip evaluation (micro-F1 x5 + mean nGED).")
    ap.add_argument("--dataset", choices=rio.DATASET_CHOICES, required=True)
    ap.add_argument("--describer-model", choices=DESCRIBER_CHOICES, required=True)
    ap.add_argument("--prompt", choices=rio.PROMPT_VARIANTS + ("all",), required=True)
    ap.add_argument("--pred-dir", default=None,
                    help="directory with reconstructed NNNN.json (default experiments/E2/outputs/"
                         "<dataset>_<prompt>_<describer>/ ; PARENT of such folders when several combinations)")
    ap.add_argument("--data-root", default=None,
                    help=f"dataset root (overrides ${dio.DATA_ROOT_ENV}; packaged datasets/ is the fallback)")
    ap.add_argument("--out-dir", default=None,
                    help="metrics output directory (default experiments/E2/outputs/metrics/, git-ignored)")
    ap.add_argument("--fail-policy", choices=("score", "skip"), default="score",
                    help="failed/missing reconstructions: score = F1 counts 0 with gold counts kept and nGED=1 "
                         "(default), skip = drop the schema")
    return ap


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    datasets = rio.expand(args.dataset, rio.DATASETS)
    describers = rio.expand(args.describer_model, ic.DESCRIBER_KEYS)
    prompts = rio.expand(args.prompt, rio.PROMPT_VARIANTS)
    multi = len(datasets) * len(describers) * len(prompts) > 1
    try:
        out_dir = rio.assert_ignored_out_dir(args.out_dir or DEFAULT_OUT_DIR)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    summary: list[dict] = []
    n_missing = 0
    for d in datasets:
        for p in prompts:
            for m in describers:
                combo = rio.combo_name(d, p, m)
                pred_dir = rio.combo_dir(args.pred_dir, DEFAULT_PRED_PARENT, combo, multi=multi)
                if not pred_dir.is_dir():
                    n_missing += 1
                    print(f"[skip] {combo}: prediction directory not found: {pred_dir}")
                    continue
                try:
                    metrics, rows = evaluate_combo(d, m, p, pred_dir, data_root=args.data_root,
                                                   fail_policy=args.fail_policy)
                except (FileNotFoundError, ValueError, KeyError) as e:
                    print(f"error: {e}", file=sys.stderr)
                    return 2
                rio.write_json(out_dir / combo / "metrics.json", metrics)
                rio.write_csv(out_dir / combo / "per_schema.csv", rows, RECORD_FIELDS)
                summary.append(summary_row(metrics))
                f1 = metrics["metrics"]["micro_f1"]
                print(f"[{combo}] gold={metrics['n_gold']} scored={metrics['n_scored']} failed={metrics['n_failed']} "
                      + " ".join(f"F1_{e[:3]}={f1[e]:.4f}" for e in ELEMENTS)
                      + f" nGED={metrics['metrics']['mean_nged']:.4f}")
    if summary:
        rio.upsert_csv(out_dir / "e2_summary.csv", summary, SUMMARY_FIELDS, ("dataset", "describer_model", "prompt"))
        print(f"wrote metrics under {out_dir}")
    elif n_missing:
        print("no prediction directory found; nothing evaluated", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
