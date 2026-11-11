#!/usr/bin/env python3
"""Run the HISTORICAL Exp4 Text2Schema evaluator on packaged predictions.

Preserves algorithm from:
  experiments/E0/original_benchmarks/evaluation/evaluate_exp4_text2schema.py
  (logical annotation.jsonl gold → synthetic metadata+DDL; typed nGED;
   Domain gold == attribute count; 5-dim Hall mean)

Path adaptations only — no metric definition changes.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "third_party"))
sys.path.insert(0, str(ROOT / "experiments/E0/original_benchmarks/evaluation"))

# Import historical module with stubbed classification deps if needed
import importlib.util

# Provide stubs for schema_classification used only for size/content splits
import types
sc = types.ModuleType("schema_classification")
sc.CONTENT_LABELS = ("easy", "medium", "hard")
sc.SIZE_LABELS = ("small", "medium", "large")
sc._split_column_definitions = lambda *a, **k: []
sc._split_create_table_blocks = lambda *a, **k: []
sc.aggregate_five_elements_by_field = lambda items, field, labels, agg, names: ({}, {})
sc.aggregate_size_content_matrix = lambda items, agg, names: {}
sys.modules["schema_classification"] = sc

# Ensure evaluate_text2schema2 / evaluate_rschema_predictions resolve from third_party
import evaluate_text2schema2 as ev  # noqa: E402
import evaluate_rschema_predictions as erp  # noqa: E402

# Load historical evaluator module from original_benchmarks
spec = importlib.util.spec_from_file_location(
    "hist_eval",
    ROOT / "experiments/E0/original_benchmarks/evaluation/evaluate_exp4_text2schema.py",
)
hist = importlib.util.module_from_spec(spec)
# Patch DATA_ROOT paths before exec by injecting into module after load via run_evaluation call

# Monkeypatch: the module sets paths at import time; we only need functions.
# Temporarily put third_party modules where it expects evaluate_* names.
sys.modules["evaluate_text2schema2"] = ev
sys.modules["evaluate_rschema_predictions"] = erp

spec.loader.exec_module(hist)

MODEL_MAP = {
    "CodeLlama-13B": "codellama13b",
    "Llama-3.1-8B": "llama31",
    "DeepSeek-Coder-6.7B": "deepseek",
    "Claude Sonnet 4.6": "sonnet46",
    "GPT-5.4-mini": "gpt54mini",
}

PRED_DIRS = {
    "RSchema": {
        "codellama13b": ROOT / "results/predictions/e0/rschema_exp4_codellama13b",
        "llama31": ROOT / "results/predictions/e0/rschema_exp4_llama31",
        "deepseek": ROOT / "results/predictions/e0/rschema_exp4_deepseek",
        "sonnet46": ROOT / "results/predictions/e0/rschema_exp4_claude_sonnet_4_6",
        "gpt54mini": ROOT / "results/predictions/e0/rschema_exp4_gpt_5_4_mini",
    },
    "SchemaBench": {
        "codellama13b": ROOT / "results/predictions/e0/schemabench_exp2_codellama13b",
        "llama31": ROOT / "results/predictions/e0/schemabench_exp2_llama31",
        "deepseek": ROOT / "results/predictions/e0/schemabench_exp2_deepseek",
        "sonnet46": ROOT / "results/predictions/e0/schemabench_exp2_claude_sonnet_4_6",
        "gpt54mini": ROOT / "results/predictions/e0/schemabench_exp2_gpt_5_4_mini",
    },
}

GOLD = {
    "RSchema": ROOT / "datasets/rschema/annotation.jsonl",
    # SchemaBench historical Experiment2 used DDL annotation; Exp3 archive numbers match
    # SchemaBench DDL gold. For RSchema Exp3 used logical annotation.jsonl.
    "SchemaBench": ROOT / "datasets/schemabench/annotation_ddl.jsonl",
}


def evaluate_pred_dir(pred_dir: Path, gold_path: Path, llm_key: str) -> dict:
    """Core historical scoring without requiring text2schema_<llm> dirname layout."""
    ev.normalize_name = erp.normalize_rschema_name
    gold_by_id = {r["id"]: r for r in erp.load_jsonl(gold_path) if r.get("id")}
    items = []
    skipped = 0
    for pred_path in sorted(pred_dir.glob("[0-9][0-9][0-9][0-9].json")):
        try:
            pred_data = json.loads(pred_path.read_text(encoding="utf-8"))
        except Exception:
            skipped += 1
            continue
        rid = pred_data.get("id")
        gold_rec = gold_by_id.get(rid) if rid else None
        if not gold_rec:
            skipped += 1
            continue
        if pred_data.get("error") or pred_data.get("skipped") or not pred_data.get("ddl"):
            skipped += 1
            continue

        answer = gold_rec.get("answer")
        # RSchema logical: answer is dict of tables; SchemaBench: answer is DDL string
        if isinstance(answer, dict):
            table_count = sum(1 for t in answer.values() if isinstance(t, dict))
            column_count = sum(len(t.get("Attributes") or []) for t in answer.values() if isinstance(t, dict))
            orig_meta, orig_ddl = erp.gold_answer_to_metadata_and_ddl(answer, database=f"gold_{str(rid)[:8]}")
        elif isinstance(answer, str):
            # SchemaBench DDL gold — historical Experiment2 path
            orig_ddl = answer
            orig_meta = hist.metadata_from_ddl(orig_ddl, database=pred_data.get("database") or gold_rec.get("db_id") or "")
            # counts from meta
            table_count = len(orig_meta.get("tables") or [])
            column_count = sum(len(v or []) for v in (orig_meta.get("columns_by_table") or {}).values())
        else:
            skipped += 1
            continue

        pred_ddl = pred_data.get("ddl") or ""
        pred_meta = hist.ensure_prediction_metadata(
            pred_data.get("metadata") or {},
            pred_ddl,
            database=pred_data.get("database") or "",
        )
        m = ev.evaluate_one(
            pred_path.stem,
            orig_meta,
            orig_ddl,
            pred_meta,
            pred_ddl,
            table_count,
            column_count,
        )
        per = {
            "tables": {"gold": m.original_tables, "recreated": m.predicted_tables, "matched": m.matched_tables},
            "attributes": {"gold": m.original_attrs, "recreated": m.predicted_attrs, "matched": m.attr_matched},
            "domain": {"gold": m.original_attrs, "recreated": m.predicted_attrs, "matched": m.domain_matched},
            "entity": {
                "gold": m.entity_original_constraints,
                "recreated": m.entity_predicted_constraints,
                "matched": m.entity_matched_constraints,
            },
            "referential": {"gold": m.original_fks, "recreated": m.predicted_fks, "matched": m.fk_matched},
        }
        nged = hist.normalized_graph_edit_distance(orig_meta, orig_ddl, pred_meta, pred_ddl)
        items.append({**per, "normalized_graph_edit_distance": nged, "id": rid})

    five = {k: hist.agg_element(items, k) for k, _ in hist.FIVE_ELEMENT_NAMES}
    ngeds = [s["normalized_graph_edit_distance"] for s in items]
    mean_nged = sum(ngeds) / len(ngeds) if ngeds else 0.0
    hall_rates = [five[k]["hallucination_rate"] for k, _ in hist.FIVE_ELEMENT_NAMES]
    mean_hall = sum(hall_rates) / len(hall_rates) if hall_rates else 0.0
    return {
        "n": len(items),
        "skipped": skipped,
        "nged": mean_nged,
        "halluc": mean_hall,
        "tables": five["tables"]["f1"],
        "attributes": five["attributes"]["f1"],
        "domain": five["domain"]["f1"],
        "entity": five["entity"]["f1"],
        "referential": five["referential"]["f1"],
        "five_elements": five,
        "items": items,
    }


def main():
    out_rows = []
    for ds, models in PRED_DIRS.items():
        gold = GOLD[ds]
        for paper_name, key in MODEL_MAP.items():
            pred = models[key]
            print(f"Historical eval {ds} {paper_name} ...", flush=True)
            res = evaluate_pred_dir(pred, gold, key)
            print(
                f"  n={res['n']} skip={res['skipped']} nGED={res['nged']:.6f} Hall5={res['halluc']:.6f} "
                f"T={res['tables']:.6f} A={res['attributes']:.6f} D={res['domain']:.6f} "
                f"E={res['entity']:.6f} R={res['referential']:.6f}"
            )
            # domain gold check
            fe = res["five_elements"]
            print(f"  Domain G/P/M={fe['domain']['gold']}/{fe['domain']['recreated']}/{fe['domain']['matched']}")
            out_rows.append({
                "dataset": ds,
                "model": paper_name,
                "protocol": "HISTORICAL_EXP4_LOGICAL_OR_DDL",
                "n": res["n"],
                "skipped": res["skipped"],
                "nged": res["nged"],
                "halluc_5dim": res["halluc"],
                "tables": res["tables"],
                "attributes": res["attributes"],
                "domain": res["domain"],
                "entity": res["entity"],
                "referential": res["referential"],
                "domain_gold": fe["domain"]["gold"],
                "domain_pred": fe["domain"]["recreated"],
                "domain_matched": fe["domain"]["matched"],
                "attr_gold": fe["attributes"]["gold"],
            })
            # save per-model items summary without full dump
            (ROOT / "audit/historical_repro" / f"{ds}_{key}_summary.json").write_text(
                json.dumps({k: v for k, v in res.items() if k != "items"}, indent=2) + "\n"
            )

    import csv
    outp = ROOT / "audit/E0_HISTORICAL_REPRODUCTION.csv"
    with outp.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(out_rows)
    print("Wrote", outp)


if __name__ == "__main__":
    main()
