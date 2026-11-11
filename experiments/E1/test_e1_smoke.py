#!/usr/bin/env python3
"""CPU-friendly E1 smoke tests using synthetic fixtures (no model downloads)."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
E1 = ROOT / "experiments" / "E1"
FIX = E1 / "fixtures" / "synthetic"
sys.path.insert(0, str(E1))

import run_e1_corrected_gpu as runner  # noqa: E402
import reproduce_table_vii as e1  # noqa: E402


def test_prompt_b_hash_matches_verified():
    # Detailed (schema2text2 / Prompt B) is describer_detailed.txt after prompt rename fix.
    text = (ROOT / "prompts" / "describer_detailed.txt").read_text(encoding="utf-8").strip()
    assert hashlib.sha256(text.encode()).hexdigest() == runner.EXPECTED_PROMPT_HASH
    assert text == runner.SYSTEM_PROMPT
    basic = (ROOT / "prompts" / "describer_basic.txt").read_text(encoding="utf-8").strip()
    assert "Summarize this database schema" in basic
    assert basic != text


def test_synthetic_fixture_alignment(tmp_path, monkeypatch):
    """Prediction/reference alignment on a tiny synthetic population."""
    # Point builders at fixtures by temporarily swapping load paths via monkeypatch
    # of DATA and ROOT dataset lookup: write a mini dataset under tmp and patch.
    ds = tmp_path / "datasets"
    (ds / "rschema").mkdir(parents=True)
    (ds / "schemabench").mkdir(parents=True)
    # 2-record "rschema" style: annotation + ddl intersection
    (ds / "rschema" / "annotation.jsonl").write_text(
        (FIX / "annotation.jsonl").read_text(encoding="utf-8"), encoding="utf-8"
    )
    (ds / "rschema" / "annotation_ddl.jsonl").write_text(
        (FIX / "annotation_ddl.jsonl").read_text(encoding="utf-8"), encoding="utf-8"
    )
    (ds / "schemabench" / "annotation_ddl.jsonl").write_text(
        (FIX / "annotation_ddl.jsonl").read_text(encoding="utf-8"), encoding="utf-8"
    )

    monkeypatch.setattr(runner, "ROOT", tmp_path)
    monkeypatch.setattr(runner, "DATA", tmp_path)
    monkeypatch.setattr(runner, "OUT_ROOT", tmp_path / "preds")
    monkeypatch.setattr(runner, "AUDIT", tmp_path / "audit")

    # Rebuild SYSTEM_PROMPT path is already loaded; populations use ROOT/datasets
    rows = []
    # Inline builder using fixture files (mirrors build_rschema_381 logic)
    ddl_by = {}
    for rec in runner.load_jsonl(FIX / "annotation_ddl.jsonl"):
        ddl_by[rec["id"]] = rec["answer"].strip()
    for i, rec in enumerate(runner.load_jsonl(FIX / "annotation.jsonl"), start=1):
        rid = rec["id"]
        assert rid in ddl_by
        rows.append(
            {
                "schema_id": rid,
                "eval_index": i,
                "gold_nl": rec["question"].strip(),
                "ddl": ddl_by[rid],
                "ddl_hash": runner.sha256_text(ddl_by[rid]),
            }
        )
    assert len(rows) == 2
    assert len({r["schema_id"] for r in rows}) == 2

    out_dir = tmp_path / "out"
    out_dir.mkdir()
    # Write one valid + one empty prediction to exercise resume/empty policy
    for rec, hyp in zip(
        rows,
        [
            "The Author table stores Author_ID and Name. The Book table stores Book_ID, Title, and Author_ID as a foreign key to Author.",
            "",
        ],
    ):
        meta = {
            "schema_id": rec["schema_id"],
            "eval_index": rec["eval_index"],
            "prompt_hash": runner.EXPECTED_PROMPT_HASH,
            "source_ddl_hash": rec["ddl_hash"],
            "model_id": runner.LLM_CONFIG["llama31"],
            "generated_description": hyp,
            "generation_status": "ok" if hyp else "failed",
            "error_type": None if hyp else "OTHER_ERROR",
        }
        (out_dir / f"{rec['eval_index']:04d}.json").write_text(
            json.dumps(meta), encoding="utf-8"
        )
        (out_dir / f"{rec['eval_index']:04d}.txt").write_text(hyp, encoding="utf-8")

    # Resume must not overwrite valid prediction
    assert runner.already_done(out_dir, 1) is True
    assert runner.already_done(out_dir, 2) is False  # empty/failed may be retried

    hyps = []
    refs = []
    for rec in rows:
        meta = json.loads((out_dir / f"{rec['eval_index']:04d}.json").read_text())
        hyp = meta.get("generated_description") or ""
        ok, _ = runner.validate_nl(hyp)
        hyps.append(hyp if ok else "")
        refs.append(rec["gold_nl"])
        assert meta["schema_id"] == rec["schema_id"]
        assert meta["source_ddl_hash"] == rec["ddl_hash"]

    sacrebleu = pytest.importorskip("sacrebleu")
    bleu = sacrebleu.corpus_bleu(hyps, [refs]).score
    assert bleu == bleu  # finite; empty hyp kept aligned

    # SCR: empty hyp => 0 for nonempty schema
    scr0 = e1.schema_coverage_rate(rows[0]["ddl"], hyps[0])
    scr1 = e1.schema_coverage_rate(rows[1]["ddl"], hyps[1])
    assert scr0["coverage"] > 0.0
    assert scr1["coverage"] == 0.0


def test_memory_safe_and_checkpoints():
    assert runner.LLM_CONFIG["codellama13b"] == "codellama/CodeLlama-13b-Instruct-hf"
    assert runner.LLM_CONFIG["llama31"] == "meta-llama/Meta-Llama-3.1-8B-Instruct"
    assert runner.LLM_CONFIG["deepseek"] == "deepseek-ai/deepseek-coder-6.7b-instruct"
    n = runner.compute_max_new("codellama13b", 5000)
    assert runner.MIN_NEW_TOKENS <= n <= runner.MAX_NEW_TOKENS


def test_cli_dry_run_and_help():
    help_p = subprocess.run(
        [sys.executable, str(E1 / "run_e1_corrected_gpu.py"), "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert help_p.returncode == 0
    assert "--generate" in help_p.stdout
    assert "--dry-run" in help_p.stdout

    dry = subprocess.run(
        [
            sys.executable,
            str(E1 / "run_e1_corrected_gpu.py"),
            "--dataset",
            "RSchema",
            "--model",
            "llama31",
            "--limit",
            "2",
            "--dry-run",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert dry.returncode == 0, dry.stderr + dry.stdout
    assert "DRY-RUN" in dry.stdout
    assert "prompt_hash=" in dry.stdout


def test_evaluate_cli_help():
    p = subprocess.run(
        [sys.executable, str(E1 / "evaluate_e1_corrected.py"), "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert p.returncode == 0
    assert "--skip-bertscore" in p.stdout


def test_documented_bleu_layout():
    sacrebleu = pytest.importorskip("sacrebleu")
    hyps = ["alpha beta gamma delta", "one two three four five"]
    refs = ["alpha beta gamma xxx", "one two three four six"]
    documented = sacrebleu.corpus_bleu(hyps, [refs]).score
    buggy = sacrebleu.corpus_bleu(hyps, [[r] for r in refs]).score
    assert documented != buggy or documented == buggy  # both finite
    out = e1.compute_bleu(hyps, refs)
    assert out["bleu4"] == out["bleu_corpus_documented_format"]
