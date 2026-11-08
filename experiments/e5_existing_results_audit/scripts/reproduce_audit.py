#!/usr/bin/env python3
"""Reproduce E5 existing-results audit tables WITHOUT API access.

Reads only local SchemaBridge artifacts. Does not modify prediction trees.
"""
from __future__ import annotations

import csv
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from src.evaluator import evaluate_schema_pair, gold_record_to_metadata_and_ddl, load_jsonl
from src.metrics import ELEMENTS, micro_prf
from experiments.e5.gold import features_from_ddl, features_from_rschema_answer

OUT = Path(__file__).resolve().parents[1]


def micro_from_pairs(pairs):
    if not pairs:
        return {k: None for k in ELEMENTS}, None
    counts = {k: {"gold": 0, "recreated": 0, "matched": 0} for k in ELEMENTS}
    ngeds = []
    for ev in pairs:
        for k in ELEMENTS:
            counts[k]["gold"] += ev[k]["gold"]
            counts[k]["recreated"] += ev[k]["recreated"]
            counts[k]["matched"] += ev[k]["matched"]
        ngeds.append(ev["normalized_graph_edit_distance"])
    f1s = {
        k: micro_prf(counts[k]["gold"], counts[k]["recreated"], counts[k]["matched"])["f1"]
        for k in ELEMENTS
    }
    return f1s, statistics.mean(ngeds)


def eval_e2_dir(pred_dir: Path, dataset: str, gold_map: dict):
    rows = []
    for p in sorted(pred_dir.glob("*.json")):
        d = json.loads(p.read_text())
        sid = d.get("id")
        gold = gold_map.get(sid)
        if not gold:
            continue
        gmeta, gddl, _, _ = gold_record_to_metadata_and_ddl(gold)
        if dataset == "rschema":
            feats = features_from_rschema_answer(gold.get("answer") or {}, d.get("database") or "x")
        else:
            feats = features_from_ddl((gold.get("answer") or "").strip())
        try:
            ev = evaluate_schema_pair(gmeta, gddl, d.get("metadata") or {}, d.get("ddl") or "")
        except Exception:
            continue
        rows.append({"ev": ev, "size_tier": feats["size_tier"]})
    return rows


def micro_csv(rs, dim):
    if not rs:
        return None
    g = sum(int(float(r.get(f"{dim}_gold") or 0)) for r in rs)
    rec = sum(int(float(r.get(f"{dim}_recreated") or 0)) for r in rs)
    m = sum(int(float(r.get(f"{dim}_matched") or 0)) for r in rs)
    return micro_prf(g, rec, m)["f1"]


def mean_f(rs, key):
    vals = [float(r[key]) for r in rs if r.get(key) not in (None, "")]
    return statistics.mean(vals) if vals else None


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rs_gold = {r["id"]: r for r in load_jsonl(ROOT / "datasets/rschema/annotation.jsonl")}
    sb_gold = {r["id"]: r for r in load_jsonl(ROOT / "datasets/schemabench/annotation_ddl.jsonl")}

    # --- Table C ---
    e2_scal = []
    for dataset, folder, model, gmap in [
        ("rschema", "rschema_rt_deepseek", "deepseek", rs_gold),
        ("rschema", "rschema_rt_codellama13b", "codellama13b", rs_gold),
        ("rschema", "rschema_rt_llama31", "llama31", rs_gold),
        ("schemabench", "schemabench_rt_deepseek", "deepseek", sb_gold),
        ("schemabench", "schemabench_rt_codellama13b", "codellama13b", sb_gold),
        ("schemabench", "schemabench_rt_llama31", "llama31", sb_gold),
    ]:
        pred = ROOT / "results/predictions/e2" / folder
        if not pred.exists():
            continue
        rows = eval_e2_dir(pred, dataset, gmap)
        for size in ("Small", "Medium", "Large", "All"):
            subset = [
                r["ev"]
                for r in (rows if size == "All" else [r for r in rows if r["size_tier"] == size])
            ]
            f1s, nged = micro_from_pairs(subset)
            e2_scal.append(
                {
                    "Dataset": dataset,
                    "Size": size,
                    "N": len(subset),
                    "Describer": model,
                    "Prompt": "detailed",
                    "Constructor": "gpt-4o-mini",
                    "Tables_F1": "" if f1s["tables"] is None else f"{f1s['tables']:.3f}",
                    "Attributes_F1": "" if f1s["attributes"] is None else f"{f1s['attributes']:.3f}",
                    "Domain_F1": "" if f1s["domain"] is None else f"{f1s['domain']:.3f}",
                    "Entity_F1": "" if f1s["entity"] is None else f"{f1s['entity']:.3f}",
                    "Referential_F1": "" if f1s["referential"] is None else f"{f1s['referential']:.3f}",
                    "nGED": "" if nged is None else f"{nged:.3f}",
                    "Source": str(pred.relative_to(ROOT)),
                }
            )
    with (OUT / "table_C_e2_scalability.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(e2_scal[0].keys()))
        w.writeheader()
        w.writerows(e2_scal)

    # --- Table E (attempted-only) ---
    e5 = list(csv.DictReader(open(ROOT / "experiments/e5/outputs/e5_per_schema.csv")))
    e_rows = []
    for ds in ("rschema", "schemabench"):
        rows = [
            r
            for r in e5
            if r["stage"] == "e5a"
            and r["describer"] == "deepseek"
            and r["prompt"] == "basic"
            and r["dataset"] == ds
            and r.get("reconstruction_valid") == "1"
        ]
        costs = [float(r["total_cost_usd"]) for r in rows if r.get("total_cost_usd")]
        e_rows.append(
            {
                "Dataset": ds,
                "Describer": "DeepSeek-Coder-6.7B",
                "Constructor": "GPT-4o-mini",
                "Prompt": "basic",
                "N": len(rows),
                "Ref_F1": f"{micro_csv(rows, 'referential'):.3f}",
                "Domain_F1": f"{micro_csv(rows, 'domain'):.3f}",
                "nGED": f"{mean_f(rows, 'nged'):.3f}",
                "Cost_usd_schema": f"{statistics.mean(costs):.4f} (est.)" if costs else "N/A",
                "Status": "archive_reuse_valid_only",
            }
        )
    with (OUT / "table_E_attempted_only_summary.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(e_rows[0].keys()))
        w.writeheader()
        w.writerows(e_rows)

    print("Wrote", OUT / "table_C_e2_scalability.csv")
    print("Wrote", OUT / "table_E_attempted_only_summary.csv")
    for r in e_rows:
        print(r)
    print("DeepSeek RSchema Small Ref:", next(r for r in e2_scal if r["Describer"] == "deepseek" and r["Dataset"] == "rschema" and r["Size"] == "Small")["Referential_F1"])


if __name__ == "__main__":
    main()
