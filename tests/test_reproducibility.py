"""Offline reproduction checks (no API, no GPU).

These tests assert the *honest* status of selected cells:

* E0 DeepSeek (RSchema): tables / attributes / entity / referential F1 and mean nGED match Table V
  within 0.0005; Domain F1 does NOT (0.2149 vs 0.214) so the row as a whole is MISMATCH.
* E0 CodeLlama (RSchema): Entity F1 MISMATCH (archived 0.278 vs paper 0.301).
* Claude / GPT rows are BLOCKED.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

import reproduce_tables as rt

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(
    not (rt.ARCHIVED / "e0_rschema_exp4_evaluation.json").is_file(),
    reason="archived Exp4 metrics not available",
)


@pytest.fixture(scope="module")
def refs():
    return rt.load_refs()


@pytest.fixture(scope="module")
def e0(refs):
    return rt.run_e0(refs)


def cells(res, label, dataset, model, **kw):
    out = [c for c in res.cells if c.table_label == label and c.dataset == dataset and c.model == model]
    for k, v in kw.items():
        out = [c for c in out if getattr(c, k) == v]
    return {c.metric: c for c in out}


def test_reference_values_complete_and_exact(refs):
    t5 = refs["tab:e0_overall"]["datasets"]
    assert t5["RSchema"]["codellama13b"]["entity"] == 0.301
    assert t5["RSchema"]["deepseek"]["nged"] == 0.733
    assert t5["SchemaBench"]["claude_sonnet_4_6"]["nged"] == 0.685
    assert set(t5["RSchema"]) == set(rt.ALL_MODELS)
    t7 = refs["tab:e1_s2t"]["datasets"]
    assert t7["RSchema"]["gpt_5_4_mini"]["bleu4_basic"] == 32.06
    assert t7["Enterprise-145"]["claude_sonnet_4_6"]["scr_detailed"] == 0.882
    assert t7["Enterprise-145"]["codellama13b"]["bleu4_basic"] is None  # 'n/a' in the paper
    t8 = refs["tab:e2_roundtrip"]["datasets"]
    assert t8["RSchema"]["deepseek"]["nged_basic"] == 0.584
    assert t8["SchemaBench"]["gpt_5_4_mini"]["nged_detailed"] == 0.2
    assert set(t8) == {"RSchema", "SchemaBench", "Enterprise-145"}
    assert refs["e0_rschema_exp4_micro"]["models"]["codellama13b"]["entity"] == 0.278
    assert refs["e0_schemabench_fewshot_corrected"]["models"]["codellama13b"]["tables"] == 0.373


def test_reference_json_matches_source_text(refs):
    """The committed JSON equals a fresh parse of the comparison text (no hand-typed numbers)."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_paper_reference_values as b

    fresh = b.build()
    for key in ("tab:e0_overall", "tab:e1_s2t", "tab:e2_roundtrip", "e0_rschema_exp4_micro",
                "e0_schemabench_fewshot_corrected"):
        assert fresh[key] == refs[key], key


def test_e0_deepseek_matches_paper_except_domain(e0):
    c = cells(e0, "tab:e0_overall", "RSchema", "deepseek")
    for m in ("nged", "tables", "attributes", "entity", "referential"):
        assert c[m].status == rt.PASS, (m, c[m])
        assert abs(c[m].delta) <= rt.TOL3 + 1e-9
    assert c["domain"].status == rt.MISMATCH  # 0.2149 vs 0.214 (honest)
    assert c["halluc"].status == rt.BLOCKED


def test_e0_codellama_entity_mismatch(e0):
    c = cells(e0, "tab:e0_overall", "RSchema", "codellama13b")
    ent = c["entity"]
    assert ent.status == rt.MISMATCH
    assert ent.paper == 0.301 and ent.reproduced == pytest.approx(0.2781, abs=1e-4)
    assert c["tables"].status == rt.PASS and c["referential"].status == rt.PASS


def test_e0_archived_exp4_micro_is_self_consistent(e0):
    lab = {(l.table_label, l.dataset): l for l in e0.labels}
    assert lab[("e0_rschema_exp4_micro", "RSchema")].status == rt.PASS
    assert lab[("e0_schemabench_fewshot_corrected", "SchemaBench")].status == rt.PASS


def test_e0_labels_and_closed_models_blocked(e0):
    lab = {(l.table_label, l.dataset): l for l in e0.labels}
    assert lab[("tab:e0_overall", "RSchema")].status == rt.MISMATCH
    assert lab[("tab:e0_overall", "SchemaBench")].status == rt.MISMATCH
    for ds in ("RSchema", "SchemaBench"):
        for model in rt.CLOSED_MODELS:
            c = cells(e0, "tab:e0_overall", ds, model)
            assert c and all(x.status == rt.BLOCKED and x.reproduced is None for x in c.values())


def test_tolerance_boundaries():
    assert rt.compare(0.554, 0.5539, rt.TOL3)[0] == rt.PASS
    assert rt.compare(0.554, 0.5545, rt.TOL3)[0] == rt.PASS  # exactly on the boundary
    assert rt.compare(0.554, 0.5546, rt.TOL3)[0] == rt.MISMATCH
    assert rt.compare(16.35, 16.3455, rt.TOL2)[0] == rt.PASS


def test_cli_all_offline_writes_csv_and_prints_statuses(tmp_path):
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "reproduce_tables.py"), "--all", "--offline", "--out-dir", str(tmp_path)],
        capture_output=True, text=True, cwd=ROOT, timeout=300,
    )
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout
    for tag in ("[MISMATCH]", "[BLOCKED ]", "[PARTIAL ]", "[PASS    ]"):
        assert tag in out
    assert "tab:e0_overall / RSchema" in out and "tab:e2_roundtrip / SchemaBench" in out
    for exp in ("E0", "E1", "E2", "E3", "E4", "E5"):
        assert (tmp_path / f"{exp}_cells.csv").exists() and (tmp_path / f"{exp}_summary.csv").exists()
    assert (tmp_path / "summary_all.csv").read_text().count("\n") > 10


def test_cli_single_experiment(tmp_path):
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "reproduce_tables.py"), "--experiment", "E1", "--out-dir", str(tmp_path)],
        capture_output=True, text=True, cwd=ROOT, timeout=120,
    )
    assert proc.returncode == 0 and "tab:e1_s2t / RSchema" in proc.stdout
    assert not (tmp_path / "E0_cells.csv").exists()
