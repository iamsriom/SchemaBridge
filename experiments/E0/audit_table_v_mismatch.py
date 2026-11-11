#!/usr/bin/env python3
"""Offline waterfall audit of E0 Table V mismatches (no predictions regenerated).

Re-scores the *byte-identical* prediction trees under a sequence of evaluator states,
moving from the historical Exp3/Exp4 protocol to the current genuine protocol:

  W0  historical *emulation* (NOT bit-faithful: ``legacy=True`` is not a faithful port, see
                            audit/E0_TABLE_V_DIAGNOSTIC.md §7; attribution uses the real historical
                            re-run, so W0 is informational only)   legacy parser, JSON-metadata-preferred prediction structure,
                            typed nGED, Hall = mean of 5 micro rates (T/A/D/E/R),
                            RSchema Domain vs synthetic varchar(255) NOT NULL gold (518)
  W1  +robust parser        legacy=False parser (still JSON-metadata preferred)
  W2  +DDL-authoritative    prediction structure from DDL (current ensure_prediction_metadata)
  W3  +names-only nGED      attribute labels = names only
  W4  +Domain gold = DDL    RSchema Domain only on the 381 genuine DDL refs
  W5  +Hall4                Hall = mean of T/A/E/R micro rates   (== current genuine)

``src/`` is imported read-only; the evaluator is NOT modified.

Usage: python3 experiments/E0/audit_table_v_mismatch.py
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.evaluator import (  # noqa: E402
    five_element_counts,
    gold_record_to_metadata_and_ddl,
    load_jsonl,
)
from src.metrics import (  # noqa: E402
    ELEMENTS,
    hallucination_rate,
    micro_aggregate,
    normalized_graph_edit_distance,
)
from src.schema_parser import ensure_prediction_metadata, metadata_from_ddl  # noqa: E402

OUT = ROOT / "audit" / "e0_table_v_mismatch"
PRED = ROOT / "results" / "predictions" / "e0"
MODELS = {
    "CodeLlama-13B": "codellama13b",
    "Llama-3.1-8B": "llama31",
    "DeepSeek-Coder-6.7B": "deepseek",
    "Claude Sonnet 4.6": "claude_sonnet_4_6",
    "GPT-5.4-mini": "gpt_5_4_mini",
}
HIST_LLM = {  # key in historical evaluation JSON
    "CodeLlama-13B": "codellama13b",
    "Llama-3.1-8B": "llama31",
    "DeepSeek-Coder-6.7B": "deepseek",
    "Claude Sonnet 4.6": "sonnet46",
    "GPT-5.4-mini": "gpt54mini",
}
GOLD = {
    "RSchema": ROOT / "datasets/rschema/annotation.jsonl",
    "SchemaBench": ROOT / "datasets/schemabench/annotation_ddl.jsonl",
}
GOLD_DDL_RS = ROOT / "datasets/rschema/annotation_ddl.jsonl"
PRED_PREFIX = {"RSchema": "rschema_exp4_", "SchemaBench": "schemabench_exp2_"}
STEPS = ["W0_historical", "W1_robust_parser", "W2_ddl_authoritative", "W3_names_only_nged",
         "W4_domain_ddl_gold", "W5_hall4_genuine"]
# Extra state (hypothesis check): genuine protocol but prediction structure taken from the
# prediction JSON ``metadata`` when it carries columns / a table list (the pre-DDL-authoritative
# ``ensure_prediction_metadata``).  Reproduces every Llama-3.1 RSchema manuscript cell.
EXTRA_STEPS = ["P1_json_structure_genuine_protocol"]
METRICS = ["nged", "halluc", "tables", "attributes", "domain", "entity", "referential"]


def hist_ensure_meta(pred_meta: dict, pred_ddl: str, *, legacy: bool) -> dict:
    """Historical rule (evaluate_exp4_text2schema.ensure_prediction_metadata): keep the
    prediction JSON metadata when it contains any column; otherwise derive from DDL."""
    meta = dict(pred_meta or {})
    cbt = meta.get("columns_by_table") or {}
    if sum(len(v or []) for v in cbt.values()) > 0:
        return meta
    parsed = metadata_from_ddl(pred_ddl, database=meta.get("database") or "", legacy=legacy)
    if not meta.get("tables"):
        meta["tables"] = parsed.get("tables") or []
    meta["columns_by_table"] = parsed.get("columns_by_table") or {}
    return meta


def load_preds(pred_dir: Path) -> dict[str, dict]:
    out = {}
    for p in sorted(pred_dir.glob("[0-9][0-9][0-9][0-9].json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        d["_stem"] = p.stem
        out[d.get("id") or p.stem] = d
    return out


def _is_valid(d: dict | None) -> bool:
    return bool(d) and not d.get("error") and not d.get("skipped") and bool((d.get("ddl") or "").strip())


def score_state(dataset, gold_rows, preds, ddl_gold_by_id, *, legacy, meta_mode, names_only,
                domain_ddl, hall_dims):
    """Return aggregated metrics + per-schema counts for one evaluator state."""
    items, nged_vals, per = [], [], {}
    for g in gold_rows:
        rid = g["id"]
        d = preds.get(rid)
        if not _is_valid(d):
            raise RuntimeError(f"unexpected failed/missing prediction {dataset}:{rid}")
        g_meta, g_ddl, _tc, _cc = gold_record_to_metadata_and_ddl(g, legacy=legacy)
        if meta_mode == "json_pref":
            p_meta = hist_ensure_meta(d.get("metadata") or {}, d["ddl"], legacy=legacy)
        else:
            p_meta = ensure_prediction_metadata(d.get("metadata") or {}, d["ddl"], legacy=legacy)
        counts = five_element_counts(g_meta, g_ddl, p_meta, d["ddl"], legacy=legacy)
        if domain_ddl and dataset == "RSchema":
            dg = ddl_gold_by_id.get(rid)
            if dg is None:
                counts = dict(counts)
                counts["domain"] = {"gold": 0, "recreated": 0, "matched": 0}
            else:
                dm, dd, _, _ = gold_record_to_metadata_and_ddl(dg, legacy=legacy)
                counts = dict(counts)
                counts["domain"] = five_element_counts(dm, dd, p_meta, d["ddl"], legacy=legacy)["domain"]
        nged = normalized_graph_edit_distance(g_meta, g_ddl, p_meta, d["ddl"], legacy=legacy,
                                              names_only=names_only)
        items.append(counts)
        nged_vals.append(nged)
        per[d["_stem"]] = (counts, nged)
    agg = {k: micro_aggregate(items, k) for k in ELEMENTS}
    hall = sum(hallucination_rate(agg[k]["recreated"], agg[k]["matched"]) for k in hall_dims) / len(hall_dims)
    return {
        "nged": sum(nged_vals) / len(nged_vals),
        "halluc": hall,
        **{k: agg[k]["f1"] for k in ELEMENTS},
        "counts": {k: (agg[k]["gold"], agg[k]["recreated"], agg[k]["matched"]) for k in ELEMENTS},
        "per": per,
    }


STATE_KW = {
    "W0_historical": dict(legacy=True, meta_mode="json_pref", names_only=False, domain_ddl=False, hall_dims=ELEMENTS),
    "W1_robust_parser": dict(legacy=False, meta_mode="json_pref", names_only=False, domain_ddl=False, hall_dims=ELEMENTS),
    "W2_ddl_authoritative": dict(legacy=False, meta_mode="ddl", names_only=False, domain_ddl=False, hall_dims=ELEMENTS),
    "W3_names_only_nged": dict(legacy=False, meta_mode="ddl", names_only=True, domain_ddl=False, hall_dims=ELEMENTS),
    "W4_domain_ddl_gold": dict(legacy=False, meta_mode="ddl", names_only=True, domain_ddl=True, hall_dims=ELEMENTS),
    "W5_hall4_genuine": dict(legacy=False, meta_mode="ddl", names_only=True, domain_ddl=True,
                             hall_dims=("tables", "attributes", "entity", "referential")),
    "P1_json_structure_genuine_protocol": dict(
        legacy=False, meta_mode="json_pref", names_only=True, domain_ddl=True,
        hall_dims=("tables", "attributes", "entity", "referential")),
}


def main() -> int:
    only_extra = "--extra-only" in sys.argv
    steps_to_run = EXTRA_STEPS if only_extra else STEPS
    out_name = "ablation_p1.csv" if only_extra else "ablation_waterfall.csv"
    OUT.mkdir(parents=True, exist_ok=True)
    ddl_gold_rs = {r["id"]: r for r in load_jsonl(GOLD_DDL_RS) if r.get("id")}
    rows_out = []
    for dataset in ("RSchema", "SchemaBench"):
        gold_rows = [r for r in load_jsonl(GOLD[dataset]) if r.get("id")]
        for model, key in MODELS.items():
            preds = load_preds(PRED / f"{PRED_PREFIX[dataset]}{key}")
            for step in steps_to_run:
                res = score_state(dataset, gold_rows, preds, ddl_gold_rs, **STATE_KW[step])
                rows_out.append({"dataset": dataset, "model": model, "step": step,
                                 **{m: f"{res[m]:.6f}" for m in METRICS},
                                 **{f"{k}_GPM": "/".join(map(str, res['counts'][k])) for k in ELEMENTS}})
                if step == "W0_historical":
                    # persist per-schema counts for port-vs-historical comparison
                    pj = OUT / "_w0_per_schema" / f"{dataset}_{key}.json"
                    pj.parent.mkdir(exist_ok=True)
                    pj.write_text(json.dumps({s: {"counts": c, "nged": n} for s, (c, n) in res["per"].items()}))
            print(dataset, model, "done", flush=True)
    fields = list(rows_out[0].keys())
    with (OUT / out_name).open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows_out)
    print("wrote", OUT / out_name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
