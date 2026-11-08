"""Thin orchestration: gold/prediction schema pairs -> five-element counts, nGED, aggregates.

The per-pair logic is a port of ``evaluate_text2schema2.evaluate_one`` (counts) combined
with the per-schema part of ``evaluate_exp4_text2schema.run_evaluation``.  Name matching
defaults to the RSchema-style normaliser, exactly like the Exp4 pipeline (which patches
it into the evaluator).  Pass ``legacy=True`` to use the vendored parser quirks and
reproduce archived numbers bit-for-bit.

Counting conventions (identical to the vendored code):

* tables:      gold/recreated = number of *raw* table names in metadata; matched = size of
  the intersection of normalised names.
* attributes:  gold/recreated = all columns of the whole schema; matched = same-named
  columns inside matched tables.
* domain:      same denominators as attributes; matched = matched columns whose type
  *family* agrees AND whose nullability agrees.
* entity:      gold/recreated = #PRIMARY KEY + #UNIQUE constraint occurrences (list
  length); matched = size of the set intersection of ``(table, sorted cols)``.
* referential: gold/recreated = #FK occurrences; matched = set intersection of directed
  ``(table, cols, ref_table, ref_cols)`` edges.

Determinism note: the vendored ``evaluate_one`` builds ``{normalized_name: raw_name}``
dicts by iterating Python *sets*.  When two raw names collapse to the same normalised
name (e.g. ``Airplane`` / ``Airplanes``) which one wins -- and hence the attribute/domain
counts -- depends on ``PYTHONHASHSEED``.  Re-running the vendored script twice changes
mean nGED by ~2e-4 and attribute F1 by ~5e-4 on RSchema.  This module iterates in sorted
order so results are reproducible; the first name in *reverse*-sorted insertion order is
overwritten last, i.e. the lexicographically smallest raw name wins.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Callable

from .metrics import (
    ELEMENTS,
    hallucination_rate,
    is_exact_match,
    macro_mean,
    micro_aggregate_all,
    normalized_graph_edit_distance,
    schema_difficulty,
    zero_scored_schema_metrics,
)
from .normalization import normalize_rschema_name, types_compatible
from .schema_parser import (
    ensure_prediction_metadata,
    extract_schema_from_metadata,
    metadata_from_ddl,
    parse_ddl_fks,
    parse_ddl_primary_unique,
)

NameFn = Callable[[str], str]


# --------------------------------------------------------------------------- gold loading


def load_jsonl(path: str | Path) -> list[dict]:
    rows = []
    with Path(path).open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _scalar_name(value: Any) -> str:
    while isinstance(value, dict):
        if not value:
            return ""
        value = next(iter(value.values()))
    return str(value or "")


def _sql_name(value: Any) -> str:
    return re.sub(r"\s+", "_", _scalar_name(value)).lower()


def gold_answer_to_metadata_and_ddl(answer: dict, database: str = "gold") -> tuple[dict, str]:
    """Convert an RSchema *logical* annotation (``answer`` dict) to metadata + synthetic DDL.

    Every attribute becomes ``varchar(255) NOT NULL`` (RSchema has no SQL types, which is
    why Domain F1 against typed predictions is low and why PaperMethods runs show
    Domain == Attributes).  Ported from ``RSchemaCode/evaluate_rschema_predictions.py``.
    """
    tables: list[str] = []
    columns_by_table: dict[str, list[dict]] = {}
    ddl_parts: list[str] = [f"-- Schema for database: {database}"]
    for table_name, tdef in answer.items():
        if not isinstance(tdef, dict):
            continue
        tables.append(table_name)
        attrs = list(tdef.get("Attributes") or [])
        pk_cols = set(tdef.get("Primary key") or [])
        fks = tdef.get("Foreign key") or {}
        col_objs: list[dict] = []
        col_lines: list[str] = []
        sql_table = _sql_name(table_name)
        for i, attr in enumerate(attrs, 1):
            sql_col = _sql_name(attr)
            col_objs.append(
                {
                    "COLUMN_NAME": attr,
                    "ORDINAL_POSITION": i,
                    "COLUMN_DEFAULT": None,
                    "IS_NULLABLE": "NO",
                    "DATA_TYPE": "varchar",
                    "CHARACTER_MAXIMUM_LENGTH": 255,
                    "NUMERIC_PRECISION": None,
                    "NUMERIC_SCALE": None,
                    "COLUMN_TYPE": "varchar(255)",
                    "COLUMN_KEY": "PRI" if attr in pk_cols else "",
                    "EXTRA": "",
                    "COLUMN_COMMENT": "",
                }
            )
            col_lines.append(f"  `{sql_col}` varchar(255) NOT NULL")
        pk_sql_cols = [_sql_name(c) for c in pk_cols if c]
        if pk_sql_cols:
            col_lines.append(f"  PRIMARY KEY (`{'`, `'.join(pk_sql_cols)}`)")
        for from_attr, ref in fks.items() if isinstance(fks, dict) else []:
            if not isinstance(ref, dict) or not ref:
                continue
            to_table, to_col = next(iter(ref.items()))
            from_sql = _sql_name(from_attr)
            col_lines.append(
                f"  CONSTRAINT `{sql_table}_ibfk_{from_sql}` FOREIGN KEY (`{from_sql}`) "
                f"REFERENCES `{_sql_name(to_table)}` (`{_sql_name(to_col)}`) "
                f"ON DELETE CASCADE ON UPDATE CASCADE"
            )
        columns_by_table[table_name] = col_objs
        body = ",\n".join(col_lines)
        ddl_parts.append(f"CREATE TABLE `{sql_table}` (\n{body}\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;")
    meta = {"database": database, "tables": tables, "columns_by_table": columns_by_table}
    return meta, "\n\n".join(ddl_parts)


def gold_record_to_metadata_and_ddl(record: dict, *, legacy: bool = False) -> tuple[dict, str, int, int]:
    """Return ``(meta, ddl, table_count, column_count)`` for an RSchema / SchemaBench gold record.

    ``record['answer']`` may be a DDL string (SchemaBench, ``annotation_ddl.jsonl``) or an
    RSchema logical-annotation dict (``annotation.jsonl``).
    """
    rid = record.get("id") or ""
    answer = record.get("answer") or {}
    gold_db = record.get("database") or f"gold_{str(rid)[:8]}"
    if isinstance(answer, str) and answer.strip():
        ddl = answer.strip()
        meta = metadata_from_ddl(ddl, database=gold_db, legacy=legacy)
        table_count = len(re.findall(r"CREATE\s+TABLE", ddl, re.IGNORECASE))
        column_count = sum(len(v or []) for v in meta["columns_by_table"].values())
        return meta, ddl, table_count, column_count
    table_count = column_count = 0
    for tdef in answer.values() if isinstance(answer, dict) else []:
        if isinstance(tdef, dict):
            table_count += 1
            column_count += len(tdef.get("Attributes") or [])
    meta, ddl = gold_answer_to_metadata_and_ddl(answer, database=gold_db)
    return meta, ddl, table_count, column_count


# --------------------------------------------------------------------------- one pair


def _constraint_key(items: list[tuple[str, list[str]]], name_fn: NameFn) -> set:
    return {(name_fn(t), tuple(sorted(name_fn(c) for c in cols))) for t, cols in items}


def five_element_counts(
    gold_meta: dict,
    gold_ddl: str,
    pred_meta: dict,
    pred_ddl: str,
    *,
    name_fn: NameFn = normalize_rschema_name,
    legacy: bool = False,
) -> dict[str, dict[str, int]]:
    """Gold/recreated/matched counts for tables, attributes, domain, entity, referential."""
    g_tables, g_cols, g_info = extract_schema_from_metadata(gold_meta)
    p_tables, p_cols, p_info = extract_schema_from_metadata(pred_meta)
    # sorted(): when two raw names normalise to the same key the *first in sorted order* wins.
    # (The vendored evaluator iterates a ``set`` here, so its result under such collisions
    # depends on PYTHONHASHSEED -- see docs in the module header.)
    g_norm = {name_fn(t): t for t in sorted(g_tables, reverse=True)}
    p_norm = {name_fn(t): t for t in sorted(p_tables, reverse=True)}
    matched_tables = set(g_norm) & set(p_norm)

    attr_gold = sum(len(c) for c in g_cols.values())
    attr_pred = sum(len(c) for c in p_cols.values())
    attr_match = domain_match = 0
    for tn in matched_tables:
        gt, pt = g_norm[tn], p_norm[tn]
        gc = {name_fn(c): c for c in sorted(g_cols.get(gt, set()), reverse=True)}
        pc = {name_fn(c): c for c in sorted(p_cols.get(pt, set()), reverse=True)}
        shared = set(gc) & set(pc)
        attr_match += len(shared)
        for cn in shared:
            gi = g_info.get(gt, {}).get(gc[cn], {})
            pi = p_info.get(pt, {}).get(pc[cn], {})
            type_ok = types_compatible(gi.get("DATA_TYPE"), pi.get("DATA_TYPE"), legacy=legacy)
            null_ok = ((gi.get("IS_NULLABLE") or "").upper() == "YES") == (
                (pi.get("IS_NULLABLE") or "").upper() == "YES"
            )
            if type_ok and null_ok:
                domain_match += 1

    g_pk, g_uq = parse_ddl_primary_unique(gold_ddl, legacy=legacy)
    p_pk, p_uq = parse_ddl_primary_unique(pred_ddl, legacy=legacy)
    pk_m = len(_constraint_key(g_pk, name_fn) & _constraint_key(p_pk, name_fn))
    uq_m = len(_constraint_key(g_uq, name_fn) & _constraint_key(p_uq, name_fn))

    g_fks, _ = parse_ddl_fks(gold_ddl, legacy=legacy)
    p_fks, _ = parse_ddl_fks(pred_ddl, legacy=legacy)

    def edge_set(fks: list) -> set:
        return {
            (name_fn(t), tuple(name_fn(c) for c in cols), name_fn(tt), tuple(name_fn(c) for c in refs))
            for t, cols, tt, refs in fks
        }

    fk_m = len(edge_set(g_fks) & edge_set(p_fks))
    return {
        "tables": {"gold": len(g_tables), "recreated": len(p_tables), "matched": len(matched_tables)},
        "attributes": {"gold": attr_gold, "recreated": attr_pred, "matched": attr_match},
        "domain": {"gold": attr_gold, "recreated": attr_pred, "matched": domain_match},
        "entity": {
            "gold": len(g_pk) + len(g_uq),
            "recreated": len(p_pk) + len(p_uq),
            "matched": pk_m + uq_m,
        },
        "referential": {"gold": len(g_fks), "recreated": len(p_fks), "matched": fk_m},
    }


def evaluate_schema_pair(
    gold_meta: dict,
    gold_ddl: str,
    pred_meta: dict,
    pred_ddl: str,
    *,
    name_fn: NameFn = normalize_rschema_name,
    legacy: bool = False,
    table_count: int | None = None,
    column_count: int | None = None,
) -> dict[str, Any]:
    """Evaluate one (gold, prediction) pair; returns a per-schema record.

    ``pred_meta`` is passed through :func:`ensure_prediction_metadata`, so ``{}`` is fine
    when the prediction is DDL only.  ``table_count``/``column_count`` (used only for the
    easy/medium/hard label) default to the gold metadata sizes.
    """
    pred_meta = ensure_prediction_metadata(pred_meta, pred_ddl, legacy=legacy)
    counts = five_element_counts(gold_meta, gold_ddl, pred_meta, pred_ddl, name_fn=name_fn, legacy=legacy)
    if table_count is None:
        table_count = len(gold_meta.get("tables") or [])
    if column_count is None:
        column_count = sum(len(v or []) for v in (gold_meta.get("columns_by_table") or {}).values())
    return {
        **counts,
        "exact_match": is_exact_match(**counts),
        "normalized_graph_edit_distance": normalized_graph_edit_distance(
            gold_meta, gold_ddl, pred_meta, pred_ddl, name_fn=name_fn, legacy=legacy
        ),
        "hallucination_rate_by_dimension": {
            k: hallucination_rate(counts[k]["recreated"], counts[k]["matched"]) for k in ELEMENTS
        },
        "difficulty": schema_difficulty(table_count, column_count),
    }


def evaluate_ddl_pair(gold_ddl: str, pred_ddl: str, **kwargs: Any) -> dict[str, Any]:
    """Convenience wrapper: derive metadata from both DDL strings, then evaluate."""
    legacy = kwargs.get("legacy", False)
    gold_meta = metadata_from_ddl(gold_ddl, legacy=legacy)
    return evaluate_schema_pair(gold_meta, gold_ddl, {}, pred_ddl, **kwargs)


# --------------------------------------------------------------------------- aggregation


def aggregate_schemas(items: list[dict], *, n_gold: int | None = None) -> dict[str, Any]:
    """Aggregate per-schema records.

    * ``five_elements``: micro aggregates (summed counts).
    * ``mean_normalized_graph_edit_distance``: macro mean over ``items``.
    * If ``n_gold`` is given and larger than ``len(items)``, the missing schemas are scored
      with the zero-score policy for nGED (1.0) and hallucination (1.0) and F1 macro means.
      Micro counts are unaffected (missing schemas contribute no counts).
    """
    n = len(items)
    n_total = max(n, n_gold or 0)
    n_zero = n_total - n
    nged_sum = sum(s["normalized_graph_edit_distance"] for s in items) + n_zero * 1.0
    exact = sum(1 for s in items if s.get("exact_match"))
    return {
        "total_schemas": n,
        "zero_scored": n_zero,
        "exact_match_count": exact,
        "exact_match_rate": exact / n if n else 0.0,
        "mean_normalized_graph_edit_distance": nged_sum / n_total if n_total else 0.0,
        "five_elements": micro_aggregate_all(items),
        "mean_hallucination_rate_over_dimensions": (
            (
                sum(macro_mean(s["hallucination_rate_by_dimension"].values()) for s in items)
                + n_zero * zero_scored_schema_metrics()["per_schema_hallucination"]
            )
            / n_total
            if n_total
            else 0.0
        ),
    }


def evaluate_predictions_dir(
    pred_dir: str | Path,
    gold_path: str | Path,
    *,
    name_fn: NameFn = normalize_rschema_name,
    legacy: bool = False,
    limit: int | None = None,
) -> dict[str, Any]:
    """Re-evaluate an Exp4-style prediction folder (``NNNN.json`` with ``id``/``ddl``/``metadata``).

    Mirrors ``evaluate_exp4_text2schema.run_evaluation``: predictions with ``error``,
    ``skipped`` or empty ``ddl`` are *skipped* (not scored).  Use ``legacy=True`` to
    reproduce archived numbers exactly.  Offline only; no API calls.
    """
    gold_by_id = {r["id"]: r for r in load_jsonl(gold_path) if r.get("id")}
    per_schema: dict[str, dict] = {}
    skipped = 0
    files = sorted(Path(pred_dir).glob("[0-9][0-9][0-9][0-9].json"))
    if limit is not None:
        files = files[:limit]
    for pred_path in files:
        label = pred_path.stem
        try:
            data = json.loads(pred_path.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            per_schema[label] = {"error": str(e)}
            skipped += 1
            continue
        gold = gold_by_id.get(data.get("id") or "")
        if not gold:
            per_schema[label] = {"error": "no gold record"}
            skipped += 1
            continue
        if data.get("error") or data.get("skipped") or not data.get("ddl"):
            per_schema[label] = {"error": data.get("error") or data.get("skip_reason") or "missing ddl"}
            skipped += 1
            continue
        g_meta, g_ddl, tc, cc = gold_record_to_metadata_and_ddl(gold, legacy=legacy)
        rec = evaluate_schema_pair(
            g_meta,
            g_ddl,
            data.get("metadata") or {},
            data.get("ddl") or "",
            name_fn=name_fn,
            legacy=legacy,
            table_count=tc,
            column_count=cc,
        )
        rec["id"] = data.get("id")
        per_schema[label] = rec
    scored = [s for s in per_schema.values() if "error" not in s]
    out = aggregate_schemas(scored)
    out.update({"skipped": skipped, "per_schema": per_schema})
    return out
