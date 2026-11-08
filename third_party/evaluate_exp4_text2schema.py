#!/usr/bin/env python3
"""
Evaluate SchemaBench text2schema outputs vs gold (annotation_ddl.jsonl DDL answer).

Metrics (same five elements as Text2ER / Text2Schema2):
  tables, attributes, domain integrity, entity integrity, referential integrity
  -> precision, recall, F1 (micro-aggregate), hallucination count & rate per dimension

Additional schema-level metrics:
  Exact Match — per-schema boolean: all five elements perfectly match gold counts
  Normalized Graph Edit Distance (nGED) — structural distance on table/attribute/FK graph

Predictions:
    <base>/text2schema_<llm>/NNNN.json  (+ NNNN.txt DDL)

Gold:
    <data_root>/SchemaBench/Dataset/annotation_ddl.jsonl  (DDL string -> metadata via metadata_from_ddl)

Outputs:
    <base>/Results/text2schema_exp4_<llm>.json
    <base>/Results/text2schema_exp4_evaluation.json   (all LLMs)
    <base>/Results/text2schema_exp4_report.txt
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
# SchemaBridge vendoring patch: when SCHEMABRIDGE_ROOT is set the script is self-contained --
# it resolves evaluate_text2schema2 / evaluate_rschema_predictions from this directory
# (third_party/) instead of the historical /data/... checkouts, and defaults to the
# repo-local datasets/ and results/predictions/ trees.  Without the variable the original
# behaviour is unchanged.
SCHEMABRIDGE_ROOT = Path(os.environ["SCHEMABRIDGE_ROOT"]) if os.environ.get("SCHEMABRIDGE_ROOT") else None
DATA_ROOT = Path("/data") if Path("/data").is_dir() else SCRIPT_DIR.parent.parent
DEFAULT_BASE = DATA_ROOT / "SchemaBench" / "Experiment"
DEFAULT_GOLD = DATA_ROOT / "SchemaBench" / "Dataset" / "annotation_ddl.jsonl"
if SCHEMABRIDGE_ROOT is not None:
    DEFAULT_BASE = SCHEMABRIDGE_ROOT / "results" / "predictions" / "e0"
    DEFAULT_GOLD = SCHEMABRIDGE_ROOT / "datasets" / "schemabench" / "annotation_ddl.jsonl"
DEFAULT_OUT_DIR = DEFAULT_BASE / "Results"
TEXT2ER_ROOT = DATA_ROOT / "Text2ER"
EVAL_ROOT = DATA_ROOT / "Results" / "Text2Schema2Results"
RSCHEMA_CODE = DATA_ROOT / "RSchemaCode"
if not RSCHEMA_CODE.is_dir():
    RSCHEMA_CODE = SCRIPT_DIR.parent.parent / "RSchemaCode"

sys.path.insert(0, str(TEXT2ER_ROOT))
sys.path.insert(0, str(EVAL_ROOT))
sys.path.insert(0, str(RSCHEMA_CODE))
if SCHEMABRIDGE_ROOT is not None:
    sys.path.insert(0, str(SCRIPT_DIR))  # vendored modules win over /data/... copies
    sys.path.insert(0, str(SCHEMABRIDGE_ROOT))

import evaluate_text2schema2 as ev  # noqa: E402
from evaluate_rschema_predictions import (  # noqa: E402
    gold_answer_to_metadata_and_ddl,
    load_jsonl,
    normalize_rschema_name,
)

PREFIX_OUT = "text2schema_"
JSON_PREFIX = "text2schema_exp4_"
GOLD_TOTAL = 518

FIVE_ELEMENT_NAMES = [
    ("tables", "1. Schema: Table name"),
    ("attributes", "2. Schema: Attributes"),
    ("domain", "3. Domain: types, NULL/NOT NULL"),
    ("entity", "4. Entity: Primary, UNIQUE (single/multi col.)"),
    ("referential", "5. Referential: Foreign Keys (single/multi col.)"),
]

METRICS_SECTION = """
Five schema elements evaluated (Gold = original, Recreated = LLM output, Matched = correct).
  Hallucinated = Recreated - Matched.
  Hallucination rate = Hallucinated / Recreated  (0 when Recreated = 0).
  Precision = Matched/Recreated.  Recall = Matched/Gold.  F1 = 2*P*R/(P+R).

  Exact Match: fraction of schemas where all five elements match gold exactly
    (gold == recreated == matched for tables, attributes, domain, entity, referential).

  Normalized Graph Edit Distance (nGED): symmetric-difference edit cost on the schema graph
    (table nodes + column labels + directed FK edges), divided by (gold_size + pred_size).
    Range [0, 1]; lower is better; 0 = identical structure under name normalization.

  Schema types: easy = ≤3 tables & ≤30 columns; medium = ≤15 tables & ≤150 columns; hard = else.

  Gold: RSchema annotation_ddl.jsonl DDL answer (synthetic metadata + DDL).
  Recreated: Exp4 text2schema_<llm> outputs (metadata parsed from DDL when empty).
  Name matching: RSchema normalization (spaces/plurals/suffixes).
"""


_TYPE_RE = re.compile(
    r"\b(varchar|char|text|int|integer|tinyint|smallint|mediumint|bigint|"
    r"float|double|decimal|numeric|real|datetime|date|time|timestamp|bool|boolean)\b",
    re.IGNORECASE,
)
_CREATE_TABLE_HEADER_RE = re.compile(
    r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?"
    r"(?:[`\"]([^`\"]+)[`\"]|([A-Za-z_][\w$]*))"
    r"\s*\(",
    re.IGNORECASE,
)
# Kept for callers/tests that still reference the old compiled pattern name.
_TABLE_RE = _CREATE_TABLE_HEADER_RE
_INT_TYPES = frozenset({"int", "tinyint", "smallint", "mediumint", "bigint", "integer"})
_STR_TYPES = frozenset({"varchar", "char", "text"})


def discover_llms(base: Path) -> list[str]:
    names: list[str] = []
    if not base.is_dir():
        return names
    for d in sorted(base.iterdir()):
        if d.is_dir() and d.name.startswith(PREFIX_OUT):
            llm = d.name[len(PREFIX_OUT) :]
            if llm and list(d.glob("[0-9][0-9][0-9][0-9].json")):
                names.append(llm)
    return names


def _parse_data_type(line: str) -> tuple[str, str]:
    m = _TYPE_RE.search(line)
    if not m:
        return "varchar", "varchar(255)"
    dtype = m.group(1).lower()
    if dtype == "integer":
        dtype = "int"
    col_type = dtype
    paren = re.search(r"\(([^)]+)\)", line)
    if paren and dtype in ("varchar", "char", "decimal", "numeric"):
        col_type = f"{dtype}({paren.group(1)})"
    elif dtype == "int":
        col_type = "int(11)"
    return dtype, col_type


def iter_ddl_table_bodies(ddl: str):
    """Yield (table_name, body) for each CREATE TABLE, including IF NOT EXISTS / no ENGINE."""
    if not (ddl or "").strip():
        return
    for m in _CREATE_TABLE_HEADER_RE.finditer(ddl):
        table = (m.group(1) or m.group(2) or "").strip()
        if not table:
            continue
        start = m.end()
        depth = 1
        i = start
        while i < len(ddl) and depth:
            ch = ddl[i]
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            i += 1
        yield table, ddl[start : i - 1]


def metadata_from_ddl(ddl: str, database: str = "") -> dict:
    """Build metadata.columns_by_table from predicted DDL when JSON metadata is empty."""
    tables: list[str] = []
    columns_by_table: dict[str, list[dict]] = {}
    if not (ddl or "").strip():
        return {"database": database, "tables": [], "columns_by_table": {}}

    for table, body in iter_ddl_table_bodies(ddl):
        tables.append(table)
        col_objs: list[dict] = []
        ord_pos = 0
        for line in body.split("\n"):
            line = line.strip().rstrip(",")
            if not line:
                continue
            upper = line.upper()
            if upper.startswith(
                ("PRIMARY KEY", "FOREIGN KEY", "UNIQUE", "KEY ", "CONSTRAINT", "CHECK ", "INDEX ")
            ):
                continue
            col_match = re.match(r"[`'\"]([^`'\"]+)[`'\"]\s+(.+)|(\w+)\s+(.+)", line)
            if not col_match:
                continue
            if col_match.group(1) is not None:
                col_name, rest = col_match.group(1), col_match.group(2)
            else:
                col_name, rest = col_match.group(3), col_match.group(4)
            if not _TYPE_RE.search(rest):
                continue
            ord_pos += 1
            dtype, col_type = _parse_data_type(rest)
            nullable = (
                "YES"
                if re.search(r"\bNULL\b", rest, re.IGNORECASE)
                and not re.search(r"\bNOT\s+NULL\b", rest, re.IGNORECASE)
                else "NO"
            )
            col_key = ""
            if re.search(r"\bPRIMARY\s+KEY\b", rest, re.IGNORECASE):
                col_key = "PRI"
            elif re.search(r"\bUNIQUE\b", rest, re.IGNORECASE):
                col_key = "UNI"
            col_objs.append(
                {
                    "COLUMN_NAME": col_name,
                    "ORDINAL_POSITION": ord_pos,
                    "COLUMN_DEFAULT": None,
                    "IS_NULLABLE": nullable,
                    "DATA_TYPE": dtype,
                    "CHARACTER_MAXIMUM_LENGTH": 255 if dtype in ("varchar", "char") else None,
                    "NUMERIC_PRECISION": None,
                    "NUMERIC_SCALE": None,
                    "COLUMN_TYPE": col_type,
                    "COLUMN_KEY": col_key,
                    "EXTRA": "",
                    "COLUMN_COMMENT": "",
                }
            )
        columns_by_table[table] = col_objs

    if not tables:
        tables = [
            (m.group(1) or m.group(2) or "").strip()
            for m in _CREATE_TABLE_HEADER_RE.finditer(ddl)
            if (m.group(1) or m.group(2))
        ]
        columns_by_table = {t: [] for t in tables}

    return {"database": database, "tables": tables, "columns_by_table": columns_by_table}


def ensure_prediction_metadata(pred_meta: dict, pred_ddl: str, database: str = "") -> dict:
    meta = dict(pred_meta or {})
    cbt = meta.get("columns_by_table") or {}
    if sum(len(v or []) for v in cbt.values()) > 0:
        return meta
    parsed = metadata_from_ddl(pred_ddl, database=database or meta.get("database") or "")
    if not meta.get("tables"):
        meta["tables"] = parsed.get("tables") or []
    meta["columns_by_table"] = parsed.get("columns_by_table") or {}
    meta.setdefault("database", parsed.get("database") or database)
    return meta


def _type_family(dtype: str) -> str:
    d = (dtype or "").lower()
    if d in _INT_TYPES:
        return "int"
    if d in _STR_TYPES:
        return "str"
    return d


def _column_labels(meta: dict) -> dict[str, set[tuple[str, str, str]]]:
    """table_norm -> set of (col_norm, type_family, nullable YES/NO)."""
    out: dict[str, set[tuple[str, str, str]]] = {}
    tables, cols_by_table, info = ev.extract_schema_from_metadata(meta)
    for t in tables:
        tn = normalize_rschema_name(t)
        labels: set[tuple[str, str, str]] = set()
        for col in cols_by_table.get(t, set()):
            cn = normalize_rschema_name(col)
            inf = info.get(t, {}).get(col, {})
            dtype = _type_family(inf.get("DATA_TYPE") or "")
            nullable = (inf.get("IS_NULLABLE") or "NO").upper()
            labels.add((cn, dtype, nullable))
        out[tn] = labels
    return out


def _fk_edges(ddl: str) -> set[tuple[str, tuple[str, ...], str, tuple[str, ...]]]:
    fks, _ = ev.parse_ddl_fks(ddl)
    return {
        (
            normalize_rschema_name(t),
            tuple(normalize_rschema_name(c) for c in cols),
            normalize_rschema_name(tt),
            tuple(normalize_rschema_name(c) for c in refs),
        )
        for t, cols, tt, refs in fks
    }


def _graph_size(tables: set[str], attrs: dict[str, set], fks: set) -> int:
    return len(tables) + sum(len(v) for v in attrs.values()) + len(fks)


def normalized_graph_edit_distance(
    gold_meta: dict,
    gold_ddl: str,
    pred_meta: dict,
    pred_ddl: str,
) -> float:
    """
    Normalized edit distance on schema graph:
      nodes = tables; node labels = column (name, type, nullability) triples;
      edges = directed FK tuples.
    Edit cost = |tables Δ| + attribute symmetric diff on matched tables
                + attribute deletions on unmatched tables + |FK Δ|.
    nGED = edit_cost / max(gold_graph_size, pred_graph_size, 1).
    """
    g_attrs = _column_labels(gold_meta)
    p_attrs = _column_labels(pred_meta)
    g_tables = set(g_attrs.keys())
    p_tables = set(p_attrs.keys())
    g_fks = _fk_edges(gold_ddl)
    p_fks = _fk_edges(pred_ddl)

    table_edits = len(g_tables ^ p_tables)
    matched_tables = g_tables & p_tables
    attr_edits = sum(len(g_attrs[t] ^ p_attrs[t]) for t in matched_tables)
    attr_edits += sum(len(g_attrs[t]) for t in g_tables - p_tables)
    attr_edits += sum(len(p_attrs[t]) for t in p_tables - g_tables)
    fk_edits = len(g_fks ^ p_fks)

    ged = table_edits + attr_edits + fk_edits
    g_size = _graph_size(g_tables, g_attrs, g_fks)
    p_size = _graph_size(p_tables, p_attrs, p_fks)
    denom = max(g_size + p_size, 1)
    return ged / denom


def is_exact_match(
    tables: dict,
    attributes: dict,
    domain: dict,
    entity: dict,
    referential: dict,
) -> bool:
    """True when gold == recreated == matched for all five elements."""
    for row in (tables, attributes, domain, entity, referential):
        g = row.get("gold", 0)
        r = row.get("recreated", 0)
        m = row.get("matched", 0)
        if not (g == r == m):
            return False
    return True


def agg_element(items: list[dict], key: str) -> dict:
    g = sum(s[key]["gold"] for s in items)
    r = sum(s[key]["recreated"] for s in items)
    m = sum(s[key]["matched"] for s in items)
    hall = max(0, r - m)
    prec = m / r if r else 0.0
    rec = m / g if g else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
    hall_rate = hall / r if r else 0.0
    return {
        "gold": g,
        "recreated": r,
        "matched": m,
        "hallucinated": hall,
        "hallucination_rate": hall_rate,
        "precision": prec,
        "recall": rec,
        "f1": f1,
    }


def run_evaluation(
    llm: str,
    base_dir: Path,
    annotation_path: Path,
) -> dict:
    ev.normalize_name = normalize_rschema_name
    pred_dir = base_dir / f"{PREFIX_OUT}{llm}"
    if not pred_dir.is_dir():
        return {"error": f"Directory not found: {pred_dir}", "llm": llm}

    gold_by_id = {r["id"]: r for r in load_jsonl(annotation_path) if r.get("id")}
    results_by_schema: dict[str, dict] = {}
    skipped = 0

    for pred_path in sorted(pred_dir.glob("[0-9][0-9][0-9][0-9].json")):
        label = pred_path.stem
        try:
            pred_data = json.loads(pred_path.read_text(encoding="utf-8"))
        except Exception as e:
            results_by_schema[label] = {"error": str(e)}
            skipped += 1
            continue

        rid = pred_data.get("id")
        gold_rec = gold_by_id.get(rid) if rid else None
        if not gold_rec:
            results_by_schema[label] = {"error": "no gold record"}
            skipped += 1
            continue
        if pred_data.get("error") or pred_data.get("skipped") or not pred_data.get("ddl"):
            results_by_schema[label] = {
                "error": pred_data.get("error") or pred_data.get("skip_reason") or "missing ddl"
            }
            skipped += 1
            continue

        answer = gold_rec.get("answer") or {}
        gold_db = gold_rec.get("database") or f"gold_{rid[:8]}"
        if isinstance(answer, str) and answer.strip():
            orig_ddl = answer.strip()
            orig_meta = metadata_from_ddl(orig_ddl, database=gold_db)
            table_count = len(re.findall(r"CREATE\s+TABLE", orig_ddl, re.IGNORECASE))
            column_count = sum(
                len(v or []) for v in (orig_meta.get("columns_by_table") or {}).values()
            )
        else:
            table_count, column_count = 0, 0
            for tdef in (answer.values() if isinstance(answer, dict) else []):
                if isinstance(tdef, dict):
                    table_count += 1
                    column_count += len(tdef.get("Attributes") or [])
            orig_meta, orig_ddl = gold_answer_to_metadata_and_ddl(
                answer, database=gold_db
            )
        pred_ddl = pred_data.get("ddl") or ""
        pred_meta = ensure_prediction_metadata(
            pred_data.get("metadata") or {},
            pred_ddl,
            database=pred_data.get("database") or "",
        )

        m = ev.evaluate_one(
            label,
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
        exact = is_exact_match(**per)
        nged = normalized_graph_edit_distance(orig_meta, orig_ddl, pred_meta, pred_ddl)

        per_schema_hall_rates = {}
        for dim, row in per.items():
            r, hall = row["recreated"], max(0, row["recreated"] - row["matched"])
            per_schema_hall_rates[dim] = hall / r if r else 0.0

        results_by_schema[label] = {
            "id": rid,
            "text_number": pred_data.get("text_number"),
            "llm": llm,
            **per,
            "exact_match": exact,
            "normalized_graph_edit_distance": nged,
            "hallucination_rate_by_dimension": per_schema_hall_rates,
            "difficulty": m.difficulty,
        }

    all_items = [s for s in results_by_schema.values() if "error" not in s]
    five_elements = {k: agg_element(all_items, k) for k, _ in FIVE_ELEMENT_NAMES}

    exact_matches = sum(1 for s in all_items if s.get("exact_match"))
    nged_values = [s["normalized_graph_edit_distance"] for s in all_items]
    mean_nged = sum(nged_values) / len(nged_values) if nged_values else 0.0

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
        for k, _ in FIVE_ELEMENT_NAMES
    }
    for diff in ("easy", "medium", "hard"):
        items = [s for s in all_items if s.get("difficulty") == diff]
        by_difficulty_count[diff] = len(items)
        five_elements_by_difficulty[diff] = (
            {k: agg_element(items, k) for k, _ in FIVE_ELEMENT_NAMES} if items else dict(empty)
        )

    return {
        "llm": llm,
        "pred_dir": str(pred_dir),
        "gold_path": str(annotation_path),
        "total_schemas": len(all_items),
        "skipped": skipped,
        "exact_match_count": exact_matches,
        "exact_match_rate": exact_matches / len(all_items) if all_items else 0.0,
        "mean_normalized_graph_edit_distance": mean_nged,
        "per_schema": results_by_schema,
        "five_elements": five_elements,
        "by_difficulty_count": by_difficulty_count,
        "five_elements_by_difficulty": five_elements_by_difficulty,
    }


def _fmt(v) -> str:
    if isinstance(v, (int, float)):
        return f"{v:.3f}" if isinstance(v, float) else str(v)
    return str(v)


def _table_row(cells: list, widths: list[int]) -> str:
    return " | ".join(str(c).ljust(w) for c, w in zip(cells, widths))


def _one_table(fe: dict, widths: list[int], headers: list[str]) -> list[str]:
    out = []
    out.append(_table_row(headers, widths))
    out.append("-" * (sum(widths) + 3 * (len(widths) - 1)))
    for key, label in FIVE_ELEMENT_NAMES:
        row_data = fe.get(key) or {}
        g = row_data.get("gold", 0)
        r = row_data.get("recreated", 0)
        m = row_data.get("matched", 0)
        h = row_data.get("hallucinated", 0)
        hr = row_data.get("hallucination_rate", 0.0)
        p = row_data.get("precision", 0)
        rec = row_data.get("recall", 0)
        f1 = row_data.get("f1", 0)
        out.append(
            _table_row([label, g, r, m, h, _fmt(hr), _fmt(p), _fmt(rec), _fmt(f1)], widths)
        )
    return out


def build_report(summaries: list[dict]) -> str:
    valid = [s for s in summaries if "error" not in s and s.get("five_elements")]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines: list[str] = []

    lines.append("SchemaBench Text2Schema — Evaluation Report")
    lines.append("=" * 100)
    lines.append(f"Generated: {now}")
    lines.append(f"Gold: {DEFAULT_GOLD} ({GOLD_TOTAL} records)")
    lines.append(METRICS_SECTION)
    lines.append("")

    # Summary table across LLMs
    lines.append("SUMMARY BY LLM")
    lines.append("-" * 100)
    hdr = (
        f"{'LLM':<16} {'Eval':>5} {'Skip':>5} {'ExactMatch':>11} {'EM rate':>8} "
        f"{'mean nGED':>10}  Tables F1  Attr F1  Domain F1  Entity F1  Ref F1"
    )
    lines.append(hdr)
    lines.append("-" * len(hdr))
    for s in valid:
        fe = s.get("five_elements") or {}
        lines.append(
            f"{s.get('llm', '?'):<16} "
            f"{s.get('total_schemas', 0):>5} "
            f"{s.get('skipped', 0):>5} "
            f"{s.get('exact_match_count', 0):>11} "
            f"{s.get('exact_match_rate', 0):>8.3f} "
            f"{s.get('mean_normalized_graph_edit_distance', 0):>10.3f}  "
            f"{fe.get('tables', {}).get('f1', 0):>8.3f} "
            f"{fe.get('attributes', {}).get('f1', 0):>7.3f} "
            f"{fe.get('domain', {}).get('f1', 0):>9.3f} "
            f"{fe.get('entity', {}).get('f1', 0):>9.3f} "
            f"{fe.get('referential', {}).get('f1', 0):>7.3f}"
        )
    lines.append("")

    w_elem = 48
    col_w = [10, 10, 8, 12, 12, 10, 8, 8]
    widths = [w_elem] + col_w
    headers = [
        "Element",
        "Gold",
        "Recreated",
        "Matched",
        "Hallucinated",
        "Hall.Rate",
        "Precision",
        "Recall",
        "F1",
    ]

    for i, s in enumerate(valid):
        if i > 0:
            lines.append("")
        llm = s.get("llm", "?")
        lines.append(f"--- LLM: {llm}  (evaluated={s.get('total_schemas', 0)}, skipped={s.get('skipped', 0)}) ---")
        lines.append(
            f"Exact Match: {s.get('exact_match_count', 0)}/{s.get('total_schemas', 0)} "
            f"({s.get('exact_match_rate', 0):.3f})   "
            f"Mean nGED: {s.get('mean_normalized_graph_edit_distance', 0):.4f}"
        )
        lines.append("")
        lines.append("OVERALL (micro-aggregate)")
        lines.extend(_one_table(s.get("five_elements") or {}, widths, headers))

        by_diff = s.get("five_elements_by_difficulty") or {}
        counts = s.get("by_difficulty_count") or {}
        for diff in ("easy", "medium", "hard"):
            n = counts.get(diff, 0)
            lines.append("")
            lines.append(f"Schema type: {diff.upper()}  (n = {n})")
            lines.extend(_one_table(by_diff.get(diff) or {}, widths, headers))

    lines.append("")
    lines.append("=" * 100)
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Exp4 text2schema vs RSchema gold")
    parser.add_argument("--base-dir", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--annotation", type=Path, default=DEFAULT_GOLD)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument(
        "--llm",
        action="append",
        dest="llms",
        help="LLM name suffix (default: all discovered text2schema_* folders)",
    )
    args = parser.parse_args()

    llms = args.llms or discover_llms(args.base_dir)
    if not llms:
        print("No text2schema prediction folders found under", args.base_dir, file=sys.stderr)
        sys.exit(1)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    summaries: list[dict] = []

    for llm in llms:
        print(f"Evaluating LLM: {llm}", flush=True)
        summary = run_evaluation(llm, args.base_dir, args.annotation)
        summaries.append(summary)
        if "error" in summary and summary.get("total_schemas", 0) == 0:
            print(f"  SKIP: {summary['error']}", file=sys.stderr)
            continue

        out_path = args.out_dir / f"{JSON_PREFIX}{llm}.json"
        out_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
        fe = summary.get("five_elements") or {}
        print(
            f"  evaluated={summary.get('total_schemas')} skipped={summary.get('skipped')} "
            f"exact_match={summary.get('exact_match_count')} "
            f"mean_nGED={summary.get('mean_normalized_graph_edit_distance', 0):.4f}"
        )
        for key, _ in FIVE_ELEMENT_NAMES:
            row = fe.get(key) or {}
            print(
                f"    {key}: gold={row.get('gold', 0)} recreated={row.get('recreated', 0)} "
                f"matched={row.get('matched', 0)} hall_rate={row.get('hallucination_rate', 0):.3f} "
                f"F1={row.get('f1', 0):.3f}"
            )
        print(f"  wrote {out_path}")

    combined = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "gold_path": str(args.annotation),
        "llms": summaries,
    }
    combined_path = args.out_dir / f"{JSON_PREFIX}evaluation.json"
    combined_path.write_text(json.dumps(combined, indent=2, default=str), encoding="utf-8")

    report_text = build_report(summaries)
    report_path = args.out_dir / f"{JSON_PREFIX}report.txt"
    report_path.write_text(report_text, encoding="utf-8")

    print(f"\nWrote combined JSON: {combined_path}")
    print(f"Wrote report: {report_path}")


if __name__ == "__main__":
    main()
