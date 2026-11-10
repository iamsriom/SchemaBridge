import math

import pytest

from src.metrics import (
    ELEMENTS,
    HALLUCINATION_DIMS,
    aggregate_hallucination_micro,
    aggregate_hallucination_micro_5dim,
    f1_score,
    graph_edit_cost,
    hallucination_rate,
    is_exact_match,
    macro_mean,
    micro_aggregate,
    micro_aggregate_all,
    micro_f1,
    micro_prf,
    normalized_graph_edit_distance,
    schema_difficulty,
    set_prf,
    zero_scored_schema_metrics,
)
from src.schema_parser import metadata_from_ddl


def test_f1_basics():
    assert f1_score(0, 0) == 0.0
    assert f1_score(1, 1) == 1.0
    assert f1_score(0.5, 1.0) == pytest.approx(2 / 3)


# --- micro F1 ------------------------------------------------------------------------
def test_micro_f1_from_counts():
    # P = 6/8, R = 6/10 -> F1 = 2*6/(8+10)
    assert micro_f1(gold=10, recreated=8, matched=6) == pytest.approx(12 / 18)


def test_micro_f1_empty_policies():
    assert micro_f1(0, 0, 0) == 0.0  # everything empty -> 0 (micro policy)
    assert micro_f1(gold=5, recreated=0, matched=0) == 0.0  # empty prediction
    assert micro_f1(gold=0, recreated=5, matched=0) == 0.0  # empty gold
    assert micro_prf(0, 0, 0)["hallucination_rate"] == 0.0


def test_micro_aggregation_is_not_mean_of_per_schema_f1():
    # schema A: tiny perfect; schema B: big and poor.  Micro pools the counts first.
    items = [
        {"tables": {"gold": 1, "recreated": 1, "matched": 1}},
        {"tables": {"gold": 99, "recreated": 99, "matched": 0}},
    ]
    agg = micro_aggregate(items, "tables")
    assert (agg["gold"], agg["recreated"], agg["matched"]) == (100, 100, 1)
    assert agg["f1"] == pytest.approx(0.01)
    macro = macro_mean([1.0, 0.0])
    assert macro == 0.5 and agg["f1"] != macro


def test_micro_aggregate_empty_list():
    agg = micro_aggregate([], "tables")
    assert agg["f1"] == 0.0 and agg["gold"] == 0 and agg["hallucinated"] == 0


def test_hallucination_rate():
    assert hallucination_rate(10, 4) == pytest.approx(0.6)
    assert hallucination_rate(0, 0) == 0.0  # nothing recreated -> 0 by policy
    assert hallucination_rate(3, 5) == 0.0  # never negative
    assert hallucination_rate(5, 5) == 0.0


def test_aggregate_hallucination_micro_vs_macro_on_unequal_sizes():
    """Micro Hall. pools counts first; macro averages per-schema rates — they diverge."""
    # Schema A: tiny, high FP rate (1/1 = 1.0 on every dim).
    # Schema B: large, low FP rate (1/99 ≈ 0.0101 on every dim).
    items = []
    for gold, rec, mat in ((1, 1, 0), (99, 99, 98)):
        row = {k: {"gold": gold, "recreated": rec, "matched": mat} for k in ELEMENTS}
        row["hallucination_rate_by_dimension"] = {
            k: hallucination_rate(rec, mat) for k in ELEMENTS
        }
        items.append(row)
    micro_h = aggregate_hallucination_micro(items)
    # Pooled: R=100, M=98 -> H_d = 2/100 = 0.02 for each of T/A/E/R -> mean = 0.02
    assert micro_h == pytest.approx(0.02)
    assert set(HALLUCINATION_DIMS) == {"tables", "attributes", "entity", "referential"}
    macro_h = macro_mean(
        [macro_mean(s["hallucination_rate_by_dimension"].values()) for s in items]
    )
    assert macro_h == pytest.approx((1.0 + 1 / 99) / 2)
    assert micro_h != pytest.approx(macro_h)


def test_aggregate_hallucination_micro_excludes_domain():
    # Domain has high FP rate; T/A/E/R are perfect -> Hall4 = 0, Hall5 > 0
    items = [
        {
            "tables": {"gold": 2, "recreated": 2, "matched": 2},
            "attributes": {"gold": 4, "recreated": 4, "matched": 4},
            "domain": {"gold": 4, "recreated": 4, "matched": 0},
            "entity": {"gold": 2, "recreated": 2, "matched": 2},
            "referential": {"gold": 1, "recreated": 1, "matched": 1},
        }
    ]
    assert aggregate_hallucination_micro(items) == 0.0
    assert aggregate_hallucination_micro_5dim(items) == pytest.approx(0.2)  # only Domain FP


def test_aggregate_hallucination_micro_empty_prediction_is_zero():
    # Empty prediction: R=0, M=0 on every dim -> each H_d = 0 -> Hall. = 0
    items = [{k: {"gold": 5, "recreated": 0, "matched": 0} for k in ELEMENTS}]
    assert aggregate_hallucination_micro(items) == 0.0
    fe = micro_aggregate_all(items)
    assert all(fe[d]["hallucination_rate"] == 0.0 for d in ELEMENTS)


def test_extra_unmatched_prediction_raises_hall():
    base = [
        {
            "tables": {"gold": 1, "recreated": 1, "matched": 1},
            "attributes": {"gold": 2, "recreated": 2, "matched": 2},
            "domain": {"gold": 2, "recreated": 2, "matched": 2},
            "entity": {"gold": 1, "recreated": 1, "matched": 1},
            "referential": {"gold": 0, "recreated": 0, "matched": 0},
        }
    ]
    assert aggregate_hallucination_micro(base) == 0.0
    worse = [
        {
            "tables": {"gold": 1, "recreated": 2, "matched": 1},  # +1 unmatched table
            "attributes": {"gold": 2, "recreated": 2, "matched": 2},
            "domain": {"gold": 2, "recreated": 99, "matched": 0},  # Domain noise must not affect Hall4
            "entity": {"gold": 1, "recreated": 1, "matched": 1},
            "referential": {"gold": 0, "recreated": 0, "matched": 0},
        }
    ]
    h = aggregate_hallucination_micro(worse)
    # Only tables contributes: H_T=1/2, others 0 -> mean = 0.125
    assert h == pytest.approx(0.125)
    assert h > 0.0


def test_micro_prf_fields_consistent():
    r = micro_prf(10, 8, 6)
    assert r["hallucinated"] == 2 and r["hallucination_rate"] == pytest.approx(0.25)
    assert r["precision"] == pytest.approx(0.75) and r["recall"] == pytest.approx(0.6)


# --- set PRF -------------------------------------------------------------------------
def test_set_prf_regular():
    r = set_prf({"a", "b", "c"}, {"b", "c", "d", "e"})
    assert r["precision"] == pytest.approx(0.5) and r["recall"] == pytest.approx(2 / 3)


def test_set_prf_empty_gold_and_pred_policies():
    assert set_prf(set(), set()) == {"precision": 1.0, "recall": 1.0, "f1": 1.0}  # vacuous
    assert set_prf(set(), set(), empty="zero") == {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    only_pred = set_prf(set(), {"x"})
    assert only_pred["f1"] == 0.0 and only_pred["recall"] == 1.0  # vacuous recall, zero precision
    only_gold = set_prf({"x"}, set())
    assert only_gold["f1"] == 0.0 and only_gold["precision"] == 1.0
    assert set_prf({"x"}, set(), empty="zero")["precision"] == 0.0
    with pytest.raises(ValueError):
        set_prf({"x"}, {"x"}, empty="bogus")


def test_set_prf_accepts_iterables_with_duplicates():
    assert set_prf(["a", "a", "b"], ["a"])["recall"] == pytest.approx(0.5)


# --- nGED ----------------------------------------------------------------------------
def test_nged_identical_and_disjoint():
    ddl = "CREATE TABLE a (x int NOT NULL, y text NOT NULL);\nCREATE TABLE b (id int, aid int, FOREIGN KEY (aid) REFERENCES a (x));"
    meta = metadata_from_ddl(ddl)
    assert normalized_graph_edit_distance(meta, ddl, meta, ddl) == 0.0
    other = "CREATE TABLE zzz (q int);"
    om = metadata_from_ddl(other)
    assert normalized_graph_edit_distance(meta, ddl, om, other) == 1.0


def test_nged_empty_graphs_policy():
    e = metadata_from_ddl("")
    assert normalized_graph_edit_distance(e, "", e, "") == 0.0  # both empty: nothing to edit
    ddl = "CREATE TABLE a (x int);"
    m = metadata_from_ddl(ddl)
    assert normalized_graph_edit_distance(m, ddl, e, "") == 1.0  # one side empty -> worst


def test_nged_normalises_by_sum_of_sizes_not_max():
    # gold: table a + col x (size 2). pred: table a + cols x,y (size 3). cost = 1 (extra col y).
    g = {"a": {("x", "int", "NO")}}
    p = {"a": {("x", "int", "NO"), ("y", "int", "NO")}}
    cost, denom = graph_edit_cost(g, p, set(), set())
    assert (cost, denom) == (1, 5)  # sum of sizes (2 + 3), NOT max(2, 3) = 3
    assert cost / denom == pytest.approx(0.2)


def test_nged_uses_rschema_name_matching_and_type_family():
    g = "CREATE TABLE `Airplane` (\n  `Airplane_Number` varchar(255) NOT NULL\n);"
    p = "CREATE TABLE airplanes (\n  airplane_number text NOT NULL\n);"
    gm, pm = metadata_from_ddl(g), metadata_from_ddl(p)
    assert normalized_graph_edit_distance(gm, g, pm, p) == 0.0
    # nullability is part of the label
    p2 = "CREATE TABLE airplanes (\n  airplane_number text NULL\n);"
    assert normalized_graph_edit_distance(gm, g, metadata_from_ddl(p2), p2) > 0


def test_fk_direction_counts_in_nged():
    a = "CREATE TABLE p (id int);\nCREATE TABLE c (pid int, FOREIGN KEY (pid) REFERENCES p (id));"
    b = "CREATE TABLE p (pid int, FOREIGN KEY (pid) REFERENCES c (id));\nCREATE TABLE c (id int);"
    assert normalized_graph_edit_distance(metadata_from_ddl(a), a, metadata_from_ddl(b), b) > 0


# --- exact match / difficulty / zero policy -------------------------------------------
def test_exact_match():
    row = {"gold": 3, "recreated": 3, "matched": 3}
    zero = {"gold": 0, "recreated": 0, "matched": 0}
    assert is_exact_match(row, row, row, row, row)
    assert is_exact_match(zero, zero, zero, zero, zero)  # two empty schemas
    assert not is_exact_match(row, row, row, row, {"gold": 3, "recreated": 4, "matched": 3})


@pytest.mark.parametrize(
    "t,c,d",
    [(1, 5, "easy"), (3, 30, "easy"), (4, 10, "medium"), (3, 31, "medium"), (15, 150, "medium"), (16, 10, "hard"), (5, 151, "hard")],
)
def test_difficulty(t, c, d):
    assert schema_difficulty(t, c) == d


def test_zero_score_policy():
    z = zero_scored_schema_metrics()
    assert z["normalized_graph_edit_distance"] == 1.0
    assert z["per_schema_hallucination"] == 1.0
    assert set(z["per_schema_f1"]) == set(ELEMENTS) and all(v == 0.0 for v in z["per_schema_f1"].values())


def test_macro_mean_empty():
    assert macro_mean([]) == 0.0
    assert math.isclose(macro_mean([1, 2, 3]), 2.0)
