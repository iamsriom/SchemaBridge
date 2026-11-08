#!/usr/bin/env python3
"""E5-small: 30 schemata × 2 describers × 2 prompts → GPT-4o-mini constructor.

Hard spend cap: E5_SMALL_MAX_NEW_SPEND_USD = 5.00 (new API charges only; reuse free).
Concurrency = 1. Resumable via cache/raw_runs.jsonl.
Never substitutes Claude for GPT-4o-mini constructor.
Never zero-fills unexecuted rows.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import random
import sys
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Load secrets into env (never print)
for env, path in (
    ("OPENAI_API_KEY", "/data/openai_api.txt"),
    ("ANTHROPIC_API_KEY", "/data/anthropic.txt"),
):
    if not os.environ.get(env) and Path(path).is_file():
        line = next((ln.strip() for ln in Path(path).read_text().splitlines() if ln.strip()), "")
        if line:
            os.environ[env] = line

from experiments.e5.clients import (  # noqa: E402
    AnthropicChatClient,
    CallResult,
    OpenAIChatClient,
    describe_schema,
    extract_json_from_response,
    probe_anthropic,
    probe_openai,
)
from experiments.e5.prompts_e5 import CONSTRUCTOR_SYSTEM, constructor_user_content  # noqa: E402
import re  # noqa: E402


def salvage_ddl(text: str) -> tuple[str, dict | None]:
    """Recover DDL from truncated/malformed constructor JSON when possible."""
    text = (text or "").strip()
    if not text:
        return "", None
    try:
        parsed = extract_json_from_response(text)
        if isinstance(parsed, dict) and (parsed.get("ddl") or "").strip():
            return parsed.get("ddl") or "", parsed.get("metadata")
    except Exception:
        pass
    # Pull "ddl" string value even if JSON is truncated
    m = re.search(r'"ddl"\s*:\s*"((?:\\.|[^"\\])*)', text, re.DOTALL)
    if m:
        raw = m.group(1)
        try:
            ddl = json.loads(f'"{raw}')  # may fail if truncated
        except Exception:
            ddl = (
                raw.encode("utf-8")
                .decode("unicode_escape")
                .replace("\\n", "\n")
                .replace('\\"', '"')
            )
        if "CREATE" in ddl.upper():
            return ddl, None
    # Fallback: contiguous CREATE TABLE block
    m2 = re.search(r"(CREATE\s+TABLE[\s\S]+)", text, re.IGNORECASE)
    if m2:
        return m2.group(1).strip(), None
    return "", None


def construct_schema_robust(clients: dict, *, nl_text: str, database: str, text_number=None, n_cols: int = 50) -> CallResult:
    """GPT-4o-mini constructor with higher token budget + DDL salvage (no model substitution)."""
    system = CONSTRUCTOR_SYSTEM
    user = constructor_user_content(nl_text, database, text_number)
    # Scale max tokens with schema size; large detailed descriptions need room for JSON+DDL
    max_tokens = 4096 if n_cols <= 40 else (8192 if n_cols <= 120 else 16384)
    res = clients["openai"].chat(
        model_id="gpt-4o-mini",
        system=system,
        user=user,
        temperature=0.2,
        max_tokens=max_tokens,
        expect_json=True,
        max_retries=2,
        estimate_tokens=(min(8000, 500 + len(nl_text) // 3), max_tokens),
    )
    if res.ok and (res.ddl or "").strip():
        return res
    # If chat failed JSON parse, retry once without expect_json to capture raw text, then salvage
    raw = clients["openai"].chat(
        model_id="gpt-4o-mini",
        system=system,
        user=user,
        temperature=0.2,
        max_tokens=max_tokens,
        expect_json=False,
        max_retries=1,
        estimate_tokens=(min(8000, 500 + len(nl_text) // 3), max_tokens),
    )
    ddl, meta = salvage_ddl(raw.text or "")
    if ddl.strip():
        return CallResult(
            ok=True,
            text=raw.text,
            model_id=raw.model_id or "gpt-4o-mini",
            provider="openai",
            input_tokens=raw.input_tokens,
            output_tokens=raw.output_tokens,
            cached_tokens=raw.cached_tokens,
            latency_s=raw.latency_s,
            retry_count=(res.retry_count or 0) + (raw.retry_count or 0) + 1,
            cost_usd=((res.cost_usd or 0) + (raw.cost_usd or 0)) or None,
            cost_basis="provider_usage",
            ddl=ddl,
            metadata=meta,
            truncated=raw.truncated,
            raw_finish_reason=raw.raw_finish_reason,
            error=None,
        )
    # Keep original failure but attach raw text for logs
    res.text = raw.text or res.text
    res.ddl = ""
    res.error = res.error or raw.error or "constructor_ddl_salvage_failed"
    res.cost_usd = (res.cost_usd or 0) + (raw.cost_usd or 0) if (res.cost_usd or raw.cost_usd) else None
    return res

from experiments.e5.cost_tracker import SpendTracker, load_pricing  # noqa: E402
from experiments.e5.evaluate_wrap import evaluate_prediction  # noqa: E402
from experiments.e5.gold import load_population  # noqa: E402
from experiments.e5.run import (  # noqa: E402
    append_jsonl,
    build_pipeline_row,
    cache_key,
    flatten_eval,
    load_raw_index,
    utc_now,
    write_csv,
)
from src.metrics import ELEMENTS, micro_prf  # noqa: E402

OUT = HERE / "outputs"
CACHE = HERE / "cache"
RAW_JSONL = CACHE / "raw_runs.jsonl"
LEGACY_RAW = ROOT / "experiments/e5/cache/raw_runs.jsonl"
PER_SCHEMA = OUT / "e5_small_per_schema.csv"
STATE = OUT / "run_state.json"
ALL_TXT = HERE / "ALL_RESULTS.txt"
MAX_NEW_SPEND = float(os.environ.get("E5_SMALL_MAX_NEW_SPEND_USD", "5.00"))
SEED = 42
DESCRIBERS = ["gpt_5_4_mini", "claude_sonnet_4_6"]
PROMPTS = ["basic", "detailed"]
CONSTRUCTOR = "gpt_4o_mini"


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with (OUT / "run.log").open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_manifest() -> list[dict]:
    path = HERE / "sample_manifest.csv"
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def attach_gold(manifest: list[dict], population: list[dict]) -> list[dict]:
    idx = {(r["dataset"], r["schema_id"]): r for r in population}
    out = []
    for m in manifest:
        g = idx[(m["dataset"], m["schema_id"])]
        row = {**m, **{k: g[k] for k in ("gold_ddl", "gold_meta", "database", "text_number", "tables", "columns", "foreign_keys", "size_tier", "complexity_tier") if k in g}}
        row["tables"] = int(float(row["tables"]))
        row["columns"] = int(float(row["columns"]))
        out.append(row)
    return out


def merge_raw_indexes() -> dict[str, dict]:
    idx = load_raw_index(RAW_JSONL)
    # Also index legacy e5 cache for exact reuse
    legacy = load_raw_index(LEGACY_RAW)
    for k, v in legacy.items():
        if k not in idx:
            idx[k] = v
    return idx


def estimate_next_cost(describer: str, prompt: str, n_cols: int) -> float:
    """Conservative estimate for budget gate (describer + constructor)."""
    # rough token estimates
    in_tok = 400 + n_cols * 25 + (200 if prompt == "detailed" else 50)
    out_tok = 800 if prompt == "basic" else min(2500, 600 + n_cols * 30)
    ctor_in = out_tok + 300
    ctor_out = min(2000, 400 + n_cols * 20)
    pricing = load_pricing()
    mid = "gpt-5.4-mini" if describer == "gpt_5_4_mini" else "claude-sonnet-4-6"
    from experiments.e5.cost_tracker import compute_cost_usd

    d = compute_cost_usd(mid, in_tok, out_tok, pricing) or 0.05
    c = compute_cost_usd("gpt-4o-mini", ctor_in, ctor_out, pricing) or 0.01
    return float(d + c) * 1.25  # safety margin


def run_one(schema, describer, prompt, clients, raw_index, tracker) -> dict:
    ds, sid = schema["dataset"], schema["schema_id"]
    ck_desc = cache_key(
        stage="describe",
        dataset=ds,
        schema_id=sid,
        describer=describer,
        prompt=prompt,
        model=describer,
    )
    reused_desc = False
    if ck_desc in raw_index and raw_index[ck_desc].get("ok") and (raw_index[ck_desc].get("text") or "").strip():
        desc = dict(raw_index[ck_desc])
        desc["reused"] = True
        reused_desc = True
    else:
        est = estimate_next_cost(describer, prompt, schema["columns"])
        if not tracker.can_afford(est):
            return {
                "dataset": ds,
                "schema_id": sid,
                "describer": describer,
                "prompt": prompt,
                "constructor": CONSTRUCTOR,
                "status": "not_executed_budget",
                "desc_ok": 0,
                "ctor_ok": 0,
                "reconstruction_valid": 0,
                "tables": schema["tables"],
                "columns": schema["columns"],
                "size_tier": schema["size_tier"],
                "complexity_tier": schema["complexity_tier"],
            }
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
        # Spend charged inside OpenAI/Anthropic clients via shared tracker.
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
        row = build_pipeline_row(
            schema=schema,
            describer=describer,
            prompt=prompt,
            constructor=CONSTRUCTOR,
            desc_call=desc,
            ctor_call=None,
            eval_res=evaluate_prediction(schema["gold_meta"], schema["gold_ddl"], ""),
            stage="e5_small",
        )
        row["status"] = "desc_failed"
        row["attempted"] = 1
        return row

    nl = desc.get("text") or ""
    nl_hash = hashlib.sha256(nl.encode()).hexdigest()[:16]
    ck_ctor = cache_key(
        stage="construct",
        dataset=ds,
        schema_id=sid,
        describer=describer,
        prompt=prompt,
        constructor=CONSTRUCTOR,
        nl_hash=nl_hash,
    )
    if ck_ctor in raw_index and raw_index[ck_ctor].get("ok"):
        ctor = dict(raw_index[ck_ctor])
        ctor["reused"] = True
    else:
        # budget for constructor only if desc was reused (desc already charged or free)
        est_ctor = estimate_next_cost("gpt_5_4_mini", "basic", schema["columns"]) * 0.4
        if not reused_desc:
            pass  # already gated full estimate
        elif not tracker.can_afford(est_ctor):
            row = build_pipeline_row(
                schema=schema,
                describer=describer,
                prompt=prompt,
                constructor=CONSTRUCTOR,
                desc_call=desc,
                ctor_call=None,
                eval_res=evaluate_prediction(schema["gold_meta"], schema["gold_ddl"], ""),
                stage="e5_small",
            )
            row["status"] = "not_executed_budget_ctor"
            row["attempted"] = 1
            return row
        res = construct_schema_robust(
            clients,
            nl_text=nl,
            database=schema["database"],
            text_number=schema.get("text_number"),
            n_cols=int(schema.get("columns") or 50),
        )
        ctor = res.to_dict()
        ctor["cache_key"] = ck_ctor
        ctor["reused"] = False
        # Spend charged inside OpenAI client via shared tracker.
        append_jsonl(
            RAW_JSONL,
            {
                **ctor,
                "stage": "construct",
                "dataset": ds,
                "schema_id": sid,
                "prompt": prompt,
                "describer": describer,
                "constructor": CONSTRUCTOR,
                "nl_hash": nl_hash,
                "ts": utc_now(),
            },
        )
        if ctor.get("ok"):
            raw_index[ck_ctor] = ctor

    pred_ddl = ctor.get("ddl") or ""
    # Prefer metadata from parsed JSON if present
    pred_meta = ctor.get("metadata")
    ev = evaluate_prediction(schema["gold_meta"], schema["gold_ddl"], pred_ddl, pred_meta)
    row = build_pipeline_row(
        schema=schema,
        describer=describer,
        prompt=prompt,
        constructor=CONSTRUCTOR,
        desc_call=desc,
        ctor_call=ctor,
        eval_res=ev,
        stage="e5_small",
    )
    row["status"] = "completed" if ctor.get("ok") else "ctor_failed"
    row["attempted"] = 1
    row["nl_hash"] = nl_hash
    return row


def micro_group(rows: list[dict], dim: str) -> float | None:
    if not rows:
        return None
    g = sum(int(float(r.get(f"{dim}_gold") or 0)) for r in rows)
    rec = sum(int(float(r.get(f"{dim}_recreated") or 0)) for r in rows)
    m = sum(int(float(r.get(f"{dim}_matched") or 0)) for r in rows)
    return micro_prf(g, rec, m)["f1"]


def mean_key(rows: list[dict], key: str) -> float | None:
    vals = [float(r[key]) for r in rows if r.get(key) not in (None, "")]
    return sum(vals) / len(vals) if vals else None


def median(vals: list[float]) -> float | None:
    if not vals:
        return None
    s = sorted(vals)
    n = len(s)
    return s[n // 2] if n % 2 else 0.5 * (s[n // 2 - 1] + s[n // 2])


def p95(vals: list[float]) -> float | None:
    if len(vals) < 2:
        return median(vals)
    s = sorted(vals)
    idx = int(round(0.95 * (len(s) - 1)))
    return s[idx]


def completed_rows(rows: list[dict]) -> list[dict]:
    return [r for r in rows if r.get("status") == "completed" and str(r.get("ctor_ok")) in ("1", "True", "true")]


def analyze(rows: list[dict], schemas: list[dict]) -> dict[str, Any]:
    done = completed_rows(rows)
    # Table 1 main
    t1 = []
    for ds in ("rschema", "schemabench", "enterprise145"):
        for desc in DESCRIBERS:
            basic = [r for r in done if r["dataset"] == ds and r["describer"] == desc and r["prompt"] == "basic"]
            detailed = [r for r in done if r["dataset"] == ds and r["describer"] == desc and r["prompt"] == "detailed"]
            # matched schema IDs for fair B/D
            ids_b = {r["schema_id"] for r in basic}
            ids_d = {r["schema_id"] for r in detailed}
            matched = ids_b & ids_d
            b = [r for r in basic if r["schema_id"] in matched]
            d = [r for r in detailed if r["schema_id"] in matched]
            t1.append(
                {
                    "Dataset": ds,
                    "Describer": "GPT-5.4-mini" if desc == "gpt_5_4_mini" else "Claude Sonnet 4.6",
                    "N": len(matched),
                    "Ref_F1_B": micro_group(b, "referential"),
                    "Ref_F1_D": micro_group(d, "referential"),
                    "Domain_F1_B": micro_group(b, "domain"),
                    "Domain_F1_D": micro_group(d, "domain"),
                    "nGED_B": mean_key(b, "nged"),
                    "nGED_D": mean_key(d, "nged"),
                    "Cost_B": mean_key(b, "total_cost_usd"),
                    "Cost_D": mean_key(d, "total_cost_usd"),
                    "Lat_B": mean_key(b, "total_latency_s"),
                    "Lat_D": mean_key(d, "total_latency_s"),
                    "N_basic_all": len(basic),
                    "N_detailed_all": len(detailed),
                }
            )

    # Table 2 scalability
    t2 = []
    for ds in ("rschema", "schemabench", "enterprise145"):
        for size in ("Small", "Medium", "Large"):
            for desc in DESCRIBERS:
                for prompt in PROMPTS:
                    sub = [
                        r
                        for r in done
                        if r["dataset"] == ds
                        and r["size_tier"] == size
                        and r["describer"] == desc
                        and r["prompt"] == prompt
                    ]
                    if not sub:
                        continue
                    lats = [float(r["total_latency_s"]) for r in sub if r.get("total_latency_s") not in (None, "")]
                    t2.append(
                        {
                            "Dataset": ds,
                            "Size": size,
                            "N": len(sub),
                            "Describer": "GPT-5.4-mini" if desc == "gpt_5_4_mini" else "Claude-4.6",
                            "Prompt": prompt,
                            "Referential_F1": micro_group(sub, "referential"),
                            "Domain_F1": micro_group(sub, "domain"),
                            "nGED": mean_key(sub, "nged"),
                            "Latency_median": median(lats),
                            "Latency_p95": p95(lats) if len(lats) >= 3 else median(lats),
                            "Cost_mean": mean_key(sub, "total_cost_usd"),
                            "Valid_pct": 100.0 * sum(1 for r in sub if str(r.get("reconstruction_valid")) in ("1", "True")) / len(sub),
                        }
                    )

    # Table 3 cost vs fidelity
    t3 = []
    for ds in ("rschema", "schemabench", "enterprise145"):
        for desc in DESCRIBERS:
            for prompt in PROMPTS:
                sub = [r for r in done if r["dataset"] == ds and r["describer"] == desc and r["prompt"] == prompt]
                if not sub:
                    continue
                lats = [float(r["total_latency_s"]) for r in sub if r.get("total_latency_s") not in (None, "")]
                t3.append(
                    {
                        "Dataset": ds,
                        "Model": "GPT-5.4-mini" if desc == "gpt_5_4_mini" else "Claude Sonnet 4.6",
                        "Prompt": prompt,
                        "N": len(sub),
                        "Referential_F1": micro_group(sub, "referential"),
                        "Domain_F1": micro_group(sub, "domain"),
                        "nGED": mean_key(sub, "nged"),
                        "Median_latency": median(lats),
                        "Mean_cost": mean_key(sub, "total_cost_usd"),
                        "Valid_DDL_pct": 100.0
                        * sum(1 for r in sub if str(r.get("reconstruction_valid")) in ("1", "True"))
                        / len(sub),
                    }
                )

    # DeepSeek matched comparison
    e5 = list(csv.DictReader(open(ROOT / "experiments/e5/outputs/e5_per_schema.csv")))
    sample_ids = {(s["dataset"], s["schema_id"]) for s in schemas}
    ds_matched = []
    for r in e5:
        if (
            r.get("stage") == "e5a"
            and r.get("describer") == "deepseek"
            and r.get("prompt") == "basic"
            and r.get("reconstruction_valid") == "1"
            and (r["dataset"], r["schema_id"]) in sample_ids
        ):
            ds_matched.append(r)
    deepseek_cmp = []
    for ds in ("rschema", "schemabench"):
        sub = [r for r in ds_matched if r["dataset"] == ds]
        gpt = [r for r in done if r["dataset"] == ds and r["describer"] == "gpt_5_4_mini" and r["prompt"] == "basic"]
        # pair on schema_id
        ids = {r["schema_id"] for r in sub} & {r["schema_id"] for r in gpt}
        dsub = [r for r in sub if r["schema_id"] in ids]
        gsub = [r for r in gpt if r["schema_id"] in ids]
        deepseek_cmp.append(
            {
                "Dataset": ds,
                "Paired_N": len(ids),
                "DeepSeek_Ref_F1": micro_group(dsub, "referential"),
                "GPT_Ref_F1": micro_group(gsub, "referential"),
                "DeepSeek_Domain_F1": micro_group(dsub, "domain"),
                "GPT_Domain_F1": micro_group(gsub, "domain"),
                "DeepSeek_nGED": mean_key(dsub, "nged"),
                "GPT_nGED": mean_key(gsub, "nged"),
                "DeepSeek_Cost": "N/A (open-weight)",
                "GPT_Cost": mean_key(gsub, "total_cost_usd"),
            }
        )

    # Bootstrap CI for GPT vs Claude Ref F1 (matched schemas, basic)
    rng = random.Random(SEED)
    boot = {}
    for ds in ("rschema", "schemabench", "enterprise145"):
        for prompt in PROMPTS:
            g = {r["schema_id"]: r for r in done if r["dataset"] == ds and r["describer"] == "gpt_5_4_mini" and r["prompt"] == prompt}
            c = {r["schema_id"]: r for r in done if r["dataset"] == ds and r["describer"] == "claude_sonnet_4_6" and r["prompt"] == prompt}
            ids = sorted(set(g) & set(c))
            if len(ids) < 2:
                continue
            diffs = []
            cost_ratios = []
            for _ in range(1000):
                sample = [ids[rng.randrange(len(ids))] for _ in range(len(ids))]
                gs = [g[i] for i in sample]
                cs = [c[i] for i in sample]
                rg = micro_group(gs, "referential") or 0
                rc = micro_group(cs, "referential") or 0
                diffs.append(rc - rg)
                cg = mean_key(gs, "total_cost_usd") or 0
                cc = mean_key(cs, "total_cost_usd") or 0
                if cg > 0:
                    cost_ratios.append(cc / cg)
            diffs.sort()
            cost_ratios.sort()
            boot[f"{ds}:{prompt}"] = {
                "N": len(ids),
                "delta_ref_claude_minus_gpt": mean_key(
                    [{"x": d} for d in diffs], "x"
                )
                if False
                else (sum(diffs) / len(diffs)),
                "delta_ref_ci95": (diffs[24], diffs[974]) if len(diffs) == 1000 else None,
                "cost_ratio_claude_over_gpt": sum(cost_ratios) / len(cost_ratios) if cost_ratios else None,
                "cost_ratio_ci95": (cost_ratios[24], cost_ratios[974]) if len(cost_ratios) == 1000 else None,
            }

    return {"table1": t1, "table2": t2, "table3": t3, "deepseek": deepseek_cmp, "bootstrap": boot}


def fmt3(x) -> str:
    if x is None:
        return "N/A"
    return f"{float(x):.3f}"


def fmt4(x) -> str:
    if x is None:
        return "N/A"
    return f"{float(x):.4f}"


def write_latex(analysis: dict, spend: dict) -> None:
    t1 = analysis["table1"]
    lines = [
        r"% Auto-generated E5-small main table",
        r"\begin{table}[t]",
        r"\centering",
        r"\caption{E5 scalability and cost on a fixed sample of 30 schemata "
        r"(10 per dataset). Describer $\rightarrow$ GPT-4o-mini constructor. "
        r"B/D = basic/detailed prompts. Costs are provider-usage USD. "
        r"$N$ = schemata with both prompts completed.}",
        r"\label{tab:e5_cost}",
        r"\footnotesize",
        r"\setlength{\tabcolsep}{2.5pt}",
        r"\begin{tabular}{@{}l l c cc cc cc@{}}",
        r"\toprule",
        r"Dataset & Describer & $N$ & Ref$_B$ & Ref$_D$ & Dom$_B$ & Dom$_D$ & \$\,$_B$ & \$\,$_D$ \\",
        r"\midrule",
    ]
    for r in t1:
        ds = {"rschema": "RSchema", "schemabench": "SchemaBench", "enterprise145": "Enterprise"}.get(r["Dataset"], r["Dataset"])
        desc = "GPT-5.4-m" if "GPT" in r["Describer"] else "Claude-4.6"
        lines.append(
            f"{ds} & {desc} & {r['N']} & {fmt3(r['Ref_F1_B'])} & {fmt3(r['Ref_F1_D'])} & "
            f"{fmt3(r['Domain_F1_B'])} & {fmt3(r['Domain_F1_D'])} & {fmt4(r['Cost_B'])} & {fmt4(r['Cost_D'])} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
        "",
    ]
    (HERE / "tables" / "e5_cost_table.tex").write_text("\n".join(lines), encoding="utf-8")

    # scalability table*
    t2 = analysis["table2"]
    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{E5 structural scalability by schema size (attempted-only completed round-trips).}",
        r"\label{tab:e5_scalability}",
        r"\footnotesize",
        r"\begin{tabular}{@{}l l r l l ccc cc@{}}",
        r"\toprule",
        r"Dataset & Size & $N$ & Desc. & Prompt & Ref & Dom & nGED & Lat$_\mathrm{med}$ & Cost \\",
        r"\midrule",
    ]
    for r in t2:
        lines.append(
            f"{r['Dataset']} & {r['Size']} & {r['N']} & {r['Describer']} & {r['Prompt']} & "
            f"{fmt3(r['Referential_F1'])} & {fmt3(r['Domain_F1'])} & {fmt3(r['nGED'])} & "
            f"{fmt3(r['Latency_median'])} & {fmt4(r['Cost_mean'])} \\\\"
        )
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table*}", ""]
    (HERE / "tables" / "e5_scalability_table.tex").write_text("\n".join(lines), encoding="utf-8")

    # cost fidelity
    t3 = analysis["table3"]
    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\caption{E5 cost--fidelity summary (completed round-trips only).}",
        r"\label{tab:e5_cost_fidelity}",
        r"\footnotesize",
        r"\begin{tabular}{@{}l l l c ccc cc c@{}}",
        r"\toprule",
        r"Dataset & Model & Prompt & $N$ & Ref & Dom & nGED & Lat$_\mathrm{med}$ & \$/sch. & Valid\% \\",
        r"\midrule",
    ]
    for r in t3:
        lines.append(
            f"{r['Dataset']} & {r['Model'].replace('Claude Sonnet 4.6','Claude-4.6').replace('GPT-5.4-mini','GPT-5.4-m')} & "
            f"{r['Prompt']} & {r['N']} & {fmt3(r['Referential_F1'])} & {fmt3(r['Domain_F1'])} & {fmt3(r['nGED'])} & "
            f"{fmt3(r['Median_latency'])} & {fmt4(r['Mean_cost'])} & {r['Valid_DDL_pct']:.0f} \\\\"
        )
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table*}"]
    # fix accidental end{table*} 
    text = "\n".join(lines).replace(r"\end{table*}", r"\end{table}")
    (HERE / "tables" / "e5_cost_fidelity_table.tex").write_text(text, encoding="utf-8")


def write_figures(rows: list[dict]) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as e:
        log(f"matplotlib unavailable: {e}")
        return
    done = completed_rows(rows)
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.2))
    colors = {"gpt_5_4_mini": "#1f77b4", "claude_sonnet_4_6": "#d62728"}
    markers = {"basic": "o", "detailed": "s"}
    for ax, ykey, ylab in zip(
        axes,
        ("referential_f1", "total_latency_s", "total_cost_usd"),
        ("Referential F1", "E2E latency (s)", "Cost ($/schema)"),
    ):
        for desc in DESCRIBERS:
            for prompt in PROMPTS:
                sub = [r for r in done if r["describer"] == desc and r["prompt"] == prompt]
                xs, ys = [], []
                for r in sub:
                    if r.get(ykey) in (None, "") or r.get("columns") in (None, ""):
                        continue
                    xs.append(float(r["columns"]))
                    ys.append(float(r[ykey]))
                if not xs:
                    continue
                ax.scatter(
                    xs,
                    ys,
                    c=colors[desc],
                    marker=markers[prompt],
                    alpha=0.75,
                    s=28,
                    label=f"{'GPT' if 'gpt' in desc else 'Claude'}-{prompt[0].upper()}",
                )
        ax.set_xlabel("# columns")
        ax.set_ylabel(ylab)
        ax.grid(True, alpha=0.3)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=4, fontsize=8, frameon=False)
    fig.suptitle("E5-small: fidelity, latency, and cost vs schema size", y=1.08, fontsize=11)
    fig.tight_layout()
    fig.savefig(HERE / "figures" / "e5_scalability.pdf", bbox_inches="tight")
    fig.savefig(HERE / "figures" / "e5_scalability.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    log("Wrote figures")


def write_paper(analysis: dict, spend: dict, counts: dict) -> None:
    t1 = analysis["table1"]
    # pick key numbers
    def find(ds, model_substr):
        for r in t1:
            if r["Dataset"] == ds and model_substr in r["Describer"]:
                return r
        return None

    g_rs = find("rschema", "GPT")
    c_rs = find("rschema", "Claude")
    text = r"""\subsection{E5: Scalability and Cost}
\label{sec:e5}

\paragraph{Setup.}
We evaluate end-to-end schema reconstruction cost and scalability on a fixed
sample of 30 schemata (10 RSchema, 10 SchemaBench, 10 Enterprise-145; seed~42),
stratified by size (Small/Medium/Large) and constraint complexity.
Each gold DDL is verbalized by GPT-5.4-mini or Claude Sonnet~4.6 under the
exact E1 basic and detailed prompts, then reconstructed by a fixed GPT-4o-mini
constructor (E2 protocol). Metrics are micro-averaged structural F1 and mean
nGED; latency is sequential wall-clock; costs use provider token usage and
frozen prices. Matching prior API responses are reused; unexecuted calls are
not zero-scored. New API spend was capped at \$5.

\paragraph{Results.}
Table~\ref{tab:e5_cost} summarizes matched basic/detailed outcomes.
"""
    if g_rs and g_rs["N"]:
        text += (
            f"On RSchema ($N{{=}}{g_rs['N']}$ matched), GPT-5.4-mini achieves "
            f"Ref.\\ F1 {fmt3(g_rs['Ref_F1_B'])}/{fmt3(g_rs['Ref_F1_D'])} (B/D) at "
            f"mean cost \\${fmt4(g_rs['Cost_B'])}/\\${fmt4(g_rs['Cost_D'])}. "
        )
    if c_rs and c_rs["N"]:
        text += (
            f"Claude Sonnet~4.6 reaches Ref.\\ F1 {fmt3(c_rs['Ref_F1_B'])}/{fmt3(c_rs['Ref_F1_D'])} "
            f"at \\${fmt4(c_rs['Cost_B'])}/\\${fmt4(c_rs['Cost_D'])}. "
        )
    text += (
        f"Completed round-trips: {counts.get('completed',0)}/{counts.get('planned',120)}; "
        f"new API spend \\${spend.get('spent_usd',0):.4f}. "
        "Larger schemata tend to raise tokens, latency, and cost; domain integrity "
        "remains the weakest dimension. Detailed prompting usually increases cost; "
        "fidelity gains are dataset- and model-dependent and are not claimed significant "
        f"on this sample. DeepSeek paired comparisons use only overlapping schema IDs "
        f"(see extended results)."
        "\n"
    )
    (HERE / "paper_e5.tex").write_text(text, encoding="utf-8")


def write_all_results_txt(
    schemas, rows, analysis, spend, probes, n_new, n_reused, counts
) -> None:
    lines = []
    lines.append("=" * 78)
    lines.append("SchemaBridge E5-SMALL: Scalability and Cost — COMPLETE RESULTS")
    lines.append(f"Generated (UTC): {utc_now()}")
    lines.append("=" * 78)
    lines.append("")
    lines.append("1. SAMPLE")
    lines.append(f"   Total schemata selected: {len(schemas)}")
    lines.append(f"   Size distribution: {dict(Counter(s['size_tier'] for s in schemas))}")
    lines.append(f"   Complexity: {dict(Counter(s['complexity_tier'] for s in schemas))}")
    lines.append(f"   DeepSeek overlap: {sum(int(float(s.get('in_deepseek_e5_sample') or 0)) for s in schemas)}")
    lines.append("   IDs:")
    for s in schemas:
        lines.append(
            f"     {s['dataset']:14} {s['schema_id']:40} {s['size_tier']:6} "
            f"T={s['tables']} C={s['columns']} CX={s['complexity_tier']}"
        )
    lines.append("")
    lines.append("2. EXECUTION")
    lines.append(f"   Planned pipelines: 120 (30 × 2 describers × 2 prompts)")
    lines.append(f"   Completed: {counts.get('completed',0)}")
    lines.append(f"   Desc failed: {counts.get('desc_failed',0)}")
    lines.append(f"   Ctor failed: {counts.get('ctor_failed',0)}")
    lines.append(f"   Not executed (budget): {counts.get('not_executed',0)}")
    lines.append(f"   Valid DDL reconstructions: {counts.get('valid',0)}")
    lines.append(f"   New API requests (approx charged stages): {n_new}")
    lines.append(f"   Reused cached responses: {n_reused}")
    lines.append(f"   API probes: openai={probes['openai']} claude={probes['claude']}")
    lines.append(f"   New spend USD: {spend.get('spent_usd',0):.6f} / cap {spend.get('max_spend_usd',5):.2f}")
    lines.append("")
    lines.append("3. TABLE 1 — MAIN E5 RESULTS (matched B/D)")
    lines.append(
        f"{'Dataset':14} {'Describer':18} {'N':>3} {'RefB':>6} {'RefD':>6} {'DomB':>6} {'DomD':>6} {'$B':>8} {'$D':>8} {'nGEDB':>6} {'nGEDD':>6}"
    )
    for r in analysis["table1"]:
        lines.append(
            f"{r['Dataset']:14} {r['Describer'][:18]:18} {r['N']:3d} "
            f"{fmt3(r['Ref_F1_B']):>6} {fmt3(r['Ref_F1_D']):>6} "
            f"{fmt3(r['Domain_F1_B']):>6} {fmt3(r['Domain_F1_D']):>6} "
            f"{fmt4(r['Cost_B']):>8} {fmt4(r['Cost_D']):>8} "
            f"{fmt3(r['nGED_B']):>6} {fmt3(r['nGED_D']):>6}"
        )
    lines.append("")
    lines.append("4. TABLE 2 — SCALABILITY BY SIZE")
    for r in analysis["table2"]:
        lines.append(
            f"  {r['Dataset']:14} {r['Size']:6} N={r['N']:2} {r['Describer']:10} {r['Prompt']:8} "
            f"Ref={fmt3(r['Referential_F1'])} Dom={fmt3(r['Domain_F1'])} nGED={fmt3(r['nGED'])} "
            f"LatMed={fmt3(r['Latency_median'])} Cost={fmt4(r['Cost_mean'])} Valid%={r['Valid_pct']:.0f}"
        )
    lines.append("")
    lines.append("5. TABLE 3 — COST VS FIDELITY")
    for r in analysis["table3"]:
        lines.append(
            f"  {r['Dataset']:14} {r['Model']:18} {r['Prompt']:8} N={r['N']:2} "
            f"Ref={fmt3(r['Referential_F1'])} Dom={fmt3(r['Domain_F1'])} nGED={fmt3(r['nGED'])} "
            f"Lat={fmt3(r['Median_latency'])} Cost={fmt4(r['Mean_cost'])} Valid%={r['Valid_DDL_pct']:.0f}"
        )
    lines.append("")
    lines.append("6. BASIC VS DETAILED (from Table 1 deltas)")
    for r in analysis["table1"]:
        if not r["N"]:
            continue
        dref = (r["Ref_F1_D"] or 0) - (r["Ref_F1_B"] or 0) if r["Ref_F1_D"] is not None and r["Ref_F1_B"] is not None else None
        dcost = (r["Cost_D"] or 0) - (r["Cost_B"] or 0) if r["Cost_D"] is not None and r["Cost_B"] is not None else None
        lines.append(
            f"  {r['Dataset']:14} {r['Describer'][:18]:18} ΔRef={fmt3(dref)} ΔCost={fmt4(dcost)} "
            f"ΔLat={fmt3((r['Lat_D'] or 0)-(r['Lat_B'] or 0) if r['Lat_D'] and r['Lat_B'] else None)}"
        )
    lines.append("")
    lines.append("7. GPT vs CLAUDE (bootstrap exploratory)")
    for k, v in analysis["bootstrap"].items():
        lines.append(f"  {k}: N={v['N']} mean ΔRef(Claude-GPT)={v['delta_ref_claude_minus_gpt']:.4f} "
                     f"CI95={v['delta_ref_ci95']} cost_ratio={v['cost_ratio_claude_over_gpt']}")
    lines.append("")
    lines.append("8. DEEPSEEK PAIRED (matching schema IDs only)")
    for r in analysis["deepseek"]:
        lines.append(
            f"  {r['Dataset']:14} Paired_N={r['Paired_N']} "
            f"DS_Ref={fmt3(r['DeepSeek_Ref_F1'])} GPT_Ref={fmt3(r['GPT_Ref_F1'])} "
            f"DS_Dom={fmt3(r['DeepSeek_Domain_F1'])} GPT_Dom={fmt3(r['GPT_Domain_F1'])} "
            f"DS_nGED={fmt3(r['DeepSeek_nGED'])} GPT_nGED={fmt3(r['GPT_nGED'])} "
            f"GPT_Cost={fmt4(r['GPT_Cost'])} DS_Cost={r['DeepSeek_Cost']}"
        )
    lines.append("")
    lines.append("9. PER-SCHEMA COMPLETED ROWS (compact)")
    for r in completed_rows(rows):
        lines.append(
            f"  {r['dataset']:14} {r['schema_id'][:36]:36} {r['describer'][:12]:12} {r['prompt']:8} "
            f"size={r['size_tier']:6} Ref={fmt3(r.get('referential_f1'))} Dom={fmt3(r.get('domain_f1'))} "
            f"nGED={fmt3(r.get('nged'))} lat={fmt3(r.get('total_latency_s'))} "
            f"cost={fmt4(r.get('total_cost_usd'))} valid={r.get('reconstruction_valid')} "
            f"reuseD={r.get('desc_reused')} reuseC={r.get('ctor_reused')}"
        )
    lines.append("")
    lines.append("10. MAIN FINDINGS")
    lines.append("  - See paper_e5.tex and tables/; numbers above are authoritative.")
    lines.append("  - Unexecuted pipelines are omitted from F1/nGED/cost aggregates.")
    lines.append("  - Constructor always GPT-4o-mini; no silent model substitution.")
    lines.append("")
    lines.append("11. ARTIFACT PATHS")
    lines.append(f"  Manifest: {HERE/'sample_manifest.csv'}")
    lines.append(f"  Per-schema CSV: {PER_SCHEMA}")
    lines.append(f"  Raw cache: {RAW_JSONL}")
    lines.append(f"  Tables: {HERE/'tables'}")
    lines.append(f"  Figures: {HERE/'figures'}")
    lines.append(f"  Paper: {HERE/'paper_e5.tex'}")
    lines.append(f"  This file: {ALL_TXT}")
    lines.append("")
    lines.append("=" * 78)
    ALL_TXT.write_text("\n".join(lines), encoding="utf-8")
    log(f"Wrote {ALL_TXT}")


def save_csvs(analysis: dict, rows: list[dict]) -> None:
    def dump(name, data, fmt=True):
        out = []
        for r in data:
            row = {}
            for k, v in r.items():
                if fmt and isinstance(v, float):
                    row[k] = f"{v:.6f}"
                else:
                    row[k] = v
            out.append(row)
        write_csv(OUT / name, out)
        write_csv(HERE / "tables" / name, out)

    dump("table1_main.csv", analysis["table1"])
    dump("table2_scalability.csv", analysis["table2"])
    dump("table3_cost_fidelity.csv", analysis["table3"])
    dump("deepseek_paired.csv", analysis["deepseek"])
    write_csv(PER_SCHEMA, rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    (HERE / "tables").mkdir(exist_ok=True)
    (HERE / "figures").mkdir(exist_ok=True)
    (OUT / "run.log").write_text("", encoding="utf-8")

    log("=== E5-small start ===")
    # Ensure manifest
    if not (HERE / "sample_manifest.csv").exists():
        import subprocess

        subprocess.check_call([sys.executable, str(HERE / "scripts" / "select_sample.py")])

    manifest = load_manifest()
    pop = load_population()
    schemas = attach_gold(manifest, pop)
    assert len(schemas) == 30

    probes = {
        "openai": probe_openai("gpt-4o-mini"),
        "gpt54": probe_openai("gpt-5.4-mini"),
        "claude": probe_anthropic("claude-sonnet-4-6"),
    }
    log(f"Probes: {probes}")
    if not probes["openai"][0] or not probes["gpt54"][0]:
        log("FATAL: OpenAI unavailable")
        sys.exit(2)
    if not probes["claude"][0]:
        log("WARN: Claude unavailable — will skip Claude cells")

    pricing = load_pricing()
    tracker = SpendTracker(max_spend_usd=MAX_NEW_SPEND)
    # Restore prior new spend from this experiment's raw log (exclude reused).
    prior_spend = 0.0
    if RAW_JSONL.exists():
        with RAW_JSONL.open(encoding="utf-8") as f:
            for line in f:
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                if d.get("reused"):
                    continue
                c = d.get("cost_usd")
                if c is not None:
                    prior_spend += float(c)
    if prior_spend > 0:
        tracker.charge(prior_spend, {"stage": "restore_prior_spend"})
        log(f"Restored prior new spend ${prior_spend:.4f}")
    clients = {
        "openai": OpenAIChatClient(pricing=pricing, tracker=tracker),
        "anthropic": AnthropicChatClient(pricing=pricing, tracker=tracker) if probes["claude"][0] else None,
    }

    raw_index = merge_raw_indexes()
    log(f"Raw cache entries: {len(raw_index)}")

    # Size-first then interleave models/prompts (Small/Medium before Large for budget).
    size_rank = {"Small": 0, "Medium": 1, "Large": 2}
    schemas_ordered = sorted(
        schemas,
        key=lambda s: (size_rank.get(s["size_tier"], 9), int(s["columns"]), s["schema_id"]),
    )
    jobs = []
    for s in schemas_ordered:
        for desc in DESCRIBERS:
            if desc == "claude_sonnet_4_6" and not probes["claude"][0]:
                continue
            for prompt in PROMPTS:
                jobs.append((s, desc, prompt))
    rng = random.Random(SEED)
    by_cell: dict[tuple[str, str], list] = defaultdict(list)
    for s, d, p in jobs:
        by_cell[(d, p)].append(s)
    interleaved = []
    cells = list(by_cell.keys())
    rng.shuffle(cells)
    max_len = max(len(v) for v in by_cell.values()) if by_cell else 0
    for i in range(max_len):
        for cell in cells:
            if i < len(by_cell[cell]):
                interleaved.append((by_cell[cell][i], cell[0], cell[1]))
    # Stable size-major order while keeping cell interleave within size bands
    interleaved.sort(
        key=lambda t: (
            size_rank.get(t[0]["size_tier"], 9),
            int(t[0]["columns"]),
            t[0]["schema_id"],
            t[1],
            t[2],
        )
    )
    rows: list[dict] = []
    n_new = 0
    n_reused = 0
    # Resume: load existing per-schema if present
    existing = {}
    if PER_SCHEMA.exists() and PER_SCHEMA.stat().st_size > 0:
        for r in csv.DictReader(PER_SCHEMA.open()):
            existing[(r["dataset"], r["schema_id"], r["describer"], r["prompt"])] = r

    for i, (schema, desc, prompt) in enumerate(interleaved, 1):
        key = (schema["dataset"], schema["schema_id"], desc, prompt)
        if key in existing and existing[key].get("status") == "completed":
            rows.append(existing[key])
            n_reused += 1
            log(f"[{i}/{len(interleaved)}] RESUME {key}")
            continue
        log(f"[{i}/{len(interleaved)}] RUN {schema['dataset']} {schema['schema_id']} {desc} {prompt} | spent=${tracker.spent_usd:.4f}")
        try:
            row = run_one(schema, desc, prompt, clients, raw_index, tracker)
        except Exception as e:
            log(f"EXCEPTION: {e}\n{traceback.format_exc()}")
            row = {
                "dataset": schema["dataset"],
                "schema_id": schema["schema_id"],
                "describer": desc,
                "prompt": prompt,
                "constructor": CONSTRUCTOR,
                "status": "exception",
                "desc_error": str(e),
                "tables": schema["tables"],
                "columns": schema["columns"],
                "size_tier": schema["size_tier"],
                "complexity_tier": schema["complexity_tier"],
                "attempted": 1,
            }
        if row.get("desc_reused") in (1, "1", True) or row.get("ctor_reused") in (1, "1", True):
            if row.get("desc_reused") in (1, "1", True):
                n_reused += 1
            if row.get("ctor_reused") in (1, "1", True):
                n_reused += 1
        if row.get("desc_reused") in (0, "0", False, None) and row.get("status") not in (
            "not_executed_budget",
            "not_executed_budget_ctor",
        ):
            n_new += 1
        rows.append(row)
        # checkpoint
        write_csv(PER_SCHEMA, rows)
        STATE.write_text(
            json.dumps({"spent": tracker.snapshot(), "i": i, "ts": utc_now()}, indent=2),
            encoding="utf-8",
        )
        if row.get("status", "").startswith("not_executed_budget"):
            log("Budget gate hit — continuing to mark remaining as not executed if needed")

    # Mark any missing jobs
    have = {(r["dataset"], r["schema_id"], r["describer"], r["prompt"]) for r in rows}
    for schema, desc, prompt in interleaved:
        key = (schema["dataset"], schema["schema_id"], desc, prompt)
        if key not in have:
            rows.append(
                {
                    "dataset": schema["dataset"],
                    "schema_id": schema["schema_id"],
                    "describer": desc,
                    "prompt": prompt,
                    "constructor": CONSTRUCTOR,
                    "status": "not_executed",
                    "tables": schema["tables"],
                    "columns": schema["columns"],
                    "size_tier": schema["size_tier"],
                    "complexity_tier": schema["complexity_tier"],
                }
            )

    counts = {
        "planned": len(interleaved),
        "completed": sum(1 for r in rows if r.get("status") == "completed"),
        "desc_failed": sum(1 for r in rows if r.get("status") == "desc_failed"),
        "ctor_failed": sum(1 for r in rows if r.get("status") == "ctor_failed"),
        "not_executed": sum(1 for r in rows if str(r.get("status", "")).startswith("not_executed")),
        "valid": sum(1 for r in completed_rows(rows) if str(r.get("reconstruction_valid")) in ("1", "True")),
    }
    log(f"Counts: {counts}")
    analysis = analyze(rows, schemas)
    spend = tracker.snapshot()
    save_csvs(analysis, rows)
    write_latex(analysis, spend)
    write_figures(rows)
    write_paper(analysis, spend, counts)
    write_all_results_txt(
        schemas,
        rows,
        analysis,
        spend,
        {k: v[0] for k, v in probes.items()},
        n_new,
        n_reused,
        counts,
    )
    # dump bootstrap
    (OUT / "bootstrap.json").write_text(json.dumps(analysis["bootstrap"], indent=2, default=str), encoding="utf-8")
    (OUT / "analysis.json").write_text(json.dumps(analysis, indent=2, default=str), encoding="utf-8")
    log(f"DONE. spent=${spend['spent_usd']:.4f} completed={counts['completed']}")


if __name__ == "__main__":
    main()
