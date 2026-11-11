#!/usr/bin/env python3
"""
E3 PRIMARY independent offline evaluator (ICDE 2027 tab:e3_overall).

Pipeline:
  Gold Schema
    -> frozen GPT-5.4-mini DETAILED Schema2Text description (E1 detailed)
    -> five constructors (CodeLlama-13B, Llama-3.1-8B, DeepSeek-Coder,
       Claude Sonnet 4.6, GPT-5.4-mini)
    -> predicted DDL
    -> structural metrics vs gold

Population (PRIMARY, same as E2):
  Enterprise-145 : 145
  RSchema        : 381 genuine DDL (annotation_ddl.jsonl ∩ RSCHEMA_381_ELIGIBLE)
  SchemaBench    : 239
  Total          : 765 schemata × 5 constructors = 3,825 evaluations

Uses the locked E2 vendor parsers (PYTHONHASHSEED=0, collision-safe maps,
normalize_rschema_name). No API calls. Read-only on prediction corpora.

Outputs under this directory only.
"""
from __future__ import annotations

import os

os.environ.setdefault("PYTHONHASHSEED", "0")

import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "metrics" / "reproduced" / "E3_AUDIT"
VENDOR = ROOT / "experiments" / "E2" / "vendor"
sys.path.insert(0, str(VENDOR))

import evaluate_text2schema2 as ev  # noqa: E402
from evaluate_exp4_text2schema import (  # noqa: E402
    agg_element,
    ensure_prediction_metadata,
    metadata_from_ddl,
    normalized_graph_edit_distance,
)
from evaluate_rschema_predictions import (  # noqa: E402
    load_jsonl,
    normalize_rschema_name,
)

DATA = Path(__import__("os").environ.get("SCHEMA_BRIDGE_DATA", "/data"))
HALL_DIMS = ("tables", "attributes", "entity", "referential")
ELEMENTS = ("tables", "attributes", "domain", "entity", "referential")
MODELS = [
    ("codellama13b", "CodeLlama-13B"),
    ("llama31", "Llama-3.1-8B"),
    ("deepseek", "DeepSeek-Coder"),
    ("sonnet46", "Claude Sonnet 4.6"),
    ("gpt54mini", "GPT-5.4-mini"),
]

# Manuscript values supplied in the audit brief (3-decimal).
PAPER = {
    ("Enterprise-145", "CodeLlama-13B"): {
        "nGED": 0.324, "Hall": 0.085, "T": 0.553, "A": 0.479, "D": 0.315, "E": 0.479, "R": 0.460
    },
    ("Enterprise-145", "Llama-3.1-8B"): {
        "nGED": 0.340, "Hall": 0.071, "T": 0.596, "A": 0.294, "D": 0.277, "E": 0.489, "R": 0.528
    },
    ("Enterprise-145", "DeepSeek-Coder"): {
        "nGED": 0.549, "Hall": 0.120, "T": 0.492, "A": 0.167, "D": 0.117, "E": 0.348, "R": 0.296
    },
    ("Enterprise-145", "Claude Sonnet 4.6"): {
        "nGED": 0.047, "Hall": 0.027, "T": 0.758, "A": 0.703, "D": 0.685, "E": 0.744, "R": 0.847
    },
    ("Enterprise-145", "GPT-5.4-mini"): {
        "nGED": 0.058, "Hall": 0.026, "T": 0.753, "A": 0.683, "D": 0.664, "E": 0.720, "R": 0.816
    },
    ("RSchema", "CodeLlama-13B"): {
        "nGED": 0.369, "Hall": 0.020, "T": 0.987, "A": 0.986, "D": 0.483, "E": 0.981, "R": 0.969
    },
    ("RSchema", "Llama-3.1-8B"): {
        "nGED": 0.493, "Hall": 0.020, "T": 0.989, "A": 0.986, "D": 0.343, "E": 0.976, "R": 0.970
    },
    ("RSchema", "DeepSeek-Coder"): {
        "nGED": 0.383, "Hall": 0.073, "T": 0.940, "A": 0.807, "D": 0.508, "E": 0.806, "R": 0.802
    },
    ("RSchema", "Claude Sonnet 4.6"): {
        "nGED": 0.468, "Hall": 0.009, "T": 0.994, "A": 0.991, "D": 0.351, "E": 0.995, "R": 0.994
    },
    ("RSchema", "GPT-5.4-mini"): {
        "nGED": 0.471, "Hall": 0.010, "T": 0.993, "A": 0.990, "D": 0.345, "E": 0.995, "R": 0.991
    },
    ("SchemaBench", "CodeLlama-13B"): {
        "nGED": 0.272, "Hall": 0.054, "T": 0.760, "A": 0.697, "D": 0.527, "E": 0.714, "R": 0.623
    },
    ("SchemaBench", "Llama-3.1-8B"): {
        "nGED": 0.369, "Hall": 0.058, "T": 0.806, "A": 0.491, "D": 0.370, "E": 0.711, "R": 0.672
    },
    ("SchemaBench", "DeepSeek-Coder"): {
        "nGED": 0.550, "Hall": 0.096, "T": 0.649, "A": 0.251, "D": 0.184, "E": 0.523, "R": 0.423
    },
    ("SchemaBench", "Claude Sonnet 4.6"): {
        "nGED": 0.194, "Hall": 0.024, "T": 0.964, "A": 0.945, "D": 0.773, "E": 0.957, "R": 0.930
    },
    ("SchemaBench", "GPT-5.4-mini"): {
        "nGED": 0.198, "Hall": 0.025, "T": 0.961, "A": 0.921, "D": 0.745, "E": 0.951, "R": 0.934
    },
}

METRIC_KEYS = [
    ("nGED", "nged"),
    ("Hall", "hall"),
    ("T", "tables"),
    ("A", "attributes"),
    ("D", "domain"),
    ("E", "entity"),
    ("R", "referential"),
]

PRED_DIRS = {
    "Enterprise-145": lambda m: DATA / "LLMTranslations" / "Exp4" / f"Text2Schema2_{m}",
    "RSchema": lambda m: DATA / "RSchema_ExpResults4" / "Exp4" / f"text2schema_{m}",
    "SchemaBench": lambda m: DATA / "Text2ER" / "SchemaBench" / "Exp4" / f"text2schema_{m}",
}
NL_DIRS = {
    "Enterprise-145": DATA / "LLMTranslations" / "Exp2" / "Schema2Text2_gpt54mini",
    "RSchema": DATA / "RSchema_ExpResults4" / "Experiment2" / "schema2text_gpt54mini",
    "SchemaBench": DATA / "Text2ER" / "SchemaBench" / "Experiment" / "schema2text_gpt54mini",
}


def r3(x: float) -> float:
    return round(float(x) + 1e-12, 3)


def sha256_text(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def load_rschema_381() -> dict[str, str]:
    candidates = [
        ROOT / "experiments" / "E3" / "manifests" / "RSCHEMA_381_ELIGIBLE.csv",
        OUT / "manifests" / "RSCHEMA_381_ELIGIBLE.csv",
        ROOT / "results" / "metrics" / "reproduced" / "E2_AUDIT" / "manifests" / "RSCHEMA_381_ELIGIBLE.csv",
        DATA / "SchemaBridge" / "results" / "metrics" / "reproduced" / "E2_AUDIT" / "manifests" / "RSCHEMA_381_ELIGIBLE.csv",
    ]
    manifest = next((p for p in candidates if p.exists()), candidates[0])
    out: dict[str, str] = {}
    with manifest.open() as f:
        for row in csv.DictReader(f):
            out[row["schema_id"]] = row["serial_in_518"]
    assert len(out) == 381, len(out)
    return out


def enterprise_gold() -> dict:
    schema_dir = DATA / "Text2ER" / "schema"
    index = json.loads((schema_dir / "index.json").read_text())
    gold = {}
    for ds in index["datasets"]:
        name = ds["safe_name"]
        meta = json.loads((schema_dir / f"{name}.metadata.json").read_text())
        ddl = (schema_dir / f"{name}.sql").read_text(encoding="utf-8", errors="replace")
        gold[name] = {
            "meta": meta,
            "ddl": ddl,
            "table_count": ds.get("table_count") or 0,
            "column_count": ds.get("column_count") or 0,
            "serial": name,
            "database": ds.get("database") or name,
        }
    assert len(gold) == 145, len(gold)
    return gold


def schemabench_gold() -> dict:
    path = DATA / "SchemaBench" / "Dataset" / "annotation_ddl.jsonl"
    if not path.exists():
        path = DATA / "Text2ER" / "SchemaBench" / "Dataset" / "annotation_ddl.jsonl"
    gold = {}
    for i, r in enumerate(load_jsonl(path), 1):
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


def rschema_gold(eligible: dict[str, str]) -> dict:
    ddl_recs = {r["id"]: r for r in load_jsonl(DATA / "RSchema" / "annotation_ddl.jsonl")}
    gold = {}
    for rid, serial in eligible.items():
        r = ddl_recs[rid]
        ddl = (r.get("answer") or "").strip() if isinstance(r.get("answer"), str) else ""
        db = r.get("database") or f"rschema_{serial}"
        meta = metadata_from_ddl(ddl, database=db)
        tables, cols, _ = ev.extract_schema_from_metadata(meta)
        gold[rid] = {
            "serial": serial,
            "meta": meta,
            "ddl": ddl,
            "table_count": len(tables),
            "column_count": sum(len(v) for v in cols.values()),
            "database": db,
        }
    assert len(gold) == 381, len(gold)
    return gold


def parse_pred(pred_path: Path):
    data = json.loads(pred_path.read_text(encoding="utf-8"))
    ddl = (data.get("ddl") or "").strip()
    err = data.get("error") or data.get("skipped")
    if err or not ddl or str(ddl).startswith("ERROR:"):
        txt_path = pred_path.with_suffix(".txt")
        if txt_path.is_file():
            txt = txt_path.read_text(encoding="utf-8", errors="replace").strip()
            if txt and not txt.startswith("ERROR:"):
                ddl = txt
                err = None
    meta = ensure_prediction_metadata(
        data.get("metadata") or {}, ddl, database=data.get("database") or ""
    )
    return data, ddl, meta, err


def index_predictions(pred_dir: Path):
    by_id, by_serial, by_name = {}, {}, {}
    raw_json = 0
    for pj in pred_dir.glob("*.json"):
        if pj.name in ("batch_state.json", "index.json"):
            continue
        raw_json += 1
        try:
            d = json.loads(pj.read_text(encoding="utf-8"))
        except Exception:
            continue
        by_serial[pj.stem] = pj
        by_name[pj.stem] = pj
        if d.get("id"):
            by_id[d["id"]] = pj
        sn = d.get("safe_name") or d.get("database")
        if sn:
            by_name[sn] = pj
    return by_id, by_serial, by_name, raw_json


def score_group(dataset: str, model_key: str, model_label: str, gold: dict, id_mode: str):
    ev.normalize_name = normalize_rschema_name
    pred_dir = PRED_DIRS[dataset](model_key)
    nl_dir = NL_DIRS[dataset]
    by_id, by_serial, by_name, n_pred_json = index_predictions(pred_dir)

    items = []
    ngeds = []
    case_rows = []
    failures = []
    missing = 0
    emptyish = 0
    nl_match = 0
    nl_mismatch = 0
    nl_missing_frozen = 0
    source_ok = 0
    source_bad = 0

    for rid, g in gold.items():
        if id_mode == "name":
            pred_path = by_name.get(rid) or (pred_dir / f"{rid}.json")
            if not pred_path.exists():
                pred_path = None
        else:
            pred_path = by_id.get(rid) or by_serial.get(g["serial"])

        frozen_nl = ""
        frozen_path = None
        if id_mode == "name":
            frozen_path = nl_dir / f"{rid}.txt"
        else:
            frozen_path = nl_dir / f"{g['serial']}.txt"
            if not frozen_path.exists() and pred_path is not None:
                frozen_path = nl_dir / f"{pred_path.stem}.txt"
        if frozen_path and frozen_path.exists():
            frozen_nl = frozen_path.read_text(encoding="utf-8", errors="replace").strip()
        else:
            nl_missing_frozen += 1

        if pred_path is None:
            missing += 1
            # Empty prediction against gold (PRIMARY: remain in N).
            empty_meta = {"database": "", "tables": [], "columns_by_table": {}}
            m = ev.evaluate_one(
                str(rid), g["meta"], g["ddl"], empty_meta, "", g["table_count"], g["column_count"]
            )
            per = {
                "tables": {"gold": m.original_tables, "recreated": 0, "matched": 0},
                "attributes": {"gold": m.original_attrs, "recreated": 0, "matched": 0},
                "domain": {"gold": m.original_attrs, "recreated": 0, "matched": 0},
                "entity": {
                    "gold": m.entity_original_constraints,
                    "recreated": 0,
                    "matched": 0,
                },
                "referential": {"gold": m.original_fks, "recreated": 0, "matched": 0},
            }
            nged = normalized_graph_edit_distance(g["meta"], g["ddl"], empty_meta, "")
            items.append(per)
            ngeds.append(nged)
            failures.append({"id": rid, "reason": "missing_prediction", "nged": nged})
            case_rows.append(
                {
                    "dataset": dataset,
                    "model": model_label,
                    "schema_id": rid,
                    "serial": g.get("serial"),
                    "status": "missing",
                    "nged": nged,
                    "nl_hash": sha256_text(frozen_nl) if frozen_nl else "",
                    "pred_nl_hash": "",
                    "source_schema2text_llm": "",
                }
            )
            continue

        try:
            data, ddl, meta, err = parse_pred(pred_path)
        except Exception as e:
            empty_meta = {"database": "", "tables": [], "columns_by_table": {}}
            m = ev.evaluate_one(
                str(rid), g["meta"], g["ddl"], empty_meta, "", g["table_count"], g["column_count"]
            )
            per = {
                "tables": {"gold": m.original_tables, "recreated": 0, "matched": 0},
                "attributes": {"gold": m.original_attrs, "recreated": 0, "matched": 0},
                "domain": {"gold": m.original_attrs, "recreated": 0, "matched": 0},
                "entity": {
                    "gold": m.entity_original_constraints,
                    "recreated": 0,
                    "matched": 0,
                },
                "referential": {"gold": m.original_fks, "recreated": 0, "matched": 0},
            }
            nged = normalized_graph_edit_distance(g["meta"], g["ddl"], empty_meta, "")
            items.append(per)
            ngeds.append(nged)
            failures.append({"id": rid, "reason": f"parse_error:{e}", "nged": nged})
            case_rows.append(
                {
                    "dataset": dataset,
                    "model": model_label,
                    "schema_id": rid,
                    "serial": g.get("serial"),
                    "status": "parse_error",
                    "nged": nged,
                    "nl_hash": sha256_text(frozen_nl) if frozen_nl else "",
                    "pred_nl_hash": "",
                    "source_schema2text_llm": "",
                }
            )
            continue

        pred_nl = (data.get("nl_text") or "").strip()
        if frozen_nl:
            if pred_nl == frozen_nl:
                nl_match += 1
            else:
                nl_mismatch += 1
        src = (data.get("source_schema2text_llm") or "").lower()
        if "gpt54" in src or "gpt-5.4" in src or src in ("gpt54mini", "gpt_5_4_mini"):
            source_ok += 1
        elif src:
            source_bad += 1

        tables = meta.get("tables") or []
        cbt = meta.get("columns_by_table") or {}
        n_cols = sum(len(v or []) for v in cbt.values())
        has_create = "CREATE TABLE" in (ddl or "").upper()
        if err or (not tables and n_cols == 0 and not has_create):
            emptyish += 1
            status = "emptyish"
        else:
            status = "ok"

        # Always score prediction content (including empty) against gold.
        # Empty gold + empty pred => nGED 0 (matches original Enterprise behavior
        # for archive/ctu_vondreli/tmp).
        m = ev.evaluate_one(
            str(rid), g["meta"], g["ddl"], meta, ddl, g["table_count"], g["column_count"]
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
        nged = normalized_graph_edit_distance(g["meta"], g["ddl"], meta, ddl)
        items.append(per)
        ngeds.append(nged)
        case_rows.append(
            {
                "dataset": dataset,
                "model": model_label,
                "schema_id": rid,
                "serial": g.get("serial"),
                "status": status,
                "nged": nged,
                "nl_hash": sha256_text(frozen_nl) if frozen_nl else "",
                "pred_nl_hash": sha256_text(pred_nl) if pred_nl else "",
                "source_schema2text_llm": data.get("source_schema2text_llm") or "",
                "model_id": data.get("model_id") or "",
                "pred_path": str(pred_path),
            }
        )

    five = {k: agg_element(items, k) for k in ELEMENTS}
    hall = sum(five[d]["hallucination_rate"] for d in HALL_DIMS) / len(HALL_DIMS)
    mean_nged = sum(ngeds) / len(ngeds) if ngeds else 1.0

    return {
        "dataset": dataset,
        "model_key": model_key,
        "model": model_label,
        "population": len(gold),
        "evaluated_n": len(items),
        "pred_dir": str(pred_dir),
        "nl_dir": str(nl_dir),
        "n_pred_json": n_pred_json,
        "missing_predictions": missing,
        "emptyish_predictions": emptyish,
        "nl_match": nl_match,
        "nl_mismatch": nl_mismatch,
        "nl_missing_frozen": nl_missing_frozen,
        "source_gpt54mini_ok": source_ok,
        "source_non_gpt54mini": source_bad,
        "mean_nged": mean_nged,
        "hall": hall,
        "five_elements": five,
        "failures": failures,
        "cases": case_rows,
    }


def verify_isolation(golds: dict[str, dict], out_dir: Path) -> dict:
    """Verify identical frozen NL across constructors at schema-ID level."""
    rows = []
    summary = {}
    for dataset, gold in golds.items():
        nl_dir = NL_DIRS[dataset]
        id_mode = "name" if dataset == "Enterprise-145" else "id_serial"
        frozen_hashes = {}
        for rid, g in gold.items():
            if id_mode == "name":
                p = nl_dir / f"{rid}.txt"
            else:
                p = nl_dir / f"{g['serial']}.txt"
            if p.exists():
                txt = p.read_text(encoding="utf-8", errors="replace").strip()
                frozen_hashes[rid] = sha256_text(txt)
            else:
                frozen_hashes[rid] = None

        per_model = {}
        for model_key, model_label in MODELS:
            pred_dir = PRED_DIRS[dataset](model_key)
            by_id, by_serial, by_name, _ = index_predictions(pred_dir)
            hashes = {}
            sources = {}
            for rid, g in gold.items():
                if id_mode == "name":
                    pj = by_name.get(rid) or (pred_dir / f"{rid}.json")
                    if not Path(pj).exists():
                        pj = None
                else:
                    pj = by_id.get(rid) or by_serial.get(g["serial"])
                if pj is None:
                    hashes[rid] = None
                    sources[rid] = None
                    continue
                d = json.loads(Path(pj).read_text(encoding="utf-8"))
                hashes[rid] = sha256_text((d.get("nl_text") or "").strip())
                sources[rid] = d.get("source_schema2text_llm") or d.get("llm") or ""
            per_model[model_label] = {"hashes": hashes, "sources": sources}

        n = len(gold)
        identical_all = 0
        mismatch_ids = []
        missing_frozen = sum(1 for h in frozen_hashes.values() if h is None)
        for rid in gold:
            fh = frozen_hashes[rid]
            model_hs = [per_model[lab]["hashes"].get(rid) for _, lab in MODELS]
            if fh is None or any(h is None for h in model_hs):
                continue
            if len(set(model_hs)) == 1 and model_hs[0] == fh:
                identical_all += 1
            else:
                mismatch_ids.append(rid)
            rows.append(
                {
                    "dataset": dataset,
                    "schema_id": rid,
                    "frozen_hash": fh or "",
                    "all_constructors_match_frozen": int(
                        len(set(model_hs)) == 1 and model_hs[0] == fh
                    ),
                    "unique_pred_hashes": len(set(h for h in model_hs if h)),
                    **{f"hash_{mk}": per_model[lab]["hashes"].get(rid) or "" for mk, lab in MODELS},
                }
            )

        summary[dataset] = {
            "population": n,
            "frozen_available": n - missing_frozen,
            "frozen_missing": missing_frozen,
            "identical_across_5_constructors_and_frozen": identical_all,
            "mismatch_or_incomplete": n - identical_all,
            "mismatch_ids_sample": mismatch_ids[:20],
        }

    with (out_dir / "isolation_schema_hashes.csv").open("w", newline="") as f:
        if rows:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    (out_dir / "isolation_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def write_outputs(results: list[dict], isolation: dict) -> None:
    metrics_dir = OUT / "metrics"
    prov = OUT / "provenance"
    latex_dir = OUT / "latex"
    inv = OUT / "inventory"
    for d in (metrics_dir, prov, latex_dir, inv, OUT / "isolation"):
        d.mkdir(parents=True, exist_ok=True)

    # Group completeness
    comp_rows = []
    for r in results:
        comp_rows.append(
            {
                "dataset": r["dataset"],
                "constructor": r["model"],
                "expected_n": r["population"],
                "evaluated_n": r["evaluated_n"],
                "pred_json_files": r["n_pred_json"],
                "missing_predictions": r["missing_predictions"],
                "emptyish_predictions": r["emptyish_predictions"],
                "frozen_nl_dir": r["nl_dir"],
                "nl_match_pred_vs_frozen": r["nl_match"],
                "nl_mismatch": r["nl_mismatch"],
                "nl_missing_frozen": r["nl_missing_frozen"],
                "source_gpt54mini_ok": r["source_gpt54mini_ok"],
                "source_non_gpt54mini": r["source_non_gpt54mini"],
                "pred_dir": r["pred_dir"],
            }
        )
    with (inv / "group_completeness.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(comp_rows[0].keys()))
        w.writeheader()
        w.writerows(comp_rows)

    # Cell comparison (105)
    cell_rows = []
    match = mismatch = 0
    for r in results:
        paper = PAPER[(r["dataset"], r["model"])]
        recomputed = {
            "nGED": r["mean_nged"],
            "Hall": r["hall"],
            "T": r["five_elements"]["tables"]["f1"],
            "A": r["five_elements"]["attributes"]["f1"],
            "D": r["five_elements"]["domain"]["f1"],
            "E": r["five_elements"]["entity"]["f1"],
            "R": r["five_elements"]["referential"]["f1"],
        }
        for metric, _ in METRIC_KEYS:
            pv = paper[metric]
            rv = recomputed[metric]
            diff = rv - pv
            status = "MATCH" if r3(pv) == r3(rv) else "MISMATCH"
            if status == "MATCH":
                match += 1
            else:
                mismatch += 1
            cell_rows.append(
                {
                    "Dataset": r["dataset"],
                    "Constructor": r["model"],
                    "Metric": metric,
                    "Paper": pv,
                    "Recomputed": rv,
                    "Recomputed_3dec": r3(rv),
                    "Difference": diff,
                    "Status": status,
                    "N": r["evaluated_n"],
                }
            )
    with (metrics_dir / "E3_CELL_COMPARISON_105.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(cell_rows[0].keys()))
        w.writeheader()
        w.writerows(cell_rows)

    # Summary table
    sum_rows = []
    for r in results:
        paper = PAPER[(r["dataset"], r["model"])]
        rec = {
            "nGED": r["mean_nged"],
            "Hall": r["hall"],
            "T": r["five_elements"]["tables"]["f1"],
            "A": r["five_elements"]["attributes"]["f1"],
            "D": r["five_elements"]["domain"]["f1"],
            "E": r["five_elements"]["entity"]["f1"],
            "R": r["five_elements"]["referential"]["f1"],
        }
        n_match = sum(1 for m, _ in METRIC_KEYS if r3(paper[m]) == r3(rec[m]))
        sum_rows.append(
            {
                "Dataset": r["dataset"],
                "Constructor": r["model"],
                "N": r["evaluated_n"],
                **{f"{m}_full": rec[m] for m, _ in METRIC_KEYS},
                **{f"{m}_3dec": r3(rec[m]) for m, _ in METRIC_KEYS},
                **{f"{m}_paper": paper[m] for m, _ in METRIC_KEYS},
                "cells_match_3dec": n_match,
            }
        )
    with (metrics_dir / "E3_PRIMARY_FINAL.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(sum_rows[0].keys()))
        w.writeheader()
        w.writerows(sum_rows)

    # Full JSON
    slim = []
    for r in results:
        slim.append({k: v for k, v in r.items() if k != "cases"})
        # write cases separately
    (metrics_dir / "E3_PRIMARY_RESULTS.json").write_text(
        json.dumps(
            {
                "generated": datetime.now(timezone.utc).isoformat(),
                "population": {"Enterprise-145": 145, "RSchema": 381, "SchemaBench": 239},
                "hallucination_dims": list(HALL_DIMS),
                "normalization": "normalize_rschema_name",
                "vendor": str(VENDOR),
                "isolation": isolation,
                "groups": slim,
                "cell_match": match,
                "cell_mismatch": mismatch,
            },
            indent=2,
        )
        + "\n"
    )

    # Case-level dump (compressed-ish CSV of nged only; full in jsonl)
    case_path = metrics_dir / "E3_CASE_LEVEL.jsonl"
    with case_path.open("w") as f:
        for r in results:
            for c in r["cases"]:
                f.write(json.dumps(c) + "\n")

    # LaTeX table from recomputed values with correct bolding
    write_latex(sum_rows, latex_dir)

    # Verdict stub numbers
    (OUT / "E3_MATCH_COUNTS.json").write_text(
        json.dumps(
            {
                "groups": 15,
                "cells_total": 105,
                "MATCH": match,
                "MISMATCH": mismatch,
                "UNVERIFIABLE": 0,
                "isolation": isolation,
            },
            indent=2,
        )
        + "\n"
    )


def write_latex(sum_rows: list[dict], latex_dir: Path) -> None:
    """Bold best-in-dataset: min nGED/Hall, max T/A/D/E/R. Ties all bolded."""
    by_ds: dict[str, list] = {}
    for row in sum_rows:
        by_ds.setdefault(row["Dataset"], []).append(row)

    def fmt(ds_rows, metric, lower_better=False):
        vals = [r[f"{metric}_3dec"] for r in ds_rows]
        best = min(vals) if lower_better else max(vals)
        out = []
        for r in ds_rows:
            v = r[f"{metric}_3dec"]
            s = f"{v:.3f}"
            if v == best:
                s = f"\\textbf{{{s}}}"
            out.append(s)
        return out

    lines = []
    lines.append("% Auto-generated from E3 PRIMARY independent evaluation.")
    lines.append("% Population: Enterprise-145=145, RSchema=381 DDL-matched, SchemaBench=239.")
    lines.append("\\begin{table*}[t]")
    lines.append("\\centering")
    lines.append(
        "\\caption{Constructor isolation (E3): frozen GPT-5.4-mini detailed descriptions "
        "reconstructed by five constructors. Mean nGED and four-dimensional hallucination "
        "(Tables/Attributes/Entity/Referential; Domain excluded); micro-averaged structural "
        "$F_1$ for Tables (T), Attributes (A), Domain (D), Entity (E), Referential (R). "
        "Lower is better for nGED and Hall.; higher is better for $F_1$. "
        "Bold = best within each dataset column (ties shared).}"
    )
    lines.append("\\label{tab:e3_overall}")
    lines.append("\\resizebox{\\textwidth}{!}{%")
    lines.append("\\begin{tabular}{llccccccc}")
    lines.append("\\toprule")
    lines.append(
        "Dataset & Constructor & nGED $\\downarrow$ & Hall. $\\downarrow$ & T & A & D & E & R \\\\"
    )
    lines.append("\\midrule")

    order = ["Enterprise-145", "RSchema", "SchemaBench"]
    model_order = [lab for _, lab in MODELS]
    for ds in order:
        rows = sorted(by_ds[ds], key=lambda r: model_order.index(r["Constructor"]))
        cols = {
            "nGED": fmt(rows, "nGED", lower_better=True),
            "Hall": fmt(rows, "Hall", lower_better=True),
            "T": fmt(rows, "T"),
            "A": fmt(rows, "A"),
            "D": fmt(rows, "D"),
            "E": fmt(rows, "E"),
            "R": fmt(rows, "R"),
        }
        for i, r in enumerate(rows):
            ds_cell = ds if i == 0 else ""
            lines.append(
                f"{ds_cell} & {r['Constructor']} & {cols['nGED'][i]} & {cols['Hall'][i]} & "
                f"{cols['T'][i]} & {cols['A'][i]} & {cols['D'][i]} & {cols['E'][i]} & {cols['R'][i]} \\\\"
            )
        if ds != order[-1]:
            lines.append("\\midrule")

    lines.append("\\bottomrule")
    lines.append("\\end{tabular}%")
    lines.append("}")
    lines.append("\\end{table*}")
    (latex_dir / "tab_e3_overall_verified.tex").write_text("\n".join(lines) + "\n")


def main() -> None:
    print("E3 PRIMARY evaluation starting", flush=True)
    print("vendor:", VENDOR, flush=True)
    eligible = load_rschema_381()
    golds = {
        "Enterprise-145": enterprise_gold(),
        "RSchema": rschema_gold(eligible),
        "SchemaBench": schemabench_gold(),
    }
    print({k: len(v) for k, v in golds.items()}, flush=True)

    print("Verifying constructor isolation...", flush=True)
    isolation = verify_isolation(golds, OUT / "isolation")
    print(json.dumps(isolation, indent=2), flush=True)

    results = []
    for dataset, id_mode in [
        ("Enterprise-145", "name"),
        ("RSchema", "id_serial"),
        ("SchemaBench", "id_serial"),
    ]:
        for model_key, model_label in MODELS:
            print(f"Evaluating {dataset} / {model_label} ...", flush=True)
            r = score_group(dataset, model_key, model_label, golds[dataset], id_mode)
            print(
                f"  n={r['evaluated_n']} nGED={r3(r['mean_nged'])} Hall={r3(r['hall'])} "
                f"T={r3(r['five_elements']['tables']['f1'])} "
                f"A={r3(r['five_elements']['attributes']['f1'])} "
                f"D={r3(r['five_elements']['domain']['f1'])} "
                f"E={r3(r['five_elements']['entity']['f1'])} "
                f"R={r3(r['five_elements']['referential']['f1'])} "
                f"nl_match={r['nl_match']} mismatch={r['nl_mismatch']}",
                flush=True,
            )
            results.append(r)

    write_outputs(results, isolation)
    print("Wrote outputs under", OUT, flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
