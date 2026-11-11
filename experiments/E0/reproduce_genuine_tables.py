#!/usr/bin/env python3
"""Recompute E0 Tables V & VI under the genuine-gold protocol.

Protocol (authoritative):
  * RSchema structural T/A/E/R + Hall4 + name-only nGED on 518 logical refs
    (``datasets/rschema/annotation.jsonl``).
  * RSchema Domain F1 only on the 381 ID-matched DDL refs
    (``datasets/rschema/annotation_ddl.jsonl``); no synthetic types as gold.
  * SchemaBench: all five dimensions on 239 DDL refs.
  * Hallucination: 4-dim micro mean over T/A/E/R (Domain excluded).
  * Failures: empty prediction, nGED=1, Hall not forced to 1.
  * PaperMethods baselines: Domain reported as ``--`` (untyped logical outputs).
  * Direct rows of Table VI are copied from Table V (bit-identical before rounding).
  * Parser: ``legacy=False``; nGED: ``names_only=True``.

Offline only — no LLM / API calls.

Usage::

    python3 experiments/E0/reproduce_genuine_tables.py
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.evaluator import (  # noqa: E402
    aggregate_schemas,
    empty_prediction_against_gold,
    evaluate_schema_pair,
    five_element_counts,
    gold_answer_to_metadata_and_ddl,
    gold_record_to_metadata_and_ddl,
    load_jsonl,
)
from src.metrics import (  # noqa: E402
    ELEMENTS,
    HALLUCINATION_DIMS,
    aggregate_hallucination_micro,
    hallucination_rate,
    micro_aggregate,
    micro_f1,
    micro_prf,
)
from src.schema_parser import ensure_prediction_metadata, metadata_from_ddl  # noqa: E402

OUT = ROOT / "results" / "metrics" / "reproduced"
AUDIT = ROOT / "audit" / "e0_gold_requirement_verification"
SEED = 42

# Default Table V Direct models (paper configuration). Missing dirs are skipped.
DIRECT = {
    "RSchema": {
        "CodeLlama-13B": ROOT / "results/predictions/e0/rschema_exp4_codellama13b",
        "Llama-3.1-8B": ROOT / "results/predictions/e0/rschema_exp4_llama31",
        "DeepSeek-Coder-6.7B": ROOT / "results/predictions/e0/rschema_exp4_deepseek",
        "Claude Sonnet 4.6": ROOT / "results/predictions/e0/rschema_exp4_claude_sonnet_4_6",
        "GPT-5.4-mini": ROOT / "results/predictions/e0/rschema_exp4_gpt_5_4_mini",
    },
    "SchemaBench": {
        "CodeLlama-13B": ROOT / "results/predictions/e0/schemabench_exp2_codellama13b",
        "Llama-3.1-8B": ROOT / "results/predictions/e0/schemabench_exp2_llama31",
        "DeepSeek-Coder-6.7B": ROOT / "results/predictions/e0/schemabench_exp2_deepseek",
        "Claude Sonnet 4.6": ROOT / "results/predictions/e0/schemabench_exp2_claude_sonnet_4_6",
        "GPT-5.4-mini": ROOT / "results/predictions/e0/schemabench_exp2_gpt_5_4_mini",
    },
}
# Optional experiment only — not part of default Table V paper rows.
OPTIONAL_DIRECT = {
    "RSchema": {
        "GPT-4o-mini": ROOT / "results/predictions/e0/rschema_exp4_gpt4omini",
    },
}
GOLD_LOGICAL = {
    "RSchema": ROOT / "datasets/rschema/annotation.jsonl",
}
GOLD_DDL = {
    "RSchema": ROOT / "datasets/rschema/annotation_ddl.jsonl",
    "SchemaBench": ROOT / "datasets/schemabench/annotation_ddl.jsonl",
}
BASELINE_ROOT = {
    "RSchema": ROOT / "results/predictions/e0/rschema_papermethods",
    "SchemaBench": ROOT / "results/predictions/e0/schemabench_papermethods",
}
OLD_GENUINE_V = OUT / "E0_TABLE_V_GENUINE.csv"
OLD_GENUINE_VI = OUT / "E0_TABLE_VI_GENUINE.csv"
# Historical Hall4 freeze kept for archive comparison only.
OLD_HALL4_V = OUT / "E0_TABLE_V_HALL4.csv"
OLD_HALL4_VI = OUT / "E0_TABLE_VI_HALL4.csv"

MODEL_FILE = {
    "CodeLlama-13B": "codellama13b",
    "Llama-3.1-8B": "llama31",
    "DeepSeek-Coder-6.7B": "deepseek",
}
FILE_MODEL = {v: k for k, v in MODEL_FILE.items()}
METHODS = ["one_shot", "one_shot_cot", "few_shot"]
METHOD_LABEL = {
    "one_shot": "One-shot",
    "one_shot_cot": "One-shot+CoT",
    "few_shot": "Few-shot",
}
STRUCT_DIMS = ("tables", "attributes", "entity", "referential")
METRICS_V = ["nged", "halluc", "tables", "attributes", "domain", "entity", "referential"]
LOWER = {"nged", "halluc"}

TYPE_TOKEN_RE = re.compile(
    r"\b(varchar|nvarchar|char|nchar|text|tinytext|mediumtext|longtext|int|integer|tinyint|smallint|"
    r"mediumint|bigint|float|double|real|decimal|numeric|bool|boolean|bit|date|datetime|"
    r"timestamp|time|year|blob|tinyblob|mediumblob|longblob|binary|varbinary|json|enum|set)\b",
    re.IGNORECASE,
)


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def r3(x: float) -> float:
    return float(f"{x:.3f}")


# --------------------------------------------------------------------------- logical prediction normalisation (PaperMethods)


def _as_attr_list(attrs: Any) -> list[str]:
    if attrs is None:
        return []
    if isinstance(attrs, dict):
        return [str(k) for k in attrs.keys()]
    if isinstance(attrs, list):
        out = []
        for a in attrs:
            if isinstance(a, dict):
                out.append(str(next(iter(a.keys()), "")))
            else:
                out.append(str(a))
        return [a for a in out if a]
    return [str(attrs)]


def _get_pk(tdef: dict) -> list[str]:
    for key in ("Primary key", "Primarykey", "primary key", "primarykey", "PrimaryKey"):
        if key in tdef:
            pk = tdef[key]
            if isinstance(pk, list):
                return [str(x) for x in pk]
            if isinstance(pk, str):
                return [pk]
    return []


def _get_fk(tdef: dict) -> dict:
    for key in ("Foreign key", "Foreignkey", "foreign key", "foreignkey", "ForeignKey"):
        if key in tdef and isinstance(tdef[key], dict):
            return tdef[key]
    return {}


def _logical_table_def(tdef: dict) -> dict | None:
    if not isinstance(tdef, dict):
        return None
    attrs = tdef.get("Attributes")
    if attrs is None:
        attrs = tdef.get("Attribute") or tdef.get("attributes") or tdef.get("attribute")
    if attrs is None and not _get_pk(tdef):
        return None
    out: dict[str, Any] = {"Attributes": _as_attr_list(attrs), "Primary key": _get_pk(tdef)}
    fk = _get_fk(tdef)
    if fk:
        out["Foreign key"] = fk
    return out


def _entity_set_to_logical(payload: dict) -> dict:
    entity_key = next((k for k in payload if "Entity Set" in k), None)
    rel_key = next((k for k in payload if "Relationship Set" in k), None)
    entities = payload.get(entity_key) if entity_key else {}
    rels = payload.get(rel_key) if rel_key else {}
    if not isinstance(entities, dict):
        return {}
    tables: dict = {}
    for ename, eattrs in entities.items():
        attrs = _as_attr_list(eattrs if not isinstance(eattrs, dict) else eattrs.get("Attributes", eattrs))
        pk = _get_pk(eattrs) if isinstance(eattrs, dict) else []
        if isinstance(eattrs, dict) and not attrs:
            attrs = _as_attr_list(eattrs.get("Attributes") or eattrs.get("Attribute"))
        if not pk and attrs:
            for a in attrs:
                if "id" in a.lower() or a.lower() == "number":
                    pk = [a]
                    break
            if not pk:
                pk = [attrs[0]]
        tables[ename] = {"Attributes": list(attrs), "Primary key": pk, "Foreign key": {}}
    if isinstance(rels, dict):
        for rname, rdef in rels.items():
            if not isinstance(rdef, dict):
                continue
            objs = rdef.get("Object") or rdef.get("Objects") or []
            card = str(
                rdef.get("Proportional Relationship")
                or rdef.get("Mapping Cardinality")
                or rdef.get("Cardinality")
                or ""
            ).lower()
            rattrs = _as_attr_list(
                rdef.get("Relationship Attribute") or rdef.get("Attributes") or rdef.get("Attribute") or []
            )
            if not isinstance(objs, list) or len(objs) < 2:
                continue
            a, b = str(objs[0]), str(objs[1])
            a_pk = (tables.get(a) or {}).get("Primary key") or []
            b_pk = (tables.get(b) or {}).get("Primary key") or []
            if "many-to-many" in card or "many to many" in card:
                cols: list[str] = []
                fks: dict = {}
                for ent, pks in ((a, a_pk), (b, b_pk)):
                    for pk in pks or [f"{ent} ID"]:
                        col = pk if pk not in cols else f"{ent}_{pk}"
                        cols.append(col)
                        fks[col] = {ent: pk}
                cols.extend(rattrs)
                tables[rname] = {
                    "Attributes": cols,
                    "Primary key": [c for c in cols if c not in rattrs][:2] or cols[:2],
                    "Foreign key": fks,
                }
            else:
                many, one = a, b
                if "one-to-many" in card or "one to many" in card:
                    many, one = b, a
                elif "many-to-one" in card or "many to one" in card:
                    many, one = a, b
                if many in tables and one in tables:
                    one_pks = tables[one]["Primary key"] or [f"{one} ID"]
                    for pk in one_pks:
                        col = pk if pk not in tables[many]["Attributes"] else f"{one}_{pk}"
                        if col not in tables[many]["Attributes"]:
                            tables[many]["Attributes"].append(col)
                        tables[many].setdefault("Foreign key", {})[col] = {one: pk}
                    for ra in rattrs:
                        if ra not in tables[many]["Attributes"]:
                            tables[many]["Attributes"].append(ra)
    for tdef in tables.values():
        if not tdef.get("Foreign key"):
            tdef.pop("Foreign key", None)
    return tables


def normalize_prediction_answer(answer: Any) -> dict:
    if not isinstance(answer, dict) or not answer:
        return {}
    payload = answer
    if "schema" in payload and isinstance(payload["schema"], dict):
        payload = payload["schema"]
    if "output" in payload and isinstance(payload["output"], dict):
        payload = payload["output"]
    if any("Entity Set" in k for k in payload):
        return _entity_set_to_logical(payload)
    tables: dict = {}
    for tname, tdef in payload.items():
        if tname in ("schema", "output", "Entity Set", "Relationship Set"):
            continue
        norm = _logical_table_def(tdef) if isinstance(tdef, dict) else None
        if norm is not None:
            tables[str(tname)] = norm
    return tables


def load_baseline_predictions(
    dataset: str,
    model_file: str,
    method: str,
    expected_ids: set[str] | None = None,
) -> dict[str, Any]:
    """Load PaperMethods baseline predictions with explicit coverage status.

    Returns::
        {
          "path": Path,
          "status": "COMPLETE"|"INCOMPLETE"|"BLOCKED"|"INVALID",
          "preds": {id: answer_dict_or_empty},
          "coverage": {...},
          "message": str,
        }
    Empty ``answer`` dict marks a recorded generation failure (scored as empty).
    """
    path = BASELINE_ROOT[dataset] / model_file / method / "results.jsonl"
    expected = set(expected_ids or [])
    empty_cov = {
        "expected": len(expected),
        "present": 0,
        "valid": 0,
        "generation_failed": 0,
        "malformed": 0,
        "missing": len(expected),
        "duplicate_ids": 0,
        "unexpected_ids": 0,
    }
    if not path.is_file():
        return {
            "path": path,
            "status": "BLOCKED",
            "preds": {},
            "coverage": empty_cov,
            "message": f"BLOCKED: baseline prediction file unavailable: {path}",
        }
    raw = path.read_text(encoding="utf-8")
    if not raw.strip():
        return {
            "path": path,
            "status": "BLOCKED",
            "preds": {},
            "coverage": empty_cov,
            "message": f"BLOCKED: baseline prediction file empty: {path}",
        }

    preds: dict[str, dict] = {}
    duplicate_ids = 0
    malformed = 0
    generation_failed = 0
    seen: set[str] = set()
    unexpected = 0
    for line_no, line in enumerate(raw.splitlines(), 1):
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except Exception:  # noqa: BLE001
            malformed += 1
            continue
        rid = r.get("id")
        if not rid:
            malformed += 1
            continue
        rid = str(rid)
        if rid in seen:
            duplicate_ids += 1
        seen.add(rid)
        if expected and rid not in expected:
            unexpected += 1
        status = r.get("status")
        if status not in (None, "ok") and r.get("error"):
            preds[rid] = {}
            generation_failed += 1
            continue
        answer = normalize_prediction_answer(r.get("answer"))
        if not answer:
            preds[rid] = {}
            generation_failed += 1
        else:
            preds[rid] = answer

    present_ids = set(preds) & expected if expected else set(preds)
    missing = sorted(expected - set(preds)) if expected else []
    valid = sum(1 for rid in present_ids if preds.get(rid))
    gen_fail_in_expected = sum(1 for rid in present_ids if not preds.get(rid))
    coverage = {
        "expected": len(expected) if expected else len(preds),
        "present": len(present_ids) if expected else len(preds),
        "valid": valid,
        "generation_failed": gen_fail_in_expected,
        "malformed": malformed,
        "missing": len(missing),
        "duplicate_ids": duplicate_ids,
        "unexpected_ids": unexpected,
    }
    if malformed or duplicate_ids or unexpected:
        status_s = "INVALID"
        msg = (
            f"INVALID: baseline malformed={malformed} duplicates={duplicate_ids} "
            f"unexpected={unexpected} present={coverage['present']}/{coverage['expected']}"
        )
    elif expected and coverage["present"] < coverage["expected"]:
        status_s = "INCOMPLETE"
        msg = (
            f"INCOMPLETE: baseline coverage {coverage['present']}/{coverage['expected']} "
            f"(missing={coverage['missing']})"
        )
    else:
        status_s = "COMPLETE"
        msg = (
            f"COMPLETE: baseline {coverage['present']}/{coverage['expected']} present, "
            f"{coverage['valid']} valid, {coverage['generation_failed']} recorded failures"
        )
    return {
        "path": path,
        "status": status_s,
        "preds": preds,
        "coverage": coverage,
        "message": msg,
    }


# --------------------------------------------------------------------------- gold verification


def ddl_has_genuine_types(ddl: str) -> bool:
    return bool(TYPE_TOKEN_RE.search(ddl or ""))


def verify_gold_refs() -> dict[str, Any]:
    logical = load_jsonl(GOLD_LOGICAL["RSchema"])
    ddl_rs = load_jsonl(GOLD_DDL["RSchema"])
    sb = load_jsonl(GOLD_DDL["SchemaBench"])
    assert len(logical) == 518, len(logical)
    assert len(ddl_rs) == 381, len(ddl_rs)
    assert len(sb) == 239, len(sb)
    ids_l = {r["id"] for r in logical if r.get("id")}
    ids_d = {r["id"] for r in ddl_rs if r.get("id")}
    ids_sb = {r["id"] for r in sb if r.get("id")}
    assert len(ids_l) == 518
    assert ids_d <= ids_l
    assert len(ids_d) == 381
    assert len(ids_sb) == 239
    typed = sum(1 for r in ddl_rs if isinstance(r.get("answer"), str) and ddl_has_genuine_types(r["answer"]))
    typed_sb = sum(1 for r in sb if isinstance(r.get("answer"), str) and ddl_has_genuine_types(r["answer"]))
    total_cols = 0
    typed_ok = 0
    unsupported = 0
    unknown_null = 0
    overlap_excl = 0
    eligible_attrs = 0
    null_dist: dict[str, int] = defaultdict(int)
    for r in ddl_rs:
        ddl = r.get("answer") or ""
        meta = metadata_from_ddl(ddl, legacy=False)
        for t, cols in (meta.get("columns_by_table") or {}).items():
            for c in cols or []:
                total_cols += 1
                dt = (c.get("DATA_TYPE") or "").strip()
                tstat = (c.get("TYPE_STATUS") or "").lower()
                nstat = (c.get("NULLABILITY_STATUS") or "").lower()
                null_dist[nstat or ""] += 1
                is_typed = bool(dt) and tstat == "ok"
                is_null_known = nstat != "unknown" and not (
                    not (c.get("IS_NULLABLE") or "").strip() and nstat in ("", "unknown")
                )
                if not is_typed:
                    unsupported += 1
                if not is_null_known:
                    unknown_null += 1
                if (not is_typed) and (not is_null_known):
                    overlap_excl += 1
                if is_typed:
                    typed_ok += 1
                if is_typed and is_null_known:
                    eligible_attrs += 1
    return {
        "rschema_logical": 518,
        "rschema_ddl": 381,
        "rschema_ddl_subset_of_logical": True,
        "rschema_ddl_typed_records": typed,
        "rschema_ddl_total_parsed_columns": total_cols,
        "rschema_ddl_typed_ok_columns": typed_ok,
        "rschema_ddl_unsupported_type_columns": unsupported,
        "rschema_ddl_unknown_nullability_columns": unknown_null,
        "rschema_ddl_overlap_unsupported_and_unknown_null": overlap_excl,
        "rschema_ddl_domain_eligible_attributes": eligible_attrs,
        "rschema_nullability_status": dict(null_dist),
        "schemabench": 239,
        "schemabench_typed_records": typed_sb,
    }


def write_domain_column_reconciliation(ddl_rows: list[dict], path: Path) -> dict[str, Any]:
    """Column-level reconciliation for the 381 RSchema DDL Domain cohort."""
    from src.schema_parser import (  # local import keeps module load light
        _ROBUST_SKIP_PREFIXES,
        _column_item_to_obj,
        _split_top_level,
        _strip_comments,
        iter_ddl_table_bodies,
    )

    rows: list[dict] = []
    for rec in ddl_rows:
        rid = rec["id"]
        ddl = rec.get("answer") or ""
        for table, body in iter_ddl_table_bodies(ddl, legacy=False):
            for item in _split_top_level(_strip_comments(body)):
                line = item.strip().rstrip(",")
                if not line:
                    continue
                if line.upper().startswith(_ROBUST_SKIP_PREFIXES):
                    rows.append(
                        {
                            "schema_id": rid,
                            "table": table,
                            "column_name": "",
                            "original_declaration": re.sub(r"\s+", " ", line)[:240],
                            "parsed_type": "",
                            "parsed_nullability": "",
                            "nullability_status": "",
                            "type_status": "",
                            "parse_status": "constraint_skipped",
                            "exclusion_reason": "table_level_constraint_or_index",
                            "domain_eligible": False,
                        }
                    )
                    continue
                obj = _column_item_to_obj(item, 1, legacy=False)
                if obj is None:
                    rows.append(
                        {
                            "schema_id": rid,
                            "table": table,
                            "column_name": "",
                            "original_declaration": re.sub(r"\s+", " ", line)[:240],
                            "parsed_type": "",
                            "parsed_nullability": "",
                            "nullability_status": "",
                            "type_status": "",
                            "parse_status": "unparsed",
                            "exclusion_reason": "unrecognised_column_declaration",
                            "domain_eligible": False,
                        }
                    )
                    continue
                typed_ok = bool(obj.get("DATA_TYPE")) and (obj.get("TYPE_STATUS") or "") == "ok"
                nstat = (obj.get("NULLABILITY_STATUS") or "").lower()
                null_known = nstat != "unknown" and not (
                    not (obj.get("IS_NULLABLE") or "").strip() and nstat in ("", "unknown")
                )
                eligible = typed_ok and null_known
                if not typed_ok and not null_known:
                    reason = "unsupported_type_and_unknown_nullability"
                    parse_status = "recovered_unsupported_type"
                elif not typed_ok:
                    reason = "unsupported_or_placeholder_type"
                    parse_status = "recovered_unsupported_type"
                elif not null_known:
                    reason = "unknown_nullability"
                    parse_status = "unknown_nullability"
                else:
                    reason = ""
                    parse_status = "ok"
                rows.append(
                    {
                        "schema_id": rid,
                        "table": table,
                        "column_name": obj.get("COLUMN_NAME") or "",
                        "original_declaration": re.sub(r"\s+", " ", line)[:240],
                        "parsed_type": obj.get("DATA_TYPE") or "",
                        "parsed_nullability": obj.get("IS_NULLABLE") if obj.get("IS_NULLABLE") != "" else "",
                        "nullability_status": obj.get("NULLABILITY_STATUS") or "",
                        "type_status": obj.get("TYPE_STATUS") or "",
                        "parse_status": parse_status,
                        "exclusion_reason": reason,
                        "domain_eligible": eligible,
                    }
                )
    fields = [
        "schema_id",
        "table",
        "column_name",
        "original_declaration",
        "parsed_type",
        "parsed_nullability",
        "nullability_status",
        "type_status",
        "parse_status",
        "exclusion_reason",
        "domain_eligible",
    ]
    write_csv(path, rows, fields)
    col_rows = [r for r in rows if r["parse_status"] not in ("constraint_skipped",)]
    parsed_cols = [r for r in col_rows if r["parse_status"] != "unparsed"]
    eligible = sum(1 for r in rows if r["domain_eligible"])
    unsupported = sum(1 for r in rows if "unsupported" in (r["exclusion_reason"] or ""))
    unknown_null = sum(
        1 for r in rows if "unknown_nullability" in (r["exclusion_reason"] or "")
    )
    overlap = sum(
        1 for r in rows if r["exclusion_reason"] == "unsupported_type_and_unknown_nullability"
    )
    unparsed = sum(1 for r in rows if r["parse_status"] == "unparsed")
    return {
        "declaration_rows": len(rows),
        "parsed_columns": len(parsed_cols),
        "domain_eligible": eligible,
        "unsupported_or_placeholder_type": unsupported,
        "unknown_nullability": unknown_null,
        "overlap_unsupported_and_unknown_null": overlap,
        "unparsed": unparsed,
        "constraints_skipped": sum(1 for r in rows if r["parse_status"] == "constraint_skipped"),
    }


# --------------------------------------------------------------------------- aggregation helpers


def hall4_independent_recount(items: list[dict]) -> dict:
    totals = {d: {"P": 0, "M": 0} for d in HALLUCINATION_DIMS}
    for s in items:
        for d in HALLUCINATION_DIMS:
            totals[d]["P"] += int(s[d]["recreated"])
            totals[d]["M"] += int(s[d]["matched"])
    rates = {d: hallucination_rate(totals[d]["P"], totals[d]["M"]) for d in HALLUCINATION_DIMS}
    return {"totals": totals, "rates": rates, "halluc": sum(rates.values()) / len(rates)}


def micro_struct(items: list[dict]) -> dict[str, float]:
    out = {}
    for d in STRUCT_DIMS:
        out[d] = float(micro_aggregate(items, d)["f1"])
    return out


def index_predictions(pred_dir: Path) -> dict[str, Any]:
    """Index NNNN.json predictions and detect duplicates / malformed files."""
    pred_by_id: dict[str, tuple[str, dict | None, str | None]] = {}
    pred_by_stem: dict[str, tuple[dict | None, str | None]] = {}
    id_to_stems: dict[str, list[str]] = defaultdict(list)
    malformed_stems: list[str] = []
    for pred_path in sorted(pred_dir.glob("[0-9][0-9][0-9][0-9].json")):
        stem = pred_path.stem
        try:
            data = json.loads(pred_path.read_text(encoding="utf-8"))
            pred_by_stem[stem] = (data, None)
            rid = str(data.get("id") or "")
            if rid:
                id_to_stems[rid].append(stem)
                pred_by_id[rid] = (stem, data, None)
        except Exception as e:  # noqa: BLE001
            pred_by_stem[stem] = (None, str(e))
            malformed_stems.append(stem)
    duplicate_ids = sorted(rid for rid, stems in id_to_stems.items() if len(stems) > 1)
    return {
        "pred_by_id": pred_by_id,
        "pred_by_stem": pred_by_stem,
        "id_to_stems": dict(id_to_stems),
        "duplicate_ids": duplicate_ids,
        "malformed_stems": malformed_stems,
    }


def classify_prediction_record(data: dict | None, read_error: str | None = None) -> str:
    """Return one of: valid | generation_failed | malformed."""
    if read_error or data is None:
        return "malformed"
    if data.get("error") or data.get("skipped"):
        return "generation_failed"
    ddl = (data.get("ddl") or "").strip()
    if not ddl or "CREATE TABLE" not in ddl.upper():
        return "generation_failed"
    return "valid"


def compute_direct_coverage(gold_rows: list[dict], index: dict[str, Any]) -> dict[str, Any]:
    """Coverage vs gold IDs — independent of scoring population size."""
    expected_ids = [str(r["id"]) for r in gold_rows]
    expected_set = set(expected_ids)
    pred_by_id = index["pred_by_id"]
    present = 0
    valid = 0
    generation_failed = 0
    malformed = 0
    missing = 0
    for rid in expected_ids:
        if rid not in pred_by_id:
            missing += 1
            continue
        present += 1
        _stem, data, _err = pred_by_id[rid]
        kind = classify_prediction_record(data)
        if kind == "valid":
            valid += 1
        elif kind == "generation_failed":
            generation_failed += 1
        else:
            malformed += 1
    # malformed stems without usable id also count
    malformed += len(index.get("malformed_stems") or [])
    unexpected = sorted(set(pred_by_id) - expected_set)
    duplicate_ids = list(index.get("duplicate_ids") or [])
    coverage = {
        "expected": len(expected_ids),
        "present": present,
        "valid": valid,
        "generation_failed": generation_failed,
        "malformed": malformed,
        "missing": missing,
        "duplicate_ids": len(duplicate_ids),
        "unexpected_ids": len(unexpected),
        "duplicate_id_list": duplicate_ids,
        "unexpected_id_list": unexpected[:20],
    }
    if duplicate_ids or unexpected or malformed:
        status = "INVALID"
        msg = (
            f"INVALID: duplicates={len(duplicate_ids)} unexpected={len(unexpected)} "
            f"malformed={malformed} present={present}/{coverage['expected']}"
        )
    elif missing > 0 or present < coverage["expected"]:
        status = "INCOMPLETE"
        msg = (
            f"INCOMPLETE: {present}/{coverage['expected']} present "
            f"({valid} valid, {generation_failed} recorded failures, {missing} missing)"
        )
    else:
        status = "COMPLETE"
        msg = (
            f"COMPLETE: {present}/{coverage['expected']} present, "
            f"{valid} valid, {generation_failed} recorded failures"
        )
    coverage["status"] = status
    coverage["message"] = msg
    return coverage


def score_empty(g_meta, g_ddl, tc, cc, reason: str) -> dict:
    rec = empty_prediction_against_gold(
        g_meta, g_ddl, table_count=tc, column_count=cc, failure_reason=reason, names_only=True
    )
    rec["failed"] = True
    rec["domain_eligible"] = False
    return rec


# --------------------------------------------------------------------------- Direct evaluation


def evaluate_direct_rschema(pred_dir: Path, logical_rows: list[dict], ddl_by_id: dict[str, dict]) -> dict:
    index = index_predictions(pred_dir)
    coverage = compute_direct_coverage(logical_rows, index)
    pred_by_id = index["pred_by_id"]
    pred_by_stem = index["pred_by_stem"]
    items: list[dict] = []
    domain_items: list[dict] = []
    failed = 0
    for idx, gold in enumerate(logical_rows):
        rid = gold["id"]
        label = f"{idx + 1:04d}"
        g_meta, g_ddl, tc, cc = gold_record_to_metadata_and_ddl(gold, legacy=False)
        failure_reason = None
        data = None
        if rid in pred_by_id:
            stem, data, _ = pred_by_id[rid]
            label = stem
            kind = classify_prediction_record(data)
            if kind == "generation_failed":
                failure_reason = data.get("error") or data.get("skip_reason") or "missing ddl"
            elif kind == "malformed":
                failure_reason = "malformed prediction"
        elif label in pred_by_stem and pred_by_stem[label][0] is None:
            failure_reason = pred_by_stem[label][1] or "unreadable prediction JSON"
        else:
            failure_reason = "missing prediction file"

        if failure_reason is not None:
            rec = score_empty(g_meta, g_ddl, tc, cc, failure_reason)
            failed += 1
        else:
            assert data is not None
            rec = evaluate_schema_pair(
                g_meta,
                g_ddl,
                data.get("metadata") or {},
                data.get("ddl") or "",
                legacy=False,
                table_count=tc,
                column_count=cc,
                names_only=True,
            )
            rec["failed"] = False
            # Override Domain with genuine DDL gold when available
            if rid in ddl_by_id and isinstance(ddl_by_id[rid].get("answer"), str) and ddl_has_genuine_types(
                ddl_by_id[rid]["answer"]
            ):
                d_meta, d_ddl, _, _ = gold_record_to_metadata_and_ddl(ddl_by_id[rid], legacy=False)
                pred_meta = ensure_prediction_metadata(
                    data.get("metadata") or {}, data.get("ddl") or "", legacy=False
                )
                dcounts = five_element_counts(
                    d_meta, d_ddl, pred_meta, data.get("ddl") or "", legacy=False
                )
                rec["domain"] = dcounts["domain"]
                rec["domain_eligible"] = True
                domain_items.append({"domain": dcounts["domain"]})
            else:
                rec["domain_eligible"] = False
        rec["id"] = rid
        # For failed cases that still have DDL gold, include zero Domain against genuine gold
        if rec.get("failed") and rid in ddl_by_id and ddl_has_genuine_types(ddl_by_id[rid].get("answer") or ""):
            d_meta, d_ddl, _, _ = gold_record_to_metadata_and_ddl(ddl_by_id[rid], legacy=False)
            dcounts = five_element_counts(d_meta, d_ddl, {}, "", legacy=False)
            rec["domain"] = dcounts["domain"]
            rec["domain_eligible"] = True
            domain_items.append({"domain": dcounts["domain"]})
        items.append(rec)

    agg = aggregate_schemas(items)
    struct = micro_struct(items)
    domain_agg = micro_aggregate(domain_items, "domain") if domain_items else micro_prf(0, 0, 0)
    ind = hall4_independent_recount(items)
    hall = agg["hallucination"]
    if abs(hall - ind["halluc"]) > 1e-12:
        raise RuntimeError(f"Hall mismatch RSchema Direct: {hall} vs {ind['halluc']}")
    return {
        "n": len(items),
        "failed": failed,
        "domain_n": len(domain_items),
        "coverage": coverage,
        "status": coverage["status"],
        "nged": agg["mean_normalized_graph_edit_distance"],
        "halluc": hall,
        "tables": struct["tables"],
        "attributes": struct["attributes"],
        "domain": float(domain_agg["f1"]),
        "entity": struct["entity"],
        "referential": struct["referential"],
        "hall_rates": ind["rates"],
        "hall_totals": ind["totals"],
        "domain_counts": {
            "gold": domain_agg["gold"],
            "recreated": domain_agg["recreated"],
            "matched": domain_agg["matched"],
        },
        "struct_counts": {d: micro_aggregate(items, d) for d in STRUCT_DIMS},
        "items": items,
    }


def evaluate_direct_schemabench(pred_dir: Path, gold_rows: list[dict]) -> dict:
    index = index_predictions(pred_dir)
    coverage = compute_direct_coverage(gold_rows, index)
    pred_by_id = index["pred_by_id"]
    pred_by_stem = index["pred_by_stem"]
    items: list[dict] = []
    failed = 0
    for idx, gold in enumerate(gold_rows):
        rid = gold["id"]
        label = f"{idx + 1:04d}"
        g_meta, g_ddl, tc, cc = gold_record_to_metadata_and_ddl(gold, legacy=False)
        failure_reason = None
        data = None
        if rid in pred_by_id:
            stem, data, _ = pred_by_id[rid]
            label = stem
            kind = classify_prediction_record(data)
            if kind == "generation_failed":
                failure_reason = data.get("error") or data.get("skip_reason") or "missing ddl"
            elif kind == "malformed":
                failure_reason = "malformed prediction"
        elif label in pred_by_stem and pred_by_stem[label][0] is None:
            failure_reason = pred_by_stem[label][1] or "unreadable prediction JSON"
        else:
            failure_reason = "missing prediction file"
        if failure_reason is not None:
            rec = score_empty(g_meta, g_ddl, tc, cc, failure_reason)
            rec["domain_eligible"] = True  # gold is typed; empty pred still in Domain cohort
            failed += 1
        else:
            assert data is not None
            rec = evaluate_schema_pair(
                g_meta,
                g_ddl,
                data.get("metadata") or {},
                data.get("ddl") or "",
                legacy=False,
                table_count=tc,
                column_count=cc,
                names_only=True,
            )
            rec["failed"] = False
            rec["domain_eligible"] = True
        rec["id"] = rid
        items.append(rec)

    agg = aggregate_schemas(items)
    fe = {d: micro_aggregate(items, d) for d in ELEMENTS}
    ind = hall4_independent_recount(items)
    hall = agg["hallucination"]
    if abs(hall - ind["halluc"]) > 1e-12:
        raise RuntimeError(f"Hall mismatch SchemaBench Direct: {hall} vs {ind['halluc']}")
    return {
        "n": len(items),
        "failed": failed,
        "domain_n": len(items),
        "coverage": coverage,
        "status": coverage["status"],
        "nged": agg["mean_normalized_graph_edit_distance"],
        "halluc": hall,
        "tables": float(fe["tables"]["f1"]),
        "attributes": float(fe["attributes"]["f1"]),
        "domain": float(fe["domain"]["f1"]),
        "entity": float(fe["entity"]["f1"]),
        "referential": float(fe["referential"]["f1"]),
        "hall_rates": ind["rates"],
        "hall_totals": ind["totals"],
        "domain_counts": {
            "gold": fe["domain"]["gold"],
            "recreated": fe["domain"]["recreated"],
            "matched": fe["domain"]["matched"],
        },
        "struct_counts": {d: fe[d] for d in STRUCT_DIMS},
        "items": items,
    }


# --------------------------------------------------------------------------- Baseline evaluation


def evaluate_baseline(
    dataset: str,
    model: str,
    method: str,
    gold_rows: list[dict],
) -> dict:
    expected_ids = {str(r["id"]) for r in gold_rows}
    bundle = load_baseline_predictions(dataset, MODEL_FILE[model], method, expected_ids=expected_ids)
    if bundle["status"] == "BLOCKED":
        return {
            "n": 0,
            "failed": 0,
            "status": "BLOCKED",
            "coverage": bundle["coverage"],
            "message": bundle["message"],
            "nged": None,
            "halluc": None,
            "tables": None,
            "attributes": None,
            "domain": None,
            "entity": None,
            "referential": None,
            "hall_rates": None,
            "hall_totals": None,
            "struct_counts": None,
            "items": [],
        }

    preds = bundle["preds"]
    items: list[dict] = []
    failed = 0
    for gold in gold_rows:
        rid = gold["id"]
        g_meta, g_ddl, tc, cc = gold_record_to_metadata_and_ddl(gold, legacy=False)
        if rid not in preds:
            rec = score_empty(g_meta, g_ddl, tc, cc, "missing prediction")
            failed += 1
        else:
            pred_answer = preds.get(rid) or {}
            if not pred_answer:
                rec = score_empty(g_meta, g_ddl, tc, cc, "recorded generation failure")
                failed += 1
            else:
                # Logical / untyped prediction → synthetic DDL for structural comparison only
                p_meta, p_ddl = gold_answer_to_metadata_and_ddl(
                    pred_answer, database=f"pred_{str(rid)[:8]}"
                )
                rec = evaluate_schema_pair(
                    g_meta,
                    g_ddl,
                    p_meta,
                    p_ddl,
                    legacy=False,
                    table_count=tc,
                    column_count=cc,
                    names_only=True,
                )
                rec["failed"] = False
        rec["id"] = rid
        rec["domain_eligible"] = False  # baselines never report Domain
        items.append(rec)

    agg = aggregate_schemas(items)
    struct = micro_struct(items)
    ind = hall4_independent_recount(items)
    hall = agg["hallucination"]
    if abs(hall - ind["halluc"]) > 1e-12:
        raise RuntimeError(f"Hall mismatch {dataset}/{model}/{method}: {hall} vs {ind['halluc']}")
    return {
        "n": len(items),
        "failed": failed,
        "status": bundle["status"],
        "coverage": bundle["coverage"],
        "message": bundle["message"],
        "nged": agg["mean_normalized_graph_edit_distance"],
        "halluc": hall,
        "tables": struct["tables"],
        "attributes": struct["attributes"],
        "domain": None,  # --
        "entity": struct["entity"],
        "referential": struct["referential"],
        "hall_rates": ind["rates"],
        "hall_totals": ind["totals"],
        "struct_counts": {d: micro_aggregate(items, d) for d in STRUCT_DIMS},
        "items": items,
    }


# --------------------------------------------------------------------------- validation sample


def validate_sample(logical_rows: list[dict], ddl_by_id: dict[str, dict]) -> list[str]:
    checks: list[str] = []
    ok = True
    rng = random.Random(SEED)
    idxs = sorted(rng.sample(range(len(logical_rows)), 10))
    pred_dir = DIRECT["RSchema"]["Llama-3.1-8B"]
    items = []
    domain_items = []
    for i in idxs:
        gold = logical_rows[i]
        rid = gold["id"]
        stem = f"{i + 1:04d}"
        g_meta, g_ddl, tc, cc = gold_record_to_metadata_and_ddl(gold, legacy=False)
        p = pred_dir / f"{stem}.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        if data.get("error") or not data.get("ddl"):
            rec = score_empty(g_meta, g_ddl, tc, cc, "empty")
        else:
            rec = evaluate_schema_pair(
                g_meta,
                g_ddl,
                data.get("metadata") or {},
                data.get("ddl") or "",
                legacy=False,
                table_count=tc,
                column_count=cc,
                names_only=True,
            )
            if rid in ddl_by_id and ddl_has_genuine_types(ddl_by_id[rid].get("answer") or ""):
                d_meta, d_ddl, _, _ = gold_record_to_metadata_and_ddl(ddl_by_id[rid], legacy=False)
                pred_meta = ensure_prediction_metadata(
                    data.get("metadata") or {}, data.get("ddl") or "", legacy=False
                )
                dcounts = five_element_counts(d_meta, d_ddl, pred_meta, data.get("ddl") or "", legacy=False)
                rec["domain"] = dcounts["domain"]
                domain_items.append({"domain": dcounts["domain"]})
        items.append(rec)

    # Independent recount of F1 for tables
    g = sum(s["tables"]["gold"] for s in items)
    p = sum(s["tables"]["recreated"] for s in items)
    m = sum(s["tables"]["matched"] for s in items)
    f1_ind = micro_f1(g, p, m)
    f1_lib = float(micro_aggregate(items, "tables")["f1"])
    if abs(f1_ind - f1_lib) > 1e-12:
        ok = False
        checks.append(f"FAIL 10-case tables F1 recount {f1_ind} vs {f1_lib}")
    else:
        checks.append(f"PASS 10-case seed42 tables F1={f1_ind:.6f} (G={g},P={p},M={m})")

    h_lib = aggregate_hallucination_micro(items)
    h_ind = hall4_independent_recount(items)["halluc"]
    if abs(h_lib - h_ind) > 1e-12:
        ok = False
        checks.append(f"FAIL 10-case Hall recount {h_lib} vs {h_ind}")
    else:
        checks.append(f"PASS 10-case seed42 Hall4={h_lib:.6f}")

    # names_only: type flip must not change nGED
    ddl_a = "CREATE TABLE t (a int NOT NULL, PRIMARY KEY (a));"
    ddl_b = "CREATE TABLE t (a varchar(255) NOT NULL, PRIMARY KEY (a));"
    ma, mb = metadata_from_ddl(ddl_a, legacy=False), metadata_from_ddl(ddl_b, legacy=False)
    from src.metrics import normalized_graph_edit_distance as nged

    if nged(ma, ddl_a, mb, ddl_b, names_only=True) != 0.0:
        ok = False
        checks.append("FAIL names_only nGED should ignore type flip")
    else:
        checks.append("PASS names_only nGED ignores type flip")
    if nged(ma, ddl_a, mb, ddl_b, names_only=False) <= 0.0:
        ok = False
        checks.append("FAIL typed nGED should see type flip")
    else:
        checks.append("PASS typed nGED sees type flip")

    # empty Hall = 0
    empty = empty_prediction_against_gold(ma, ddl_a, names_only=True)
    if empty["normalized_graph_edit_distance"] != 1.0 or aggregate_hallucination_micro([empty]) != 0.0:
        ok = False
        checks.append("FAIL empty failure policy")
    else:
        checks.append("PASS empty failure: nGED=1 Hall=0")

    checks.append("OVERALL " + ("PASS" if ok else "FAIL"))
    return checks


# --------------------------------------------------------------------------- LaTeX / CSV


def fmt_num(val: float | None, bold: bool, na: bool = False) -> str:
    if na or val is None:
        return "--"
    s = f"{val:.3f}"
    return f"\\textbf{{{s}}}" if bold else s


def build_table_v_tex(rows: list[dict]) -> str:
    lines = [
        "\\begin{table*}[t]",
        "\\centering",
        "\\small",
        "\\setlength{\\tabcolsep}{3pt}",
        "\\renewcommand{\\arraystretch}{1.0}",
        "\\caption{E0: Direct Text2Schema from gold natural-language",
        "requirements. Mean structural nGED and four-dimensional",
        "micro-aggregated hallucination (lower is better), and",
        "micro-averaged structural $F_1$ (higher is better).",
        "RSchema uses 518 logical references for structural metrics",
        "and 381 matched DDL references for Domain $F_1$.",
        "Best values per dataset and column are bold.}",
        "\\label{tab:e0_overall}",
        "",
        "\\begin{tabular*}{\\textwidth}",
        "{@{\\extracolsep{\\fill}}llccccccc@{}}",
        "\\toprule",
        "\\multirow{2}{*}{\\textbf{Dataset}}",
        "& \\multirow{2}{*}{\\textbf{Model}}",
        "& \\multirow{2}{*}{\\textbf{nGED} $\\downarrow$}",
        "& \\multirow{2}{*}{\\textbf{Hall.} $\\downarrow$}",
        "& \\multicolumn{5}{c}{\\textbf{Structural} $F_1$ $\\uparrow$} \\\\",
        "\\cmidrule(lr){5-9}",
        "& & & &",
        "\\textbf{Tables} & \\textbf{Attr.}",
        "& \\textbf{Domain} & \\textbf{Entity}",
        "& \\textbf{Ref.} \\\\",
        "\\midrule",
        "",
    ]
    by_ds = defaultdict(list)
    for r in rows:
        by_ds[r["dataset"]].append(r)
    first = True
    for ds in ["RSchema", "SchemaBench"]:
        ds_rows = by_ds[ds]
        if not ds_rows:
            continue
        best = {m: (min if m in LOWER else max)(r3(r[m]) for r in ds_rows) for m in METRICS_V}
        if not first:
            lines += ["\\midrule", ""]
        first = False
        for i, r in enumerate(ds_rows):
            cells = [ds if i == 0 else "", r["model"]]
            for m in METRICS_V:
                cells.append(fmt_num(r[m], r3(r[m]) == best[m]))
            lines.append(" & ".join(cells) + " \\\\")
        lines.append("")
    lines += ["\\bottomrule", "\\end{tabular*}", "\\end{table*}", ""]
    return "\n".join(lines)


def build_table_vi_tex(rows: list[dict]) -> str:
    lines = [
        "\\begin{table*}[t]",
        "\\centering",
        "\\scriptsize",
        "\\setlength{\\tabcolsep}{2.5pt}",
        "\\renewcommand{\\arraystretch}{1.0}",
        "\\caption{E0: Prompting baselines and Direct Text2Schema",
        "under a common evaluation protocol. Structural $F_1$",
        "is micro-averaged, while hallucination is the unweighted",
        "mean of four dimension-wise micro false-positive rates.",
        "Failed generations are evaluated as empty predictions.",
        "Domain $F_1$ is reported only where genuine typed",
        "predictions and references are available.}",
        "\\label{tab:e0_baselines}",
        "",
        "\\begin{tabular*}{\\textwidth}",
        "{@{\\extracolsep{\\fill}}lllrrccccccc@{}}",
        "\\toprule",
        "\\textbf{Dataset} & \\textbf{Method} & \\textbf{Model}",
        "& \\textbf{Eval} & \\textbf{Zero}",
        "& \\textbf{nGED}$\\downarrow$ & \\textbf{Hall.}$\\downarrow$",
        "& \\textbf{Tables} & \\textbf{Attr.} & \\textbf{Domain}",
        "& \\textbf{Entity} & \\textbf{Ref.} \\\\",
        "\\midrule",
        "",
    ]
    order_m = {"One-shot": 0, "One-shot+CoT": 1, "Few-shot": 2, "Direct": 3}
    order_model = {
        "CodeLlama-13B": 0,
        "Llama-3.1-8B": 1,
        "DeepSeek-Coder-6.7B": 2,
        "GPT-4o-mini": 3,
        "Claude Sonnet 4.6": 4,
        "GPT-5.4-mini": 5,
    }
    for ds in ["RSchema", "SchemaBench"]:
        ds_rows = [r for r in rows if r["dataset"] == ds]
        ds_rows.sort(key=lambda r: (order_m.get(r["method"], 9), order_model.get(r["model"], 9)))
        numeric_rows = ds_rows  # Domain may be None
        best: dict[str, float] = {}
        for m in METRICS_V:
            vals = [r3(r[m]) for r in numeric_rows if r.get(m) is not None]
            if not vals:
                continue
            best[m] = (min if m in LOWER else max)(vals)
        for i, r in enumerate(ds_rows):
            cells = [ds if i == 0 else "", r["method"], r["model"], str(r["eval"]), str(r["zero"])]
            for m in METRICS_V:
                na = r.get(m) is None
                bold = (not na) and m in best and r3(r[m]) == best[m]
                cells.append(fmt_num(r.get(m), bold, na=na))
            lines.append(" & ".join(cells) + " \\\\")
        if ds == "RSchema":
            lines += ["\\midrule", ""]
    lines += ["\\bottomrule", "\\end{tabular*}", "\\end{table*}", ""]
    return "\n".join(lines)


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            out = {}
            for k in fields:
                v = r.get(k)
                if isinstance(v, float):
                    out[k] = f"{v:.6f}"
                elif v is None and k == "domain":
                    out[k] = "--"
                else:
                    out[k] = v
            w.writerow(out)


def load_old_csv(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return list(csv.DictReader(path.open(encoding="utf-8")))


# --------------------------------------------------------------------------- main


def main() -> int:
    global OUT, AUDIT
    ap = argparse.ArgumentParser(
        description="Canonical E0 offline evaluator: genuine-gold Tables V and VI"
    )
    ap.add_argument("--validate-only", action="store_true", help="Gold + sample checks only")
    ap.add_argument("--skip-pytest", action="store_true", help="Skip pytest")
    ap.add_argument(
        "--include-gpt4o-mini",
        action="store_true",
        help="Also evaluate optional GPT-4o-mini Direct preds (not default Table V)",
    )
    ap.add_argument(
        "--dataset",
        choices=("rschema", "schemabench", "all"),
        default="all",
        help="Dataset scope for Tables V/VI (default: all)",
    )
    ap.add_argument(
        "--model",
        action="append",
        default=None,
        help="Filter Direct display names (repeatable); default = paper Table V set",
    )
    ap.add_argument(
        "--pred-root",
        type=Path,
        default=None,
        help="Override results/predictions/e0 root (rewrites configured Direct dirs)",
    )
    ap.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help="Override results/metrics/reproduced output directory",
    )
    ap.add_argument(
        "--audit-root",
        type=Path,
        default=None,
        help="Override audit/e0_gold_requirement_verification directory",
    )
    ap.add_argument(
        "--strict",
        action="store_true",
        help="Non-zero exit if any configured Direct prediction directory is missing/incomplete",
    )
    ap.add_argument(
        "--no-render",
        action="store_true",
        help="Skip printing Table V/VI rows to stdout (files still written)",
    )
    ap.add_argument(
        "--write-gpm",
        action="store_true",
        help="Write independent G/P/M count CSV under the audit root",
    )
    args = ap.parse_args()
    if args.include_gpt4o_mini:
        for ds, models in OPTIONAL_DIRECT.items():
            DIRECT.setdefault(ds, {}).update(models)

    if args.pred_root is not None:
        pred_root = args.pred_root if args.pred_root.is_absolute() else (ROOT / args.pred_root)
        for ds_key, models in list(DIRECT.items()):
            for model, pred_dir in list(models.items()):
                DIRECT[ds_key][model] = pred_root / pred_dir.name
        for ds_key, models in list(OPTIONAL_DIRECT.items()):
            for model, pred_dir in list(models.items()):
                OPTIONAL_DIRECT[ds_key][model] = pred_root / pred_dir.name
        for ds_key, base in list(BASELINE_ROOT.items()):
            BASELINE_ROOT[ds_key] = pred_root / base.name

    if args.output_root is not None:
        OUT = args.output_root if args.output_root.is_absolute() else (ROOT / args.output_root)
    if args.audit_root is not None:
        AUDIT = args.audit_root if args.audit_root.is_absolute() else (ROOT / args.audit_root)

    datasets_wanted = {"RSchema", "SchemaBench"}
    if args.dataset == "rschema":
        datasets_wanted = {"RSchema"}
    elif args.dataset == "schemabench":
        datasets_wanted = {"SchemaBench"}

    model_filter = set(args.model) if args.model else None

    OUT.mkdir(parents=True, exist_ok=True)
    AUDIT.mkdir(parents=True, exist_ok=True)
    incomplete: list[str] = []
    blocked: list[str] = []
    coverage_rows: list[dict[str, Any]] = []

    print(f"[{utcnow()}] Verifying gold references...", flush=True)
    gold_info = verify_gold_refs()
    for k, v in gold_info.items():
        print(f"  {k}: {v}", flush=True)

    logical_rows = load_jsonl(GOLD_LOGICAL["RSchema"])
    ddl_rows = load_jsonl(GOLD_DDL["RSchema"])
    ddl_by_id = {r["id"]: r for r in ddl_rows}
    sb_rows = load_jsonl(GOLD_DDL["SchemaBench"])

    print(f"[{utcnow()}] Domain column reconciliation...", flush=True)
    recon = write_domain_column_reconciliation(ddl_rows, AUDIT / "E0_DOMAIN_COLUMN_RECONCILIATION.csv")
    gold_info["domain_reconciliation"] = recon
    for k, v in recon.items():
        print(f"  {k}: {v}", flush=True)

    print(f"[{utcnow()}] 10-schema validation (seed={SEED})...", flush=True)
    checks = validate_sample(logical_rows, ddl_by_id)
    for c in checks:
        print(" ", c, flush=True)
    if checks[-1] != "OVERALL PASS":
        return 2
    if args.validate_only:
        return 0

    if args.skip_pytest:
        pytest_rc = 0
        pytest_passed = "Tests skipped for this run."
        print(f"[{utcnow()}] {pytest_passed}", flush=True)
    else:
        print(f"[{utcnow()}] pytest (full suite required)...", flush=True)
        rc = subprocess.call([sys.executable, "-m", "pytest", "-q"], cwd=str(ROOT))
        pytest_rc = rc
        if rc != 0:
            print(
                "Full pytest FAILED — refusing to report final verification as PASS.",
                file=sys.stderr,
                flush=True,
            )
            return rc
        pytest_passed = f"full suite passed (exit={rc})"

    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:  # noqa: BLE001
        commit = "unknown"

    # ---- Table V
    print(f"[{utcnow()}] Table V Direct...", flush=True)
    tv_rows = []
    tv_detail = {}
    gpm_rows: list[dict[str, Any]] = []
    for model, pred_dir in DIRECT["RSchema"].items():
        if "RSchema" not in datasets_wanted:
            break
        if model_filter is not None and model not in model_filter:
            continue
        print(f"  RSchema / {model}", flush=True)
        if not pred_dir.is_dir():
            print(f"    SKIP missing pred dir: {pred_dir}", flush=True)
            incomplete.append(f"RSchema/{model}: missing {pred_dir}")
            continue
        res = evaluate_direct_rschema(pred_dir, logical_rows, ddl_by_id)
        cov = res.get("coverage") or {}
        coverage_rows.append({"dataset": "RSchema", "model": model, "method": "Direct", **cov})
        print(f"    {cov.get('message') or res.get('status')}", flush=True)
        if res.get("status") in ("INCOMPLETE", "INVALID"):
            incomplete.append(f"RSchema/{model}: {cov.get('message') or res.get('status')}")
        row = {
            "dataset": "RSchema",
            "model": model,
            "n": res["n"],
            "failed": res["failed"],
            "domain_n": res["domain_n"],
            "status": res.get("status"),
            "present": cov.get("present"),
            "valid": cov.get("valid"),
            "missing": cov.get("missing"),
            "nged": res["nged"],
            "halluc": res["halluc"],
            "tables": res["tables"],
            "attributes": res["attributes"],
            "domain": res["domain"],
            "entity": res["entity"],
            "referential": res["referential"],
        }
        tv_rows.append(row)
        tv_detail[("RSchema", model)] = {k: v for k, v in res.items() if k != "items"}
        if args.write_gpm:
            for dim, agg in res.get("struct_counts", {}).items():
                gpm_rows.append(
                    {
                        "dataset": "RSchema",
                        "model": model,
                        "method": "Direct",
                        "dimension": dim,
                        "G": agg["gold"],
                        "P": agg["recreated"],
                        "M": agg["matched"],
                        "n": res["n"],
                        "failed": res["failed"],
                        "F1": agg["f1"],
                    }
                )
            dc = res.get("domain_counts") or {}
            gpm_rows.append(
                {
                    "dataset": "RSchema",
                    "model": model,
                    "method": "Direct",
                    "dimension": "domain",
                    "G": dc.get("gold"),
                    "P": dc.get("recreated"),
                    "M": dc.get("matched"),
                    "n": res["n"],
                    "failed": res["failed"],
                    "F1": res["domain"],
                }
            )
        print(
            f"    n={row['n']} failed={row['failed']} domain_n={row['domain_n']} "
            f"nGED={row['nged']:.4f} Hall={row['halluc']:.4f} DomF1={row['domain']:.4f}",
            flush=True,
        )
        # drop items to save memory after recount already done
        res.pop("items", None)

    for model, pred_dir in DIRECT["SchemaBench"].items():
        if "SchemaBench" not in datasets_wanted:
            break
        if model_filter is not None and model not in model_filter:
            continue
        print(f"  SchemaBench / {model}", flush=True)
        if not pred_dir.is_dir():
            print(f"    SKIP missing pred dir: {pred_dir}", flush=True)
            incomplete.append(f"SchemaBench/{model}: missing {pred_dir}")
            continue
        res = evaluate_direct_schemabench(pred_dir, sb_rows)
        cov = res.get("coverage") or {}
        coverage_rows.append({"dataset": "SchemaBench", "model": model, "method": "Direct", **cov})
        print(f"    {cov.get('message') or res.get('status')}", flush=True)
        if res.get("status") in ("INCOMPLETE", "INVALID"):
            incomplete.append(f"SchemaBench/{model}: {cov.get('message') or res.get('status')}")
        row = {
            "dataset": "SchemaBench",
            "model": model,
            "n": res["n"],
            "failed": res["failed"],
            "domain_n": res["domain_n"],
            "status": res.get("status"),
            "present": cov.get("present"),
            "valid": cov.get("valid"),
            "missing": cov.get("missing"),
            "nged": res["nged"],
            "halluc": res["halluc"],
            "tables": res["tables"],
            "attributes": res["attributes"],
            "domain": res["domain"],
            "entity": res["entity"],
            "referential": res["referential"],
        }
        tv_rows.append(row)
        tv_detail[("SchemaBench", model)] = {k: v for k, v in res.items() if k != "items"}
        if args.write_gpm:
            for dim, agg in res.get("struct_counts", {}).items():
                gpm_rows.append(
                    {
                        "dataset": "SchemaBench",
                        "model": model,
                        "method": "Direct",
                        "dimension": dim,
                        "G": agg["gold"],
                        "P": agg["recreated"],
                        "M": agg["matched"],
                        "n": res["n"],
                        "failed": res["failed"],
                        "F1": agg["f1"],
                    }
                )
            dc = res.get("domain_counts") or {}
            gpm_rows.append(
                {
                    "dataset": "SchemaBench",
                    "model": model,
                    "method": "Direct",
                    "dimension": "domain",
                    "G": dc.get("gold"),
                    "P": dc.get("recreated"),
                    "M": dc.get("matched"),
                    "n": res["n"],
                    "failed": res["failed"],
                    "F1": res["domain"],
                }
            )
        print(
            f"    n={row['n']} failed={row['failed']} "
            f"nGED={row['nged']:.4f} Hall={row['halluc']:.4f} DomF1={row['domain']:.4f}",
            flush=True,
        )
        res.pop("items", None)

    # ---- Table VI
    print(f"[{utcnow()}] Table VI baselines...", flush=True)
    tvi_rows = []
    for ds, gold_rows in (("RSchema", logical_rows), ("SchemaBench", sb_rows)):
        if ds not in datasets_wanted:
            continue
        for method in METHODS:
            for model in MODEL_FILE:
                if model_filter is not None and model not in model_filter:
                    continue
                print(f"  {ds} / {METHOD_LABEL[method]} / {model}", flush=True)
                res = evaluate_baseline(ds, model, method, gold_rows)
                cov = res.get("coverage") or {}
                coverage_rows.append(
                    {
                        "dataset": ds,
                        "model": model,
                        "method": METHOD_LABEL[method],
                        **{k: v for k, v in cov.items() if k != "duplicate_id_list"},
                        "status": res.get("status"),
                        "message": res.get("message"),
                    }
                )
                print(f"    {res.get('message') or res.get('status')}", flush=True)
                if res.get("status") == "BLOCKED":
                    blocked.append(f"{ds}/{METHOD_LABEL[method]}/{model}: {res.get('message')}")
                    tvi_rows.append(
                        {
                            "dataset": ds,
                            "method": METHOD_LABEL[method],
                            "model": model,
                            "eval": 0,
                            "zero": 0,
                            "status": "BLOCKED",
                            "nged": None,
                            "halluc": None,
                            "tables": None,
                            "attributes": None,
                            "domain": None,
                            "entity": None,
                            "referential": None,
                        }
                    )
                    continue
                if res.get("status") in ("INCOMPLETE", "INVALID"):
                    incomplete.append(
                        f"{ds}/{METHOD_LABEL[method]}/{model}: {res.get('message') or res.get('status')}"
                    )
                tvi_rows.append(
                    {
                        "dataset": ds,
                        "method": METHOD_LABEL[method],
                        "model": model,
                        "eval": res["n"],
                        "zero": res["failed"],
                        "status": res.get("status"),
                        "nged": res["nged"],
                        "halluc": res["halluc"],
                        "tables": res["tables"],
                        "attributes": res["attributes"],
                        "domain": None,
                        "entity": res["entity"],
                        "referential": res["referential"],
                        "_struct_counts": res.get("struct_counts"),
                        "_hall_rates": res.get("hall_rates"),
                        "_hall_totals": res.get("hall_totals"),
                    }
                )
                print(
                    f"    Eval={res['n']} Zero={res['failed']} "
                    f"nGED={res['nged']:.4f} Hall={res['halluc']:.4f}",
                    flush=True,
                )
                res.pop("items", None)
        # Direct rows from Table V
        for r in tv_rows:
            if r["dataset"] != ds:
                continue
            tvi_rows.append(
                {
                    "dataset": ds,
                    "method": "Direct",
                    "model": r["model"],
                    "eval": r["n"],
                    "zero": r["failed"],
                    "status": r.get("status"),
                    "nged": r["nged"],
                    "halluc": r["halluc"],
                    "tables": r["tables"],
                    "attributes": r["attributes"],
                    "domain": r["domain"],
                    "entity": r["entity"],
                    "referential": r["referential"],
                }
            )

    # Direct consistency
    consistency = []
    for r in tv_rows:
        vi = next(
            x
            for x in tvi_rows
            if x["dataset"] == r["dataset"] and x["model"] == r["model"] and x["method"] == "Direct"
        )
        equal = all(
            r[m] == vi[m] for m in ("nged", "halluc", "tables", "attributes", "domain", "entity", "referential")
        ) and r["n"] == vi["eval"] and r["failed"] == vi["zero"]
        consistency.append(
            {
                "dataset": r["dataset"],
                "model": r["model"],
                "equal": equal,
            }
        )
        if not equal:
            raise RuntimeError(f"Direct V/VI mismatch {r['dataset']}/{r['model']}")
        print(f"  Direct match OK: {r['dataset']}/{r['model']}", flush=True)

    # Write FINAL outputs (preserve prior GENUINE / HALL4 archives untouched)
    write_csv(
        OUT / "E0_TABLE_V_FINAL.csv",
        tv_rows,
        [
            "dataset",
            "model",
            "n",
            "failed",
            "domain_n",
            "status",
            "present",
            "valid",
            "missing",
            *METRICS_V,
        ],
    )
    (OUT / "E0_TABLE_V_FINAL.tex").write_text(build_table_v_tex(tv_rows), encoding="utf-8")
    (OUT / "E0_TABLE_V_FINAL.json").write_text(
        json.dumps(
            {
                "protocol": {
                    "rschema_structural_n": 518,
                    "rschema_domain_n": 381,
                    "schemabench_n": 239,
                    "hallucination": "4-dim micro mean T/A/E/R",
                    "nged": "names_only=True (tables + attribute names + FK edges)",
                    "legacy": False,
                    "sql_dialect_nullability": "MySQL: bare columns nullable; NOT NULL / inline PK -> NO",
                    "failure_policy": "empty prediction; nGED=1; Hall not forced to 1",
                },
                "commit": commit,
                "gold_verification": gold_info,
                "rows": tv_rows,
                "detail": {f"{a}/{b}": d for (a, b), d in tv_detail.items()},
            },
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    write_csv(
        OUT / "E0_TABLE_VI_FINAL.csv",
        tvi_rows,
        ["dataset", "method", "model", "eval", "zero", "status", *METRICS_V],
    )
    (OUT / "E0_TABLE_VI_FINAL.tex").write_text(build_table_vi_tex(tvi_rows), encoding="utf-8")
    (OUT / "E0_TABLE_VI_FINAL.json").write_text(
        json.dumps(
            {
                "protocol": {
                    "baseline_domain": "-- (untyped logical predictions)",
                    "direct_rows": "copied from Table V FINAL",
                    "f1": "micro",
                    "hallucination": "4-dim micro mean T/A/E/R",
                    "nged": "names_only=True",
                },
                "commit": commit,
                "rows": tvi_rows,
                "direct_consistency": consistency,
            },
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    # Old (pre-parser-fix GENUINE) vs FINAL
    old_v = load_old_csv(OLD_GENUINE_V) or load_old_csv(OLD_HALL4_V)
    old_vi = load_old_csv(OLD_GENUINE_VI) or load_old_csv(OLD_HALL4_VI)
    cmp_rows = []
    for r in tv_rows:
        old = next((o for o in old_v if o.get("dataset") == r["dataset"] and o.get("model") == r["model"]), None)
        cmp_rows.append(
            {
                "table": "V",
                "dataset": r["dataset"],
                "method": "Direct",
                "model": r["model"],
                "old_nged": old.get("nged") if old else "",
                "new_nged": f"{r['nged']:.6f}",
                "old_hall": old.get("halluc") if old else "",
                "new_hall": f"{r['halluc']:.6f}",
                "old_tables": old.get("tables") if old else "",
                "new_tables": f"{r['tables']:.6f}",
                "old_attributes": old.get("attributes") if old else "",
                "new_attributes": f"{r['attributes']:.6f}",
                "old_domain": old.get("domain") if old else "",
                "new_domain": f"{r['domain']:.6f}",
                "old_entity": old.get("entity") if old else "",
                "new_entity": f"{r['entity']:.6f}",
                "old_referential": old.get("referential") if old else "",
                "new_referential": f"{r['referential']:.6f}",
            }
        )
    for r in tvi_rows:
        if r["method"] == "Direct":
            continue
        # Skip BLOCKED / incomplete baseline rows (missing predictions → null metrics).
        if r.get("nged") is None or r.get("status") == "BLOCKED":
            cmp_rows.append(
                {
                    "table": "VI",
                    "dataset": r["dataset"],
                    "method": r["method"],
                    "model": r["model"],
                    "old_nged": "",
                    "new_nged": "",
                    "old_hall": "",
                    "new_hall": "",
                    "old_tables": "",
                    "new_tables": "",
                    "old_attributes": "",
                    "new_attributes": "",
                    "old_domain": "",
                    "new_domain": "--",
                    "old_entity": "",
                    "new_entity": "",
                    "old_referential": "",
                    "new_referential": "",
                    "status": r.get("status") or "BLOCKED",
                }
            )
            continue
        old = next(
            (
                o
                for o in old_vi
                if o.get("dataset") == r["dataset"]
                and o.get("method") == r["method"]
                and o.get("model") == r["model"]
            ),
            None,
        )
        cmp_rows.append(
            {
                "table": "VI",
                "dataset": r["dataset"],
                "method": r["method"],
                "model": r["model"],
                "old_nged": old.get("nged") if old else "",
                "new_nged": f"{r['nged']:.6f}",
                "old_hall": old.get("halluc") if old else "",
                "new_hall": f"{r['halluc']:.6f}",
                "old_tables": old.get("tables") if old else "",
                "new_tables": f"{r['tables']:.6f}",
                "old_attributes": old.get("attributes") if old else "",
                "new_attributes": f"{r['attributes']:.6f}",
                "old_domain": old.get("domain") if old else "",
                "new_domain": "--",
                "old_entity": old.get("entity") if old else "",
                "new_entity": f"{r['entity']:.6f}",
                "old_referential": old.get("referential") if old else "",
                "new_referential": f"{r['referential']:.6f}",
            }
        )
    write_csv(
        AUDIT / "E0_OLD_VS_FINAL.csv",
        cmp_rows,
        [
            "table",
            "dataset",
            "method",
            "model",
            "old_nged",
            "new_nged",
            "old_hall",
            "new_hall",
            "old_tables",
            "new_tables",
            "old_attributes",
            "new_attributes",
            "old_domain",
            "new_domain",
            "old_entity",
            "new_entity",
            "old_referential",
            "new_referential",
        ],
    )

    # Verification markdown
    md: list[str] = []
    md.append("# E0 Final Parser Verification")
    md.append("")
    md.append(f"- Commit: `{commit}`")
    md.append(f"- Finished: `{utcnow()}`")
    md.append("- Command: `python3 experiments/E0/reproduce_genuine_tables.py`")
    md.append("- No LLM / API calls.")
    md.append("")
    md.append("## Parser corrections")
    md.append("")
    md.append("- Extended `_ROBUST_TYPE_RE` (blob/json/enum/binary/text variants); never invent VARCHAR for unknowns.")
    md.append("- Lenient identifiers: `-`, `/`, mid-word `'` recovered; apostrophe no longer swallows following columns.")
    md.append("- MySQL nullability: bare → YES (`dialect_default`); NOT NULL / inline PK → NO; unsupported type → unknown.")
    md.append(
        "- Domain denominators count only columns with recognised type "
        "(`TYPE_STATUS=ok`) **and** known nullability."
    )
    md.append("")
    md.append("## Gold references")
    md.append("")
    for k, v in gold_info.items():
        md.append(f"- `{k}`: {v}")
    md.append("")
    md.append("## Validation")
    md.append("")
    for c in checks:
        md.append(f"- {c}")
    md.append(f"- pytest: `{pytest_passed}` (exit={pytest_rc})")
    md.append("")
    md.append("## Prediction coverage")
    md.append("")
    md.append(
        "| Dataset | Model/Method | Status | Expected | Present | Valid | GenFail | Missing | Dup | Unexpected |"
    )
    md.append("|---|---|---|---:|---:|---:|---:|---:|---:|---:|")
    for c in coverage_rows:
        md.append(
            f"| {c.get('dataset')} | {c.get('model')}/{c.get('method')} | {c.get('status')} | "
            f"{c.get('expected')} | {c.get('present')} | {c.get('valid')} | "
            f"{c.get('generation_failed')} | {c.get('missing')} | "
            f"{c.get('duplicate_ids')} | {c.get('unexpected_ids')} |"
        )
    md.append("")
    md.append("## Table V")
    md.append("")
    md.append(
        "| Dataset | Model | Status | Present | Eval | Zero | Domain_n | nGED | Hall | "
        "Tables | Attr | Domain | Entity | Ref |"
    )
    md.append("|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in tv_rows:
        md.append(
            f"| {r['dataset']} | {r['model']} | {r.get('status')} | {r.get('present')} | "
            f"{r['n']} | {r['failed']} | {r['domain_n']} | "
            f"{r['nged']:.3f} | {r['halluc']:.3f} | {r['tables']:.3f} | {r['attributes']:.3f} | "
            f"{r['domain']:.3f} | {r['entity']:.3f} | {r['referential']:.3f} |"
        )
    md.append("")
    md.append("## Table VI")
    md.append("")
    md.append(
        "| Dataset | Method | Model | Status | Eval | Zero | nGED | Hall | "
        "Tables | Attr | Domain | Entity | Ref |"
    )
    md.append("|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|")
    for r in tvi_rows:
        if r.get("status") == "BLOCKED" or r.get("nged") is None:
            md.append(
                f"| {r['dataset']} | {r['method']} | {r['model']} | {r.get('status')} | "
                f"{r['eval']} | {r['zero']} | -- | -- | -- | -- | -- | -- | -- |"
            )
            continue
        dom = "--" if r["domain"] is None else f"{r['domain']:.3f}"
        md.append(
            f"| {r['dataset']} | {r['method']} | {r['model']} | {r.get('status')} | "
            f"{r['eval']} | {r['zero']} | "
            f"{r['nged']:.3f} | {r['halluc']:.3f} | {r['tables']:.3f} | {r['attributes']:.3f} | "
            f"{dom} | {r['entity']:.3f} | {r['referential']:.3f} |"
        )
    md.append("")
    md.append("## Direct V↔VI consistency")
    md.append("")
    for c in consistency:
        md.append(f"- {c['dataset']} / {c['model']}: equal={c['equal']}")
    md.append("")
    md.append("## Unsupported")
    md.append("")
    md.append("- Default Table V: open-weight trio + Claude Sonnet 4.6 + GPT-5.4-mini (missing prediction dirs skipped).")
    md.append("- GPT-4o-mini: optional via `--include-gpt4o-mini` only (not default paper Table V).")
    md.append("- Never substitute `configs/paper_reference_values.json` for missing predictions.")
    md.append("- PaperMethods Domain F1: untyped logical outputs → reported as `--`.")
    md.append("- Domain eligibility is computed from gold DDL; do not hardcode denominators.")
    md.append("")
    md.append("## Outputs")
    md.append("")
    md.append("- `results/metrics/reproduced/E0_TABLE_V_FINAL.{csv,json,tex}`")
    md.append("- `results/metrics/reproduced/E0_TABLE_VI_FINAL.{csv,json,tex}`")
    md.append("- `audit/e0_gold_requirement_verification/E0_FINAL_PARSER_VERIFICATION.md`")
    md.append("- `audit/e0_gold_requirement_verification/E0_DOMAIN_COLUMN_RECONCILIATION.csv`")
    md.append("- `audit/e0_gold_requirement_verification/E0_OLD_VS_FINAL.csv`")
    (AUDIT / "E0_FINAL_PARSER_VERIFICATION.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    if args.write_gpm and gpm_rows:
        write_csv(
            AUDIT / "E0_GPM_COUNTS.csv",
            gpm_rows,
            ["dataset", "model", "method", "dimension", "G", "P", "M", "n", "failed", "F1"],
        )
        print(f"[{utcnow()}] Wrote G/P/M counts -> {AUDIT / 'E0_GPM_COUNTS.csv'}", flush=True)

    if coverage_rows:
        write_csv(
            AUDIT / "E0_PREDICTION_COVERAGE.csv",
            coverage_rows,
            [
                "dataset",
                "model",
                "method",
                "status",
                "expected",
                "present",
                "valid",
                "generation_failed",
                "malformed",
                "missing",
                "duplicate_ids",
                "unexpected_ids",
                "message",
            ],
        )

    print(f"[{utcnow()}] Wrote FINAL tables + verification.", flush=True)
    if blocked:
        print(f"[{utcnow()}] Blocked baselines ({len(blocked)}):", flush=True)
        for msg in blocked:
            print(f"  - {msg}", flush=True)
    if incomplete:
        print(f"[{utcnow()}] Incomplete/invalid coverage ({len(incomplete)}):", flush=True)
        for msg in incomplete:
            print(f"  - {msg}", flush=True)
    if blocked and not incomplete:
        status = "BLOCKED"
    elif incomplete:
        status = "INCOMPLETE"
    else:
        status = "COMPLETE"
    print(f"[{utcnow()}] Experiment status: {status}", flush=True)

    if not args.no_render:
        print("\n===== TABLE V =====", flush=True)
        for r in tv_rows:
            print(
                f"{r['dataset']:12} {r['model']:22} {str(r.get('status') or ''):12} "
                f"present={r.get('present')}/{r.get('n')} "
                f"nGED={r['nged']:.3f} Hall={r['halluc']:.3f} "
                f"T={r['tables']:.3f} A={r['attributes']:.3f} D={r['domain']:.3f} "
                f"E={r['entity']:.3f} R={r['referential']:.3f}",
                flush=True,
            )
        print("\n===== TABLE VI =====", flush=True)
        for r in tvi_rows:
            if r.get("status") == "BLOCKED" or r.get("nged") is None:
                print(
                    f"{r['dataset']:12} {r['method']:12} {r['model']:22} "
                    f"status=BLOCKED (no fabricated metrics)",
                    flush=True,
                )
                continue
            dom = "--" if r["domain"] is None else f"{r['domain']:.3f}"
            print(
                f"{r['dataset']:12} {r['method']:12} {r['model']:22} "
                f"{str(r.get('status') or ''):12} "
                f"Eval={r['eval']:3} Zero={r['zero']:3} "
                f"nGED={r['nged']:.3f} Hall={r['halluc']:.3f} "
                f"T={r['tables']:.3f} A={r['attributes']:.3f} D={dom} "
                f"E={r['entity']:.3f} R={r['referential']:.3f}",
                flush=True,
            )
    if args.strict and (incomplete or blocked):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
