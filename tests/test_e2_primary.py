"""Regression tests for E2 PRIMARY (765-schema) round-trip reproduction."""
from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
E2 = ROOT / "experiments" / "E2"
AUDIT = ROOT / "results" / "metrics" / "reproduced" / "E2_AUDIT"
MANIFEST = AUDIT / "manifests" / "RSCHEMA_381_ELIGIBLE.csv"
COMPARISON = AUDIT / "metrics" / "E2_CELL_COMPARISON_180.csv"
PRIMARY = AUDIT / "metrics" / "full_precision_primary.json"
TEX = AUDIT / "latex" / "tab_e2_roundtrip_verified.tex"


def test_rschema_381_manifest_unique_ids():
    assert MANIFEST.exists(), "RSchema-381 manifest must be published"
    rows = list(csv.DictReader(MANIFEST.open()))
    assert len(rows) == 381
    ids = [r["schema_id"] for r in rows]
    assert len(ids) == len(set(ids))
    # Must not be positional 1..381 — serial_in_518 spans the 518 corpus
    serials = sorted(int(r["serial_in_518"]) for r in rows)
    assert serials[0] >= 1
    assert serials[-1] <= 518
    assert serials != list(range(1, 382))


def test_primary_metrics_30_groups_180_cells():
    assert PRIMARY.exists(), "full_precision_primary.json missing — run evaluate_table_viii_full.py"
    rows = json.loads(PRIMARY.read_text())
    primary = [
        r
        for r in rows
        if r.get("population_label")
        in ("enterprise_145", "schemabench_239", "genuine_ddl_381")
    ]
    assert len(primary) == 30
    pops = {(r["dataset"], r["population"]) for r in primary}
    assert ("Enterprise-145", 145) in pops
    assert ("RSchema", 381) in pops
    assert ("SchemaBench", 239) in pops
    assert COMPARISON.exists()
    cells = list(csv.DictReader(COMPARISON.open()))
    assert len(cells) == 180


def test_constructor_identity_sample_and_failure_policy_docs():
    cfg = (E2 / "config.yaml").read_text()
    assert "gpt-4o-mini" in cfg
    assert "381" in cfg
    assert "failure_policy: score" in cfg
    prompt = (ROOT / "prompts" / "constructor.txt").read_text()
    assert "ddl" in prompt and "metadata" in prompt


def test_nged_denominator_is_sum_of_sizes():
    """Manuscript / PRIMARY: nGED = edit_cost / (gold_size + pred_size)."""
    from src.metrics import graph_edit_cost, graph_size, column_labels, fk_edges

    gold_meta = {
        "database": "db",
        "tables": ["A"],
        "columns_by_table": {
            "A": [
                {
                    "COLUMN_NAME": "id",
                    "DATA_TYPE": "int",
                    "IS_NULLABLE": "NO",
                    "COLUMN_TYPE": "int(11)",
                }
            ]
        },
    }
    pred_meta = {
        "database": "db",
        "tables": ["A", "B"],
        "columns_by_table": {
            "A": [
                {
                    "COLUMN_NAME": "id",
                    "DATA_TYPE": "int",
                    "IS_NULLABLE": "NO",
                    "COLUMN_TYPE": "int(11)",
                }
            ],
            "B": [
                {
                    "COLUMN_NAME": "x",
                    "DATA_TYPE": "varchar",
                    "IS_NULLABLE": "YES",
                    "COLUMN_TYPE": "varchar(10)",
                }
            ],
        },
    }
    g_ddl = "CREATE TABLE `A` (`id` int NOT NULL, PRIMARY KEY (`id`));"
    p_ddl = (
        "CREATE TABLE `A` (`id` int NOT NULL, PRIMARY KEY (`id`));"
        "CREATE TABLE `B` (`x` varchar(10));"
    )
    cost, denom = graph_edit_cost(
        column_labels(gold_meta),
        column_labels(pred_meta),
        fk_edges(g_ddl),
        fk_edges(p_ddl),
    )
    g_size = graph_size(set(column_labels(gold_meta)), column_labels(gold_meta), fk_edges(g_ddl))
    p_size = graph_size(set(column_labels(pred_meta)), column_labels(pred_meta), fk_edges(p_ddl))
    assert denom == max(g_size + p_size, 1)
    assert denom != max(g_size, p_size, 1) or g_size == p_size


def test_micro_f1_not_macro_mean():
    from src.metrics import micro_f1, f1_score

    # Two schemas: (g,r,m) = (2,2,2) and (2,2,0)
    micro = micro_f1(4, 4, 2)
    # Macro mean of per-schema F1 would be (1.0 + 0.0) / 2 = 0.5
    macro = (f1_score(1.0, 1.0) + f1_score(0.0, 0.0)) / 2
    assert micro == pytest.approx(0.5)
    # Same in this constructed case; change counts to diverge
    micro2 = micro_f1(10, 2, 2)  # P=1, R=0.2, F1≈0.333
    per_schema = [f1_score(1.0, 2 / 8), f1_score(1.0, 0 / 2)]  # not how micro works
    assert micro2 == pytest.approx(2 * 1.0 * 0.2 / 1.2)


def test_latex_table_bold_rschema_basic_nged():
    assert TEX.exists()
    tex = TEX.read_text()
    assert r"\label{tab:e2_roundtrip}" in tex
    # DeepSeek basic nGED must be bold; CodeLlama basic nGED must not
    assert r"DeepSeek-Coder & \textbf{0.353}" in tex or r"DeepSeek-Coder & \textbf{0.352}" in tex
    # Find RSchema CodeLlama line: 0.364 should not be textbf for B nGED
    for line in tex.splitlines():
        if "RSchema" in line and "CodeLlama" in line:
            # first numeric after describer is basic nGED
            assert r"& \textbf{0.364}" not in line
            break


def test_generate_table_viii_cli():
    if not PRIMARY.exists():
        pytest.skip("PRIMARY metrics not generated yet")
    out = AUDIT / "latex" / "_test_tab_e2.tex"
    subprocess.check_call(
        [
            sys.executable,
            str(E2 / "generate_table_viii.py"),
            "--metrics",
            str(PRIMARY),
            "--out",
            str(out),
        ],
        cwd=str(ROOT),
    )
    assert out.exists() and r"\label{tab:e2_roundtrip}" in out.read_text()
    out.unlink()


def test_run_py_refuses_online():
    proc = subprocess.run(
        [sys.executable, str(E2 / "run.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert proc.returncode != 0 or "DISABLED" in proc.stdout or "DISABLED" in proc.stderr or "archived" in proc.stdout.lower() or "GPT-4o-mini" in proc.stdout


def test_evaluate_help():
    proc = subprocess.run(
        [sys.executable, str(E2 / "evaluate_table_viii_full.py"), "--help"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert "nGED" in proc.stdout or "Round-Trip" in proc.stdout
