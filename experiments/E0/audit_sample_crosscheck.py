#!/usr/bin/env python3
"""Per-schema cross-check: historical evaluator (re-run JSON) vs current evaluator, same predictions.

For 10 seeded-random schemas of each large-delta model (Claude / GPT, both datasets) report
  hist nGED (typed)  |  current nGED typed (names_only=False) | current nGED names-only
  hist vs current Domain G/P/M (RSchema: synthetic varchar NOT NULL gold, as historical) .
Expect hist == current-typed up to parser differences, and names-only to be the large shift.

Usage: python3 experiments/E0/audit_sample_crosscheck.py /tmp/e0audit/hist_rschema/text2schema_exp4_evaluation.json \
          /tmp/e0audit/hist_sb/text2schema_exp4_evaluation.json
"""
from __future__ import annotations

import csv
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.evaluator import evaluate_schema_pair, gold_record_to_metadata_and_ddl, load_jsonl  # noqa: E402

PRED = ROOT / "results/predictions/e0"
CASES = [
    ("RSchema", "Claude Sonnet 4.6", "sonnet46", "rschema_exp4_claude_sonnet_4_6", ROOT / "datasets/rschema/annotation.jsonl"),
    ("RSchema", "GPT-5.4-mini", "gpt54mini", "rschema_exp4_gpt_5_4_mini", ROOT / "datasets/rschema/annotation.jsonl"),
    ("SchemaBench", "Claude Sonnet 4.6", "sonnet46", "schemabench_exp2_claude_sonnet_4_6", ROOT / "datasets/schemabench/annotation_ddl.jsonl"),
    ("SchemaBench", "GPT-5.4-mini", "gpt54mini", "schemabench_exp2_gpt_5_4_mini", ROOT / "datasets/schemabench/annotation_ddl.jsonl"),
]


def main() -> int:
    hist = {"RSchema": json.load(open(sys.argv[1])), "SchemaBench": json.load(open(sys.argv[2]))}
    out = []
    for ds, model, hkey, pdir, gpath in CASES:
        h = next(x for x in hist[ds]["llms"] if x["llm"] == hkey)["per_schema"]
        gold = {r["id"]: r for r in load_jsonl(gpath) if r.get("id")}
        rng = random.Random(42)
        stems = sorted(s for s, v in h.items() if "error" not in v)
        for stem in sorted(rng.sample(stems, 10)):
            pred = json.loads((PRED / pdir / f"{stem}.json").read_text())
            g = gold[pred["id"]]
            gm, gd, tc, cc = gold_record_to_metadata_and_ddl(g)
            typed = evaluate_schema_pair(gm, gd, pred.get("metadata") or {}, pred["ddl"], names_only=False, table_count=tc, column_count=cc)
            names = evaluate_schema_pair(gm, gd, pred.get("metadata") or {}, pred["ddl"], names_only=True, table_count=tc, column_count=cc)
            hv = h[stem]
            dom = hv["domain"]
            out.append({
                "dataset": ds, "model": model, "schema": stem,
                "hist_nged_typed": f"{hv['normalized_graph_edit_distance']:.4f}",
                "cur_nged_typed": f"{typed['normalized_graph_edit_distance']:.4f}",
                "cur_nged_names_only": f"{names['normalized_graph_edit_distance']:.4f}",
                "hist_domain_GPM": f"{dom['gold']}/{dom['recreated']}/{dom['matched']}",
                "cur_domain_GPM_synthetic_or_ddl_gold": "{gold}/{recreated}/{matched}".format(**typed["domain"]),
                "hist_tables_GPM": "{gold}/{recreated}/{matched}".format(**hv["tables"]),
                "cur_tables_GPM": "{gold}/{recreated}/{matched}".format(**typed["tables"]),
            })
    dst = ROOT / "audit/e0_table_v_mismatch/sample_schema_crosscheck.csv"
    with dst.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    # summary
    for ds, model, *_ in CASES:
        rows = [r for r in out if r["dataset"] == ds and r["model"] == model]
        d1 = sum(abs(float(r["hist_nged_typed"]) - float(r["cur_nged_typed"])) for r in rows) / len(rows)
        d2 = sum(float(r["hist_nged_typed"]) - float(r["cur_nged_names_only"]) for r in rows) / len(rows)
        print(f"{ds:11s} {model:18s} mean|hist-typed(cur)|={d1:.4f}  mean(hist-names_only)={d2:+.4f}")
    print("wrote", dst)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
