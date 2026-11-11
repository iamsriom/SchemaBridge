#!/usr/bin/env python3
"""Documented 4-bit nf4 recovery pass for SchemaBench CUDA_OOM failures.

Protocol change vs Exp4 fp16: load model in 4-bit BitsAndBytes nf4, keep Prompt B,
same temperature/top_p, memory-safe max_new_tokens. Does not truncate DDL beyond
the original DDL_MAX_CHARS=60000 policy.
"""
from __future__ import annotations

import argparse
import gc
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_e1_corrected_gpu as runner  # noqa: E402

LLM_CONFIG = runner.LLM_CONFIG


def load_model_4bit(model_id: str):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    token = runner.load_hf_token()
    kw = {"token": token} if token else {}
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True, **kw)
    if tokenizer.pad_token_id is None and tokenizer.eos_token_id is not None:
        tokenizer.pad_token_id = tokenizer.eos_token_id
    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.float16,
    )
    n_gpu = torch.cuda.device_count()
    device_map = "auto" if n_gpu > 1 else {"": 0}
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        quantization_config=bnb,
        device_map=device_map,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
        attn_implementation="sdpa",
        **kw,
    )
    model.eval()
    return model, tokenizer


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=list(LLM_CONFIG))
    ap.add_argument("--dataset", default="SchemaBench", choices=["SchemaBench", "RSchema"])
    args = ap.parse_args()

    prompt_hash = runner.sha256_text(runner.SYSTEM_PROMPT)
    records = (
        runner.build_schemabench_239()
        if args.dataset == "SchemaBench"
        else runner.build_rschema_381()
    )
    out_dir = runner.out_dir_for(args.dataset, args.model)
    need = []
    for rec in records:
        _, js = runner.record_paths(out_dir, rec["eval_index"])
        if not js.is_file():
            need.append(rec)
            continue
        meta = json.loads(js.read_text(encoding="utf-8"))
        if meta.get("generation_status") in ("ok", "reused_valid") and runner.validate_nl(
            meta.get("generated_description") or ""
        )[0]:
            continue
        need.append(rec)
    print(f"[4bit-recovery {args.dataset}|{args.model}] need={len(need)}", flush=True)
    if not need:
        return 0

    # More aggressive memory-safe totals for 4bit recovery of huge schemas
    runner.MEMORY_SAFE_TOTAL_TOKENS[args.model] = 4096

    model_id = LLM_CONFIG[args.model]
    print(f"Loading 4-bit {model_id}...", flush=True)
    t0 = time.time()
    model, tokenizer = load_model_4bit(model_id)
    print(f"Loaded in {time.time()-t0:.1f}s", flush=True)

    import torch

    ok = fail = 0
    for i, rec in enumerate(need, 1):
        print(f"  [{i}/{len(need)}] eval={rec['eval_index']:04d} chars={len(rec['ddl'])}", flush=True)
        status = "failed"
        error_type = None
        hyp = ""
        settings = {}
        last_err = None
        for attempt in range(3):
            try:
                gc.collect()
                torch.cuda.empty_cache()
                hyp, settings = runner.generate_one(
                    model, tokenizer, args.model, rec["database"], rec["ddl"]
                )
                settings["quantization"] = "4bit_nf4_recovery"
                settings["recovery_pass"] = True
                good, reason = runner.validate_nl(hyp)
                if good:
                    status = "ok"
                    break
                error_type = "INVALID_OUTPUT"
                last_err = reason
            except Exception as exc:  # noqa: BLE001
                error_type = runner.classify_error(exc)
                last_err = f"{type(exc).__name__}: {exc}"
                print(f"    attempt {attempt+1} {error_type}: {exc}", flush=True)
                runner.MEMORY_SAFE_TOTAL_TOKENS[args.model] = max(
                    1536, runner.MEMORY_SAFE_TOTAL_TOKENS[args.model] // 2
                )
                gc.collect()
                torch.cuda.empty_cache()
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
            "generation_settings": settings
            or {"quantization": "4bit_nf4_recovery", "recovery_pass": True},
            "device": f"cuda:{os.environ.get('CUDA_VISIBLE_DEVICES', 'all')}",
            "retry_count": 3,
            "error_type": error_type,
            "error_message": last_err,
            "gold_nl": rec["gold_nl"],
            "ddl": rec["ddl"],
            "database": rec["database"],
            "recovery_method": "4bit_nf4",
        }
        txt, js = runner.record_paths(out_dir, rec["eval_index"])
        runner.write_atomic_text(txt, hyp if status == "ok" else "")
        runner.write_atomic_json(js, obj)
        if status == "ok":
            ok += 1
        else:
            fail += 1
    print(f"DONE recovered_ok={ok} still_failed={fail}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
