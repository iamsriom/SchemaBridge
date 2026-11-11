"""Regression tests for scripts/build_e0_paper_comparison.py Domain logic."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "build_e0_paper_comparison",
    ROOT / "scripts" / "build_e0_paper_comparison.py",
)
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


def test_domain_both_na_is_pass():
    st, p, r = mod.status_for(None, None)
    assert st == "PASS" and p is None and r is None
    st, p, r = mod.status_for("--", None)
    assert st == "PASS"


def test_direct_domain_numeric_comparison():
    st, p, r = mod.status_for(0.115, 0.114962)
    assert st == "PASS"
    st, p, r = mod.status_for(0.115, 0.208)
    assert st == "MISMATCH"


def test_one_numeric_vs_na_is_mismatch():
    st, _, _ = mod.status_for(0.115, None)
    assert st == "BLOCKED"  # paper has number, recomputed missing
    st, _, _ = mod.status_for(None, 0.115)
    assert st == "MISMATCH"  # paper N/A, recomputed numeric


def test_archive_annotation():
    assert mod.annotate_archive("PASS", "ARCHIVE_AGGREGATE") == "PASS_ARCHIVE"
    assert mod.annotate_archive("MISMATCH", "ARCHIVE_AGGREGATE") == "MISMATCH_ARCHIVE"
    assert mod.annotate_archive("PASS", "COMPLETE") == "PASS"
