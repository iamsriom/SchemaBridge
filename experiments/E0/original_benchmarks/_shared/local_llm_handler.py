"""Local open-source LLM backend for E0 PaperMethods prompting baselines (transformers + GPU)."""

from __future__ import annotations

import gc
import json
import os
import threading
from pathlib import Path
from typing import Any, Tuple

os.environ.setdefault("PYTORCH_NVML_BASED_CUDA_CHECK", "0")
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

from json_extract import extract_json_from_text

_MODEL_CACHE: dict[str, tuple[Any, Any]] = {}
_LOCK = threading.Lock()

MODEL_ALIASES = {
    "qwen2.5-7b": "Qwen/Qwen2.5-7B-Instruct",
    "qwen2.5-7b-instruct": "Qwen/Qwen2.5-7B-Instruct",
    "llama3.1-8b": "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "llama-3.1-8b": "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "meta-llama-3.1-8b-instruct": "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "codellama-13b": "codellama/CodeLlama-13b-Instruct-hf",
    "codellama13b": "codellama/CodeLlama-13b-Instruct-hf",
    "deepseek-coder-6.7b": "deepseek-ai/deepseek-coder-6.7b-instruct",
    "deepseek-coder": "deepseek-ai/deepseek-coder-6.7b-instruct",
}

# Models that need 4-bit quant on 16GB GPUs
MODELS_4BIT = {
    "codellama/CodeLlama-13b-Instruct-hf",
    "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "meta-llama/Llama-3.1-8B-Instruct",
    # Keep headroom for long agent prompts on T4
    "deepseek-ai/deepseek-coder-6.7b-instruct",
}


def _resolve_model_path(model_name: str) -> str:
    if model_name.startswith("/") or model_name.startswith("."):
        return model_name
    key = model_name.lower().replace("_", "-")
    return MODEL_ALIASES.get(key, model_name)


def _device_index(device: str) -> int:
    if device.startswith("cuda:"):
        return int(device.split(":")[1])
    if device == "cuda":
        return 0
    return -1


def _load_model(model_path: str, device: str):
    cache_key = f"{model_path}@{device}"
    with _LOCK:
        if cache_key in _MODEL_CACHE:
            return _MODEL_CACHE[cache_key]

        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        if tokenizer.pad_token_id is None:
            tokenizer.pad_token_id = tokenizer.eos_token_id

        gpu_idx = _device_index(device)
        use_4bit = model_path in MODELS_4BIT and gpu_idx >= 0

        load_kwargs: dict[str, Any] = {
            "trust_remote_code": True,
            # Avoid SDPA path that crashes on this host's broken NVML:
            # RuntimeError: NVML_SUCCESS == ... nvmlInit_v2_()
            "attn_implementation": "eager",
        }
        if use_4bit:
            load_kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
            )
            load_kwargs["device_map"] = {"": gpu_idx}
        elif gpu_idx >= 0:
            load_kwargs["torch_dtype"] = torch.bfloat16
            load_kwargs["device_map"] = {"": gpu_idx}
        else:
            load_kwargs["torch_dtype"] = torch.float32

        model = AutoModelForCausalLM.from_pretrained(model_path, **load_kwargs)
        if gpu_idx < 0:
            model = model.to(device)
        model.eval()
        _MODEL_CACHE[cache_key] = (tokenizer, model)
        return tokenizer, model


class LocalLLMHandler:
    """Drop-in replacement for api_handler using a local HuggingFace model."""

    def __init__(
        self,
        model_name: str = "Qwen/Qwen2.5-7B-Instruct",
        device: str | None = None,
        max_new_tokens: int = 1500,
        temperature: float = 0.0,
    ):
        self.model_path = _resolve_model_path(model_name)
        if device is None:
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.device = device
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.tokenizer, self.model = _load_model(self.model_path, self.device)
        self.calls: list[dict] = []
        self.call_meta: dict = {}
        self.retry_used = False
        self.last_call: dict = {}
        quant = "4bit" if self.model_path in MODELS_4BIT else "bf16"
        print(f"[LocalLLM] loaded {self.model_path} on {self.device} ({quant})")

    @property
    def _model_device(self):
        return self.model.device

    def prepare_messages(self, messages: list[dict]) -> list[dict]:
        """Suppress DeepSeek's default system text with an empty system message.

        Llama-3.1 still inserts its date lines when the system content is empty,
        so an empty system message is not applied for Llama. CodeLlama injects
        no default system sentence on a user-only prompt; an empty system
        message would add <<SYS>> tags, so it is not applied either.
        Existing system messages are left unchanged.
        """
        work = [dict(m) for m in messages]
        has_system = any(m.get("role") == "system" for m in work)
        if not has_system and "deepseek-coder" in self.model_path:
            work.insert(0, {"role": "system", "content": ""})
        return work

    def render_prompt(self, messages: list[dict]) -> str:
        work = self.prepare_messages(messages)
        if hasattr(self.tokenizer, "apply_chat_template"):
            try:
                prompt = self.tokenizer.apply_chat_template(
                    work, tokenize=False, add_generation_prompt=True
                )
                if isinstance(prompt, str) and prompt.strip():
                    return prompt
            except Exception:
                pass
        return "\n".join((m.get("content") or "") for m in work)

    def _log_jsonl(self, name: str, row: dict) -> None:
        path = Path(os.getenv("LOCAL_LLM_LOG_DIR", str(Path(__file__).resolve().parents[4] / "results" / "baselines" / "logs"))) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()

    def _new_tokens_that_fit(self, n_prompt: int, requested: int) -> int:
        """Cap the continuation so this prompt, and the next one, can be prefilled.

        The prompt is never shortened. Measured on the 16GB GPUs: a 13B model
        with full attention prefills prompts up to 2800 tokens and fails from
        4339 upward. A 4096-token turn makes the next agent's prompt too long,
        so that turn is capped. Smaller models keep the requested budget.
        Returns 0 when this prompt itself cannot be prefilled.
        """
        requested = max(1, int(requested))
        cfg = getattr(self.model, "config", None)
        n_layer = int(getattr(cfg, "num_hidden_layers", 0) or 0)
        n_heads = int(getattr(cfg, "num_attention_heads", 0) or 0)
        n_kv = int(getattr(cfg, "num_key_value_heads", 0) or n_heads)
        # 40 layers x 40 KV heads is CodeLlama-13B. 8B/6.7B models are below this.
        if n_layer * n_kv < 1500:
            return requested
        prefill_limit = 2700
        if n_prompt > prefill_limit:
            return 0
        # The next agent prompt is this completion plus about 2000 tokens of role text.
        completion_cap = prefill_limit - 2000
        room = prefill_limit - int(n_prompt)
        fitted = min(requested, completion_cap, room)
        return fitted if fitted >= 32 else 0

    def generate_chat(self, messages: list[dict], max_new_tokens: int, temperature: float | None = None) -> dict:
        """Greedy generation. No truncation. One OOM retry of the same input."""
        from pathlib import Path

        temp = self.temperature if temperature is None else temperature
        prompt = self.render_prompt(messages)
        inputs = self.tokenizer(prompt, return_tensors="pt")
        n_prompt = int(inputs["input_ids"].shape[-1])
        meta = getattr(self, "call_meta", {}) or {}
        overflow = n_prompt > 12288
        if overflow:
            self._log_jsonl("overflow.jsonl", {
                "sample_id": meta.get("sample_id"),
                "model": self.model_path,
                "method": meta.get("method"),
                "agent_role": meta.get("agent_role"),
                "prompt_tokens": n_prompt,
            })
        inputs = {k: v.to(self._model_device) for k, v in inputs.items()}
        fitted = self._new_tokens_that_fit(n_prompt, int(max_new_tokens))
        gen_kwargs = {
            "max_new_tokens": fitted,
            "do_sample": temp > 0,
            "pad_token_id": self.tokenizer.pad_token_id or self.tokenizer.eos_token_id,
        }
        if temp > 0:
            gen_kwargs["temperature"] = temp

        oom = fitted == 0
        text = ""
        n_new = 0
        last_err = None
        if fitted == 0:
            last_err = RuntimeError(f"prompt of {n_prompt} tokens does not fit free GPU memory")
            self._log_jsonl("oom.jsonl", {
                "sample_id": meta.get("sample_id"),
                "model": self.model_path,
                "method": meta.get("method"),
                "agent_role": meta.get("agent_role"),
                "prompt_tokens": n_prompt,
                "error": str(last_err),
            })
        for attempt in range(2):
            if fitted == 0:
                break
            try:
                with torch.inference_mode():
                    output_ids = self.model.generate(**inputs, **gen_kwargs)
                new_tokens = output_ids[0, inputs["input_ids"].shape[-1]:]
                n_new = int(new_tokens.shape[-1])
                text = self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
                del output_ids
                last_err = None
                break
            except Exception as exc:
                msg = str(exc).lower()
                is_oom = isinstance(exc, torch.cuda.OutOfMemoryError) or "out of memory" in msg
                if not is_oom:
                    raise
                last_err = exc
                oom = True
                try:
                    del output_ids
                except Exception:
                    pass
                gc.collect()
                try:
                    torch.cuda.empty_cache()
                except Exception:
                    pass
                # Keep the full prompt. Halve the continuation that just failed.
                fitted = max(32, int(gen_kwargs["max_new_tokens"]) // 2)
                gen_kwargs["max_new_tokens"] = fitted
                if attempt == 1:
                    self._log_jsonl("oom.jsonl", {
                        "sample_id": meta.get("sample_id"),
                        "model": self.model_path,
                        "method": meta.get("method"),
                        "agent_role": meta.get("agent_role"),
                        "prompt_tokens": n_prompt,
                        "error": str(exc),
                    })
        if last_err is not None:
            text = ""
        hit = n_new == int(gen_kwargs["max_new_tokens"]) and n_new > 0
        role = meta.get("agent_role") or ""
        if not role:
            for m in messages:
                if m.get("role") == "system" and (m.get("content") or "").strip():
                    role = (m.get("content") or "").strip().splitlines()[0][:80]
                    break
        rec = {
            "role": role,
            "input_messages": self.prepare_messages(messages),
            "prompt_tokens": n_prompt,
            "completion_tokens": n_new,
            "hit_token_limit": hit,
            "overflow": overflow,
            "oom": oom and last_err is not None,
            "output": text,
        }
        self.last_call = rec
        self.calls.append(rec)
        self._log_jsonl("calls.jsonl", {**rec, **{k: meta.get(k) for k in ("sample_id", "model", "method")}})
        return rec

    def get_output_multiagent(
        self,
        system_role: str,
        user_input: str,
        max_tokens: int,
        temperature: float = 0,
        frequency_penalty: float = 0,
        presence_penalty: float = 0,
        stop=None,
    ) -> Tuple[str, dict]:
        del frequency_penalty, presence_penalty, stop
        messages = []
        if system_role:
            messages.append({"role": "system", "content": system_role})
        messages.append({"role": "user", "content": user_input})
        budget = int(max_tokens) if max_tokens else int(self.max_new_tokens)
        before = len(self.calls)
        content = ""
        response_json: dict = {}
        for attempt in range(2):
            rec = self.generate_chat(messages, max_new_tokens=budget, temperature=temperature)
            content = rec["output"]
            print("=" * 40)
            print(content)
            response_json = extract_json_from_text(content) if content else {}
            if response_json or rec.get("oom"):
                break
            if attempt == 0:
                print("[LocalLLM] attempt 1: no JSON parsed, retrying")
        self.retry_used = len(self.calls) - before > 1
        self.last_parse = response_json or None
        return content if content else "ERROR.", response_json or {}


def smoke_test(model_name: str = "Qwen/Qwen2.5-7B-Instruct", device: str | None = None) -> bool:
    handler = LocalLLMHandler(model_name=model_name, device=device)
    prompt = (
        "Return ONLY valid JSON with this shape:\n"
        '{"schema":{"Student":{"Attributes":["ID","Name"],"Primary key":["ID"],"Foreign key":{}}}}'
    )
    content, parsed = handler.get_output_multiagent("", prompt, max_tokens=512)
    ok = isinstance(parsed, dict) and "schema" in parsed
    print("[smoke_test]", "PASS" if ok else "FAIL", json.dumps(parsed)[:300])
    return ok
