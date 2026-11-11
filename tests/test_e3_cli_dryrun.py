"""Subprocess smoke tests for E3 CLIs (dry-run, help, paid-API isolation)."""
from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

from _synthetic import ROOT, build_data_root, corpus, load_script, write_e1_preds
from src import datasets_io as dio
from src import inference_clients as ic
from src import repro_io as rio

CLIS = [
    "experiments/E3/run.py",
    "experiments/E3/evaluate.py",
    "experiments/E3/prepare_inputs.py",
    "experiments/E3/validate_inputs.py",
    "experiments/E3/generate_table_ix.py",
]


def _run(args, **kw):
    env = {k: v for k, v in os.environ.items() if k not in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY")}
    return subprocess.run([sys.executable, *args], capture_output=True, text=True, cwd=ROOT, timeout=120, env=env, **kw)


@pytest.mark.parametrize("cli", CLIS)
def test_help(cli):
    p = _run([cli, "--help"])
    assert p.returncode == 0 and "usage:" in p.stdout


def test_documented_flags_exist_in_help():
    h = _run(["experiments/E3/run.py", "--help"]).stdout
    for flag in ("--dataset", "--constructor", "--descriptions-dir", "--out-dir", "--limit",
                 "--skip-existing", "--dry-run", "--execute", "--confirm-paid", "--write-plan",
                 "--load-in-4bit", "--schema-id"):
        assert flag in h, flag


def test_e3_dry_run_validates_payload_without_descriptions(tmp_path):
    p = _run(["experiments/E3/run.py", "--dataset", "rschema", "--constructor", "llama31",
              "--descriptions-dir", str(tmp_path / "nope"), "--out-dir", str(tmp_path / "o"), "--limit", "2"])
    assert p.returncode == 0, p.stderr
    assert "392a396f7073bc015d206460055f7e3b8a3c94a21ed09c059bc47c13d3884ad4" in p.stdout
    assert "placeholder" in p.stdout and not (tmp_path / "o").exists()


@pytest.mark.parametrize("ctor", ["sonnet46", "gpt54mini", "all"])
def test_e3_paid_execute_is_disabled(ctor, tmp_path):
    p = _run(["experiments/E3/run.py", "--dataset", "rschema", "--constructor", ctor, "--execute",
              "--limit", "1", "--out-dir", str(tmp_path / "o"),
              "--descriptions-dir", str(tmp_path / "d")])
    assert p.returncode == 2 and "Paid API methods are disabled" in p.stderr
    assert not (tmp_path / "o").exists()


def test_e3_dry_run_uses_fixed_descriptions(tmp_path, monkeypatch):
    root = build_data_root(tmp_path)
    gold = dio.load_schemabench(root, strict=False)
    s = corpus()["schemas"]
    write_e1_preds(tmp_path / "e1", gold, {g.serial: s[i]["description_good"] for i, g in enumerate(gold)})
    mod = load_script("experiments/E3/run.py", "e3_run")

    from src import datasets_io as dio_mod
    monkeypatch.setattr(mod.dio, "load_dataset",
                        lambda name, data_root=None, strict=True: dio_mod.LOADERS[name](data_root, strict=False))
    args = mod.build_parser().parse_args([
        "--dataset", "schemabench", "--constructor", "deepseek",
        "--data-root", str(root),
    ])
    plan = mod.dry_run_one("schemabench", "deepseek", args, tmp_path / "e1", tmp_path / "e3out")
    assert plan["n_descriptions_available"] == 3 and plan["n_descriptions_missing"] == 0
    assert plan["first_requests"][0]["max_tokens"] == ic.E3_HF_MAX_NEW_TOKENS["deepseek"]
    assert plan["first_requests"][0]["temperature"] == ic.E3_CONSTRUCTOR_TEMPERATURE["deepseek"]
    assert not (tmp_path / "e3out").exists()


def test_e3_execute_pipeline_with_fake_client(tmp_path, monkeypatch):
    root = build_data_root(tmp_path)
    gold = dio.load_schemabench(root, strict=False)
    s = corpus()["schemas"]
    write_e1_preds(tmp_path / "e1", gold, {g.serial: s[i]["description_good"] for i, g in enumerate(gold)})
    mod = load_script("experiments/E3/run.py", "e3_run_exec")
    from src import datasets_io as dio_mod
    monkeypatch.setattr(mod.dio, "load_dataset",
                        lambda name, data_root=None, strict=True: dio_mod.LOADERS[name](data_root, strict=False))

    class Fake:
        calls = 0

        def generate(self, req):
            self.calls += 1
            ddl = s[0]["ddl"]
            return json.dumps({"ddl": ddl, "metadata": {}})

    client = Fake()
    args = mod.build_parser().parse_args([
        "--dataset", "schemabench", "--constructor", "llama31",
        "--data-root", str(root), "--no-skip-existing",
    ])
    out = tmp_path / "e3out"
    n_err = mod.execute_one("schemabench", "llama31", args, tmp_path / "e1", out, client)
    assert n_err == 0 and client.calls == 3
    rec = json.loads((out / f"{gold[0].serial}.json").read_text())
    assert rec["llm"] == "llama31" and rec["source_schema2text_llm"] == "gpt54mini"
    assert rec["nl_sha256"] == rio.sha256_text(rec["nl_text"])
    assert (out / f"{gold[0].serial}.txt").is_file()


def test_e3_resume_skips_complete(tmp_path, monkeypatch):
    root = build_data_root(tmp_path)
    gold = dio.load_schemabench(root, strict=False)
    s = corpus()["schemas"]
    write_e1_preds(tmp_path / "e1", gold, {g.serial: "fixed" for g in gold})
    mod = load_script("experiments/E3/run.py", "e3_run_resume")
    from src import datasets_io as dio_mod
    monkeypatch.setattr(mod.dio, "load_dataset",
                        lambda name, data_root=None, strict=True: dio_mod.LOADERS[name](data_root, strict=False))
    out = tmp_path / "e3out"
    out.mkdir()
    # Pre-seed one complete reconstruction
    first = gold[0]
    (out / f"{first.serial}.json").write_text(json.dumps({
        "id": first.schema_id, "ddl": s[0]["ddl"], "metadata": {}, "nl_text": "fixed",
        "nl_sha256": rio.sha256_text("fixed"),
    }))
    client = type("Fake", (), {"calls": 0})()
    def _gen(req):
        client.calls += 1
        return json.dumps({"ddl": s[0]["ddl"], "metadata": {}})
    client.generate = _gen
    args = mod.build_parser().parse_args([
        "--dataset", "schemabench", "--constructor", "codellama13b", "--data-root", str(root),
    ])
    mod.execute_one("schemabench", "codellama13b", args, tmp_path / "e1", out, client)
    # One skipped + two constructed
    assert client.calls == 2


def test_e3_prepare_inputs_dry(tmp_path):
    p = _run(["experiments/E3/prepare_inputs.py", "--dataset", "rschema", "--limit", "2",
              "--descriptions-dir", str(tmp_path / "missing")])
    assert p.returncode == 1  # missing descriptions -> incomplete
    assert "gpt54mini" in p.stdout and "NOT FOUND" in p.stdout


def test_e3_generate_table_ix_empty(tmp_path):
    out = tmp_path / "outputs" / "latex_generated"
    p = _run(["experiments/E3/generate_table_ix.py", "--metrics-dir", str(tmp_path / "empty"),
              "--out-dir", str(out)])
    assert p.returncode == 0, p.stderr
    tex = (out / "table_ix.tex").read_text()
    assert r"\label{tab:e3_overall}" in tex and "--" in tex


def test_e3_constructor_decoding_defaults():
    for key, tok in ic.E3_HF_MAX_NEW_TOKENS.items():
        req = ic.build_request(key, task="constructor", database="db", nl_text="hello")
        assert req.max_tokens == tok
        assert req.temperature == ic.E3_CONSTRUCTOR_TEMPERATURE[key]
    for key, tok in ic.E3_API_MAX_TOKENS.items():
        req = ic.build_request(key, task="constructor", database="db", nl_text="hello")
        assert req.max_tokens == tok
        assert req.temperature == ic.E3_CONSTRUCTOR_TEMPERATURE[key]
