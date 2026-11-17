"""Regression tests for E3 PRIMARY (765-schema) constructor-isolation reproduction."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E3 = ROOT / "experiments" / "E3"
AUDIT = ROOT / "results" / "metrics" / "reproduced" / "E3_AUDIT"
MANIFEST = E3 / "manifests" / "RSCHEMA_381_ELIGIBLE.csv"
COMPARISON = AUDIT / "metrics" / "E3_CELL_COMPARISON_105.csv"
FINAL = AUDIT / "metrics" / "E3_PRIMARY_FINAL.csv"
TEX = AUDIT / "latex" / "tab_e3_overall_verified.tex"
TEX_PAPER = AUDIT / "latex" / "tab_e3_overall_paper_historical.tex"
ISOLATION = AUDIT / "isolation" / "isolation_summary.json"
MATCH = AUDIT / "E3_MATCH_COUNTS.json"

# Exact TABLE IX / manuscript screenshot cells (archived as *_paper).
SCREENSHOT_TABLE_IX = {
    ("Enterprise-145", "CodeLlama-13B"): dict(nGED=0.324, Hall=0.085, T=0.553, A=0.479, D=0.315, E=0.479, R=0.460),
    ("Enterprise-145", "Llama-3.1-8B"): dict(nGED=0.340, Hall=0.071, T=0.596, A=0.294, D=0.277, E=0.489, R=0.528),
    ("Enterprise-145", "DeepSeek-Coder"): dict(nGED=0.549, Hall=0.120, T=0.492, A=0.167, D=0.117, E=0.348, R=0.296),
    ("Enterprise-145", "Claude Sonnet 4.6"): dict(nGED=0.047, Hall=0.027, T=0.758, A=0.703, D=0.685, E=0.744, R=0.847),
    ("Enterprise-145", "GPT-5.4-mini"): dict(nGED=0.058, Hall=0.026, T=0.753, A=0.683, D=0.664, E=0.720, R=0.816),
    ("RSchema", "CodeLlama-13B"): dict(nGED=0.369, Hall=0.020, T=0.987, A=0.986, D=0.483, E=0.981, R=0.969),
    ("RSchema", "Llama-3.1-8B"): dict(nGED=0.493, Hall=0.020, T=0.989, A=0.986, D=0.343, E=0.976, R=0.970),
    ("RSchema", "DeepSeek-Coder"): dict(nGED=0.383, Hall=0.073, T=0.940, A=0.807, D=0.508, E=0.806, R=0.802),
    ("RSchema", "Claude Sonnet 4.6"): dict(nGED=0.468, Hall=0.009, T=0.994, A=0.991, D=0.351, E=0.995, R=0.994),
    ("RSchema", "GPT-5.4-mini"): dict(nGED=0.471, Hall=0.010, T=0.993, A=0.990, D=0.345, E=0.995, R=0.991),
    ("SchemaBench", "CodeLlama-13B"): dict(nGED=0.272, Hall=0.054, T=0.760, A=0.697, D=0.527, E=0.714, R=0.623),
    ("SchemaBench", "Llama-3.1-8B"): dict(nGED=0.369, Hall=0.058, T=0.806, A=0.491, D=0.370, E=0.711, R=0.672),
    ("SchemaBench", "DeepSeek-Coder"): dict(nGED=0.550, Hall=0.096, T=0.649, A=0.251, D=0.184, E=0.523, R=0.423),
    ("SchemaBench", "Claude Sonnet 4.6"): dict(nGED=0.194, Hall=0.024, T=0.964, A=0.945, D=0.773, E=0.957, R=0.930),
    ("SchemaBench", "GPT-5.4-mini"): dict(nGED=0.198, Hall=0.025, T=0.961, A=0.921, D=0.745, E=0.951, R=0.934),
}
METRICS = ("nGED", "Hall", "T", "A", "D", "E", "R")


def test_rschema_381_manifest_unique_ids():
    assert MANIFEST.exists(), "RSchema-381 manifest must be published"
    rows = list(csv.DictReader(MANIFEST.open()))
    assert len(rows) == 381
    ids = [r["schema_id"] for r in rows]
    assert len(ids) == len(set(ids))
    serials = sorted(int(r["serial_in_518"]) for r in rows)
    assert serials[0] >= 1
    assert serials[-1] <= 518
    assert serials != list(range(1, 382))


def test_primary_metrics_15_groups_105_cells():
    assert FINAL.exists(), "E3_PRIMARY_FINAL.csv missing — run experiments/E3/evaluate.py"
    rows = list(csv.DictReader(FINAL.open()))
    assert len(rows) == 15
    pops = {(r["Dataset"], int(r["N"])) for r in rows}
    assert ("Enterprise-145", 145) in pops
    assert ("RSchema", 381) in pops
    assert ("SchemaBench", 239) in pops
    assert COMPARISON.exists()
    cells = list(csv.DictReader(COMPARISON.open()))
    assert len(cells) == 105
    assert MATCH.exists()
    counts = json.loads(MATCH.read_text())
    assert counts["cells_total"] == 105
    assert counts["MATCH"] + counts["MISMATCH"] + counts.get("UNVERIFIABLE", 0) == 105
    assert counts["UNVERIFIABLE"] == 0


def test_isolation_summary_765():
    assert ISOLATION.exists()
    iso = json.loads(ISOLATION.read_text())
    total = sum(v["identical_across_5_constructors_and_frozen"] for v in iso.values())
    assert total == 765
    for ds, v in iso.items():
        assert v["frozen_missing"] == 0
        assert v["mismatch_or_incomplete"] == 0


def test_latex_and_config():
    assert TEX.exists()
    tex = TEX.read_text()
    assert "tab:e3_overall" in tex
    assert "0.047" in tex  # Enterprise Claude nGED
    assert "\\textbf{0.991}" in tex  # RSchema Attr tie (PRIMARY)
    assert "0.704" in tex  # Enterprise Claude Attr PRIMARY (screenshot was 0.703)
    assert TEX_PAPER.exists()
    paper_tex = TEX_PAPER.read_text()
    assert "0.703" in paper_tex  # screenshot TABLE IX Attr
    assert "\\textbf{0.986}" in paper_tex or "0.986" in paper_tex
    cfg = (E3 / "config.yaml").read_text()
    assert "VERIFIED" in cfg
    assert "381" in cfg
    assert "hallucination_dims" in cfg
    prompt = (ROOT / "prompts" / "constructor.txt").read_text()
    assert "ddl" in prompt and "metadata" in prompt
    desc = (ROOT / "prompts" / "describer_detailed.txt").read_text()
    assert "paragraph" in desc.lower()


def test_screenshot_table_ix_matches_paper_column():
    """Public clone can reproduce the manuscript screenshot from frozen CSV (*_paper)."""
    rows = list(csv.DictReader(FINAL.open()))
    assert len(rows) == 15
    mismatches = []
    for r in rows:
        key = (r["Dataset"], r["Constructor"])
        expected = SCREENSHOT_TABLE_IX[key]
        for m in METRICS:
            got = float(r[f"{m}_paper"])
            if abs(got - expected[m]) > 1e-9:
                mismatches.append((key, m, expected[m], got))
    assert mismatches == [], f"screenshot drift: {mismatches[:5]}"


def test_primary_vs_screenshot_locked_27_cells():
    rows = list(csv.DictReader(FINAL.open()))
    n_mis = 0
    for r in rows:
        key = (r["Dataset"], r["Constructor"])
        expected = SCREENSHOT_TABLE_IX[key]
        for m in METRICS:
            if abs(float(r[f"{m}_3dec"]) - expected[m]) > 1e-9:
                n_mis += 1
    assert n_mis == 27
    counts = json.loads(MATCH.read_text())
    assert counts["MISMATCH"] == 27
    assert counts["MATCH"] == 78


def test_run_refuses_online():
    import subprocess
    import sys

    proc = subprocess.run(
        [sys.executable, str(E3 / "run.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode != 0
    blob = (proc.stdout + proc.stderr).lower()
    assert "disabled" in blob or "refus" in blob or "no api" in blob
