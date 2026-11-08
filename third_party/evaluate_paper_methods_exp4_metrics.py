#!/usr/bin/env python3
"""
Evaluate LLM4DBdesign PaperMethods outputs with the exact Exp4 Text2Schema metrics:
  nGED, Hallucination, Tables/Attributes/Domain/Entity/Referential F1

Reuses RSchema_ExpResults4/Code/evaluate_exp4_text2schema.py helpers unchanged.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

DATA_ROOT = Path("/mnt/text2er-data")
if not DATA_ROOT.is_dir():
    DATA_ROOT = Path("/data")

sys.path.insert(0, str(DATA_ROOT / "Text2ER"))
sys.path.insert(0, str(DATA_ROOT / "Results" / "Text2Schema2Results"))
sys.path.insert(0, str(DATA_ROOT / "RSchemaCode"))
sys.path.insert(0, str(DATA_ROOT / "RSchema_ExpResults4" / "Code"))

import evaluate_text2schema2 as ev  # noqa: E402
import evaluate_exp4_text2schema as exp4  # noqa: E402
from evaluate_rschema_predictions import (  # noqa: E402
    gold_answer_to_metadata_and_ddl,
    load_jsonl,
    normalize_rschema_name,
)

PAPER_ROOT = DATA_ROOT / "LLM4DBdesign_PaperMethods"
GOLD_PATH = DATA_ROOT / "LLM4DBdesign-main" / "datasets" / "RSchema" / "annotation.jsonl"
if not GOLD_PATH.is_file():
    GOLD_PATH = DATA_ROOT / "RSchema" / "annotation.jsonl"
OUT_DIR = PAPER_ROOT / "Results"

MODELS = ["codellama13b", "llama31", "deepseek"]
METHODS = ["one_shot", "one_shot_cot", "few_shot", "schema_agent"]

METHOD_LABEL = {
    "one_shot": "one_shot",
    "one_shot_cot": "CoT",
    "few_shot": "few_shot",
    "schema_agent": "schema_agent",
}
MODEL_LABEL = {
    "codellama13b": "CodeLlama",
    "llama31": "Llama",
    "deepseek": "DeepSeek",
}


def _as_attr_list(attrs) -> list:
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


def _get_pk(tdef: dict) -> list:
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
    out = {"Attributes": _as_attr_list(attrs), "Primary key": _get_pk(tdef)}
    fk = _get_fk(tdef)
    if fk:
        out["Foreign key"] = fk
    return out


def _entity_set_to_logical(payload: dict) -> dict:
    """Best-effort conceptual ER -> relational schema for metric evaluation."""
    entity_key = next((k for k in payload if "Entity Set" in k), None)
    rel_key = next((k for k in payload if "Relationship Set" in k), None)
    entities = payload.get(entity_key) if entity_key else {}
    rels = payload.get(rel_key) if rel_key else {}
    if not isinstance(entities, dict):
        return {}

    tables: dict = {}
    for ename, eattrs in entities.items():
        attrs = _as_attr_list(eattrs if not isinstance(eattrs, dict) else eattrs.get("Attributes", eattrs))
        pk = []
        if isinstance(eattrs, dict):
            pk = _get_pk(eattrs)
            if not attrs:
                attrs = _as_attr_list(eattrs.get("Attributes") or eattrs.get("Attribute"))
        if not pk and attrs:
            # heuristic: first attr containing id/number, else first attr
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
                rdef.get("Relationship Attribute")
                or rdef.get("Attributes")
                or rdef.get("Attribute")
                or []
            )
            if not isinstance(objs, list) or len(objs) < 2:
                continue
            a, b = str(objs[0]), str(objs[1])
            a_pk = (tables.get(a) or {}).get("Primary key") or []
            b_pk = (tables.get(b) or {}).get("Primary key") or []
            if "many-to-many" in card or "many to many" in card:
                cols = []
                fks = {}
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
                # many-to-one / one-to-many: put FK on the many side when detectable
                many = a
                one = b
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

    # drop empty FK dicts
    for tdef in tables.values():
        if not tdef.get("Foreign key"):
            tdef.pop("Foreign key", None)
    return tables


def normalize_prediction_answer(answer) -> dict:
    """Normalize paper/agent answer into gold-style {table: {Attributes, Primary key, Foreign key}}."""
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


def load_method_predictions(model: str, method: str) -> dict[str, dict]:
    """id -> normalized answer dict (possibly empty)."""
    out: dict[str, dict] = {}
    d = PAPER_ROOT / model / method

    if method == "schema_agent":
        agent_json = d / f"agent_chat_{model}_RSchema.json"
        if agent_json.is_file():
            data = json.loads(agent_json.read_text(encoding="utf-8"))
            for r in data.get("records") or []:
                rid = r.get("id")
                if not rid:
                    continue
                schema = r.get("schema")
                if schema is None and r.get("answer") is not None:
                    schema = r.get("answer")
                out[rid] = normalize_prediction_answer(schema)
        # merge jsonl extras if present
        agent_jsonl = d / f"agent_chat_{model}_RSchema.jsonl"
        if agent_jsonl.is_file():
            for line in agent_jsonl.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                r = json.loads(line)
                rid = r.get("id")
                if not rid:
                    continue
                schema = r.get("schema") or r.get("answer")
                if schema and (rid not in out or not out[rid]):
                    out[rid] = normalize_prediction_answer(schema)
        return out

    jsonl = d / "results.jsonl"
    if not jsonl.is_file():
        return out
    for line in jsonl.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        rid = r.get("id")
        if not rid:
            continue
        out[rid] = normalize_prediction_answer(r.get("answer"))
    return out


def _f1_counts(gold: int, recreated: int, matched: int) -> float:
    prec = matched / recreated if recreated else 0.0
    rec = matched / gold if gold else 0.0
    return 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0


def _gold_element_counts(answer: dict) -> dict[str, dict]:
    """Gold-side counts for a failed/empty prediction (recreated=matched=0)."""
    tables = 0
    attrs = 0
    entity = 0
    referential = 0
    for tdef in answer.values():
        if not isinstance(tdef, dict):
            continue
        tables += 1
        attrs += len(tdef.get("Attributes") or [])
        pk = tdef.get("Primary key") or []
        if pk:
            entity += 1
        fks = tdef.get("Foreign key") or {}
        if isinstance(fks, dict):
            referential += len(fks)
    return {
        "tables": {"gold": tables, "recreated": 0, "matched": 0},
        "attributes": {"gold": attrs, "recreated": 0, "matched": 0},
        "domain": {"gold": attrs, "recreated": 0, "matched": 0},
        "entity": {"gold": entity, "recreated": 0, "matched": 0},
        "referential": {"gold": referential, "recreated": 0, "matched": 0},
    }


def _zero_failed_row(rid: str, label: str, answer: dict, difficulty: str) -> dict:
    """
    Failed / missing / empty prediction scored as zero credit:
      F1 dimensions → 0; nGED → 1.0 (worst); Hallucination → 1.0 (worst).
    """
    per = _gold_element_counts(answer)
    return {
        "id": rid,
        "llm": label,
        **per,
        "exact_match": False,
        "normalized_graph_edit_distance": 1.0,
        "hallucination_rate_by_dimension": {k: 1.0 for k, _ in exp4.FIVE_ELEMENT_NAMES},
        "per_schema_f1": {k: 0.0 for k, _ in exp4.FIVE_ELEMENT_NAMES},
        "per_schema_hallucination": 1.0,
        "difficulty": difficulty,
        "scored_as_zero": True,
        "zero_reason": "missing or empty prediction",
    }


def evaluate_method(model: str, method: str, gold_by_id: dict[str, dict]) -> dict:
    ev.normalize_name = normalize_rschema_name
    preds = load_method_predictions(model, method)
    results_by_schema: dict[str, dict] = {}
    scored_zero = 0
    label = f"{model}/{method}"

    # Evaluate full gold set. Failed/unrun cases are scored as zero (included in means).
    for idx, (rid, gold_rec) in enumerate(sorted(gold_by_id.items(), key=lambda x: x[0]), start=1):
        stem = f"{idx:04d}"
        answer = gold_rec.get("answer") or {}
        table_count, column_count = 0, 0
        for tdef in answer.values():
            if isinstance(tdef, dict):
                table_count += 1
                column_count += len(tdef.get("Attributes") or [])
        difficulty = (
            "easy"
            if table_count <= 3 and column_count <= 30
            else "medium"
            if table_count <= 15 and column_count <= 150
            else "hard"
        )

        pred_answer = preds.get(rid) or {}
        if not pred_answer:
            results_by_schema[stem] = _zero_failed_row(rid, label, answer, difficulty)
            scored_zero += 1
            continue

        orig_meta, orig_ddl = gold_answer_to_metadata_and_ddl(answer, database=f"gold_{rid[:8]}")
        pred_meta, pred_ddl = gold_answer_to_metadata_and_ddl(
            pred_answer, database=f"pred_{rid[:8]}"
        )

        m = ev.evaluate_one(
            stem,
            orig_meta,
            orig_ddl,
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
        nged = exp4.normalized_graph_edit_distance(orig_meta, orig_ddl, pred_meta, pred_ddl)
        hall = {}
        for dim, row in per.items():
            r, h = row["recreated"], max(0, row["recreated"] - row["matched"])
            hall[dim] = h / r if r else 0.0
        per_f1 = {
            k: _f1_counts(per[k]["gold"], per[k]["recreated"], per[k]["matched"])
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

    # All gold IDs are included (failed scored as zero).
    all_items = list(results_by_schema.values())
    n = len(all_items)
    five_elements_micro = {k: exp4.agg_element(all_items, k) for k, _ in exp4.FIVE_ELEMENT_NAMES}

    # Reported table metrics = macro mean over all gold schemas (zeros included).
    mean_nged = (
        sum(s["normalized_graph_edit_distance"] for s in all_items) / n if n else 0.0
    )
    mean_hall = sum(s.get("per_schema_hallucination", 0.0) for s in all_items) / n if n else 0.0
    five_elements = {}
    for k, _ in exp4.FIVE_ELEMENT_NAMES:
        macro_f1 = (
            sum((s.get("per_schema_f1") or {}).get(k, 0.0) for s in all_items) / n if n else 0.0
        )
        row = dict(five_elements_micro[k])
        row["f1"] = macro_f1
        row["f1_micro"] = five_elements_micro[k]["f1"]
        row["aggregation"] = "macro_mean_over_all_gold_failed_as_zero"
        five_elements[k] = row

    exact_matches = sum(1 for s in all_items if s.get("exact_match"))

    by_difficulty_count = {"easy": 0, "medium": 0, "hard": 0}
    five_elements_by_difficulty: dict[str, dict] = {}
    empty = {
        k: {
            "gold": 0,
            "recreated": 0,
            "matched": 0,
            "hallucinated": 0,
            "hallucination_rate": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "f1": 0.0,
        }
        for k, _ in exp4.FIVE_ELEMENT_NAMES
    }
    for diff in ("easy", "medium", "hard"):
        items = [s for s in all_items if s.get("difficulty") == diff]
        by_difficulty_count[diff] = len(items)
        if not items:
            five_elements_by_difficulty[diff] = dict(empty)
            continue
        nn = len(items)
        fe_diff = {}
        micro = {k: exp4.agg_element(items, k) for k, _ in exp4.FIVE_ELEMENT_NAMES}
        for k, _ in exp4.FIVE_ELEMENT_NAMES:
            row = dict(micro[k])
            row["f1"] = sum((s.get("per_schema_f1") or {}).get(k, 0.0) for s in items) / nn
            fe_diff[k] = row
        five_elements_by_difficulty[diff] = fe_diff

    return {
        "model": model,
        "method": method,
        "label": f"{MODEL_LABEL[model]} {METHOD_LABEL[method]}",
        "gold_path": str(GOLD_PATH),
        "total_schemas": n,
        "scored_ok": n - scored_zero,
        "scored_zero": scored_zero,
        "skipped": scored_zero,  # kept for compatibility; now counted as zero, not excluded
        "gold_total": len(gold_by_id),
        "zero_policy": (
            "Failed/missing/empty predictions included in means as "
            "F1=0, nGED=1.0, Hallucination=1.0"
        ),
        "exact_match_count": exact_matches,
        "exact_match_rate": exact_matches / n if n else 0.0,
        "mean_normalized_graph_edit_distance": mean_nged,
        "mean_hallucination_rate": mean_hall,
        "per_schema": results_by_schema,
        "five_elements": five_elements,
        "by_difficulty_count": by_difficulty_count,
        "five_elements_by_difficulty": five_elements_by_difficulty,
    }


def build_summary_table(summaries: list[dict]) -> str:
    lines = []
    hdr = (
        f"{'Method':<28} {'Eval':>4} {'Zero':>4} "
        f"{'nGED':>6} {'Halluc':>6} {'Tables':>6} {'Attrs':>6} "
        f"{'Domain':>6} {'Entity':>6} {'Ref':>6}"
    )
    lines.append(hdr)
    lines.append("-" * len(hdr))
    for s in summaries:
        fe = s.get("five_elements") or {}
        lines.append(
            f"{s.get('label', '?'):<28} "
            f"{s.get('total_schemas', 0):>4} "
            f"{s.get('scored_zero', s.get('skipped', 0)):>4} "
            f"{s.get('mean_normalized_graph_edit_distance', 0):>6.3f} "
            f"{s.get('mean_hallucination_rate', 0):>6.3f} "
            f"{fe.get('tables', {}).get('f1', 0):>6.3f} "
            f"{fe.get('attributes', {}).get('f1', 0):>6.3f} "
            f"{fe.get('domain', {}).get('f1', 0):>6.3f} "
            f"{fe.get('entity', {}).get('f1', 0):>6.3f} "
            f"{fe.get('referential', {}).get('f1', 0):>6.3f}"
        )
    return "\n".join(lines)


def main() -> None:
    gold_rows = load_jsonl(GOLD_PATH)
    gold_by_id = {r["id"]: r for r in gold_rows if r.get("id")}
    print(f"Gold: {GOLD_PATH} ({len(gold_by_id)} ids)", flush=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summaries: list[dict] = []

    for model in MODELS:
        for method in METHODS:
            print(f"Evaluating {model}/{method} ...", flush=True)
            summary = evaluate_method(model, method, gold_by_id)
            summaries.append(summary)
            # write per-method (drop bulky per_schema from console; keep in file)
            out_path = OUT_DIR / f"{model}_{method}_evaluation.json"
            out_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
            fe = summary["five_elements"]
            print(
                f"  eval={summary['total_schemas']} skip={summary['skipped']} "
                f"nGED={summary['mean_normalized_graph_edit_distance']:.3f} "
                f"hall={summary['mean_hallucination_rate']:.3f} "
                f"T={fe['tables']['f1']:.3f} A={fe['attributes']['f1']:.3f} "
                f"D={fe['domain']['f1']:.3f} E={fe['entity']['f1']:.3f} "
                f"R={fe['referential']['f1']:.3f}",
                flush=True,
            )

    combined = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "gold_path": str(GOLD_PATH),
        "metric_source": str(
            DATA_ROOT / "RSchema_ExpResults4" / "Code" / "evaluate_exp4_text2schema.py"
        ),
        "methods": [
            {k: v for k, v in s.items() if k != "per_schema"} for s in summaries
        ],
    }
    combined_path = OUT_DIR / "paper_methods_evaluation.json"
    # full with per_schema too
    full_path = OUT_DIR / "paper_methods_evaluation_full.json"
    combined_path.write_text(json.dumps(combined, indent=2, default=str), encoding="utf-8")
    full_path.write_text(
        json.dumps(
            {
                **combined,
                "methods": summaries,
            },
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    table = build_summary_table(summaries)
    report_path = OUT_DIR / "paper_methods_report.txt"
    report = (
        "LLM4DBdesign PaperMethods — Exp4 metrics\n"
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        f"Gold: {GOLD_PATH}\n"
        "Metric code: RSchema_ExpResults4/Code/evaluate_exp4_text2schema.py\n"
        "Failed / missing / empty predictions are SCORED AS ZERO and included:\n"
        "  F1 (Tables/Attrs/Domain/Entity/Ref) = 0.0\n"
        "  nGED = 1.0 (worst)\n"
        "  Hallucination = 1.0 (worst)\n"
        "Reported F1 / nGED / Halluc = macro mean over all gold schemas (Eval column).\n"
        "Zero column = count of failed/unrun cases scored as zero.\n"
        "nGED / Hallucination lower is better; F1 columns higher is better.\n\n"
        + table
        + "\n"
    )
    report_path.write_text(report, encoding="utf-8")
    print("\n" + table)
    print(f"\nWrote {combined_path}")
    print(f"Wrote {report_path}")


if __name__ == "__main__":
    main()
