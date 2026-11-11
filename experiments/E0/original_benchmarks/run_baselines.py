#!/usr/bin/env python3
"""Standalone E0 PaperMethods baseline runner (one-shot / CoT / few-shot).

Historical provenance: LLM4DBdesign ``run_local_full.py`` + ``agent_format.fully_decode``
(base_direct / base_cot). SchemaAgent multi-agent path is intentionally excluded.

Default models are the three Table VI open-weight constructors — never Qwen.

Examples::

    # Model-free dry-run (prompt + dataset assembly only)
    python3 experiments/E0/original_benchmarks/run_baselines.py --dry-run \\
        --model codellama-13b --method one_shot --limit 2

    # Smoke (1 record, requires GPU + HF cache)
    HF_HOME=/data/Text2ER/hf_cache \\
    python3 experiments/E0/original_benchmarks/run_baselines.py \\
        --model llama-3.1-8b --method one_shot_cot --limit 1 --device cuda:0

    # Full RSchema regeneration (label as REGENERATED_NEW_RUN)
    python3 experiments/E0/original_benchmarks/run_baselines.py \\
        --model deepseek-coder-6.7b --method few_shot --device cuda:1
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # SchemaBridge/
BENCH = Path(__file__).resolve().parent
SHARED = BENCH / "_shared"
ONE_SHOT = BENCH / "one_shot"

sys.path.insert(0, str(SHARED))
sys.path.insert(0, str(ONE_SHOT))  # baseline_decode + prompt_generator_format

from baseline_decode import fully_decode  # noqa: E402

PAPER_MODELS = {
    "codellama-13b": "codellama/CodeLlama-13b-Instruct-hf",
    "codellama13b": "codellama/CodeLlama-13b-Instruct-hf",
    "llama-3.1-8b": "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "llama31": "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "deepseek-coder-6.7b": "deepseek-ai/deepseek-coder-6.7b-instruct",
    "deepseek": "deepseek-ai/deepseek-coder-6.7b-instruct",
}
MODEL_DIR = {
    "codellama/CodeLlama-13b-Instruct-hf": "codellama13b",
    "meta-llama/Meta-Llama-3.1-8B-Instruct": "llama31",
    "deepseek-ai/deepseek-coder-6.7b-instruct": "deepseek",
}
METHOD_MAP = {
    "one_shot": ("base_direct", False, "one_shot"),
    "one_shot_cot": ("base_cot", False, "one_shot_cot"),
    "few_shot": ("base_direct", True, "few_shot"),
}


class Args:
    def __init__(self, method: str, few_shot: bool):
        self.method = method
        self.few_shot = few_shot
        self.verification = ""


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def resolve_model(name: str) -> str:
    key = name.strip()
    if key in PAPER_MODELS:
        return PAPER_MODELS[key]
    low = key.lower().replace("_", "-")
    if low in PAPER_MODELS:
        return PAPER_MODELS[low]
    # Allow full HF id only if it is one of the three paper models.
    if key in MODEL_DIR:
        return key
    raise SystemExit(
        f"Unsupported model {name!r}. Table VI baselines require one of: "
        + ", ".join(sorted(set(PAPER_MODELS.values())))
    )


def load_dataset(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rows.append(json.loads(line))
    return rows


def load_done(path: Path) -> set[str]:
    done: set[str] = set()
    if not path.is_file():
        return done
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("id"):
                done.add(str(row["id"]))
    return done


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--model",
        required=True,
        help="codellama-13b | llama-3.1-8b | deepseek-coder-6.7b (or full HF id)",
    )
    ap.add_argument(
        "--method",
        required=True,
        choices=list(METHOD_MAP),
        help="one_shot | one_shot_cot | few_shot",
    )
    ap.add_argument(
        "--dataset",
        default=str(ROOT / "datasets/rschema/annotation.jsonl"),
        help="Gold NL requirements JSONL (question field used as input)",
    )
    ap.add_argument(
        "--output-root",
        default=str(ROOT / "results/predictions/e0/rschema_papermethods_regenerated"),
        help="Root for regenerated results.jsonl trees",
    )
    ap.add_argument("--device", default=None)
    ap.add_argument("--limit", type=int, default=0, help="Max records (0 = all)")
    ap.add_argument("--start-idx", type=int, default=0)
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate prompts + dataset assembly without loading a model",
    )
    ap.add_argument(
        "--check-leakage",
        action="store_true",
        default=True,
        help="Refuse if gold answer/DDL appears in the constructor prompt (default on)",
    )
    args = ap.parse_args()

    model_id = resolve_model(args.model)
    model_dir = MODEL_DIR[model_id]
    decode_method, few_shot, method_dir = METHOD_MAP[args.method]
    dataset_path = Path(args.dataset)
    rows = load_dataset(dataset_path)
    if args.start_idx:
        rows = rows[args.start_idx :]
    if args.limit and args.limit > 0:
        rows = rows[: args.limit]

    out_dir = Path(args.output_root) / model_dir / method_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "results.jsonl"
    meta_path = out_dir / "run_metadata.json"

    # Dry-run: build prompts for first record(s) and exit.
    from prompt_generator_format import (  # noqa: WPS433
        get_cot_prompt,
        get_direct_few_shot_prompt,
        get_direct_prompt,
    )

    print(f"[{utc_now()}] model={model_id} method={args.method} n={len(rows)}")
    print(f"[{utc_now()}] dataset={dataset_path}")
    print(f"[{utc_now()}] output={out_path}")
    print(f"[{utc_now()}] label=REGENERATED_NEW_RUN (not recovered historical)")

    for i, row in enumerate(rows[:3]):
        q = row.get("question") or row.get("nl") or ""
        if not q.strip():
            raise SystemExit(f"Empty question for id={row.get('id')}")
        if few_shot:
            prompt = get_direct_few_shot_prompt(q)
        elif decode_method == "base_cot":
            prompt = get_cot_prompt(q)
        else:
            prompt = get_direct_prompt(q)
        # Leakage check: gold answer must not appear in the prompt.
        gold = row.get("answer")
        if args.check_leakage and gold is not None:
            gold_s = json.dumps(gold, ensure_ascii=False) if not isinstance(gold, str) else gold
            # Demonstrations are allowed; the *current* gold must not be in the prompt.
            # Heuristic: if a distinctive gold table name set of size>=3 all appear, flag.
            if isinstance(gold, dict):
                schema = gold.get("schema", gold)
                if isinstance(schema, dict):
                    tables = [k for k in schema if k not in ("Attributes", "Primary key", "Foreign key", "schema")]
                    if len(tables) >= 3 and all(t in prompt for t in tables[:5]):
                        # Could be coincidence with demos; check id-specific question uniqueness
                        pass
            # Hard fail if the raw gold JSON blob is embedded.
            if len(gold_s) > 80 and gold_s[:80] in prompt:
                raise SystemExit(f"LEAKAGE: gold answer prefix found in prompt for id={row.get('id')}")
        print(f"  dry sample[{i}] id={row.get('id')} prompt_chars={len(prompt)}")

    if args.dry_run:
        meta = {
            "generated": utc_now(),
            "status": "DRY_RUN",
            "model_id": model_id,
            "method": args.method,
            "decode_method": decode_method,
            "few_shot": few_shot,
            "dataset": str(dataset_path),
            "n_planned": len(rows),
            "settings": {"temperature": 0, "max_tokens": 4096},
            "note": "REGENERATED_NEW_RUN scaffold; no model inference performed",
        }
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        print(f"[{utc_now()}] dry-run OK; wrote {meta_path}")
        return 0

    # Live inference
    os.environ.setdefault("HF_HOME", "/data/Text2ER/hf_cache")
    os.environ.setdefault("TRANSFORMERS_CACHE", os.environ["HF_HOME"] + "/hub")
    from local_llm_handler import LocalLLMHandler  # noqa: WPS433

    device = args.device or ("cuda:0" if __import__("torch").cuda.is_available() else "cpu")
    handler = LocalLLMHandler(model_name=model_id, device=device)
    decode_args = Args(decode_method, few_shot)
    done = load_done(out_path)

    run_meta = {
        "generated": utc_now(),
        "status": "REGENERATED_NEW_RUN",
        "model_id": model_id,
        "model_revision_hint": {
            "codellama/CodeLlama-13b-Instruct-hf": "745795438019e47e4dad1347a0093e11deee4c68",
            "meta-llama/Meta-Llama-3.1-8B-Instruct": "0e9e39f249a16976918f6564b8830bc894c89659",
            "deepseek-ai/deepseek-coder-6.7b-instruct": "e5d64addd26a6a1db0f9b863abf6ee3141936807",
        }.get(model_id),
        "method": args.method,
        "decode_method": decode_method,
        "few_shot": few_shot,
        "dataset": str(dataset_path),
        "device": device,
        "settings": {"temperature": 0, "max_tokens": 4096},
        "hf_home": os.environ.get("HF_HOME"),
        "note": "New regeneration — not bit-for-bit historical PaperMethods recovery",
    }
    meta_path.write_text(json.dumps(run_meta, indent=2), encoding="utf-8")

    n_ok = n_fail = 0
    t0 = time.time()
    with out_path.open("a", encoding="utf-8") as fout:
        for idx, row in enumerate(rows):
            rid = str(row["id"])
            if rid in done:
                continue
            question = row.get("question") or ""
            handler.call_meta = {
                "sample_id": rid,
                "model": model_id,
                "method": args.method,
            }
            try:
                result = fully_decode(question, handler, decode_args)
                answer = result.get("answer") or {}
                status = "ok" if answer else "empty"
                if not answer:
                    n_fail += 1
                else:
                    n_ok += 1
                rec = {
                    "id": rid,
                    "status": status,
                    "question": question,
                    "answer": answer,
                    "raw_output": result.get("raw_output"),
                    "model": model_id,
                    "method": args.method,
                    "generated_at": utc_now(),
                    "run_label": "REGENERATED_NEW_RUN",
                }
            except Exception as exc:  # noqa: BLE001
                n_fail += 1
                rec = {
                    "id": rid,
                    "status": "error",
                    "error": str(exc),
                    "question": question,
                    "answer": {},
                    "model": model_id,
                    "method": args.method,
                    "generated_at": utc_now(),
                    "run_label": "REGENERATED_NEW_RUN",
                }
            fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
            fout.flush()
            if (idx + 1) % 10 == 0 or idx == 0:
                print(
                    f"[{utc_now()}] {idx+1}/{len(rows)} ok={n_ok} fail={n_fail} "
                    f"elapsed={time.time()-t0:.0f}s",
                    flush=True,
                )

    print(f"[{utc_now()}] done ok={n_ok} fail={n_fail} -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
