"""Wrap SchemaBridge evaluator for E5; preserve zero-score policy for failures."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.evaluator import evaluate_schema_pair  # noqa: E402
from src.metrics import ELEMENTS, micro_prf, zero_scored_schema_metrics  # noqa: E402
from src.schema_parser import ensure_prediction_metadata, metadata_from_ddl  # noqa: E402


def evaluate_prediction(
    gold_meta: dict,
    gold_ddl: str,
    pred_ddl: str | None,
    pred_meta: dict | None = None,
    *,
    parse_ok: bool | None = None,
) -> dict[str, Any]:
    """Evaluate one reconstruction. Empty/unparseable → zero scores, nGED=1."""
    pred_ddl = (pred_ddl or "").strip()
    if not pred_ddl:
        z = zero_scored_schema_metrics()
        counts = {
            k: {"gold": 0, "recreated": 0, "matched": 0, "tp": 0, "fp": 0, "fn": 0} for k in ELEMENTS
        }
        # Still compute gold sizes for TP/FP/FN denominators via a dummy eval against empty.
        empty_meta = {"database": "empty", "tables": [], "columns_by_table": {}}
        real = evaluate_schema_pair(gold_meta, gold_ddl, empty_meta, "")
        for k in ELEMENTS:
            g = real[k]["gold"]
            counts[k] = {
                "gold": g,
                "recreated": 0,
                "matched": 0,
                "tp": 0,
                "fp": 0,
                "fn": g,
            }
        return {
            "parse_success": False if parse_ok is None else bool(parse_ok),
            "reconstruction_valid": False,
            "scored_as_zero": True,
            "nged": 1.0 if any(counts[k]["gold"] > 0 for k in ELEMENTS) else 0.0,
            "exact_match": False,
            "counts": counts,
            "per_schema_f1": {k: 0.0 for k in ELEMENTS},
            **{k: counts[k] for k in ELEMENTS},
        }

    meta = ensure_prediction_metadata(pred_meta or {}, pred_ddl)
    try:
        result = evaluate_schema_pair(gold_meta, gold_ddl, meta, pred_ddl)
    except Exception:
        return evaluate_prediction(gold_meta, gold_ddl, "", None, parse_ok=False)

    counts = {}
    f1s = {}
    for k in ELEMENTS:
        g = result[k]["gold"]
        r = result[k]["recreated"]
        m = result[k]["matched"]
        counts[k] = {
            "gold": g,
            "recreated": r,
            "matched": m,
            "tp": m,
            "fp": max(0, r - m),
            "fn": max(0, g - m),
        }
        f1s[k] = micro_prf(g, r, m)["f1"]
    return {
        "parse_success": True if parse_ok is None else bool(parse_ok),
        "reconstruction_valid": True,
        "scored_as_zero": False,
        "nged": result["normalized_graph_edit_distance"],
        "exact_match": result["exact_match"],
        "counts": counts,
        "per_schema_f1": f1s,
        **{k: counts[k] for k in ELEMENTS},
    }


def micro_f1_from_rows(rows: list[dict], dim: str) -> float:
    g = sum(int(r.get(f"{dim}_gold", r.get(dim, {}).get("gold", 0))) for r in rows)
    # support flat columns
    if rows and f"{dim}_gold" in rows[0]:
        g = sum(int(r[f"{dim}_gold"]) for r in rows)
        rec = sum(int(r[f"{dim}_recreated"]) for r in rows)
        m = sum(int(r[f"{dim}_matched"]) for r in rows)
    else:
        g = sum(int(r[dim]["gold"]) for r in rows)
        rec = sum(int(r[dim]["recreated"]) for r in rows)
        m = sum(int(r[dim]["matched"]) for r in rows)
    return float(micro_prf(g, rec, m)["f1"])
