"""Tests for scripts/build_e0_paper_comparison.py Domain comparator semantics."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "build_e0_paper_comparison", ROOT / "scripts" / "build_e0_paper_comparison.py"
)
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


def test_status_for_numeric_direct_domain_pass_within_tol():
    st, p, rec = mod.status_for(0.115, 0.114962)
    assert st == "PASS"
    assert p == pytest.approx(0.115)
    assert rec == pytest.approx(0.114962)


def test_status_for_numeric_direct_domain_pass_on_3dp_rounding():
    # 0.149578 rounds to 0.150, so equality-at-3dp alone would fail against 0.149;
    # abs(diff) > 0.0005 → MISMATCH under declared policy.
    st, _, _ = mod.status_for(0.149, 0.149578)
    assert st == "MISMATCH"


def test_status_for_baseline_domain_both_dash():
    st, p, rec = mod.status_for("--", None)
    assert st == "PASS"
    assert p is None and rec is None


def test_status_for_baseline_domain_dash_vs_numeric_is_mismatch():
    st, p, rec = mod.status_for("--", 0.115)
    assert st == "MISMATCH"
    assert p is None
    assert rec == pytest.approx(0.115)


def test_table_vi_domain_branch_direct_numeric(tmp_path, monkeypatch):
    """Direct Domain must compare numeric paper vs numeric recomputed (not force '--')."""
    paper = {
        "_meta": {},
        "tab:e0_overall": {
            "RSchema|CodeLlama-13B": {
                "nged": 0.583,
                "halluc": 0.669,
                "tables": 0.554,
                "attributes": 0.414,
                "domain": 0.115,
                "entity": 0.301,
                "referential": 0.14,
            },
        },
        "tab:e0_baselines": {
            "CodeLlama-13B|Direct": {
                "nged": 0.583,
                "halluc": 0.669,
                "tables": 0.554,
                "attributes": 0.414,
                "domain": 0.115,
                "entity": 0.301,
                "referential": 0.14,
            },
            "CodeLlama-13B|One-shot": {
                "nged": 0.613,
                "halluc": 0.728,
                "tables": 0.587,
                "attributes": 0.379,
                "domain": None,
                "entity": 0.13,
                "referential": 0.034,
            },
        },
    }
    tv = tmp_path / "E0_TABLE_V_FINAL.csv"
    tvi = tmp_path / "E0_TABLE_VI_FINAL.csv"
    out = tmp_path / "E0_PAPER_COMPARISON.csv"
    tv.write_text(
        "dataset,model,n,failed,domain_n,status,present,valid,missing,"
        "nged,halluc,tables,attributes,domain,entity,referential\n"
        "RSchema,CodeLlama-13B,518,0,381,COMPLETE,518,518,0,"
        "0.583048,0.668598,0.553864,0.414443,0.114962,0.300543,0.139797\n",
        encoding="utf-8",
    )
    tvi.write_text(
        "dataset,model,method,n,failed,status,present,valid,missing,"
        "nged,halluc,tables,attributes,domain,entity,referential\n"
        "RSchema,CodeLlama-13B,Direct,518,0,COMPLETE,518,518,0,"
        "0.583048,0.668598,0.553864,0.414443,0.114962,0.300543,0.139797\n"
        "RSchema,CodeLlama-13B,One-shot,518,3,ARCHIVE_AGGREGATE,515,515,0,"
        "0.613,0.728,0.587,0.379,--,0.130,0.034\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    monkeypatch.setattr(mod, "PAPER", paper)
    monkeypatch.setattr(mod, "OUT", out)
    # Point loader at our temp FINAL CSVs via ROOT-relative paths used in main().
    (tmp_path / "results/metrics/reproduced").mkdir(parents=True)
    (tmp_path / "results/metrics/reproduced/E0_TABLE_V_FINAL.csv").write_text(
        tv.read_text(encoding="utf-8"), encoding="utf-8"
    )
    (tmp_path / "results/metrics/reproduced/E0_TABLE_VI_FINAL.csv").write_text(
        tvi.read_text(encoding="utf-8"), encoding="utf-8"
    )
    assert mod.main() == 0
    rows = list(__import__("csv").DictReader(out.open(encoding="utf-8")))
    direct_dom = [
        r
        for r in rows
        if r["Table"] == "VI" and r["Method"] == "Direct" and r["Metric"] == "domain"
    ][0]
    oneshot_dom = [
        r
        for r in rows
        if r["Table"] == "VI" and r["Method"] == "One-shot" and r["Metric"] == "domain"
    ][0]
    assert direct_dom["Status"] == "PASS", direct_dom
    assert oneshot_dom["Status"] == "PASS_ARCHIVE", oneshot_dom
    assert oneshot_dom["Recomputed"] == "--"
