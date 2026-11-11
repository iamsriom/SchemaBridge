#!/usr/bin/env python3
"""Unit tests for E1 Table VII offline evaluator helpers."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "E1"))

import reproduce_table_vii as e1  # noqa: E402


def test_norm_ident_and_scr_basic():
    ddl = """
    CREATE TABLE Airplane (
      Airplane_Number INTEGER PRIMARY KEY,
      Model VARCHAR(255)
    );
    """
    hyp = "The Airplane table stores airplane_number and model."
    scr = e1.schema_coverage_rate(ddl, hyp)
    assert scr["total"] == 3  # airplane, airplanenumber, model
    assert scr["coverage"] == 1.0


def test_scr_does_not_use_ddl_as_hypothesis():
    ddl = """
    CREATE TABLE SecretTable (
      secret_col INTEGER
    );
    """
    hyp = "A short description without identifiers."
    # Ensure we are not accidentally scoring the DDL string
    scr = e1.schema_coverage_rate(ddl, hyp)
    assert scr["coverage"] == 0.0
    # If someone mistakenly passed ddl as hyp, coverage would be 1.0
    assert e1.schema_coverage_rate(ddl, ddl)["coverage"] == 1.0


def test_empty_schema_denominator_policy():
    scr = e1.schema_coverage_rate("", "anything")
    assert scr["empty_denominator"] is True
    assert scr["coverage"] == 1.0


def test_validate_nl_rejects_errors_and_empties():
    assert e1.validate_nl_text("")[0] is False
    assert e1.validate_nl_text("ERROR: CUDA out of memory")[0] is False
    ok, _ = e1.validate_nl_text(
        "This is a sufficiently long natural language description of a database schema "
        "with tables and columns described in plain English for evaluation purposes."
    )
    assert ok is True


def test_bleu_reference_formats_differ_or_match_documented(tmp_path):
    sacrebleu = pytest.importorskip("sacrebleu")
    hyps = [
        "the cat sat on the mat",
        "there is a database with users and orders",
    ]
    refs = [
        "the cat is on the mat",
        "the database contains users and orders tables",
    ]
    orig = sacrebleu.corpus_bleu(hyps, [[r] for r in refs]).score
    doc = sacrebleu.corpus_bleu(hyps, [refs]).score
    # Both must be finite; document that evaluator computes both.
    assert orig == orig and doc == doc
    out = e1.compute_bleu(hyps, refs)
    assert "bleu_corpus_original_format" in out
    assert "bleu_corpus_documented_format" in out
    assert out["bleu4"] == out["bleu_corpus_documented_format"]


def test_rouge_mean_aggregation():
    pytest.importorskip("rouge_score")
    hyps = ["a b c d", "hello world"]
    refs = ["a b c e", "hello there"]
    out = e1.compute_rougeL(hyps, refs)
    assert 0.0 <= out["rougeL"] <= 1.0


def test_status_tolerances_and_rounding_boundary():
    st, diff, _ = e1.status_for("bleu4", 16.35, 16.345523)
    assert st == e1.PASS
    st, _, _ = e1.status_for("rougeL", 0.232, 0.23182085)
    assert st == e1.PASS
    st, _, _ = e1.status_for("scr", 0.928, 0.900)
    assert st == e1.MISMATCH


def test_prompt_files_exist_and_differ():
    prompts = e1.read_prompt_files()
    assert "describer_basic.txt" in prompts
    assert "describer_detailed.txt" in prompts
    assert prompts["describer_basic.txt"] != prompts["describer_detailed.txt"]
    # After 2026-11-11 fix: basic = short summary; detailed = exhaustive paragraph
    assert "Summarize this database schema" in prompts["describer_basic.txt"]
    assert "ONE single paragraph" in prompts["describer_detailed.txt"]
    assert "Be exhaustive" in prompts["describer_detailed.txt"]


def test_discover_sources_finds_rschema_detailed():
    srcs = e1.discover_prediction_sources()
    rs = [s for s in srcs if s.dataset == "RSchema" and s.prompt == "detailed"]
    if not rs:
        pytest.skip("no local RSchema detailed prediction archives")
    assert rs[0].path.is_dir()


def test_paper_reference_has_ninety_numerical_targets():
    paper = e1.load_paper()
    n = 0
    for ds, models in paper.items():
        for model, vals in models.items():
            if not isinstance(vals, dict):
                continue
            for metric in e1.METRICS:
                for prompt in e1.PROMPTS:
                    key = f"{metric}_{prompt}"
                    if ds == "Enterprise-145" and metric != "scr":
                        continue
                    assert key in vals
                    n += 1
    assert n == 90


def test_validate_only_smoke(tmp_path):
    rc = e1.main(
        [
            "--validate-only",
            "--audit-dir",
            str(tmp_path),
            "--progress-log",
            str(tmp_path / "p.log"),
        ]
    )
    assert rc == 0
    assert (tmp_path / "E1_ARTIFACT_INVENTORY.csv").is_file()
    assert (tmp_path / "E1_METRIC_CONFIG.json").is_file()


def test_bleu_documented_format_is_not_first_hyp_only():
    sacrebleu = pytest.importorskip("sacrebleu")
    hyps = ["aaa bbb ccc ddd eee fff", "the cat sat on the mat today"]
    refs = ["aaa bbb ccc xxx yyy zzz", "the cat sat on a mat today"]
    buggy = sacrebleu.corpus_bleu(hyps, [[r] for r in refs])
    correct = sacrebleu.corpus_bleu(hyps, [refs])
    # Buggy call collapses to first hypothesis multi-ref behaviour
    first_only = sacrebleu.corpus_bleu([hyps[0]], [[r] for r in refs])
    assert abs(buggy.score - first_only.score) < 1e-9
    assert buggy.sys_len == first_only.sys_len
    assert correct.sys_len > buggy.sys_len


def test_enterprise_schema2text1_is_codellama7b_not_13b():
    p = Path("/data/LLMTranslations/Schema2Text1_codellama/Airline.json")
    if not p.is_file():
        pytest.skip("Enterprise Schema2Text1 archive absent")
    meta = json.loads(p.read_text())
    assert meta.get("model_id") == "codellama/CodeLlama-7b-Instruct-hf"


def test_rschema_ddl_provenance_381_137():
    gold = e1.load_rschema_gold()
    assert len(gold) == 518
    from collections import Counter
    c = Counter(g.ddl_source for g in gold)
    assert c.get("annotation_ddl") == 381
    assert c.get("structured_synthetic") == 137


def test_schemabench_authoritative_experiment_is_complete():
    """Authoritative Detailed tree is SchemaBench/Experiment/ (full 239), not Experiment4."""
    gold = e1.load_schemabench_gold()
    assert len(gold) == 239
    auth = Path("/data/SchemaBench/Experiment/schema2text_deepseek")
    if not auth.is_dir():
        pytest.skip("authoritative SchemaBench Experiment archive absent")
    preds, cov = e1.load_numbered_predictions(auth, gold)
    assert cov["valid"] == 239
    assert cov["invalid"] == 0

    stale = Path("/data/SchemaBench/Experiment4/schema2text_deepseek")
    if stale.is_dir():
        _, stale_cov = e1.load_numbered_predictions(stale, gold)
        # Stale Experiment4 lineage behind results/predictions/e1/schemabench_* — do not use.
        assert stale_cov["invalid"] >= 40
        assert stale_cov["valid"] < 239


def test_prompt_b_hash_stable():
    import hashlib
    text = (ROOT / "prompts" / "describer_detailed.txt").read_text().strip()
    assert "ONE single paragraph" in text
    assert "Be exhaustive" in text
    h = hashlib.sha256(text.encode()).hexdigest()
    assert h == "f09fc8cae8d8ec73deb79f8bc7c2e71842d5fd35e92d833a02954b539755622d"


def test_paper_models_do_not_include_7b_or_gpt4omini():
    assert "codellama" not in e1.MODELS  # 7B key must not be a paper model key
    assert "gpt4omini" not in e1.MODELS
    assert "claude_sonnet_4_6" in e1.MODELS
    assert "gpt_5_4_mini" in e1.MODELS
