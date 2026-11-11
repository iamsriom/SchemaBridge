#!/usr/bin/env python3
"""Independent E1 (tab:e1_s2t) reproduction from archived predictions.

Read-only on prediction trees. Writes audit artifacts under audit/e1_repro/.

Protocols:
  * RSchema_full_518  — all annotation.jsonl rows (locked paper_reference_values)
  * RSchema_ddl_381   — ID intersection with annotation_ddl.jsonl (user task expectation)
  * SchemaBench_239   — annotation_ddl.jsonl
  * Enterprise_145    — SCR only (no human gold NL)

Basic  = Exp1 / Schema2Text1  (short summary prompt = schema2text1)
Detailed = Experiment2 / Schema2Text2 / Exp2 (exhaustive paragraph = schema2text2)
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import sacrebleu
from rouge_score import rouge_scorer

ROOT = Path(__file__).resolve().parents[1]
if not (ROOT / "experiments" / "E1").is_dir():
    ROOT = Path("/data/SchemaBridge")
OUT = ROOT / "experiments" / "E1" / "outputs" / "verified"
OUT.mkdir(parents=True, exist_ok=True)
# Keep a copy under audit/e1_repro for local forensics (gitignored CSVs OK).
AUDIT_OUT = ROOT / "audit" / "e1_repro"
AUDIT_OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Paper values: (A) user-supplied audit table, (B) on-disk locked reference
# ---------------------------------------------------------------------------
USER_PAPER = {
    ("Enterprise-145", "CodeLlama-13B", "B", "SCR"): 0.514,
    ("Enterprise-145", "CodeLlama-13B", "D", "SCR"): 0.605,
    ("Enterprise-145", "Llama-3.1-8B", "B", "SCR"): 0.447,
    ("Enterprise-145", "Llama-3.1-8B", "D", "SCR"): 0.636,
    ("Enterprise-145", "DeepSeek-Coder", "B", "SCR"): 0.638,
    ("Enterprise-145", "DeepSeek-Coder", "D", "SCR"): 0.661,
    ("Enterprise-145", "Claude Sonnet 4.6", "B", "SCR"): 0.472,
    ("Enterprise-145", "Claude Sonnet 4.6", "D", "SCR"): 0.882,
    ("Enterprise-145", "GPT-5.4-mini", "B", "SCR"): 0.411,
    ("Enterprise-145", "GPT-5.4-mini", "D", "SCR"): 0.917,
    ("RSchema", "CodeLlama-13B", "B", "BLEU"): 7.63,
    ("RSchema", "CodeLlama-13B", "D", "BLEU"): 4.55,
    ("RSchema", "CodeLlama-13B", "B", "ROUGE"): 0.260,
    ("RSchema", "CodeLlama-13B", "D", "ROUGE"): 0.225,
    ("RSchema", "CodeLlama-13B", "B", "BERT"): 0.864,
    ("RSchema", "CodeLlama-13B", "D", "BERT"): 0.840,
    ("RSchema", "CodeLlama-13B", "B", "SCR"): 0.748,
    ("RSchema", "CodeLlama-13B", "D", "SCR"): 0.932,
    ("RSchema", "Llama-3.1-8B", "B", "BLEU"): 6.37,
    ("RSchema", "Llama-3.1-8B", "D", "BLEU"): 6.76,
    ("RSchema", "Llama-3.1-8B", "B", "ROUGE"): 0.263,
    ("RSchema", "Llama-3.1-8B", "D", "ROUGE"): 0.252,
    ("RSchema", "Llama-3.1-8B", "B", "BERT"): 0.862,
    ("RSchema", "Llama-3.1-8B", "D", "BERT"): 0.863,
    ("RSchema", "Llama-3.1-8B", "B", "SCR"): 0.519,
    ("RSchema", "Llama-3.1-8B", "D", "SCR"): 0.754,
    ("RSchema", "DeepSeek-Coder", "B", "BLEU"): 2.90,
    ("RSchema", "DeepSeek-Coder", "D", "BLEU"): 2.56,
    ("RSchema", "DeepSeek-Coder", "B", "ROUGE"): 0.226,
    ("RSchema", "DeepSeek-Coder", "D", "ROUGE"): 0.214,
    ("RSchema", "DeepSeek-Coder", "B", "BERT"): 0.832,
    ("RSchema", "DeepSeek-Coder", "D", "BERT"): 0.829,
    ("RSchema", "DeepSeek-Coder", "B", "SCR"): 0.963,
    ("RSchema", "DeepSeek-Coder", "D", "SCR"): 0.973,
    ("RSchema", "Claude Sonnet 4.6", "B", "BLEU"): 4.60,
    ("RSchema", "Claude Sonnet 4.6", "D", "BLEU"): 1.19,
    ("RSchema", "Claude Sonnet 4.6", "B", "ROUGE"): 0.241,
    ("RSchema", "Claude Sonnet 4.6", "D", "ROUGE"): 0.189,
    ("RSchema", "Claude Sonnet 4.6", "B", "BERT"): 0.859,
    ("RSchema", "Claude Sonnet 4.6", "D", "BERT"): 0.817,
    ("RSchema", "Claude Sonnet 4.6", "B", "SCR"): 0.421,
    ("RSchema", "Claude Sonnet 4.6", "D", "SCR"): 0.999,
    ("RSchema", "GPT-5.4-mini", "B", "BLEU"): 3.18,
    ("RSchema", "GPT-5.4-mini", "D", "BLEU"): 1.52,
    ("RSchema", "GPT-5.4-mini", "B", "ROUGE"): 0.244,
    ("RSchema", "GPT-5.4-mini", "D", "ROUGE"): 0.185,
    ("RSchema", "GPT-5.4-mini", "B", "BERT"): 0.860,
    ("RSchema", "GPT-5.4-mini", "D", "BERT"): 0.816,
    ("RSchema", "GPT-5.4-mini", "B", "SCR"): 0.365,
    ("RSchema", "GPT-5.4-mini", "D", "SCR"): 1.000,
    ("SchemaBench", "CodeLlama-13B", "B", "BLEU"): 3.79,
    ("SchemaBench", "CodeLlama-13B", "D", "BLEU"): 2.30,
    ("SchemaBench", "CodeLlama-13B", "B", "ROUGE"): 0.168,
    ("SchemaBench", "CodeLlama-13B", "D", "ROUGE"): 0.147,
    ("SchemaBench", "CodeLlama-13B", "B", "BERT"): 0.819,
    ("SchemaBench", "CodeLlama-13B", "D", "BERT"): 0.803,
    ("SchemaBench", "CodeLlama-13B", "B", "SCR"): 0.556,
    ("SchemaBench", "CodeLlama-13B", "D", "SCR"): 0.758,
    ("SchemaBench", "Llama-3.1-8B", "B", "BLEU"): 4.19,
    ("SchemaBench", "Llama-3.1-8B", "D", "BLEU"): 3.67,
    ("SchemaBench", "Llama-3.1-8B", "B", "ROUGE"): 0.174,
    ("SchemaBench", "Llama-3.1-8B", "D", "ROUGE"): 0.173,
    ("SchemaBench", "Llama-3.1-8B", "B", "BERT"): 0.831,
    ("SchemaBench", "Llama-3.1-8B", "D", "BERT"): 0.815,
    ("SchemaBench", "Llama-3.1-8B", "B", "SCR"): 0.405,
    ("SchemaBench", "Llama-3.1-8B", "D", "SCR"): 0.605,
    ("SchemaBench", "DeepSeek-Coder", "B", "BLEU"): 3.02,
    ("SchemaBench", "DeepSeek-Coder", "D", "BLEU"): 1.66,
    ("SchemaBench", "DeepSeek-Coder", "B", "ROUGE"): 0.146,
    ("SchemaBench", "DeepSeek-Coder", "D", "ROUGE"): 0.144,
    ("SchemaBench", "DeepSeek-Coder", "B", "BERT"): 0.798,
    ("SchemaBench", "DeepSeek-Coder", "D", "BERT"): 0.793,
    ("SchemaBench", "DeepSeek-Coder", "B", "SCR"): 0.702,
    ("SchemaBench", "DeepSeek-Coder", "D", "SCR"): 0.825,
    ("SchemaBench", "Claude Sonnet 4.6", "B", "BLEU"): 2.09,
    ("SchemaBench", "Claude Sonnet 4.6", "D", "BLEU"): 1.07,
    ("SchemaBench", "Claude Sonnet 4.6", "B", "ROUGE"): 0.167,
    ("SchemaBench", "Claude Sonnet 4.6", "D", "ROUGE"): 0.128,
    ("SchemaBench", "Claude Sonnet 4.6", "B", "BERT"): 0.817,
    ("SchemaBench", "Claude Sonnet 4.6", "D", "BERT"): 0.785,
    ("SchemaBench", "Claude Sonnet 4.6", "B", "SCR"): 0.386,
    ("SchemaBench", "Claude Sonnet 4.6", "D", "SCR"): 0.944,
    ("SchemaBench", "GPT-5.4-mini", "B", "BLEU"): 1.02,
    ("SchemaBench", "GPT-5.4-mini", "D", "BLEU"): 1.02,
    ("SchemaBench", "GPT-5.4-mini", "B", "ROUGE"): 0.157,
    ("SchemaBench", "GPT-5.4-mini", "D", "ROUGE"): 0.124,
    ("SchemaBench", "GPT-5.4-mini", "B", "BERT"): 0.816,
    ("SchemaBench", "GPT-5.4-mini", "D", "BERT"): 0.781,
    ("SchemaBench", "GPT-5.4-mini", "B", "SCR"): 0.316,
    ("SchemaBench", "GPT-5.4-mini", "D", "SCR"): 0.974,
}

LOCKED_PAPER = json.loads((ROOT / "configs/paper_reference_values.json").read_text())[
    "tab:e1_s2t"
]["datasets"]

MODEL_KEYS = {
    "CodeLlama-13B": "codellama13b",
    "Llama-3.1-8B": "llama31",
    "DeepSeek-Coder": "deepseek",
    "Claude Sonnet 4.6": "claude_sonnet_4_6",
    "GPT-5.4-mini": "gpt_5_4_mini",
}
LLM_DIR = {
    "CodeLlama-13B": "codellama13b",
    "Llama-3.1-8B": "llama31",
    "DeepSeek-Coder": "deepseek",
    "Claude Sonnet 4.6": "sonnet46",
    "GPT-5.4-mini": "gpt54mini",
}

PRED = {
    ("RSchema", "B"): Path("/data/RSchema_ExpResults4/Exp1"),
    ("RSchema", "D"): Path("/data/RSchema_ExpResults4/Experiment2"),
    ("SchemaBench", "B"): Path("/data/SchemaBench/Exp1"),
    ("SchemaBench", "D"): Path("/data/SchemaBench/Experiment"),
    ("Enterprise-145", "B"): Path("/data/LLMTranslations/Exp1"),
    ("Enterprise-145", "D"): Path("/data/LLMTranslations/Exp2"),
}
ENT_PREFIX = {"B": "Schema2Text1", "D": "Schema2Text2"}

NL_BUG_MARKERS = ("\u0120", "Ġ", "Ċ", "▁", "<|endoftext|>", "[INST]", "[/INST]")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sanitize_nl_text(text: str) -> str:
    if not text:
        return text
    text = text.replace("\u0120", " ").replace("Ċ", "\n").replace("▁", " ")
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


def norm_ident(name: str) -> str:
    return re.sub(r'[\s_\-`"]+', "", (name or "").strip().lower())


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


def schema_coverage(elements: set[str], text: str) -> float:
    if not elements:
        return 1.0
    compact = norm_ident(text)
    matched = sum(1 for e in elements if e in compact)
    return matched / len(elements)


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _sql_ident(name: object) -> str:
    if isinstance(name, dict):
        if not name:
            return "col"
        _key, val = next(iter(name.items()))
        return _sql_ident(val)
    return re.sub(r"\s+", "_", str(name or "").strip()).lower()


def structured_answer_to_ddl(answer: dict, database: str) -> str:
    """Mirror of third_party/evaluate_exp4_schema2text_nl.structured_answer_to_ddl."""
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


def load_rschema_gold(subset: str) -> list[dict]:
    gold_path = Path("/data/RSchema/annotation.jsonl")
    ddl_path = Path("/data/RSchema/annotation_ddl.jsonl")
    ddl_by_id = {
        r["id"]: (r.get("answer") or "").strip()
        for r in load_jsonl(ddl_path)
        if r.get("id") and isinstance(r.get("answer"), str)
    }
    ddl_ids = set(ddl_by_id)
    records = []
    with gold_path.open(encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            rec = json.loads(line)
            rid = rec.get("id", "")
            if subset == "ddl_381" and rid not in ddl_ids:
                continue
            ddl = ddl_by_id.get(rid, "")
            if not ddl and isinstance(rec.get("answer"), dict):
                # synthetic fallback used by original evaluator for non-DDL rows
                ddl = structured_answer_to_ddl(
                    rec["answer"], database=f"rschema_{i:04d}"
                )
            records.append(
                {
                    "serial": f"{i:04d}",
                    "id": rid,
                    "gold_nl": (rec.get("question") or "").strip(),
                    "ddl": ddl,
                }
            )
    return records


def load_schemabench_gold() -> list[dict]:
    path = Path("/data/SchemaBench/Dataset/annotation_ddl.jsonl")
    records = []
    with path.open(encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            rec = json.loads(line)
            records.append(
                {
                    "serial": f"{i:04d}",
                    "id": rec.get("id", ""),
                    "gold_nl": (rec.get("question") or "").strip(),
                    "ddl": (rec.get("answer") or "").strip(),
                }
            )
    return records


def load_enterprise_schemas() -> list[dict]:
    schema_dir = Path("/data/Text2ER/schema")
    records = []
    for sql in sorted(schema_dir.glob("*.sql")):
        records.append(
            {
                "safe_name": sql.stem,
                "id": sql.stem,
                "ddl": sql.read_text(encoding="utf-8", errors="replace"),
            }
        )
    return records


@dataclass
class EvalResult:
    dataset: str
    model: str
    prompt: str
    protocol: str
    expected: int
    available: int
    evaluated: int
    missing: int
    invalid: int
    bleu_corpus: float | None = None
    bleu_sentence_mean: float | None = None
    rougeL_f1: float | None = None
    bertscore_f1: float | None = None
    scr: float | None = None
    pred_dir: str = ""


def evaluate_nl_group(
    dataset: str,
    model: str,
    prompt: str,
    protocol: str,
    gold: list[dict],
    pred_dir: Path,
    *,
    compute_bert: bool,
    bert_device: str,
    enterprise: bool = False,
) -> EvalResult:
    rouge = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    refs: list[str] = []
    hyps: list[str] = []
    scrs: list[float] = []
    missing = 0
    invalid = 0
    available = 0

    if enterprise:
        prefix = ENT_PREFIX[prompt]
        llm = LLM_DIR[model]
        # prefer codellama13b naming; some dirs use codellama
        candidates = [
            pred_dir / f"{prefix}_{llm}",
            pred_dir / f"{prefix}_codellama" if llm == "codellama13b" else None,
        ]
        base = next((c for c in candidates if c and c.is_dir()), None)
        if base is None:
            return EvalResult(
                dataset,
                model,
                prompt,
                protocol,
                len(gold),
                0,
                0,
                len(gold),
                0,
                pred_dir=str(pred_dir),
            )
        for rec in gold:
            # enterprise files named by schema stem
            txt = None
            for cand in (
                base / f"{rec['safe_name']}.txt",
                base / f"{rec['safe_name']}.sql.txt",
            ):
                if cand.is_file():
                    txt = cand
                    break
            if txt is None:
                # try case-insensitive
                found = list(base.glob(f"{rec['safe_name']}*.txt"))
                if not found:
                    missing += 1
                    continue
                txt = found[0]
            available += 1
            hyp = sanitize_nl_text(txt.read_text(encoding="utf-8", errors="replace"))
            ok, _ = validate_nl_text(hyp, min_chars=20)
            if not ok:
                # Enterprise short empties still score SCR=0 coverage of elements
                if not hyp.strip():
                    invalid += 1
                    continue
            elems = extract_ddl_elements(rec["ddl"])["all"]
            scrs.append(schema_coverage(elems, hyp))
        scr = sum(scrs) / len(scrs) if scrs else None
        return EvalResult(
            dataset,
            model,
            prompt,
            protocol,
            len(gold),
            available,
            len(scrs),
            missing,
            invalid,
            scr=scr,
            pred_dir=str(base),
        )

    llm = LLM_DIR[model]
    base = pred_dir / f"schema2text_{llm}"
    for rec in gold:
        txt_path = base / f"{rec['serial']}.txt"
        json_path = base / f"{rec['serial']}.json"
        if not txt_path.is_file():
            missing += 1
            continue
        available += 1
        hyp_raw = txt_path.read_text(encoding="utf-8", errors="replace")
        hyp = sanitize_nl_text(hyp_raw)
        ok, _ = validate_nl_text(hyp)
        gold_nl = rec["gold_nl"]
        ddl = rec["ddl"]
        if json_path.is_file():
            try:
                meta = json.loads(json_path.read_text(encoding="utf-8"))
                if meta.get("ddl"):
                    ddl = meta["ddl"]
            except Exception:
                pass
        if not ok or not gold_nl:
            invalid += 1
            continue
        refs.append(gold_nl)
        hyps.append(hyp)
        scrs.append(schema_coverage(extract_ddl_elements(ddl)["all"], hyp))

    metrics: dict = {}
    if refs:
        # Correct SacreBLEU single-reference layout (NOT [[r] for r in refs],
        # which inflates scores / effectively scores the first hypothesis only).
        bleu = sacrebleu.corpus_bleu(hyps, [refs])
        sent = [
            sacrebleu.sentence_bleu(h, [r]).score for h, r in zip(hyps, refs)
        ]
        rouge_scores = [rouge.score(r, h)["rougeL"].fmeasure for r, h in zip(refs, hyps)]
        metrics = {
            "bleu_corpus": bleu.score,
            "bleu_sentence_mean": sum(sent) / len(sent),
            "rougeL_f1": sum(rouge_scores) / len(rouge_scores),
            "scr": sum(scrs) / len(scrs),
        }
        if compute_bert:
            import bert_score

            _P, _R, F1 = bert_score.score(
                hyps,
                refs,
                lang="en",
                verbose=False,
                batch_size=16,
                device=bert_device,
            )
            metrics["bertscore_f1"] = float(F1.mean())

    return EvalResult(
        dataset,
        model,
        prompt,
        protocol,
        len(gold),
        available,
        len(refs),
        missing,
        invalid,
        bleu_corpus=metrics.get("bleu_corpus"),
        bleu_sentence_mean=metrics.get("bleu_sentence_mean"),
        rougeL_f1=metrics.get("rougeL_f1"),
        bertscore_f1=metrics.get("bertscore_f1"),
        scr=metrics.get("scr"),
        pred_dir=str(base),
    )


def locked_value(dataset: str, model: str, prompt: str, metric: str):
    key = MODEL_KEYS[model]
    row = LOCKED_PAPER[dataset][key]
    mapping = {
        ("B", "BLEU"): "bleu4_basic",
        ("D", "BLEU"): "bleu4_detailed",
        ("B", "ROUGE"): "rougeL_basic",
        ("D", "ROUGE"): "rougeL_detailed",
        ("B", "BERT"): "bertscore_basic",
        ("D", "BERT"): "bertscore_detailed",
        ("B", "SCR"): "scr_basic",
        ("D", "SCR"): "scr_detailed",
    }
    return row.get(mapping[(prompt, metric)])


def status_vs(paper, recomputed, metric: str) -> str:
    if paper is None or recomputed is None:
        return "UNVERIFIABLE"
    if metric == "BLEU":
        return "MATCH" if abs(paper - recomputed) <= 0.005 + 1e-9 else "MISMATCH"
    return "MATCH" if abs(paper - recomputed) <= 0.0005 + 1e-9 else "MISMATCH"


def main() -> int:
    compute_bert = "--bert" in sys.argv
    bert_device = "cuda:0"
    for a in sys.argv:
        if a.startswith("--bert-device="):
            bert_device = a.split("=", 1)[1]

    rs_full = load_rschema_gold("full_518")
    rs_381 = load_rschema_gold("ddl_381")
    sb = load_schemabench_gold()
    ent = load_enterprise_schemas()

    # Prefer bridge enterprise SQL if Text2ER missing names
    if len(ent) != 145:
        alt = Path("/data/SchemaBridge/datasets/enterprise145/schema")
        if alt.is_dir():
            ent = [
                {
                    "safe_name": p.stem,
                    "id": p.stem,
                    "ddl": p.read_text(encoding="utf-8", errors="replace"),
                }
                for p in sorted(alt.glob("*.sql"))
            ]

    coverage_rows = []
    results: list[EvalResult] = []

    # RSchema both protocols
    for prompt in ("B", "D"):
        for model in LLM_DIR:
            for protocol, gold in (("full_518", rs_full), ("ddl_381", rs_381)):
                er = evaluate_nl_group(
                    "RSchema",
                    model,
                    prompt,
                    protocol,
                    gold,
                    PRED[("RSchema", prompt)],
                    compute_bert=compute_bert,
                    bert_device=bert_device,
                )
                results.append(er)
                coverage_rows.append(
                    {
                        "dataset": "RSchema",
                        "model": model,
                        "prompt": prompt,
                        "protocol": protocol,
                        "expected": er.expected,
                        "available": er.available,
                        "evaluated": er.evaluated,
                        "missing": er.missing,
                        "invalid": er.invalid,
                        "pred_dir": er.pred_dir,
                    }
                )

    for prompt in ("B", "D"):
        for model in LLM_DIR:
            er = evaluate_nl_group(
                "SchemaBench",
                model,
                prompt,
                "full_239",
                sb,
                PRED[("SchemaBench", prompt)],
                compute_bert=compute_bert,
                bert_device=bert_device,
            )
            results.append(er)
            coverage_rows.append(
                {
                    "dataset": "SchemaBench",
                    "model": model,
                    "prompt": prompt,
                    "protocol": "full_239",
                    "expected": er.expected,
                    "available": er.available,
                    "evaluated": er.evaluated,
                    "missing": er.missing,
                    "invalid": er.invalid,
                    "pred_dir": er.pred_dir,
                }
            )

    for prompt in ("B", "D"):
        for model in LLM_DIR:
            er = evaluate_nl_group(
                "Enterprise-145",
                model,
                prompt,
                "scr_only_145",
                ent,
                PRED[("Enterprise-145", prompt)],
                compute_bert=False,
                bert_device=bert_device,
                enterprise=True,
            )
            results.append(er)
            coverage_rows.append(
                {
                    "dataset": "Enterprise-145",
                    "model": model,
                    "prompt": prompt,
                    "protocol": "scr_only_145",
                    "expected": er.expected,
                    "available": er.available,
                    "evaluated": er.evaluated,
                    "missing": er.missing,
                    "invalid": er.invalid,
                    "pred_dir": er.pred_dir,
                }
            )

    # Comparison rows vs user paper (primary) and locked paper
    # Primary recompute protocol for user table: RSchema ddl_381, SchemaBench full, Ent SCR
    compare_rows = []
    for er in results:
        use_for_user = (
            (er.dataset == "RSchema" and er.protocol == "ddl_381")
            or (er.dataset == "SchemaBench" and er.protocol == "full_239")
            or (er.dataset == "Enterprise-145")
        )
        use_for_locked = (
            (er.dataset == "RSchema" and er.protocol == "full_518")
            or (er.dataset == "SchemaBench" and er.protocol == "full_239")
            or (er.dataset == "Enterprise-145")
        )
        metric_map = [
            ("BLEU", er.bleu_corpus, er.bleu_sentence_mean),
            ("ROUGE", er.rougeL_f1, None),
            ("BERT", er.bertscore_f1, None),
            ("SCR", er.scr, None),
        ]
        for metric, corpus_or_main, sent in metric_map:
            if er.dataset == "Enterprise-145" and metric != "SCR":
                continue
            user_p = USER_PAPER.get((er.dataset, er.model, er.prompt, metric))
            locked_p = locked_value(er.dataset, er.model, er.prompt, metric)
            # primary recomputed value for classification vs user:
            # BLEU: paper claims corpus BLEU; also report sentence mean
            recomputed = corpus_or_main
            if use_for_user:
                st_user_corpus = status_vs(user_p, recomputed, metric)
                st_user_sent = (
                    status_vs(user_p, sent, metric)
                    if metric == "BLEU" and sent is not None
                    else None
                )
                compare_rows.append(
                    {
                        "dataset": er.dataset,
                        "model": er.model,
                        "prompt": er.prompt,
                        "metric": metric,
                        "protocol": er.protocol,
                        "N": er.evaluated,
                        "paper_user": user_p,
                        "paper_locked": locked_p if use_for_locked else None,
                        "recomputed_corpus_or_main": recomputed,
                        "recomputed_sentence_bleu": sent if metric == "BLEU" else None,
                        "diff_user_vs_corpus": (
                            None
                            if user_p is None or recomputed is None
                            else recomputed - user_p
                        ),
                        "diff_user_vs_sentbleu": (
                            None
                            if user_p is None or sent is None
                            else sent - user_p
                        ),
                        "status_vs_user_corpus_BLEU_or_main": st_user_corpus,
                        "status_vs_user_sentence_BLEU": st_user_sent,
                        "status_vs_locked": (
                            status_vs(locked_p, recomputed, metric)
                            if use_for_locked
                            else None
                        ),
                    }
                )

    # Also add locked-protocol comparison rows for RSchema full_518
    for er in results:
        if not (er.dataset == "RSchema" and er.protocol == "full_518"):
            continue
        for metric, val, sent in [
            ("BLEU", er.bleu_corpus, er.bleu_sentence_mean),
            ("ROUGE", er.rougeL_f1, None),
            ("BERT", er.bertscore_f1, None),
            ("SCR", er.scr, None),
        ]:
            locked_p = locked_value(er.dataset, er.model, er.prompt, metric)
            user_p = USER_PAPER.get((er.dataset, er.model, er.prompt, metric))
            compare_rows.append(
                {
                    "dataset": er.dataset,
                    "model": er.model,
                    "prompt": er.prompt,
                    "metric": metric,
                    "protocol": er.protocol,
                    "N": er.evaluated,
                    "paper_user": user_p,
                    "paper_locked": locked_p,
                    "recomputed_corpus_or_main": val,
                    "recomputed_sentence_bleu": sent if metric == "BLEU" else None,
                    "diff_user_vs_corpus": (
                        None if user_p is None or val is None else val - user_p
                    ),
                    "diff_user_vs_sentbleu": (
                        None if user_p is None or sent is None else sent - user_p
                    ),
                    "status_vs_user_corpus_BLEU_or_main": status_vs(user_p, val, metric),
                    "status_vs_user_sentence_BLEU": (
                        status_vs(user_p, sent, metric) if sent is not None else None
                    ),
                    "status_vs_locked": status_vs(locked_p, val, metric),
                }
            )

    stamp = datetime.now(timezone.utc).isoformat()
    raw = {
        "generated_utc": stamp,
        "compute_bert": compute_bert,
        "bert_device": bert_device if compute_bert else None,
        "sacrebleu_version": sacrebleu.__version__,
        "results": [er.__dict__ for er in results],
    }
    (OUT / "e1_recompute_raw.json").write_text(json.dumps(raw, indent=2), encoding="utf-8")

    with (OUT / "e1_coverage.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(coverage_rows[0].keys()))
        w.writeheader()
        w.writerows(coverage_rows)

    with (OUT / "e1_comparison.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(compare_rows[0].keys()))
        w.writeheader()
        w.writerows(compare_rows)

    # Convenience: primary user-protocol table
    primary = [
        r
        for r in compare_rows
        if (r["dataset"] == "RSchema" and r["protocol"] == "ddl_381")
        or (r["dataset"] == "SchemaBench" and r["protocol"] == "full_239")
        or (r["dataset"] == "Enterprise-145")
    ]
    with (OUT / "e1_comparison_user_protocol.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        w = csv.DictWriter(f, fieldnames=list(primary[0].keys()))
        w.writeheader()
        w.writerows(primary)

    # Mirror forensic copies under audit/e1_repro (gitignored CSVs/JSON).
    for name in (
        "e1_recompute_raw.json",
        "e1_coverage.csv",
        "e1_comparison.csv",
        "e1_comparison_user_protocol.csv",
    ):
        src = OUT / name
        if src.is_file():
            (AUDIT_OUT / name).write_bytes(src.read_bytes())

    print(f"Wrote {OUT}")
    print(f"coverage rows={len(coverage_rows)} compare={len(compare_rows)} bert={compute_bert}")
    # quick summary counts for user protocol
    for key in (
        "status_vs_user_corpus_BLEU_or_main",
        "status_vs_user_sentence_BLEU",
        "status_vs_locked",
    ):
        counts: dict[str, int] = {}
        for r in primary:
            st = r.get(key)
            if st is None:
                continue
            counts[st] = counts.get(st, 0) + 1
        print(key, counts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
