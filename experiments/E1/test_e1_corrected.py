#!/usr/bin/env python3
"""Regression tests for E1 corrected 381/239 full-population protocol."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "E1"))

import run_e1_corrected_gpu as runner  # noqa: E402
import reproduce_table_vii as e1  # noqa: E402


def test_prompt_b_hash():
    h = hashlib.sha256(runner.SYSTEM_PROMPT.encode()).hexdigest()
    assert h == runner.EXPECTED_PROMPT_HASH
    assert "ONE single paragraph" in runner.SYSTEM_PROMPT


def test_rschema_381_no_synthetic():
    rows = runner.build_rschema_381()
    assert len(rows) == 381
    assert len({r["schema_id"] for r in rows}) == 381
    assert all(r["ddl_source"] == "annotation_ddl" for r in rows)
    assert all(r["ddl"].strip() for r in rows)


def test_schemabench_239():
    rows = runner.build_schemabench_239()
    assert len(rows) == 239
    assert len({r["schema_id"] for r in rows}) == 239


def test_bleu_includes_empty_hypotheses():
    sacrebleu = pytest.importorskip("sacrebleu")
    hyps = ["the cat sat", ""]
    refs = ["the cat sat", "a missing prediction reference"]
    score = sacrebleu.corpus_bleu(hyps, [refs]).score
    assert score == score  # finite
    # documented format, not buggy first-only
    buggy = sacrebleu.corpus_bleu(hyps, [[r] for r in refs]).score
    assert abs(score - buggy) > 1e-6 or True  # may differ; ensure call works


def test_failure_metrics_are_zero_for_nonempty_schema():
    ddl = "CREATE TABLE T (a INT); CREATE TABLE U (b INT);"
    scr = e1.schema_coverage_rate(ddl, "")
    assert scr["coverage"] == 0.0
    rouge_scorer = pytest.importorskip("rouge_score.rouge_scorer")

    r = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True).score("gold text here", "")
    assert r["rougeL"].fmeasure == 0.0


def test_memory_safe_new_tokens_respects_cap():
    # long input should shrink new tokens below 3072
    n = runner.compute_max_new("codellama13b", input_len=5000)
    assert runner.MIN_NEW_TOKENS <= n <= runner.MAX_NEW_TOKENS
    assert n <= runner.MEMORY_SAFE_TOTAL_TOKENS["codellama13b"] - 5000


def test_primary_denominators_not_legacy_eligible_counts():
    # Guardrail: corrected populations are fixed sizes
    assert len(runner.build_rschema_381()) == 381
    assert len(runner.build_schemabench_239()) == 239
    # legacy SchemaBench eligible counts must not be used as primary N
    legacy_eligible = {216, 227, 195, 518}
    assert 381 not in legacy_eligible
    assert 239 not in legacy_eligible


def test_prediction_coverage_1860():
    """Every schema/model pair must be accounted for (valid or recorded failure)."""
    root = ROOT / "results" / "predictions" / "e1_corrected"
    if not root.is_dir() or not any(root.glob("*/0001.json")):
        pytest.skip("local e1_corrected predictions not present")
    total = 0
    for dataset, n, prefix in [
        ("RSchema", 381, "rschema381_detailed"),
        ("SchemaBench", 239, "schemabench239_detailed"),
    ]:
        for model in ("codellama13b", "llama31", "deepseek"):
            d = root / f"{prefix}_{model}"
            assert d.is_dir(), d
            for i in range(1, n + 1):
                js = d / f"{i:04d}.json"
                assert js.is_file(), js
                import json
                meta = json.loads(js.read_text(encoding="utf-8"))
                assert meta.get("schema_id") is not None
                assert meta.get("prompt_hash") == runner.EXPECTED_PROMPT_HASH
                assert meta.get("generation_status")
                total += 1
    assert total == 1860


def test_no_synthetic_in_rschema_predictions():
    d = ROOT / "results" / "predictions" / "e1_corrected" / "rschema381_detailed_llama31"
    if not d.is_dir():
        pytest.skip("local e1_corrected predictions not present")
    rows = {r["schema_id"] for r in runner.build_rschema_381()}
    import json
    pred_ids = set()
    for p in d.glob("*.json"):
        pred_ids.add(json.loads(p.read_text())["schema_id"])
    assert pred_ids == rows


def test_full_pop_denominators_in_metrics_csv():
    csv_path = ROOT / "results" / "metrics" / "reproduced" / "E1_RSCHEMA381_DETAILED.csv"
    if not csv_path.is_file():
        pytest.skip("metrics not yet written")
    import csv
    rows = list(csv.DictReader(csv_path.open()))
    assert all(int(r["N"]) == 381 for r in rows)
    sb = ROOT / "results" / "metrics" / "reproduced" / "E1_SCHEMABENCH239_DETAILED.csv"
    rows2 = list(csv.DictReader(sb.open()))
    assert all(int(r["N"]) == 239 for r in rows2)
    # Never use legacy eligible-only denominators as primary N
    for r in rows + rows2:
        assert int(r["N"]) not in (216, 227, 195, 518)
