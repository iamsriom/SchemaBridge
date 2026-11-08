#!/usr/bin/env python3
"""
Offline recompute of Figure 5 (E0: F1 by Schema Size × Constraint Complexity).

Uses existing gold schemata + saved E0 predictions. Does NOT run LLMs.
Reuses SchemaBench/RSchema Exp4 evaluators and the corrected DDL parser.
"""
from __future__ import annotations

import csv
import json
import math
import re
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

DATA = Path("/data")
OUT = DATA / "experiments" / "fig5_corrected_e0"

sys.path.insert(0, str(DATA / "Text2ER"))
sys.path.insert(0, str(DATA / "Results" / "Text2Schema2Results"))
sys.path.insert(0, str(DATA / "RSchemaCode"))
sys.path.insert(0, str(DATA / "RSchema_ExpResults4" / "Code"))
sys.path.insert(0, str(DATA / "LLM4DBdesign_PaperMethods"))
sys.path.insert(0, str(DATA / "SchemaBench" / "Code"))
sys.path.insert(0, str(DATA / "SchemaBench" / "PaperMethods" / "logs"))

import evaluate_text2schema2 as ev  # noqa: E402
import evaluate_exp4_text2schema as exp4  # noqa: E402
from evaluate_rschema_predictions import (  # noqa: E402
    gold_answer_to_metadata_and_ddl,
    load_jsonl,
    normalize_rschema_name,
)
from evaluate_exp4_text2schema import metadata_from_ddl, ensure_prediction_metadata  # noqa: E402
import evaluate_paper_methods_exp4_metrics as pm  # noqa: E402
import evaluate_schemabench_paper_methods as sb_eval  # noqa: E402

ev.normalize_name = normalize_rschema_name

# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------
RSCHEMA_GOLD = DATA / "RSchema" / "annotation.jsonl"
if not RSCHEMA_GOLD.is_file():
    RSCHEMA_GOLD = DATA / "LLM4DBdesign-main" / "datasets" / "RSchema" / "annotation.jsonl"
SCHEMABENCH_GOLD = DATA / "SchemaBench" / "Dataset" / "annotation_ddl.jsonl"

RSCHEMA_PRED = {
    "CodeLlama-13B": DATA / "RSchema_ExpResults4" / "Experiments" / "text2schema_codellama13b",
    "Llama-3.1-8B": DATA / "RSchema_ExpResults4" / "Experiments" / "text2schema_llama31",
    "DeepSeek-Coder": DATA / "RSchema_ExpResults4" / "Experiments" / "text2schema_deepseek",
}
SCHEMABENCH_PAPER_ROOT = DATA / "SchemaBench" / "PaperMethods"
SCHEMABENCH_MODEL_DIR = {
    "CodeLlama-13B": "codellama13b",
    "Llama-3.1-8B": "llama31",
    "DeepSeek-Coder": "deepseek",
}
SCHEMABENCH_PROMPT = "few_shot"
RSCHEMA_PROMPT = "exp4_text2schema_from_gold_nl"  # DDL generation from gold requirements

OPEN_MODELS = ["CodeLlama-13B", "Llama-3.1-8B", "DeepSeek-Coder"]
PROPRIETARY_MODELS = ["Claude Sonnet 4.6", "GPT-5.4-mini"]

PARSER_PATHS = [
    str(DATA / "SchemaBench" / "Code" / "evaluate_exp4_text2schema.py"),
    str(DATA / "Results" / "Text2Schema2Results" / "evaluate_text2schema2.py"),
]
EVAL_PATHS = [
    str(DATA / "Results" / "Text2Schema2Results" / "evaluate_text2schema2.py"),
    str(DATA / "SchemaBench" / "Code" / "evaluate_exp4_text2schema.py"),
    str(DATA / "SchemaBench" / "PaperMethods" / "logs" / "evaluate_schemabench_paper_methods.py"),
    str(DATA / "LLM4DBdesign_PaperMethods" / "evaluate_paper_methods_exp4_metrics.py"),
]

EXPECTED_TABLE_VII = {
    "RSchema": {
        "CodeLlama-13B": dict(nged=0.734, hall=0.694, tables=0.554, attributes=0.415, domain=0.217, entity=0.301, referential=0.139),
        "Llama-3.1-8B": dict(nged=0.764, hall=0.731, tables=0.572, attributes=0.375, domain=0.181, entity=0.169, referential=0.102),
        "DeepSeek-Coder": dict(nged=0.733, hall=0.633, tables=0.566, attributes=0.441, domain=0.214, entity=0.388, referential=0.182),
        "Claude Sonnet 4.6": dict(nged=0.780, hall=0.687, tables=0.602, attributes=0.400, domain=0.123, entity=0.407, referential=0.201),
        "GPT-5.4-mini": dict(nged=0.777, hall=0.660, tables=0.600, attributes=0.433, domain=0.133, entity=0.399, referential=0.221),
    },
    "SchemaBench": {
        "CodeLlama-13B": dict(nged=0.901, hall=0.718, tables=0.373, attributes=0.147, domain=0.053, entity=0.191, referential=0.020),
        "Llama-3.1-8B": dict(nged=0.898, hall=0.827, tables=0.378, attributes=0.140, domain=0.052, entity=0.189, referential=0.034),
        "DeepSeek-Coder": dict(nged=0.893, hall=0.796, tables=0.393, attributes=0.145, domain=0.054, entity=0.186, referential=0.052),
        "Claude Sonnet 4.6": dict(nged=0.685, hall=0.643, tables=0.530, attributes=0.278, domain=0.192, entity=0.345, referential=0.264),
        "GPT-5.4-mini": dict(nged=0.760, hall=0.685, tables=0.466, attributes=0.217, domain=0.144, entity=0.255, referential=0.175),
    },
}

HISTORICAL_FIG5 = {
    ("Small", "Easy"): 0.25,
    ("Small", "Medium"): 0.34,
    ("Small", "Hard"): 0.35,
    ("Medium", "Easy"): 0.18,
    ("Medium", "Medium"): 0.29,
    ("Medium", "Hard"): 0.31,
    ("Large", "Easy"): 0.04,
    ("Large", "Medium"): None,  # empty
    ("Large", "Hard"): 0.15,
}

SIZE_ORDER = ["Small", "Medium", "Large"]
COMPLEXITY_ORDER = ["Easy", "Medium", "Hard"]


def round3(x: float) -> float:
    return float(f"{x:.3f}")


def f1_from_counts(g: int, r: int, m: int) -> tuple[float, float, float]:
    p = m / r if r else 0.0
    rec = m / g if g else 0.0
    if g == 0 and r == 0:
        # evaluator treats empty/empty as perfect on some dims via recall=1 when gold empty;
        # for F1 from counts used in reports: 0/0 -> 0 unless both empty for tables in evaluate_one.
        # Match evaluate_one's P/R then F1:
        p = 1.0
        rec = 1.0
    f1 = 2 * p * rec / (p + rec) if (p + rec) else 0.0
    return p, rec, f1


def schema_size(n_tab: int, n_col: int) -> str:
    if n_tab <= 5 and n_col <= 50:
        return "Small"
    if n_tab <= 15 and n_col <= 150:
        return "Medium"
    return "Large"


def constraint_score(f: int, c: int, u: int, n_col: int, n_tab: int) -> float:
    if n_tab <= 0:
        return float("nan")
    return (
        2 * min(f, 10)
        + 3 * c
        + min(u, 5)
        + (1.0 / 5.0) * max(0.0, (n_col / n_tab) - 10.0)
    )


def complexity_category(s: float) -> str:
    if math.isnan(s):
        return "INVALID"
    if s < 4:
        return "Easy"
    if s < 10:
        return "Medium"
    return "Hard"


def unique_excluding_pk(primaries, uniques) -> int:
    pk_sets = {(t, tuple(sorted(c.lower() for c in cols))) for t, cols in primaries}
    count = 0
    for t, cols in uniques:
        key = (t, tuple(sorted(c.lower() for c in cols)))
        if key in pk_sets:
            continue
        count += 1
    return count


def gold_features_from_ddl(ddl: str) -> dict:
    meta = metadata_from_ddl(ddl)
    tables = meta.get("tables") or []
    n_tab = len(tables)
    n_col = sum(len(v or []) for v in (meta.get("columns_by_table") or {}).values())
    fks, n_comp = ev.parse_ddl_fks(ddl)
    primaries, uniques = ev.parse_ddl_primary_unique(ddl)
    u = unique_excluding_pk(primaries, uniques)
    f = len(fks)
    c = n_comp
    status = "ok" if n_tab > 0 else "empty_or_unparsed"
    s = constraint_score(f, c, u, n_col, n_tab)
    return {
        "n_tab": n_tab,
        "n_col": n_col,
        "f": f,
        "c": c,
        "u": u,
        "constraint_score": s,
        "size_category": schema_size(n_tab, n_col) if n_tab > 0 else "INVALID",
        "complexity_category": complexity_category(s),
        "gold_parse_status": status,
        "meta": meta,
        "ddl": ddl,
    }


def gold_features_from_structured(answer: dict) -> dict:
    meta, ddl = gold_answer_to_metadata_and_ddl(answer, database="gold")
    # Prefer structural counts from answer for size; FK/UNIQUE from answer + DDL parse for constraints
    n_tab = 0
    n_col = 0
    f = 0
    c = 0
    for _t, tdef in (answer or {}).items():
        if not isinstance(tdef, dict):
            continue
        n_tab += 1
        attrs = tdef.get("Attributes") or []
        if isinstance(attrs, list):
            n_col += len(attrs)
        fks = tdef.get("Foreign key") or tdef.get("Foreignkey") or {}
        if isinstance(fks, dict):
            for _src, ref in fks.items():
                f += 1
                # structured RSchema FKs are single-column edges
                if isinstance(ref, dict) and len(ref) > 1:
                    c += 1
    # UNIQUE rarely present in RSchema structured answers; count from synthetic DDL excluding PKs
    primaries, uniques = ev.parse_ddl_primary_unique(ddl)
    u = unique_excluding_pk(primaries, uniques)
    # Prefer DDL-parsed FK composite count when available (synthetic DDL expands structured FKs)
    fks_ddl, c_ddl = ev.parse_ddl_fks(ddl)
    if fks_ddl:
        f = len(fks_ddl)
        c = c_ddl
    status = "ok" if n_tab > 0 else "empty_or_unparsed"
    s = constraint_score(f, c, u, n_col, n_tab)
    return {
        "n_tab": n_tab,
        "n_col": n_col,
        "f": f,
        "c": c,
        "u": u,
        "constraint_score": s,
        "size_category": schema_size(n_tab, n_col) if n_tab > 0 else "INVALID",
        "complexity_category": complexity_category(s),
        "gold_parse_status": status,
        "meta": meta,
        "ddl": ddl,
        "answer": answer,
    }


def dim_prf(item: dict, key: str) -> tuple[float, float, float]:
    row = item[key]
    return f1_from_counts(row["gold"], row["recreated"], row["matched"])


def mean_structural_f1(item: dict) -> float:
    vals = []
    for key in ("tables", "attributes", "domain", "entity", "referential"):
        _p, _r, f1 = dim_prf(item, key)
        vals.append(f1)
    return sum(vals) / 5.0


# ---------------------------------------------------------------------------
# Load gold
# ---------------------------------------------------------------------------
def load_rschema_gold() -> dict[str, dict]:
    out = {}
    for rec in load_jsonl(RSCHEMA_GOLD):
        rid = rec.get("id")
        if not rid:
            continue
        feats = gold_features_from_structured(rec.get("answer") or {})
        feats["dataset"] = "RSchema"
        feats["schema_id"] = rid
        out[rid] = feats
    return out


def load_schemabench_gold() -> dict[str, dict]:
    out = {}
    for rec in load_jsonl(SCHEMABENCH_GOLD):
        rid = rec.get("id")
        if not rid:
            continue
        ddl = (rec.get("answer") or "").strip()
        feats = gold_features_from_ddl(ddl)
        feats["dataset"] = "SchemaBench"
        feats["schema_id"] = rid
        out[rid] = feats
    return out


# ---------------------------------------------------------------------------
# Evaluate predictions
# ---------------------------------------------------------------------------
def evaluate_rschema_pred(gold_feats: dict, pred_path: Path) -> dict:
    if not pred_path.is_file():
        return {"error": "missing_prediction", "scored_as_zero": True}
    try:
        pred = json.loads(pred_path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"error": f"json_error:{e}", "scored_as_zero": True}
    if pred.get("error") or pred.get("skipped") or not (pred.get("ddl") or "").strip():
        return {
            "error": pred.get("error") or pred.get("skip_reason") or "missing_ddl",
            "scored_as_zero": True,
            "prediction_parse_status": "failed_or_empty",
        }
    pred_ddl = pred.get("ddl") or ""
    pred_meta = ensure_prediction_metadata(
        pred.get("metadata") or {}, pred_ddl, database=pred.get("database") or ""
    )
    orig_meta = gold_feats["meta"]
    orig_ddl = gold_feats["ddl"]
    m = ev.evaluate_one(
        pred_path.stem,
        orig_meta,
        orig_ddl,
        pred_meta,
        pred_ddl,
        gold_feats["n_tab"],
        gold_feats["n_col"],
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
    return {
        "per": per,
        "scored_as_zero": False,
        "prediction_parse_status": "ok",
        "nged": exp4.normalized_graph_edit_distance(orig_meta, orig_ddl, pred_meta, pred_ddl),
    }


def evaluate_schemabench_pred(gold_feats: dict, pred_answer: dict | None, rid: str) -> dict:
    if not pred_answer:
        # zero row consistent with paper-methods zero policy
        per = {
            "tables": {"gold": gold_feats["n_tab"], "recreated": 0, "matched": 0},
            "attributes": {"gold": gold_feats["n_col"], "recreated": 0, "matched": 0},
            "domain": {"gold": gold_feats["n_col"], "recreated": 0, "matched": 0},
            "entity": {"gold": 0, "recreated": 0, "matched": 0},
            "referential": {"gold": gold_feats["f"], "recreated": 0, "matched": 0},
        }
        # entity gold from DDL
        pks, uqs = ev.parse_ddl_primary_unique(gold_feats["ddl"])
        per["entity"]["gold"] = len(pks) + len(uqs)
        return {
            "per": per,
            "scored_as_zero": True,
            "prediction_parse_status": "missing_or_empty",
            "nged": 1.0,
        }
    orig_meta = gold_feats["meta"]
    orig_ddl = gold_feats["ddl"]
    pred_meta, pred_ddl = gold_answer_to_metadata_and_ddl(pred_answer, database=f"pred_{rid}")
    m = ev.evaluate_one(
        rid,
        orig_meta,
        orig_ddl,
        pred_meta,
        pred_ddl,
        gold_feats["n_tab"],
        gold_feats["n_col"],
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
    return {
        "per": per,
        "scored_as_zero": False,
        "prediction_parse_status": "ok",
        "nged": exp4.normalized_graph_edit_distance(orig_meta, orig_ddl, pred_meta, pred_ddl),
    }


def row_from_eval(dataset, schema_id, model, prompt, gold_feats, ev_out) -> dict:
    per = ev_out["per"]
    dims = {}
    f1s = []
    for key, prefix in [
        ("tables", "table"),
        ("attributes", "attribute"),
        ("domain", "domain"),
        ("entity", "entity"),
        ("referential", "referential"),
    ]:
        p, r, f1 = f1_from_counts(per[key]["gold"], per[key]["recreated"], per[key]["matched"])
        # Align empty-gold behaviour with evaluate_one for precision/recall used in F1 mean:
        # when gold=0, evaluate_one sets recall=1.0; when pred=0 and gold>0, precision undefined->0
        if per[key]["gold"] == 0:
            r = 1.0
            p = 1.0 if per[key]["recreated"] == 0 else (per[key]["matched"] / per[key]["recreated"])
            f1 = 2 * p * r / (p + r) if (p + r) else 0.0
        dims[f"{prefix}_precision"] = p
        dims[f"{prefix}_recall"] = r
        dims[f"{prefix}_f1"] = f1
        f1s.append(f1)
    return {
        "dataset": dataset,
        "schema_id": schema_id,
        "model": model,
        "prompt_configuration": prompt,
        "gold_table_count": gold_feats["n_tab"],
        "gold_column_count": gold_feats["n_col"],
        "gold_fk_count": gold_feats["f"],
        "gold_composite_fk_count": gold_feats["c"],
        "gold_unique_count": gold_feats["u"],
        "constraint_score": gold_feats["constraint_score"],
        "size_category": gold_feats["size_category"],
        "complexity_category": gold_feats["complexity_category"],
        "gold_parse_status": gold_feats["gold_parse_status"],
        "prediction_parse_status": ev_out.get("prediction_parse_status", "ok"),
        **dims,
        "mean_structural_f1": sum(f1s) / 5.0,
        "scored_as_zero": bool(ev_out.get("scored_as_zero")),
        "nged": ev_out.get("nged", 1.0),
    }


def hall_rate(per: dict) -> float:
    rates = []
    for key in ("tables", "attributes", "domain", "entity", "referential"):
        r = per[key]["recreated"]
        m = per[key]["matched"]
        rates.append((max(0, r - m) / r) if r else 0.0)
    return sum(rates) / len(rates)


# ---------------------------------------------------------------------------
# Table VII validation helpers
# ---------------------------------------------------------------------------
def aggregate_table_vii(rows: list[dict], use_macro_f1: bool) -> dict:
    """Aggregate overall metrics for one model on one dataset."""
    if not rows:
        return {}
    n = len(rows)
    mean_nged = sum(r["nged"] for r in rows) / n
    # hallucination from stored per if available — recompute from dim extras not stored;
    # use mean of per-schema hall if we stash it
    mean_hall = sum(r.get("per_schema_hallucination", 0.0) for r in rows) / n
    out = {"nged": mean_nged, "hall": mean_hall}
    if use_macro_f1:
        for key, prefix in [
            ("tables", "table"),
            ("attributes", "attribute"),
            ("domain", "domain"),
            ("entity", "entity"),
            ("referential", "referential"),
        ]:
            out[key] = sum(r[f"{prefix}_f1"] for r in rows) / n
    else:
        # micro: pool counts — need gold/recreated/matched; not in row. Skip here.
        pass
    return out


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()

    print("=== Loading gold ===", flush=True)
    rschema_gold = load_rschema_gold()
    sb_gold = load_schemabench_gold()
    print(f"RSchema gold: {len(rschema_gold)}  SchemaBench gold: {len(sb_gold)}", flush=True)

    gold_parse_failures = {
        "RSchema": sum(1 for g in rschema_gold.values() if g["gold_parse_status"] != "ok"),
        "SchemaBench": sum(1 for g in sb_gold.values() if g["gold_parse_status"] != "ok"),
    }
    print("Gold parse failures:", gold_parse_failures, flush=True)

    # Size/complexity distribution
    def dist(gold_map):
        d = defaultdict(int)
        for g in gold_map.values():
            d[(g["size_category"], g["complexity_category"])] += 1
        return dict(d)

    print("RSchema strata:", dist(rschema_gold), flush=True)
    print("SchemaBench strata:", dist(sb_gold), flush=True)

    per_schema_rows: list[dict] = []
    pred_failures = 0
    validation = {"RSchema": {}, "SchemaBench": {}, "status": "PASS", "notes": []}

    # ----- RSchema open models (Exp4 predictions) -----
    print("=== Evaluating RSchema Exp4 predictions ===", flush=True)
    # Map id -> stem via index or file content
    for model, pred_dir in RSCHEMA_PRED.items():
        rows_for_model = []
        files = sorted(pred_dir.glob("[0-9][0-9][0-9][0-9].json"))
        print(f"  {model}: {len(files)} prediction files", flush=True)
        for fp in files:
            pred = json.loads(fp.read_text(encoding="utf-8"))
            rid = pred.get("id")
            if rid not in rschema_gold:
                continue
            gold_feats = rschema_gold[rid]
            ev_out = evaluate_rschema_pred(gold_feats, fp)
            if ev_out.get("scored_as_zero"):
                pred_failures += 1
                # zero per counts
                pks, uqs = ev.parse_ddl_primary_unique(gold_feats["ddl"])
                ev_out["per"] = {
                    "tables": {"gold": gold_feats["n_tab"], "recreated": 0, "matched": 0},
                    "attributes": {"gold": gold_feats["n_col"], "recreated": 0, "matched": 0},
                    "domain": {"gold": gold_feats["n_col"], "recreated": 0, "matched": 0},
                    "entity": {"gold": len(pks) + len(uqs), "recreated": 0, "matched": 0},
                    "referential": {"gold": gold_feats["f"], "recreated": 0, "matched": 0},
                }
                ev_out["nged"] = 1.0
                ev_out["prediction_parse_status"] = ev_out.get("prediction_parse_status", "failed")
            row = row_from_eval("RSchema", rid, model, RSCHEMA_PROMPT, gold_feats, ev_out)
            row["per_schema_hallucination"] = hall_rate(ev_out["per"]) if not ev_out.get("scored_as_zero") else 1.0
            # Fix F1 empty-gold using evaluate_one semantics already applied in row_from_eval
            per_schema_rows.append(row)
            rows_for_model.append(row)

        # Table VII style: for RSchema Exp4 the published table uses MICRO F1
        # Compute micro from pooled counts by re-evaluating quickly via saved structure
        # Macro mean of per-schema F1 for cross-check; micro for Table VII compare
        n = len(rows_for_model)
        mean_nged = sum(r["nged"] for r in rows_for_model) / n if n else 0
        mean_hall = sum(r["per_schema_hallucination"] for r in rows_for_model) / n if n else 0
        # micro via Exp4 evaluation JSON if available
        validation["RSchema"][model] = {
            "n": n,
            "nged": round3(mean_nged),
            "hall": round3(mean_hall),
            "tables_macro": round3(sum(r["table_f1"] for r in rows_for_model) / n),
            "attributes_macro": round3(sum(r["attribute_f1"] for r in rows_for_model) / n),
            "domain_macro": round3(sum(r["domain_f1"] for r in rows_for_model) / n),
            "entity_macro": round3(sum(r["entity_f1"] for r in rows_for_model) / n),
            "referential_macro": round3(sum(r["referential_f1"] for r in rows_for_model) / n),
        }

    # Load Exp4 micro from saved evaluation for Table VII check
    exp4_eval = json.loads(
        (DATA / "RSchema_ExpResults4" / "Experiments" / "Results" / "text2schema_exp4_evaluation.json").read_text()
    )
    llm_map = {"codellama13b": "CodeLlama-13B", "llama31": "Llama-3.1-8B", "deepseek": "DeepSeek-Coder"}
    for s in exp4_eval.get("llms") or []:
        model = llm_map.get(s.get("llm"))
        if not model:
            continue
        fe = s.get("five_elements") or {}
        got = {
            "nged": round3(s.get("mean_normalized_graph_edit_distance", 0)),
            "hall": None,  # Exp4 report doesn't store mean hall the same way
            "tables": round3(fe.get("tables", {}).get("f1", 0)),
            "attributes": round3(fe.get("attributes", {}).get("f1", 0)),
            "domain": round3(fe.get("domain", {}).get("f1", 0)),
            "entity": round3(fe.get("entity", {}).get("f1", 0)),
            "referential": round3(fe.get("referential", {}).get("f1", 0)),
        }
        exp = EXPECTED_TABLE_VII["RSchema"][model]
        diffs = {k: (got[k], exp[k]) for k in ("nged", "tables", "attributes", "domain", "entity", "referential") if got[k] != exp[k]}
        validation["RSchema"][model]["table_vii_micro_from_exp4_json"] = got
        validation["RSchema"][model]["table_vii_expected"] = exp
        validation["RSchema"][model]["table_vii_diffs"] = diffs
        if diffs:
            validation["status"] = "FAIL"
            validation["notes"].append(f"RSchema {model} Exp4 micro differs from Table VII: {diffs}")

    # ----- SchemaBench few-shot -----
    print("=== Evaluating SchemaBench few-shot PaperMethods ===", flush=True)
    pm.PAPER_ROOT = SCHEMABENCH_PAPER_ROOT
    pm.GOLD_PATH = SCHEMABENCH_GOLD
    sb_eval.pm = pm
    sb_eval.PAPER_ROOT = SCHEMABENCH_PAPER_ROOT
    sb_eval.GOLD_PATH = SCHEMABENCH_GOLD

    sb_gold_by_id = {}
    for rec in load_jsonl(SCHEMABENCH_GOLD):
        if rec.get("id"):
            sb_gold_by_id[rec["id"]] = rec

    for model, mdir in SCHEMABENCH_MODEL_DIR.items():
        print(f"  {model} / few_shot ...", flush=True)
        summary = sb_eval.evaluate_method(mdir, SCHEMABENCH_PROMPT, sb_gold_by_id)
        fe = summary["five_elements"]
        got = {
            "nged": round3(summary["mean_normalized_graph_edit_distance"]),
            "hall": round3(summary["mean_hallucination_rate"]),
            "tables": round3(fe["tables"]["f1"]),
            "attributes": round3(fe["attributes"]["f1"]),
            "domain": round3(fe["domain"]["f1"]),
            "entity": round3(fe["entity"]["f1"]),
            "referential": round3(fe["referential"]["f1"]),
        }
        exp = EXPECTED_TABLE_VII["SchemaBench"][model]
        diffs = {k: (got[k], exp[k]) for k in exp if got[k] != exp[k]}
        validation["SchemaBench"][model] = {
            "got": got,
            "expected": exp,
            "diffs": diffs,
            "zero": summary.get("scored_zero"),
            "n": summary.get("total_schemas"),
        }
        if diffs:
            # allow 0.001 float noise
            real = {k: v for k, v in diffs.items() if abs(v[0] - v[1]) > 0.0015}
            if real:
                validation["status"] = "FAIL"
                validation["notes"].append(f"SchemaBench {model} differs from Table VII: {real}")
            else:
                validation["notes"].append(f"SchemaBench {model}: 3dp rounding noise only {diffs}")

        # Per-schema rows from summary
        for stem, item in summary["per_schema"].items():
            rid = item["id"]
            gold_feats = sb_gold[rid]
            # Rebuild PRF from item counts
            ev_out = {
                "per": {k: item[k] for k in ("tables", "attributes", "domain", "entity", "referential")},
                "scored_as_zero": bool(item.get("scored_as_zero")),
                "prediction_parse_status": "missing_or_empty" if item.get("scored_as_zero") else "ok",
                "nged": item.get("normalized_graph_edit_distance", 1.0),
            }
            if item.get("scored_as_zero"):
                pred_failures += 1
            row = row_from_eval("SchemaBench", rid, model, SCHEMABENCH_PROMPT, gold_feats, ev_out)
            row["per_schema_hallucination"] = item.get("per_schema_hallucination", 1.0 if item.get("scored_as_zero") else 0.0)
            per_schema_rows.append(row)

    # Proprietary models: missing predictions
    for model in PROPRIETARY_MODELS:
        validation["notes"].append(
            f"MISSING per-schema predictions for {model} on both datasets; "
            "Table VII values exist only as paper aggregates."
        )
        validation["status"] = "FAIL"

    # ----- Heatmap aggregation -----
    # Equal weight: each schema-model pair; with incomplete models, only available models.
    cells = defaultdict(list)  # (size, complexity) -> list of mean_structural_f1
    cell_schemas = defaultdict(set)
    cell_by_model = defaultdict(list)

    for r in per_schema_rows:
        if r["size_category"] == "INVALID" or r["complexity_category"] == "INVALID":
            continue
        key = (r["size_category"], r["complexity_category"])
        cells[key].append(r["mean_structural_f1"])
        cell_schemas[key].add((r["dataset"], r["schema_id"]))
        cell_by_model[(r["dataset"], r["model"], r["size_category"], r["complexity_category"])].append(
            r["mean_structural_f1"]
        )

    heatmap_rows = []
    matrix = {s: {} for s in SIZE_ORDER}
    for size in SIZE_ORDER:
        for comp in COMPLEXITY_ORDER:
            key = (size, comp)
            vals = cells.get(key, [])
            n_schema = len(cell_schemas.get(key, set()))
            n_eval = len(vals)
            if n_eval == 0:
                mean_full = None
                std = None
                matrix[size][comp] = "NA"
                heatmap_rows.append({
                    "size_category": size,
                    "complexity_category": comp,
                    "schema_count": 0,
                    "evaluation_count": 0,
                    "mean_f1_full_precision": "NA",
                    "mean_f1_3dp": "NA",
                    "mean_f1_2dp": "NA",
                    "std_f1": "NA",
                })
            else:
                mean_full = sum(vals) / n_eval
                std = statistics.stdev(vals) if n_eval > 1 else 0.0
                matrix[size][comp] = mean_full
                heatmap_rows.append({
                    "size_category": size,
                    "complexity_category": comp,
                    "schema_count": n_schema,
                    "evaluation_count": n_eval,
                    "mean_f1_full_precision": f"{mean_full:.10f}",
                    "mean_f1_3dp": f"{mean_full:.3f}",
                    "mean_f1_2dp": f"{mean_full:.2f}",
                    "std_f1": f"{std:.10f}",
                })

    # Strata counts
    strata_rows = []
    for dataset, gold_map in [("RSchema", rschema_gold), ("SchemaBench", sb_gold)]:
        buckets = defaultdict(list)
        for g in gold_map.values():
            buckets[(g["size_category"], g["complexity_category"])].append(g)
        for size in SIZE_ORDER + ["INVALID"]:
            for comp in COMPLEXITY_ORDER + ["INVALID"]:
                gs = buckets.get((size, comp), [])
                if not gs and size == "INVALID":
                    continue
                if not gs:
                    continue
                strata_rows.append({
                    "dataset": dataset,
                    "size_category": size,
                    "complexity_category": comp,
                    "schema_count": len(gs),
                    "mean_gold_tables": sum(g["n_tab"] for g in gs) / len(gs),
                    "mean_gold_columns": sum(g["n_col"] for g in gs) / len(gs),
                    "mean_gold_fks": sum(g["f"] for g in gs) / len(gs),
                    "mean_constraint_score": sum(g["constraint_score"] for g in gs if not math.isnan(g["constraint_score"])) / len(gs),
                })

    # Per-model
    per_model_rows = []
    for (dataset, model, size, comp), vals in sorted(cell_by_model.items()):
        prompt = RSCHEMA_PROMPT if dataset == "RSchema" else SCHEMABENCH_PROMPT
        per_model_rows.append({
            "dataset": dataset,
            "model": model,
            "prompt_configuration": prompt,
            "size_category": size,
            "complexity_category": comp,
            "schema_count": len(vals),
            "mean_f1": sum(vals) / len(vals),
        })

    # Old vs new
    old_vs_new = []
    for size in SIZE_ORDER:
        for comp in COMPLEXITY_ORDER:
            hist = HISTORICAL_FIG5[(size, comp)]
            key = (size, comp)
            vals = cells.get(key, [])
            n_schema = len(cell_schemas.get(key, set()))
            if not vals:
                new_v = None
                change = "EMPTY_CELL_CHANGED" if hist is not None else "UNCHANGED"
                diff = None
            else:
                new_v = sum(vals) / len(vals)
                if hist is None:
                    change = "EMPTY_CELL_CHANGED"
                    diff = None
                else:
                    diff = new_v - hist
                    score_changed = abs(round(new_v, 2) - hist) > 0.005
                    # historical counts unknown except large=50 and large-medium empty
                    change = "SCORE_CHANGED" if score_changed else "UNCHANGED"
            old_vs_new.append({
                "size_category": size,
                "complexity_category": comp,
                "historical_mean_f1": "HISTORICAL_PAPER_VALUE" if hist is not None else "NA",
                "historical_mean_f1_numeric": hist if hist is not None else "NA",
                "recomputed_mean_f1": "NA" if new_v is None else f"{new_v:.10f}",
                "recomputed_mean_f1_2dp": "NA" if new_v is None else f"{new_v:.2f}",
                "recomputed_mean_f1_3dp": "NA" if new_v is None else f"{new_v:.3f}",
                "absolute_difference": "NA" if diff is None else f"{diff:.10f}",
                "recomputed_schema_count": n_schema,
                "historical_schema_count": "unknown" if not (size == "Large" and comp == "Medium") else 0,
                "change_class": change,
                "constructors_included": len(OPEN_MODELS),
                "constructors_expected": 5,
            })

    # Large tier schema count
    all_gold = list(rschema_gold.values()) + list(sb_gold.values())
    large_n = sum(1 for g in all_gold if g["size_category"] == "Large")
    large_medium_n = sum(1 for g in all_gold if g["size_category"] == "Large" and g["complexity_category"] == "Medium")

    # ----- Write CSV/JSON/MD -----
    def write_csv(path: Path, rows: list[dict], fieldnames: list[str]):
        with path.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            w.writeheader()
            for r in rows:
                w.writerow(r)

    # FILE 1
    f1_fields = [
        "dataset", "schema_id", "model", "prompt_configuration",
        "gold_table_count", "gold_column_count", "gold_fk_count", "gold_composite_fk_count",
        "gold_unique_count", "constraint_score", "size_category", "complexity_category",
        "gold_parse_status", "prediction_parse_status",
        "table_precision", "table_recall", "table_f1",
        "attribute_precision", "attribute_recall", "attribute_f1",
        "domain_precision", "domain_recall", "domain_f1",
        "entity_precision", "entity_recall", "entity_f1",
        "referential_precision", "referential_recall", "referential_f1",
        "mean_structural_f1",
    ]
    write_csv(OUT / "fig5_per_schema_results.csv", per_schema_rows, f1_fields)

    # FILE 2
    write_csv(
        OUT / "fig5_heatmap_values.csv",
        heatmap_rows,
        [
            "size_category", "complexity_category", "schema_count", "evaluation_count",
            "mean_f1_full_precision", "mean_f1_3dp", "mean_f1_2dp", "std_f1",
        ],
    )

    # FILE 3
    with (OUT / "fig5_heatmap_matrix.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["size_category", "Easy", "Medium", "Hard"])
        for size in SIZE_ORDER:
            row = [size]
            for comp in COMPLEXITY_ORDER:
                v = matrix[size][comp]
                row.append("NA" if v == "NA" or v is None else f"{v:.10f}")
            w.writerow(row)

    # FILE 4
    write_csv(
        OUT / "fig5_strata_counts.csv",
        strata_rows,
        [
            "dataset", "size_category", "complexity_category", "schema_count",
            "mean_gold_tables", "mean_gold_columns", "mean_gold_fks", "mean_constraint_score",
        ],
    )

    # FILE 5
    write_csv(
        OUT / "fig5_per_model.csv",
        per_model_rows,
        [
            "dataset", "model", "prompt_configuration", "size_category",
            "complexity_category", "schema_count", "mean_f1",
        ],
    )

    # FILE 6
    write_csv(
        OUT / "fig5_old_vs_new.csv",
        old_vs_new,
        list(old_vs_new[0].keys()) if old_vs_new else [],
    )

    # Analysis for small-easy
    def cell_mean(size, comp):
        vals = cells.get((size, comp), [])
        return (sum(vals) / len(vals)) if vals else None

    se, sm, sh = cell_mean("Small", "Easy"), cell_mean("Small", "Medium"), cell_mean("Small", "Hard")
    me, mm, mh = cell_mean("Medium", "Easy"), cell_mean("Medium", "Medium"), cell_mean("Medium", "Hard")
    le, lm, lh = cell_mean("Large", "Easy"), cell_mean("Large", "Medium"), cell_mean("Large", "Hard")

    # FILE 7 validation report
    n_unique = len(rschema_gold) + len(sb_gold)
    n_evals = len(per_schema_rows)
    report = []
    report.append("# Figure 5 Corrected E0 — Validation Report\n")
    report.append(f"Generated: {timestamp}\n")
    report.append(f"## Validation status: **{validation['status']}**\n")
    report.append("### 1. Source files\n")
    report.append(f"- RSchema gold: `{RSCHEMA_GOLD}` ({len(rschema_gold)} schemata)\n")
    report.append(f"- SchemaBench gold: `{SCHEMABENCH_GOLD}` ({len(sb_gold)} schemata)\n")
    report.append("- RSchema predictions (Exp4 text2schema from gold NL):\n")
    for m, p in RSCHEMA_PRED.items():
        report.append(f"  - {m}: `{p}`\n")
    report.append(f"- SchemaBench predictions: `{SCHEMABENCH_PAPER_ROOT}/<model>/few_shot/results.json`\n")
    report.append("### 2. Parser\n")
    for p in PARSER_PATHS:
        report.append(f"- `{p}`\n")
    report.append("Corrections: IF NOT EXISTS, no ENGINE, inline PK/UNIQUE, quoted names with spaces.\n")
    report.append("### 3. Evaluation code\n")
    for p in EVAL_PATHS:
        report.append(f"- `{p}`\n")
    report.append("### 4. Run configuration\n")
    report.append("| Dataset | Model | Prompt |\n|---|---|---|\n")
    for m in OPEN_MODELS:
        report.append(f"| RSchema | {m} | `{RSCHEMA_PROMPT}` |\n")
        report.append(f"| SchemaBench | {m} | `{SCHEMABENCH_PROMPT}` |\n")
    for m in PROPRIETARY_MODELS:
        report.append(f"| RSchema / SchemaBench | {m} | **MISSING local predictions** |\n")
    report.append("\n### 5. Table VII validation\n")
    report.append("```json\n" + json.dumps(validation, indent=2, default=str) + "\n```\n")
    report.append(f"### 6–9. Counts\n")
    report.append(f"- Unique gold schemata: {n_unique} (expected 757)\n")
    report.append(f"- Model–schema evaluations present: {n_evals} (expected 3785 for 5 models)\n")
    report.append(f"- Open-weight constructors: {len(OPEN_MODELS)}\n")
    report.append(f"- Prediction failures / zeros counted: {pred_failures}\n")
    report.append(f"- Gold parse failures: {gold_parse_failures}\n")
    report.append("### 10. Size × complexity distribution (unique gold)\n")
    report.append("| Size | Easy | Medium | Hard |\n|---|---:|---:|---:|\n")
    for size in SIZE_ORDER:
        row = [size]
        for comp in COMPLEXITY_ORDER:
            n = sum(1 for g in all_gold if g["size_category"] == size and g["complexity_category"] == comp)
            row.append(str(n))
        report.append("| " + " | ".join(row) + " |\n")
    report.append(f"\nLarge tier total: **{large_n}** (historical caption: 50)\n")
    report.append(f"Large–Medium cell schemata: **{large_medium_n}** (historical: empty)\n")
    report.append("### 11. Heatmap (mean structural F1, 3 open-weight models)\n")
    report.append("| Size | Easy | Medium | Hard |\n|---|---:|---:|---:|\n")
    for size in SIZE_ORDER:
        row = [size]
        for comp in COMPLEXITY_ORDER:
            v = matrix[size][comp]
            row.append("NA" if v == "NA" else f"{v:.3f}")
        report.append("| " + " | ".join(row) + " |\n")
    report.append("\n### 12. Unresolved inconsistencies\n")
    for n in validation["notes"]:
        report.append(f"- {n}\n")
    report.append(
        "\n**NOT READY FOR PAPER as a 5-constructor Figure 5** until Claude Sonnet 4.6 "
        "and GPT-5.4-mini per-schema E0 predictions are available locally.\n"
    )
    (OUT / "fig5_validation_report.md").write_text("".join(report), encoding="utf-8")

    # FILE 8 paper updates
    paper = []
    paper.append("# Figure 5 — Exact manuscript update notes\n\n")
    paper.append("## Status\n")
    paper.append(
        "**NOT READY to replace the published 5-constructor Figure 5.** "
        "Verified numbers below use only the three open-weight constructors "
        "with local predictions. Proprietary per-schema outputs are missing.\n\n"
    )
    paper.append("## A. Corrected Figure 5 matrix (3 open-weight models; mean structural F1)\n\n")
    paper.append("| | Easy | Medium | Hard |\n|---|---:|---:|---:|\n")
    for size in SIZE_ORDER:
        row = [size]
        for comp in COMPLEXITY_ORDER:
            v = matrix[size][comp]
            row.append("NA" if v == "NA" else f"{v:.2f}")
        paper.append("| " + " | ".join(row) + " |\n")
    paper.append("\n## B. Schema counts per cell (unique gold)\n\n")
    paper.append("| | Easy | Medium | Hard |\n|---|---:|---:|---:|\n")
    for size in SIZE_ORDER:
        row = [size]
        for comp in COMPLEXITY_ORDER:
            n = sum(1 for g in all_gold if g["size_category"] == size and g["complexity_category"] == comp)
            row.append(str(n))
        paper.append("| " + " | ".join(row) + " |\n")
    paper.append(f"\n## C. Large–Medium empty? **{'YES' if large_medium_n == 0 else 'NO'}** (n={large_medium_n})\n")
    paper.append(f"\n## D. Large-schema group size: **{large_n}** (historical caption said 50)\n")
    large_max = max([x for x in (le, lh) if x is not None], default=None)
    paper.append(
        f"\n## E. “Large schemata score at most 0.15”? "
        f"**{'YES' if large_max is not None and large_max <= 0.15 + 1e-9 else 'CHECK'}** "
        f"(Large-Easy={None if le is None else f'{le:.3f}'}, "
        f"Large-Hard={None if lh is None else f'{lh:.3f}'}; Large-Medium={'NA' if lm is None else f'{lm:.3f}'})\n"
    )
    paper.append("\n## F. Small-Easy vs Small-Medium vs Small-Hard\n")
    paper.append(
        f"- Small-Easy={None if se is None else f'{se:.3f}'}, "
        f"Small-Medium={None if sm is None else f'{sm:.3f}'}, "
        f"Small-Hard={None if sh is None else f'{sh:.3f}'}\n"
    )
    if se is not None and sm is not None and sh is not None:
        paper.append(
            f"- Small-Easy still lower than Medium/Hard? **{se < sm and se < sh}**\n"
        )
    paper.append(
        f"- Medium-Easy={None if me is None else f'{me:.3f}'}, "
        f"Medium-Medium={None if mm is None else f'{mm:.3f}'}, "
        f"Medium-Hard={None if mh is None else f'{mh:.3f}'}\n"
    )
    paper.append("\n## G–I. Suggested caption / wording\n")
    paper.append(
        "Suggested caption (once 5 constructors are complete):\n\n"
        "```\n"
        "Figure 5. E0 mean structural $F_1$ by schema size (rows) and constraint "
        "complexity (columns), averaged over constructors. Size uses gold table/column "
        "thresholds; complexity uses the paper score $s$. Empty cells marked NA.\n"
        "```\n\n"
        "Do **not** update the caption to claim five constructors until Claude/GPT "
        "per-schema files are integrated.\n"
    )
    paper.append("\n## J. Figure 5 vs Table VII\n")
    paper.append(
        "Table VII reports overall micro/macro metrics per model; Figure 5 reports "
        "mean of per-schema mean of five dimensional $F_1$s within size×complexity "
        "cells. These are different aggregations and need not match numerically.\n"
    )
    (OUT / "fig5_paper_updates.md").write_text("".join(paper), encoding="utf-8")

    # FILE 9 manifest
    manifest = {
        "timestamp": timestamp,
        "git_commit": None,
        "datasets": {
            "RSchema": {"gold": str(RSCHEMA_GOLD), "n": len(rschema_gold)},
            "SchemaBench": {"gold": str(SCHEMABENCH_GOLD), "n": len(sb_gold)},
        },
        "predictions": {
            "RSchema": {m: str(p) for m, p in RSCHEMA_PRED.items()},
            "SchemaBench": {
                m: str(SCHEMABENCH_PAPER_ROOT / d / "few_shot" / "results.json")
                for m, d in SCHEMABENCH_MODEL_DIR.items()
            },
            "missing_models": PROPRIETARY_MODELS,
        },
        "prompt_configurations": {
            "RSchema_open_weight": RSCHEMA_PROMPT,
            "SchemaBench_open_weight": SCHEMABENCH_PROMPT,
            "proprietary": "unknown_missing_local_files",
        },
        "parser_sources": PARSER_PATHS,
        "evaluation_sources": EVAL_PATHS,
        "figure5_aggregation": {
            "per_schema": "mean of five dimensional F1 scores",
            "per_cell": "mean over schema–model pairs in the cell (equal weight)",
            "constructors_used": OPEN_MODELS,
            "constructors_expected_by_paper": OPEN_MODELS + PROPRIETARY_MODELS,
        },
        "counts": {
            "unique_gold": n_unique,
            "evaluations": n_evals,
            "pred_failures_or_zeros": pred_failures,
            "gold_parse_failures": gold_parse_failures,
            "large_schema_count": large_n,
            "large_medium_count": large_medium_n,
        },
        "validation_status": validation["status"],
        "validation": validation,
        "heatmap_3dp": {
            size: {
                comp: ("NA" if matrix[size][comp] == "NA" else round3(matrix[size][comp]))
                for comp in COMPLEXITY_ORDER
            }
            for size in SIZE_ORDER
        },
        "small_easy_analysis": {
            "small_easy": se,
            "small_medium": sm,
            "small_hard": sh,
            "medium_easy": me,
            "medium_medium": mm,
            "medium_hard": mh,
            "large_easy": le,
            "large_medium": lm,
            "large_hard": lh,
        },
    }
    (OUT / "fig5_run_manifest.json").write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")

    # Print summary for operator
    print("\n========== FINAL SUMMARY ==========")
    print("Validation:", validation["status"])
    print("Unique gold:", n_unique, "evaluations:", n_evals)
    print("Heatmap 3dp (3 open-weight models):")
    print(f"{'':8} {'Easy':>8} {'Medium':>8} {'Hard':>8}")
    for size in SIZE_ORDER:
        vals = []
        for comp in COMPLEXITY_ORDER:
            v = matrix[size][comp]
            vals.append("     NA" if v == "NA" else f"{v:8.3f}")
            n = len(cell_schemas.get((size, comp), set()))
        print(f"{size:8} " + " ".join(vals))
    print("Schema counts:")
    for size in SIZE_ORDER:
        ns = []
        for comp in COMPLEXITY_ORDER:
            ns.append(f"{len(cell_schemas.get((size,comp), set())):8d}")
        print(f"{size:8} " + " ".join(ns))
    print("Large n:", large_n, "Large-Medium n:", large_medium_n)
    print("Small Easy/Med/Hard F1:", se, sm, sh)
    print("Outputs:", OUT)
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
