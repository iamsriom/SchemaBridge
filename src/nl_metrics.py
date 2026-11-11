"""Schema-to-text (E1) text metrics: BLEU-4, ROUGE-L, BERTScore and Schema Coverage Rate (SCR).

Ported from the verified E1 recovery evaluator.  This module contains no reference scores.

Notes
-----
* Enterprise-145 has no gold natural language: BLEU / ROUGE-L / BERTScore are not applicable
  there; only SCR (which needs the gold DDL) is defined.
* BLEU must use the CORRECT sacrebleu layout ``corpus_bleu(hyps, [refs])`` (one reference
  stream).  The historical bug ``corpus_bleu(hyps, [[r] for r in refs])`` treats every
  reference as a separate stream and gives wrong scores.
* Heavy dependencies (sacrebleu, rouge-score, bert-score, torch) are imported lazily.
"""

from __future__ import annotations

import re
from typing import Sequence

NL_BUG_MARKERS = ("\u0120", "\u010a", "\u2581", "<|endoftext|>", "[INST]", "[/INST]")

BERTSCORE_MODEL = "roberta-large"
BERTSCORE_LANG = "en"

NOT_APPLICABLE_FOR_ENTERPRISE = ("bleu4", "rougeL", "bertscore")


def sanitize_nl_text(text: str) -> str:
    """Repair BPE/SentencePiece artefacts and collapse whitespace; drop blank lines."""
    if not text:
        return text
    text = text.replace("\u0120", " ").replace("\u010a", "\n").replace("\u2581", " ")
    lines = [" ".join(line.split()) for line in text.splitlines()]
    return "\n".join(ln for ln in lines if ln).strip()


def validate_nl_text(text: str, *, min_chars: int = 80) -> tuple[bool, str]:
    """Return (ok, reason).  ``reason`` is empty when ok."""
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
    """Case-fold and strip whitespace, underscores, hyphens and quote characters."""
    return re.sub(r'[\s_\-`"]+', "", (name or "").strip().lower())


_SKIP_PREFIXES = ("PRIMARY", "CONSTRAINT", "FOREIGN", "UNIQUE", "KEY", "INDEX", "CHECK")


def extract_ddl_elements(ddl: str) -> dict[str, set[str]]:
    """Normalised table and column identifiers of a DDL string."""
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
            if line.upper().startswith(_SKIP_PREFIXES):
                continue
            cm = re.match(r"[`']?(\w+)[`']?", line)
            if cm:
                columns.add(norm_ident(cm.group(1)))
    return {"tables": tables, "columns": columns, "all": tables | columns}


def schema_coverage_rate(ddl: str, hyp: str) -> dict[str, float | int | bool]:
    """Fraction of DDL table/column names whose normalised form occurs in the hypothesis."""
    elems = extract_ddl_elements(ddl)["all"]
    if not elems:
        return {"matched": 0, "total": 0, "coverage": 1.0, "empty_denominator": True}
    hyp_norm = norm_ident(hyp)
    matched = sum(1 for e in elems if norm_ident(e) in hyp_norm)
    total = len(elems)
    return {"matched": matched, "total": total, "coverage": matched / total, "empty_denominator": False}


def _check_parallel(hyps: Sequence[str], refs: Sequence[str]) -> None:
    if len(hyps) != len(refs):
        raise ValueError(f"hyps/refs length mismatch: {len(hyps)} vs {len(refs)}")


def compute_bleu(hyps: Sequence[str], refs: Sequence[str]) -> float:
    """Corpus BLEU-4 (sacrebleu defaults) with the CORRECT single-reference-stream layout."""
    _check_parallel(hyps, refs)
    import sacrebleu

    return float(sacrebleu.corpus_bleu(list(hyps), [list(refs)]).score)


def compute_rougeL(hyps: Sequence[str], refs: Sequence[str]) -> float:
    """Mean ROUGE-L F1 (rouge-score, Porter stemming)."""
    _check_parallel(hyps, refs)
    from rouge_score import rouge_scorer

    scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    scores = [scorer.score(r, h)["rougeL"].fmeasure for h, r in zip(hyps, refs)]
    return float(sum(scores) / len(scores)) if scores else float("nan")


def compute_bertscore(
    hyps: Sequence[str],
    refs: Sequence[str],
    device: str = "cpu",
    batch_size: int = 32,
) -> float:
    """Mean BERTScore F1: roberta-large, no IDF weighting, no baseline rescaling."""
    _check_parallel(hyps, refs)
    import bert_score

    _, _, f1 = bert_score.score(
        list(hyps),
        list(refs),
        lang=BERTSCORE_LANG,
        model_type=BERTSCORE_MODEL,
        device=device,
        verbose=False,
        idf=False,
        rescale_with_baseline=False,
        batch_size=batch_size,
    )
    return float(f1.mean())


def compute_scr_macro(hyps: Sequence[str], ddls: Sequence[str]) -> float:
    """Macro-average SCR over schemas (each schema weighted equally)."""
    _check_parallel(hyps, ddls)
    vals = [float(schema_coverage_rate(d, h)["coverage"]) for h, d in zip(hyps, ddls)]
    return float(sum(vals) / len(vals)) if vals else float("nan")


__all__ = [
    "BERTSCORE_MODEL",
    "NL_BUG_MARKERS",
    "NOT_APPLICABLE_FOR_ENTERPRISE",
    "compute_bertscore",
    "compute_bleu",
    "compute_rougeL",
    "compute_scr_macro",
    "extract_ddl_elements",
    "norm_ident",
    "sanitize_nl_text",
    "schema_coverage_rate",
    "validate_nl_text",
]
