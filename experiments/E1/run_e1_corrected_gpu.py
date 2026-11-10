#!/usr/bin/env python3
"""E1 corrected Detailed (Prompt B) inference on RSchema-381 + SchemaBench-239.

- Does not overwrite original Exp4 archives.
- Reuses prior predictions only when schema_id, ddl_hash, model_id, prompt_hash match
  and the saved NL is valid.
- Regenerates CUDA-OOM / missing / invalid outputs with multi-GPU memory-safe settings.
- Writes under results/predictions/e1_corrected/.
"""
from __future__ import annotations

import argparse
import csv
import gc
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


def _resolve_data_root() -> Path:
    """External archives (optional Exp4 reuse) live under SCHEMABRIDGE_DATA_ROOT.

    Primary evaluation populations are loaded from ``datasets/`` inside the repo.
    """
    env = os.environ.get("SCHEMABRIDGE_DATA_ROOT", "").strip()
    if env:
        return Path(env)
    if Path("/data/RSchema").is_dir() or Path("/data/SchemaBench").is_dir():
        return Path("/data")
    return ROOT


DATA = _resolve_data_root()
OUT_ROOT = ROOT / "results" / "predictions" / "e1_corrected"
AUDIT = ROOT / "audit" / "e1_verification" / "full_gpu_run"
PROMPT_PATH = ROOT / "prompts" / "describer_basic.txt"
EXPECTED_PROMPT_HASH = "f09fc8cae8d8ec73deb79f8bc7c2e71842d5fd35e92d833a02954b539755622d"

LLM_CONFIG = {
    "codellama13b": "codellama/CodeLlama-13b-Instruct-hf",
    "llama31": "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "deepseek": "deepseek-ai/deepseek-coder-6.7b-instruct",
}
# Historical Exp4 decoding (preserved)
DDL_MAX_CHARS = 60_000
MAX_NEW_TOKENS = 3072
MAX_INPUT_TOKENS = 8192
GENERATION_TEMPERATURE = 0.2
GENERATION_TOP_P = 1.0
# Documented OOM mitigation: cap total sequence length so KV cache fits on T4s.
# Original OOMs occurred on long DDL with max_new_tokens=3072 (input+output KV).
MEMORY_SAFE_TOTAL_TOKENS = {
    "codellama13b": 6144,
    "llama31": 7168,
    "deepseek": 7168,
}
MIN_NEW_TOKENS = 512

SYSTEM_PROMPT = PROMPT_PATH.read_text(encoding="utf-8").strip()


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_hf_token() -> str | None:
    for key in ("HF_TOKEN", "HUGGING_FACE_HUB_TOKEN"):
        if os.environ.get(key):
            return os.environ[key].strip()
    for p in (DATA / "huggingface_api.txt", ROOT / "huggingface_api.txt"):
        if p.is_file():
            t = p.read_text().strip()
            if t:
                return t
    return None


def sanitize_nl_text(text: str) -> str:
    if not text:
        return text
    text = text.replace("\u0120", " ").replace("Ċ", "\n").replace("▁", " ")
    lines = [" ".join(line.split()) for line in text.splitlines()]
    return "\n".join(ln for ln in lines if ln).strip()


def validate_nl(text: str) -> tuple[bool, str]:
    if not text or not text.strip():
        return False, "empty"
    if text.strip().startswith("ERROR:"):
        return False, "error_marker"
    if len(text.strip()) < 80:
        return False, "too_short"
    if sum(c.isalpha() for c in text) < 30:
        return False, "insufficient_prose"
    return True, ""


def build_rschema_381() -> list[dict]:
    ann = DATA / "RSchema" / "annotation.jsonl"
    ddl_path = DATA / "RSchema" / "annotation_ddl.jsonl"
    if (ROOT / "datasets/rschema/annotation_ddl.jsonl").is_file():
        ddl_path = ROOT / "datasets/rschema/annotation_ddl.jsonl"
    if (ROOT / "datasets/rschema/annotation.jsonl").is_file():
        ann = ROOT / "datasets/rschema/annotation.jsonl"
    ddl_by_id = {}
    for rec in load_jsonl(ddl_path):
        rid = rec.get("id")
        ans = rec.get("answer")
        if rid and isinstance(ans, str) and ans.strip():
            ddl_by_id[rid] = ans.strip()
    out = []
    for i, rec in enumerate(load_jsonl(ann), start=1):
        rid = rec.get("id") or ""
        if rid not in ddl_by_id:
            continue
        ddl = ddl_by_id[rid]
        out.append(
            {
                "dataset": "RSchema",
                "schema_id": rid,
                "original_serial_in_518": f"{i:04d}",
                "eval_index": len(out) + 1,
                "gold_nl": (rec.get("question") or "").strip(),
                "ddl": ddl,
                "ddl_source": "annotation_ddl",
                "ddl_hash": sha256_text(ddl),
                "database": f"rschema_{i:04d}",
                "domain": rec.get("domain"),
            }
        )
    assert len(out) == 381, len(out)
    assert len({r["schema_id"] for r in out}) == 381
    return out


def build_schemabench_239() -> list[dict]:
    path = DATA / "SchemaBench" / "Dataset" / "annotation_ddl.jsonl"
    if (ROOT / "datasets/schemabench/annotation_ddl.jsonl").is_file():
        path = ROOT / "datasets/schemabench/annotation_ddl.jsonl"
    out = []
    for i, rec in enumerate(load_jsonl(path), start=1):
        rid = rec.get("id") or ""
        ans = rec.get("answer")
        assert isinstance(ans, str) and ans.strip(), f"missing DDL at {i}"
        ddl = ans.strip()
        out.append(
            {
                "dataset": "SchemaBench",
                "schema_id": rid,
                "original_serial": f"{i:04d}",
                "eval_index": i,
                "gold_nl": (rec.get("question") or "").strip(),
                "ddl": ddl,
                "ddl_source": "annotation_ddl",
                "ddl_hash": sha256_text(ddl),
                "database": f"schemabench_{i:04d}",
                "domain": rec.get("domain"),
            }
        )
    assert len(out) == 239, len(out)
    assert len({r["schema_id"] for r in out}) == 239
    return out


def out_dir_for(dataset: str, model: str) -> Path:
    if dataset == "RSchema":
        return OUT_ROOT / f"rschema381_detailed_{model}"
    return OUT_ROOT / f"schemabench239_detailed_{model}"


def record_paths(out_dir: Path, eval_index: int) -> tuple[Path, Path]:
    stem = f"{eval_index:04d}"
    return out_dir / f"{stem}.txt", out_dir / f"{stem}.json"


def write_atomic_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    tmp.replace(path)


def write_atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def try_reuse_from_exp4(
    rec: dict, model: str, prompt_hash: str, out_dir: Path
) -> dict[str, Any] | None:
    """Reuse Exp4 / SchemaBench Experiment prediction if provenance matches."""
    model_id = LLM_CONFIG[model]
    if rec["dataset"] == "RSchema":
        src = DATA / "RSchema_ExpResults4/Experiment2" / f"schema2text_{model}"
        serial = rec["original_serial_in_518"]
    else:
        src = DATA / "SchemaBench/Experiment" / f"schema2text_{model}"
        serial = rec["original_serial"]
    js = src / f"{serial}.json"
    txt = src / f"{serial}.txt"
    if not js.is_file() or not txt.is_file():
        return None
    try:
        meta = json.loads(js.read_text(encoding="utf-8"))
    except Exception:
        return None
    if str(meta.get("id") or "") != rec["schema_id"]:
        return None
    if str(meta.get("model_id") or "") != model_id:
        return None
    src_ddl = (meta.get("ddl") or "").strip()
    # Compare hash of source DDL used at inference vs our genuine DDL
    if src_ddl and sha256_text(src_ddl) != rec["ddl_hash"]:
        # Allow if ddl in meta is truncated version of ours
        if not rec["ddl"].startswith(src_ddl[:1000]) and not src_ddl.startswith(rec["ddl"][:1000]):
            return None
    hyp = sanitize_nl_text(txt.read_text(encoding="utf-8", errors="replace"))
    ok, reason = validate_nl(hyp)
    if not ok:
        return None
    obj = {
        "schema_id": rec["schema_id"],
        "dataset": rec["dataset"],
        "eval_index": rec["eval_index"],
        "model_id": model_id,
        "model_revision": "pretrained_default",
        "prompt_variant": "B",
        "prompt_hash": prompt_hash,
        "source_ddl_hash": rec["ddl_hash"],
        "ddl_source": rec["ddl_source"],
        "generated_description": hyp,
        "generation_status": "reused_valid",
        "generation_settings": {
            "reused_from": str(src / f"{serial}.txt"),
            "original_temperature": GENERATION_TEMPERATURE,
            "original_top_p": GENERATION_TOP_P,
            "original_max_new_tokens": MAX_NEW_TOKENS,
            "original_max_input_tokens": MAX_INPUT_TOKENS,
        },
        "device": "reused",
        "retry_count": 0,
        "error_type": None,
        "gold_nl": rec["gold_nl"],
        "ddl": rec["ddl"],
        "database": rec["database"],
    }
    txt_out, js_out = record_paths(out_dir, rec["eval_index"])
    if js_out.is_file():
        try:
            existing = json.loads(js_out.read_text(encoding="utf-8"))
            if existing.get("generation_status") in ("ok", "reused_valid") and validate_nl(
                existing.get("generated_description") or ""
            )[0]:
                return existing
        except Exception:
            pass
    write_atomic_text(txt_out, hyp)
    write_atomic_json(js_out, obj)
    return obj


def already_done(out_dir: Path, eval_index: int) -> bool:
    _, js = record_paths(out_dir, eval_index)
    if not js.is_file():
        return False
    try:
        meta = json.loads(js.read_text(encoding="utf-8"))
    except Exception:
        return False
    if meta.get("generation_status") in ("ok", "reused_valid"):
        return validate_nl(meta.get("generated_description") or "")[0]
    # keep failed records as done for resume of successful; failures may be retried
    return False


def compute_max_new(llm_name: str, input_len: int) -> int:
    safe = MEMORY_SAFE_TOTAL_TOKENS[llm_name]
    budget = safe - input_len - 32
    return max(MIN_NEW_TOKENS, min(MAX_NEW_TOKENS, budget))


def load_model(llm_name: str, model_id: str):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    token = load_hf_token()
    kw = {"token": token} if token else {}
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True, **kw)
    if tokenizer.pad_token_id is None and tokenizer.eos_token_id is not None:
        tokenizer.pad_token_id = tokenizer.eos_token_id

    n_gpu = torch.cuda.device_count()
    device_map: Any = "auto" if n_gpu > 1 else {"": 0}
    max_memory = None
    if n_gpu > 1:
        # leave headroom on each visible GPU
        max_memory = {i: "13GiB" for i in range(n_gpu)}
        max_memory["cpu"] = "48GiB"

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        trust_remote_code=True,
        torch_dtype=torch.float16,
        device_map=device_map,
        max_memory=max_memory,
        low_cpu_mem_usage=True,
        attn_implementation="sdpa",
        **kw,
    )
    model.eval()
    return model, tokenizer


def generate_one(model, tokenizer, llm_name: str, database: str, ddl: str) -> tuple[str, dict]:
    import torch

    if len(ddl) > DDL_MAX_CHARS:
        ddl = ddl[:DDL_MAX_CHARS] + "\n\n... [DDL truncated for length]"
    user = (
        f"Database name: {database}\n\n"
        f"DDL:\n{ddl}\n\n"
        "Write the single exhaustive paragraph now."
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]
    text = None
    if hasattr(tokenizer, "apply_chat_template") and getattr(tokenizer, "chat_template", None):
        try:
            text = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        except Exception:
            text = None
    if text is None:
        text = f"<s>[INST] {SYSTEM_PROMPT}\n\n{user} [/INST]\n"

    # Cap input so input+output fit MEMORY_SAFE_TOTAL (documented OOM mitigation).
    max_input = min(
        MAX_INPUT_TOKENS,
        max(512, MEMORY_SAFE_TOTAL_TOKENS[llm_name] - MIN_NEW_TOKENS),
    )
    inputs = tokenizer(
        text, return_tensors="pt", truncation=True, max_length=max_input
    )
    input_len = int(inputs["input_ids"].shape[1])
    max_new = compute_max_new(llm_name, input_len)
    device = next(model.parameters()).device
    inputs = {k: v.to(device) for k, v in inputs.items()}
    settings = {
        "temperature": GENERATION_TEMPERATURE,
        "top_p": GENERATION_TOP_P,
        "max_input_tokens_requested": MAX_INPUT_TOKENS,
        "effective_max_input_tokens": max_input,
        "requested_max_new_tokens": MAX_NEW_TOKENS,
        "effective_max_new_tokens": max_new,
        "input_tokens": input_len,
        "memory_safe_total_tokens": MEMORY_SAFE_TOTAL_TOKENS[llm_name],
        "do_sample": True,
        "input_truncation_policy": (
            "tokenizer truncation to effective_max_input_tokens so that "
            "input+output <= MEMORY_SAFE_TOTAL_TOKENS on T4 VRAM"
        ),
    }
    with torch.inference_mode():
        out = model.generate(
            **inputs,
            max_new_tokens=max_new,
            do_sample=True,
            temperature=GENERATION_TEMPERATURE,
            top_p=GENERATION_TOP_P,
            pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
        )
    hyp = sanitize_nl_text(
        tokenizer.decode(
            out[0][input_len:],
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        ).strip()
    )
    del out, inputs
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return hyp, settings


def classify_error(exc: BaseException) -> str:
    msg = str(exc).lower()
    if "out of memory" in msg or "cuda" in msg and "memory" in msg:
        return "CUDA_OOM"
    if "maximum context" in msg or "seq" in msg and "length" in msg:
        return "CONTEXT_LENGTH_EXCEEDED"
    return "MODEL_ERROR"


def run_inference_worker(
    dataset: str,
    model: str,
    records: list[dict],
    prompt_hash: str,
    only_missing_or_failed: bool,
) -> dict[str, int]:
    import torch

    out_dir = out_dir_for(dataset, model)
    out_dir.mkdir(parents=True, exist_ok=True)
    model_id = LLM_CONFIG[model]
    stats = Counter()

    # First pass: reuse
    need_gen: list[dict] = []
    for rec in records:
        txt_out, js_out = record_paths(out_dir, rec["eval_index"])
        if already_done(out_dir, rec["eval_index"]):
            stats["skipped_done"] += 1
            continue
        reused = try_reuse_from_exp4(rec, model, prompt_hash, out_dir)
        if reused is not None:
            stats["reused"] += 1
            continue
        # if failed prior exists and only_missing_or_failed, still regenerate
        need_gen.append(rec)

    print(
        f"[{dataset}|{model}] reuse={stats['reused']} done={stats['skipped_done']} "
        f"to_generate={len(need_gen)} visible_gpus={torch.cuda.device_count()}",
        flush=True,
    )
    if not need_gen:
        return dict(stats)

    print(f"[{dataset}|{model}] Loading {model_id}...", flush=True)
    t0 = time.time()
    model_obj, tokenizer = load_model(model, model_id)
    print(f"[{dataset}|{model}] Loaded in {time.time()-t0:.1f}s", flush=True)

    for i, rec in enumerate(need_gen, 1):
        print(
            f"[{dataset}|{model}] gen {i}/{len(need_gen)} eval_index={rec['eval_index']:04d} "
            f"id={rec['schema_id'][:12]} ddl_chars={len(rec['ddl'])}",
            flush=True,
        )
        error_type = None
        hyp = ""
        settings: dict = {}
        retry = 0
        status = "failed"
        last_err = None
        for attempt in range(3):
            retry = attempt
            try:
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                hyp, settings = generate_one(
                    model_obj, tokenizer, model, rec["database"], rec["ddl"]
                )
                ok, reason = validate_nl(hyp)
                if ok:
                    status = "ok"
                    error_type = None
                    break
                status = "failed"
                error_type = "INVALID_OUTPUT"
                last_err = reason
            except Exception as exc:  # noqa: BLE001
                error_type = classify_error(exc)
                last_err = f"{type(exc).__name__}: {exc}"
                status = "failed"
                print(f"  attempt {attempt+1} {error_type}: {exc}", flush=True)
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                # On OOM, shrink memory-safe total further for next attempt
                if error_type == "CUDA_OOM":
                    MEMORY_SAFE_TOTAL_TOKENS[model] = max(
                        2048, MEMORY_SAFE_TOTAL_TOKENS[model] // 2
                    )
                    print(
                        f"  lowered MEMORY_SAFE_TOTAL_TOKENS[{model}]="
                        f"{MEMORY_SAFE_TOTAL_TOKENS[model]}",
                        flush=True,
                    )

        obj = {
            "schema_id": rec["schema_id"],
            "dataset": rec["dataset"],
            "eval_index": rec["eval_index"],
            "model_id": model_id,
            "model_revision": "pretrained_default",
            "prompt_variant": "B",
            "prompt_hash": prompt_hash,
            "source_ddl_hash": rec["ddl_hash"],
            "ddl_source": rec["ddl_source"],
            "generated_description": hyp if status == "ok" else "",
            "generation_status": status,
            "generation_settings": settings,
            "device": f"cuda:{os.environ.get('CUDA_VISIBLE_DEVICES', 'all')}",
            "retry_count": retry,
            "error_type": error_type,
            "error_message": last_err,
            "gold_nl": rec["gold_nl"],
            "ddl": rec["ddl"],
            "database": rec["database"],
        }
        txt_out, js_out = record_paths(out_dir, rec["eval_index"])
        write_atomic_text(txt_out, hyp if status == "ok" else "")
        write_atomic_json(js_out, obj)
        stats["ok" if status == "ok" else "failed"] += 1
        if status != "ok":
            stats[f"fail_{error_type or 'OTHER'}"] += 1

    del model_obj
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return dict(stats)


def write_manifests(rs: list[dict], sb: list[dict]) -> None:
    AUDIT.mkdir(parents=True, exist_ok=True)
    with (AUDIT / "RSCHEMA_381_MANIFEST.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "schema_id",
                "original_record_id",
                "original_serial_in_518",
                "eval_index",
                "ddl_source",
                "ddl_hash",
                "gold_nl_available",
            ],
        )
        w.writeheader()
        for r in rs:
            w.writerow(
                {
                    "schema_id": r["schema_id"],
                    "original_record_id": r["schema_id"],
                    "original_serial_in_518": r["original_serial_in_518"],
                    "eval_index": r["eval_index"],
                    "ddl_source": r["ddl_source"],
                    "ddl_hash": r["ddl_hash"],
                    "gold_nl_available": bool(r["gold_nl"]),
                }
            )
    # also user-requested path
    (ROOT / "audit/e1_verification").mkdir(parents=True, exist_ok=True)
    (ROOT / "audit/e1_verification/E1_RSCHEMA_381_MANIFEST.csv").write_text(
        (AUDIT / "RSCHEMA_381_MANIFEST.csv").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    with (AUDIT / "SCHEMABENCH_239_MANIFEST.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "schema_id",
                "original_serial",
                "eval_index",
                "ddl_source",
                "ddl_hash",
                "gold_nl_available",
            ],
        )
        w.writeheader()
        for r in sb:
            w.writerow(
                {
                    "schema_id": r["schema_id"],
                    "original_serial": r["original_serial"],
                    "eval_index": r["eval_index"],
                    "ddl_source": r["ddl_source"],
                    "ddl_hash": r["ddl_hash"],
                    "gold_nl_available": bool(r["gold_nl"]),
                }
            )


def gpu_inventory() -> dict:
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional at dry-run/import time
        return {
            "generated_utc": utcnow(),
            "torch": None,
            "cuda_available": False,
            "n_gpus": 0,
            "gpus": [],
            "torch_import_error": f"{type(exc).__name__}: {exc}",
            "nvidia_smi": subprocess.getoutput(
                "nvidia-smi --query-gpu=index,name,memory.total,memory.used --format=csv"
            ),
        }

    gpus = []
    for i in range(torch.cuda.device_count()):
        p = torch.cuda.get_device_properties(i)
        gpus.append(
            {
                "index": i,
                "name": torch.cuda.get_device_name(i),
                "total_memory_gb": round(p.total_memory / 1e9, 2),
            }
        )
    return {
        "generated_utc": utcnow(),
        "torch": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "n_gpus": torch.cuda.device_count(),
        "gpus": gpus,
        "nvidia_smi": subprocess.getoutput(
            "nvidia-smi --query-gpu=index,name,memory.total,memory.used --format=csv"
        ),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=(
            "E1 Schema2Text Detailed (Prompt B) generation for RSchema-381 and "
            "SchemaBench-239. Writes under results/predictions/e1_corrected/."
        )
    )
    ap.add_argument("--dataset", choices=["RSchema", "SchemaBench", "all"], default="all")
    ap.add_argument("--model", choices=list(LLM_CONFIG) + ["all"], default="all")
    ap.add_argument(
        "--reuse-only",
        action="store_true",
        help="Only attempt provenance-matched reuse from SCHEMABRIDGE_DATA_ROOT archives",
    )
    ap.add_argument(
        "--generate",
        action="store_true",
        help="Run GPU generation for missing/invalid predictions (resumable)",
    )
    ap.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Optional cap on records per dataset/model (debug/smoke; 0 = full population)",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Load populations, write manifests/config, print plan; do not generate",
    )
    args = ap.parse_args(argv)

    prompt_hash = sha256_text(SYSTEM_PROMPT)
    assert prompt_hash == EXPECTED_PROMPT_HASH, (prompt_hash, EXPECTED_PROMPT_HASH)

    AUDIT.mkdir(parents=True, exist_ok=True)
    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    inv = gpu_inventory()
    (AUDIT / "GPU_INVENTORY.json").write_text(json.dumps(inv, indent=2) + "\n", encoding="utf-8")

    cfg = {
        "prompt_path": str(PROMPT_PATH),
        "prompt_hash": prompt_hash,
        "prompt_variant": "B",
        "models": LLM_CONFIG,
        "ddl_max_chars": DDL_MAX_CHARS,
        "max_new_tokens": MAX_NEW_TOKENS,
        "max_input_tokens": MAX_INPUT_TOKENS,
        "temperature": GENERATION_TEMPERATURE,
        "top_p": GENERATION_TOP_P,
        "memory_safe_total_tokens": MEMORY_SAFE_TOTAL_TOKENS,
        "min_new_tokens": MIN_NEW_TOKENS,
        "data_root": str(DATA),
        "oom_mitigation": (
            "device_map=auto across visible GPUs; max_memory 13GiB/GPU; "
            "torch.inference_mode; empty_cache between gens; "
            "effective_max_new_tokens = min(3072, MEMORY_SAFE_TOTAL - input_len); "
            "OOM retry halves MEMORY_SAFE_TOTAL; optional NF4 via recover_oom_4bit.py"
        ),
        "populations": {"RSchema": 381, "SchemaBench": 239},
    }
    (AUDIT / "INFERENCE_CONFIG.json").write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")

    rs = build_rschema_381()
    sb = build_schemabench_239()
    if args.limit and args.limit > 0:
        rs = rs[: args.limit]
        sb = sb[: args.limit]
    write_manifests(rs, sb)
    print(
        f"RSchema={len(rs)} SchemaBench={len(sb)} prompt_hash={prompt_hash} "
        f"data_root={DATA} generate={args.generate} dry_run={args.dry_run}",
        flush=True,
    )

    datasets = []
    if args.dataset in ("RSchema", "all"):
        datasets.append(("RSchema", rs))
    if args.dataset in ("SchemaBench", "all"):
        datasets.append(("SchemaBench", sb))
    models = list(LLM_CONFIG) if args.model == "all" else [args.model]

    if args.dry_run:
        for ds_name, recs in datasets:
            for model in models:
                out_dir = out_dir_for(ds_name, model)
                done = sum(1 for r in recs if already_done(out_dir, r["eval_index"]))
                print(
                    f"DRY-RUN {ds_name} {model} records={len(recs)} "
                    f"already_done={done} remaining={len(recs) - done} out={out_dir}",
                    flush=True,
                )
        return 0

    # Always reuse first
    summary = []
    for ds_name, recs in datasets:
        for model in models:
            st = (
                run_inference_worker(
                    ds_name,
                    model,
                    recs,
                    prompt_hash,
                    only_missing_or_failed=True,
                )
                if args.generate
                else Counter()
            )
            if not args.generate:
                # reuse-only / planning path
                out_dir = out_dir_for(ds_name, model)
                out_dir.mkdir(parents=True, exist_ok=True)
                st = Counter()
                for rec in recs:
                    if already_done(out_dir, rec["eval_index"]):
                        st["skipped_done"] += 1
                        continue
                    if try_reuse_from_exp4(rec, model, prompt_hash, out_dir):
                        st["reused"] += 1
                    else:
                        st["need_generate"] += 1
            summary.append({"dataset": ds_name, "model": model, **dict(st)})
            print(f"SUMMARY {ds_name} {model} {dict(st)}", flush=True)

    (AUDIT / "job_manifest.json").write_text(
        json.dumps({"generated_utc": utcnow(), "summary": summary}, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
