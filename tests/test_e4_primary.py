"""PRIMARY E4 verified values and offline evaluate entry point."""
from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "E4"))

from verified_values import E4_RECOVERY, E4_SPLIT  # noqa: E402


def test_split_ten_cells():
    assert len(E4_SPLIT) == 5
    assert E4_SPLIT["MD Domain"]["inferable"] == {"recall": 0.196, "gold_n": 8578}
    assert E4_SPLIT["MD Domain"]["non_inferable"] == {"recall": 0.451, "gold_n": 36669}
    assert E4_SPLIT["ME Entity"]["non_inferable"]["recall"] == 0.447
    assert E4_SPLIT["ME Entity"]["inferable"]["recall"] == 0.871


def test_recovery_twenty_cells():
    assert E4_RECOVERY["MD Domain"] == {
        "gold_n": 8578, "direct": 0.196, "rt": 0.049, "retention": 0.251,
    }
    assert E4_RECOVERY["ME Entity"]["gold_n"] == 2087
    assert E4_RECOVERY["ME Entity"]["direct"] == 0.877
    assert E4_RECOVERY["MR Referential"]["gold_n"] == 4197
    # Entity/Referential Split N > Recovery N (duplicate Direct rows)
    assert E4_SPLIT["ME Entity"]["inferable"]["gold_n"] == 2161
    assert E4_SPLIT["MR Referential"]["inferable"]["gold_n"] == 4214


def test_no_stale_domain_or_entity_values():
    stale = {
        (0.409, 1574), (0.479, 35573), (0.032,), (0.078,),
        (0.635,), (0.425, 14284), (0.611, 242556),
    }
    # Domain must not equal superseded SchemaBench-only / domain_facts cells
    d = E4_SPLIT["MD Domain"]["inferable"]
    assert (d["recall"], d["gold_n"]) not in {(0.409, 1574), (0.425, 14284)}
    assert E4_SPLIT["ME Entity"]["non_inferable"]["recall"] != 0.635


def test_evaluate_and_generate(tmp_path=None):
    env = {"PATH": "/usr/bin:/bin", "PYTHONPATH": str(ROOT)}
    p = subprocess.run(
        [sys.executable, str(ROOT / "experiments" / "E4" / "evaluate_e4_primary.py"), "--check-only"],
        cwd=ROOT, capture_output=True, text=True, timeout=60, env={**env},
    )
    assert p.returncode == 0, p.stdout + p.stderr
    assert "PASS" in p.stdout


def test_cells_csv_if_present():
    path = ROOT / "results" / "metrics" / "reproduced" / "E4_cells.csv"
    if not path.is_file():
        pytest.skip("E4_cells.csv not generated yet")
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    assert any(r["table_label"] == "tab:e4_split" and r["status"] == "VERIFIED" for r in rows)
    assert any(r["table_label"] == "tab:e4_recovery" and r["metric"] == "retention" for r in rows)
