#!/usr/bin/env python3
"""Run SchemaAgent base_direct on full dataset with local open-source LLM."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from agent_format import fully_decode
from local_llm_handler import LocalLLMHandler


class Args:
    method = "base_direct"
    few_shot = False
    verification = ""


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def log_progress(path: str, msg: str) -> None:
    line = f"[{utc_now()}] {msg}\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)
        f.flush()
    print(line, end="")


def load_completed_ids(output_path: Path) -> set[str]:
    done: set[str] = set()
    if not output_path.exists():
        return done
    with output_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
                if row.get("id"):
                    done.add(row["id"])
            except json.JSONDecodeError:
                continue
    return done


_META_TABLE_KEYS = {
    "Attributes", "Primary key", "Foreign key", "schema",
    "属性", "主键", "外键",
}


def schema_table_names(answer: dict) -> list[str]:
    if not isinstance(answer, dict):
        return []
    schema = answer.get("schema", answer)
    if not isinstance(schema, dict):
        return []
    names = [k for k in schema if k not in _META_TABLE_KEYS]
    table_like = [
        k for k in names
        if isinstance(schema[k], dict)
        and any(key in schema[k] for key in ("Attributes", "Attribute", "属性"))
    ]
    return table_like


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="Qwen/Qwen2.5-7B-Instruct")
    parser.add_argument("--device", default=None)
    parser.add_argument("--start-idx", type=int, default=0)
    parser.add_argument("--end-idx", type=int, default=-1)
    parser.add_argument(
        "--dataset",
        default=str(ROOT / "datasets/RSchema/annotation.jsonl"),
    )
    parser.add_argument(
        "--output",
        default=str(ROOT / "outputs/local_full/qwen25_7b_base_direct.jsonl"),
    )
    parser.add_argument(
        "--progress-log",
        default=str(ROOT / "outputs/local_full/run_progress.txt"),
    )
    parser.add_argument("--check-only", action="store_true", help="Run one sample then exit")
    parser.add_argument("--ids", default="", help="Comma-separated sample ids to run, in this order")
    parser.add_argument(
        "--method",
        default="base_direct",
        choices=["base_direct", "base_cot"],
        help="base_direct = one/few-shot; base_cot = same with chain-of-thought",
    )
    parser.add_argument(
        "--few-shot",
        action="store_true",
        help="Use few-shot examples (3) instead of one-shot (1)",
    )
    args = parser.parse_args()

    device = args.device or ("cuda:0" if torch.cuda.is_available() else "cpu")
    output_path = Path(args.output)
    progress_path = Path(args.progress_log)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    progress_path.parent.mkdir(parents=True, exist_ok=True)

    with open(args.dataset, encoding="utf-8") as f:
        samples = [json.loads(line) for line in f if line.strip()]

    end_idx = len(samples) if args.end_idx < 0 else min(args.end_idx, len(samples))
    start_idx = max(0, args.start_idx)
    if args.check_only:
        end_idx = min(start_idx + 1, len(samples))

    done_ids = load_completed_ids(output_path)
    if args.ids:
        wanted = [x for x in args.ids.split(",") if x]
        by_id = {s["id"]: (i, s) for i, s in enumerate(samples)}
        todo = [by_id[i] for i in wanted if i in by_id and i not in done_ids]
    else:
        todo = [
            (i, s)
            for i, s in enumerate(samples[start_idx:end_idx], start=start_idx)
            if s["id"] not in done_ids
        ]

    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        commit = "unknown"
    log_progress(
        str(progress_path),
        f"HEADER commit={commit} model={args.model} temperature=0 do_sample=False "
        f"max_new_tokens=4096 max_input_tokens=12288 "
        f"fixes=empty_deepseek_system,no_truncation,no_injected_agent_text,parser_v2,retry_1",
    )
    log_progress(
        str(progress_path),
        f"START model={args.model} device={device} method={args.method} few_shot={args.few_shot} "
        f"dataset={args.dataset} range=[{start_idx},{end_idx}) total={end_idx-start_idx} "
        f"pending={len(todo)} already_done={len(done_ids)}",
    )
    log_progress(str(progress_path), f"CUDA available={torch.cuda.is_available()}")
    if torch.cuda.is_available():
        idx = int(device.split(":")[1]) if ":" in device else 0
        log_progress(str(progress_path), f"GPU={torch.cuda.get_device_name(idx)} device={device}")

    if not todo:
        log_progress(str(progress_path), "Nothing to do — all samples in range already completed.")
        return 0

    t0 = time.time()
    handler = LocalLLMHandler(model_name=args.model, device=device)
    log_progress(str(progress_path), f"Model loaded in {time.time()-t0:.1f}s")

    run_args = Args()
    run_args.method = args.method
    run_args.few_shot = bool(args.few_shot)
    ok = fail = 0

    for n, (idx, sample) in enumerate(todo, start=1):
        sample_t0 = time.time()
        log_progress(
            str(progress_path),
            f"PROCESSING {n}/{len(todo)} idx={idx} id={sample['id']}",
        )
        try:
            handler.calls = []
            handler.call_meta = {
                "sample_id": sample["id"],
                "method": args.method + ("_fewshot" if args.few_shot else ""),
                "model": args.model,
            }
            result = fully_decode(sample["question"], handler, run_args)
            calls = list(handler.calls)
            last = calls[-1] if calls else {}
            raw = last.get("output") or ""
            low = raw.lower()
            refusal = any(s in low for s in (
                "i'm sorry", "missing some context", "missing some details",
                "can't assist", "cannot provide", "can't provide",
            ))
            result["method"] = args.method
            result["few_shot"] = bool(args.few_shot)
            result["id"] = sample["id"]
            result["sample_id"] = sample["id"]
            result["sample_idx"] = idx
            result["model"] = args.model
            result["prompt_tokens"] = sum(c.get("prompt_tokens") or 0 for c in calls)
            result["completion_tokens"] = sum(c.get("completion_tokens") or 0 for c in calls)
            result["hit_token_limit"] = any(c.get("hit_token_limit") for c in calls)
            result["overflow"] = any(c.get("overflow") for c in calls)
            result["oom"] = any(c.get("oom") for c in calls)
            result["raw_output"] = raw
            result["parsed_schema"] = handler.last_parse
            result["parse_ok"] = bool(handler.last_parse)
            result["retry_used"] = bool(handler.retry_used)
            result["refusal"] = refusal
            result["gold_answer_keys"] = list(sample.get("answer", {}).keys())
            tables = schema_table_names(result.get("answer", {}))
            status = "OK" if tables else "EMPTY_SCHEMA"
            if tables:
                ok += 1
            else:
                fail += 1
            elapsed = time.time() - sample_t0
            result["wall_time_s"] = round(elapsed, 3)
            with output_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")
                f.flush()
            avg = (time.time() - t0) / n
            eta_s = avg * (len(todo) - n)
            log_progress(
                str(progress_path),
                f"{status} idx={idx} id={sample['id']} tables={tables} "
                f"sample_time={elapsed:.1f}s avg={avg:.1f}s eta={eta_s/60:.1f}min ok={ok} fail={fail}",
            )
        except Exception as exc:
            fail += 1
            log_progress(str(progress_path), f"ERROR idx={idx} id={sample['id']}: {exc}")

    total_elapsed = time.time() - t0
    log_progress(
        str(progress_path),
        f"DONE processed={len(todo)} ok={ok} fail={fail} total_time={total_elapsed/60:.1f}min output={output_path}",
    )
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
