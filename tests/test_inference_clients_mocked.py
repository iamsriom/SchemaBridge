"""Paid-client behaviour with MOCKED anthropic / openai SDKs (no network, no keys, no cost)."""
import socket
import subprocess
import sys
from types import ModuleType, SimpleNamespace

import pytest

from _synthetic import ROOT
from src import inference_clients as ic

DDL = "CREATE TABLE `a` (\n  `id` int NOT NULL,\n  PRIMARY KEY (`id`)\n);"
FAKE_KEY = "test-key-not-real"


class Recorder:
    """Shared call log + scripted behaviour for the fake SDK endpoints."""

    def __init__(self):
        self.calls: list[dict] = []
        self.script: list = []  # items: str (reply text) or Exception; last item repeats
        self.init_kwargs: dict = {}

    def next(self):
        item = self.script[min(len(self.calls) - 1, len(self.script) - 1)]
        if isinstance(item, Exception):
            raise item
        return item


@pytest.fixture()
def rec():
    return Recorder()


@pytest.fixture(autouse=True)
def _no_sleep_no_keys(monkeypatch):
    monkeypatch.setattr(ic.time, "sleep", lambda s: None)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)


@pytest.fixture()
def fake_anthropic(monkeypatch, rec):
    mod = ModuleType("anthropic")

    class Messages:
        def create(self, **kw):
            rec.calls.append(kw)
            text = rec.next()
            return SimpleNamespace(content=[SimpleNamespace(type="thinking", text="ignored"),
                                            SimpleNamespace(type="text", text=text)])

    class Anthropic:
        def __init__(self, **kw):
            rec.init_kwargs.update(kw)
            self.messages = Messages()

    mod.Anthropic = Anthropic
    monkeypatch.setitem(sys.modules, "anthropic", mod)
    return mod


@pytest.fixture()
def fake_openai(monkeypatch, rec):
    mod = ModuleType("openai")

    class Completions:
        def create(self, **kw):
            rec.calls.append(kw)
            text = rec.next()
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=text))])

    class OpenAI:
        def __init__(self, **kw):
            rec.init_kwargs.update(kw)
            self.chat = SimpleNamespace(completions=Completions())

    mod.OpenAI = OpenAI
    monkeypatch.setitem(sys.modules, "openai", mod)
    return mod


def _req(model_key, task="schema2text"):
    if task == "constructor":
        return ic.build_request(model_key, task="constructor", database="db1", nl_text="A description.")
    return ic.build_request(model_key, task="schema2text", database="db1", ddl=DDL, variant="basic")


# --------------------------------------------------------------------------- request shape


def test_anthropic_request_shape(monkeypatch, rec, fake_anthropic):
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    rec.script = ["  A   described schema.  "]
    client = ic.get_client("sonnet46", dry_run=False, confirm_paid=True)
    assert isinstance(client, ic.AnthropicClient) and rec.init_kwargs == {"api_key": FAKE_KEY}
    req = _req("sonnet46")
    out = client.generate(req)
    assert out == "A described schema."  # schema2text output is whitespace-normalised; thinking blocks ignored
    (call,) = rec.calls
    assert call == {
        "model": "claude-sonnet-4-6", "max_tokens": 1024, "system": req.system,
        "messages": [{"role": "user", "content": req.user}], "temperature": 0.2,
    }


def test_openai_gpt5_uses_max_completion_tokens(monkeypatch, rec, fake_openai):
    monkeypatch.setenv("OPENAI_API_KEY", FAKE_KEY)
    rec.script = ["desc"]
    client = ic.get_client("gpt54mini", dry_run=False, confirm_paid=True)
    assert isinstance(client, ic.OpenAIClient) and rec.init_kwargs == {"api_key": FAKE_KEY}
    req = _req("gpt54mini")
    assert client.generate(req) == "desc"
    (call,) = rec.calls
    assert call["model"] == "gpt-5.4-mini" and call["max_completion_tokens"] == 1024 and "max_tokens" not in call
    assert call["temperature"] == req.temperature == 0.2
    assert call["messages"] == [{"role": "system", "content": req.system}, {"role": "user", "content": req.user}]


def test_openai_gpt4o_mini_constructor_uses_max_tokens_and_keeps_json_verbatim(monkeypatch, rec, fake_openai):
    monkeypatch.setenv("OPENAI_API_KEY", FAKE_KEY)
    reply = '{"ddl": "CREATE TABLE t (id int);",\n  "metadata": {}}'
    rec.script = ["\n" + reply + "\n"]
    client = ic.get_client("gpt4omini", dry_run=False, confirm_paid=True)
    req = _req("gpt4omini", "constructor")
    assert client.generate(req) == reply  # constructor output is only stripped
    (call,) = rec.calls
    assert call["model"] == "gpt-4o-mini" and call["max_tokens"] == 16384 and "max_completion_tokens" not in call
    assert call["temperature"] == 0.2


# --------------------------------------------------------------------------- retries / empty


def test_transient_errors_are_retried_then_succeed(monkeypatch, rec, fake_openai):
    monkeypatch.setenv("OPENAI_API_KEY", FAKE_KEY)
    sleeps = []
    monkeypatch.setattr(ic.time, "sleep", sleeps.append)
    rec.script = [RuntimeError("Error 429 rate limit"), RuntimeError("503 overloaded"), "finally"]
    client = ic.get_client("gpt54mini", dry_run=False, confirm_paid=True)
    assert client.generate(_req("gpt54mini")) == "finally"
    assert len(rec.calls) == 3 and sleeps == [2, 4]  # exponential backoff for transient errors


def test_persistent_failure_raises_after_three_attempts(monkeypatch, rec, fake_anthropic):
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    rec.script = [RuntimeError("invalid request")]
    client = ic.get_client("sonnet46", dry_run=False, confirm_paid=True)
    with pytest.raises(RuntimeError, match="invalid request"):
        client.generate(_req("sonnet46"))
    assert len(rec.calls) == 3


@pytest.mark.parametrize("provider,model,env", [("anthropic", "sonnet46", "ANTHROPIC_API_KEY"),
                                                ("openai", "gpt54mini", "OPENAI_API_KEY")])
@pytest.mark.parametrize("blank", ["", "   "])
def test_empty_response_is_an_error(monkeypatch, rec, fake_anthropic, fake_openai, provider, model, env, blank):
    monkeypatch.setenv(env, FAKE_KEY)
    rec.script = [blank]
    client = ic.get_client(model, dry_run=False, confirm_paid=True)
    with pytest.raises(ValueError, match="empty .* response"):
        client.generate(_req(model))
    assert len(rec.calls) == 3  # empty replies are retried like any other failure


def test_openai_none_content_is_empty(monkeypatch, rec, fake_openai):
    monkeypatch.setenv("OPENAI_API_KEY", FAKE_KEY)
    rec.script = [None, "second try"]
    client = ic.get_client("gpt54mini", dry_run=False, confirm_paid=True)
    assert client.generate(_req("gpt54mini")) == "second try" and len(rec.calls) == 2


# --------------------------------------------------------------------------- gates


@pytest.mark.parametrize("model", ["sonnet46", "gpt54mini", "gpt4omini"])
def test_dry_run_touches_no_sdk_no_network_no_key(monkeypatch, model):
    monkeypatch.setitem(sys.modules, "anthropic", None)  # import would raise ImportError
    monkeypatch.setitem(sys.modules, "openai", None)

    def no_net(*a, **k):
        raise AssertionError("network access in dry-run")

    monkeypatch.setattr(socket.socket, "connect", no_net)
    monkeypatch.setattr(socket, "create_connection", no_net)
    client = ic.get_client(model, dry_run=True)
    assert isinstance(client, ic.DryRunClient)
    req = _req(model, "constructor") if model == "gpt4omini" else _req(model)
    assert "DRY-RUN" in client.generate(req) and client.requests == [req]
    # dry-run ignores confirm_paid too
    assert isinstance(ic.get_client(model, dry_run=True, confirm_paid=True), ic.DryRunClient)


@pytest.mark.parametrize("model,env", [("sonnet46", "ANTHROPIC_API_KEY"), ("gpt54mini", "OPENAI_API_KEY"),
                                       ("gpt4omini", "OPENAI_API_KEY")])
def test_confirm_paid_gates_paid_clients(monkeypatch, rec, fake_anthropic, fake_openai, model, env):
    monkeypatch.setenv(env, FAKE_KEY)  # a key alone is not enough
    with pytest.raises(ic.PaidCallNotConfirmed):
        ic.get_client(model, dry_run=False)
    with pytest.raises(ic.PaidCallNotConfirmed):
        ic.get_client(model, dry_run=False, confirm_paid=False)
    spec = ic.MODELS[model]
    cls = ic.AnthropicClient if spec.provider == "anthropic" else ic.OpenAIClient
    with pytest.raises(ic.PaidCallNotConfirmed):
        cls(spec, confirm_paid=False)  # direct construction is gated as well
    assert rec.init_kwargs == {} and rec.calls == []  # the SDK was never instantiated
    assert isinstance(ic.get_client(model, dry_run=False, confirm_paid=True), cls)


@pytest.mark.parametrize("model", ["sonnet46", "gpt54mini", "gpt4omini"])
def test_missing_key_is_reported_without_touching_sdk(monkeypatch, rec, fake_anthropic, fake_openai, model):
    with pytest.raises(ic.MissingApiKey) as ei:
        ic.get_client(model, dry_run=False, confirm_paid=True)
    assert ic.ENV_KEYS[ic.MODELS[model].provider] in str(ei.value)
    assert rec.init_kwargs == {} and rec.calls == []


def test_sdk_imported_lazily():
    """A fresh interpreter importing the module must not pull in either SDK (or torch / transformers)."""
    code = ("import sys; import src.inference_clients as ic; "
            "bad = [m for m in ('anthropic', 'openai', 'torch', 'transformers') if m in sys.modules]; "
            "assert not bad, bad")
    p = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True, timeout=60)
    assert p.returncode == 0, p.stderr


def test_hf_client_is_lazy_and_needs_no_confirmation():
    client = ic.get_client("llama31", dry_run=False)
    assert isinstance(client, ic.HFClient) and client._lm is None  # no weights loaded until generate()


def test_legacy_disabled_api_is_kept_but_never_blocks(monkeypatch):
    assert ic.API_METHODS_DISABLED is False and issubclass(ic.ApiMethodsDisabled, RuntimeError)
    monkeypatch.setenv("OPENAI_API_KEY", FAKE_KEY)
    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=lambda **kw: SimpleNamespace()))
    assert isinstance(ic.get_client("gpt54mini", dry_run=False, confirm_paid=True), ic.OpenAIClient)


def test_secret_never_appears_in_errors(monkeypatch, rec, fake_openai):
    monkeypatch.setenv("OPENAI_API_KEY", FAKE_KEY)
    rec.script = [RuntimeError("bad request")]
    client = ic.get_client("gpt54mini", dry_run=False, confirm_paid=True)
    with pytest.raises(RuntimeError) as ei:
        client.generate(_req("gpt54mini"))
    assert FAKE_KEY not in str(ei.value)
    with pytest.raises(ic.MissingApiKey) as ei2:
        monkeypatch.delenv("OPENAI_API_KEY")
        ic.require_api_key("openai")
    assert FAKE_KEY not in str(ei2.value)
