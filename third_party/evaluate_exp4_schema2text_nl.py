#!/usr/bin/env python3
"""
Evaluate RSchema Exp4 schema2text outputs vs gold NL references.

Reads hypothesis text from:
    <DATA_ROOT>/RSchema_ExpResults4/Experiment2/schema2text_<llm>/NNNN.txt

Gold reference (natural language schema description):
    <DATA_ROOT>/RSchema/annotation.jsonl  field "question" (518 records, order 0001..0518)

Metrics:
    BLEU-4 (corpus + sentence mean), ROUGE-L, METEOR, BERTScore (P/R/F1),
    schema coverage (fraction of DDL tables/columns mentioned in generated NL).

Outputs:
    <DATA_ROOT>/RSchema_ExpResults4/Experiment2/Results/schema2text_evaluation.txt
    <DATA_ROOT>/RSchema_ExpResults4/Experiment2/Results/schema2text_evaluation.json
    <DATA_ROOT>/RSchema_ExpResults4/Experiment2/Results/per_record_<llm>.jsonl

Usage:
    python evaluate_exp4_schema2text_nl.py
    python evaluate_exp4_schema2text_nl.py --skip-bertscore
    python evaluate_exp4_schema2text_nl.py --bertscore-device cuda:0
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import sacrebleu
from nltk.tokenize import word_tokenize
from nltk.translate.meteor_score import meteor_score
from rouge_score import rouge_scorer

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_ROOT = Path("/data") if Path("/data").is_dir() else SCRIPT_DIR.parent.parent
DEFAULT_BASE = DATA_ROOT / "RSchema_ExpResults4" / "Experiment2"
DEFAULT_GOLD = DATA_ROOT / "RSchema" / "annotation.jsonl"
DEFAULT_DDL = DATA_ROOT / "RSchema" / "annotation_ddl.jsonl"
DEFAULT_OUT_DIR = DEFAULT_BASE / "Results"

LLMS = ("codellama13b", "llama31", "deepseek")

NL_BUG_MARKERS: tuple[str, ...] = (
    "\u0120",
    "Ġ",
    "Ċ",
    "▁",
    "<|endoftext|>",
    "[INST]",
    "[/INST]",
)


def sanitize_nl_text(text: str) -> str:
    if not text:
        return text
    text = text.replace("\u0120", " ")
    text = text.replace("Ċ", "\n").replace("▁", " ")
    lines = [" ".join(line.split()) for line in text.splitlines()]
    return "\n".join(ln for ln in lines if ln).strip()


def validate_nl_text(text: str, *, min_chars: int = 80) -> tuple[bool, str]:
    if not text or not text.strip():
        return False, "empty_nl_text"
    if text.strip().startswith("ERROR:"):
        return False, "error_marker_in_text"
    for marker in NL_BUG_MARKERS:
        if marker in text:
            return False, f"tokenization_artifact:{marker!r}"
    stripped = text.strip()
    if len(stripped) < min_chars:
        return False, f"too_short:{len(stripped)}"
    if sum(c.isalpha() for c in stripped) < 30:
        return False, "insufficient_prose"
    return True, ""


def serial_stem(n: int) -> str:
    return f"{n:04d}"


def norm_ident(name: str) -> str:
    return re.sub(r'[\s_\-`"]+', "", (name or "").strip().lower())


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_gold_references(gold_path: Path) -> list[dict]:
    records: list[dict] = []
    with gold_path.open(encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            records.append(
                {
                    "text_number": i,
                    "serial": serial_stem(i),
                    "id": rec.get("id", ""),
                    "gold_nl": (rec.get("question") or "").strip(),
                    "answer": rec.get("answer"),
                }
            )
    return records


def _load_ddl_by_id(ddl_path: Path) -> dict[str, str]:
    by_id: dict[str, str] = {}
    if not ddl_path.is_file():
        return by_id
    for rec in load_jsonl(ddl_path):
        rid = rec.get("id")
        answer = rec.get("answer")
        if rid and isinstance(answer, str) and answer.strip():
            by_id[rid] = answer.strip()
    return by_id


def _sql_ident(name: object) -> str:
    if isinstance(name, dict):
        if not name:
            return "col"
        _key, val = next(iter(name.items()))
        return _sql_ident(val)
    return re.sub(r"\s+", "_", str(name or "").strip()).lower()


def structured_answer_to_ddl(answer: dict, database: str) -> str:
    ddl_parts: list[str] = [f"-- Schema for database: {database}"]
    for table_name, tdef in answer.items():
        if not isinstance(tdef, dict):
            continue
        sql_table = _sql_ident(table_name)
        attrs = list(tdef.get("Attributes") or [])
        pk_cols = set(tdef.get("Primary key") or [])
        fks = tdef.get("Foreign key") or {}
        col_lines: list[str] = []
        for attr in attrs:
            sql_col = _sql_ident(attr)
            col_lines.append(f"  `{sql_col}` varchar(255) NOT NULL")
        pk_sql = [_sql_ident(c) for c in pk_cols if c]
        if pk_sql:
            col_lines.append(f"  PRIMARY KEY (`{'`, `'.join(pk_sql)}`)")
        if isinstance(fks, dict):
            for from_attr, ref in fks.items():
                if not isinstance(ref, dict) or not ref:
                    continue
                to_table, to_col = next(iter(ref.items()))
                while isinstance(to_col, dict) and to_col:
                    to_table, to_col = next(iter(to_col.items()))
                from_sql = _sql_ident(from_attr)
                col_lines.append(
                    f"  CONSTRAINT `{sql_table}_ibfk_{from_sql}` FOREIGN KEY (`{from_sql}`) "
                    f"REFERENCES `{_sql_ident(to_table)}` (`{_sql_ident(to_col)}`) "
                    f"ON DELETE CASCADE ON UPDATE CASCADE"
                )
        body = ",\n".join(col_lines)
        ddl_parts.append(
            f"CREATE TABLE `{sql_table}` (\n{body}\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;"
        )
    return "\n\n".join(ddl_parts)


def gold_ddl_for_record(rec: dict, ddl_by_id: dict[str, str]) -> str:
    rid = rec.get("id") or ""
    if rid in ddl_by_id:
        return ddl_by_id[rid]
    answer = rec.get("answer")
    if isinstance(answer, dict) and answer:
        database = f"rschema_{int(rec.get('text_number') or 0):04d}"
        return structured_answer_to_ddl(answer, database=database)
    return ""


def extract_ddl_elements(ddl: str) -> dict[str, set[str]]:
    tables: set[str] = set()
    columns: set[str] = set()
    if not ddl or not ddl.strip():
        return {"tables": tables, "columns": columns, "all": set()}

    blocks = re.split(r"(?=CREATE\s+TABLE)", ddl, flags=re.IGNORECASE)
    for block in blocks:
        tm = re.search(r"CREATE\s+TABLE\s+[`']?(\w+)[`']?", block, re.IGNORECASE)
        if not tm:
            continue
        tables.add(norm_ident(tm.group(1)))
        body_m = re.search(r"\((.*)\)\s*(?:ENGINE|;)", block, re.DOTALL | re.IGNORECASE)
        if not body_m:
            body_m = re.search(r"\((.*)\)", block, re.DOTALL)
        if not body_m:
            continue
        for line in body_m.group(1).split("\n"):
            line = line.strip().rstrip(",")
            if not line:
                continue
            upper = line.upper()
            if upper.startswith(
                ("PRIMARY", "CONSTRAINT", "FOREIGN", "UNIQUE", "KEY", "INDEX", "CHECK")
            ):
                continue
            cm = re.match(r"[`']?(\w+)[`']?", line)
            if cm:
                columns.add(norm_ident(cm.group(1)))

    return {"tables": tables, "columns": columns, "all": tables | columns}


def element_mentioned(element: str, text: str) -> bool:
    el = norm_ident(element)
    if not el:
        return False
    compact = norm_ident(text)
    return el in compact


def schema_coverage(elements: set[str], text: str) -> dict[str, float | int]:
    if not elements:
        return {"matched": 0, "total": 0, "coverage": 1.0}
    matched = sum(1 for e in elements if element_mentioned(e, text))
    total = len(elements)
    return {
        "matched": matched,
        "total": total,
        "coverage": matched / total,
    }


def compute_schema_coverage_metrics(
    ddl: str, hyp: str, gold_nl: str
) -> dict[str, float | int]:
    elems = extract_ddl_elements(ddl)
    hyp_all = schema_coverage(elems["all"], hyp)
    hyp_tables = schema_coverage(elems["tables"], hyp)
    hyp_columns = schema_coverage(elems["columns"], hyp)
    gold_all = schema_coverage(elems["all"], gold_nl)
    return {
        "ddl_tables": len(elems["tables"]),
        "ddl_columns": len(elems["columns"]),
        "ddl_elements": len(elems["all"]),
        "schema_coverage": hyp_all["coverage"],
        "schema_table_coverage": hyp_tables["coverage"],
        "schema_column_coverage": hyp_columns["coverage"],
        "schema_coverage_matched": hyp_all["matched"],
        "schema_coverage_total": hyp_all["total"],
        "gold_schema_coverage": gold_all["coverage"],
    }


def ensure_nltk_data() -> None:
    import nltk

    for pkg in ("punkt", "punkt_tab", "wordnet", "omw-1.4"):
        nltk.download(pkg, quiet=True)


def _score_one_pair(ref: str, hyp: str) -> tuple[float, float, float, float]:
    """Per-record BLEU, ROUGE-L, METEOR."""
    ensure_nltk_data()
    rouge = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    sb = sacrebleu.sentence_bleu(hyp, [ref]).score
    rs = rouge.score(ref, hyp)
    ref_tok = word_tokenize(ref.lower())
    hyp_tok = word_tokenize(hyp.lower())
    met = meteor_score([ref_tok], hyp_tok)
    return sb, rs["rougeL"].fmeasure, met, rs["rougeL"].fmeasure


def compute_pair_metrics(
    refs: list[str],
    hyps: list[str],
    *,
    skip_bertscore: bool,
    bertscore_device: str = "cpu",
    workers: int = 8,
    label: str = "",
) -> dict:
    ensure_nltk_data()

    # HISTORICAL BUG (fixed): this used ``corpus_bleu(hyps, [[r] for r in refs])``, which hands
    # sacrebleu one reference *stream* per record instead of ONE stream holding all references.
    # The correct layout for a single-reference corpus is ``corpus_bleu(hyps, [refs])``.
    bleu_corpus = sacrebleu.corpus_bleu(hyps, [list(refs)])

    sent_bleu: list[float] = []
    rougeL: list[float] = []
    meteors: list[float] = []

    pairs = list(zip(refs, hyps))
    n_workers = max(1, min(workers, len(pairs)))
    print(f"  [{label}] Scoring {len(pairs)} pairs (workers={n_workers})...", flush=True)

    if n_workers == 1:
        for ref, hyp in pairs:
            row = _score_one_pair(ref, hyp)
            sent_bleu.append(row[0])
            rougeL.append(row[1])
            meteors.append(row[2])
    else:
        with ProcessPoolExecutor(max_workers=n_workers) as pool:
            futures = {
                pool.submit(_score_one_pair, ref, hyp): i for i, (ref, hyp) in enumerate(pairs)
            }
            rows: list[tuple[float, ...] | None] = [None] * len(pairs)
            done = 0
            for fut in as_completed(futures):
                rows[futures[fut]] = fut.result()
                done += 1
                if done % 100 == 0 or done == len(pairs):
                    print(f"  [{label}] Per-pair metrics: {done}/{len(pairs)}", flush=True)
            for row in rows:
                assert row is not None
                sent_bleu.append(row[0])
                rougeL.append(row[1])
                meteors.append(row[2])

    out: dict = {
        "bleu_corpus": bleu_corpus.score,
        "bleu_corpus_precisions": list(bleu_corpus.precisions),
        "bleu_sentence_mean": sum(sent_bleu) / len(sent_bleu),
        "rougeL_f1": sum(rougeL) / len(rougeL),
        "meteor": sum(meteors) / len(meteors),
        "gold_chars_mean": sum(len(r) for r in refs) / len(refs),
        "hyp_chars_mean": sum(len(h) for h in hyps) / len(hyps),
    }

    if not skip_bertscore:
        import bert_score

        print(f"  [{label}] BERTScore on {bertscore_device}...", flush=True)
        P, R, F1 = bert_score.score(
            hyps,
            refs,
            lang="en",
            verbose=False,
            batch_size=16,
            device=bertscore_device,
        )
        out["bertscore_precision"] = float(P.mean())
        out["bertscore_recall"] = float(R.mean())
        out["bertscore_f1"] = float(F1.mean())

    return out


def evaluate_llm(
    llm: str,
    base_dir: Path,
    gold_records: list[dict],
    ddl_by_id: dict[str, str],
    out_dir: Path,
    *,
    skip_bertscore: bool,
    bertscore_device: str = "cpu",
    workers: int = 8,
) -> dict:
    pred_dir = base_dir / f"schema2text_{llm}"
    pairs: list[dict] = []
    invalid: list[dict] = []
    missing: list[str] = []

    for rec in gold_records:
        serial = rec["serial"]
        gold = rec["gold_nl"]
        txt_path = pred_dir / f"{serial}.txt"
        json_path = pred_dir / f"{serial}.json"
        if not txt_path.is_file():
            missing.append(serial)
            continue

        hyp_raw = txt_path.read_text(encoding="utf-8")
        hyp = sanitize_nl_text(hyp_raw)
        ok, reason = validate_nl_text(hyp)

        ddl = ""
        if json_path.is_file():
            try:
                meta = json.loads(json_path.read_text(encoding="utf-8"))
                ddl = (meta.get("ddl") or "").strip()
            except Exception:
                pass
        if not ddl:
            ddl = gold_ddl_for_record(rec, ddl_by_id)

        entry = {
            "serial": serial,
            "text_number": rec["text_number"],
            "id": rec["id"],
            "gold_nl": gold,
            "hyp_nl": hyp,
            "ddl": ddl,
        }
        if not ok:
            invalid.append({**entry, "skip_reason": reason})
            continue
        if not gold:
            invalid.append({**entry, "skip_reason": "empty_gold_reference"})
            continue
        pairs.append(entry)

    per_record: list[dict] = []
    for p in pairs:
        cov = compute_schema_coverage_metrics(p["ddl"], p["hyp_nl"], p["gold_nl"])
        per_record.append({**p, **cov})

    refs = [p["gold_nl"] for p in pairs]
    hyps = [p["hyp_nl"] for p in pairs]

    metrics: dict = {}
    if refs:
        metrics = compute_pair_metrics(
            refs,
            hyps,
            skip_bertscore=skip_bertscore,
            bertscore_device=bertscore_device,
            workers=workers,
            label=llm,
        )
        metrics["schema_coverage_mean"] = sum(r["schema_coverage"] for r in per_record) / len(
            per_record
        )
        metrics["schema_table_coverage_mean"] = sum(
            r["schema_table_coverage"] for r in per_record
        ) / len(per_record)
        metrics["schema_column_coverage_mean"] = sum(
            r["schema_column_coverage"] for r in per_record
        ) / len(per_record)
        metrics["gold_schema_coverage_mean"] = sum(
            r["gold_schema_coverage"] for r in per_record
        ) / len(per_record)

    per_record_path = out_dir / f"per_record_{llm}.jsonl"
    per_record_path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in per_record) + "\n",
        encoding="utf-8",
    )

    return {
        "llm": llm,
        "pred_dir": str(pred_dir),
        "total_records": len(gold_records),
        "evaluated": len(pairs),
        "invalid": len(invalid),
        "missing": len(missing),
        "invalid_records": invalid,
        "missing_serials": missing,
        "per_record_path": str(per_record_path),
        "metrics": metrics,
    }


def fmt(v: float | int | None, width: int = 10) -> str:
    if v is None:
        return "n/a".rjust(width)
    if isinstance(v, float):
        return f"{v:.4f}".rjust(width)
    return str(v).rjust(width)


def write_report(
    summaries: list[dict],
    out_path: Path,
    *,
    skip_bertscore: bool,
    gold_path: Path,
    base_dir: Path,
) -> None:
    lines: list[str] = []
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines.append("RSchema Exp4 Schema-to-Text NL Evaluation")
    lines.append("=" * 100)
    lines.append(f"Generated: {ts}")
    lines.append("")
    lines.append("Task: Compare LLM-generated schema descriptions (DDL -> NL) to gold NL text.")
    lines.append(f"Gold reference: {gold_path} field 'question' (518 records, order 0001..0518).")
    lines.append(f"Hypothesis: {base_dir}/schema2text_<llm>/NNNN.txt")
    lines.append("")
    lines.append("Metrics:")
    lines.append("  BLEU-4        — corpus BLEU (sacrebleu); also mean sentence BLEU")
    lines.append("  ROUGE-L       — longest common subsequence F1, stemmed (rouge-score)")
    lines.append("  METEOR        — synonym-aware alignment (NLTK)")
    if not skip_bertscore:
        lines.append("  BERTScore F1  — contextual embedding similarity (roberta-large)")
    lines.append("  Schema Cov.   — fraction of DDL tables+columns mentioned in generated NL")
    lines.append("  Table Cov.    — fraction of DDL tables mentioned in generated NL")
    lines.append("  Column Cov.   — fraction of DDL columns mentioned in generated NL")
    lines.append("  Gold Sch.Cov. — schema coverage of gold reference NL (baseline)")
    lines.append("")
    lines.append(
        "Invalid hypotheses (ERROR:, tokenizer artifacts, too short) are excluded from metrics."
    )
    lines.append("")

    header = [
        "LLM",
        "Eval",
        "Skip",
        "Miss",
        "BLEU-4",
        "SentBLEU",
        "ROUGE-L",
        "METEOR",
    ]
    if not skip_bertscore:
        header.append("BS-F1")
    header.extend(
        [
            "SchemaCov",
            "TableCov",
            "ColCov",
            "GoldCov",
        ]
    )

    widths = [14, 5, 5, 5] + [10] * (len(header) - 4)
    lines.append("TABLE 1 — SUMMARY (higher is better)")
    lines.append("-" * 100)
    lines.append(" | ".join(h.ljust(w) for h, w in zip(header, widths)))
    lines.append("-" * 100)

    for s in summaries:
        m = s.get("metrics") or {}
        row = [
            s["llm"],
            str(s["evaluated"]),
            str(s["invalid"]),
            str(s["missing"]),
            fmt(m.get("bleu_corpus"), 10),
            fmt(m.get("bleu_sentence_mean"), 10),
            fmt(m.get("rougeL_f1"), 10),
            fmt(m.get("meteor"), 10),
        ]
        if not skip_bertscore:
            row.append(fmt(m.get("bertscore_f1"), 10))
        row.extend(
            [
                fmt(m.get("schema_coverage_mean"), 10),
                fmt(m.get("schema_table_coverage_mean"), 10),
                fmt(m.get("schema_column_coverage_mean"), 10),
                fmt(m.get("gold_schema_coverage_mean"), 10),
            ]
        )
        lines.append(" | ".join(str(c).ljust(w) for c, w in zip(row, widths)))

    lines.append("")
    lines.append("TABLE 2 — DETAILED PER-LLM METRICS")
    lines.append("-" * 100)
    for s in summaries:
        m = s.get("metrics") or {}
        lines.append(f"LLM: {s['llm']}")
        lines.append(f"  Directory      : {s['pred_dir']}")
        lines.append(f"  Evaluated        : {s['evaluated']} / {s['total_records']}")
        lines.append(f"  Invalid / Missing: {s['invalid']} / {s['missing']}")
        if m:
            lines.append(f"  Gold chars (mean): {m.get('gold_chars_mean', 0):.1f}")
            lines.append(f"  Hyp  chars (mean): {m.get('hyp_chars_mean', 0):.1f}")
            lines.append(f"  BLEU-4 (corpus)  : {m.get('bleu_corpus', 0):.4f}")
            lines.append(f"  BLEU (sentence)  : {m.get('bleu_sentence_mean', 0):.4f}")
            if m.get("bleu_corpus_precisions"):
                p = m["bleu_corpus_precisions"]
                lines.append(
                    "  BLEU precisions  : "
                    + ", ".join(f"p{i+1}={x:.2f}" for i, x in enumerate(p))
                )
            lines.append(f"  ROUGE-L F1       : {m.get('rougeL_f1', 0):.4f}")
            lines.append(f"  METEOR           : {m.get('meteor', 0):.4f}")
            if not skip_bertscore:
                lines.append(f"  BERTScore P/R/F1 : {m.get('bertscore_precision', 0):.4f} / "
                             f"{m.get('bertscore_recall', 0):.4f} / {m.get('bertscore_f1', 0):.4f}")
            lines.append(f"  Schema coverage  : {m.get('schema_coverage_mean', 0):.4f}")
            lines.append(f"  Table coverage   : {m.get('schema_table_coverage_mean', 0):.4f}")
            lines.append(f"  Column coverage  : {m.get('schema_column_coverage_mean', 0):.4f}")
            lines.append(f"  Gold sch. cov.   : {m.get('gold_schema_coverage_mean', 0):.4f}")
        if s.get("per_record_path"):
            lines.append(f"  Per-record file  : {s['per_record_path']}")
        lines.append("")

    rank_key = "bertscore_f1" if not skip_bertscore else "bleu_corpus"
    ranked = sorted(
        [s for s in summaries if s.get("metrics")],
        key=lambda x: x["metrics"].get(rank_key, 0),
        reverse=True,
    )
    if ranked:
        lines.append("TABLE 3 — RANKING")
        lines.append("-" * 100)
        lines.append(
            f"Ranked by {'BERTScore F1' if not skip_bertscore else 'corpus BLEU-4'} "
            f"(primary), then schema coverage."
        )
        lines.append(
            f"{'Rank':<6}{'LLM':<16}{'BLEU-4':>10}{'ROUGE-L':>10}{'METEOR':>10}"
            + (f"{'BS-F1':>10}" if not skip_bertscore else "")
            + f"{'SchemaCov':>12}"
        )
        lines.append("-" * 100)
        for i, s in enumerate(ranked, 1):
            m = s["metrics"]
            row = (
                f"{i:<6}{s['llm']:<16}"
                f"{m.get('bleu_corpus', 0):>10.4f}"
                f"{m.get('rougeL_f1', 0):>10.4f}"
                f"{m.get('meteor', 0):>10.4f}"
            )
            if not skip_bertscore:
                row += f"{m.get('bertscore_f1', 0):>10.4f}"
            row += f"{m.get('schema_coverage_mean', 0):>12.4f}"
            lines.append(row)
        lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate RSchema Exp4 schema2text NL vs gold references."
    )
    parser.add_argument("--base-dir", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--gold", type=Path, default=DEFAULT_GOLD)
    parser.add_argument("--ddl-jsonl", type=Path, default=DEFAULT_DDL)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument(
        "--llms",
        nargs="+",
        default=list(LLMS),
        help=f"LLM folders to evaluate (default: {list(LLMS)})",
    )
    parser.add_argument(
        "--skip-bertscore",
        action="store_true",
        help="Skip BERTScore (faster; no model download).",
    )
    parser.add_argument(
        "--bertscore-device",
        default="cuda:0",
        choices=("cpu", "cuda", "cuda:0", "cuda:1", "cuda:2", "cuda:3"),
        help="Device for BERTScore (default: cuda:0).",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=8,
        help="Parallel workers for per-record BLEU/ROUGE/METEOR scoring.",
    )
    args = parser.parse_args()

    if not args.gold.is_file():
        print(f"Gold file not found: {args.gold}", file=sys.stderr)
        sys.exit(1)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    txt_out = args.output_dir / "schema2text_evaluation.txt"
    json_out = args.output_dir / "schema2text_evaluation.json"

    gold_records = load_gold_references(args.gold)
    ddl_by_id = _load_ddl_by_id(args.ddl_jsonl)
    print(f"Loaded {len(gold_records)} gold references from {args.gold}", flush=True)

    summaries: list[dict] = []
    for llm in args.llms:
        pred_dir = args.base_dir / f"schema2text_{llm}"
        if not pred_dir.is_dir():
            print(f"SKIP {llm}: directory not found ({pred_dir})", flush=True)
            continue
        print(f"Evaluating {llm}...", flush=True)
        summary = evaluate_llm(
            llm,
            args.base_dir,
            gold_records,
            ddl_by_id,
            args.output_dir,
            skip_bertscore=args.skip_bertscore,
            bertscore_device=args.bertscore_device,
            workers=args.workers,
        )
        summaries.append(summary)
        m = summary.get("metrics") or {}
        print(
            f"  {summary['evaluated']} evaluated, {summary['invalid']} invalid, "
            f"{summary['missing']} missing"
            + (f" | BLEU={m.get('bleu_corpus', 0):.2f}" if m else "")
            + (f" | ROUGE-L={m.get('rougeL_f1', 0):.4f}" if m else "")
            + (f" | SchemaCov={m.get('schema_coverage_mean', 0):.4f}" if m else ""),
            flush=True,
        )

    if not summaries:
        print("No LLM results found to evaluate.", file=sys.stderr)
        sys.exit(1)

    write_report(
        summaries,
        txt_out,
        skip_bertscore=args.skip_bertscore,
        gold_path=args.gold,
        base_dir=args.base_dir,
    )
    print(f"\nReport: {txt_out}")

    json_payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "gold_path": str(args.gold),
        "ddl_path": str(args.ddl_jsonl),
        "base_dir": str(args.base_dir),
        "skip_bertscore": args.skip_bertscore,
        "bertscore_device": args.bertscore_device,
        "summaries": summaries,
    }
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(json_payload, f, indent=2)
    print(f"JSON:   {json_out}")


if __name__ == "__main__":
    main()
