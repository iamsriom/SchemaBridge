#!/usr/bin/env python3
"""
Evaluate Text2Schema2 outputs vs original schemas.
Compares: schema (table/attribute names), domain integrity (types, nullability),
entity integrity (PRIMARY, UNIQUE), reference integrity (FKs, composite FKs).
Classifies schemas as easy/medium/hard. Saves per-LLM results and prints analysis.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from dataclasses import dataclass

# Paths
DATA_ROOT = Path("/data")
SCHEMA_DIR = Path("/data/Text2ER/schema")
LLM_TRANSLATIONS = DATA_ROOT / "LLMTranslations"
RESULTS_DIR = Path(__file__).resolve().parent
TEXT2SCHEMA2_PREFIX = "Text2Schema2_"
# Locked: schema_classification from this vendor directory only.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from schema_classification import classify_schema, parse_ddl_primary_unique  # noqa: E402


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def normalize_name(s: str) -> str:
    return (s or "").strip().lower()


def _norm_map(names) -> dict[str, str]:
    """Map normalize_name(x) -> x with deterministic collision resolution.

    When multiple raw names share a normalized key, keep the lexicographically
    greatest raw name (stable across PYTHONHASHSEED).
    """
    out: dict[str, str] = {}
    for raw in sorted(names):
        out[normalize_name(raw)] = raw
    return out



_CREATE_TABLE_RE = re.compile(
    r"CREATE\s+TABLE(?:\s+IF\s+NOT\s+EXISTS)?\s+[`']?(\w+)[`'\"]?\s*",
    re.IGNORECASE,
)
_TABLE_BODY_RE = re.compile(
    r"CREATE\s+TABLE(?:\s+IF\s+NOT\s+EXISTS)?\s+[`']?(\w+)[`'\"]?\s*\((.*?)\)\s*(?:ENGINE[^;]*)?;?",
    re.DOTALL | re.IGNORECASE,
)


def parse_ddl_fks(ddl: str) -> tuple[list[tuple[str, list[str], str, list[str]]], int]:
    """Parse DDL for FOREIGN KEY constraints. Returns list of (from_table, from_cols, to_table, to_cols) and count of composite FKs."""
    fks: list[tuple[str, list[str], str, list[str]]] = []
    pattern = re.compile(
        r"FOREIGN\s+KEY\s*\(([^)]+)\)\s+REFERENCES\s+[`']?\(?[`']?(\w+)[`'\"]?\)?[`']?\s*\(([^)]+)\)",
        re.IGNORECASE,
    )
    for m in pattern.finditer(ddl):
        from_cols = [c.strip().strip("`'").strip() for c in m.group(1).split(",")]
        to_table = m.group(2).strip("`'")
        to_cols = [c.strip().strip("`'").strip() for c in m.group(3).split(",")]
        from_table = ""
        pos = m.start()
        chunk = ddl[:pos]
        last_create = list(_CREATE_TABLE_RE.finditer(chunk))
        if last_create:
            from_table = last_create[-1].group(1).strip("`'")
        if from_table:
            fks.append((from_table, from_cols, to_table, to_cols))
    composite_count = sum(1 for _, from_cols, _, _ in fks if len(from_cols) > 1)
    return fks, composite_count


def extract_schema_from_metadata(meta: dict) -> tuple[set[str], dict[str, set[str]], dict[str, dict[str, dict]]]:
    tables = set(meta.get("tables", []))
    cols_by_table: dict[str, set[str]] = {}
    info_by_table: dict[str, dict[str, dict]] = {}
    for t, cols in (meta.get("columns_by_table") or {}).items():
        cols_set = set()
        info = {}
        for c in cols:
            name = c.get("COLUMN_NAME") or ""
            cols_set.add(name)
            info[name] = {
                "DATA_TYPE": (c.get("DATA_TYPE") or "").lower(),
                "IS_NULLABLE": (c.get("IS_NULLABLE") or "").upper(),
                "COLUMN_KEY": (c.get("COLUMN_KEY") or "").upper(),
                "COLUMN_TYPE": (c.get("COLUMN_TYPE") or "").lower(),
            }
        cols_by_table[t] = cols_set
        info_by_table[t] = info
    return tables, cols_by_table, info_by_table


def schema_difficulty(table_count: int, column_count: int) -> str:
    if table_count <= 3 and column_count <= 30:
        return "easy"
    if table_count <= 15 and column_count <= 150:
        return "medium"
    return "hard"


@dataclass
class SchemaMetrics:
    table_recall: float
    table_precision: float
    attr_recall: float
    attr_precision: float
    domain_type_recall: float
    domain_type_precision: float
    domain_null_recall: float
    domain_null_precision: float
    entity_pri_recall: float
    entity_pri_precision: float
    entity_uni_recall: float
    entity_uni_precision: float
    ref_fk_recall: float
    ref_fk_precision: float
    ref_fk_undirected_recall: float
    ref_fk_undirected_precision: float
    ref_composite_recall: float
    ref_composite_precision: float
    original_tables: int
    original_attrs: int
    predicted_tables: int
    predicted_attrs: int
    original_fks: int
    predicted_fks: int
    original_composite_fks: int
    predicted_composite_fks: int
    difficulty: str
    size: str
    content: str
    content_score: float
    matched_tables: int
    attr_matched: int
    domain_matched: int
    entity_original_constraints: int
    entity_predicted_constraints: int
    entity_matched_constraints: int
    fk_matched: int


def evaluate_one(
    safe_name: str,
    original_meta: dict,
    original_ddl: str,
    predicted_meta: dict,
    predicted_ddl: str,
    table_count: int,
    column_count: int,
) -> SchemaMetrics:
    orig_tables, orig_cols, orig_info = extract_schema_from_metadata(original_meta)
    pred_tables, pred_cols, pred_info = extract_schema_from_metadata(predicted_meta)
    orig_tables_norm = _norm_map(orig_tables)
    pred_tables_norm = _norm_map(pred_tables)
    matched_tables = set(orig_tables_norm) & set(pred_tables_norm)
    table_recall = len(matched_tables) / len(orig_tables) if orig_tables else 1.0
    table_precision = len(matched_tables) / len(pred_tables) if pred_tables else 1.0
    # Gold/Recreated attribute totals are computed over the FULL schemas (independent of
    # which tables the LLM matched), so the denominators are stable across LLMs and the
    # report reflects true recall/precision against the entire ground-truth schema.
    attr_original = sum(len(cols) for cols in orig_cols.values())
    attr_predicted = sum(len(cols) for cols in pred_cols.values())
    attr_match = 0
    domain_type_match = 0
    domain_type_total_orig = attr_original
    domain_type_total_pred = attr_predicted
    domain_null_match = 0
    domain_null_total_orig = attr_original
    domain_null_total_pred = attr_predicted
    domain_both_match = 0
    for tn in matched_tables:
        ot, pt = orig_tables_norm[tn], pred_tables_norm[tn]
        oc = orig_cols.get(ot, set())
        pc = pred_cols.get(pt, set())
        oc_norm = _norm_map(oc)
        pc_norm = _norm_map(pc)
        matched_cols = set(oc_norm) & set(pc_norm)
        attr_match += len(matched_cols)
        for cn in matched_cols:
            ocol, pcol = oc_norm[cn], pc_norm[cn]
            oi = orig_info.get(ot, {}).get(ocol, {})
            pi = pred_info.get(pt, {}).get(pcol, {})
            otype = (oi.get("DATA_TYPE") or "").lower()
            ptype = (pi.get("DATA_TYPE") or "").lower()
            type_ok = otype == ptype or (otype in ("int", "tinyint", "smallint", "mediumint", "bigint") and ptype in ("int", "tinyint", "smallint", "mediumint", "bigint")) or (otype in ("varchar", "char", "text") and ptype in ("varchar", "char", "text"))
            if type_ok:
                domain_type_match += 1
            onull = (oi.get("IS_NULLABLE") or "").upper() == "YES"
            pnull = (pi.get("IS_NULLABLE") or "").upper() == "YES"
            if onull == pnull:
                domain_null_match += 1
            if type_ok and (onull == pnull):
                domain_both_match += 1
    attr_recall = attr_match / attr_original if attr_original else 1.0
    attr_precision = attr_match / attr_predicted if attr_predicted else 1.0
    domain_type_recall = domain_type_match / domain_type_total_orig if domain_type_total_orig else 1.0
    domain_type_precision = domain_type_match / domain_type_total_pred if domain_type_total_pred else 1.0
    domain_null_recall = domain_null_match / domain_null_total_orig if domain_null_total_orig else 1.0
    domain_null_precision = domain_null_match / domain_null_total_pred if domain_null_total_pred else 1.0
    orig_pk, orig_uq = parse_ddl_primary_unique(original_ddl)
    pred_pk, pred_uq = parse_ddl_primary_unique(predicted_ddl)

    def pk_uq_match(orig_list: list, pred_list: list) -> tuple[int, int]:
        om = {(normalize_name(t), tuple(sorted(normalize_name(c) for c in cols))) for t, cols in orig_list}
        pm = {(normalize_name(t), tuple(sorted(normalize_name(c) for c in cols))) for t, cols in pred_list}
        return len(om & pm), len(om)

    pk_m, pk_orig = pk_uq_match(orig_pk, pred_pk)
    pred_pk_set = {(normalize_name(t), tuple(sorted(normalize_name(c) for c in cols))) for t, cols in pred_pk}
    entity_pri_recall = pk_m / pk_orig if pk_orig else 1.0
    entity_pri_precision = pk_m / len(pred_pk_set) if pred_pk_set else 1.0
    uq_m, uq_orig = pk_uq_match(orig_uq, pred_uq)
    pred_uq_set = {(normalize_name(t), tuple(sorted(normalize_name(c) for c in cols))) for t, cols in pred_uq}
    entity_uni_recall = uq_m / uq_orig if uq_orig else 1.0
    entity_uni_precision = uq_m / len(pred_uq_set) if pred_uq_set else 1.0
    orig_fks, orig_comp = parse_ddl_fks(original_ddl)
    pred_fks, pred_comp = parse_ddl_fks(predicted_ddl)
    orig_fk_set = {(normalize_name(t), tuple(normalize_name(c) for c in cols), normalize_name(tt), tuple(normalize_name(c) for c in refs)) for t, cols, tt, refs in orig_fks}
    pred_fk_set = {(normalize_name(t), tuple(normalize_name(c) for c in cols), normalize_name(tt), tuple(normalize_name(c) for c in refs)) for t, cols, tt, refs in pred_fks}
    fk_match = len(orig_fk_set & pred_fk_set)
    ref_fk_recall = fk_match / len(orig_fk_set) if orig_fk_set else 1.0
    ref_fk_precision = fk_match / len(pred_fk_set) if pred_fk_set else 1.0
    def _undirected_edge(t: str, cols: tuple, tt: str, refs: tuple) -> frozenset:
        return frozenset({(normalize_name(t), cols), (normalize_name(tt), refs)})
    orig_fk_undirected = {_undirected_edge(t, tuple(normalize_name(c) for c in cols), tt, tuple(normalize_name(c) for c in refs)) for t, cols, tt, refs in orig_fks}
    pred_fk_undirected = {_undirected_edge(t, tuple(normalize_name(c) for c in cols), tt, tuple(normalize_name(c) for c in refs)) for t, cols, tt, refs in pred_fks}
    fk_undirected_match = len(orig_fk_undirected & pred_fk_undirected)
    ref_fk_undirected_recall = fk_undirected_match / len(orig_fk_undirected) if orig_fk_undirected else 1.0
    ref_fk_undirected_precision = fk_undirected_match / len(pred_fk_undirected) if pred_fk_undirected else 1.0
    orig_comp_set = {(normalize_name(t), tuple(normalize_name(c) for c in cols)) for t, cols, _, _ in orig_fks if len(cols) > 1}
    pred_comp_set = {(normalize_name(t), tuple(normalize_name(c) for c in cols)) for t, cols, _, _ in pred_fks if len(cols) > 1}
    comp_match = len(orig_comp_set & pred_comp_set)
    ref_composite_recall = comp_match / len(orig_comp_set) if orig_comp_set else 1.0
    ref_composite_precision = comp_match / len(pred_comp_set) if pred_comp_set else 1.0
    labels = classify_schema(original_ddl, table_count, column_count)
    entity_orig_constraints = len(orig_pk) + len(orig_uq)
    entity_pred_constraints = len(pred_pk) + len(pred_uq)
    entity_matched_constraints = pk_m + uq_m
    return SchemaMetrics(
        table_recall=table_recall,
        table_precision=table_precision,
        attr_recall=attr_recall,
        attr_precision=attr_precision,
        domain_type_recall=domain_type_recall,
        domain_type_precision=domain_type_precision,
        domain_null_recall=domain_null_recall,
        domain_null_precision=domain_null_precision,
        entity_pri_recall=entity_pri_recall,
        entity_pri_precision=entity_pri_precision,
        entity_uni_recall=entity_uni_recall,
        entity_uni_precision=entity_uni_precision,
        ref_fk_recall=ref_fk_recall,
        ref_fk_precision=ref_fk_precision,
        ref_fk_undirected_recall=ref_fk_undirected_recall,
        ref_fk_undirected_precision=ref_fk_undirected_precision,
        ref_composite_recall=ref_composite_recall,
        ref_composite_precision=ref_composite_precision,
        original_tables=len(orig_tables),
        original_attrs=attr_original,
        predicted_tables=len(pred_tables),
        predicted_attrs=attr_predicted,
        original_fks=len(orig_fks),
        predicted_fks=len(pred_fks),
        original_composite_fks=orig_comp,
        predicted_composite_fks=pred_comp,
        difficulty=labels["size"],
        size=labels["size"],
        content=labels["content"],
        content_score=labels["content_score"],
        matched_tables=len(matched_tables),
        attr_matched=attr_match,
        domain_matched=domain_both_match,
        entity_original_constraints=entity_orig_constraints,
        entity_predicted_constraints=entity_pred_constraints,
        entity_matched_constraints=entity_matched_constraints,
        fk_matched=fk_match,
    )


def run_evaluation(llm_name: str) -> dict:
    index = load_json(SCHEMA_DIR / "index.json")
    datasets = index.get("datasets", [])
    input_dir = LLM_TRANSLATIONS / f"{TEXT2SCHEMA2_PREFIX}{llm_name}"
    if not input_dir.is_dir():
        return {"error": f"Directory not found: {input_dir}", "llm": llm_name}
    results_by_schema: dict[str, dict] = {}
    by_difficulty: dict[str, list[dict]] = {"easy": [], "medium": [], "hard": []}
    for ds in datasets:
        safe_name = ds.get("safe_name")
        if not safe_name:
            continue
        pred_path = input_dir / f"{safe_name}.json"
        if not pred_path.is_file():
            continue
        meta_path = SCHEMA_DIR / f"{safe_name}.metadata.json"
        ddl_path = SCHEMA_DIR / f"{safe_name}.sql"
        if not meta_path.is_file() or not ddl_path.is_file():
            continue
        try:
            original_meta = load_json(meta_path)
            original_ddl = ddl_path.read_text(encoding="utf-8")
            pred_data = load_json(pred_path)
            predicted_meta = pred_data.get("metadata") or {}
            predicted_ddl = pred_data.get("ddl") or ""
        except Exception as e:
            results_by_schema[safe_name] = {"error": str(e)}
            continue
        table_count = ds.get("table_count") or 0
        column_count = ds.get("column_count") or 0
        m = evaluate_one(
            safe_name,
            original_meta,
            original_ddl,
            predicted_meta,
            predicted_ddl,
            table_count,
            column_count,
        )
        d = {
            "tables": {"gold": m.original_tables, "recreated": m.predicted_tables, "matched": m.matched_tables},
            "attributes": {"gold": m.original_attrs, "recreated": m.predicted_attrs, "matched": m.attr_matched},
            "domain": {"gold": m.original_attrs, "recreated": m.predicted_attrs, "matched": m.domain_matched},
            "entity": {"gold": m.entity_original_constraints, "recreated": m.entity_predicted_constraints, "matched": m.entity_matched_constraints},
            "referential": {"gold": m.original_fks, "recreated": m.predicted_fks, "matched": m.fk_matched},
            "difficulty": m.difficulty,
        }
        results_by_schema[safe_name] = d
    def agg_element(items: list[dict], key: str) -> dict:
        g = sum(s[key]["gold"] for s in items)
        r = sum(s[key]["recreated"] for s in items)
        m = sum(s[key]["matched"] for s in items)
        hall = max(0, r - m)
        prec = m / r if r else 0.0
        rec = m / g if g else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
        return {"gold": g, "recreated": r, "matched": m, "hallucinated": hall, "precision": prec, "recall": rec, "f1": f1}
    all_items = list(results_by_schema.values())
    five_elements = {
        "tables": agg_element(all_items, "tables"),
        "attributes": agg_element(all_items, "attributes"),
        "domain": agg_element(all_items, "domain"),
        "entity": agg_element(all_items, "entity"),
        "referential": agg_element(all_items, "referential"),
    }
    by_difficulty_count = {"easy": 0, "medium": 0, "hard": 0}
    five_elements_by_difficulty: dict[str, dict] = {}
    for diff in ("easy", "medium", "hard"):
        items = [s for s in all_items if s.get("difficulty") == diff]
        by_difficulty_count[diff] = len(items)
        five_elements_by_difficulty[diff] = {
            "tables": agg_element(items, "tables"),
            "attributes": agg_element(items, "attributes"),
            "domain": agg_element(items, "domain"),
            "entity": agg_element(items, "entity"),
            "referential": agg_element(items, "referential"),
        } if items else {k: {"gold": 0, "recreated": 0, "matched": 0, "hallucinated": 0, "precision": 0.0, "recall": 0.0, "f1": 0.0} for k in ("tables", "attributes", "domain", "entity", "referential")}
    summary = {
        "llm": llm_name,
        "total_schemas": len(results_by_schema),
        "per_schema": results_by_schema,
        "five_elements": five_elements,
        "by_difficulty_count": by_difficulty_count,
        "five_elements_by_difficulty": five_elements_by_difficulty,
    }
    return summary


def print_report(summary: dict) -> None:
    if "error" in summary:
        print(f"Error: {summary['error']}", file=sys.stderr)
        return
    llm = summary["llm"]
    print(f"\n{'='*60}\nText2Schema2 — LLM: {llm}\n{'='*60}")
    print(f"Total schemas evaluated: {summary['total_schemas']}")
    fe = summary.get("five_elements") or {}
    for name, row in fe.items():
        print(f"  {name}: Gold={row['gold']} Recreated={row['recreated']} Matched={row['matched']} Hallucinated={row['hallucinated']} P={row['precision']:.3f} R={row['recall']:.3f} F1={row['f1']:.3f}")


# Table labels (short so they fit in column; full names in METRICS_SECTION)
FIVE_ELEMENT_NAMES = [
    ("tables", "1. Schema: Table name"),
    ("attributes", "2. Schema: Attributes"),
    ("domain", "3. Domain: types, NULL/NOT NULL"),
    ("entity", "4. Entity: Primary, UNIQUE (single/multi col.)"),
    ("referential", "5. Referential: Foreign Keys (single/multi col.)"),
]

METRICS_SECTION = """
Five schema elements evaluated (Gold = original, Recreated = LLM output, Matched = correct).
  Hallucinated = Recreated - Matched.  Precision = Matched/Recreated.  Recall = Matched/Gold.  F1 = 2*P*R/(P+R).

  Schema types: easy = ≤3 tables & ≤30 columns; medium = ≤15 tables & ≤150 columns; hard = else.

  1. Schema: Table name
  2. Schema: Attributes
  3. Domain integrity: data types and NULL/NOT NULL per column (both must agree)
  4. Entity integrity: PRIMARY KEY and UNIQUE constraints (single- and multi-column)
  5. Referential integrity: FOREIGN KEY constraints (single- and multi-column)

"""


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
        p = row_data.get("precision", 0)
        rec = row_data.get("recall", 0)
        f1 = row_data.get("f1", 0)
        out.append(_table_row([label, g, r, m, h, _fmt(p), _fmt(rec), _fmt(f1)], widths))
    return out


def build_five_elements_report(summaries: list[dict]) -> list[str]:
    valid = [s for s in summaries if "error" not in s and s.get("five_elements")]
    if not valid:
        return []
    lines = []
    w_elem = 48
    col_w = [10, 10, 8, 12, 10, 8, 8]
    widths = [w_elem] + col_w
    headers = ["Element", "Gold", "Recreated", "Matched", "Hallucinated", "Precision", "Recall", "F1"]
    for i, s in enumerate(valid):
        if i > 0:
            lines.append("")
            lines.append("")
        llm = s.get("llm", "?")
        lines.append("")
        lines.append(f"  ---  LLM: {llm}  (schemas: {s.get('total_schemas', 0)})  ---")
        lines.append("")
        lines.append("  OVERALL")
        lines.append("")
        lines.extend(_one_table(s.get("five_elements") or {}, widths, headers))
        by_diff = s.get("five_elements_by_difficulty") or {}
        counts = s.get("by_difficulty_count") or {}
        for diff in ("easy", "medium", "hard"):
            n = counts.get(diff, 0)
            lines.append("")
            lines.append(f"  Schema type: {diff.upper()}  (n = {n})")
            lines.append("")
            lines.extend(_one_table(by_diff.get(diff) or {}, widths, headers))
    return lines


def write_report_txt(summaries: list[dict], report_path: Path) -> None:
    lines = build_five_elements_report(summaries)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("Text2Schema2 — RESULTS (5 schema elements)\n")
        f.write("=" * 80 + "\n")
        f.write("\n")
        f.write(METRICS_SECTION)
        f.write("\n")
        for line in lines:
            f.write(line + "\n")
        f.write("\n")
        f.write("=" * 80 + "\n")
    print(f"Saved report: {report_path}")


def main() -> None:
    llms = []
    for d in sorted(LLM_TRANSLATIONS.iterdir()):
        if d.is_dir() and d.name.startswith(TEXT2SCHEMA2_PREFIX):
            name = d.name[len(TEXT2SCHEMA2_PREFIX):]
            if name and list(d.glob("*.json")):
                llms.append(name)
    if not llms:
        print("No Text2Schema2_* folders with JSON found.", file=sys.stderr)
        sys.exit(1)
    print("Text2Schema2 evaluation — LLMs:", llms)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    all_summaries = []
    for llm in llms:
        summary = run_evaluation(llm)
        all_summaries.append(summary)
        print_report(summary)
        out_path = RESULTS_DIR / f"Text2Schema2_{llm}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, default=str)
        print(f"\nSaved: {out_path}")
    write_report_txt(all_summaries, RESULTS_DIR / "text2schema2_report.txt")
    print("\nReport: 5 schema elements (Gold, Recreated, Matched, Hallucinated, Precision, Recall, F1) in text2schema2_report.txt.")


if __name__ == "__main__":
    main()
