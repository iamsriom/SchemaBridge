"""Gold dataset sanity: sizes 518 / 239 / 145 and unique ids.

Fails (rather than skips) if a dataset is missing: these files are part of the package.
The enterprise schemas are a symlink to /data/Text2ER/schema, so that test skips only when
the symlink dangles.
"""
import json
from pathlib import Path

import pytest

from src.evaluator import gold_record_to_metadata_and_ddl, load_jsonl

D = Path(__file__).resolve().parents[1] / "datasets"


def test_rschema_has_518_unique_records():
    rows = load_jsonl(D / "rschema" / "annotation.jsonl")
    assert len(rows) == 518
    assert len({r["id"] for r in rows}) == 518
    assert all(isinstance(r["answer"], dict) and r["question"] for r in rows)


def test_rschema_annotation_ddl_is_a_381_subset_not_518():
    """Observation, not an aspiration: the DDL-answer file covers only 381 of the 518 RSchema schemas."""
    rows = load_jsonl(D / "rschema" / "annotation_ddl.jsonl")
    ids = {r["id"] for r in rows}
    gold_ids = {r["id"] for r in load_jsonl(D / "rschema" / "annotation.jsonl")}
    assert len(rows) == len(ids) == 381
    assert ids <= gold_ids


def test_schemabench_has_239_unique_records():
    rows = load_jsonl(D / "schemabench" / "annotation_ddl.jsonl")
    assert len(rows) == 239
    assert len({r["id"] for r in rows}) == 239
    assert all(isinstance(r["answer"], str) and "CREATE TABLE" in r["answer"].upper() for r in rows)
    manifest = json.loads((D / "schemabench" / "manifest.json").read_text())
    assert manifest["record_count"] == 239
    pairs = json.loads((D / "schemabench" / "schema_nl_pairs.json").read_text())
    assert len(pairs) == 239 and {p["id"] for p in pairs} == {r["id"] for r in rows}


def test_enterprise145_has_145_schemas():
    schema_dir = D / "enterprise145" / "schema"
    if not schema_dir.is_dir():
        pytest.skip("enterprise145/schema symlink target (/data/Text2ER/schema) not available")
    sql = sorted(schema_dir.glob("*.sql"))
    meta = sorted(p for p in schema_dir.glob("*.metadata.json"))
    assert len(sql) == 145
    assert len(meta) == 145
    index = json.loads((schema_dir / "index.json").read_text())
    assert len(index["datasets"]) == 145
    assert len({d["safe_name"] for d in index["datasets"]}) == 145


def test_gold_records_parse_to_nonempty_schemas():
    for fname in ("rschema/annotation.jsonl", "schemabench/annotation_ddl.jsonl"):
        for rec in load_jsonl(D / fname)[:60]:
            meta, ddl, n_tables, n_cols = gold_record_to_metadata_and_ddl(rec)
            assert n_tables >= 1 and n_cols >= 1, (fname, rec["id"])
            assert len(meta["tables"]) >= 1
