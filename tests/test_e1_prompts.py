"""Prompt hash verification and message assembly (E1 describers, E2 constructor)."""
import hashlib
import shutil

import pytest

from src import inference_clients as ic
from src import prompt_assets as pa

DDL = "CREATE TABLE `a` (\n  `id` int NOT NULL,\n  PRIMARY KEY (`id`)\n);\nCREATE TABLE `b` (\n  `id` int\n);"


def test_pinned_hashes_match_files():
    actual = pa.verify_all_prompts()
    assert set(actual) == {"basic", "detailed", "constructor"}
    for name, digest in actual.items():
        assert digest == pa.EXPECTED_SHA256[name]
        assert hashlib.sha256(pa.prompt_path(name).read_bytes()).hexdigest() == digest
        assert len(digest) == 64


def test_hash_mismatch_is_detected(tmp_path):
    for name, fn in pa.PROMPT_FILES.items():
        shutil.copy(pa.PROMPT_DIR / fn, tmp_path / fn)
    pa.verify_all_prompts(tmp_path)  # untouched copies verify
    (tmp_path / pa.PROMPT_FILES["basic"]).write_bytes(pa.prompt_path("basic").read_bytes() + b"\n")
    with pytest.raises(pa.PromptHashError):
        pa.load_describer_system("basic", tmp_path)
    with pytest.raises(pa.PromptHashError):
        ic.build_request("llama31", task="schema2text", database="d", ddl=DDL, variant="basic", prompt_dir=tmp_path)


def test_basic_and_detailed_user_messages():
    assert pa.build_basic_user_message("db1", DDL) == f"Database name: db1\n\nDDL:\n{DDL}"
    detailed = pa.build_detailed_user_message("db1", DDL)
    lines = detailed.split("\n")
    assert lines[0] == "Database name: db1" and lines[1] == "Number of tables in schema: 2"
    assert "DDL:" in lines and DDL in detailed
    assert lines[-2].startswith("Task: Write ONE continuous paragraph")
    assert lines[-1].startswith("Do not output any SQL")
    with pytest.raises(ValueError):
        pa.build_describer_user_message("verbose", "db1", DDL)


def test_constructor_user_message():
    msg = pa.build_constructor_user_message("A short description.", "db1")
    assert msg == "Database name: db1\n\nNatural language description:\nA short description."


@pytest.mark.parametrize("variant", pa.DESCRIBER_VARIANTS)
@pytest.mark.parametrize("model", ic.DESCRIBER_KEYS)
def test_describer_request_assembly(model, variant):
    req = ic.build_request(model, task="schema2text", database="db1", ddl=DDL, variant=variant)
    assert req.system == pa.load_describer_system(variant)
    assert req.user == pa.build_describer_user_message(variant, "db1", DDL)
    assert req.temperature == 0.2
    expected = 3072 if ic.MODELS[model].provider == "hf" else (1024 if variant == "basic" else 2048)
    assert req.max_tokens == expected


def test_api_models_truncate_long_ddl_but_open_models_do_not():
    long_ddl = "CREATE TABLE `t` (`c` int);\n" * 5000
    api = ic.build_request("sonnet46", task="schema2text", database="d", ddl=long_ddl, variant="basic")
    hf = ic.build_request("llama31", task="schema2text", database="d", ddl=long_ddl, variant="basic")
    assert "[DDL truncated for length]" in api.user and "[DDL truncated" not in hf.user


def test_constructor_request_and_role_guards():
    req = ic.build_request("gpt4omini", task="constructor", database="db1", nl_text="desc")
    assert req.system == pa.load_constructor_system() and req.max_tokens == 16384
    with pytest.raises(ValueError):
        ic.build_request("gpt4omini", task="schema2text", database="d", ddl=DDL, variant="basic")
    # E3 constructors reuse the five describer keys as Text2Schema constructors.
    e3 = ic.build_request("llama31", task="constructor", database="d", nl_text="x")
    assert e3.max_tokens == ic.E3_HF_MAX_NEW_TOKENS["llama31"]
    assert e3.temperature == ic.E3_CONSTRUCTOR_TEMPERATURE["llama31"]
    with pytest.raises(ValueError):
        ic.build_request("llama31", task="schema2text", database="d", ddl=None, variant="basic")


def test_paid_api_methods_are_disabled(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert isinstance(ic.get_client("sonnet46", dry_run=True), ic.DryRunClient)
    with pytest.raises(ic.ApiMethodsDisabled):
        ic.get_client("gpt54mini", dry_run=False, confirm_paid=False)
    with pytest.raises(ic.ApiMethodsDisabled):
        ic.get_client("gpt54mini", dry_run=False, confirm_paid=True)
    with pytest.raises(ic.ApiMethodsDisabled):
        ic.get_client("gpt4omini", dry_run=False, confirm_paid=True)
