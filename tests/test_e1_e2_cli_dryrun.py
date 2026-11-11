"""Subprocess smoke tests: every E1/E2 CLI answers --help and the generators dry-run safely."""
import json
import os
import subprocess
import sys

import pytest

from _synthetic import ROOT, build_data_root, load_script

CLIS = [
    "experiments/E1/run.py", "experiments/E1/evaluate.py", "experiments/E1/prepare_dataset.py",
    "experiments/E1/generate_table_vii.py", "experiments/E2/run.py", "experiments/E2/evaluate.py",
    "experiments/E2/generate_table_viii.py", "scripts/plot_e1_e2_figures.py", "scripts/generate_e1_e2_tables.py",
]


def _run(args, **kw):
    env = {k: v for k, v in os.environ.items() if k not in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY")}
    return subprocess.run([sys.executable, *args], capture_output=True, text=True, cwd=ROOT, timeout=120, env=env, **kw)


@pytest.mark.parametrize("cli", CLIS)
def test_help(cli):
    p = _run([cli, "--help"])
    assert p.returncode == 0 and "usage:" in p.stdout


def test_documented_flags_exist_in_help():
    h1 = _run(["experiments/E1/run.py", "--help"]).stdout
    for flag in ("--dataset", "--model", "--prompt", "--data-root", "--out-dir", "--limit", "--skip-existing",
                 "--no-skip-existing", "--device", "--dtype", "--max-tokens", "--dry-run", "--execute",
                 "--confirm-paid", "--resume", "--write-plan"):
        assert flag in h1, flag
    h2 = _run(["experiments/E2/run.py", "--help"]).stdout
    for flag in ("--describer-model", "--e1-pred-dir", "--execute", "--confirm-paid", "--skip-existing", "--limit"):
        assert flag in h2, flag


def test_e1_dry_run_writes_nothing(tmp_path):
    out = tmp_path / "e1out"
    p = _run(["experiments/E1/run.py", "--dataset", "schemabench", "--model", "llama31", "--prompt", "basic",
              "--limit", "2", "--out-dir", str(out)])
    assert p.returncode == 0, p.stderr
    assert "DRY-RUN" in p.stdout and "e1422bc806119c375d89e44759feee44f13eb2717335154ad3c9ca933b6e6c20" in p.stdout
    assert "selected=2" in p.stdout and not out.exists()


def test_e1_dry_run_all_models_and_datasets(tmp_path):
    p = _run(["experiments/E1/run.py", "--dataset", "all", "--model", "all", "--prompt", "detailed", "--limit", "1",
              "--out-dir", str(tmp_path / "x")])
    assert p.returncode == 0, p.stderr
    assert p.stdout.count("[dry-run]") == 15 and not (tmp_path / "x").exists()


def test_e1_write_plan_only_writes_plan(tmp_path):
    out = tmp_path / "plan"
    p = _run(["experiments/E1/run.py", "--dataset", "rschema", "--model", "deepseek", "--prompt", "detailed",
              "--limit", "2", "--out-dir", str(out), "--write-plan"])
    assert p.returncode == 0, p.stderr
    assert [f.name for f in out.iterdir()] == ["dry_run_plan.json"]
    plan = json.loads((out / "dry_run_plan.json").read_text())
    assert plan["n_expected"] == 381 and plan["dry_run"] is True and "nl_text" not in json.dumps(plan)


@pytest.mark.parametrize("model", ["sonnet46", "gpt54mini", "all"])
def test_e1_paid_execute_requires_confirm_paid(model, tmp_path):
    p = _run(["experiments/E1/run.py", "--dataset", "rschema", "--model", model, "--prompt", "basic", "--execute",
              "--limit", "1", "--out-dir", str(tmp_path / "o")])
    assert p.returncode == 2 and "--confirm-paid" in p.stderr and not (tmp_path / "o").exists()


def test_e1_execute_paid_without_key_fails_before_any_call(tmp_path):
    p = _run(["experiments/E1/run.py", "--dataset", "rschema", "--model", "gpt54mini", "--prompt", "basic",
              "--execute", "--confirm-paid", "--limit", "1", "--out-dir", str(tmp_path / "o")])
    assert p.returncode == 2 and "OPENAI_API_KEY" in p.stderr


def test_e1_refuses_tracked_out_dir():
    p = _run(["experiments/E1/run.py", "--dataset", "rschema", "--model", "llama31", "--prompt", "basic",
              "--out-dir", "src"])
    assert p.returncode == 2 and "refusing" in p.stderr


def test_e2_dry_run_validates_payload_without_descriptions(tmp_path):
    p = _run(["experiments/E2/run.py", "--dataset", "rschema", "--describer-model", "llama31", "--prompt", "detailed",
              "--e1-pred-dir", str(tmp_path / "nope"), "--out-dir", str(tmp_path / "o"), "--limit", "2"])
    assert p.returncode == 0, p.stderr
    assert "392a396f7073bc015d206460055f7e3b8a3c94a21ed09c059bc47c13d3884ad4" in p.stdout
    assert "placeholder" in p.stdout and not (tmp_path / "o").exists()


def test_e2_execute_requires_confirm_paid(tmp_path):
    p = _run(["experiments/E2/run.py", "--dataset", "rschema", "--describer-model", "llama31", "--prompt", "basic",
              "--execute", "--out-dir", str(tmp_path / "o")])
    assert p.returncode == 2 and "--confirm-paid" in p.stderr


def _non_strict(mod, monkeypatch):
    """Let a script's dataset loader accept the tiny synthetic corpora (restored after the test)."""
    from src import datasets_io as dio

    monkeypatch.setattr(mod.dio, "load_dataset",
                        lambda name, data_root=None, strict=True: dio.LOADERS[name](data_root, strict=False))


def test_e2_dry_run_uses_real_e1_descriptions(tmp_path, monkeypatch):
    from _synthetic import corpus, write_e1_preds
    from src import datasets_io as dio

    root = build_data_root(tmp_path)
    gold = dio.load_schemabench(root, strict=False)
    s = corpus()["schemas"]
    write_e1_preds(tmp_path / "e1", gold, {g.serial: s[i]["description_good"] for i, g in enumerate(gold)})
    mod = load_script("experiments/E2/run.py", "e2_run")
    _non_strict(mod, monkeypatch)
    args = mod.build_parser().parse_args(["--dataset", "schemabench", "--describer-model", "llama31", "--prompt", "basic",
                                          "--data-root", str(root)])
    plan = mod.dry_run_one("schemabench", "llama31", "basic", args, tmp_path / "e1", tmp_path / "e2out")
    assert plan["n_descriptions_available"] == 3 and plan["n_descriptions_missing"] == 0
    assert plan["first_requests"][0]["max_tokens"] == 16384 and not (tmp_path / "e2out").exists()


def test_e2_execute_pipeline_with_fake_client(tmp_path, monkeypatch):
    """Full execute path with an in-process fake client: no network, no key."""
    from _synthetic import corpus, write_e1_preds
    from src import datasets_io as dio

    root = build_data_root(tmp_path)
    gold = dio.load_schemabench(root, strict=False)
    s = corpus()["schemas"]
    write_e1_preds(tmp_path / "e1", gold, {g.serial: s[i]["description_good"] for i, g in enumerate(gold)})
    mod = load_script("experiments/E2/run.py", "e2_run2")

    class Fake:
        calls = 0

        def generate(self, req):
            Fake.calls += 1
            return "```json\n" + json.dumps({"ddl": "CREATE TABLE `t` (`id` int NOT NULL, PRIMARY KEY (`id`));",
                                             "metadata": {"database": "d", "tables": ["t"], "columns_by_table": {}}}) + "\n```"

    args = mod.build_parser().parse_args(["--dataset", "schemabench", "--describer-model", "llama31", "--prompt", "basic",
                                          "--execute", "--confirm-paid", "--data-root", str(root)])
    out = tmp_path / "e2"
    _non_strict(mod, monkeypatch)  # the strict loader would reject the 3-record synthetic corpus
    assert mod.execute_one("schemabench", "llama31", "basic", args, tmp_path / "e1", out, Fake()) == 0
    assert Fake.calls == 3 and sorted(p.name for p in out.glob("*.json")) == ["0001.json", "0002.json", "0003.json"]
    rec = json.loads((out / "0001.json").read_text())
    assert rec["llm"] == "gpt4omini" and rec["ddl"].startswith("CREATE TABLE") and "error" not in rec
    # resume: nothing re-sent
    assert mod.execute_one("schemabench", "llama31", "basic", args, tmp_path / "e1", out, Fake()) == 0
    assert Fake.calls == 3


def test_backoff_retries_rate_limits_only():
    from src import repro_io as rio

    class Flaky:
        def __init__(self, n, msg):
            self.n, self.msg, self.calls = n, msg, 0

        def generate(self, req):
            self.calls += 1
            if self.calls <= self.n:
                raise RuntimeError(self.msg)
            return "ok"

    sleeps = []
    c = Flaky(2, "Error 429 rate limit")
    assert rio.generate_with_backoff(c, None, sleep=sleeps.append, jitter=lambda: 0.5, base_delay=2.0) == "ok"
    assert c.calls == 3 and sleeps == [2.0, 4.0]
    bad = Flaky(1, "invalid request")
    with pytest.raises(RuntimeError):
        rio.generate_with_backoff(bad, None, sleep=sleeps.append)
    assert bad.calls == 1
    always = Flaky(99, "overloaded")
    with pytest.raises(RuntimeError):
        rio.generate_with_backoff(always, None, max_retries=2, sleep=lambda s: None)
    assert always.calls == 3


def test_e1_execute_pipeline_with_fake_client(tmp_path, monkeypatch):
    root = build_data_root(tmp_path)
    mod = load_script("experiments/E1/run.py", "e1_run")
    _non_strict(mod, monkeypatch)

    class Fake:
        def generate(self, req):
            return "A synthetic description of the schema."

    args = mod.build_parser().parse_args(["--dataset", "rschema", "--model", "llama31", "--prompt", "detailed",
                                          "--execute", "--data-root", str(root)])
    out = tmp_path / "e1"
    assert mod.execute_one("rschema", "llama31", "detailed", args, out, Fake()) == 0
    assert sorted(p.name for p in out.glob("*.json")) == ["0001.json", "0003.json", "0004.json"]  # 518-positions
    rec = json.loads((out / "0003.json").read_text())
    for key in ("text_number", "id", "llm", "model_id", "database", "ddl", "gold_question", "ddl_source",
                "prompt_style", "nl_text"):
        assert key in rec
    assert rec["text_number"] == 3 and rec["prompt_style"] == "schema2text2" and "error" not in rec
    assert (out / "0003.txt").read_text() == rec["nl_text"]
    assert "api_key" not in json.dumps(rec).lower()


def test_table_generators_have_no_baked_in_scores(tmp_path):
    p = _run(["scripts/generate_e1_e2_tables.py", "--out-dir", str(tmp_path / "tex"),
              "--e1-metrics-dir", str(tmp_path / "none"), "--e2-metrics-dir", str(tmp_path / "none")])
    assert p.returncode == 0, p.stderr
    for name in ("table_vii.tex", "table_viii.tex"):
        rows = [ln for ln in (tmp_path / "tex" / name).read_text().splitlines()
                if ln.endswith(r"\\") and "&" in ln and "Dataset" not in ln]
        assert rows
        for ln in rows:
            cells = [c.strip().rstrip("\\").strip() for c in ln.split("&")][3:]  # metric cells + N
            assert all(c == "--" for c in cells), ln  # no local metrics -> every cell is a placeholder


DOC_FILES = [
    "docs/REPRODUCE_E1_E2.md", "docs/REPRODUCIBILITY.md", "docs/experiments/E1.md", "docs/experiments/E2.md",
    "experiments/E1/README.md", "experiments/E2/README.md",
]


def _documented_commands():
    import re

    for rel in DOC_FILES:
        text = (ROOT / rel).read_text(encoding="utf-8")
        for block in re.findall(r"```bash\n(.*?)```", text, re.DOTALL):
            joined = re.sub(r"\\\n\s*", " ", block)
            for line in joined.splitlines():
                m = re.match(r"python3?\s+(\S+\.py)\s*(.*)", line.strip())
                if m and m.group(1) in CLIS:
                    yield rel, m.group(1), re.findall(r"(?<![\w-])(--[a-z0-9][a-z0-9-]*)", m.group(2).split("#")[0])


def test_every_documented_flag_exists_in_cli_help():
    helps: dict[str, str] = {}
    n = 0
    for rel, script, flags in _documented_commands():
        helps.setdefault(script, _run([script, "--help"]).stdout)
        for flag in flags:
            assert flag in helps[script], f"{rel}: {script} has no {flag}"
        n += 1
    assert n >= 15  # the guides really contain runnable commands
