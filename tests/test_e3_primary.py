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
ISOLATION = AUDIT / "isolation" / "isolation_summary.json"
MATCH = AUDIT / "E3_MATCH_COUNTS.json"


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
    assert "\\textbf{0.991}" in tex  # RSchema Attr tie
    cfg = (E3 / "config.yaml").read_text()
    assert "VERIFIED" in cfg
    assert "381" in cfg
    assert "hallucination_dims" in cfg
    prompt = (ROOT / "prompts" / "constructor.txt").read_text()
    assert "ddl" in prompt and "metadata" in prompt
    desc = (ROOT / "prompts" / "describer_detailed.txt").read_text()
    assert "paragraph" in desc.lower()


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
