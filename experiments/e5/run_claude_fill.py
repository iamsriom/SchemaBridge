#!/usr/bin/env python3
"""Fill Claude Sonnet 4.6 E5 rows using /data/anthropic.txt.

Because OpenAI auth is currently failing, E5-A Claude reconstructions use
Claude Sonnet 4.6 as constructor (documented fallback). GPT-5.4-mini rows stay
N/A until a working OpenAI key is provided.
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

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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
from experiments.e5.sample_select import (  # noqa: E402
    build_sample_manifest,
    selected_records,
    write_manifest,
)

# Ensure Anthropic env from file if unset
if not os.environ.get("ANTHROPIC_API_KEY"):
    for p in (Path("/data/anthropic.txt"), Path("/data/anthropic_api.txt")):
        if p.is_file() and p.read_text().strip():
            os.environ["ANTHROPIC_API_KEY"] = p.read_text().strip().splitlines()[0].strip()
            break


def merge_per_schema(existing: list[dict], new_rows: list[dict]) -> list[dict]:
    """Replace rows matching (stage, dataset, schema_id, describer, prompt[, constructor])."""
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["pilot", "full"], default="pilot")
    ap.add_argument("--max-spend", type=float, default=float(os.environ.get("E5_MAX_SPEND_USD", "25")))
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    tracker = SpendTracker(args.max_spend)
    pricing = load_pricing()

    oa_ok, oa_reason = probe_openai("gpt-4o-mini")
    an_ok, an_reason = probe_anthropic()
    print("openai:", oa_ok, "|", oa_reason[:160])
    print("anthropic:", an_ok, "|", an_reason[:160])
    print("spend_cap:", tracker.snapshot())
    if not an_ok:
        print("Anthropic unavailable; cannot fill Claude rows.")
        return 2

    clients = {
        "openai": OpenAIChatClient(tracker, pricing),
        "anthropic": AnthropicChatClient(tracker, pricing),
    }
    raw_index = load_raw_index(RAW_JSONL)

    population = load_population()
    manifest = build_sample_manifest(population, per_dataset=40, seed=42)
    write_manifest(manifest, OUT / "sample_manifest.csv")
    selected = selected_records(population, manifest)
    if args.mode == "pilot":
        schemas = []
        for ds in ("enterprise145", "rschema", "schemabench"):
            cands = [s for s in selected if s["dataset"] == ds]
            cands.sort(key=lambda x: (x["columns"], x["schema_id"]))
            if cands:
                schemas.append(cands[0])
    else:
        schemas = selected

    prompts = ["basic", "detailed"]
    jobs = [(s, p) for s in schemas for p in prompts]
    rng = random.Random(42)
    rng.shuffle(jobs)

    print(f"Claude E5-A jobs: {len(jobs)} schemas×prompts; constructor preference gpt-4o-mini then Claude fallback")
    new_rows: list[dict] = []
    failures: list[dict] = []
    t0 = time.time()

    for i, (schema, prompt) in enumerate(jobs, 1):
        ds, sid = schema["dataset"], schema["schema_id"]
        print(f"[{i}/{len(jobs)}] {ds} {sid} | claude/{prompt} remaining=${tracker.remaining():.2f}", flush=True)
        # Estimate headroom: ~$0.04 describe + ~$0.04 construct
        if not tracker.can_afford(0.08):
            print("Stopping before spend cap.")
            failures.append(
                {
                    "dataset": ds,
                    "schema_id": sid,
                    "describer": "claude_sonnet_4_6",
                    "prompt": prompt,
                    "constructor": "pending",
                    "stage": "e5a",
                    "reason": f"spend_cap remaining=${tracker.remaining():.4f}",
                }
            )
            break

        ck_desc = cache_key(
            stage="describe",
            dataset=ds,
            schema_id=sid,
            describer="claude_sonnet_4_6",
            prompt=prompt,
            model="claude_sonnet_4_6",
        )
        if ck_desc in raw_index and raw_index[ck_desc].get("ok"):
            desc = dict(raw_index[ck_desc])
            desc["reused"] = True
            print("  reuse describer cache")
        else:
            res = describe_schema(
                "claude_sonnet_4_6",
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
                    "describer": "claude_sonnet_4_6",
                    "ts": utc_now(),
                },
            )
            if desc.get("ok"):
                raw_index[ck_desc] = desc

        if not desc.get("ok"):
            ev = evaluate_prediction(schema["gold_meta"], schema["gold_ddl"], "")
            row = build_pipeline_row(
                schema=schema,
                describer="claude_sonnet_4_6",
                prompt=prompt,
                constructor="gpt_4o_mini",
                desc_call=desc,
                ctor_call=None,
                eval_res=ev,
                stage="e5a",
            )
            row["failure_reason"] = desc.get("error")
            row["constructor_note"] = "describer_failed"
            new_rows.append(row)
            failures.append(
                {
                    "dataset": ds,
                    "schema_id": sid,
                    "describer": "claude_sonnet_4_6",
                    "prompt": prompt,
                    "constructor": "",
                    "stage": "e5a",
                    "reason": desc.get("error"),
                }
            )
            continue

        nl = desc.get("text") or ""
        nl_hash = hashlib.sha256(nl.encode()).hexdigest()[:16]
        constructor = "gpt_4o_mini"
        ctor_fallback = False
        ck_ctor = cache_key(
            stage="construct",
            dataset=ds,
            schema_id=sid,
            describer="claude_sonnet_4_6",
            prompt=prompt,
            constructor=constructor,
            nl_hash=nl_hash,
        )

        ctor = None
        if clients["openai"].available:
            if ck_ctor in raw_index and raw_index[ck_ctor].get("ok"):
                ctor = dict(raw_index[ck_ctor])
                ctor["reused"] = True
            else:
                res = construct_schema(
                    "gpt_4o_mini",
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
                        "describer": "claude_sonnet_4_6",
                        "constructor": constructor,
                        "ts": utc_now(),
                    },
                )

        if not (ctor and ctor.get("ok")):
            # Documented fallback: Claude constructor when GPT-4o-mini unavailable
            constructor = "claude_sonnet_4_6"
            ctor_fallback = True
            ck_ctor = cache_key(
                stage="construct",
                dataset=ds,
                schema_id=sid,
                describer="claude_sonnet_4_6",
                prompt=prompt,
                constructor=constructor,
                nl_hash=nl_hash,
            )
            if ck_ctor in raw_index and raw_index[ck_ctor].get("ok"):
                ctor = dict(raw_index[ck_ctor])
                ctor["reused"] = True
                print("  reuse Claude constructor cache")
            else:
                res = construct_schema(
                    "claude_sonnet_4_6",
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
                        "describer": "claude_sonnet_4_6",
                        "constructor": constructor,
                        "constructor_fallback": True,
                        "ts": utc_now(),
                    },
                )
                if ctor.get("ok"):
                    raw_index[ck_ctor] = ctor

        if ctor and ctor.get("ok"):
            ev = evaluate_prediction(
                schema["gold_meta"],
                schema["gold_ddl"],
                ctor.get("ddl"),
                ctor.get("metadata"),
                parse_ok=True,
            )
        else:
            ev = evaluate_prediction(schema["gold_meta"], schema["gold_ddl"], "")

        row = build_pipeline_row(
            schema=schema,
            describer="claude_sonnet_4_6",
            prompt=prompt,
            constructor=constructor,
            desc_call=desc,
            ctor_call=ctor,
            eval_res=ev,
            stage="e5a",
        )
        row["constructor_note"] = (
            "claude_fallback_openai_unavailable" if ctor_fallback else "gpt_4o_mini"
        )
        if not (ctor and ctor.get("ok")):
            row["failure_reason"] = (ctor or {}).get("error")
            failures.append(
                {
                    "dataset": ds,
                    "schema_id": sid,
                    "describer": "claude_sonnet_4_6",
                    "prompt": prompt,
                    "constructor": constructor,
                    "stage": "e5a",
                    "reason": (ctor or {}).get("error"),
                }
            )
        new_rows.append(row)
        print(
            "  recon",
            row.get("reconstruction_valid"),
            "ref_f1",
            row.get("referential_f1"),
            "cost",
            row.get("total_cost_usd"),
            "ctor",
            constructor,
            "spend",
            tracker.snapshot()["spent_usd"],
        )

    # E5-B: fixed Claude detailed descriptions (proxy for blocked GPT-5.4-mini), Claude constructor
    print("E5-B proxy: fixed Claude detailed descriptions → Claude constructor")
    fixed = {}
    for r in new_rows:
        if r["prompt"] == "detailed" and int(r.get("desc_ok") or 0) == 1:
            fixed[(r["dataset"], r["schema_id"])] = r
    for schema in schemas:
        key = (schema["dataset"], schema["schema_id"])
        src = fixed.get(key)
        if not src:
            continue
        # Already have Claude detailed → Claude construct as E5-A; also record as e5b row
        e5b = dict(src)
        e5b["stage"] = "e5b"
        e5b["describer"] = "claude_sonnet_4_6"  # proxy; GPT-5.4-mini unavailable
        e5b["constructor"] = src.get("constructor")
        e5b["constructor_note"] = "e5b_proxy_fixed_claude_detailed_openai_blocked"
        new_rows.append(e5b)

    # Merge into existing per-schema CSV
    existing_path = OUT / "e5_per_schema.csv"
    existing = []
    if existing_path.exists() and existing_path.stat().st_size:
        with existing_path.open(encoding="utf-8") as f:
            existing = list(csv.DictReader(f))
    merged = merge_per_schema(existing, new_rows)
    write_csv(existing_path, merged)

    fail_path = OUT / "e5_failures.csv"
    old_fail = []
    if fail_path.exists() and fail_path.stat().st_size:
        with fail_path.open(encoding="utf-8") as f:
            old_fail = list(csv.DictReader(f))
    # Drop prior Claude e5a failures that we superseded
    old_fail = [
        r
        for r in old_fail
        if not (
            r.get("describer") == "claude_sonnet_4_6"
            and r.get("stage") in ("e5a", "e5b")
        )
    ]
    write_csv(fail_path, old_fail + failures)

    meta = {
        "finished_utc": utc_now(),
        "mode": args.mode,
        "component": "claude_fill",
        "n_schemas": len(schemas),
        "n_new_rows": len(new_rows),
        "spend": tracker.snapshot(),
        "openai_available": oa_ok,
        "openai_reason": oa_reason,
        "anthropic_available": an_ok,
        "anthropic_reason": an_reason,
        "constructor_fallback": "claude_sonnet_4_6 when gpt-4o-mini unavailable",
        "elapsed_s": time.time() - t0,
    }
    (OUT / "e5_claude_fill_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
