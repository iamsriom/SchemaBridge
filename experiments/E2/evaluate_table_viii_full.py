#!/usr/bin/env python3
"""
Independent offline evaluator for ICDE 2027 Table VIII (E2 Round-Trip / Text2Schema).

Pipeline: Gold Schema -> E1 Schema2Text NL -> GPT-4o-mini -> reconstructed DDL.

Populations:
  Enterprise-145 : 145 (Text2ER/schema)
  SchemaBench    : 239 (annotation_ddl.jsonl)
  RSchema PRIMARY: 381 genuine DDL (annotation_ddl.jsonl)
  RSchema HIST   : 518 synthetic metadata from annotation.jsonl (paper source)

Failure convention (paper-declared, PRIMARY):
  missing/empty/unparseable -> gold counts with matched=0, recreated=0; nGED=1.0

Micro-F1 aggregates matched/predicted/gold before P/R/F1.
nGED: symmetric diff of tables + (col,type_family,null) + directed FKs;
      denom = max(g_size + p_size, 1); mean over population.

No API calls. Read-only on prediction corpora.
"""
from __future__ import annotations

import os
os.environ.setdefault("PYTHONHASHSEED", "0")

import csv
import hashlib
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENDOR = ROOT / "vendor"
# Locked vendor-only imports for deterministic PRIMARY evaluation.
sys.path.insert(0, str(VENDOR))

import evaluate_text2schema2 as ev  # noqa: E402
from evaluate_exp4_text2schema import (  # noqa: E402
    agg_element,
    ensure_prediction_metadata,
    metadata_from_ddl,
    normalized_graph_edit_distance,
)
from evaluate_rschema_predictions import (  # noqa: E402
    gold_answer_to_metadata_and_ddl,
    load_jsonl,
    normalize_rschema_name,
)

# Sanity: SchemaBench gold uses FOREIGN KEY(col) without space; parser must allow \s*.
assert r"KEY\s*\(" in Path(ev.__file__).read_text(), ev.__file__

DATA = Path("/data")
OUT = Path("/data/SchemaBridge/results/metrics/reproduced/E2_AUDIT")
MODELS = [
    ("codellama13b", "CodeLlama-13B"),
    ("llama31", "Llama-3.1-8B"),
    ("deepseek", "DeepSeek-Coder"),
    ("sonnet46", "Claude Sonnet 4.6"),
    ("gpt54mini", "GPT-5.4-mini"),
]
METRICS = ["nged", "tables", "attributes", "domain", "entity", "referential"]
PAPER_MODEL_MAP = {
    "codellama13b": "codellama13b",
    "llama31": "llama31",
    "deepseek": "deepseek",
    "claude_sonnet_4_6": "sonnet46",
    "gpt_5_4_mini": "gpt54mini",
}


def load_paper_table() -> dict:
    p = OUT / "from_schemabridge" / "paper_reference_values.json"
    if not p.exists():
        alt = Path(
            "/home/ubuntu/recovery_audits/E1_TABLE_VII_FULL_RECOVERY/"
            "from_schemabridge/paper_reference_values.json"
        )
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(alt.read_text())
    return json.loads(p.read_text())["tab:e2_roundtrip"]["datasets"]


def load_rschema_381() -> dict:
    manifest = OUT / "manifests" / "RSCHEMA_381_ELIGIBLE.csv"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    if not manifest.exists():
        src = OUT / "RSCHEMA_381_ELIGIBLE.csv"
        if src.exists():
            manifest.write_text(src.read_text())
        else:
            e1 = Path(
                "/home/ubuntu/recovery_audits/E1_TABLE_VII_FULL_RECOVERY/"
                "manifests/RSCHEMA_381_ELIGIBLE.csv"
            )
            manifest.write_text(e1.read_text())
    out = {}
    with manifest.open() as f:
        for row in csv.DictReader(f):
            out[row["schema_id"]] = row["serial_in_518"]
    return out


def score_pair(label, gold_meta, gold_ddl, pred_meta, pred_ddl, table_count, column_count):
    m = ev.evaluate_one(
        label, gold_meta, gold_ddl, pred_meta, pred_ddl, table_count, column_count
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
    nged = normalized_graph_edit_distance(gold_meta, gold_ddl, pred_meta, pred_ddl)
    return per, nged


def gold_counts_only(gold_meta, gold_ddl, table_count, column_count):
    empty_meta = {"database": "", "tables": [], "columns_by_table": {}}
    per, _ = score_pair(
        "FAIL", gold_meta, gold_ddl, empty_meta, "", table_count, column_count
    )
    for k in per:
        per[k]["recreated"] = 0
        per[k]["matched"] = 0
    return per, 1.0


def parse_pred(pred_path: Path):
    data = json.loads(pred_path.read_text(encoding="utf-8"))
    ddl = (data.get("ddl") or "").strip()
    err = data.get("error") or data.get("skipped")
    # Historical Enterprise fallback: if JSON ddl missing/errored, try sibling .txt
    if (err or not ddl or str(ddl).startswith("ERROR:")):
        txt_path = pred_path.with_suffix(".txt")
        if txt_path.is_file():
            txt = txt_path.read_text(encoding="utf-8", errors="replace")
            if txt.strip() and not txt.strip().startswith("ERROR:"):
                ddl = txt.strip()
                err = None
    meta = ensure_prediction_metadata(
        data.get("metadata") or {}, ddl, database=data.get("database") or ""
    )
    tables = meta.get("tables") or []
    cbt = meta.get("columns_by_table") or {}
    n_cols = sum(len(v or []) for v in cbt.values())
    ok = (not err) and bool(ddl) and (
        len(tables) > 0 or n_cols > 0 or "CREATE TABLE" in ddl.upper()
    )
    if ddl and not tables and n_cols == 0 and "CREATE TABLE" not in ddl.upper():
        ok = False
    return data, ddl, meta, ok, err


def enterprise_normalize_name(s: str) -> str:
    return (s or "").strip().lower()


def enterprise_gold_index():
    schema_dir = DATA / "Text2ER" / "schema"
    index = json.loads((schema_dir / "index.json").read_text())
    gold = {}
    for ds in index.get("datasets", []):
        name = ds.get("safe_name")
        if not name:
            continue
        meta_path = schema_dir / f"{name}.metadata.json"
        ddl_path = schema_dir / f"{name}.sql"
        ddl = ddl_path.read_text(encoding="utf-8", errors="replace")
        meta = json.loads(meta_path.read_text())
        gold[name] = {
            "safe_name": name,
            "meta": meta,
            "ddl": ddl,
            "table_count": ds.get("table_count") or 0,
            "column_count": ds.get("column_count") or 0,
            "database": ds.get("database") or name,
        }
    assert len(gold) == 145, len(gold)
    return gold


def schemabench_gold():
    path = DATA / "SchemaBench" / "Dataset" / "annotation_ddl.jsonl"
    if not path.exists():
        path = DATA / "Text2ER" / "SchemaBench" / "Dataset" / "annotation_ddl.jsonl"
    records = load_jsonl(path)
    gold = {}
    for i, r in enumerate(records, 1):
        rid = r.get("id") or f"SB-{i:03d}"
        ddl = (r.get("answer") or "").strip() if isinstance(r.get("answer"), str) else ""
        db = r.get("database") or f"schemabench_{i:04d}"
        meta = metadata_from_ddl(ddl, database=db)
        tables, cols, _ = ev.extract_schema_from_metadata(meta)
        gold[rid] = {
            "serial": f"{i:04d}",
            "meta": meta,
            "ddl": ddl,
            "table_count": len(tables),
            "column_count": sum(len(v) for v in cols.values()),
            "database": db,
        }
    assert len(gold) == 239, len(gold)
    return gold


def rschema_gold_synthetic():
    ann = load_jsonl(DATA / "RSchema" / "annotation.jsonl")
    gold = {}
    for i, r in enumerate(ann, 1):
        rid = r["id"]
        answer = r.get("answer") or {}
        db = r.get("database") or f"rschema_{i:04d}"
        meta, ddl = gold_answer_to_metadata_and_ddl(answer, database=db)
        tables, cols, _ = ev.extract_schema_from_metadata(meta)
        gold[rid] = {
            "serial": f"{i:04d}",
            "meta": meta,
            "ddl": ddl,
            "table_count": len(tables),
            "column_count": sum(len(v) for v in cols.values()),
            "mode": "synthetic_annotation",
        }
    assert len(gold) == 518, len(gold)
    return gold


def rschema_gold_genuine(eligible: dict):
    ddl_recs = {r["id"]: r for r in load_jsonl(DATA / "RSchema" / "annotation_ddl.jsonl")}
    gold = {}
    for rid, serial in eligible.items():
        r = ddl_recs[rid]
        answer = r.get("answer")
        db = r.get("database") or f"rschema_{serial}"
        if isinstance(answer, str) and answer.strip():
            ddl = answer.strip()
            meta = metadata_from_ddl(ddl, database=db)
        else:
            meta, ddl = gold_answer_to_metadata_and_ddl(answer or {}, database=db)
        tables, cols, _ = ev.extract_schema_from_metadata(meta)
        gold[rid] = {
            "serial": serial,
            "meta": meta,
            "ddl": ddl,
            "table_count": len(tables),
            "column_count": sum(len(v) for v in cols.values()),
            "mode": "genuine_ddl",
        }
    assert len(gold) == 381, len(gold)
    return gold


def _run_generic(pred_dir, nl_dir, gold, fail_policy, id_mode, dataset, prompt, model, population_label):
    """id_mode: 'name' for enterprise safe_name keys; 'id_serial' for rschema/sb."""
    items, ngeds, failures = [], [], []
    nl_match = nl_mismatch = 0
    n_pred = len(list(pred_dir.glob("*.json"))) if pred_dir.is_dir() else 0
    inventory = {
        "pred_dir": str(pred_dir),
        "nl_dir": str(nl_dir),
        "n_pred_json": n_pred,
        "population_label": population_label,
    }

    pred_by_id, pred_by_serial, pred_by_name = {}, {}, {}
    if pred_dir.is_dir():
        for pj in pred_dir.glob("*.json"):
            try:
                d = json.loads(pj.read_text())
            except Exception:
                continue
            pred_by_serial[pj.stem] = pj
            pred_by_name[pj.stem] = pj
            if d.get("id"):
                pred_by_id[d["id"]] = pj
            sn = d.get("safe_name") or d.get("database")
            if sn:
                pred_by_name[sn] = pj

    for rid, g in gold.items():
        if id_mode == "name":
            pred_path = pred_by_name.get(rid) or (pred_dir / f"{rid}.json")
            if not pred_path.exists():
                pred_path = None
        else:
            pred_path = pred_by_id.get(rid) or pred_by_serial.get(g["serial"])

        if pred_path is None:
            per, nged = gold_counts_only(
                g["meta"], g["ddl"], g["table_count"], g["column_count"]
            )
            if fail_policy == "skip":
                failures.append({"id": rid, "reason": "missing_file", "included": False})
                continue
            items.append(per)
            ngeds.append(nged)
            failures.append({"id": rid, "reason": "missing_file", "included": True})
            continue

        try:
            data, ddl, meta, ok, err = parse_pred(pred_path)
        except Exception as e:
            per, nged = gold_counts_only(
                g["meta"], g["ddl"], g["table_count"], g["column_count"]
            )
            if fail_policy == "skip":
                failures.append({"id": rid, "reason": f"json_error:{e}", "included": False})
                continue
            items.append(per)
            ngeds.append(nged)
            failures.append({"id": rid, "reason": f"json_error:{e}", "included": True})
            continue

        nl = (data.get("nl_text") or "").strip()
        nl_file = nl_dir / f"{pred_path.stem}.txt"
        if not nl_file.exists() and id_mode == "name":
            nl_file = nl_dir / f"{rid}.txt"
        if nl_file.exists():
            src = nl_file.read_text(encoding="utf-8", errors="replace").strip()
            if src == nl:
                nl_match += 1
            else:
                nl_mismatch += 1

        if not ok:
            per, nged = gold_counts_only(
                g["meta"], g["ddl"], g["table_count"], g["column_count"]
            )
            if fail_policy == "skip":
                failures.append(
                    {"id": rid, "reason": f"invalid:{err or 'empty'}", "included": False}
                )
                continue
            items.append(per)
            ngeds.append(nged)
            failures.append(
                {"id": rid, "reason": f"invalid:{err or 'empty'}", "included": True}
            )
            continue

        per, nged = score_pair(
            str(rid), g["meta"], g["ddl"], meta, ddl, g["table_count"], g["column_count"]
        )
        items.append(per)
        ngeds.append(nged)

    five = {
        k: agg_element(items, k)
        for k in ["tables", "attributes", "domain", "entity", "referential"]
    }
    mean_nged = sum(ngeds) / len(ngeds) if ngeds else 1.0
    return {
        "dataset": dataset,
        "prompt": prompt,
        "model": model,
        "population": len(gold),
        "evaluated_n": len(items),
        "population_label": population_label,
        "failure_count": sum(1 for f in failures if f.get("included")),
        "skipped_count": sum(1 for f in failures if not f.get("included")),
        "mean_nged": mean_nged,
        "five_elements": five,
        "nl_match_checked": nl_match,
        "nl_mismatch": nl_mismatch,
        "inventory": inventory,
        "failures": failures,
        "fail_policy": fail_policy,
        "constructor": "gpt-4o-mini",
    }


def run_enterprise(prompt, model, gold, fail_policy):
    # E2 cross-dataset / Exp1 round-trip scorers pin RSchema-style normalization.
    # (Exp2 Detailed historically used strip().lower(); we standardize on the
    # RSchema-style rule used for Exp1 Basic, SchemaBench, and RSchema.)
    ev.normalize_name = normalize_rschema_name
    if prompt == "basic":
        pred_dir = DATA / "LLMTranslations" / "Exp1" / f"Text2Schema1_{model}"
        nl_dir = DATA / "LLMTranslations" / "Exp1" / f"Schema2Text1_{model}"
    else:
        pred_dir = DATA / "LLMTranslations" / "Exp2" / f"Text2Schema2_{model}"
        nl_dir = DATA / "LLMTranslations" / "Exp2" / f"Schema2Text2_{model}"
    return _run_generic(
        pred_dir,
        nl_dir,
        gold,
        fail_policy,
        "name",
        "Enterprise-145",
        prompt,
        model,
        "enterprise_145",
    )


def run_schemabench(prompt, model, gold, fail_policy):
    ev.normalize_name = normalize_rschema_name
    if prompt == "basic":
        pred_dir = DATA / "SchemaBench" / "Exp1" / f"text2schema_gpt4omini_schema2text_{model}"
        nl_dir = DATA / "SchemaBench" / "Exp1" / f"schema2text_{model}"
    else:
        pred_dir = (
            DATA
            / "Text2ER"
            / "SchemaBench"
            / "Experiment"
            / f"text2schema_gpt4omini_schema2text_{model}"
        )
        nl_dir = DATA / "Text2ER" / "SchemaBench" / "Experiment" / f"schema2text_{model}"
        if not pred_dir.is_dir():
            pred_dir = (
                DATA
                / "SchemaBench"
                / "Experiment"
                / f"text2schema_gpt4omini_schema2text_{model}"
            )
            nl_dir = DATA / "SchemaBench" / "Experiment" / f"schema2text_{model}"
    return _run_generic(
        pred_dir,
        nl_dir,
        gold,
        fail_policy,
        "id_serial",
        "SchemaBench",
        prompt,
        model,
        "schemabench_239",
    )


def run_rschema(prompt, model, gold, fail_policy, population_label):
    ev.normalize_name = normalize_rschema_name
    if prompt == "basic":
        pred_dir = (
            DATA
            / "RSchema_ExpResults4"
            / "Exp1"
            / f"text2schema_gpt4omini_schema2text_{model}"
        )
        nl_dir = DATA / "RSchema_ExpResults4" / "Exp1" / f"schema2text_{model}"
    else:
        pred_dir = (
            DATA
            / "RSchema_ExpResults4"
            / "Experiment2"
            / f"text2schema_gpt4omini_schema2text_{model}"
        )
        nl_dir = DATA / "RSchema_ExpResults4" / "Experiment2" / f"schema2text_{model}"
    return _run_generic(
        pred_dir,
        nl_dir,
        gold,
        fail_policy,
        "id_serial",
        "RSchema",
        prompt,
        model,
        population_label,
    )


def r3(x: float) -> float:
    return round(float(x) + 1e-12, 3)


def status_for(orig, recomputed):
    if orig is None:
        return "MISSING"
    if r3(orig) == r3(recomputed):
        return "VERIFIED"
    return "CORRECTED"


def pack(res_list):
    out = []
    for r in res_list:
        row = {
            "dataset": r["dataset"],
            "prompt": r["prompt"],
            "model": r["model"],
            "population": r["population"],
            "evaluated_n": r["evaluated_n"],
            "population_label": r.get("population_label") or r["dataset"],
            "fail_policy": r["fail_policy"],
            "failure_count": r["failure_count"],
            "skipped_count": r["skipped_count"],
            "mean_nged": r["mean_nged"],
            "nl_match_checked": r["nl_match_checked"],
            "nl_mismatch": r["nl_mismatch"],
            "inventory": r["inventory"],
        }
        for k, v in r["five_elements"].items():
            row[f"{k}_f1"] = v["f1"]
            row[f"{k}_precision"] = v["precision"]
            row[f"{k}_recall"] = v["recall"]
            row[f"{k}_gold"] = v["gold"]
            row[f"{k}_recreated"] = v["recreated"]
            row[f"{k}_matched"] = v["matched"]
        out.append(row)
    return out


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=None, help="Override output root (default: E2_AUDIT)")
    args = ap.parse_args(argv)
    global OUT
    if args.out is not None:
        OUT = args.out
    print("Loading gold indices...", flush=True)
    ent_gold = enterprise_gold_index()
    sb_gold = schemabench_gold()
    eligible = load_rschema_381()
    rs_syn = rschema_gold_synthetic()
    rs_gen = rschema_gold_genuine(eligible)
    paper = load_paper_table()

    results_primary = []
    results_hist = []

    for prompt in ("basic", "detailed"):
        for model, _disp in MODELS:
            print(f"Enterprise {prompt} {model}...", flush=True)
            results_primary.append(
                run_enterprise(prompt, model, ent_gold, fail_policy="score")
            )
            results_hist.append(
                run_enterprise(prompt, model, ent_gold, fail_policy="skip")
            )

            print(f"SchemaBench {prompt} {model}...", flush=True)
            results_primary.append(
                run_schemabench(prompt, model, sb_gold, fail_policy="score")
            )
            results_hist.append(
                run_schemabench(prompt, model, sb_gold, fail_policy="skip")
            )

            print(f"RSchema genuine {prompt} {model}...", flush=True)
            results_primary.append(
                run_rschema(
                    prompt,
                    model,
                    rs_gen,
                    fail_policy="score",
                    population_label="genuine_ddl_381",
                )
            )

            print(f"RSchema synthetic {prompt} {model}...", flush=True)
            results_hist.append(
                run_rschema(
                    prompt,
                    model,
                    rs_syn,
                    fail_policy="skip",
                    population_label="synthetic_518",
                )
            )

    (OUT / "metrics").mkdir(parents=True, exist_ok=True)
    (OUT / "failures").mkdir(parents=True, exist_ok=True)
    (OUT / "inventory").mkdir(parents=True, exist_ok=True)

    (OUT / "metrics" / "full_precision_primary.json").write_text(
        json.dumps(pack(results_primary), indent=2)
    )
    (OUT / "metrics" / "full_precision_historical_replication.json").write_text(
        json.dumps(pack(results_hist), indent=2)
    )

    prim = {(r["dataset"], r["prompt"], r["model"]): r for r in results_primary}
    hist = {(r["dataset"], r["prompt"], r["model"]): r for r in results_hist}

    matrix_rows = []
    for ds in ("Enterprise-145", "RSchema", "SchemaBench"):
        paper_ds = paper[ds]
        for pkey, model in PAPER_MODEL_MAP.items():
            disp = paper_ds[pkey]["display_name"]
            for prompt, pfx in (("basic", "basic"), ("detailed", "detailed")):
                rr = prim[(ds, prompt, model)]
                hr = hist[(ds, prompt, model)]
                for metric in METRICS:
                    col = f"{metric}_{pfx}"
                    orig = paper_ds[pkey][col]
                    if metric == "nged":
                        recomputed = rr["mean_nged"]
                        hist_val = hr["mean_nged"]
                    else:
                        recomputed = rr["five_elements"][metric]["f1"]
                        hist_val = hr["five_elements"][metric]["f1"]
                    st = status_for(orig, recomputed)
                    evidence = rr.get("population_label") or f"N={rr['evaluated_n']}"
                    if ds == "RSchema" and r3(orig) == r3(hist_val) and st == "CORRECTED":
                        evidence += "; paper≈historical_synthetic_518_skip_failures"
                    matrix_rows.append(
                        {
                            "Dataset": ds,
                            "Describer": disp,
                            "Prompt": prompt.capitalize(),
                            "Metric": metric,
                            "Original": orig,
                            "Recomputed": r3(recomputed),
                            "Recomputed_full": recomputed,
                            "Historical_replication": r3(hist_val),
                            "Evaluated_N": rr["evaluated_n"],
                            "Population_label": rr.get("population_label") or ds,
                            "Failures_scored": rr["failure_count"],
                            "Status": st,
                            "Evidence": evidence,
                        }
                    )

    with (OUT / "metrics" / "VERIFICATION_MATRIX.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(matrix_rows[0].keys()))
        w.writeheader()
        w.writerows(matrix_rows)

    with (OUT / "metrics" / "FULL_PRECISION_METRICS.csv").open("w", newline="") as f:
        fields = [
            "dataset",
            "prompt",
            "model",
            "population",
            "evaluated_n",
            "population_label",
            "fail_policy",
            "failure_count",
            "mean_nged",
            "tables_f1",
            "attributes_f1",
            "domain_f1",
            "entity_f1",
            "referential_f1",
            "nl_match_checked",
            "nl_mismatch",
        ]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in results_primary:
            w.writerow(
                {
                    "dataset": r["dataset"],
                    "prompt": r["prompt"],
                    "model": r["model"],
                    "population": r["population"],
                    "evaluated_n": r["evaluated_n"],
                    "population_label": r.get("population_label") or r["dataset"],
                    "fail_policy": r["fail_policy"],
                    "failure_count": r["failure_count"],
                    "mean_nged": r["mean_nged"],
                    "tables_f1": r["five_elements"]["tables"]["f1"],
                    "attributes_f1": r["five_elements"]["attributes"]["f1"],
                    "domain_f1": r["five_elements"]["domain"]["f1"],
                    "entity_f1": r["five_elements"]["entity"]["f1"],
                    "referential_f1": r["five_elements"]["referential"]["f1"],
                    "nl_match_checked": r["nl_match_checked"],
                    "nl_mismatch": r["nl_mismatch"],
                }
            )

    fail_rows = []
    for r in results_primary:
        reasons = defaultdict(int)
        for fr in r["failures"]:
            reasons[fr["reason"].split(":")[0]] += 1
        fail_rows.append(
            {
                "dataset": r["dataset"],
                "prompt": r["prompt"],
                "model": r["model"],
                "population": r["population"],
                "evaluated_n": r["evaluated_n"],
                "failures_scored": r["failure_count"],
                "skipped": r["skipped_count"],
                "failure_reasons": dict(reasons),
            }
        )
    (OUT / "failures" / "FAILURE_AUDIT.json").write_text(json.dumps(fail_rows, indent=2))

    inv = []
    for r in results_primary:
        inv.append(
            {
                "dataset": r["dataset"],
                "prompt": r["prompt"],
                "model": r["model"],
                **r["inventory"],
            }
        )
    (OUT / "inventory" / "PREDICTION_INVENTORY.json").write_text(json.dumps(inv, indent=2))

    verified = sum(1 for m in matrix_rows if m["Status"] == "VERIFIED")
    corrected = sum(1 for m in matrix_rows if m["Status"] == "CORRECTED")
    missing = sum(1 for m in matrix_rows if m["Status"] == "MISSING")
    summary = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "cells": 180,
        "verified": verified,
        "corrected": corrected,
        "missing": missing,
        "primary_population": {
            "Enterprise-145": 145,
            "RSchema": "381 genuine DDL (annotation_ddl.jsonl)",
            "SchemaBench": 239,
        },
        "historical_rschema_population": "518 synthetic from annotation.jsonl",
        "constructor": "gpt-4o-mini",
    }
    (OUT / "metrics" / "STATUS_COUNTS.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    print("DONE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main() or 0)
