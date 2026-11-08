#!/usr/bin/env python3
"""Small OpenAI pilot for E5: GPT-5.4-mini describer + GPT-4o-mini constructor.

Also optionally reconstructs existing Claude descriptions with GPT-4o-mini.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Load OpenAI key from file into env if needed
if not os.environ.get("OPENAI_API_KEY"):
    p = Path("/data/openai_api.txt")
    if p.is_file():
        lines = [ln.strip() for ln in p.read_text().splitlines() if ln.strip()]
        if lines:
            os.environ["OPENAI_API_KEY"] = lines[0]

from experiments.e5.clients import (  # noqa: E402
    AnthropicChatClient,
    OpenAIChatClient,
    construct_schema,
    describe_schema,
    probe_anthropic,
    probe_openai,
)
from experiments.e5.cost_tracker import SpendTracker, load_pricing  # noqa: E402
from experiments.e5.evaluate_wrap import evaluate_prediction  # noqa: E402
from experiments.e5.gold import load_population  # noqa: E402
from experiments.e5.run import (  # noqa: E402
    OUT,
    RAW_JSONL,
    append_jsonl,
    build_pipeline_row,
    cache_key,
    load_raw_index,
    utc_now,
    write_csv,
)
from experiments.e5.sample_select import build_sample_manifest, selected_records  # noqa: E402


def merge_rows(existing: list[dict], new_rows: list[dict]) -> list[dict]:
    def key(r: dict) -> tuple:
        return (
            r.get("stage"),
            r.get("dataset"),
            r.get("schema_id"),
            r.get("describer"),
            r.get("prompt"),
            r.get("constructor"),
        )

    idx = {key(r): i for i, r in enumerate(existing)}
    out = list(existing)
    for r in new_rows:
        k = key(r)
        if k in idx:
            out[idx[k]] = r
        else:
            idx[k] = len(out)
            out.append(r)
    return out


def run_one(schema, describer, prompt, clients, raw_index, tracker):
    ds, sid = schema["dataset"], schema["schema_id"]
    constructor = "gpt_4o_mini"
    ck_desc = cache_key(
        stage="describe",
        dataset=ds,
        schema_id=sid,
        describer=describer,
        prompt=prompt,
        model=describer,
    )
    if ck_desc in raw_index and raw_index[ck_desc].get("ok"):
        desc = dict(raw_index[ck_desc])
        desc["reused"] = True
    else:
        res = describe_schema(
            describer,
            clients,
            database=schema["database"],
            ddl=schema["gold_ddl"],
            prompt_variant=prompt,
        )
        desc = res.to_dict()
        desc["cache_key"] = ck_desc
        desc["reused"] = False
        append_jsonl(
            RAW_JSONL,
            {
                **desc,
                "stage": "describe",
                "dataset": ds,
                "schema_id": sid,
                "prompt": prompt,
                "describer": describer,
                "ts": utc_now(),
            },
        )
        if desc.get("ok"):
            raw_index[ck_desc] = desc

    if not desc.get("ok"):
        ev = evaluate_prediction(schema["gold_meta"], schema["gold_ddl"], "")
        row = build_pipeline_row(
            schema=schema,
            describer=describer,
            prompt=prompt,
            constructor=constructor,
            desc_call=desc,
            ctor_call=None,
            eval_res=ev,
            stage="e5a",
        )
        row["failure_reason"] = desc.get("error")
        return row

    nl = desc.get("text") or ""
    nl_hash = hashlib.sha256(nl.encode()).hexdigest()[:16]
    ck_ctor = cache_key(
        stage="construct",
        dataset=ds,
        schema_id=sid,
        describer=describer,
        prompt=prompt,
        constructor=constructor,
        nl_hash=nl_hash,
    )
    if ck_ctor in raw_index and raw_index[ck_ctor].get("ok"):
        ctor = dict(raw_index[ck_ctor])
        ctor["reused"] = True
    else:
        res = construct_schema(
            constructor,
            clients,
            nl_text=nl,
            database=schema["database"],
            text_number=schema.get("text_number"),
        )
        ctor = res.to_dict()
        ctor["cache_key"] = ck_ctor
        append_jsonl(
            RAW_JSONL,
            {
                **ctor,
                "stage": "construct",
                "dataset": ds,
                "schema_id": sid,
                "prompt": prompt,
                "describer": describer,
                "constructor": constructor,
                "ts": utc_now(),
            },
        )
        if ctor.get("ok"):
            raw_index[ck_ctor] = ctor

    if ctor.get("ok"):
        ev = evaluate_prediction(
            schema["gold_meta"], schema["gold_ddl"], ctor.get("ddl"), ctor.get("metadata"), parse_ok=True
        )
    else:
        ev = evaluate_prediction(schema["gold_meta"], schema["gold_ddl"], "")
    row = build_pipeline_row(
        schema=schema,
        describer=describer,
        prompt=prompt,
        constructor=constructor,
        desc_call=desc,
        ctor_call=ctor,
        eval_res=ev,
        stage="e5a",
    )
    if not ctor.get("ok"):
        row["failure_reason"] = ctor.get("error")
    return row


def main() -> int:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    tracker = SpendTracker(float(os.environ.get("E5_MAX_SPEND_USD", "25")))
    pricing = load_pricing()
    oa_ok, oa_reason = probe_openai("gpt-4o-mini")
    an_ok, an_reason = probe_anthropic()
    print("openai:", oa_ok, oa_reason[:100])
    print("anthropic:", an_ok, an_reason[:100])
    if not oa_ok:
        return 2

    clients = {
        "openai": OpenAIChatClient(tracker, pricing),
        "anthropic": AnthropicChatClient(tracker, pricing),
    }
    raw_index = load_raw_index(RAW_JSONL)
    pop = load_population()
    man = build_sample_manifest(pop, per_dataset=40, seed=42)
    selected = selected_records(pop, man)

    # Pick n schemas: prefer one small from different datasets
    schemas = []
    for ds in ("rschema", "schemabench", "enterprise145"):
        cands = sorted(
            [s for s in selected if s["dataset"] == ds],
            key=lambda x: (x["columns"], x["schema_id"]),
        )
        if cands:
            schemas.append(cands[0])
        if len(schemas) >= n:
            break
    schemas = schemas[:n]
    print("pilot schemas:", [(s["dataset"], s["schema_id"], s["columns"]) for s in schemas])

    jobs = []
    for s in schemas:
        for describer in ("gpt_5_4_mini",):
            for prompt in ("basic", "detailed"):
                jobs.append((s, describer, prompt))
        # Also one Claude→GPT-4o-mini proper E5-A path if Anthropic available
        if an_ok:
            jobs.append((s, "claude_sonnet_4_6", "basic"))

    new_rows = []
    t0 = time.time()
    for i, (s, describer, prompt) in enumerate(jobs, 1):
        print(f"[{i}/{len(jobs)}] {s['dataset']} {s['schema_id']} {describer}/{prompt} rem=${tracker.remaining():.2f}", flush=True)
        if not tracker.can_afford(0.05):
            print("spend cap near; stop")
            break
        row = run_one(s, describer, prompt, clients, raw_index, tracker)
        new_rows.append(row)
        print(
            "  recon", row.get("reconstruction_valid"),
            "ref", row.get("referential_f1"),
            "cost", row.get("total_cost_usd"),
            "lat", row.get("total_latency_s"),
            "err", (row.get("failure_reason") or "")[:80],
        )

    # E5-B on first schema if we have GPT-5.4-mini detailed description
    e5b_rows = []
    if schemas:
        s0 = schemas[0]
        fixed = None
        for r in new_rows:
            if (
                r["dataset"] == s0["dataset"]
                and r["schema_id"] == s0["schema_id"]
                and r["describer"] == "gpt_5_4_mini"
                and r["prompt"] == "detailed"
                and int(r.get("desc_ok") or 0) == 1
            ):
                fixed = r
                break
        if fixed and fixed.get("nl_text"):
            nl = fixed["nl_text"]
            for ctor in ("gpt_4o_mini", "gpt_5_4_mini"):
                print(f"E5-B {s0['schema_id']} constructor={ctor}")
                res = construct_schema(
                    ctor,
                    clients,
                    nl_text=nl,
                    database=s0["database"],
                    text_number=s0.get("text_number"),
                )
                ctor_call = res.to_dict()
                append_jsonl(
                    RAW_JSONL,
                    {
                        **ctor_call,
                        "stage": "e5b_construct",
                        "dataset": s0["dataset"],
                        "schema_id": s0["schema_id"],
                        "constructor": ctor,
                        "ts": utc_now(),
                    },
                )
                if ctor_call.get("ok"):
                    ev = evaluate_prediction(
                        s0["gold_meta"], s0["gold_ddl"], ctor_call.get("ddl"), ctor_call.get("metadata"), parse_ok=True
                    )
                else:
                    ev = evaluate_prediction(s0["gold_meta"], s0["gold_ddl"], "")
                desc_call = {
                    "ok": True,
                    "text": nl,
                    "model_id": fixed.get("desc_model_id") or "gpt-5.4-mini",
                    "input_tokens": fixed.get("desc_input_tokens"),
                    "output_tokens": fixed.get("desc_output_tokens"),
                    "latency_s": fixed.get("desc_latency_s"),
                    "cost_usd": fixed.get("desc_cost_usd"),
                    "cost_basis": fixed.get("desc_cost_basis"),
                    "reused": True,
                }
                row = build_pipeline_row(
                    schema=s0,
                    describer="gpt_5_4_mini",
                    prompt="detailed",
                    constructor=ctor,
                    desc_call=desc_call,
                    ctor_call=ctor_call,
                    eval_res=ev,
                    stage="e5b",
                )
                e5b_rows.append(row)
                print("  e5b recon", row.get("reconstruction_valid"), "ref", row.get("referential_f1"), "cost", row.get("total_cost_usd"))

    existing = []
    path = OUT / "e5_per_schema.csv"
    if path.exists() and path.stat().st_size:
        existing = list(csv.DictReader(path.open()))
    merged = merge_rows(existing, new_rows + e5b_rows)
    write_csv(path, merged)

    meta = {
        "finished_utc": utc_now(),
        "component": "openai_pilot",
        "n_schemas": len(schemas),
        "n_jobs": len(jobs),
        "n_new_rows": len(new_rows) + len(e5b_rows),
        "spend": tracker.snapshot(),
        "openai_available": oa_ok,
        "anthropic_available": an_ok,
        "elapsed_s": time.time() - t0,
        "schemas": [{"dataset": s["dataset"], "schema_id": s["schema_id"], "columns": s["columns"]} for s in schemas],
    }
    (OUT / "e5_openai_pilot_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
