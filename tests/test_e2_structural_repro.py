"""E2 structural evaluation on synthetic DDL (parser, micro-F1, nGED, composite keys)."""
import pytest

from _synthetic import build_data_root, corpus, load_script, write_e2_preds
from src import datasets_io as dio
from src.evaluator import aggregate_schemas, empty_prediction_against_gold, evaluate_schema_pair
from src.metrics import ELEMENTS, micro_f1
from src.schema_parser import metadata_from_ddl, parse_ddl_fks, parse_ddl_primary_unique

S = corpus()["schemas"]
COMPOSITE = S[1]["ddl"]


def _eval(gold_ddl, pred_ddl):
    return evaluate_schema_pair(metadata_from_ddl(gold_ddl), gold_ddl, {}, pred_ddl)


def test_parser_tables_and_columns():
    meta = metadata_from_ddl(S[0]["ddl"])
    assert meta["tables"] == ["author", "book"]
    assert [c["COLUMN_NAME"] for c in meta["columns_by_table"]["book"]] == ["book_id", "title", "author_id"]


def test_composite_primary_and_foreign_keys_are_parsed():
    pk, uq = parse_ddl_primary_unique(COMPOSITE)
    assert ("order_line", ["order_id", "line_no"]) in pk
    assert ("shipment_item", ["shipment_id", "order_id", "line_no"]) in pk and uq == []
    fks, _ = parse_ddl_fks(COMPOSITE)
    assert fks == [("shipment_item", ["order_id", "line_no"], "order_line", ["order_id", "line_no"])]


def test_identical_schema_is_perfect():
    r = _eval(COMPOSITE, COMPOSITE)
    assert r["normalized_graph_edit_distance"] == 0.0 and r["exact_match"]
    for e in ELEMENTS:
        assert r[e]["matched"] == r[e]["gold"] == r[e]["recreated"]
    assert (r["entity"]["gold"], r["referential"]["gold"]) == (2, 1)


def test_composite_fk_must_match_all_columns():
    broken = COMPOSITE.replace("FOREIGN KEY (`order_id`, `line_no`)", "FOREIGN KEY (`order_id`)").replace(
        "(`order_id`, `line_no`)\n) ENGINE=InnoDB;", "(`order_id`)\n) ENGINE=InnoDB;")
    r = _eval(COMPOSITE, broken)
    assert r["referential"] == {"gold": 1, "recreated": 1, "matched": 0}


def test_partial_composite_pk_does_not_match():
    pred = COMPOSITE.replace("PRIMARY KEY (`order_id`, `line_no`)", "PRIMARY KEY (`order_id`)")
    r = _eval(COMPOSITE, pred)
    assert r["entity"]["gold"] == 2 and r["entity"]["matched"] == 1  # only shipment_item's key still matches


def test_empty_prediction_counts_and_ngde_one():
    meta = metadata_from_ddl(COMPOSITE)
    e = empty_prediction_against_gold(meta, COMPOSITE, failure_reason="boom")
    assert e["normalized_graph_edit_distance"] == 1.0 and e["failed"] and e["failure_reason"] == "boom"
    for el in ELEMENTS:
        assert e[el]["recreated"] == 0 and e[el]["matched"] == 0
    assert e["tables"]["gold"] == 2 and e["attributes"]["gold"] == 6 and e["entity"]["gold"] == 2
    assert e["referential"]["gold"] == 1


def test_micro_f1_aggregation_with_failure_hand_computed():
    ok = _eval(S[0]["ddl"], S[0]["ddl"])
    failed = empty_prediction_against_gold(metadata_from_ddl(S[2]["ddl"]), S[2]["ddl"])
    agg = aggregate_schemas([ok, failed])
    t = agg["five_elements"]["tables"]
    # gold 2 + 2, recreated 2 + 0, matched 2 + 0  -> P = 1, R = 0.5, F1 = 2/3
    assert (t["gold"], t["recreated"], t["matched"]) == (4, 2, 2)
    assert t["f1"] == pytest.approx(2 / 3) == pytest.approx(micro_f1(4, 2, 2))
    assert agg["mean_normalized_graph_edit_distance"] == pytest.approx(0.5)
    assert agg["failed_count"] == 1 and agg["total_schemas"] == 2


def test_missing_table_lowers_f1_and_nged():
    pred = S[0]["ddl"].split("CREATE TABLE `book`")[0]
    r = _eval(S[0]["ddl"], pred)
    assert r["tables"] == {"gold": 2, "recreated": 1, "matched": 1}
    assert 0.0 < r["normalized_graph_edit_distance"] < 1.0 and r["referential"]["recreated"] == 0


def test_e2_evaluate_combo_policies(tmp_path):
    ev = load_script("experiments/E2/evaluate.py", "e2_evaluate")
    root = build_data_root(tmp_path)
    gold = dio.load_rschema_381(root, strict=False)  # serials 0001, 0003, 0004
    write_e2_preds(tmp_path / "pred", gold, {"0001": S[0]["ddl"], "0004": ""}, errors={"0004": "parse"})
    kw = dict(data_root=str(root), strict=False)
    m, rows = ev.evaluate_combo("rschema", "llama31", "detailed", tmp_path / "pred", fail_policy="score", **kw)
    assert (m["n_gold"], m["n_scored"], m["n_failed"]) == (3, 3, 2)
    assert m["gold_source"].startswith("annotation_ddl")
    by_serial = {r["serial"]: r for r in rows}
    assert by_serial["0001"]["nged"] == 0.0
    assert by_serial["0003"]["status"] == "scored_failure" and by_serial["0003"]["nged"] == 1.0
    assert by_serial["0004"]["status"] == "scored_failure" and by_serial["0004"]["failure_reason"] == "error_field"
    assert by_serial["0003"]["tables_gold"] == 2 and by_serial["0003"]["tables_recreated"] == 0
    assert m["metrics"]["mean_nged"] == pytest.approx(2 / 3)
    assert set(m["metrics"]["micro_f1"]) == set(ELEMENTS)
    # gold tables: 2 (ok) + 2 + 2 (failed); matched only from the good one -> recall 1/3, precision 1
    assert m["metrics"]["micro_f1"]["tables"] == pytest.approx(micro_f1(6, 2, 2))
    ms, rows = ev.evaluate_combo("rschema", "llama31", "detailed", tmp_path / "pred", fail_policy="skip", **kw)
    assert (ms["n_scored"], ms["n_failed"]) == (1, 2) and ms["metrics"]["mean_nged"] == 0.0
    assert [r["status"] for r in rows] == ["ok", "skipped", "skipped"]
