"""Strict E1 -> E2 provenance (synthetic only): wrong describer / prompt / model / id / hash / duplicates rejected."""
import copy
import json

import pytest

from _synthetic import build_data_root, corpus, load_script, write_e1_preds
from src import datasets_io as dio
from src import inference_clients as ic
from src import prompt_assets as pa
from src import provenance as prov
from src import repro_io as rio
from src.datasets_io import GoldRecord

GOLD = GoldRecord("schemabench", "0001", "SB-1", "q", "CREATE TABLE `t` (`id` int);", "synthetic", "s1", "d")


def good(describer="llama31", prompt="basic", **over):
    d = {"text_number": 1, "id": "SB-1", "llm": describer, "model_id": ic.MODELS[describer].model_id,
         "database": "d", "prompt_style": rio.PROMPT_STYLE[prompt], "nl_text": "A usable description.",
         "generation": {"prompt_variant": prompt, "prompt_sha256": pa.EXPECTED_SHA256[prompt], "temperature": 0.2}}
    d.update(over)
    return d


def check(entry, mode="strict", describer="llama31", prompt="basic", dataset="schemabench"):
    return prov.validate_e1_description(entry, gold=GOLD, dataset=dataset, describer=describer, prompt=prompt, mode=mode)


# --------------------------------------------------------------------------- per-entry, strict


@pytest.mark.parametrize("describer", ic.DESCRIBER_KEYS)
@pytest.mark.parametrize("prompt", ["basic", "detailed"])
def test_valid_entry_accepted(describer, prompt):
    assert check(good(describer, prompt), describer=describer, prompt=prompt) == []


def test_provenance_error_is_a_value_error():
    assert issubclass(prov.ProvenanceError, ValueError)


@pytest.mark.parametrize("name,entry", [
    ("wrong id", good(id="SB-2")),
    ("wrong describer llm", good(llm="llama31x")),
    ("other describer", good("deepseek")),
    ("alias is not a describer key", good(llm="claude_sonnet_4_6")),
    ("wrong model_id", good(model_id="meta-llama/Meta-Llama-3-8B")),
    ("wrong prompt_style", good(prompt_style="schema2text2")),
    ("wrong variant", good(generation={"prompt_variant": "detailed", "prompt_sha256": pa.EXPECTED_SHA256["basic"]})),
    ("wrong hash", good(generation={"prompt_variant": "basic", "prompt_sha256": pa.EXPECTED_SHA256["detailed"]})),
    ("garbage hash", good(generation={"prompt_variant": "basic", "prompt_sha256": "0" * 64})),
    ("wrong dataset field", good(dataset="rschema")),
    ("error field", good(error="boom")),
    ("empty nl_text", good(nl_text="   ")),
    ("no nl_text", {k: v for k, v in good().items() if k != "nl_text"}),
])
def test_contradicting_or_unusable_entries_rejected(name, entry):
    with pytest.raises(prov.ProvenanceError):
        check(entry)
    with pytest.raises(prov.ProvenanceError):  # present-but-wrong is rejected in legacy mode too
        check(entry, mode="legacy")


def test_none_and_non_dict_rejected():
    for bad in (None, [], "x"):
        with pytest.raises(prov.ProvenanceError):
            check(bad)


def test_detailed_prompt_dir_is_not_accepted_as_basic():
    with pytest.raises(prov.ProvenanceError):
        check(good(prompt="detailed"), prompt="basic")
    with pytest.raises(prov.ProvenanceError):
        check(good("sonnet46"), describer="llama31")


@pytest.mark.parametrize("field", ["llm", "model_id", "prompt_style"])
def test_strict_requires_top_level_fields(field):
    e = good()
    del e[field]
    with pytest.raises(prov.ProvenanceError, match=field):
        check(e)


def test_strict_requires_prompt_hash_but_not_variant():
    e = good()
    e["generation"] = {"prompt_variant": "basic"}
    with pytest.raises(prov.ProvenanceError, match="prompt_sha256"):
        check(e)
    e["generation"] = {"prompt_sha256": pa.EXPECTED_SHA256["basic"]}  # variant is optional, checked if present
    assert check(e) == []
    e.pop("generation")
    with pytest.raises(prov.ProvenanceError):
        check(e)


def test_missing_id_rejected_in_both_modes():
    e = good()
    del e["id"]
    for mode in ("strict", "legacy"):
        with pytest.raises(prov.ProvenanceError, match="id"):
            check(e, mode=mode)


def test_unknown_mode_describer_prompt():
    with pytest.raises(ValueError):
        check(good(), mode="lenient")
    with pytest.raises(prov.ProvenanceError):
        check(good(), describer="gpt4omini")  # the constructor is not a describer
    with pytest.raises(prov.ProvenanceError):
        check(good(), prompt="verbose")


# --------------------------------------------------------------------------- legacy mode


def test_legacy_allows_missing_fields_with_warnings():
    e = good()
    for k in ("llm", "model_id", "prompt_style", "generation"):
        del e[k]
    warns = check(e, mode="legacy")
    joined = " ".join(warns)
    assert len(warns) == 4 and all("legacy" in w for w in warns)
    for k in ("llm", "model_id", "prompt_style", "prompt_sha256"):
        assert k in joined
    assert check(good(), mode="legacy") == []  # fully provenanced legacy-mode record: no warnings


def test_legacy_still_requires_usable_text_and_no_error():
    e = {"id": "SB-1", "nl_text": ""}
    with pytest.raises(prov.ProvenanceError):
        check(e, mode="legacy")
    with pytest.raises(prov.ProvenanceError):
        check({"id": "SB-1", "nl_text": "ok", "error": "x"}, mode="legacy")
    assert len(check({"id": "SB-1", "nl_text": "ok"}, mode="legacy")) == 4


def test_entry_provenance_fields():
    p = prov.entry_provenance(good(), describer="llama31", prompt="basic", mode="strict")
    assert p["source_schema2text_llm"] == "llama31" and p["source_prompt_style"] == "schema2text1"
    assert p["source_model_id"] == ic.MODELS["llama31"].model_id
    assert p["source_prompt_sha256"] == pa.EXPECTED_SHA256["basic"] and p["source_prompt_variant"] == "basic"
    assert p["source_provenance_mode"] == "strict" and p["source_provenance_warnings"] == []
    legacy = prov.entry_provenance({"id": "SB-1", "nl_text": "x"}, describer="llama31", prompt="basic",
                                   mode="legacy", warnings=["w"])
    assert legacy["source_model_id"] is None and legacy["source_prompt_sha256"] is None  # unverified stays unset
    assert legacy["source_provenance_warnings"] == ["w"]


# --------------------------------------------------------------------------- directory level


def _preds(*entries):
    return {f"{i:04d}": (e, None) for i, e in enumerate(entries, 1)}


def test_duplicate_ids_rejected():
    with pytest.raises(prov.ProvenanceError, match="duplicate"):
        prov.check_directory(_preds(good(), good()), prompt="basic")
    with pytest.raises(prov.ProvenanceError, match="duplicate"):
        prov.check_directory(_preds(good(), good()), prompt="basic", mode="legacy")
    prov.check_directory(_preds(good(), good(id="SB-2")), prompt="basic")  # distinct ids fine
    prov.check_directory({"0001": (None, "unreadable_json:ValueError")}, prompt="basic")  # unreadable files ignored


def test_mixed_prompt_styles_rejected_in_strict_only():
    mixed = _preds(good(), good(id="SB-2", prompt_style="schema2text2"))
    with pytest.raises(prov.ProvenanceError, match="mixed prompt_style"):
        prov.check_directory(mixed, prompt="basic")
    prov.check_directory(mixed, prompt="basic", mode="legacy")


# --------------------------------------------------------------------------- E2/run.py integration


@pytest.fixture()
def e2(monkeypatch):
    mod = load_script("experiments/E2/run.py", "e2_run_prov")
    monkeypatch.setattr(mod.dio, "load_dataset",
                        lambda name, data_root=None, strict=True: dio.LOADERS[name](data_root, strict=False))
    return mod


def _setup(tmp_path, **kw):
    root = build_data_root(tmp_path)
    gold = dio.load_schemabench(root, strict=False)
    s = corpus()["schemas"]
    write_e1_preds(tmp_path / "e1", gold, {g.serial: s[i]["description_good"] for i, g in enumerate(gold)}, **kw)
    return root, gold


def _load(e2, root, tmp_path, **kw):
    return e2._load_descriptions("schemabench", tmp_path / "e1", str(root), None, describer="llama31",
                                 prompt="basic", **kw)


def test_run_accepts_matching_e1_directory(e2, tmp_path):
    root, gold = _setup(tmp_path, describer="llama31", prompt="basic")
    _, items, provenance = _load(e2, root, tmp_path)
    assert [why for _, _, why in items] == [None] * 3 and len(provenance) == 3
    assert provenance["0001"]["source_provenance_mode"] == "strict"


@pytest.mark.parametrize("describer,prompt", [("deepseek", "basic"), ("llama31", "detailed"), ("sonnet46", "detailed")])
def test_run_rejects_wrong_describer_or_prompt_without_relabelling(e2, tmp_path, describer, prompt):
    root, _ = _setup(tmp_path, describer=describer, prompt=prompt)
    _, items, provenance = _load(e2, root, tmp_path)  # requested: llama31 / basic
    assert all(nl is None and why.startswith("provenance:") for _, nl, why in items) and provenance == {}


def test_legacy_flag_still_rejects_present_but_wrong_provenance(e2, tmp_path):
    root, _ = _setup(tmp_path)  # llm="synthetic" model_id="synthetic": present but WRONG
    _, items, _ = _load(e2, root, tmp_path, allow_legacy=True)
    assert all(why and why.startswith("provenance:") for _, _, why in items)


def _strip_provenance(pred_dir):
    for p in pred_dir.glob("*.json"):
        d = json.loads(p.read_text())
        for k in ("llm", "model_id", "prompt_style", "generation"):
            d.pop(k, None)
        p.write_text(json.dumps(d))


def test_missing_provenance_needs_allow_legacy(e2, tmp_path):
    root, _ = _setup(tmp_path, describer="llama31", prompt="basic")
    _strip_provenance(tmp_path / "e1")
    _, strict_items, _ = _load(e2, root, tmp_path)
    assert all(nl is None and "missing provenance" in why for _, nl, why in strict_items)
    _, legacy_items, provenance = _load(e2, root, tmp_path, allow_legacy=True)
    assert all(why is None for _, _, why in legacy_items)
    assert provenance["0001"]["source_provenance_mode"] == "legacy"
    assert provenance["0001"]["source_provenance_warnings"] and provenance["0001"]["source_model_id"] is None


def test_run_rejects_duplicate_ids_and_mixed_styles(e2, tmp_path):
    root, _ = _setup(tmp_path, describer="llama31", prompt="basic")
    e1 = tmp_path / "e1"
    dup = json.loads((e1 / "0001.json").read_text())
    (e1 / "0009.json").write_text(json.dumps(dup))
    with pytest.raises(prov.ProvenanceError, match="duplicate"):
        _load(e2, root, tmp_path)
    (e1 / "0009.json").unlink()
    other = copy.deepcopy(dup)
    other["id"] = "SB-OTHER"
    other["prompt_style"] = "schema2text2"
    (e1 / "0009.json").write_text(json.dumps(other))
    with pytest.raises(prov.ProvenanceError, match="mixed prompt_style"):
        _load(e2, root, tmp_path)


def test_dry_run_reports_invalid_descriptions_and_cli_exit_code(e2, tmp_path, capsys):
    root, _ = _setup(tmp_path, describer="deepseek", prompt="basic")
    args = e2.build_parser().parse_args(["--dataset", "schemabench", "--describer-model", "llama31", "--prompt", "basic",
                                         "--data-root", str(root)])
    assert args.allow_legacy_e1 is False
    plan = e2.dry_run_one("schemabench", "llama31", "basic", args, tmp_path / "e1", tmp_path / "out")
    assert plan["n_descriptions_available"] == 0 and plan["n_descriptions_missing"] == 3
    assert plan["e1_provenance_mode"] == "strict" and "provenance" in capsys.readouterr().out
    rc = e2.main(["--dataset", "schemabench", "--describer-model", "llama31", "--prompt", "basic",
                  "--data-root", str(root), "--e1-pred-dir", str(tmp_path / "e1"), "--out-dir", str(tmp_path / "o2")])
    assert rc == 0  # invalid descriptions are reported, never silently used; the dry-run itself still validates


def test_execute_writes_error_records_for_rejected_descriptions_without_api_call(e2, tmp_path):
    root, _ = _setup(tmp_path, describer="deepseek", prompt="basic")

    class Boom:
        def generate(self, req):  # pragma: no cover - must not be reached
            raise AssertionError("constructor called for a description with wrong provenance")

    args = e2.build_parser().parse_args(["--dataset", "schemabench", "--describer-model", "llama31", "--prompt", "basic",
                                         "--execute", "--confirm-paid", "--data-root", str(root)])
    out = tmp_path / "e2"
    assert e2.execute_one("schemabench", "llama31", "basic", args, tmp_path / "e1", out, Boom()) == 3
    rec = json.loads((out / "0001.json").read_text())
    assert rec["error"].startswith("missing_e1_description:provenance:") and rec["ddl"] == ""
    assert not rio.is_complete_ddl_record(out / "0001.json", rec["id"])
