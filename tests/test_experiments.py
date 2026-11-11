"""E1-E5 status tests.  Each one pins the *currently true* status and is skipped (clearly) when
the artefact that justifies the status is missing, so a later fix of the artefacts does not
silently keep a stale expectation.
"""
import subprocess
import sys
from pathlib import Path

import pytest

import reproduce_tables as rt

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def refs():
    return rt.load_refs()


def status(res, label, dataset):
    return next(l for l in res.labels if l.table_label == label and l.dataset == dataset)


# ------------------------------------------------------------------ E1
@pytest.mark.skipif(not (rt.ARCHIVED / "e1_rschema_schema2text_evaluation.json").is_file(),
                    reason="E1 archived metrics missing")
def test_e1_rschema_detailed_passes_for_open_models(refs):
    res = rt.run_e1(refs)
    lab = status(res, "tab:e1_s2t", "RSchema")
    assert lab.status == rt.PARTIAL and lab.n_mismatch == 0 and lab.n_pass == 9
    for model in rt.OPEN_MODELS:
        d = {c.metric: c for c in res.cells if c.dataset == "RSchema" and c.model == model}
        for m in ("bleu4_detailed", "rougeL_detailed", "scr_detailed"):
            assert d[m].status == rt.PASS, (model, m, d[m])
        assert d["bertscore_detailed"].status == rt.BLOCKED  # skip_bertscore
        assert d["bleu4_basic"].status == rt.BLOCKED


def test_e1_blocked_labels(refs):
    res = rt.run_e1(refs)
    assert status(res, "tab:e1_s2t", "SchemaBench").status == rt.BLOCKED
    assert status(res, "tab:e1_s2t", "Enterprise-145").status == rt.BLOCKED
    # Enterprise BLEU/ROUGE/BERT are 'n/a' in the paper -> no cell at all (only SCR)
    ent = [c for c in res.cells if c.dataset == "Enterprise-145"]
    assert {c.metric for c in ent} == {"scr_basic", "scr_detailed"}
    closed = [c for c in res.cells if c.model in rt.CLOSED_MODELS]
    assert closed and all(c.status == rt.BLOCKED for c in closed)


# ------------------------------------------------------------------ E2
@pytest.mark.skipif(not (rt.ARCHIVED / "e2_rschema_roundtrip_evaluation.json").is_file(),
                    reason="E2 archived metrics missing")
def test_e2_legacy_archive_harness_still_runs(refs):
    """Legacy ``reproduce_tables.run_e2`` compares the N=518 Detailed archive.

    Canonical PRIMARY results (145/381/239) live under
    ``results/metrics/reproduced/E2_AUDIT/`` and are covered by ``test_e2_primary.py``.
    Paper reference values are PRIMARY, so archive cells are expected to MISMATCH
    or remain BLOCKED for Basic/closed/incomplete slices.
    """
    res = rt.run_e2(refs)
    lab = status(res, "tab:e2_roundtrip", "RSchema")
    assert lab.n_blocked > 0
    assert lab.status in (rt.MISMATCH, rt.PARTIAL, rt.PASS, rt.BLOCKED)
    basic = [c for c in res.cells if c.dataset == "RSchema" and c.variant == "basic"]
    assert basic and all(c.status == rt.BLOCKED for c in basic)
    d = {c.metric: c for c in res.cells if c.dataset == "RSchema" and c.model == "codellama13b"}
    assert d["nged_detailed"].status in (rt.PASS, rt.MISMATCH)
    assert d["tables_detailed"].status in (rt.PASS, rt.MISMATCH)


def test_e2_schemabench_incomplete_is_blocked(refs):
    res = rt.run_e2(refs)
    lab = status(res, "tab:e2_roundtrip", "SchemaBench")
    assert lab.status == rt.BLOCKED
    assert "incomplete" in lab.reason and "/239" in lab.reason
    assert status(res, "tab:e2_roundtrip", "Enterprise-145").status == rt.BLOCKED


# ------------------------------------------------------------------ E3 / E4 / E5
def test_e3_constructor_isolation_blocked(refs):
    res = rt.run_e3(refs)
    lab = status(res, "tab:e3_overall", "all")
    assert lab.status == rt.BLOCKED
    assert "GPT-5.4-mini" in lab.reason or "constructor" in lab.reason.lower()


@pytest.mark.skipif(not (rt.ARCHIVED / "e4_cases3_results.json").is_file(), reason="E4 archived metrics missing")
def test_e4_partial_and_exports_rows(refs):
    res = rt.run_e4(refs)
    lab = status(res, "tab:e4_split", "Enterprise-145")
    assert lab.status == rt.PARTIAL
    assert status(res, "tab:e4_by_dataset", "multi").status == rt.BLOCKED
    rows = res.extra_csvs["E4_archived_cases_aggregates.csv"]
    assert {r["source"] for r in rows} == {"cases3_table_attr_hiding", "cases_structural_imputation"}
    cases3_all = next(r for r in rows if r["source"] == "cases3_table_attr_hiding" and r["group"] == "overall"
                      and r["element"] == "entity")
    assert cases3_all["f1"] == pytest.approx(0.2053, abs=1e-4)


def test_e5_cost_blocked(refs):
    res = rt.run_e5(refs)
    lab = status(res, "tab:e5_cost", "multi")
    assert lab.status == rt.BLOCKED
    assert "billing" in lab.reason.lower() or "usage" in lab.reason.lower() or "cost" in lab.reason.lower()


# ------------------------------------------------------------------ entry points
@pytest.mark.parametrize("exp", ["E0", "E1", "E2", "E3", "E4", "E5"])
def test_experiment_files_exist(exp):
    d = ROOT / "experiments" / exp
    for f in ("README.md", "config.yaml", "evaluate.py"):
        assert (d / f).is_file(), f"{exp}/{f}"
    assert (d / "run.py").is_file() == (exp != "E5")


@pytest.mark.parametrize("exp", ["E1", "E2", "E3", "E4"])
def test_run_py_refuses_online(exp):
    p = subprocess.run([sys.executable, str(ROOT / "experiments" / exp / "run.py"), "--online"],
                       capture_output=True, text=True, cwd=ROOT, timeout=60,
                       env={"PATH": "/usr/bin:/bin"})  # no SCHEMABRIDGE_ALLOW_ONLINE
    assert p.returncode == 2
    assert "DISABLED" in p.stdout and "archived predictions" in p.stdout and "--online ignored" in p.stdout


def test_e0_run_py_online_requires_confirm_paid():
    """E0 routes --online to run_direct_api.py but still requires --confirm-paid."""
    p = subprocess.run(
        [sys.executable, str(ROOT / "experiments" / "E0" / "run.py"), "--online"],
        capture_output=True,
        text=True,
        cwd=ROOT,
        timeout=60,
        env={"PATH": "/usr/bin:/bin"},
    )
    assert p.returncode == 2
    combined = (p.stdout + p.stderr).lower()
    assert "confirm-paid" in combined
    assert "disabled" not in combined  # E0 is not the legacy refuse_online path


def test_configs_load_and_match_paper_semantics():
    yaml = pytest.importorskip("yaml")
    cfg = yaml.safe_load((ROOT / "configs" / "experiment_configs.yaml").read_text())
    exps = cfg["experiments"]
    assert set(exps) == {"E0", "E1", "E2", "E3", "E4", "E5"}
    assert "tab:e0_overall" in exps["E0"]["paper_tables"] and exps["E0"]["name"] == "text2schema"
    assert "tab:e1_s2t" in exps["E1"]["paper_tables"] and exps["E1"]["name"] == "schema2text"
    assert "tab:e2_roundtrip" in exps["E2"]["paper_tables"] and exps["E2"]["constructor"] == "gpt-4o-mini"
    assert exps["E3"]["name"] == "constructor_isolation"
    assert exps["E5"]["name"] == "cost_latency"
    models = yaml.safe_load((ROOT / "configs" / "model_configs.yaml").read_text())["models"]
    assert models["claude_sonnet_4_6"]["archived_predictions"] is False
    assert models["gpt4omini_constructor"]["model_id"] == "gpt-4o-mini"
    for e in ("E0", "E1", "E2", "E3", "E4", "E5"):
        ec = yaml.safe_load((ROOT / "experiments" / e / "config.yaml").read_text())
        assert ec["online"] is False and ec["experiment"] == e
