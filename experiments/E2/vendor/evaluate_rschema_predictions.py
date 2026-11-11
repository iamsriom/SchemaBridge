#!/usr/bin/env python3
"""
Evaluate RSchema LLM predictions (e.g. GPT-4o-mini) vs gold schemas in annotation.jsonl.

Reuses metrics from Text2ER/Results Text2Schema2 evaluation (5 elements: tables, attributes,
domain, entity, referential) with RSchema-aware name normalization (spaces, plurals).
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TEXT2ER_ROOT = Path("/data/Text2ER")
EVAL_ROOT = Path("/data/Results/Text2Schema2Results")
sys.path.insert(0, str(SCRIPT_DIR))

import evaluate_text2schema2 as ev  # noqa: E402

def schema_difficulty(*args, **kwargs):  # pragma: no cover - unused by E2 PRIMARY
    return {"size": "medium", "content": "medium", "content_score": 0.0}

RSCHEMA_DIR = Path("/data/RSchema")
ANNOTATION_PATH = RSCHEMA_DIR / "annotation.jsonl"
DEFAULT_PRED_DIR = Path("/data/RSchema_Results/text2schema_gpt4omini")
OUT_DIR = Path("/data/RSchema_Results/eval_gpt4omini")


def normalize_rschema_name(s: str) -> str:
    """Match gold ('Airplane Number') with pred ('airplane_number', 'airplanes')."""
    s = re.sub(r"[\s_\-]+", "", (s or "").strip().lower())
    for suf in ("members", "member", "details", "records", "record"):
        if len(s) > len(suf) + 2 and s.endswith(suf):
            s = s[: -len(suf)]
            break
    if len(s) > 3 and s.endswith("s") and not s.endswith("ss"):
        s = s[:-1]
    return s


def _scalar_name(value) -> str:
    """Coerce gold FK/column reference to a string (some records nest dict values)."""
    while isinstance(value, dict):
        if not value:
            return ""
        value = next(iter(value.values()))
    return str(value or "")


def attr_to_sql_name(attr: str) -> str:
    return re.sub(r"\s+", "_", _scalar_name(attr)).lower()


def table_to_sql_name(name: str) -> str:
    return re.sub(r"\s+", "_", _scalar_name(name)).lower()


def gold_answer_to_metadata_and_ddl(answer: dict, database: str = "gold") -> tuple[dict, str]:
    """Convert RSchema structured answer to metadata + synthetic DDL for evaluation."""
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
        sql_table = table_to_sql_name(table_name)

        for i, attr in enumerate(attrs, 1):
            sql_col = attr_to_sql_name(attr)
            is_pk = attr in pk_cols
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
                    "COLUMN_KEY": "PRI" if is_pk else "",
                    "EXTRA": "",
                    "COLUMN_COMMENT": "",
                }
            )
            col_lines.append(f"  `{sql_col}` varchar(255) NOT NULL")

        pk_sql_cols = [attr_to_sql_name(c) for c in pk_cols if c]
        if pk_sql_cols:
            col_lines.append(f"  PRIMARY KEY (`{'`, `'.join(pk_sql_cols)}`)")

        for from_attr, ref in (fks.items() if isinstance(fks, dict) else []):
            if not isinstance(ref, dict) or not ref:
                continue
            to_table, to_col = next(iter(ref.items()))
            from_sql = attr_to_sql_name(from_attr)
            to_table_sql = table_to_sql_name(to_table)
            to_col_sql = attr_to_sql_name(to_col)
            col_lines.append(
                f"  CONSTRAINT `{sql_table}_ibfk_{from_sql}` FOREIGN KEY (`{from_sql}`) "
                f"REFERENCES `{to_table_sql}` (`{to_col_sql}`) "
                f"ON DELETE CASCADE ON UPDATE CASCADE"
            )

        columns_by_table[table_name] = col_objs
        body = ",\n".join(col_lines)
        ddl_parts.append(
            f"CREATE TABLE `{sql_table}` (\n{body}\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;"
        )

    meta = {
        "database": database,
        "tables": tables,
        "columns_by_table": columns_by_table,
    }
    return meta, "\n\n".join(ddl_parts)


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def f1(prec: float, rec: float) -> float:
    return 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0


def evaluate_predictions(
    pred_dir: Path,
    annotation_path: Path = ANNOTATION_PATH,
    record_ids: list[str] | None = None,
) -> dict:
    ev.normalize_name = normalize_rschema_name

    gold_by_id = {r["id"]: r for r in load_jsonl(annotation_path) if r.get("id")}
    pred_files = sorted(pred_dir.glob("*.json"))
    if record_ids:
        want = set(record_ids)
        pred_files = [p for p in pred_files if p.stem in want]

    per_record: dict[str, dict] = {}
    metrics_list = []

    for pred_path in pred_files:
        if pred_path.name == "index.jsonl":
            continue
        try:
            pred_data = json.loads(pred_path.read_text(encoding="utf-8"))
            rid = pred_data.get("id") or pred_path.stem
        except Exception:
            per_record[pred_path.stem] = {"error": "invalid json"}
            continue
        gold_rec = gold_by_id.get(rid)
        if not gold_rec:
            per_record[rid] = {"error": "no gold record"}
            continue
        if pred_data.get("error") or not pred_data.get("ddl"):
            per_record[rid] = {"error": pred_data.get("error", "missing ddl")}
            continue

        answer = gold_rec.get("answer") or {}
        table_count, column_count = 0, 0
        for tdef in answer.values():
            if isinstance(tdef, dict):
                table_count += 1
                column_count += len(tdef.get("Attributes") or [])

        orig_meta, orig_ddl = gold_answer_to_metadata_and_ddl(answer, database=f"gold_{rid[:8]}")
        pred_meta = pred_data.get("metadata") or {}
        pred_ddl = pred_data.get("ddl") or ""

        m = ev.evaluate_one(
            rid,
            orig_meta,
            orig_ddl,
            pred_meta,
            pred_ddl,
            table_count,
            column_count,
        )

        gold_tables = sorted(answer.keys())
        pred_tables = list((pred_meta.get("tables") or []))
        gold_fk_count = sum(
            len(tdef.get("Foreign key") or {})
            for tdef in answer.values()
            if isinstance(tdef, dict)
        )

        label = f"text_{pred_data.get('text_number', pred_path.stem):04d}" if pred_data.get("text_number") else rid
        per_record[label] = {
            "text_number": pred_data.get("text_number"),
            "id": rid,
            "difficulty": m.difficulty,
            "gold_tables": gold_tables,
            "pred_tables": pred_tables,
            "tables": {
                "gold": m.original_tables,
                "pred": m.predicted_tables,
                "matched": m.matched_tables,
                "recall": m.table_recall,
                "precision": m.table_precision,
            },
            "attributes": {
                "gold": m.original_attrs,
                "pred": m.predicted_attrs,
                "matched": m.attr_matched,
                "recall": m.attr_recall,
                "precision": m.attr_precision,
            },
            "entity_pk": {
                "recall": m.entity_pri_recall,
                "precision": m.entity_pri_precision,
            },
            "referential": {
                "gold_fks": m.original_fks,
                "pred_fks": m.predicted_fks,
                "matched": m.fk_matched,
                "recall": m.ref_fk_recall,
                "precision": m.ref_fk_precision,
                "undirected_recall": m.ref_fk_undirected_recall,
                "undirected_precision": m.ref_fk_undirected_precision,
            },
            "gold_fk_count_structured": gold_fk_count,
        }
        metrics_list.append(m)

    # Aggregate micro counts
    def agg(key_gold, key_pred, key_match):
        g = sum(getattr(m, key_gold) for m in metrics_list)
        r = sum(getattr(m, key_pred) for m in metrics_list)
        mt = sum(getattr(m, key_match) for m in metrics_list)
        p = mt / r if r else 0.0
        rc = mt / g if g else 0.0
        return {"gold": g, "pred": r, "matched": mt, "precision": p, "recall": rc, "f1": f1(p, rc)}

    summary = {
        "n_evaluated": len(metrics_list),
        "pred_dir": str(pred_dir),
        "tables": agg("original_tables", "predicted_tables", "matched_tables"),
        "attributes": agg("original_attrs", "predicted_attrs", "attr_matched"),
        "entity": agg(
            "entity_original_constraints",
            "entity_predicted_constraints",
            "entity_matched_constraints",
        ),
        "referential_directed": agg("original_fks", "predicted_fks", "fk_matched"),
        "per_record": per_record,
        "mean_table_recall": sum(m.table_recall for m in metrics_list) / len(metrics_list) if metrics_list else 0,
        "mean_attr_recall": sum(m.attr_recall for m in metrics_list) / len(metrics_list) if metrics_list else 0,
        "mean_fk_recall": sum(m.ref_fk_recall for m in metrics_list) / len(metrics_list) if metrics_list else 0,
        "mean_fk_undirected_recall": sum(m.ref_fk_undirected_recall for m in metrics_list) / len(metrics_list) if metrics_list else 0,
    }
    return summary


def format_report(summary: dict) -> str:
    lines = [
        "RSchema Text2Schema Evaluation — GPT-4o-mini vs Gold",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"Predictions: {summary['pred_dir']}",
        f"Records evaluated: {summary['n_evaluated']}",
        "",
        "Aggregate (micro) — name-normalized matching (spaces/plurals/suffixes):",
        "",
    ]
    for elem in ("tables", "attributes", "entity", "referential_directed"):
        row = summary[elem]
        lines.append(
            f"  {elem:22s}  gold={row['gold']:3d}  pred={row['pred']:3d}  matched={row['matched']:3d}  "
            f"P={row['precision']:.3f}  R={row['recall']:.3f}  F1={row['f1']:.3f}"
        )
    lines.extend(
        [
            "",
            f"Mean per-schema table recall:  {summary['mean_table_recall']:.3f}",
            f"Mean per-schema attr recall:   {summary['mean_attr_recall']:.3f}",
            f"Mean per-schema FK recall:     {summary['mean_fk_recall']:.3f} (directed)",
            f"Mean per-schema FK recall:     {summary['mean_fk_undirected_recall']:.3f} (undirected)",
            "",
            "Per-record detail:",
            "-" * 72,
        ]
    )
    for rid, rec in summary["per_record"].items():
        if rec.get("error"):
            lines.append(f"\n{rid}: ERROR — {rec['error']}")
            continue
        lines.append(f"\n{rid}  [{rec['difficulty']}]")
        lines.append(f"  Gold tables:  {', '.join(rec['gold_tables'])}")
        lines.append(f"  Pred tables:  {', '.join(rec['pred_tables'])}")
        lines.append(
            f"  Tables:  matched {rec['tables']['matched']}/{rec['tables']['gold']} gold  "
            f"(R={rec['tables']['recall']:.2f} P={rec['tables']['precision']:.2f})"
        )
        lines.append(
            f"  Attrs:   matched {rec['attributes']['matched']}/{rec['attributes']['gold']} gold  "
            f"(R={rec['attributes']['recall']:.2f} P={rec['attributes']['precision']:.2f})"
        )
        lines.append(
            f"  FKs:     matched {rec['referential']['matched']}/{rec['referential']['gold_fks']} gold  "
            f"(directed R={rec['referential']['recall']:.2f}, undirected R={rec['referential']['undirected_recall']:.2f})"
        )
        lines.append(
            f"  PK recall: {rec['entity_pk']['recall']:.2f}  (gold structured FKs: {rec['gold_fk_count_structured']})"
        )

    lines.append("\n" + ev.METRICS_SECTION.strip())
    return "\n".join(lines) + "\n"


def write_report(summary: dict, out_path: Path) -> str:
    text = format_report(summary)
    out_path.write_text(text, encoding="utf-8")
    return text


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate RSchema predictions vs gold")
    parser.add_argument("--pred-dir", type=Path, default=DEFAULT_PRED_DIR)
    parser.add_argument("--annotation", type=Path, default=ANNOTATION_PATH)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    args = parser.parse_args()

    if not args.pred_dir.is_dir():
        print("Error: pred dir not found:", args.pred_dir, file=sys.stderr)
        sys.exit(1)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    summary = evaluate_predictions(args.pred_dir, args.annotation)
    json_path = args.out_dir / "eval_summary.json"
    report_path = args.out_dir / "eval_report.txt"
    json_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    report_text = write_report(summary, report_path)
    print(report_text)
    print(f"Wrote {json_path}")


if __name__ == "__main__":
    main()
