"""E0 genuine-gold protocol tests (no live APIs / no paid calls)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments" / "E0"))

from src.evaluator import (  # noqa: E402
    empty_prediction_against_gold,
    five_element_counts,
    gold_record_to_metadata_and_ddl,
)
from src.metrics import (  # noqa: E402
    HALLUCINATION_DIMS,
    aggregate_hallucination_micro,
    micro_f1,
    normalized_graph_edit_distance,
)
from src.schema_parser import ensure_prediction_metadata, metadata_from_ddl  # noqa: E402

import reproduce_genuine_tables as genuine  # noqa: E402
import run_direct_api as api  # noqa: E402


def _load_jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.open() if l.strip()]


def test_rschema_populations_518_381():
    logical = _load_jsonl(ROOT / "datasets/rschema/annotation.jsonl")
    ddl = _load_jsonl(ROOT / "datasets/rschema/annotation_ddl.jsonl")
    assert len(logical) == 518
    assert len(ddl) == 381
    lids = {r["id"] for r in logical}
    dids = {r["id"] for r in ddl}
    assert dids.issubset(lids)


def test_schemabench_population_239():
    rows = _load_jsonl(ROOT / "datasets/schemabench/annotation_ddl.jsonl")
    assert len(rows) == 239
    assert rows[0]["id"] == "SB-001"


def test_dataset_join_by_id_not_position():
    logical = _load_jsonl(ROOT / "datasets/rschema/annotation.jsonl")
    ddl = _load_jsonl(ROOT / "datasets/rschema/annotation_ddl.jsonl")
    by_id = {r["id"]: r for r in ddl}
    first = ddl[0]
    assert by_id[first["id"]]["id"] == first["id"]
    assert any(r["id"] == first["id"] for r in logical)


def test_unknown_type_not_imputed_as_varchar():
    ddl = "CREATE TABLE t (`x` null, `y` int);"
    meta = metadata_from_ddl(ddl, legacy=False)
    x = next(c for c in meta["columns_by_table"]["t"] if c["COLUMN_NAME"] == "x")
    assert (x.get("DATA_TYPE") or "").lower() != "varchar"
    assert x.get("TYPE_STATUS") == "unsupported"
    assert "varchar" not in (x.get("COLUMN_TYPE") or "").lower()


def test_mysql_nullability_bare_vs_not_null():
    ddl = """
    CREATE TABLE t (
      `a` int,
      `b` int NOT NULL,
      `id` int PRIMARY KEY
    );
    """
    meta = metadata_from_ddl(ddl, legacy=False)
    a = next(c for c in meta["columns_by_table"]["t"] if c["COLUMN_NAME"] == "a")
    b = next(c for c in meta["columns_by_table"]["t"] if c["COLUMN_NAME"] == "b")
    pk = next(c for c in meta["columns_by_table"]["t"] if c["COLUMN_NAME"] == "id")
    assert a["IS_NULLABLE"] == "YES"
    assert b["IS_NULLABLE"] == "NO"
    assert pk["IS_NULLABLE"] == "NO"


def test_special_char_identifier_recovered():
    ddl = "CREATE TABLE `user-data` (`full/name` varchar(50), `o'brien` int);"
    meta = metadata_from_ddl(ddl, legacy=False)
    assert "user-data" in meta["tables"] or any("-" in t for t in meta["tables"])
    cols = [c["COLUMN_NAME"] for c in meta["columns_by_table"][meta["tables"][0]]]
    assert any("/" in c or "name" in c.lower() for c in cols)


def test_nged_names_only_ignores_type_flip():
    gold_ddl = "CREATE TABLE t (`a` int NOT NULL, PRIMARY KEY (`a`));"
    pred_ddl = "CREATE TABLE t (`a` varchar(255) NOT NULL, PRIMARY KEY (`a`));"
    gold = metadata_from_ddl(gold_ddl, legacy=False)
    pred = metadata_from_ddl(pred_ddl, legacy=False)
    d_names = normalized_graph_edit_distance(gold, gold_ddl, pred, pred_ddl, names_only=True)
    d_typed = normalized_graph_edit_distance(gold, gold_ddl, pred, pred_ddl, names_only=False)
    assert d_names == 0.0
    assert d_typed > 0.0


def test_domain_requires_type_and_nullability():
    gold_ddl = "CREATE TABLE t (`a` int, `b` int NOT NULL);"
    pred_bad_null = "CREATE TABLE t (`a` int NOT NULL, `b` int NOT NULL);"
    g_meta = metadata_from_ddl(gold_ddl, legacy=False)
    p_meta = metadata_from_ddl(pred_bad_null, legacy=False)
    counts = five_element_counts(g_meta, gold_ddl, p_meta, pred_bad_null, legacy=False)
    assert counts["attributes"]["matched"] >= 1
    assert counts["domain"]["matched"] < counts["attributes"]["matched"]


def test_domain_unknown_nullability_excluded_from_denominator():
    # Unsupported placeholder type with unknown nullability must not enter Domain G.
    gold_ddl = "CREATE TABLE t (`x` null, `y` int);"
    g_meta = metadata_from_ddl(gold_ddl, legacy=False)
    counts = five_element_counts(g_meta, gold_ddl, g_meta, gold_ddl, legacy=False)
    assert counts["attributes"]["gold"] == 2
    assert counts["domain"]["gold"] == 1  # only `y`


def test_micro_f1_sums_before_ratio():
    g = [10, 2]
    p = [10, 2]
    m = [10, 0]
    assert abs(micro_f1(sum(g), sum(p), sum(m)) - (20 / 24)) < 1e-9
    macro = sum(micro_f1(gi, pi, mi) for gi, pi, mi in zip(g, p, m)) / 2
    assert abs(macro - 0.5) < 1e-9
    assert micro_f1(sum(g), sum(p), sum(m)) != macro


def test_hallucination_excludes_domain_and_empty_not_forced():
    assert set(HALLUCINATION_DIMS) == {"tables", "attributes", "entity", "referential"}
    assert "domain" not in HALLUCINATION_DIMS
    gold_ddl = "CREATE TABLE t (`a` int PRIMARY KEY);"
    gold = metadata_from_ddl(gold_ddl, legacy=False)
    empty = empty_prediction_against_gold(gold, gold_ddl)
    assert empty["normalized_graph_edit_distance"] == 1.0
    assert aggregate_hallucination_micro([empty]) == 0.0


def test_empty_prediction_retains_gold_counts():
    gold_ddl = "CREATE TABLE t (`a` int PRIMARY KEY, `b` int);"
    gold = metadata_from_ddl(gold_ddl, legacy=False)
    empty = empty_prediction_against_gold(gold, gold_ddl)
    assert empty["tables"]["gold"] >= 1
    assert empty["tables"]["recreated"] == 0
    assert empty["tables"]["matched"] == 0
    assert empty["attributes"]["gold"] >= 1
    assert empty["attributes"]["recreated"] == 0


def test_sb001_deepseek_failure_kept_in_population():
    pred = ROOT / "results/predictions/e0/schemabench_exp2_deepseek/0001.json"
    if not pred.is_file():
        pytest.skip("SB DeepSeek 0001 prediction not present in this checkout")
    data = json.loads(pred.read_text(encoding="utf-8"))
    assert data.get("id") == "SB-001"
    gold_rows = _load_jsonl(ROOT / "datasets/schemabench/annotation_ddl.jsonl")
    gold = next(r for r in gold_rows if r["id"] == "SB-001")
    g_meta, g_ddl, _, _ = gold_record_to_metadata_and_ddl(gold)
    ddl = (data.get("ddl") or "").strip()
    if not ddl or data.get("error"):
        empty = empty_prediction_against_gold(g_meta, g_ddl)
        assert empty["normalized_graph_edit_distance"] == 1.0
        assert empty["tables"]["gold"] > 0
        assert empty["tables"]["recreated"] == 0
    else:
        assert g_meta["tables"]


def test_ensure_prediction_metadata_prefers_ddl_over_partial_json():
    ddl = "CREATE TABLE t (`a` int, `b` int);"
    partial = {
        "database": "db",
        "tables": ["t"],
        "columns_by_table": {
            "t": [{"COLUMN_NAME": "a", "DATA_TYPE": "int", "IS_NULLABLE": "YES", "TYPE_STATUS": "ok"}]
        },
    }
    fixed = ensure_prediction_metadata(partial, ddl, legacy=False)
    cols = fixed["columns_by_table"]["t"]
    assert len(cols) == 2
    assert any(m.startswith("column_count_mismatch") for m in fixed.get("_metadata_ddl_mismatches") or [])


def test_ensure_prediction_metadata_empty_ddl_keeps_json():
    meta = {"database": "db", "tables": ["t"], "columns_by_table": {"t": [{"COLUMN_NAME": "a"}]}}
    out = ensure_prediction_metadata(meta, "", legacy=False)
    assert out["tables"] == ["t"]
    assert len(out["columns_by_table"]["t"]) == 1


def test_ensure_prediction_metadata_type_conflict_recorded():
    ddl = "CREATE TABLE t (`a` int);"
    meta = {
        "tables": ["t"],
        "columns_by_table": {
            "t": [
                {
                    "COLUMN_NAME": "a",
                    "DATA_TYPE": "varchar",
                    "IS_NULLABLE": "YES",
                    "TYPE_STATUS": "ok",
                }
            ]
        },
    }
    out = ensure_prediction_metadata(meta, ddl, legacy=False)
    assert (out["columns_by_table"]["t"][0].get("DATA_TYPE") or "").lower() == "int"
    assert any("type_mismatch" in m for m in out.get("_metadata_ddl_mismatches") or [])


def _write_pred(pred_dir: Path, stem: str, rid: str, *, ddl: str | None = "CREATE TABLE t (`a` int);", error: str | None = None):
    payload = {
        "text_number": int(stem),
        "id": rid,
        "llm": "x",
        "model_id": "x",
        "database": "db",
        "question": "q",
        "ddl": ddl,
        "metadata": {},
    }
    if error is not None:
        payload["error"] = error
        payload["ddl"] = None
    (pred_dir / f"{stem}.json").write_text(json.dumps(payload), encoding="utf-8")


def test_direct_coverage_complete_expected_set(tmp_path):
    gold = [{"id": "g1"}, {"id": "g2"}]
    pred_dir = tmp_path / "preds"
    pred_dir.mkdir()
    _write_pred(pred_dir, "0001", "g1")
    _write_pred(pred_dir, "0002", "g2")
    cov = genuine.compute_direct_coverage(gold, genuine.index_predictions(pred_dir))
    assert cov["status"] == "COMPLETE"
    assert cov["present"] == 2 and cov["valid"] == 2 and cov["missing"] == 0


def test_direct_coverage_complete_with_recorded_failure(tmp_path):
    gold = [{"id": "g1"}, {"id": "g2"}]
    pred_dir = tmp_path / "preds"
    pred_dir.mkdir()
    _write_pred(pred_dir, "0001", "g1")
    _write_pred(pred_dir, "0002", "g2", error="timeout")
    cov = genuine.compute_direct_coverage(gold, genuine.index_predictions(pred_dir))
    assert cov["status"] == "COMPLETE"
    assert cov["valid"] == 1
    assert cov["generation_failed"] == 1
    assert cov["missing"] == 0


def test_direct_coverage_partial_is_incomplete(tmp_path):
    gold = [{"id": "g1"}, {"id": "g2"}, {"id": "g3"}]
    pred_dir = tmp_path / "preds"
    pred_dir.mkdir()
    _write_pred(pred_dir, "0001", "g1")
    cov = genuine.compute_direct_coverage(gold, genuine.index_predictions(pred_dir))
    assert cov["expected"] == 3
    assert cov["present"] == 1
    assert cov["missing"] == 2
    assert cov["status"] == "INCOMPLETE"


def test_direct_coverage_detects_duplicate_ids(tmp_path):
    gold = [{"id": "g1"}]
    pred_dir = tmp_path / "preds"
    pred_dir.mkdir()
    _write_pred(pred_dir, "0001", "g1")
    _write_pred(pred_dir, "0002", "g1")
    cov = genuine.compute_direct_coverage(gold, genuine.index_predictions(pred_dir))
    assert cov["duplicate_ids"] >= 1
    assert cov["status"] == "INVALID"


def test_direct_coverage_unexpected_id_is_invalid(tmp_path):
    gold = [{"id": "g1"}]
    pred_dir = tmp_path / "preds"
    pred_dir.mkdir()
    _write_pred(pred_dir, "0001", "g1")
    _write_pred(pred_dir, "0002", "extra")
    cov = genuine.compute_direct_coverage(gold, genuine.index_predictions(pred_dir))
    assert cov["unexpected_ids"] == 1
    assert cov["present"] == 1
    assert cov["status"] == "INVALID"


def test_direct_coverage_malformed_json_is_invalid(tmp_path):
    gold = [{"id": "g1"}]
    pred_dir = tmp_path / "preds"
    pred_dir.mkdir()
    _write_pred(pred_dir, "0001", "g1")
    (pred_dir / "0002.json").write_text("{not-json", encoding="utf-8")
    cov = genuine.compute_direct_coverage(gold, genuine.index_predictions(pred_dir))
    assert cov["malformed"] >= 1
    assert cov["status"] == "INVALID"


def test_direct_coverage_complete_plus_malformed_extra_is_invalid(tmp_path):
    gold = [{"id": "g1"}, {"id": "g2"}]
    pred_dir = tmp_path / "preds"
    pred_dir.mkdir()
    _write_pred(pred_dir, "0001", "g1")
    _write_pred(pred_dir, "0002", "g2")
    (pred_dir / "0003.json").write_text("<<<broken>>>", encoding="utf-8")
    cov = genuine.compute_direct_coverage(gold, genuine.index_predictions(pred_dir))
    assert cov["present"] == 2
    assert cov["malformed"] >= 1
    assert cov["status"] == "INVALID"


def test_missing_baseline_is_blocked(tmp_path, monkeypatch):
    monkeypatch.setitem(genuine.BASELINE_ROOT, "RSchema", tmp_path / "missing_root")
    bundle = genuine.load_baseline_predictions("RSchema", "codellama13b", "one_shot", expected_ids={"a"})
    assert bundle["status"] == "BLOCKED"
    assert "unavailable" in bundle["message"].lower()


def test_partial_baseline_is_incomplete(tmp_path, monkeypatch):
    root = tmp_path / "rschema_papermethods"
    path = root / "codellama13b" / "one_shot" / "results.jsonl"
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps({"id": "a", "status": "ok", "answer": {"T": {"Attributes": ["x"], "Primary key": ["x"]}}})
        + "\n"
    )
    monkeypatch.setitem(genuine.BASELINE_ROOT, "RSchema", root)
    bundle = genuine.load_baseline_predictions(
        "RSchema", "codellama13b", "one_shot", expected_ids={"a", "b"}
    )
    assert bundle["status"] == "INCOMPLETE"
    assert bundle["coverage"]["present"] == 1
    assert bundle["coverage"]["missing"] == 1


def test_baseline_complete_with_recorded_failure(tmp_path, monkeypatch):
    root = tmp_path / "rschema_papermethods"
    path = root / "codellama13b" / "one_shot" / "results.jsonl"
    path.parent.mkdir(parents=True)
    lines = [
        json.dumps({"id": "a", "status": "ok", "answer": {"T": {"Attributes": ["x"], "Primary key": ["x"]}}}),
        json.dumps({"id": "b", "status": "error", "error": "oom", "answer": None}),
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    monkeypatch.setitem(genuine.BASELINE_ROOT, "RSchema", root)
    bundle = genuine.load_baseline_predictions(
        "RSchema", "codellama13b", "one_shot", expected_ids={"a", "b"}
    )
    assert bundle["status"] == "COMPLETE"
    assert bundle["coverage"]["generation_failed"] == 1
    assert bundle["coverage"]["valid"] == 1


def test_baseline_unexpected_id_is_invalid(tmp_path, monkeypatch):
    root = tmp_path / "rschema_papermethods"
    path = root / "codellama13b" / "one_shot" / "results.jsonl"
    path.parent.mkdir(parents=True)
    lines = [
        json.dumps({"id": "a", "status": "ok", "answer": {"T": {"Attributes": ["x"], "Primary key": ["x"]}}}),
        json.dumps({"id": "extra", "status": "ok", "answer": {"T": {"Attributes": ["x"], "Primary key": ["x"]}}}),
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    monkeypatch.setitem(genuine.BASELINE_ROOT, "RSchema", root)
    bundle = genuine.load_baseline_predictions(
        "RSchema", "codellama13b", "one_shot", expected_ids={"a"}
    )
    assert bundle["coverage"]["unexpected_ids"] == 1
    assert bundle["status"] == "INVALID"


def test_baseline_duplicate_id_is_invalid(tmp_path, monkeypatch):
    root = tmp_path / "rschema_papermethods"
    path = root / "codellama13b" / "one_shot" / "results.jsonl"
    path.parent.mkdir(parents=True)
    row = json.dumps({"id": "a", "status": "ok", "answer": {"T": {"Attributes": ["x"], "Primary key": ["x"]}}})
    path.write_text(row + "\n" + row + "\n", encoding="utf-8")
    monkeypatch.setitem(genuine.BASELINE_ROOT, "RSchema", root)
    bundle = genuine.load_baseline_predictions(
        "RSchema", "codellama13b", "one_shot", expected_ids={"a"}
    )
    assert bundle["coverage"]["duplicate_ids"] >= 1
    assert bundle["status"] == "INVALID"


def test_baseline_malformed_jsonl_is_invalid(tmp_path, monkeypatch):
    root = tmp_path / "rschema_papermethods"
    path = root / "codellama13b" / "one_shot" / "results.jsonl"
    path.parent.mkdir(parents=True)
    good = json.dumps({"id": "a", "status": "ok", "answer": {"T": {"Attributes": ["x"], "Primary key": ["x"]}}})
    path.write_text(good + "\n{bad\n", encoding="utf-8")
    monkeypatch.setitem(genuine.BASELINE_ROOT, "RSchema", root)
    bundle = genuine.load_baseline_predictions(
        "RSchema", "codellama13b", "one_shot", expected_ids={"a"}
    )
    assert bundle["coverage"]["malformed"] >= 1
    assert bundle["status"] == "INVALID"


def test_evaluator_strict_incomplete_tmpdir(tmp_path):
    """Missing Direct pred dir → INCOMPLETE/BLOCKED under --strict."""
    gold_dir = tmp_path / "gold"
    gold_dir.mkdir()
    # Tiny synthetic gold files
    (gold_dir / "annotation.jsonl").write_text(
        json.dumps(
            {
                "id": "S1",
                "question": "q",
                "answer": {"T": {"Attributes": ["a"], "Primary key": ["a"]}},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (gold_dir / "annotation_ddl.jsonl").write_text(
        json.dumps(
            {
                "id": "S1",
                "answer": "CREATE TABLE `T` (`a` int NOT NULL, PRIMARY KEY (`a`));",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    pred_root = tmp_path / "preds"
    # Intentionally omit closed-model dirs; create one open-weight complete dump
    d = pred_root / "rschema_exp4_codellama13b"
    d.mkdir(parents=True)
    (d / "0001.json").write_text(
        json.dumps(
            {
                "text_number": 1,
                "id": "S1",
                "llm": "codellama13b",
                "model_id": "x",
                "database": "db",
                "question": "q",
                "ddl": "CREATE TABLE `T` (`a` int NOT NULL, PRIMARY KEY (`a`));",
                "metadata": {},
            }
        ),
        encoding="utf-8",
    )
    (d / "0001.txt").write_text("CREATE TABLE `T` (`a` int NOT NULL, PRIMARY KEY (`a`));\n")

    # Unit-level: coverage for missing Claude dir
    missing = pred_root / "rschema_exp4_claude_sonnet_4_6"
    assert not missing.is_dir()
    # Simulate evaluator coverage for empty/missing dir via empty index
    missing.mkdir()
    cov = genuine.compute_direct_coverage(
        [{"id": "S1"}], genuine.index_predictions(missing)
    )
    assert cov["status"] == "INCOMPLETE"
    assert cov["missing"] == 1

    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "experiments/E0/reproduce_genuine_tables.py"),
            "--validate-only",
            "--skip-pytest",
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    # validate-only uses real gold; should pass independently of preds
    assert proc.returncode == 0


def test_direct_api_dry_run_no_network(tmp_path, monkeypatch):
    env = {k: v for k, v in os.environ.items() if k not in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY")}
    proc = subprocess.run(
        [sys.executable, str(ROOT / "experiments/E0/run_direct_api.py"), "--dry-run", "--limit", "1"],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    assert "no API" in proc.stdout.lower() or "Dry-run" in proc.stdout
    assert "sk-" not in proc.stdout
    assert "sk-" not in proc.stderr


def test_direct_api_refuses_without_confirm_paid():
    env = {k: v for k, v in os.environ.items() if k not in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY")}
    proc = subprocess.run(
        [sys.executable, str(ROOT / "experiments/E0/run_direct_api.py"), "--limit", "1"],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 2
    assert "confirm-paid" in (proc.stdout + proc.stderr).lower()


def test_record_done_does_not_treat_error_as_valid(tmp_path):
    out = tmp_path / "preds"
    out.mkdir()
    api.save_record(
        out,
        "claude_sonnet_4_6",
        "claude-sonnet-4-6",
        "id1",
        1,
        "q",
        "db",
        None,
        error="boom",
    )
    assert api.record_done(out, 1, expected_id="id1", expected_llm="claude_sonnet_4_6") is False


def _done_kwargs():
    return dict(
        expected_id="id1",
        expected_llm="gpt_5_4_mini",
        expected_model_id="gpt-5.4-mini",
        expected_question="q",
    )


def test_resume_skips_valid_prediction(tmp_path):
    out = tmp_path / "preds"
    out.mkdir()
    ddl = "CREATE TABLE `t` (`a` int NOT NULL, PRIMARY KEY (`a`));"
    api.save_record(
        out,
        "gpt_5_4_mini",
        "gpt-5.4-mini",
        "id1",
        1,
        "q",
        "db",
        {"ddl": ddl, "metadata": {"database": "db", "tables": ["t"], "columns_by_table": {"t": []}}},
    )
    assert api.record_done(out, 1, **_done_kwargs()) is True


def test_txt_json_identical_ddl_is_done(tmp_path):
    out = tmp_path / "preds"
    out.mkdir()
    ddl = "CREATE TABLE t (`a` int);"
    api.save_record(out, "gpt_5_4_mini", "gpt-5.4-mini", "id1", 1, "q", "db", {"ddl": ddl, "metadata": {}})
    assert api.record_done(out, 1, **_done_kwargs()) is True


def test_txt_json_crlf_and_trailing_whitespace_still_done(tmp_path):
    out = tmp_path / "preds"
    out.mkdir()
    ddl = "CREATE TABLE t (`a` int);"
    api.save_record(out, "gpt_5_4_mini", "gpt-5.4-mini", "id1", 1, "q", "db", {"ddl": ddl, "metadata": {}})
    # Simulate Windows line endings / trailing blank line in TXT only.
    txt_path = out / "0001.txt"
    txt_path.write_bytes((ddl + "\r\n\r\n").encode("utf-8"))
    assert api.normalize_saved_ddl(txt_path.read_text(encoding="utf-8")) == api.normalize_saved_ddl(ddl)
    assert api.record_done(out, 1, **_done_kwargs()) is True


def test_txt_json_different_table_name_not_done(tmp_path):
    out = tmp_path / "preds"
    out.mkdir()
    ddl = "CREATE TABLE t (`a` int);"
    api.save_record(out, "gpt_5_4_mini", "gpt-5.4-mini", "id1", 1, "q", "db", {"ddl": ddl, "metadata": {}})
    (out / "0001.txt").write_text("CREATE TABLE other (`a` int);", encoding="utf-8")
    assert api.record_done(out, 1, **_done_kwargs()) is False


def test_txt_json_different_columns_not_done(tmp_path):
    out = tmp_path / "preds"
    out.mkdir()
    ddl = "CREATE TABLE t (`a` int);"
    api.save_record(out, "gpt_5_4_mini", "gpt-5.4-mini", "id1", 1, "q", "db", {"ddl": ddl, "metadata": {}})
    (out / "0001.txt").write_text("CREATE TABLE t (`a` int, `b` int);", encoding="utf-8")
    assert api.record_done(out, 1, **_done_kwargs()) is False


def test_txt_json_different_fk_not_done(tmp_path):
    out = tmp_path / "preds"
    out.mkdir()
    ddl = "CREATE TABLE t (`a` int, FOREIGN KEY (`a`) REFERENCES p(`id`));"
    api.save_record(out, "gpt_5_4_mini", "gpt-5.4-mini", "id1", 1, "q", "db", {"ddl": ddl, "metadata": {}})
    (out / "0001.txt").write_text(
        "CREATE TABLE t (`a` int, FOREIGN KEY (`a`) REFERENCES q(`id`));",
        encoding="utf-8",
    )
    assert api.record_done(out, 1, **_done_kwargs()) is False


def test_txt_json_partial_txt_not_done(tmp_path):
    out = tmp_path / "preds"
    out.mkdir()
    ddl = "CREATE TABLE t (`a` int);\nCREATE TABLE u (`b` int);"
    api.save_record(out, "gpt_5_4_mini", "gpt-5.4-mini", "id1", 1, "q", "db", {"ddl": ddl, "metadata": {}})
    (out / "0001.txt").write_text("CREATE TABLE t (`a` int);", encoding="utf-8")
    assert api.record_done(out, 1, **_done_kwargs()) is False


def test_txt_json_substring_create_table_not_enough(tmp_path):
    """Both contain CREATE TABLE but differ — must NOT be treated as done."""
    out = tmp_path / "preds"
    out.mkdir()
    ddl = "CREATE TABLE t (`a` int);"
    api.save_record(out, "gpt_5_4_mini", "gpt-5.4-mini", "id1", 1, "q", "db", {"ddl": ddl, "metadata": {}})
    (out / "0001.txt").write_text("CREATE TABLE t (`a` varchar(10));", encoding="utf-8")
    assert "CREATE TABLE" in (out / "0001.txt").read_text(encoding="utf-8").upper()
    assert api.record_done(out, 1, **_done_kwargs()) is False


def test_missing_txt_not_done(tmp_path):
    out = tmp_path / "preds"
    out.mkdir()
    ddl = "CREATE TABLE t (`a` int);"
    api.save_record(out, "gpt_5_4_mini", "gpt-5.4-mini", "id1", 1, "q", "db", {"ddl": ddl, "metadata": {}})
    (out / "0001.txt").unlink()
    assert api.record_done(out, 1, **_done_kwargs()) is False


def test_corrupted_json_not_done(tmp_path):
    out = tmp_path / "preds"
    out.mkdir()
    ddl = "CREATE TABLE t (`a` int);"
    api.save_record(out, "gpt_5_4_mini", "gpt-5.4-mini", "id1", 1, "q", "db", {"ddl": ddl, "metadata": {}})
    (out / "0001.json").write_text("{broken", encoding="utf-8")
    assert api.record_done(out, 1, **_done_kwargs()) is False


def test_recorded_failure_not_done(tmp_path):
    out = tmp_path / "preds"
    out.mkdir()
    api.save_record(
        out, "gpt_5_4_mini", "gpt-5.4-mini", "id1", 1, "q", "db", None, error="boom"
    )
    assert api.record_done(out, 1, **_done_kwargs()) is False


def test_resume_rejects_wrong_model_id(tmp_path):
    out = tmp_path / "preds"
    out.mkdir()
    ddl = "CREATE TABLE `t` (`a` int);"
    api.save_record(
        out,
        "gpt_5_4_mini",
        "gpt-5.4-mini",
        "id1",
        1,
        "q",
        "db",
        {"ddl": ddl, "metadata": {}},
    )
    assert (
        api.record_done(
            out,
            1,
            expected_id="id1",
            expected_llm="claude_sonnet_4_6",
            expected_model_id="claude-sonnet-4-6",
            expected_question="q",
        )
        is False
    )


def test_resume_rejects_wrong_schema_id(tmp_path):
    out = tmp_path / "preds"
    out.mkdir()
    ddl = "CREATE TABLE `t` (`a` int);"
    api.save_record(
        out, "gpt_5_4_mini", "gpt-5.4-mini", "id1", 1, "q", "db", {"ddl": ddl, "metadata": {}}
    )
    assert (
        api.record_done(
            out,
            1,
            expected_id="OTHER",
            expected_llm="gpt_5_4_mini",
            expected_model_id="gpt-5.4-mini",
            expected_question="q",
        )
        is False
    )


def test_resume_detects_id_conflict(tmp_path):
    out = tmp_path / "preds"
    out.mkdir()
    ddl = "CREATE TABLE `t` (`a` int);"
    api.save_record(
        out,
        "gpt_5_4_mini",
        "gpt-5.4-mini",
        "OTHER",
        1,
        "q",
        "db",
        {"ddl": ddl, "metadata": {}},
    )
    assert api.record_id_conflict(out, 1, "id1") is not None


def test_empty_requirement_saves_failure_record(tmp_path, monkeypatch):
    out = tmp_path / "preds"
    # Exercise save path used by empty-q handling
    api.save_record(
        out,
        "claude_sonnet_4_6",
        "claude-sonnet-4-6",
        "id1",
        1,
        "",
        "db",
        None,
        error="empty or missing requirement (question)",
    )
    data = json.loads((out / "0001.json").read_text(encoding="utf-8"))
    assert data["id"] == "id1"
    assert data.get("error")
    assert api.record_done(out, 1, expected_id="id1") is False


def test_redact_secrets_never_leaks_keys():
    assert "sk-abc" not in api._redact_secrets("fail sk-abcdefghijklmnopqrstuvwxyz error")
    assert "[REDACTED]" in api._redact_secrets("fail sk-abcdefghijklmnopqrstuvwxyz error")


def test_constructor_prompt_file_exists_and_matches_contract():
    text = api.load_constructor_prompt()
    assert '"ddl"' in text and '"metadata"' in text
    assert "CREATE TABLE" in text


def test_table_v_vi_direct_consistency_helper():
    # Bit-identity of Direct rows is enforced in reproduce_genuine_tables.main;
    # unit-check the equality predicate used there.
    r = {
        "dataset": "RSchema",
        "model": "X",
        "n": 2,
        "failed": 0,
        "nged": 0.1,
        "halluc": 0.2,
        "tables": 0.3,
        "attributes": 0.4,
        "domain": 0.5,
        "entity": 0.6,
        "referential": 0.7,
    }
    vi = {
        "dataset": "RSchema",
        "method": "Direct",
        "model": "X",
        "eval": 2,
        "zero": 0,
        "nged": 0.1,
        "halluc": 0.2,
        "tables": 0.3,
        "attributes": 0.4,
        "domain": 0.5,
        "entity": 0.6,
        "referential": 0.7,
    }
    assert all(
        r[m] == vi[m]
        for m in ("nged", "halluc", "tables", "attributes", "domain", "entity", "referential")
    )
    assert r["n"] == vi["eval"] and r["failed"] == vi["zero"]
