"""Packaged dataset populations (145 / 239 / 381 / 518) and E1 dataset preparation."""
import pytest

from _synthetic import ROOT, build_data_root, load_script
from src import datasets_io as dio

PACKAGED = ROOT / "datasets"


@pytest.fixture(scope="module")
def packaged():
    if not (PACKAGED / "rschema" / "annotation.jsonl").is_file():
        pytest.skip("packaged datasets/ not present")
    return PACKAGED


def test_expected_constants():
    assert dio.EXPECTED_COUNTS == {"enterprise145": 145, "schemabench": 239, "rschema": 381, "rschema_logical": 518}


def test_packaged_counts(packaged):
    assert len(dio.load_enterprise145(packaged)) == 145
    assert len(dio.load_schemabench(packaged)) == 239
    assert len(dio.load_rschema_381(packaged)) == 381
    assert len(dio.load_rschema_logical_518(packaged)) == 518


def test_rschema_serials_are_positions_in_518(packaged):
    recs = dio.load_rschema_381(packaged)
    logical = {r.serial: r for r in dio.load_rschema_logical_518(packaged)}
    serials = [int(r.serial) for r in recs]
    assert serials == sorted(set(serials)) and max(serials) <= 518 and serials != list(range(1, 382))
    for r in recs:
        assert logical[r.serial].schema_id == r.schema_id and logical[r.serial].has_ddl
        assert r.ddl_source == "annotation_ddl" and r.ddl.strip() and r.gold_nl
    assert sum(1 for r in logical.values() if r.has_ddl) == 381


def test_enterprise_has_no_gold_text_and_schemabench_has_gold(packaged):
    assert all(r.gold_nl == "" and r.ddl.strip() for r in dio.load_enterprise145(packaged))
    assert all(r.gold_nl and r.ddl.strip() for r in dio.load_schemabench(packaged))


def test_strict_loader_rejects_wrong_count(tmp_path):
    root = build_data_root(tmp_path)
    with pytest.raises(ValueError):
        dio.load_rschema_381(root)  # synthetic root has 3 records, not 381
    assert len(dio.load_rschema_381(root, strict=False)) == 3


def test_prepare_dataset_eligible_rows_and_csv(tmp_path):
    prep = load_script("experiments/E1/prepare_dataset.py", "e1_prepare")
    root = build_data_root(tmp_path)
    recs = dio.load_rschema_381(root, strict=False)
    rows = prep.eligible_rows(recs)
    assert [(r["serial_in_518"], r["eval_index"]) for r in rows] == [("0001", 1), ("0003", 2), ("0004", 3)]
    info = prep.explain_518_vs_381(str(root))
    assert (info["n_logical"], info["n_ddl_matched"], info["n_logical_only"]) == (4, 3, 1)
    out = tmp_path / "out"
    assert prep.main(["--data-root", str(root), "--out-dir", str(out), "--no-strict"]) == 0
    header = (out / prep.ELIGIBLE_FILE).read_text().splitlines()[0]
    assert header == "schema_id,serial_in_518,eval_index,database"
    assert prep.main(["--data-root", str(root), "--out-dir", str(out)]) == 1  # strict: counts differ
