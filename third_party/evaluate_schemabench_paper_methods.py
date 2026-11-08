#!/usr/bin/env python3
"""Evaluate SchemaBench PaperMethods with Exp4 Text2Schema metrics (failed as zero)."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

DATA_ROOT = Path("/mnt/text2er-data")
sys.path.insert(0, str(DATA_ROOT / "Text2ER"))
sys.path.insert(0, str(DATA_ROOT / "Results" / "Text2Schema2Results"))
sys.path.insert(0, str(DATA_ROOT / "RSchemaCode"))
sys.path.insert(0, str(DATA_ROOT / "RSchema_ExpResults4" / "Code"))
sys.path.insert(0, str(DATA_ROOT / "LLM4DBdesign_PaperMethods"))
sys.path.insert(0, str(DATA_ROOT / "SchemaBench" / "Code"))

import evaluate_text2schema2 as ev  # noqa: E402
import evaluate_exp4_text2schema as exp4  # noqa: E402
from evaluate_rschema_predictions import (  # noqa: E402
    gold_answer_to_metadata_and_ddl,
    load_jsonl,
    normalize_rschema_name,
)
from evaluate_exp4_text2schema import metadata_from_ddl  # noqa: E402

# Reuse PaperMethods prediction loaders / helpers
import evaluate_paper_methods_exp4_metrics as pm  # noqa: E402

PAPER_ROOT = DATA_ROOT / "SchemaBench" / "PaperMethods"
GOLD_PATH = DATA_ROOT / "SchemaBench" / "Dataset" / "annotation_ddl.jsonl"
OUT_DIR = PAPER_ROOT / "Results"

# Point the imported loader at SchemaBench outputs
pm.PAPER_ROOT = PAPER_ROOT
pm.GOLD_PATH = GOLD_PATH
pm.OUT_DIR = OUT_DIR


def _meta_to_logical(meta: dict) -> dict:
    """Approx gold logical schema from DDL-derived metadata (for zero-row gold counts)."""
    tables = {}
    cbt = meta.get("columns_by_table") or {}
    for tname, cols in cbt.items():
        attrs = [c.get("COLUMN_NAME") for c in (cols or []) if c.get("COLUMN_NAME")]
        pk = [c["COLUMN_NAME"] for c in (cols or []) if str(c.get("COLUMN_KEY", "")).upper() == "PRI"]
        tables[tname] = {"Attributes": attrs, "Primary key": pk}
    return tables


def evaluate_method(model: str, method: str, gold_by_id: dict[str, dict]) -> dict:
    ev.normalize_name = normalize_rschema_name
    preds = pm.load_method_predictions(model, method)
    results_by_schema: dict[str, dict] = {}
    scored_zero = 0
    label = f"{model}/{method}"

    for idx, (rid, gold_rec) in enumerate(sorted(gold_by_id.items(), key=lambda x: x[0]), start=1):
        stem = f"{idx:04d}"
        gold_ddl = (gold_rec.get("answer") or "").strip()
        gold_db = gold_rec.get("database") or f"gold_{rid}"
        orig_meta = metadata_from_ddl(gold_ddl, database=gold_db)
        gold_logical = _meta_to_logical(orig_meta)

        table_count = len(orig_meta.get("tables") or [])
        column_count = sum(len(v or []) for v in (orig_meta.get("columns_by_table") or {}).values())
        difficulty = (
            "easy"
            if table_count <= 3 and column_count <= 30
            else "medium"
            if table_count <= 15 and column_count <= 150
            else "hard"
        )

        pred_answer = preds.get(rid) or {}
        if not pred_answer:
            results_by_schema[stem] = pm._zero_failed_row(rid, label, gold_logical, difficulty)
            scored_zero += 1
            continue

        pred_meta, pred_ddl = gold_answer_to_metadata_and_ddl(
            pred_answer, database=f"pred_{rid}"
        )

        m = ev.evaluate_one(
            stem,
            orig_meta,
            gold_ddl,
            pred_meta,
            pred_ddl,
            table_count,
            column_count,
        )
        per = {
            "tables": {
                "gold": m.original_tables,
                "recreated": m.predicted_tables,
                "matched": m.matched_tables,
            },
            "attributes": {
                "gold": m.original_attrs,
                "recreated": m.predicted_attrs,
                "matched": m.attr_matched,
            },
            "domain": {
                "gold": m.original_attrs,
                "recreated": m.predicted_attrs,
                "matched": m.domain_matched,
            },
            "entity": {
                "gold": m.entity_original_constraints,
                "recreated": m.entity_predicted_constraints,
                "matched": m.entity_matched_constraints,
            },
            "referential": {
                "gold": m.original_fks,
                "recreated": m.predicted_fks,
                "matched": m.fk_matched,
            },
        }
        exact = exp4.is_exact_match(**per)
        nged = exp4.normalized_graph_edit_distance(orig_meta, gold_ddl, pred_meta, pred_ddl)
        hall = {}
        for dim, row in per.items():
            r, h = row["recreated"], max(0, row["recreated"] - row["matched"])
            hall[dim] = h / r if r else 0.0
        per_f1 = {
            k: pm._f1_counts(per[k]["gold"], per[k]["recreated"], per[k]["matched"])
            for k, _ in exp4.FIVE_ELEMENT_NAMES
        }
        per_hall = sum(hall.values()) / len(hall) if hall else 0.0
        results_by_schema[stem] = {
            "id": rid,
            "llm": label,
            **per,
            "exact_match": exact,
            "normalized_graph_edit_distance": nged,
            "hallucination_rate_by_dimension": hall,
            "per_schema_f1": per_f1,
            "per_schema_hallucination": per_hall,
            "difficulty": m.difficulty,
            "scored_as_zero": False,
        }

    all_items = list(results_by_schema.values())
    n = len(all_items)
    five_elements_micro = {k: exp4.agg_element(all_items, k) for k, _ in exp4.FIVE_ELEMENT_NAMES}
    mean_nged = sum(s["normalized_graph_edit_distance"] for s in all_items) / n if n else 0.0
    mean_hall = sum(s.get("per_schema_hallucination", 0.0) for s in all_items) / n if n else 0.0
    five_elements = {}
    for k, _ in exp4.FIVE_ELEMENT_NAMES:
        macro_f1 = (
            sum((s.get("per_schema_f1") or {}).get(k, 0.0) for s in all_items) / n if n else 0.0
        )
        row = dict(five_elements_micro[k])
        row["f1"] = macro_f1
        row["f1_micro"] = five_elements_micro[k]["f1"]
        five_elements[k] = row

    return {
        "model": model,
        "method": method,
        "label": f"{pm.MODEL_LABEL[model]} {pm.METHOD_LABEL[method]}",
        "gold_path": str(GOLD_PATH),
        "total_schemas": n,
        "scored_ok": n - scored_zero,
        "scored_zero": scored_zero,
        "skipped": scored_zero,
        "gold_total": len(gold_by_id),
        "mean_normalized_graph_edit_distance": mean_nged,
        "mean_hallucination_rate": mean_hall,
        "exact_match_count": sum(1 for s in all_items if s.get("exact_match")),
        "five_elements": five_elements,
        "per_schema": results_by_schema,
    }


def main() -> None:
    gold_rows = load_jsonl(GOLD_PATH)
    gold_by_id = {r["id"]: r for r in gold_rows if r.get("id")}
    print(f"Gold: {GOLD_PATH} ({len(gold_by_id)} ids)", flush=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summaries = []
    for model in pm.MODELS:
        for method in pm.METHODS:
            print(f"Evaluating {model}/{method} ...", flush=True)
            summary = evaluate_method(model, method, gold_by_id)
            summaries.append(summary)
            fe = summary["five_elements"]
            print(
                f"  eval={summary['total_schemas']} zero={summary['scored_zero']} "
                f"nGED={summary['mean_normalized_graph_edit_distance']:.3f} "
                f"hall={summary['mean_hallucination_rate']:.3f} "
                f"T={fe['tables']['f1']:.3f} A={fe['attributes']['f1']:.3f} "
                f"D={fe['domain']['f1']:.3f} E={fe['entity']['f1']:.3f} "
                f"R={fe['referential']['f1']:.3f}",
                flush=True,
            )
            (OUT_DIR / f"{model}_{method}_evaluation.json").write_text(
                json.dumps({k: v for k, v in summary.items() if k != "per_schema"}, indent=2),
                encoding="utf-8",
            )

    table = pm.build_summary_table(summaries)
    report = (
        "SchemaBench PaperMethods — Exp4 metrics\n"
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        f"Gold: {GOLD_PATH} ({len(gold_by_id)} records)\n"
        f"Predictions: {PAPER_ROOT}/<model>/<method>/\n"
        "Failed / missing / empty predictions scored as zero and included in means:\n"
        "  F1=0, nGED=1.0, Hallucination=1.0\n"
        "nGED / Hallucination lower better; F1 higher better.\n\n"
        + table
        + "\n"
    )
    report_path = OUT_DIR / "schemabench_paper_methods_report.txt"
    report_path.write_text(report, encoding="utf-8")
    combined = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "gold_path": str(GOLD_PATH),
        "methods": [{k: v for k, v in s.items() if k != "per_schema"} for s in summaries],
    }
    (OUT_DIR / "schemabench_paper_methods_evaluation.json").write_text(
        json.dumps(combined, indent=2), encoding="utf-8"
    )
    print("\n" + table)
    print(f"\nWrote {report_path}")


if __name__ == "__main__":
    main()
