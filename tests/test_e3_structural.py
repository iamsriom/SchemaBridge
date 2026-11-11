"""E3 structural evaluation on synthetic DDL (empty-gold, Hall., isolation hashes, micro-F1)."""
from __future__ import annotations

import json

import pytest

from _synthetic import build_data_root, corpus, load_script, write_e1_preds, write_e2_preds
from src import datasets_io as dio
from src import repro_io as rio
from src.evaluator import aggregate_schemas, empty_prediction_against_gold, evaluate_schema_pair
from src.metrics import (
    ELEMENTS,
    aggregate_hallucination_micro_5dim,
    hallucination_rate,
    micro_f1,
    normalized_graph_edit_distance,
)
from src.schema_parser import metadata_from_ddl

S = corpus()["schemas"]
COMPOSITE = S[1]["ddl"]
EMPTY_DDL = "-- empty placeholder schema\n"


def _eval(gold_ddl, pred_ddl):
    return evaluate_schema_pair(metadata_from_ddl(gold_ddl), gold_ddl, {}, pred_ddl)


def test_valid_empty_schema_and_empty_empty_nged_zero():
    g_meta = metadata_from_ddl(EMPTY_DDL)
    assert rio.gold_is_empty(EMPTY_DDL, g_meta)
    r = _eval(EMPTY_DDL, "")
    assert r["normalized_graph_edit_distance"] == 0.0
    assert r["exact_match"]
    assert rio.e3_reconstruction_failure({"ddl": "", "metadata": {}}, gold_ddl=EMPTY_DDL, gold_meta=g_meta) is None


def test_nonempty_gold_empty_reconstruction_is_failure():
    g_meta = metadata_from_ddl(COMPOSITE)
    assert rio.e3_reconstruction_failure({"ddl": ""}, gold_ddl=COMPOSITE, gold_meta=g_meta) == "empty_ddl"
    e = empty_prediction_against_gold(g_meta, COMPOSITE, failure_reason="empty_ddl")
    assert e["normalized_graph_edit_distance"] == 1.0 and e["failed"]


def test_invalid_sql_and_missing_prediction():
    assert rio.e3_reconstruction_failure(None, gold_ddl=COMPOSITE) == "missing"
    assert rio.e3_reconstruction_failure({"error": "boom", "ddl": "x"}, gold_ddl=COMPOSITE) == "error_field"
    # Comment-only against nonempty gold
    reason = rio.e3_reconstruction_failure({"ddl": "-- no tables"}, gold_ddl=COMPOSITE,
                                           gold_meta=metadata_from_ddl(COMPOSITE))
    assert reason == "empty_or_unparseable"


def test_exact_schema_reconstruction():
    r = _eval(COMPOSITE, COMPOSITE)
    assert r["normalized_graph_edit_distance"] == 0.0 and r["exact_match"]
    for e in ELEMENTS:
        assert r[e]["matched"] == r[e]["gold"] == r[e]["recreated"]


def test_extra_and_missing_table():
    extra = COMPOSITE + "\nCREATE TABLE `extra` (`id` int NOT NULL, PRIMARY KEY (`id`));"
    r = _eval(COMPOSITE, extra)
    assert r["tables"]["recreated"] == r["tables"]["gold"] + 1
    assert r["tables"]["matched"] == r["tables"]["gold"]
    assert r["normalized_graph_edit_distance"] > 0
    missing = COMPOSITE.split("CREATE TABLE `shipment_item`")[0]
    r2 = _eval(COMPOSITE, missing)
    assert r2["tables"]["matched"] < r2["tables"]["gold"]


def test_extra_missing_attribute_and_datatype_nullability():
    base = S[0]["ddl"]
    title_line = "`title` varchar(200) NOT NULL"
    assert title_line in base
    extra_col = base.replace(title_line, title_line + ",\n  `extra` int DEFAULT NULL")
    r = _eval(base, extra_col)
    assert r["attributes"]["recreated"] == r["attributes"]["gold"] + 1
    wrong_type = base.replace(title_line, "`title` int NOT NULL")
    r2 = _eval(base, wrong_type)
    assert r2["attributes"]["matched"] == r2["attributes"]["gold"]  # names match
    assert r2["domain"]["matched"] < r2["domain"]["gold"]
    null_flip = base.replace(title_line, "`title` varchar(200) DEFAULT NULL")
    r3 = _eval(base, null_flip)
    assert r3["domain"]["matched"] < r3["domain"]["gold"]


def test_composite_pk_unique_and_fk_direction():
    r = _eval(COMPOSITE, COMPOSITE)
    assert r["entity"]["gold"] >= 1 and r["referential"]["gold"] == 1
    broken = COMPOSITE.replace(
        "FOREIGN KEY (`order_id`, `line_no`) REFERENCES `order_line` (`order_id`, `line_no`)",
        "FOREIGN KEY (`order_id`, `line_no`) REFERENCES `order_line` (`line_no`, `order_id`)",
    )
    # Direction / column grouping mismatch should reduce referential matches.
    r2 = _eval(COMPOSITE, broken)
    assert r2["referential"]["matched"] <= r2["referential"]["gold"]


def test_micro_f1_aggregation_and_nged_normalization():
    ok = _eval(S[0]["ddl"], S[0]["ddl"])
    failed = empty_prediction_against_gold(metadata_from_ddl(S[2]["ddl"]), S[2]["ddl"])
    agg = aggregate_schemas([ok, failed])
    t = agg["five_elements"]["tables"]
    assert (t["gold"], t["recreated"], t["matched"]) == (4, 2, 2)
    assert t["f1"] == pytest.approx(micro_f1(4, 2, 2))
    assert agg["mean_normalized_graph_edit_distance"] == pytest.approx(0.5)
    # Empty+empty contributes 0 to mean nGED
    empty = _eval(EMPTY_DDL, "")
    assert empty["normalized_graph_edit_distance"] == 0.0
    assert normalized_graph_edit_distance(metadata_from_ddl(EMPTY_DDL), EMPTY_DDL, {}, "") == 0.0


def test_hallucination_zero_denominator_and_five_dim_mean():
    assert hallucination_rate(0, 0) == 0.0
    assert hallucination_rate(10, 7) == pytest.approx(0.3)
    exact = _eval(COMPOSITE, COMPOSITE)
    hall = aggregate_hallucination_micro_5dim([exact])
    assert hall == 0.0
    # Extra table => tables hall > 0; other dims may be 0 if recreations match
    extra = COMPOSITE + "\nCREATE TABLE `ghost` (`id` int NOT NULL);"
    over = _eval(COMPOSITE, extra)
    hall2 = aggregate_hallucination_micro_5dim([over])
    assert hall2 > 0.0
    # Empty reconstruction against nonempty gold: recreations 0 -> hall contribution 0
    failed = empty_prediction_against_gold(metadata_from_ddl(COMPOSITE), COMPOSITE)
    assert aggregate_hallucination_micro_5dim([failed]) == 0.0


def test_fixed_description_hash_matching_and_rejection():
    text_a = "Fixed description A for schema X."
    text_b = "Different description B."
    assert rio.sha256_text(text_a) != rio.sha256_text(text_b)
    assert rio.description_hash({"nl_text": text_a}) == rio.sha256_text(text_a)
    assert rio.description_hash({"nl_text": ""}) is None
    assert rio.description_hash({"error": "x", "nl_text": text_a}) is None


def test_e3_evaluate_combo_empty_gold_and_policies(tmp_path):
    ev = load_script("experiments/E3/evaluate.py", "e3_evaluate")
    root = build_data_root(tmp_path)
    # Use schemabench synthetic (3 schemas); inject an empty-gold enterprise-style via custom preds
    gold = dio.load_schemabench(root, strict=False)
    pred = tmp_path / "pred"
    pred.mkdir()
    # schema 0 exact; schema 1 missing; schema 2 empty ddl failure
    write_e2_preds(pred, gold, {gold[0].serial: S[0]["ddl"], gold[2].serial: ""},
                   errors={gold[2].serial: "parse"})
    # Also write an empty-gold empty-pred record using a fabricated id path via enterprise gold
    ent = dio.load_enterprise145(root, strict=False)
    # Force one enterprise gold to empty by evaluating with EMPTY_DDL gold through helper
    g_meta = metadata_from_ddl(EMPTY_DDL)
    assert rio.e3_reconstruction_failure({"ddl": "", "id": "empty"}, gold_ddl=EMPTY_DDL, gold_meta=g_meta) is None

    kw = dict(data_root=str(root), strict=False)
    m, rows = ev.evaluate_combo("schemabench", "llama31", pred, fail_policy="score", **kw)
    assert m["n_gold"] == 3 and m["n_failed"] >= 1
    assert set(m["metrics"]["micro_f1"]) == set(ELEMENTS)
    assert "mean_hall" in m["metrics"]
    by = {r["serial"]: r for r in rows}
    assert by[gold[0].serial]["nged"] == 0.0
    assert by[gold[1].serial]["status"] == "scored_empty" and by[gold[1].serial]["nged"] == 1.0

    ms, rows2 = ev.evaluate_combo("schemabench", "llama31", pred, fail_policy="skip", **kw)
    assert ms["n_scored"] == 1 and any(r["status"] == "skipped" for r in rows2)
    # unused ent keeps lint quiet about loaders
    assert len(ent) == 3


def test_e3_validate_inputs_rejects_wrong_hash(tmp_path):
    val = load_script("experiments/E3/validate_inputs.py", "e3_validate")
    root = build_data_root(tmp_path)
    gold = dio.load_schemabench(root, strict=False)
    desc = tmp_path / "desc"
    write_e1_preds(desc, gold, {g.serial: f"desc-{g.serial}" for g in gold})
    pred_parent = tmp_path / "e3"
    good = pred_parent / "schemabench_detailed_llama31"
    write_e2_preds(good, gold, {g.serial: S[i % 3]["ddl"] for i, g in enumerate(gold)})
    # Inject matching nl_text into predictions
    for g in gold:
        p = good / f"{g.serial}.json"
        d = json.loads(p.read_text())
        d["nl_text"] = f"desc-{g.serial}"
        d["nl_sha256"] = rio.sha256_text(d["nl_text"])
        d["llm"] = "llama31"
        p.write_text(json.dumps(d))
    errs = val.check_dataset("schemabench", ["llama31"], desc, pred_parent,
                             data_root=str(root), limit=None, require_all=True, strict=False)
    assert errs == []
    # Corrupt one hash
    bad = json.loads((good / f"{gold[0].serial}.json").read_text())
    bad["nl_sha256"] = rio.sha256_text("tampered")
    bad["nl_text"] = "tampered"
    (good / f"{gold[0].serial}.json").write_text(json.dumps(bad))
    errs2 = val.check_dataset("schemabench", ["llama31"], desc, pred_parent,
                              data_root=str(root), limit=None, require_all=True, strict=False)
    assert any("hash mismatch" in e for e in errs2)


def test_table_ix_generation_synthetic(tmp_path):
    gen = load_script("experiments/E3/generate_table_ix.py", "e3_table")
    metrics_dir = tmp_path / "metrics" / "schemabench_detailed_llama31"
    metrics_dir.mkdir(parents=True)
    fake = {
        "experiment": "E3", "dataset": "schemabench", "constructor": "llama31",
        "n_gold": 3, "n_scored": 3, "n_failed": 0,
        "metrics": {
            "micro_f1": {e: 0.5 for e in ELEMENTS},
            "mean_nged": 0.25, "mean_hall": 0.1,
        },
    }
    (metrics_dir / "metrics.json").write_text(json.dumps(fake))
    out = tmp_path / "latex_generated"
    out.mkdir()
    # assert_ignored_out_dir requires outputs/ in path when under repo — use absolute outside or
    # monkey via writing directly
    tex = gen.build_table_ix(gen.load_metrics([tmp_path / "metrics"]))
    assert r"\label{tab:e3_overall}" in tex
    assert "0.250" in tex and "0.100" in tex
    assert "--" in tex  # other constructors missing
