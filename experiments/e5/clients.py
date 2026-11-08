"""LLM clients for E5 with usage/latency logging. Never prints secrets."""

from __future__ import annotations

import json
import os
import re
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

from .cost_tracker import SpendTracker, compute_cost_usd, load_pricing
from .prompts_e5 import (
    CONSTRUCTOR_SYSTEM,
    constructor_user_content,
    describer_user_content,
    system_for_describer,
)

ROOT = Path(__file__).resolve().parents[2]


@dataclass
class CallResult:
    ok: bool
    text: str = ""
    model_id: str = ""
    provider: str = ""
    input_tokens: int | None = None
    output_tokens: int | None = None
    cached_tokens: int = 0
    reasoning_tokens: int | None = None
    latency_s: float | None = None
    retry_count: int = 0
    retry_latency_s: float = 0.0
    cost_usd: float | None = None
    cost_basis: str = "unavailable"
    error: str | None = None
    truncated: bool = False
    raw_finish_reason: str | None = None
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parsed_json: dict | None = None
    ddl: str = ""
    metadata: dict | None = None
    reused: bool = False
    cache_key: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        return d


def _read_secret_file(path: Path) -> str | None:
    if path.is_file():
        t = path.read_text(encoding="utf-8").strip()
        return t or None
    return None


def openai_api_key() -> str | None:
    return os.environ.get("OPENAI_API_KEY") or _read_secret_file(Path("/data/openai_api.txt"))


def anthropic_api_key() -> str | None:
    return (
        os.environ.get("ANTHROPIC_API_KEY")
        or _read_secret_file(Path("/data/anthropic.txt"))
        or _read_secret_file(Path("/data/anthropic_api.txt"))
    )


def probe_openai(model_id: str = "gpt-4o-mini") -> tuple[bool, str]:
    key = openai_api_key()
    if not key:
        return False, "OPENAI_API_KEY missing"
    try:
        from openai import OpenAI

        client = OpenAI(api_key=key)
        kwargs: dict[str, Any] = {
            "model": model_id,
            "messages": [{"role": "user", "content": "Reply OK"}],
        }
        try:
            client.chat.completions.create(**kwargs, max_completion_tokens=8)
        except Exception:
            client.chat.completions.create(**kwargs, max_tokens=8)
        return True, "ok"
    except Exception as e:  # noqa: BLE001
        return False, f"{type(e).__name__}: {e}"


def probe_anthropic(model_id: str = "claude-sonnet-4-6") -> tuple[bool, str]:
    key = anthropic_api_key()
    if not key:
        return False, "ANTHROPIC_API_KEY missing"
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=key)
        client.messages.create(
            model=model_id,
            max_tokens=16,
            messages=[{"role": "user", "content": "Reply OK"}],
        )
        return True, "ok"
    except Exception as e:  # noqa: BLE001
        return False, f"{type(e).__name__}: {e}"


def extract_json_from_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if not m:
            raise
        return json.loads(m.group(0))


class OpenAIChatClient:
    def __init__(self, tracker: SpendTracker, pricing: dict | None = None):
        self.tracker = tracker
        self.pricing = pricing or load_pricing()
        self._client = None
        self.available, self.unavailable_reason = probe_openai()
        if self.available:
            from openai import OpenAI

            self._client = OpenAI(api_key=openai_api_key())

    def chat(
        self,
        *,
        model_id: str,
        system: str,
        user: str,
        temperature: float = 0.2,
        max_tokens: int = 4096,
        max_retries: int = 2,
        expect_json: bool = False,
        estimate_tokens: tuple[int, int] = (2000, 1500),
    ) -> CallResult:
        if not self.available or self._client is None:
            return CallResult(
                ok=False,
                model_id=model_id,
                provider="openai",
                error=f"OpenAI unavailable: {self.unavailable_reason}",
                cost_basis="n/a",
            )
        est = compute_cost_usd(model_id, estimate_tokens[0], estimate_tokens[1], self.pricing) or 0.0
        # Include retries in affordability check.
        if not self.tracker.can_afford(est * (max_retries + 1)):
            return CallResult(
                ok=False,
                model_id=model_id,
                provider="openai",
                error=f"Spend cap would be exceeded (est ${est:.4f} x retries; remaining ${self.tracker.remaining():.4f})",
                cost_basis="capped",
            )

        last_err = None
        retry_lat = 0.0
        total_cost = 0.0
        for attempt in range(max_retries + 1):
            t0 = time.perf_counter()
            try:
                kwargs: dict[str, Any] = {
                    "model": model_id,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    "temperature": temperature,
                }
                # gpt-5* often rejects max_tokens in favor of max_completion_tokens
                try:
                    resp = self._client.chat.completions.create(**kwargs, max_completion_tokens=max_tokens)
                except Exception:
                    resp = self._client.chat.completions.create(**kwargs, max_tokens=max_tokens)
                lat = time.perf_counter() - t0
                if attempt:
                    retry_lat += lat
                text = (resp.choices[0].message.content or "").strip()
                usage = resp.usage
                in_tok = getattr(usage, "prompt_tokens", None) if usage else None
                out_tok = getattr(usage, "completion_tokens", None) if usage else None
                cached = 0
                reasoning = None
                if usage is not None:
                    details = getattr(usage, "prompt_tokens_details", None)
                    if details is not None:
                        cached = int(getattr(details, "cached_tokens", 0) or 0)
                    cdet = getattr(usage, "completion_tokens_details", None)
                    if cdet is not None:
                        reasoning = getattr(cdet, "reasoning_tokens", None)
                finish = getattr(resp.choices[0], "finish_reason", None)
                cost = compute_cost_usd(model_id, in_tok, out_tok, self.pricing, cached_tokens=cached)
                if cost is not None:
                    total_cost += cost
                    self.tracker.charge(cost, {"model_id": model_id, "execution": "openai_chat"})
                parsed = None
                ddl = ""
                meta = None
                if expect_json:
                    parsed = extract_json_from_response(text)
                    if not isinstance(parsed, dict) or "ddl" not in parsed:
                        raise ValueError("JSON missing ddl")
                    ddl = parsed.get("ddl") or ""
                    meta = parsed.get("metadata") or {}
                return CallResult(
                    ok=True,
                    text=text if not expect_json else json.dumps(parsed),
                    model_id=model_id,
                    provider="openai",
                    input_tokens=in_tok,
                    output_tokens=out_tok,
                    cached_tokens=cached,
                    reasoning_tokens=reasoning,
                    latency_s=lat + retry_lat,
                    retry_count=attempt,
                    retry_latency_s=retry_lat,
                    cost_usd=total_cost if total_cost else cost,
                    cost_basis="provider_usage",
                    truncated=(finish == "length"),
                    raw_finish_reason=finish,
                    parsed_json=parsed,
                    ddl=ddl,
                    metadata=meta,
                )
            except Exception as e:  # noqa: BLE001
                last_err = e
                lat = time.perf_counter() - t0
                if attempt:
                    retry_lat += lat
                else:
                    retry_lat += 0.0
                if attempt >= max_retries:
                    break
        return CallResult(
            ok=False,
            model_id=model_id,
            provider="openai",
            error=f"{type(last_err).__name__}: {last_err}",
            retry_count=max_retries,
            retry_latency_s=retry_lat,
            cost_usd=total_cost or None,
            cost_basis="provider_usage" if total_cost else "n/a",
        )


class AnthropicChatClient:
    def __init__(self, tracker: SpendTracker, pricing: dict | None = None):
        self.tracker = tracker
        self.pricing = pricing or load_pricing()
        self._client = None
        self.available, self.unavailable_reason = probe_anthropic()
        if self.available:
            import anthropic

            self._client = anthropic.Anthropic(api_key=anthropic_api_key())

    def chat(
        self,
        *,
        model_id: str = "claude-sonnet-4-6",
        system: str,
        user: str,
        temperature: float = 0.2,
        max_tokens: int = 4096,
        max_retries: int = 2,
        expect_json: bool = False,
        estimate_tokens: tuple[int, int] = (2000, 1500),
    ) -> CallResult:
        if not self.available or self._client is None:
            return CallResult(
                ok=False,
                model_id=model_id,
                provider="anthropic",
                error=f"Anthropic unavailable: {self.unavailable_reason}",
                cost_basis="n/a",
            )
        est = compute_cost_usd(model_id, estimate_tokens[0], estimate_tokens[1], self.pricing) or 0.0
        if not self.tracker.can_afford(est * (max_retries + 1)):
            return CallResult(
                ok=False,
                model_id=model_id,
                provider="anthropic",
                error=(
                    f"Spend cap would be exceeded (est ${est:.4f} x retries; "
                    f"remaining ${self.tracker.remaining():.4f})"
                ),
                cost_basis="capped",
            )

        last_err = None
        retry_lat = 0.0
        total_cost = 0.0
        for attempt in range(max_retries + 1):
            t0 = time.perf_counter()
            try:
                # Anthropic SDK >=2.6 / Claude Sonnet 4.6: temperature is not an
                # accepted Messages.create argument on this deployment. Effective
                # sampling uses the provider default; requested temperature is logged only.
                _ = temperature  # requested 0.2 from E1/E2 config; not sent
                resp = self._client.messages.create(
                    model=model_id,
                    max_tokens=max_tokens,
                    system=system,
                    messages=[{"role": "user", "content": user}],
                )
                lat = time.perf_counter() - t0
                if attempt:
                    retry_lat += lat
                text = "".join(getattr(b, "text", "") or "" for b in (resp.content or [])).strip()
                in_tok = int(getattr(resp.usage, "input_tokens", 0) or 0)
                out_tok = int(getattr(resp.usage, "output_tokens", 0) or 0)
                cached = int(getattr(resp.usage, "cache_read_input_tokens", 0) or 0)
                cost = compute_cost_usd(
                    model_id, in_tok, out_tok, self.pricing, cached_tokens=cached
                )
                if cost is not None:
                    total_cost += cost
                    self.tracker.charge(cost, {"model_id": model_id, "execution": "anthropic_chat"})
                finish = getattr(resp, "stop_reason", None)
                parsed = None
                ddl = ""
                meta = None
                if expect_json:
                    parsed = extract_json_from_response(text)
                    if not isinstance(parsed, dict) or "ddl" not in parsed:
                        raise ValueError("JSON missing ddl")
                    ddl = parsed.get("ddl") or ""
                    meta = parsed.get("metadata") or {}
                return CallResult(
                    ok=True,
                    text=text if not expect_json else json.dumps(parsed),
                    model_id=model_id,
                    provider="anthropic",
                    input_tokens=in_tok,
                    output_tokens=out_tok,
                    cached_tokens=cached,
                    latency_s=lat + retry_lat,
                    retry_count=attempt,
                    retry_latency_s=retry_lat,
                    cost_usd=total_cost if total_cost else cost,
                    cost_basis="provider_usage",
                    truncated=(finish == "max_tokens"),
                    raw_finish_reason=finish,
                    parsed_json=parsed,
                    ddl=ddl,
                    metadata=meta,
                )
            except Exception as e:  # noqa: BLE001
                last_err = e
                lat = time.perf_counter() - t0
                retry_lat += lat
                if attempt >= max_retries:
                    break
        return CallResult(
            ok=False,
            model_id=model_id,
            provider="anthropic",
            error=f"{type(last_err).__name__}: {last_err}",
            retry_count=max_retries,
            retry_latency_s=retry_lat,
            cost_usd=total_cost or None,
            cost_basis="provider_usage" if total_cost else "n/a",
        )


class LocalDeepSeekClient:
    """Local HF DeepSeek-Coder-6.7B-Instruct (exact archived model id)."""

    def __init__(self, tracker: SpendTracker, pricing: dict | None = None, device_map: str = "auto"):
        self.tracker = tracker
        self.pricing = pricing or load_pricing()
        self.model_id = "deepseek-ai/deepseek-coder-6.7b-instruct"
        self.snapshot = Path(
            "/data/LLM4DBdesign-main/agent/models--deepseek-ai--deepseek-coder-6.7b-instruct/"
            "snapshots/e5d64addd26a6a1db0f9b863abf6ee3141936807"
        )
        self.device_map = device_map
        self._model = None
        self._tokenizer = None
        self.available = self.snapshot.exists()
        self.unavailable_reason = None if self.available else f"snapshot missing: {self.snapshot}"

    def _ensure_tokenizer(self) -> None:
        if self._tokenizer is not None:
            return
        from transformers import AutoTokenizer

        self._tokenizer = AutoTokenizer.from_pretrained(str(self.snapshot), trust_remote_code=True)

    def _ensure(self) -> None:
        if self._model is not None:
            return
        import torch
        from transformers import AutoModelForCausalLM

        self._ensure_tokenizer()
        self._model = AutoModelForCausalLM.from_pretrained(
            str(self.snapshot),
            trust_remote_code=True,
            torch_dtype=torch.float16,
            device_map=self.device_map,
        )
        self._model.eval()

    @staticmethod
    def _sanitize_nl(text: str) -> str:
        if not text:
            return text
        text = text.replace("\u0120", " ")
        text = text.replace("Ċ", "\n").replace("▁", " ")
        lines = [" ".join(line.split()) for line in text.splitlines()]
        return "\n".join(ln for ln in lines if ln).strip()

    def generate(
        self,
        *,
        system: str,
        user: str,
        temperature: float = 0.2,
        max_new_tokens: int = 3072,
        top_p: float = 1.0,
    ) -> CallResult:
        if not self.available:
            return CallResult(
                ok=False,
                model_id=self.model_id,
                provider="huggingface_local",
                error=self.unavailable_reason,
                cost_basis="n/a",
            )
        try:
            self._ensure()
            assert self._tokenizer is not None and self._model is not None
            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ]
            prompt = None
            if hasattr(self._tokenizer, "apply_chat_template") and getattr(
                self._tokenizer, "chat_template", None
            ):
                try:
                    prompt = self._tokenizer.apply_chat_template(
                        messages, tokenize=False, add_generation_prompt=True
                    )
                except Exception:
                    prompt = None
            if prompt is None:
                combined = f"{system}\n\n{user}"
                prompt = f"<s>[INST] {combined} [/INST]\n"
            inputs = self._tokenizer(
                prompt, return_tensors="pt", truncation=True, max_length=8192
            )
            device = next(self._model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            in_tok = int(inputs["input_ids"].shape[-1])
            t0 = time.perf_counter()
            import torch

            with torch.inference_mode():
                out = self._model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    temperature=max(temperature, 1e-5),
                    top_p=top_p,
                    pad_token_id=self._tokenizer.pad_token_id or self._tokenizer.eos_token_id,
                )
            lat = time.perf_counter() - t0
            gen = out[0][in_tok:]
            out_tok = int(gen.shape[-1])
            text = self._sanitize_nl(
                self._tokenizer.decode(
                    gen, skip_special_tokens=True, clean_up_tokenization_spaces=False
                ).strip()
            )
            truncated = out_tok >= max_new_tokens
            return CallResult(
                ok=True,
                text=text,
                model_id=self.model_id,
                provider="huggingface_local",
                input_tokens=in_tok,
                output_tokens=out_tok,
                latency_s=lat,
                cost_usd=None,
                cost_basis="local_gpu_unmetered",
                truncated=truncated,
                raw_finish_reason="length" if truncated else "stop",
            )
        except Exception as e:  # noqa: BLE001
            return CallResult(
                ok=False,
                model_id=self.model_id,
                provider="huggingface_local",
                error=f"{type(e).__name__}: {e}",
                cost_basis="n/a",
            )

    def count_tokens(self, text: str) -> int:
        self._ensure_tokenizer()
        assert self._tokenizer is not None
        return len(self._tokenizer.encode(text))


def estimate_openai_tokens(text: str, model_hint: str = "gpt-4o-mini") -> int:
    try:
        import tiktoken

        try:
            enc = tiktoken.encoding_for_model(model_hint)
        except Exception:
            enc = tiktoken.get_encoding("o200k_base")
        return len(enc.encode(text))
    except Exception:
        return max(1, len(text) // 4)


def describe_schema(
    client_kind: str,
    clients: dict[str, Any],
    *,
    database: str,
    ddl: str,
    prompt_variant: str,
) -> CallResult:
    system = system_for_describer(prompt_variant)
    user = describer_user_content(database, ddl, prompt_variant)
    if client_kind == "deepseek":
        return clients["deepseek"].generate(system=system, user=user, temperature=0.2, max_new_tokens=3072)
    if client_kind == "gpt_5_4_mini":
        return clients["openai"].chat(
            model_id="gpt-5.4-mini",
            system=system,
            user=user,
            temperature=0.2,
            max_tokens=3072,
        )
    if client_kind == "claude_sonnet_4_6":
        return clients["anthropic"].chat(
            model_id="claude-sonnet-4-6",
            system=system,
            user=user,
            temperature=0.2,
            max_tokens=3072,
        )
    raise ValueError(client_kind)


def construct_schema(
    client_kind: str,
    clients: dict[str, Any],
    *,
    nl_text: str,
    database: str,
    text_number: int | None = None,
) -> CallResult:
    system = CONSTRUCTOR_SYSTEM
    user = constructor_user_content(nl_text, database, text_number)
    if client_kind == "gpt_4o_mini":
        return clients["openai"].chat(
            model_id="gpt-4o-mini",
            system=system,
            user=user,
            temperature=0.2,
            max_tokens=4096,
            expect_json=True,
        )
    if client_kind == "gpt_5_4_mini":
        return clients["openai"].chat(
            model_id="gpt-5.4-mini",
            system=system,
            user=user,
            temperature=0.2,
            max_tokens=4096,
            expect_json=True,
        )
    if client_kind == "claude_sonnet_4_6":
        return clients["anthropic"].chat(
            model_id="claude-sonnet-4-6",
            system=system,
            user=user,
            temperature=0.2,
            max_tokens=4096,
            expect_json=True,
        )
    raise ValueError(client_kind)
