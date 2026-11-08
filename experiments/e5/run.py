#!/usr/bin/env python3
"""E5 Scalability and Cost — executable runner.

Usage:
  python -m experiments.e5.run --mode pilot
  python -m experiments.e5.run --mode full
  python -m experiments.e5.run --mode sample-only
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from experiments.e5.archive_reuse import (
        estimate_archived_constructor_usage,
        estimate_archived_describer_tokens,
        load_deepseek_basic_description,
        load_deepseek_basic_roundtrip,
    )
    from experiments.e5.clients import (
        LocalDeepSeekClient,
        OpenAIChatClient,
        construct_schema,
        describe_schema,
        probe_anthropic,
        probe_openai,
    )
    from experiments.e5.cost_tracker import SpendTracker, load_pricing
    from experiments.e5.evaluate_wrap import evaluate_prediction
    from experiments.e5.gold import load_population
    from experiments.e5.sample_select import build_sample_manifest, selected_records, write_manifest
except ImportError:  # pragma: no cover
    from .archive_reuse import (
        estimate_archived_constructor_usage,
        estimate_archived_describer_tokens,
        load_deepseek_basic_description,
        load_deepseek_basic_roundtrip,
    )
    from .clients import (
        LocalDeepSeekClient,
        OpenAIChatClient,
        construct_schema,
        describe_schema,
        probe_anthropic,
        probe_openai,
    )
    from .cost_tracker import SpendTracker, load_pricing
    from .evaluate_wrap import evaluate_prediction
    from .gold import load_population
    from .sample_select import build_sample_manifest, selected_records, write_manifest

OUT = HERE / "outputs"
CACHE = HERE / "cache"
RAW_JSONL = CACHE / "raw_runs.jsonl"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")


def cache_key(**parts: Any) -> str:
    blob = json.dumps(parts, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()[:24]


def load_raw_index(path: Path) -> dict[str, dict]:
    idx: dict[str, dict] = {}
    if not path.exists():
        return idx
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            ck = d.get("cache_key")
            if ck and d.get("ok"):
                idx[ck] = d
    return idx


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = fieldnames or list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fields})


def flatten_eval(ev: dict) -> dict[str, Any]:
    out = {
        "parse_success": int(bool(ev.get("parse_success"))),
        "reconstruction_valid": int(bool(ev.get("reconstruction_valid"))),
        "scored_as_zero": int(bool(ev.get("scored_as_zero"))),
        "nged": ev.get("nged"),
        "exact_match": int(bool(ev.get("exact_match"))),
    }
    for dim in ("tables", "attributes", "domain", "entity", "referential"):
        c = ev.get(dim) or ev.get("counts", {}).get(dim) or {}
        out[f"{dim}_gold"] = c.get("gold", 0)
        out[f"{dim}_recreated"] = c.get("recreated", 0)
        out[f"{dim}_matched"] = c.get("matched", 0)
        out[f"{dim}_tp"] = c.get("tp", 0)
        out[f"{dim}_fp"] = c.get("fp", 0)
        out[f"{dim}_fn"] = c.get("fn", 0)
        f1s = ev.get("per_schema_f1") or {}
        out[f"{dim}_f1"] = f1s.get(dim)
    return out


def build_pipeline_row(
    *,
    schema: dict,
    describer: str,
    prompt: str,
    constructor: str,
    desc_call: dict,
    ctor_call: dict | None,
    eval_res: dict,
    stage: str,
) -> dict[str, Any]:
    d_in = desc_call.get("input_tokens")
    d_out = desc_call.get("output_tokens")
    c_in = (ctor_call or {}).get("input_tokens")
    c_out = (ctor_call or {}).get("output_tokens")
    d_cost = desc_call.get("cost_usd")
    c_cost = (ctor_call or {}).get("cost_usd")
    total_cost = None
    if d_cost is not None or c_cost is not None:
        total_cost = (d_cost or 0.0) + (c_cost or 0.0)
        # If describer cost is intentionally N/A (local), still sum constructor when present
        if d_cost is None and c_cost is not None and desc_call.get("cost_basis") == "local_gpu_unmetered":
            total_cost = c_cost  # end-to-end billed portion; local unmetered
    d_lat = desc_call.get("latency_s")
    c_lat = (ctor_call or {}).get("latency_s")
    total_lat = None
    if d_lat is not None or c_lat is not None:
        total_lat = (d_lat or 0.0) + (c_lat or 0.0)

    row = {
        "dataset": schema["dataset"],
        "schema_id": schema["schema_id"],
        "database": schema.get("database"),
        "tables": schema["tables"],
        "columns": schema["columns"],
        "size_tier": schema["size_tier"],
        "complexity_tier": schema["complexity_tier"],
        "describer": describer,
        "prompt": prompt,
        "constructor": constructor,
        "stage": stage,
        "desc_ok": int(bool(desc_call.get("ok"))),
        "desc_reused": int(bool(desc_call.get("reused"))),
        "desc_model_id": desc_call.get("model_id"),
        "desc_input_tokens": d_in,
        "desc_output_tokens": d_out,
        "desc_latency_s": d_lat,
        "desc_cost_usd": d_cost,
        "desc_cost_basis": desc_call.get("cost_basis"),
        "desc_error": desc_call.get("error"),
        "desc_truncated": int(bool(desc_call.get("truncated"))),
        "desc_output_chars": len(desc_call.get("text") or ""),
        "ctor_ok": int(bool((ctor_call or {}).get("ok"))) if ctor_call else 0,
        "ctor_reused": int(bool((ctor_call or {}).get("reused"))) if ctor_call else 0,
        "ctor_model_id": (ctor_call or {}).get("model_id"),
        "ctor_input_tokens": c_in,
        "ctor_output_tokens": c_out,
        "ctor_latency_s": c_lat,
        "ctor_cost_usd": c_cost,
        "ctor_cost_basis": (ctor_call or {}).get("cost_basis"),
        "ctor_error": (ctor_call or {}).get("error"),
        "ctor_truncated": int(bool((ctor_call or {}).get("truncated"))) if ctor_call else 0,
        "total_input_tokens": (d_in or 0) + (c_in or 0) if (d_in is not None or c_in is not None) else None,
        "total_output_tokens": (d_out or 0) + (c_out or 0) if (d_out is not None or c_out is not None) else None,
        "total_cost_usd": total_cost,
        "total_latency_s": total_lat,
        "nl_text": (desc_call.get("text") or "")[:5000],
        "pred_ddl": ((ctor_call or {}).get("ddl") or "")[:8000],
    }
    row.update(flatten_eval(eval_res))
    return row


def run_e5a_unit(
    schema: dict,
    describer: str,
    prompt: str,
    clients: dict,
    raw_index: dict,
    tracker: SpendTracker,
    *,
    allow_new_deepseek: bool,
    allow_openai: bool,
) -> tuple[dict, list[dict]]:
    """Return (per_schema_row, raw_call_rows)."""
    raw_rows: list[dict] = []
    constructor = "gpt_4o_mini"
    gold_meta, gold_ddl = schema["gold_meta"], schema["gold_ddl"]
    database = schema["database"]
    sid = schema["schema_id"]
    ds = schema["dataset"]

    # --- Description ---
    desc_call: dict[str, Any]
    ck_desc = cache_key(
        stage="describe",
        dataset=ds,
        schema_id=sid,
        describer=describer,
        prompt=prompt,
        model=describer,
    )

    if describer == "deepseek" and prompt == "basic":
        archived = load_deepseek_basic_description(ds, sid)
        if archived:
            tok = estimate_archived_describer_tokens(
                database,
                gold_ddl,
                archived["nl_text"],
                tokenizer_count=(clients["deepseek"].count_tokens if clients.get("deepseek_ready") else None),
            )
            desc_call = {
                "ok": True,
                "text": archived["nl_text"],
                "model_id": archived["model_id"],
                "provider": "huggingface_local",
                "input_tokens": tok["input_tokens"],
                "output_tokens": tok["output_tokens"],
                "latency_s": None,
                "cost_usd": None,
                "cost_basis": "local_gpu_unmetered",
                "reused": True,
                "cache_key": ck_desc,
                "error": None,
                "truncated": False,
                "source_path": archived.get("source_path"),
            }
        elif allow_new_deepseek and clients.get("deepseek_ready"):
            if ck_desc in raw_index:
                desc_call = raw_index[ck_desc]
                desc_call["reused"] = True
            else:
                res = describe_schema("deepseek", clients, database=database, ddl=gold_ddl, prompt_variant=prompt)
                desc_call = res.to_dict()
                desc_call["cache_key"] = ck_desc
                desc_call["reused"] = False
                append_jsonl(RAW_JSONL, {**desc_call, "stage": "describe", "dataset": ds, "schema_id": sid, "prompt": prompt, "describer": describer, "ts": utc_now()})
        else:
            desc_call = {
                "ok": False,
                "error": "DeepSeek basic archive missing and new local generation disabled/unavailable",
                "model_id": "deepseek-ai/deepseek-coder-6.7b-instruct",
                "cost_basis": "n/a",
                "reused": False,
            }
    elif describer == "deepseek" and prompt == "detailed":
        if ck_desc in raw_index:
            desc_call = raw_index[ck_desc]
            desc_call["reused"] = True
        elif allow_new_deepseek and clients.get("deepseek_ready"):
            res = describe_schema("deepseek", clients, database=database, ddl=gold_ddl, prompt_variant=prompt)
            desc_call = res.to_dict()
            desc_call["cache_key"] = ck_desc
            desc_call["reused"] = False
            append_jsonl(RAW_JSONL, {**desc_call, "stage": "describe", "dataset": ds, "schema_id": sid, "prompt": prompt, "describer": describer, "ts": utc_now()})
        else:
            desc_call = {
                "ok": False,
                "error": "DeepSeek detailed requires local generation (disabled or model not ready)",
                "model_id": "deepseek-ai/deepseek-coder-6.7b-instruct",
                "cost_basis": "n/a",
                "reused": False,
            }
    elif describer in ("gpt_5_4_mini", "claude_sonnet_4_6"):
        if ck_desc in raw_index:
            desc_call = raw_index[ck_desc]
            desc_call["reused"] = True
        elif describer == "gpt_5_4_mini" and allow_openai and clients["openai"].available:
            res = describe_schema("gpt_5_4_mini", clients, database=database, ddl=gold_ddl, prompt_variant=prompt)
            desc_call = res.to_dict()
            desc_call["cache_key"] = ck_desc
            append_jsonl(RAW_JSONL, {**desc_call, "stage": "describe", "dataset": ds, "schema_id": sid, "prompt": prompt, "describer": describer, "ts": utc_now()})
        else:
            reason = (
                clients["openai"].unavailable_reason
                if describer == "gpt_5_4_mini"
                else "Anthropic credentials unavailable"
            )
            desc_call = {
                "ok": False,
                "error": f"Describer {describer} unavailable: {reason}",
                "model_id": "gpt-5.4-mini" if describer == "gpt_5_4_mini" else "claude-sonnet-4-6",
                "cost_basis": "n/a",
                "reused": False,
            }
    else:
        desc_call = {"ok": False, "error": f"Unknown describer {describer}", "cost_basis": "n/a"}

    raw_rows.append({**desc_call, "stage": "describe", "dataset": ds, "schema_id": sid, "prompt": prompt, "describer": describer})

    # --- Construction ---
    ctor_call: dict[str, Any] | None = None
    if not desc_call.get("ok"):
        ev = evaluate_prediction(gold_meta, gold_ddl, "")
        row = build_pipeline_row(
            schema=schema,
            describer=describer,
            prompt=prompt,
            constructor=constructor,
            desc_call=desc_call,
            ctor_call=None,
            eval_res=ev,
            stage="e5a",
        )
        row["failure_reason"] = desc_call.get("error")
        return row, raw_rows

    nl = desc_call.get("text") or ""
    ck_ctor = cache_key(
        stage="construct",
        dataset=ds,
        schema_id=sid,
        describer=describer,
        prompt=prompt,
        constructor=constructor,
        nl_hash=hashlib.sha256(nl.encode()).hexdigest()[:16],
    )

    if describer == "deepseek" and prompt == "basic":
        archived_rt = load_deepseek_basic_roundtrip(ds, sid)
        # Only reuse if NL matches archived (or archived exists and we reused E1 text)
        if archived_rt and (not archived_rt.get("nl_text") or archived_rt["nl_text"].strip() == nl.strip() or desc_call.get("reused")):
            usage = estimate_archived_constructor_usage(
                nl, database, archived_rt["ddl"], archived_rt.get("metadata"), schema.get("text_number")
            )
            ctor_call = {
                "ok": True,
                "ddl": archived_rt["ddl"],
                "metadata": archived_rt.get("metadata") or {},
                "model_id": archived_rt["model_id"],
                "provider": "openai",
                "input_tokens": usage["input_tokens"],
                "output_tokens": usage["output_tokens"],
                "latency_s": None,
                "cost_usd": usage["cost_usd"],
                "cost_basis": usage["cost_basis"],
                "reused": True,
                "cache_key": ck_ctor,
                "error": None,
                "truncated": False,
                "text": "",
                "source_path": archived_rt.get("source_path"),
            }
        elif allow_openai and clients["openai"].available:
            if ck_ctor in raw_index:
                ctor_call = raw_index[ck_ctor]
                ctor_call["reused"] = True
            else:
                res = construct_schema(
                    "gpt_4o_mini",
                    clients,
                    nl_text=nl,
                    database=database,
                    text_number=schema.get("text_number"),
                )
                ctor_call = res.to_dict()
                ctor_call["cache_key"] = ck_ctor
                append_jsonl(RAW_JSONL, {**ctor_call, "stage": "construct", "dataset": ds, "schema_id": sid, "prompt": prompt, "describer": describer, "constructor": constructor, "ts": utc_now()})
        else:
            ctor_call = {
                "ok": False,
                "error": "GPT-4o-mini constructor unavailable (no archive match / OpenAI 401)",
                "model_id": "gpt-4o-mini",
                "cost_basis": "n/a",
                "reused": False,
            }
    else:
        # detailed or closed describers need live GPT-4o-mini
        if ck_ctor in raw_index:
            ctor_call = raw_index[ck_ctor]
            ctor_call["reused"] = True
        elif allow_openai and clients["openai"].available:
            res = construct_schema(
                "gpt_4o_mini",
                clients,
                nl_text=nl,
                database=database,
                text_number=schema.get("text_number"),
            )
            ctor_call = res.to_dict()
            ctor_call["cache_key"] = ck_ctor
            append_jsonl(RAW_JSONL, {**ctor_call, "stage": "construct", "dataset": ds, "schema_id": sid, "prompt": prompt, "describer": describer, "constructor": constructor, "ts": utc_now()})
        else:
            ctor_call = {
                "ok": False,
                "error": f"GPT-4o-mini constructor unavailable: {clients['openai'].unavailable_reason}",
                "model_id": "gpt-4o-mini",
                "cost_basis": "n/a",
                "reused": False,
            }

    raw_rows.append({**(ctor_call or {}), "stage": "construct", "dataset": ds, "schema_id": sid, "prompt": prompt, "describer": describer, "constructor": constructor})

    if ctor_call and ctor_call.get("ok"):
        ev = evaluate_prediction(gold_meta, gold_ddl, ctor_call.get("ddl"), ctor_call.get("metadata"), parse_ok=True)
    else:
        ev = evaluate_prediction(gold_meta, gold_ddl, "")

    row = build_pipeline_row(
        schema=schema,
        describer=describer,
        prompt=prompt,
        constructor=constructor,
        desc_call=desc_call,
        ctor_call=ctor_call,
        eval_res=ev,
        stage="e5a",
    )
    if not (ctor_call and ctor_call.get("ok")):
        row["failure_reason"] = (ctor_call or {}).get("error")
    return row, raw_rows


def run_e5b_unit(
    schema: dict,
    constructor: str,
    fixed_desc: dict,
    clients: dict,
    raw_index: dict,
    *,
    allow_openai: bool,
) -> tuple[dict, list[dict]]:
    """E5-B: fixed GPT-5.4-mini detailed description; vary constructor."""
    raw_rows: list[dict] = []
    gold_meta, gold_ddl = schema["gold_meta"], schema["gold_ddl"]
    database = schema["database"]
    sid = schema["schema_id"]
    ds = schema["dataset"]
    nl = fixed_desc.get("text") or ""
    describer = "gpt_5_4_mini"
    prompt = "detailed"

    if not fixed_desc.get("ok") or not nl:
        ev = evaluate_prediction(gold_meta, gold_ddl, "")
        row = build_pipeline_row(
            schema=schema,
            describer=describer,
            prompt=prompt,
            constructor=constructor,
            desc_call=fixed_desc,
            ctor_call=None,
            eval_res=ev,
            stage="e5b",
        )
        row["failure_reason"] = fixed_desc.get("error") or "missing fixed GPT-5.4-mini detailed description"
        return row, raw_rows

    ck_ctor = cache_key(
        stage="e5b_construct",
        dataset=ds,
        schema_id=sid,
        constructor=constructor,
        nl_hash=hashlib.sha256(nl.encode()).hexdigest()[:16],
    )
    if ck_ctor in raw_index:
        ctor_call = raw_index[ck_ctor]
        ctor_call["reused"] = True
    elif constructor == "claude_sonnet_4_6":
        ctor_call = {
            "ok": False,
            "error": "Anthropic credentials unavailable",
            "model_id": "claude-sonnet-4-6",
            "cost_basis": "n/a",
            "reused": False,
        }
    elif allow_openai and clients["openai"].available:
        res = construct_schema(
            constructor,
            clients,
            nl_text=nl,
            database=database,
            text_number=schema.get("text_number"),
        )
        ctor_call = res.to_dict()
        ctor_call["cache_key"] = ck_ctor
        append_jsonl(RAW_JSONL, {**ctor_call, "stage": "e5b_construct", "dataset": ds, "schema_id": sid, "constructor": constructor, "ts": utc_now()})
    else:
        ctor_call = {
            "ok": False,
            "error": f"Constructor {constructor} unavailable: {clients['openai'].unavailable_reason}",
            "model_id": constructor,
            "cost_basis": "n/a",
            "reused": False,
        }

    raw_rows.append({**ctor_call, "stage": "e5b_construct", "dataset": ds, "schema_id": sid, "constructor": constructor})
    if ctor_call.get("ok"):
        ev = evaluate_prediction(gold_meta, gold_ddl, ctor_call.get("ddl"), ctor_call.get("metadata"), parse_ok=True)
    else:
        ev = evaluate_prediction(gold_meta, gold_ddl, "")
    row = build_pipeline_row(
        schema=schema,
        describer=describer,
        prompt=prompt,
        constructor=constructor,
        desc_call=fixed_desc,
        ctor_call=ctor_call,
        eval_res=ev,
        stage="e5b",
    )
    if not ctor_call.get("ok"):
        row["failure_reason"] = ctor_call.get("error")
    return row, raw_rows


def prepare_sample(mode: str) -> tuple[list[dict], list[dict], list[dict]]:
    population = load_population()
    manifest = build_sample_manifest(population, per_dataset=40, seed=42)
    write_manifest(manifest, OUT / "sample_manifest.csv")
    selected = selected_records(population, manifest)
    if mode == "pilot":
        # one schema per dataset, prefer E2-available
        pilot = []
        for ds in ("enterprise145", "rschema", "schemabench"):
            cands = [s for s in selected if s["dataset"] == ds]
            cands.sort(key=lambda x: (0 if x.get("e2_deepseek_basic_available") else 1, x["columns"], x["schema_id"]))
            if cands:
                pilot.append(cands[0])
        return population, manifest, pilot
    return population, manifest, selected


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="SchemaBridge E5 runner")
    ap.add_argument("--mode", choices=["pilot", "full", "sample-only", "status"], default="pilot")
    ap.add_argument("--enable-deepseek-local", action="store_true", help="Load local DeepSeek for new generations / token counts")
    ap.add_argument("--deepseek-latency-n", type=int, default=0, help="Also re-run DeepSeek locally on N schemas for latency (basic+detailed)")
    ap.add_argument("--skip-openai-probe", action="store_true")
    args = ap.parse_args(argv)

    OUT.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)

    tracker = SpendTracker()
    pricing = load_pricing()

    print("=== E5 runner ===")
    print("time_utc:", utc_now())
    print("spend_cap:", tracker.snapshot())

    oa_ok, oa_reason = (False, "skipped")
    if not args.skip_openai_probe:
        oa_ok, oa_reason = probe_openai("gpt-4o-mini")
    an_ok, an_reason = probe_anthropic()
    print("openai_available:", oa_ok, "|", oa_reason[:120])
    print("anthropic_available:", an_ok, "|", an_reason[:120])

    population, manifest, schemas = prepare_sample(args.mode)
    print("population:", len(population), "selected_manifest:", sum(1 for r in manifest if int(r["selected"])), "run_schemas:", len(schemas))
    if args.mode == "sample-only":
        print("Wrote", OUT / "sample_manifest.csv")
        return 0
    if args.mode == "status":
        return 0

    clients: dict[str, Any] = {
        "openai": OpenAIChatClient(tracker, pricing),
        "deepseek": LocalDeepSeekClient(tracker, pricing),
        "deepseek_ready": False,
    }
    # Tokenizer for archived DeepSeek token accounting; full weights only when generating.
    allow_new_deepseek_gen = False
    if clients["deepseek"].available:
        try:
            clients["deepseek"]._ensure_tokenizer()
            clients["deepseek_ready"] = True  # tokenizer ready for counts / archive path
            print("DeepSeek tokenizer ready")
        except Exception as e:  # noqa: BLE001
            print("DeepSeek tokenizer failed:", type(e).__name__, str(e)[:200])
            clients["deepseek_ready"] = False
    # New DeepSeek *generations* require an explicit flag. Latency remount loads
    # weights separately and does not enable archive-replacement generations.
    if args.enable_deepseek_local and clients["deepseek"].available:
        try:
            print("Loading local DeepSeek weights (may take a minute)...")
            clients["deepseek"]._ensure()
            allow_new_deepseek_gen = clients["deepseek"]._model is not None
            print("DeepSeek model ready on", clients["deepseek"]._model.device)
        except Exception as e:  # noqa: BLE001
            print("DeepSeek weight load failed:", type(e).__name__, str(e)[:200])
            allow_new_deepseek_gen = False
    if args.deepseek_latency_n > 0 and clients["deepseek"].available and clients["deepseek"]._model is None:
        try:
            print("Loading local DeepSeek weights for latency remount...")
            clients["deepseek"]._ensure()
            print("DeepSeek model ready on", clients["deepseek"]._model.device)
        except Exception as e:  # noqa: BLE001
            print("DeepSeek latency weight load failed:", type(e).__name__, str(e)[:200])

    raw_index = load_raw_index(RAW_JSONL)
    allow_openai = bool(clients["openai"].available)
    allow_new_deepseek = allow_new_deepseek_gen

    # Deterministic interleaved order of (schema, describer, prompt)
    describers = ["deepseek", "gpt_5_4_mini", "claude_sonnet_4_6"]
    prompts = ["basic", "detailed"]
    jobs = []
    for s in schemas:
        for d in describers:
            for p in prompts:
                jobs.append((s, d, p))
    rng = random.Random(42)
    rng.shuffle(jobs)

    per_schema_rows: list[dict] = []
    raw_summary_rows: list[dict] = []
    failures: list[dict] = []

    print(f"E5-A jobs: {len(jobs)} (concurrency=1)")
    t_run = time.time()
    for i, (schema, describer, prompt) in enumerate(jobs, 1):
        print(f"[{i}/{len(jobs)}] {schema['dataset']} {schema['schema_id']} | {describer}/{prompt}", flush=True)
        row, raws = run_e5a_unit(
            schema,
            describer,
            prompt,
            clients,
            raw_index,
            tracker,
            allow_new_deepseek=allow_new_deepseek,
            allow_openai=allow_openai,
        )
        per_schema_rows.append(row)
        for r in raws:
            raw_summary_rows.append(
                {
                    "execution_id": r.get("execution_id"),
                    "ts": utc_now(),
                    "stage": r.get("stage"),
                    "dataset": schema["dataset"],
                    "schema_id": schema["schema_id"],
                    "describer": describer,
                    "prompt": prompt,
                    "constructor": "gpt_4o_mini" if r.get("stage") == "construct" else "",
                    "model_id": r.get("model_id"),
                    "provider": r.get("provider"),
                    "ok": int(bool(r.get("ok"))),
                    "reused": int(bool(r.get("reused"))),
                    "input_tokens": r.get("input_tokens"),
                    "output_tokens": r.get("output_tokens"),
                    "cached_tokens": r.get("cached_tokens"),
                    "latency_s": r.get("latency_s"),
                    "retry_count": r.get("retry_count"),
                    "cost_usd": r.get("cost_usd"),
                    "cost_basis": r.get("cost_basis"),
                    "truncated": int(bool(r.get("truncated"))),
                    "error": r.get("error"),
                    "output_chars": len(r.get("text") or r.get("ddl") or ""),
                    "cache_key": r.get("cache_key"),
                }
            )
        if row.get("failure_reason") or not row.get("reconstruction_valid"):
            if row.get("failure_reason"):
                failures.append(
                    {
                        "dataset": schema["dataset"],
                        "schema_id": schema["schema_id"],
                        "describer": describer,
                        "prompt": prompt,
                        "constructor": "gpt_4o_mini",
                        "stage": "e5a",
                        "reason": row.get("failure_reason"),
                    }
                )
        print("  spend:", tracker.snapshot(), "ok_recon", row.get("reconstruction_valid"), "ref_f1", row.get("referential_f1"))

    # E5-B: fixed GPT-5.4-mini detailed descriptions from E5-A rows
    print("E5-B constructor isolation...")
    fixed_desc_by_schema: dict[tuple[str, str], dict] = {}
    for row in per_schema_rows:
        if row["describer"] == "gpt_5_4_mini" and row["prompt"] == "detailed" and row.get("desc_ok"):
            fixed_desc_by_schema[(row["dataset"], row["schema_id"])] = {
                "ok": True,
                "text": row.get("nl_text") or "",
                "model_id": row.get("desc_model_id") or "gpt-5.4-mini",
                "input_tokens": row.get("desc_input_tokens"),
                "output_tokens": row.get("desc_output_tokens"),
                "latency_s": row.get("desc_latency_s"),
                "cost_usd": row.get("desc_cost_usd"),
                "cost_basis": row.get("desc_cost_basis"),
                "reused": row.get("desc_reused"),
            }

    schema_by_id = {(s["dataset"], s["schema_id"]): s for s in schemas}
    for s in schemas:
        key = (s["dataset"], s["schema_id"])
        fixed = fixed_desc_by_schema.get(key) or {
            "ok": False,
            "error": "GPT-5.4-mini detailed description unavailable (OpenAI auth failure)",
            "cost_basis": "n/a",
            "model_id": "gpt-5.4-mini",
        }
        for ctor in ("gpt_4o_mini", "gpt_5_4_mini", "claude_sonnet_4_6"):
            row, raws = run_e5b_unit(
                s, ctor, fixed, clients, raw_index, allow_openai=allow_openai
            )
            per_schema_rows.append(row)
            for r in raws:
                raw_summary_rows.append(
                    {
                        "execution_id": r.get("execution_id"),
                        "ts": utc_now(),
                        "stage": r.get("stage"),
                        "dataset": s["dataset"],
                        "schema_id": s["schema_id"],
                        "describer": "gpt_5_4_mini",
                        "prompt": "detailed",
                        "constructor": ctor,
                        "model_id": r.get("model_id"),
                        "provider": r.get("provider"),
                        "ok": int(bool(r.get("ok"))),
                        "reused": int(bool(r.get("reused"))),
                        "input_tokens": r.get("input_tokens"),
                        "output_tokens": r.get("output_tokens"),
                        "cached_tokens": r.get("cached_tokens"),
                        "latency_s": r.get("latency_s"),
                        "retry_count": r.get("retry_count"),
                        "cost_usd": r.get("cost_usd"),
                        "cost_basis": r.get("cost_basis"),
                        "truncated": int(bool(r.get("truncated"))),
                        "error": r.get("error"),
                        "output_chars": len(r.get("text") or r.get("ddl") or ""),
                        "cache_key": r.get("cache_key"),
                    }
                )
            if row.get("failure_reason"):
                failures.append(
                    {
                        "dataset": s["dataset"],
                        "schema_id": s["schema_id"],
                        "describer": "gpt_5_4_mini",
                        "prompt": "detailed",
                        "constructor": ctor,
                        "stage": "e5b",
                        "reason": row["failure_reason"],
                    }
                )

    # Optional DeepSeek latency remount
    if args.deepseek_latency_n > 0 and clients["deepseek_ready"]:
        lat_schemas = schemas[: args.deepseek_latency_n]
        print(f"DeepSeek latency remount on {len(lat_schemas)} schemas × 2 prompts")
        for s in lat_schemas:
            for prompt in ("basic", "detailed"):
                ck = cache_key(stage="deepseek_latency", dataset=s["dataset"], schema_id=s["schema_id"], prompt=prompt)
                if ck in raw_index:
                    continue
                res = describe_schema(
                    "deepseek", clients, database=s["database"], ddl=s["gold_ddl"], prompt_variant=prompt
                )
                d = res.to_dict()
                d["cache_key"] = ck
                append_jsonl(
                    RAW_JSONL,
                    {**d, "stage": "deepseek_latency", "dataset": s["dataset"], "schema_id": s["schema_id"], "prompt": prompt, "ts": utc_now()},
                )
                raw_summary_rows.append(
                    {
                        "execution_id": d.get("execution_id"),
                        "ts": utc_now(),
                        "stage": "deepseek_latency",
                        "dataset": s["dataset"],
                        "schema_id": s["schema_id"],
                        "describer": "deepseek",
                        "prompt": prompt,
                        "constructor": "",
                        "model_id": d.get("model_id"),
                        "provider": d.get("provider"),
                        "ok": int(bool(d.get("ok"))),
                        "reused": 0,
                        "input_tokens": d.get("input_tokens"),
                        "output_tokens": d.get("output_tokens"),
                        "cached_tokens": 0,
                        "latency_s": d.get("latency_s"),
                        "retry_count": 0,
                        "cost_usd": None,
                        "cost_basis": "local_gpu_unmetered",
                        "truncated": int(bool(d.get("truncated"))),
                        "error": d.get("error"),
                        "output_chars": len(d.get("text") or ""),
                        "cache_key": ck,
                    }
                )

    # Persist primary CSVs (report.py will aggregate further)
    write_csv(OUT / "e5_raw_runs.csv", raw_summary_rows)
    write_csv(OUT / "e5_per_schema.csv", per_schema_rows)
    write_csv(OUT / "e5_failures.csv", failures)

    meta = {
        "finished_utc": utc_now(),
        "mode": args.mode,
        "n_schemas": len(schemas),
        "n_per_schema_rows": len(per_schema_rows),
        "n_raw_rows": len(raw_summary_rows),
        "n_failures": len(failures),
        "spend": tracker.snapshot(),
        "openai_available": allow_openai,
        "openai_reason": clients["openai"].unavailable_reason,
        "anthropic_available": an_ok,
        "anthropic_reason": an_reason,
        "deepseek_ready": clients["deepseek_ready"],
        "elapsed_s": time.time() - t_run,
        "execution_env": {
            "concurrency": 1,
            "seed": 42,
            "host": os.uname().nodename if hasattr(os, "uname") else "",
            "python": sys.executable,
        },
    }
    (OUT / "e5_run_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print("Done.", json.dumps(meta, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
