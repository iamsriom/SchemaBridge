"""Load compatible E1/E2 DeepSeek-basic archives for E5 reuse."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .clients import estimate_openai_tokens
from .cost_tracker import compute_cost_usd, load_pricing
from .prompts_e5 import CONSTRUCTOR_SYSTEM, BASIC_SYSTEM, constructor_user_content, describer_user_content

ROOT = Path(__file__).resolve().parents[2]

E1_DIRS = {
    "rschema": ROOT / "results" / "predictions" / "e1" / "rschema_schema2text_deepseek",
    "schemabench": ROOT / "results" / "predictions" / "e1" / "schemabench_schema2text_deepseek",
}
E2_DIRS = {
    "rschema": ROOT / "results" / "predictions" / "e2" / "rschema_rt_deepseek",
    "schemabench": ROOT / "results" / "predictions" / "e2" / "schemabench_rt_deepseek",
}

DEEPSEEK_ID = "deepseek-ai/deepseek-coder-6.7b-instruct"
GPT4O_ID = "gpt-4o-mini"


def _index_by_id(pred_dir: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    if not pred_dir.exists():
        return out
    for p in pred_dir.glob("*.json"):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        sid = d.get("id")
        if sid:
            out[sid] = d
            out[sid]["_path"] = str(p)
    return out


_E1_CACHE: dict[str, dict[str, dict]] = {}
_E2_CACHE: dict[str, dict[str, dict]] = {}


def e1_index(dataset: str) -> dict[str, dict]:
    if dataset not in _E1_CACHE:
        _E1_CACHE[dataset] = _index_by_id(E1_DIRS.get(dataset, Path("/__none__")))
    return _E1_CACHE[dataset]


def e2_index(dataset: str) -> dict[str, dict]:
    if dataset not in _E2_CACHE:
        _E2_CACHE[dataset] = _index_by_id(E2_DIRS.get(dataset, Path("/__none__")))
    return _E2_CACHE[dataset]


def load_deepseek_basic_description(dataset: str, schema_id: str) -> dict[str, Any] | None:
    d = e1_index(dataset).get(schema_id)
    if not d:
        return None
    if d.get("model_id") not in (None, DEEPSEEK_ID) and d.get("model_id") != DEEPSEEK_ID:
        # Allow missing model_id only if llm == deepseek
        if d.get("llm") != "deepseek":
            return None
    if d.get("llm") not in (None, "deepseek"):
        return None
    text = d.get("nl_text") or ""
    if not text.strip():
        return None
    return {
        "nl_text": text,
        "model_id": d.get("model_id") or DEEPSEEK_ID,
        "source_path": d.get("_path"),
        "prompt_variant": "basic",
        "prompt_fingerprint": "e1_describer_basic_v1",
    }


def load_deepseek_basic_roundtrip(dataset: str, schema_id: str) -> dict[str, Any] | None:
    d = e2_index(dataset).get(schema_id)
    if not d:
        return None
    if d.get("model_id") != GPT4O_ID and d.get("llm") not in ("gpt4omini", "gpt-4o-mini"):
        return None
    if d.get("source_schema2text_llm") not in (None, "deepseek"):
        return None
    ddl = d.get("ddl") or ""
    if not ddl.strip():
        return None
    return {
        "ddl": ddl,
        "metadata": d.get("metadata") or {},
        "nl_text": d.get("nl_text") or "",
        "model_id": d.get("model_id") or GPT4O_ID,
        "source_path": d.get("_path"),
        "constructor": "gpt_4o_mini",
        "describer": "deepseek",
        "prompt_variant": "basic",
    }


def estimate_archived_constructor_usage(
    nl_text: str,
    database: str,
    pred_ddl: str,
    pred_metadata: dict | None,
    text_number: int | None,
    pricing: dict | None = None,
) -> dict[str, Any]:
    """Tokenizer-estimated tokens/cost for archived GPT-4o-mini constructor I/O."""
    pricing = pricing or load_pricing()
    system = CONSTRUCTOR_SYSTEM
    user = constructor_user_content(nl_text, database, text_number)
    out_obj = {"ddl": pred_ddl, "metadata": pred_metadata or {}}
    out_text = json.dumps(out_obj, ensure_ascii=False)
    in_tok = estimate_openai_tokens(system + "\n" + user, "gpt-4o-mini")
    out_tok = estimate_openai_tokens(out_text, "gpt-4o-mini")
    cost = compute_cost_usd(GPT4O_ID, in_tok, out_tok, pricing)
    return {
        "input_tokens": in_tok,
        "output_tokens": out_tok,
        "cost_usd": cost,
        "cost_basis": "estimated_from_archived_text",
        "latency_s": None,
    }


def estimate_archived_describer_tokens(
    database: str,
    ddl: str,
    nl_text: str,
    tokenizer_count=None,
) -> dict[str, Any]:
    system = BASIC_SYSTEM
    user = describer_user_content(database, ddl, "basic")
    if tokenizer_count is not None:
        in_tok = tokenizer_count(system + "\n" + user)
        out_tok = tokenizer_count(nl_text)
    else:
        in_tok = max(1, len(system + user) // 4)
        out_tok = max(1, len(nl_text) // 4)
    return {
        "input_tokens": in_tok,
        "output_tokens": out_tok,
        "cost_usd": None,
        "cost_basis": "local_gpu_unmetered",
        "latency_s": None,
    }
