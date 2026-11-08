"""Load gold schemata and compute size/complexity features for E5."""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.evaluator import gold_answer_to_metadata_and_ddl  # noqa: E402
from src.schema_parser import metadata_from_ddl, parse_ddl_fks, parse_ddl_primary_unique  # noqa: E402

ENT_SCHEMA_DIR = ROOT / "datasets" / "enterprise145" / "schema"
RSCHEMA_ANN = ROOT / "datasets" / "rschema" / "annotation.jsonl"
RSCHEMA_DDL = ROOT / "datasets" / "rschema" / "annotation_ddl.jsonl"
SB_DDL = ROOT / "datasets" / "schemabench" / "annotation_ddl.jsonl"


def schema_size(n_tab: int, n_col: int) -> str:
    if n_tab <= 5 and n_col <= 50:
        return "Small"
    if n_tab <= 15 and n_col <= 150:
        return "Medium"
    return "Large"


def constraint_score(f: int, c: int, u: int, n_col: int, n_tab: int) -> float:
    if n_tab <= 0:
        return float("nan")
    return (
        2 * min(f, 10)
        + 3 * c
        + min(u, 5)
        + 0.2 * max(0.0, (n_col / n_tab) - 10.0)
    )


def complexity_tier(s: float) -> str:
    if math.isnan(s):
        return "INVALID"
    if s < 4:
        return "Easy"
    if s < 10:
        return "Medium"
    return "Hard"


def unique_excluding_pk(primaries, uniques) -> int:
    pk_sets = {(t, tuple(sorted(c.lower() for c in cols))) for t, cols in primaries}
    count = 0
    for t, cols in uniques:
        key = (t, tuple(sorted(c.lower() for c in cols)))
        if key in pk_sets:
            continue
        count += 1
    return count


def features_from_ddl(ddl: str) -> dict[str, Any]:
    meta = metadata_from_ddl(ddl)
    tables = meta.get("tables") or []
    n_tab = len(tables)
    n_col = sum(len(v or []) for v in (meta.get("columns_by_table") or {}).values())
    fks, n_comp = parse_ddl_fks(ddl)
    primaries, uniques = parse_ddl_primary_unique(ddl)
    u = unique_excluding_pk(primaries, uniques)
    f = len(fks)
    s = constraint_score(f, n_comp, u, n_col, n_tab)
    return {
        "tables": n_tab,
        "columns": n_col,
        "foreign_keys": f,
        "composite_foreign_keys": n_comp,
        "unique_constraints": u,
        "constraint_score": s,
        "size_tier": schema_size(n_tab, n_col) if n_tab > 0 else "INVALID",
        "complexity_tier": complexity_tier(s),
        "meta": meta,
        "ddl": ddl,
    }


def features_from_rschema_answer(answer: dict, database: str) -> dict[str, Any]:
    meta, ddl = gold_answer_to_metadata_and_ddl(answer, database=database)
    n_tab = 0
    n_col = 0
    f = 0
    c = 0
    for _t, tdef in (answer or {}).items():
        if not isinstance(tdef, dict):
            continue
        n_tab += 1
        attrs = tdef.get("Attributes") or []
        if isinstance(attrs, list):
            n_col += len(attrs)
        fks = tdef.get("Foreign key") or tdef.get("Foreignkey") or {}
        if isinstance(fks, dict):
            for _src, ref in fks.items():
                f += 1
                if isinstance(ref, dict) and len(ref) > 1:
                    c += 1
    primaries, uniques = parse_ddl_primary_unique(ddl)
    u = unique_excluding_pk(primaries, uniques)
    s = constraint_score(f, c, u, n_col, n_tab)
    return {
        "tables": n_tab,
        "columns": n_col,
        "foreign_keys": f,
        "composite_foreign_keys": c,
        "unique_constraints": u,
        "constraint_score": s,
        "size_tier": schema_size(n_tab, n_col) if n_tab > 0 else "INVALID",
        "complexity_tier": complexity_tier(s),
        "meta": meta,
        "ddl": ddl,
    }


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_population() -> list[dict[str, Any]]:
    """Return one record per gold schema across all three datasets."""
    out: list[dict[str, Any]] = []

    # Enterprise-145
    schema_dir = ENT_SCHEMA_DIR.resolve()
    for sql_path in sorted(schema_dir.glob("*.sql")):
        ddl = sql_path.read_text(encoding="utf-8", errors="replace")
        feats = features_from_ddl(ddl)
        sid = sql_path.stem
        out.append(
            {
                "dataset": "enterprise145",
                "schema_id": sid,
                "database": sid,
                "question": "",
                "has_typed_ddl": True,
                "e2_deepseek_basic_available": False,
                **{k: v for k, v in feats.items() if k not in ("meta",)},
                "gold_meta": feats["meta"],
                "gold_ddl": feats["ddl"],
            }
        )

    # RSchema
    for i, rec in enumerate(load_jsonl(RSCHEMA_ANN), start=1):
        sid = rec["id"]
        database = f"rschema_{i:04d}"
        feats = features_from_rschema_answer(rec.get("answer") or {}, database)
        out.append(
            {
                "dataset": "rschema",
                "schema_id": sid,
                "database": database,
                "text_number": i,
                "question": rec.get("question") or "",
                "has_typed_ddl": False,
                "e2_deepseek_basic_available": True,  # 518/518 archived
                **{k: v for k, v in feats.items() if k not in ("meta",)},
                "gold_meta": feats["meta"],
                "gold_ddl": feats["ddl"],
            }
        )

    # SchemaBench
    e2_ids: set[str] = set()
    e2_dir = ROOT / "results" / "predictions" / "e2" / "schemabench_rt_deepseek"
    if e2_dir.exists():
        for p in e2_dir.glob("*.json"):
            try:
                e2_ids.add(json.loads(p.read_text(encoding="utf-8")).get("id") or "")
            except Exception:
                continue

    for i, rec in enumerate(load_jsonl(SB_DDL), start=1):
        sid = rec["id"]
        database = rec.get("database") or f"schemabench_{i:04d}"
        ddl = (rec.get("answer") or "").strip()
        feats = features_from_ddl(ddl)
        out.append(
            {
                "dataset": "schemabench",
                "schema_id": sid,
                "database": database,
                "text_number": i,
                "question": rec.get("question") or "",
                "has_typed_ddl": True,
                "e2_deepseek_basic_available": sid in e2_ids,
                **{k: v for k, v in feats.items() if k not in ("meta",)},
                "gold_meta": feats["meta"],
                "gold_ddl": feats["ddl"],
            }
        )

    return out


def n_tables_in_ddl(ddl: str) -> int:
    return len(re.findall(r"CREATE\s+TABLE", ddl, re.IGNORECASE))
