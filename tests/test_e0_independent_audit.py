"""Independent (hand-computed) audit tests for the E0 / Table V evaluator.

Two groups:

* ``TestProtocolConfirmed`` -- each test states the manuscript protocol item it checks and
  uses expectations worked out by hand (not produced by calling the code under test twice).
  These PASS: micro F1, names-only nGED, empty-prediction policy, Hall4, Domain cohorts.

* ``TestGenuineDefects`` -- minimal DDL where the *correct* answer is unambiguous
  (``CREATE TABLE`` count == tables parsed; a column named ``unique_code`` is a column).
  These were previously ``xfail`` while defects F1–F6 were open; they must PASS after
  the 2026-11-11 parser repair.

Audit date: 2026-11-11.  See audit/E0_TABLE_V_DIAGNOSTIC.md.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import pytest

from src.evaluator import (
    aggregate_schemas,
    empty_prediction_against_gold,
    evaluate_ddl_pair,
    gold_record_to_metadata_and_ddl,
    load_jsonl,
)
from src.metrics import aggregate_hallucination_micro
from src.schema_parser import (
    ensure_prediction_metadata,
    metadata_from_ddl,
    parse_ddl_fks,
    parse_ddl_primary_unique,
)

ROOT = Path(__file__).resolve().parents[1]
HEADER = re.compile(r"CREATE\s+TABLE", re.IGNORECASE)


def _pair(gold: str, pred: str, **kw):
    return evaluate_ddl_pair(gold, pred, names_only=True, **kw)


class TestProtocolConfirmed:
    def test_micro_f1_not_macro(self):
        # schema 1: gold {alpha,beta} pred {alpha,beta}      -> G=2 P=2 M=2
        # schema 2: gold {gamma,delta,omega,sigma} pred {gamma} -> G=4 P=1 M=1
        s1 = _pair(
            "CREATE TABLE alpha (id int);\nCREATE TABLE beta (id int);",
            "CREATE TABLE alpha (id int);\nCREATE TABLE beta (id int);",
        )
        s2 = _pair(
            "CREATE TABLE gamma (id int);\nCREATE TABLE delta (id int);\n"
            "CREATE TABLE omega (id int);\nCREATE TABLE sigma (id int);",
            "CREATE TABLE gamma (id int);",
        )
        agg = aggregate_schemas([s1, s2])["five_elements"]["tables"]
        assert (agg["gold"], agg["recreated"], agg["matched"]) == (6, 3, 3)
        # micro: P=1.0, R=0.5 -> F1 = 2/3 ; macro-of-per-schema F1 would be 0.7
        assert agg["f1"] == pytest.approx(2 / 3, abs=1e-12)
        assert abs(agg["f1"] - 0.7) > 0.03

    def test_names_only_ngd_ignores_type_and_nullability(self):
        gold = "CREATE TABLE alpha (id int, name varchar(10));"
        pred = "CREATE TABLE alpha (id bigint NOT NULL, name text NOT NULL);"
        assert _pair(gold, pred)["normalized_graph_edit_distance"] == 0.0
        typed = evaluate_ddl_pair(gold, pred, names_only=False)["normalized_graph_edit_distance"]
        assert typed > 0.0  # historical typed labels do see the flip

    def test_names_only_ngd_hand_value(self):
        # gold graph = 1 table + 2 cols = 3 ; pred = 1 table + 1 col = 2 ; edit = 1 (missing col)
        gold = "CREATE TABLE alpha (id int, name varchar(10));"
        pred = "CREATE TABLE alpha (id int);"
        assert _pair(gold, pred)["normalized_graph_edit_distance"] == pytest.approx(1 / 5)

    def test_empty_prediction_policy(self):
        gold = "CREATE TABLE alpha (id int PRIMARY KEY, name varchar(10));"
        g_meta = metadata_from_ddl(gold)
        rec = empty_prediction_against_gold(g_meta, gold, names_only=True)
        assert rec["normalized_graph_edit_distance"] == 1.0
        for dim in ("tables", "attributes", "entity", "referential"):
            assert rec[dim]["recreated"] == 0 and rec[dim]["matched"] == 0
        assert rec["tables"]["gold"] == 1 and rec["attributes"]["gold"] == 2
        # Hall is NOT forced to 1 by an empty prediction (P=0 -> rate 0)
        assert aggregate_hallucination_micro([rec]) == 0.0

    def test_hall4_excludes_domain(self):
        item = {
            "tables": {"gold": 4, "recreated": 4, "matched": 2},        # 0.5
            "attributes": {"gold": 10, "recreated": 10, "matched": 5},  # 0.5
            "domain": {"gold": 10, "recreated": 10, "matched": 0},      # 1.0  (ignored)
            "entity": {"gold": 2, "recreated": 2, "matched": 2},        # 0.0
            "referential": {"gold": 0, "recreated": 0, "matched": 0},   # 0.0 (P=0)
        }
        assert aggregate_hallucination_micro([item]) == pytest.approx(0.25)

    def test_table_v_domain_cohorts(self):
        path = ROOT / "results/metrics/reproduced/E0_TABLE_V_FINAL.csv"
        if not path.exists():
            pytest.skip("E0_TABLE_V_FINAL.csv absent")
        rows = list(csv.DictReader(path.open()))
        for r in rows:
            if r["dataset"] == "RSchema":
                assert (int(r["n"]), int(r["domain_n"])) == (518, 381)
            else:
                assert (int(r["n"]), int(r["domain_n"])) == (239, 239)

    def test_rschema_ddl_gold_is_subset_with_real_types(self):
        logical = ROOT / "datasets/rschema/annotation.jsonl"
        ddl = ROOT / "datasets/rschema/annotation_ddl.jsonl"
        if not (logical.exists() and ddl.exists()):
            pytest.skip("datasets absent")
        lid = {r["id"] for r in load_jsonl(logical) if r.get("id")}
        did = {r["id"] for r in load_jsonl(ddl) if r.get("id")}
        assert len(lid) == 518 and len(did) == 381 and did <= lid
        # synthetic logical gold would be varchar(255) NOT NULL everywhere -> must not be used for Domain
        r = next(iter(load_jsonl(logical)))
        meta, _, _, _ = gold_record_to_metadata_and_ddl(r)
        types = {c["DATA_TYPE"] for cols in meta["columns_by_table"].values() for c in cols}
        assert types == {"varchar"}


class TestGenuineDefects:
    """Regression tests for parser defects F1–F6 (must PASS after the repair)."""

    def test_empty_string_default_does_not_swallow_following_table(self):
        ddl = "CREATE TABLE a (x varchar(3) NOT NULL DEFAULT '', y int);\nCREATE TABLE b (z int);"
        meta = metadata_from_ddl(ddl)
        assert meta["tables"] == ["a", "b"]
        assert [c["COLUMN_NAME"] for c in meta["columns_by_table"]["a"]] == ["x", "y"]

    def test_paren_inside_default_literal(self):
        ddl = "CREATE TABLE a (x varchar(9) DEFAULT 'a)b', y int);\nCREATE TABLE b (z int);"
        meta = metadata_from_ddl(ddl)
        assert [c["COLUMN_NAME"] for c in meta["columns_by_table"]["a"]] == ["x", "y"]

    def test_unterminated_table_body_does_not_hide_later_tables(self):
        ddl = (
            "CREATE TABLE a (\n x int,\n PRIMARY KEY (x),\n ENGINE=InnoDB;\n"
            "CREATE TABLE b (\n z int,\n PRIMARY KEY (z),\n ENGINE=InnoDB;"
        )
        assert metadata_from_ddl(ddl)["tables"] == ["a", "b"]
        # same through the E0 entry point (DDL is authoritative)
        assert ensure_prediction_metadata({"tables": ["a", "b"]}, ddl)["tables"] == ["a", "b"]

    def test_hyphenated_unquoted_table_name(self):
        ddl = "CREATE TABLE Sign-in (\n a int,\n b int\n);"
        meta = metadata_from_ddl(ddl)
        assert meta["tables"] == ["Sign-in"]
        assert len(meta["columns_by_table"]["Sign-in"]) == 2

    def test_column_named_unique_code_is_a_column(self):
        ddl = "CREATE TABLE c (\n unique_code VARCHAR(30) NOT NULL PRIMARY KEY,\n n int\n);"
        meta = metadata_from_ddl(ddl)
        assert [c["COLUMN_NAME"] for c in meta["columns_by_table"]["c"]] == ["unique_code", "n"]
        pk, _ = parse_ddl_primary_unique(ddl)
        assert pk == [("c", ["unique_code"])]

    def test_escaped_newline_ddl_parses_like_real_newlines(self):
        real = "CREATE TABLE a (\n  x int NOT NULL,\n  y int,\n  PRIMARY KEY (x)\n);"
        escaped = real.replace("\n", "\\n")
        assert "\\n" in escaped and "\n" not in escaped
        m_real, m_esc = metadata_from_ddl(real), metadata_from_ddl(escaped)
        assert len(m_esc["columns_by_table"]["a"]) == len(m_real["columns_by_table"]["a"]) == 2
        assert parse_ddl_primary_unique(escaped) == parse_ddl_primary_unique(real)

    def test_comment_prefix_before_create_table_still_recovers_columns(self):
        """DeepSeek-style prompt echo: ``--Foreachtable:CREATE TABLE ...`` on one line."""
        ddl = (
            "--Schemafordatabase:demo\n"
            "--Foreachtable:CREATE TABLE `t1` (`id` int(11) NOT NULL,`name` varchar(255) NOT NULL,"
            "PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;\n"
            "--Foreachtable:CREATE TABLE `t2` (`t1_id` int(11) NOT NULL,PRIMARY KEY (`t1_id`))"
            " ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;"
        )
        meta = metadata_from_ddl(ddl)
        assert meta["tables"] == ["t1", "t2"]
        assert [c["COLUMN_NAME"] for c in meta["columns_by_table"]["t1"]] == ["id", "name"]
        assert [c["COLUMN_NAME"] for c in meta["columns_by_table"]["t2"]] == ["t1_id"]

    def test_alter_table_foreign_key_counted(self):
        ddl = (
            "CREATE TABLE p (id int PRIMARY KEY);\n"
            "CREATE TABLE c (id int PRIMARY KEY, p_id int);\n"
            "ALTER TABLE c ADD CONSTRAINT fk_c_p FOREIGN KEY (p_id) REFERENCES p (id);"
        )
        fks, _ = parse_ddl_fks(ddl)
        assert fks == [("c", ["p_id"], "p", ["id"])]

    def test_schemabench_gold_table_count_equals_create_table_count(self):
        path = ROOT / "datasets/schemabench/annotation_ddl.jsonl"
        if not path.exists():
            pytest.skip("dataset absent")
        lost = 0
        for r in load_jsonl(path):
            if not r.get("id"):
                continue
            ddl = r["answer"]
            lost += max(0, len(HEADER.findall(ddl)) - len(metadata_from_ddl(ddl)["tables"]))
        assert lost == 0, f"{lost} CREATE TABLE statements in gold not parsed"

    def test_llama_rschema_predictions_tables_equal_headers(self):
        d = ROOT / "results/predictions/e0/rschema_exp4_llama31"
        if not d.exists():
            pytest.skip("predictions absent")
        lost = 0
        for p in sorted(d.glob("[0-9][0-9][0-9][0-9].json")):
            ddl = json.loads(p.read_text())["ddl"]
            lost += max(0, len(HEADER.findall(ddl)) - len(metadata_from_ddl(ddl)["tables"]))
        assert lost == 0, f"{lost} predicted CREATE TABLE statements not parsed"
