"""Inference clients (Hugging Face, Anthropic, OpenAI) for E1 schema2text and the E2 constructor.

Safety model
------------
* Importing this module performs no network access and imports no heavy dependency.
* Dry-run is the default everywhere: requests are built and sized, nothing is sent.
* **Dry-run is the default.**  Paid providers (Anthropic ``sonnet46``; OpenAI ``gpt54mini`` and the
  E2 constructor ``gpt4omini``) are opt-in: a real call needs BOTH ``--execute`` and
  ``--confirm-paid`` (``dry_run=False`` and ``confirm_paid=True`` in code).  Without the
  confirmation ``get_client`` raises :class:`PaidCallNotConfirmed`.
* API keys come from the environment ONLY (``ANTHROPIC_API_KEY`` / ``OPENAI_API_KEY``); a missing
  key raises :class:`MissingApiKey`.  Keys are never read from files, printed or stored.
* The ``anthropic`` / ``openai`` SDKs are imported lazily, only when a paid client is constructed.
* Open-weight HF generation is available with ``--execute`` (local GPU only).
* Generated text is written only when ``--out-dir`` is given and it lies outside the repo tree or
  inside an ``outputs/`` directory (git-ignored).

Generation settings (from the original runs): temperature 0.2 for schema2text and constructor;
max new tokens 3072 (open models), 1024 / 2048 (API basic / detailed), 16384 (constructor).
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, Sequence

from . import prompt_assets as pa
from .nl_metrics import sanitize_nl_text

REPO_ROOT = Path(__file__).resolve().parents[1]

TEMPERATURE = 0.2
DDL_MAX_CHARS = {"basic": 60_000, "detailed": 120_000}  # API-run truncation limits

ENV_KEYS = {"anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY"}
PAID_PROVIDERS = frozenset(ENV_KEYS)


@dataclass(frozen=True)
class ModelSpec:
    key: str
    provider: str  # "hf" | "anthropic" | "openai"
    model_id: str
    role: str = "describer"  # "describer" | "constructor"

    @property
    def paid(self) -> bool:
        return self.provider in PAID_PROVIDERS


MODELS: dict[str, ModelSpec] = {
    "codellama13b": ModelSpec("codellama13b", "hf", "codellama/CodeLlama-13b-Instruct-hf"),
    "llama31": ModelSpec("llama31", "hf", "meta-llama/Meta-Llama-3.1-8B-Instruct"),
    "deepseek": ModelSpec("deepseek", "hf", "deepseek-ai/deepseek-coder-6.7b-instruct"),
    "sonnet46": ModelSpec("sonnet46", "anthropic", "claude-sonnet-4-6"),
    "gpt54mini": ModelSpec("gpt54mini", "openai", "gpt-5.4-mini"),
    "gpt4omini": ModelSpec("gpt4omini", "openai", "gpt-4o-mini", role="constructor"),
}
DESCRIBER_KEYS = tuple(k for k, m in MODELS.items() if m.role == "describer")


@dataclass(frozen=True)
class Request:
    """Provider-agnostic chat request."""

    model_key: str
    task: str  # "schema2text" | "constructor"
    system: str
    user: str
    temperature: float
    max_tokens: int

    def approx_input_chars(self) -> int:
        return len(self.system) + len(self.user)


def max_tokens_for(model: ModelSpec, task: str, variant: str | None) -> int:
    if task == "constructor":
        return 16384
    if model.provider == "hf":
        return 3072
    return 1024 if variant == "basic" else 2048


def build_request(
    model_key: str,
    *,
    task: str,
    database: str,
    ddl: str | None = None,
    nl_text: str | None = None,
    variant: str | None = None,
    prompt_dir: Path | None = None,
) -> Request:
    """Build a (hash-verified) request.  Pure: no network, no I/O besides reading prompts."""
    model = MODELS[model_key]
    if task == "schema2text":
        if model.role != "describer":
            raise ValueError(f"{model_key} is a constructor, not a schema2text describer")
        if variant not in pa.DESCRIBER_VARIANTS:
            raise ValueError(f"variant must be one of {pa.DESCRIBER_VARIANTS}")
        if ddl is None:
            raise ValueError("schema2text requires ddl")
        if model.provider != "hf" and len(ddl) > DDL_MAX_CHARS[variant]:
            ddl = ddl[: DDL_MAX_CHARS[variant]] + "\n\n... [DDL truncated for length]"
        system = pa.load_describer_system(variant, prompt_dir)
        user = pa.build_describer_user_message(variant, database, ddl)
    elif task == "constructor":
        if model.role != "constructor":
            raise ValueError(f"{model_key} is not the E2 constructor model")
        if nl_text is None:
            raise ValueError("constructor requires nl_text")
        system = pa.load_constructor_system(prompt_dir)
        user = pa.build_constructor_user_message(nl_text, database)
    else:
        raise ValueError(f"unknown task {task!r}")
    return Request(model_key, task, system, user, TEMPERATURE, max_tokens_for(model, task, variant))


# --------------------------------------------------------------------------- guards

class PaidCallNotConfirmed(RuntimeError):
    pass


class MissingApiKey(RuntimeError):
    pass


class ApiMethodsDisabled(RuntimeError):
    """Legacy exception kept for backwards compatibility.

    Paid API methods are enabled (opt-in) again; nothing in this module raises this any more.
    """


API_METHODS_DISABLED = False  # legacy flag; never used to block anything
API_DISABLED_MESSAGE = (
    "Paid API methods are opt-in: pass --execute together with --confirm-paid and set "
    "ANTHROPIC_API_KEY / OPENAI_API_KEY in the environment."
)


def require_api_key(provider: str) -> str:
    """Return the key from the environment ONLY; never log it.

    Raises :class:`MissingApiKey` (without echoing any value) if the variable is unset or blank.
    """
    if provider not in ENV_KEYS:
        raise ValueError(f"unknown paid provider {provider!r}; expected one of {sorted(ENV_KEYS)}")
    name = ENV_KEYS[provider]
    key = (os.environ.get(name) or "").strip()
    if not key:
        raise MissingApiKey(f"{name} is not set in the environment (needed for provider {provider!r})")
    return key


def _require_confirmation(model: ModelSpec, confirm_paid: bool) -> None:
    if not confirm_paid:
        raise PaidCallNotConfirmed(
            f"{model.model_id} is a paid API model: pass confirm_paid=True (CLI: --execute --confirm-paid)"
        )


def _assert_out_dir_ok(out_dir: Path) -> Path:
    out_dir = Path(out_dir).resolve()
    try:
        rel = out_dir.relative_to(REPO_ROOT)
    except ValueError:
        return out_dir
    if "outputs" not in rel.parts:
        raise ValueError(f"refusing to write generations inside the repo tree outside 'outputs/': {out_dir}")
    return out_dir


# --------------------------------------------------------------------------- clients

class Client(Protocol):
    def generate(self, req: Request) -> str: ...


class DryRunClient:
    """No network, no weights.  Records requests and returns a clearly-marked placeholder."""

    def __init__(self) -> None:
        self.requests: list[Request] = []

    def generate(self, req: Request) -> str:
        self.requests.append(req)
        return f"[DRY-RUN placeholder for {req.model_key}/{req.task}]"


def _retry(fn, max_retries: int = 3):
    last: Exception | None = None
    for attempt in range(max_retries):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001 - provider SDKs raise many types
            last = e
            msg = str(e).lower()
            transient = any(k in msg for k in ("rate", "429", "overloaded", "timeout", "529", "503"))
            if attempt + 1 == max_retries:
                raise
            time.sleep(min(60, 2 ** (attempt + 1)) if transient else 1.0)
    raise last or RuntimeError("retry failed")


class AnthropicClient:
    def __init__(self, model: ModelSpec, *, confirm_paid: bool) -> None:
        _require_confirmation(model, confirm_paid)
        key = require_api_key("anthropic")
        import anthropic  # lazy: only needed for real paid calls

        self.model = model
        self._client = anthropic.Anthropic(api_key=key)

    def generate(self, req: Request) -> str:
        def call() -> str:
            resp = self._client.messages.create(
                model=self.model.model_id,
                max_tokens=req.max_tokens,
                system=req.system,
                messages=[{"role": "user", "content": req.user}],
                temperature=req.temperature,
            )
            text = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text").strip()
            if not text:
                raise ValueError("empty Anthropic response")
            return text

        return _postprocess(req, _retry(call))


class OpenAIClient:
    def __init__(self, model: ModelSpec, *, confirm_paid: bool) -> None:
        _require_confirmation(model, confirm_paid)
        key = require_api_key("openai")
        import openai  # lazy: only needed for real paid calls

        self.model = model
        self._client = openai.OpenAI(api_key=key)

    def generate(self, req: Request) -> str:
        def call() -> str:
            kwargs: dict[str, Any] = dict(
                model=self.model.model_id,
                messages=[
                    {"role": "system", "content": req.system},
                    {"role": "user", "content": req.user},
                ],
                temperature=req.temperature,
            )
            if self.model.model_id.startswith("gpt-5"):
                kwargs["max_completion_tokens"] = req.max_tokens
            else:
                kwargs["max_tokens"] = req.max_tokens
            resp = self._client.chat.completions.create(**kwargs)
            text = (resp.choices[0].message.content or "").strip()
            if not text:
                raise ValueError("empty OpenAI response")
            return text

        return _postprocess(req, _retry(call))


class HFClient:
    """Local open-weight generation via transformers (loads weights on first ``generate``)."""

    def __init__(
        self,
        model: ModelSpec,
        *,
        load_in_4bit: bool = False,
        device_map: str = "auto",
        dtype: str = "float16",
    ) -> None:
        self.model = model
        self.load_in_4bit = load_in_4bit
        self.device_map = device_map
        self.dtype = dtype
        self._tok = None
        self._lm = None

    def _load(self) -> None:
        if self._lm is not None:
            return
        import torch  # lazy
        from transformers import AutoModelForCausalLM, AutoTokenizer

        kwargs: dict[str, Any] = {"device_map": self.device_map}
        if self.load_in_4bit:
            from transformers import BitsAndBytesConfig

            kwargs["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)
        else:
            kwargs["torch_dtype"] = getattr(torch, self.dtype)
        self._tok = AutoTokenizer.from_pretrained(self.model.model_id)
        self._lm = AutoModelForCausalLM.from_pretrained(self.model.model_id, **kwargs)

    def generate(self, req: Request) -> str:
        self._load()
        assert self._tok is not None and self._lm is not None
        messages = [{"role": "system", "content": req.system}, {"role": "user", "content": req.user}]
        try:
            prompt = self._tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        except Exception:  # templates without a system role (e.g. CodeLlama variants)
            merged = [{"role": "user", "content": req.system + "\n\n" + req.user}]
            prompt = self._tok.apply_chat_template(merged, tokenize=False, add_generation_prompt=True)
        inputs = self._tok(prompt, return_tensors="pt", add_special_tokens=False).to(self._lm.device)
        out = self._lm.generate(
            **inputs,
            max_new_tokens=req.max_tokens,
            do_sample=req.temperature > 0,
            temperature=req.temperature,
            pad_token_id=self._tok.eos_token_id,
        )
        new_tokens = out[0][inputs["input_ids"].shape[1]:]
        return _postprocess(req, self._tok.decode(new_tokens, skip_special_tokens=True))


def _postprocess(req: Request, text: str) -> str:
    # NL descriptions are whitespace-normalised; constructor output (JSON) is left verbatim.
    return sanitize_nl_text(text) if req.task == "schema2text" else text.strip()


def get_client(
    model_key: str,
    *,
    dry_run: bool = True,
    confirm_paid: bool = False,
    load_in_4bit: bool = False,
    device_map: str = "auto",
    dtype: str = "float16",
) -> Client:
    """Return a client.  ``dry_run=True`` NEVER touches the network or loads weights.

    Paid Anthropic/OpenAI models with ``dry_run=False`` need ``confirm_paid=True``
    (:class:`PaidCallNotConfirmed` otherwise) and an API key in the environment
    (:class:`MissingApiKey` otherwise).  Open-weight models return a lazily-loading :class:`HFClient`.
    """
    model = MODELS[model_key]
    if dry_run:
        return DryRunClient()
    if model.paid:
        _require_confirmation(model, confirm_paid)
        if model.provider == "anthropic":
            return AnthropicClient(model, confirm_paid=confirm_paid)
        if model.provider == "openai":
            return OpenAIClient(model, confirm_paid=confirm_paid)
        raise ValueError(f"unsupported paid provider {model.provider!r}")
    return HFClient(model, load_in_4bit=load_in_4bit, device_map=device_map, dtype=dtype)


# --------------------------------------------------------------------------- CLI

def _iter_requests(model_key: str, dataset: str, variant: str, data_root: str | None, limit: int | None):
    from .datasets_io import load_dataset

    for rec in load_dataset(dataset, data_root)[: limit or None]:
        yield rec, build_request(model_key, task="schema2text", database=rec.database, ddl=rec.ddl, variant=variant)


def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="schema2text inference (dry-run by default).")
    ap.add_argument("--model", required=True, choices=DESCRIBER_KEYS)
    ap.add_argument("--dataset", required=True, choices=["enterprise145", "schemabench", "rschema"])
    ap.add_argument("--variant", required=True, choices=pa.DESCRIBER_VARIANTS)
    ap.add_argument("--data-root", default=None)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--execute", action="store_true", help="actually generate (default: dry-run, no network)")
    ap.add_argument("--confirm-paid", action="store_true", help="required for Anthropic/OpenAI calls")
    ap.add_argument("--load-in-4bit", action="store_true", help="HF only; needs bitsandbytes")
    ap.add_argument("--out-dir", default=None, help="write NNNN.txt/.json here (outside repo, or under outputs/)")
    args = ap.parse_args(argv)

    model = MODELS[args.model]
    if args.execute and model.paid and not args.confirm_paid:
        ap.error(f"{model.model_id} is a paid API model: add --confirm-paid together with --execute")
    out_dir = _assert_out_dir_ok(Path(args.out_dir)) if args.out_dir else None
    try:
        client = get_client(args.model, dry_run=not args.execute, confirm_paid=args.confirm_paid,
                            load_in_4bit=args.load_in_4bit)
    except (PaidCallNotConfirmed, MissingApiKey) as e:
        ap.error(str(e))

    n = 0
    for rec, req in _iter_requests(args.model, args.dataset, args.variant, args.data_root, args.limit):
        n += 1
        if not args.execute:
            print(f"[dry-run] {rec.dataset} {rec.serial} -> {model.model_id} "
                  f"(~{req.approx_input_chars()} input chars, max_tokens={req.max_tokens}, T={req.temperature})")
            continue
        text = client.generate(req)
        if out_dir:
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / f"{rec.serial}.txt").write_text(text, encoding="utf-8")
            meta = {"serial": rec.serial, "id": rec.schema_id, "model_id": model.model_id,
                    "variant": args.variant, "database": rec.database, "temperature": req.temperature,
                    "nl_text": text}
            (out_dir / f"{rec.serial}.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{'executed' if args.execute else 'dry-run'}: {n} request(s) for {args.model}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
