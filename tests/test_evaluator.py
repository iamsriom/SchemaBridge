"""Pair evaluation + (optional) agreement with archived Exp4 per-schema counts."""
import json
from pathlib import Path

import pytest

from src.evaluator import (
    aggregate_schemas,
    evaluate_ddl_pair,
    evaluate_predictions_dir,
    gold_answer_to_metadata_and_ddl,
)

ROOT = Path(__file__).resolve().parents[1]
GOLD = ROOT / "datasets" / "rschema" / "annotation.jsonl"
ARCHIVE = ROOT / "results" / "metrics" / "archived" / "e0_rschema_exp4_evaluation.json"
PRED = ROOT / "results" / "predictions" / "e0" / "rschema_exp4_deepseek"


def test_perfect_prediction_scores_one():
    ddl = (
        "CREATE TABLE p (id int NOT NULL, PRIMARY KEY (id));\n"
        "CREATE TABLE c (id int NOT NULL, pid int NOT NULL, PRIMARY KEY (id), FOREIGN KEY (pid) REFERENCES p (id));"
    )
    r = evaluate_ddl_pair(ddl, ddl)
    assert r["exact_match"] and r["normalized_graph_edit_distance"] == 0.0
    agg = aggregate_schemas([r])
    assert all(agg["five_elements"][k]["f1"] == 1.0 for k in agg["five_elements"])


def test_empty_prediction():
    gold = "CREATE TABLE p (id int NOT NULL, PRIMARY KEY (id));"
    r = evaluate_ddl_pair(gold, "")
    assert r["normalized_graph_edit_distance"] == 1.0
    assert r["tables"] == {"gold": 1, "recreated": 0, "matched": 0}
    assert r["hallucination_rate_by_dimension"]["tables"] == 0.0


def test_wrong_type_breaks_domain_but_not_attributes():
    g = "CREATE TABLE t (a varchar(10) NOT NULL);"
    p = "CREATE TABLE t (a int NOT NULL);"
    r = evaluate_ddl_pair(g, p)
    assert r["attributes"]["matched"] == 1 and r["domain"]["matched"] == 0


def test_nullability_mismatch_breaks_domain():
    r = evaluate_ddl_pair("CREATE TABLE t (a int NOT NULL);", "CREATE TABLE t (a int NULL);")
    assert r["attributes"]["matched"] == 1 and r["domain"]["matched"] == 0


def test_zero_scored_missing_predictions_in_aggregate():
    ddl = "CREATE TABLE t (a int NOT NULL);"
    r = evaluate_ddl_pair(ddl, ddl)
    agg = aggregate_schemas([r], n_gold=4)  # 3 missing -> nGED 1.0 each
    assert agg["zero_scored"] == 3
    assert agg["mean_normalized_graph_edit_distance"] == pytest.approx(3 / 4)
    assert agg["mean_hallucination_rate_over_dimensions"] == pytest.approx(3 / 4)


def test_gold_answer_conversion_roundtrip():
    answer = {
        "Airplane": {"Attributes": ["Airplane Number", "Model"], "Primary key": ["Airplane Number"]},
        "Flight": {
            "Attributes": ["Flight Number", "Airplane Number"],
            "Primary key": ["Flight Number"],
            "Foreign key": {"Airplane Number": {"Airplane": "Airplane Number"}},
        },
    }
    meta, ddl = gold_answer_to_metadata_and_ddl(answer, "g")
    assert meta["tables"] == ["Airplane", "Flight"]
    r = evaluate_ddl_pair(ddl, ddl)
    assert r["referential"] == {"gold": 1, "recreated": 1, "matched": 1}


needs_artifacts = pytest.mark.skipif(
    not (GOLD.is_file() and ARCHIVE.is_file() and PRED.is_dir()),
    reason="RSchema gold / archived Exp4 evaluation / DeepSeek predictions not available",
)


@needs_artifacts
def test_library_is_deterministic_and_matches_archive_where_parser_independent():
    """Tables and referential counts (parser-version independent) equal the archive per schema.

    Entity/attribute/domain counts legitimately differ from the archive because the archived JSON
    predates the DDL-parser correction; that is covered (as MISMATCH) by test_reproducibility.
    """
    arch = {s["llm"]: s for s in json.load(ARCHIVE.open())["llms"]}["deepseek"]["per_schema"]
    a = evaluate_predictions_dir(PRED, GOLD, legacy=True, limit=120)
    b = evaluate_predictions_dir(PRED, GOLD, legacy=True, limit=120)
    assert a["mean_normalized_graph_edit_distance"] == b["mean_normalized_graph_edit_distance"]
    for label, rec in a["per_schema"].items():
        assert rec["tables"] == arch[label]["tables"], label
        assert rec["referential"] == arch[label]["referential"], label
