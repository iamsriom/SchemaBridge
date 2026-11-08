#!/usr/bin/env python3
"""Dedicated DeepSeek latency remount on a stratified subset (concurrency=1)."""

from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.e5.clients import LocalDeepSeekClient, describe_schema  # noqa: E402
from experiments.e5.cost_tracker import SpendTracker  # noqa: E402
from experiments.e5.gold import load_population  # noqa: E402
from experiments.e5.sample_select import build_sample_manifest, selected_records  # noqa: E402

OUT = HERE / "outputs"
CACHE = HERE / "cache" / "latency_runs.jsonl"


def main() -> int:
    n_per_ds = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    pop = load_population()
    manifest = build_sample_manifest(pop, per_dataset=40, seed=42)
    selected = selected_records(pop, manifest)
    # Stratify: take up to n_per_ds from each dataset, preferring diverse size tiers
    schemas = []
    for ds in ("enterprise145", "rschema", "schemabench"):
        cands = [s for s in selected if s["dataset"] == ds]
        # round-robin across size tiers
        by_size = {"Small": [], "Medium": [], "Large": []}
        for s in cands:
            by_size.setdefault(s["size_tier"], []).append(s)
        picked = []
        while len(picked) < n_per_ds:
            progressed = False
            for tier in ("Small", "Medium", "Large"):
                if by_size.get(tier):
                    picked.append(by_size[tier].pop(0))
                    progressed = True
                    if len(picked) >= n_per_ds:
                        break
            if not progressed:
                break
        schemas.extend(picked)

    tracker = SpendTracker()
    client = LocalDeepSeekClient(tracker)
    print("Loading DeepSeek...")
    client._ensure()
    clients = {"deepseek": client}
    print(f"Measuring latency on {len(schemas)} schemas × 2 prompts")
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for i, s in enumerate(schemas, 1):
        for prompt in ("basic", "detailed"):
            print(f"[{i}/{len(schemas)}] {s['dataset']} {s['schema_id']} {prompt}", flush=True)
            t0 = time.time()
            res = describe_schema(
                "deepseek", clients, database=s["database"], ddl=s["gold_ddl"], prompt_variant=prompt
            )
            d = res.to_dict()
            rec = {
                "dataset": s["dataset"],
                "schema_id": s["schema_id"],
                "columns": s["columns"],
                "tables": s["tables"],
                "size_tier": s["size_tier"],
                "prompt": prompt,
                "ok": int(bool(d.get("ok"))),
                "input_tokens": d.get("input_tokens"),
                "output_tokens": d.get("output_tokens"),
                "latency_s": d.get("latency_s"),
                "truncated": int(bool(d.get("truncated"))),
                "output_chars": len(d.get("text") or ""),
                "error": d.get("error"),
                "wall_s": time.time() - t0,
            }
            rows.append(rec)
            with CACHE.open("a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            print("  lat", rec["latency_s"], "out_tok", rec["output_tokens"], "chars", rec["output_chars"])

    out_csv = OUT / "e5_deepseek_latency.csv"
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("Wrote", out_csv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
