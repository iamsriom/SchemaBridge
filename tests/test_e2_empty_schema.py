"""E2 empty-schema handling (synthetic only): valid empty vs incorrect empty vs failed reconstructions."""
import json

import pytest

from _synthetic import corpus, load_script
from src import repro_io as rio
from src.datasets_io import GoldRecord
from src.evaluator import evaluate_schema_pair
from src.schema_parser import metadata_from_ddl

GOOD = corpus()["schemas"][0]["ddl"]
EMPTY_META = {"database": "d", "tables": [], "columns_by_table": {}}
EMPTY_REPLY = json.dumps({"ddl": "", "metadata": EMPTY_META})


def _gold(serial: str, ddl: str) -> GoldRecord:
    return GoldRecord("schemabench", serial, f"G-{serial}", "q", ddl, "synthetic", f"s{serial}", "d")


def _entry(serial: str, ddl, **extra):
    d = {"text_number": int(serial), "id": f"G-{serial}", "llm": "gpt4omini", "model_id": "gpt-4o-mini",
         "nl_text": "x", "ddl": ddl, "metadata": {}}
    d.update(extra)
    return d


# --------------------------------------------------------------------------- predicates


def test_gold_is_empty():
    assert rio.gold_is_empty("") and rio.gold_is_empty("   \n") and rio.gold_is_empty("-- only a comment")
    assert not rio.gold_is_empty(GOOD)
    assert rio.gold_is_empty(GOOD, {"tables": [], "columns_by_table": {}})  # metadata wins when given
    assert not rio.gold_is_empty("", {"tables": ["t"], "columns_by_table": {"t": []}})


def test_pred_is_structurally_empty():
    for ddl in ("", "  ", "-- nothing to create", "/* nothing */", "-- a\n/* b */\n;", "SELECT 1;"):
        assert rio.pred_is_structurally_empty(ddl), ddl
    assert not rio.pred_is_structurally_empty(GOOD)
    assert not rio.pred_is_structurally_empty("", {"tables": ["t"], "columns_by_table": {}})
    assert rio.pred_is_structurally_empty("", EMPTY_META)


# --------------------------------------------------------------------------- ddl_outcome


@pytest.mark.parametrize("entry", [None, {"id": "G-1", "ddl": "", "error": "boom"}, {"id": "G-1", "ddl": "", "skipped": True},
                                   {"id": "G-1", "metadata": {}}, {"id": "G-1", "ddl": None}])
@pytest.mark.parametrize("gold_ddl", ["", GOOD])
def test_unsuccessful_records_are_failed_for_empty_and_nonempty_gold(entry, gold_ddl):
    status, reason = rio.ddl_outcome(entry, gold_ddl, schema_id="G-1")
    assert status == "failed" and reason


def test_failed_reasons():
    assert rio.ddl_outcome(None, "") == ("failed", "missing")
    assert rio.ddl_outcome({"id": "x", "ddl": "", "error": "e"}, "") == ("failed", "error_field")
    assert rio.ddl_outcome({"id": "x"}, "") == ("failed", "missing_ddl")
    assert rio.ddl_outcome({"id": "other", "ddl": ""}, "", schema_id="x") == ("failed", "id_mismatch")
    assert rio.ddl_outcome({"ddl": ""}, "", schema_id="x") == ("failed", "missing_id")  # no evidence of identity
    assert rio.ddl_outcome({"id": "x", "ddl": "I cannot answer"}, "", schema_id="x") == ("failed", "unparseable_ddl")


@pytest.mark.parametrize("ddl", ["", "   ", "-- empty schema", "/* nothing */"])
def test_valid_empty(ddl):
    assert rio.ddl_outcome(_entry("0001", ddl, metadata=EMPTY_META), "", schema_id="G-0001") == (
        "valid_empty", "empty_gold_empty_pred")
    assert rio.ddl_outcome({"id": "G-0001", "ddl": ddl}, "-- comment-only gold", schema_id="G-0001")[0] == "valid_empty"


def test_incorrect_empty_is_not_a_failure():
    assert rio.ddl_outcome(_entry("0001", ""), GOOD, schema_id="G-0001") == ("incorrect_empty", "empty_prediction")
    assert rio.ddl_outcome(_entry("0001", "-- nothing"), GOOD, schema_id="G-0001")[0] == "incorrect_empty"


def test_nonempty_prediction_is_ok_even_for_empty_gold():
    assert rio.ddl_outcome(_entry("0001", GOOD), GOOD, schema_id="G-0001") == ("ok", None)
    assert rio.ddl_outcome(_entry("0001", GOOD), "", schema_id="G-0001") == ("ok", None)


def test_legacy_ddl_failure_kept():
    assert rio.ddl_failure({"ddl": ""}) == "empty_ddl" and rio.ddl_failure(None) == "missing"
    assert rio.ddl_failure({"ddl": GOOD}) is None


# --------------------------------------------------------------------------- parse_constructor_response


def test_parse_constructor_response_accepts_explicit_empty_ddl():
    obj, why = rio.parse_constructor_response(EMPTY_REPLY)
    assert why is None and obj == {"ddl": "", "metadata": EMPTY_META}
    obj2, why2 = rio.parse_constructor_response("```json\n" + EMPTY_REPLY + "\n```", allow_empty_ddl=True)
    assert why2 is None and obj2["ddl"] == ""
    assert rio.parse_constructor_response(EMPTY_REPLY, allow_empty_ddl=False) == (None, "missing_ddl")


@pytest.mark.parametrize("text,reason", [
    ('{"ddl": ""}', "missing_ddl"),  # empty but no metadata object: indistinguishable from truncation
    ('{"metadata": {}}', "missing_ddl"), ('{"ddl": null, "metadata": {}}', "missing_ddl"),
    ("", "empty_response"), ("not json", "invalid_json"),
])
def test_parse_constructor_response_rejects_non_explicit_empty(text, reason):
    assert rio.parse_constructor_response(text) == (None, reason)


def test_parse_constructor_response_nonempty_unchanged():
    obj, why = rio.parse_constructor_response(json.dumps({"ddl": f"  {GOOD}\n", "metadata": {"tables": ["a"]}}))
    assert why is None and obj["ddl"] == GOOD and obj["metadata"] == {"tables": ["a"]}


# --------------------------------------------------------------------------- nGED


def test_nged_empty_vs_empty_is_zero_and_empty_vs_gold_is_natural():
    assert evaluate_schema_pair(metadata_from_ddl(""), "", {}, "")["normalized_graph_edit_distance"] == 0.0
    g = metadata_from_ddl(GOOD)
    assert evaluate_schema_pair(g, GOOD, {}, "")["normalized_graph_edit_distance"] == pytest.approx(1.0)
    half = GOOD.split("CREATE TABLE `book`")[0]
    assert 0.0 < evaluate_schema_pair(g, GOOD, {}, half)["normalized_graph_edit_distance"] < 1.0


# --------------------------------------------------------------------------- resume


def _write(path, obj):
    path.write_text(json.dumps(obj), encoding="utf-8")


def test_is_complete_ddl_record_resume(tmp_path):
    sid = "G-0001"
    p = tmp_path / "0001.json"
    assert not rio.is_complete_ddl_record(p, sid)  # missing file
    _write(p, _entry("0001", GOOD))
    assert rio.is_complete_ddl_record(p, sid)
    _write(p, _entry("0001", "", metadata=EMPTY_META))  # explicit valid empty reconstruction
    assert rio.is_complete_ddl_record(p, sid)
    _write(p, _entry("0001", "", error="constructor_parse_failed:missing_ddl"))  # error record: retried
    assert not rio.is_complete_ddl_record(p, sid)
    _write(p, _entry("0001", GOOD, error="boom"))
    assert not rio.is_complete_ddl_record(p, sid)
    _write(p, _entry("0001", GOOD, skipped=True))
    assert not rio.is_complete_ddl_record(p, sid)
    _write(p, _entry("0002", GOOD))  # id mismatch
    assert not rio.is_complete_ddl_record(p, sid)
    _write(p, {"id": sid, "metadata": {}})  # no ddl key
    assert not rio.is_complete_ddl_record(p, sid)
    _write(p, {"id": sid, "ddl": None})
    assert not rio.is_complete_ddl_record(p, sid)
    p.write_text("{not json", encoding="utf-8")
    assert not rio.is_complete_ddl_record(p, sid)
    p.write_text("[]", encoding="utf-8")
    assert not rio.is_complete_ddl_record(p, sid)


# --------------------------------------------------------------------------- evaluate_combo scenarios


@pytest.fixture()
def ev(monkeypatch):
    mod = load_script("experiments/E2/evaluate.py", "e2_evaluate_empty")
    return mod


def _run_combo(ev, monkeypatch, tmp_path, gold, preds, policy="score"):
    pred_dir = tmp_path / "pred"
    pred_dir.mkdir()
    for serial, obj in preds.items():
        if obj is not None:
            _write(pred_dir / f"{serial}.json", obj)
    monkeypatch.setattr(ev.dio, "load_dataset", lambda name, data_root=None, strict=True: gold)
    m, rows = ev.evaluate_combo("schemabench", "llama31", "basic", pred_dir, data_root=None, fail_policy=policy)
    return m, {r["serial"]: r for r in rows}


def test_case_a_empty_gold(ev, monkeypatch, tmp_path):
    """Gold is genuinely empty: only a successful empty record is valid (nGED 0); everything else failed (nGED 1)."""
    gold = [_gold(f"000{i}", "") for i in range(1, 5)]
    preds = {
        "0001": _entry("0001", "", metadata=EMPTY_META),           # valid empty
        "0002": _entry("0002", "-- empty", metadata=EMPTY_META),   # comment-only: valid empty
        "0003": _entry("0003", "", error="constructor_parse_failed:invalid_json"),  # error record
        # 0004: missing file
    }
    m, rows = _run_combo(ev, monkeypatch, tmp_path, gold, preds)
    assert [rows[s]["status"] for s in ("0001", "0002", "0003", "0004")] == [
        "valid_empty", "valid_empty", "scored_failure", "scored_failure"]
    assert rows["0001"]["nged"] == 0.0 and rows["0002"]["nged"] == 0.0
    assert rows["0003"]["nged"] == 1.0 and rows["0004"]["nged"] == 1.0
    assert rows["0004"]["failure_reason"] == "missing_prediction_file" and rows["0001"]["failure_reason"] == ""
    assert (m["n_scored"], m["n_failed"], m["n_valid_empty"], m["n_incorrect_empty"]) == (4, 2, 2, 0)
    assert m["metrics"]["mean_nged"] == pytest.approx(0.5)


def test_case_a_empty_gold_skip_policy_drops_only_failures(ev, monkeypatch, tmp_path):
    gold = [_gold("0001", ""), _gold("0002", "")]
    m, rows = _run_combo(ev, monkeypatch, tmp_path, gold, {"0001": _entry("0001", "", metadata=EMPTY_META)}, "skip")
    assert rows["0001"]["status"] == "valid_empty" and rows["0002"]["status"] == "skipped"
    assert (m["n_scored"], m["n_failed"]) == (1, 1) and m["metrics"]["mean_nged"] == 0.0


def test_case_b_nonempty_gold_empty_prediction_is_scored_naturally(ev, monkeypatch, tmp_path):
    gold = [_gold("0001", GOOD), _gold("0002", GOOD), _gold("0003", GOOD)]
    preds = {
        "0001": _entry("0001", "", metadata=EMPTY_META),            # successful but empty -> incorrect_empty
        "0002": _entry("0002", "", error="constructor_parse_failed:missing_ddl"),  # failed
        "0003": _entry("0003", GOOD),                               # ok, exact
    }
    m, rows = _run_combo(ev, monkeypatch, tmp_path, gold, preds)
    assert [rows[s]["status"] for s in ("0001", "0002", "0003")] == ["incorrect_empty", "scored_failure", "ok"]
    assert rows["0001"]["failure_reason"] == "empty_prediction"
    assert rows["0001"]["tables_gold"] == 2 and rows["0001"]["tables_recreated"] == 0
    assert rows["0001"]["nged"] == pytest.approx(1.0)  # natural value of empty-vs-gold (not a forced policy value)
    assert rows["0002"]["nged"] == 1.0 and rows["0003"]["nged"] == 0.0
    assert (m["n_failed"], m["n_incorrect_empty"], m["n_valid_empty"]) == (1, 1, 0)


def test_case_c_empty_gold_nonempty_prediction_is_ok_and_hallucinates(ev, monkeypatch, tmp_path):
    gold = [_gold("0001", "")]
    m, rows = _run_combo(ev, monkeypatch, tmp_path, gold, {"0001": _entry("0001", GOOD)})
    assert rows["0001"]["status"] == "ok" and rows["0001"]["tables_gold"] == 0 and rows["0001"]["tables_recreated"] == 2
    assert rows["0001"]["nged"] > 0.0 and m["n_failed"] == 0


def test_id_mismatch_is_failed_not_valid_empty(ev, monkeypatch, tmp_path):
    gold = [_gold("0001", "")]
    m, rows = _run_combo(ev, monkeypatch, tmp_path, gold, {"0001": _entry("0001", "", id="SOMEONE-ELSE")})
    assert rows["0001"]["status"] == "scored_failure" and rows["0001"]["nged"] == 1.0
    assert m["n_valid_empty"] == 0
