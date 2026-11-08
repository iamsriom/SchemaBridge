"""Automated checks for E5 sample, pairing, and metric integrity."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.e5.gold import constraint_score, load_population, schema_size  # noqa: E402
from experiments.e5.sample_select import build_sample_manifest  # noqa: E402


def test_size_and_complexity_definitions():
    assert schema_size(5, 50) == "Small"
    assert schema_size(5, 51) == "Medium"
    assert schema_size(16, 10) == "Large"
    s = constraint_score(f=2, c=0, u=0, n_col=20, n_tab=2)
    assert abs(s - (4 + 0 + 0 + 0.2 * 0)) < 1e-9


def test_population_count():
    pop = load_population()
    assert len(pop) == 902
    by = {}
    for r in pop:
        by[r["dataset"]] = by.get(r["dataset"], 0) + 1
    assert by["enterprise145"] == 145
    assert by["rschema"] == 518
    assert by["schemabench"] == 239


def test_sample_manifest_seed42():
    pop = load_population()
    m = build_sample_manifest(pop, per_dataset=40, seed=42)
    sel = [r for r in m if int(r["selected"]) == 1]
    assert len(sel) == 120
    for ds in ("enterprise145", "rschema", "schemabench"):
        assert sum(1 for r in sel if r["dataset"] == ds) == 40
    # Determinism
    m2 = build_sample_manifest(pop, per_dataset=40, seed=42)
    ids1 = [(r["dataset"], r["schema_id"]) for r in m if int(r["selected"])]
    ids2 = [(r["dataset"], r["schema_id"]) for r in m2 if int(r["selected"])]
    assert ids1 == ids2


@pytest.mark.skipif(not (HERE / "outputs" / "e5_per_schema.csv").exists(), reason="run first")
def test_per_schema_tp_consistency():
    with (HERE / "outputs" / "e5_per_schema.csv").open() as f:
        rows = list(csv.DictReader(f))
    assert rows
    for r in rows:
        for dim in ("tables", "attributes", "domain", "entity", "referential"):
            tp = int(float(r[f"{dim}_tp"] or 0))
            fp = int(float(r[f"{dim}_fp"] or 0))
            fn = int(float(r[f"{dim}_fn"] or 0))
            g = int(float(r[f"{dim}_gold"] or 0))
            rec = int(float(r[f"{dim}_recreated"] or 0))
            m = int(float(r[f"{dim}_matched"] or 0))
            assert tp == m
            assert fp == max(0, rec - m)
            assert fn == max(0, g - m)
