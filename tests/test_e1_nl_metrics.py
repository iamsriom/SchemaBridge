"""E1 text metrics on tiny synthetic strings (no research data)."""
import pytest

from _synthetic import FIXTURES, build_data_root, corpus, load_script, write_e1_preds
from src import datasets_io as dio
from src import nl_metrics as nlm

HYPS = ["the cat sat on the mat today", "a quick brown fox jumps over", "hello world again my friend"]
REFS = ["the cat sat on the mat today", "a quick brown fox jumped over", "hello world once more my friend"]


def test_bleu_uses_single_reference_stream_layout():
    sacrebleu = pytest.importorskip("sacrebleu")
    ours = nlm.compute_bleu(HYPS, REFS)
    assert ours == pytest.approx(sacrebleu.corpus_bleu(HYPS, [REFS]).score)
    assert nlm.compute_bleu(REFS, REFS) == pytest.approx(100.0)
    # The historical layout [[r] for r in refs] (one stream per record) gives a DIFFERENT, wrong number.
    try:
        buggy = sacrebleu.corpus_bleu(HYPS, [[r] for r in REFS]).score
    except Exception:  # newer sacrebleu may reject the layout outright
        return
    assert buggy != pytest.approx(ours)


def test_bleu_length_mismatch_raises():
    pytest.importorskip("sacrebleu")
    with pytest.raises(ValueError):
        nlm.compute_bleu(HYPS[:2], REFS)


def test_rouge_l_identical_and_disjoint():
    pytest.importorskip("rouge_score")
    assert nlm.compute_rougeL(REFS, REFS) == pytest.approx(1.0)
    assert nlm.compute_rougeL(["zzz qqq"], ["alpha beta gamma"]) == pytest.approx(0.0)


def test_sanitize_repairs_bpe_artifacts_and_blank_lines():
    raw = "Hello\u0120world\u010a\u010a  second   line \u2581end"
    out = nlm.sanitize_nl_text(raw)
    assert out == "Hello world\nsecond line end"
    assert nlm.sanitize_nl_text("") == ""
    ok, reason = nlm.validate_nl_text("[INST] " + "word " * 40)
    assert not ok and reason.startswith("tokenization_artifact")


def test_scr_full_partial_and_empty():
    ddl = corpus()["schemas"][0]["ddl"]
    good = corpus()["schemas"][0]["description_good"]
    full = nlm.schema_coverage_rate(ddl, good)
    assert full["total"] == 6 and full["matched"] == 6 and full["coverage"] == 1.0  # 2 tables + 4 distinct columns
    part = nlm.schema_coverage_rate(ddl, "only the author table and its full name")
    assert 0.0 < part["coverage"] < 1.0
    assert nlm.schema_coverage_rate(ddl, "")["coverage"] == 0.0
    assert nlm.schema_coverage_rate("", "anything")["empty_denominator"] is True
    # normalisation: case / underscores / backticks are ignored
    assert nlm.norm_ident("`Full_Name`") == "fullname"


def test_scr_macro_weights_schemas_equally():
    s = corpus()["schemas"]
    hyps = [s[0]["description_good"], ""]
    ddls = [s[0]["ddl"], s[1]["ddl"]]
    assert nlm.compute_scr_macro(hyps, ddls) == pytest.approx(0.5)


def test_enterprise_text_metrics_not_applicable(tmp_path):
    ev = load_script("experiments/E1/evaluate.py", "e1_evaluate")
    root = build_data_root(tmp_path)
    gold = dio.load_enterprise145(root, strict=False)
    assert all(g.gold_nl == "" for g in gold)
    texts = {g.serial: corpus()["schemas"][i]["description_good"] for i, g in enumerate(gold)}
    write_e1_preds(tmp_path / "pred", gold, texts)
    m, rows = ev.evaluate_combo("enterprise145", "llama31", "basic", tmp_path / "pred", data_root=str(root),
                                fail_policy="score", skip_bertscore=True, device="cpu", strict=False)
    assert m["metrics"]["bleu4"] is None and m["metrics"]["rougeL"] is None and m["metrics"]["bertscore_f1"] is None
    assert set(m["not_applicable"]) == {"bleu4", "rougeL", "bertscore_f1"}
    assert m["metrics"]["scr_macro"] == pytest.approx(1.0)
    assert len(rows) == 3


def test_e1_fail_policy_score_vs_skip(tmp_path):
    pytest.importorskip("sacrebleu")
    pytest.importorskip("rouge_score")
    ev = load_script("experiments/E1/evaluate.py", "e1_evaluate")
    root = build_data_root(tmp_path)
    gold = dio.load_rschema_381(root, strict=False)
    assert [g.serial for g in gold] == ["0001", "0003", "0004"]  # non-contiguous serials
    s = corpus()["schemas"]
    # 0001 good; 0003 missing file; 0004 error record
    write_e1_preds(tmp_path / "pred", gold, {"0001": s[0]["description_good"], "0004": ""},
                   errors={"0004": "RateLimit"})
    kw = dict(data_root=str(root), skip_bertscore=True, device="cpu", strict=False)
    m_score, rows = ev.evaluate_combo("rschema", "llama31", "detailed", tmp_path / "pred", fail_policy="score", **kw)
    assert (m_score["n_gold"], m_score["n_scored"], m_score["n_failed"]) == (3, 3, 2)
    assert [r["status"] for r in rows] == ["ok", "scored_empty", "scored_empty"]
    assert m_score["metrics"]["scr_macro"] == pytest.approx(1 / 3)
    assert m_score["metrics"]["bleu4"] is not None and m_score["skipped"] == ["bertscore_f1"]
    m_skip, rows = ev.evaluate_combo("rschema", "llama31", "detailed", tmp_path / "pred", fail_policy="skip", **kw)
    assert (m_skip["n_scored"], m_skip["n_failed"]) == (1, 2)
    assert m_skip["metrics"]["scr_macro"] == pytest.approx(1.0)
    assert [r["status"] for r in rows] == ["ok", "skipped", "skipped"]


def test_fixture_files_contain_no_numeric_results():
    text = (FIXTURES / "tiny_corpus.json").read_text(encoding="utf-8")
    assert "bleu" not in text.lower() and "f1" not in text.lower()
