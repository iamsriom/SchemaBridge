"""Deterministic stratified sample for E5 (seed=42)."""

from __future__ import annotations

import csv
import random
from collections import defaultdict
from pathlib import Path
from typing import Any


SIZE_ORDER = ["Small", "Medium", "Large"]
COMP_ORDER = ["Easy", "Medium", "Hard"]


def _cells(records: list[dict]) -> dict[tuple[str, str], list[dict]]:
    cells: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in records:
        st = r.get("size_tier") or "INVALID"
        ct = r.get("complexity_tier") or "INVALID"
        if st == "INVALID" or ct == "INVALID":
            continue
        cells[(st, ct)].append(r)
    for key in cells:
        cells[key].sort(key=lambda x: str(x["schema_id"]))
    return cells


def stratified_sample_dataset(
    records: list[dict],
    n_target: int,
    seed: int,
    *,
    prefer_e2: bool = False,
) -> list[dict]:
    """Allocate up to n_target records, covering every nonempty size×complexity cell."""
    rng = random.Random(seed)
    cells = _cells(records)
    nonempty = [(k, list(v)) for k, v in cells.items() if v]
    if not nonempty:
        return []

    # Prefer E2-available first within each cell when requested.
    for _k, lst in nonempty:
        if prefer_e2:
            lst.sort(
                key=lambda x: (0 if x.get("e2_deepseek_basic_available") else 1, str(x["schema_id"]))
            )
        rng.shuffle(lst)
        if prefer_e2:
            # Keep E2-first order but shuffle within each availability group.
            avail = [x for x in lst if x.get("e2_deepseek_basic_available")]
            miss = [x for x in lst if not x.get("e2_deepseek_basic_available")]
            rng.shuffle(avail)
            rng.shuffle(miss)
            lst[:] = avail + miss

    n_cells = len(nonempty)
    base = n_target // n_cells
    rem = n_target % n_cells
    # Stable cell order
    nonempty.sort(key=lambda kv: (SIZE_ORDER.index(kv[0][0]), COMP_ORDER.index(kv[0][1])))

    selected: list[dict] = []
    leftovers: list[dict] = []
    for i, (_key, lst) in enumerate(nonempty):
        take = base + (1 if i < rem else 0)
        take = min(take, len(lst))
        selected.extend(lst[:take])
        leftovers.extend(lst[take:])

    # If some cells were short, redistribute without replacement from leftovers.
    need = n_target - len(selected)
    if need > 0 and leftovers:
        rng.shuffle(leftovers)
        selected.extend(leftovers[:need])

    # Cap if overshot (should not happen)
    selected = selected[:n_target]
    selected.sort(key=lambda x: str(x["schema_id"]))
    return selected


def build_sample_manifest(
    population: list[dict],
    *,
    per_dataset: int = 40,
    seed: int = 42,
) -> list[dict[str, Any]]:
    by_ds: dict[str, list[dict]] = defaultdict(list)
    for r in population:
        by_ds[r["dataset"]].append(r)

    selected_ids: set[tuple[str, str]] = set()
    rows: list[dict[str, Any]] = []

    for ds, recs in sorted(by_ds.items()):
        prefer = ds in ("rschema", "schemabench")
        # Dataset-specific seed offset for independence while remaining deterministic.
        ds_seed = seed + sum(ord(c) for c in ds)
        picked = stratified_sample_dataset(recs, per_dataset, ds_seed, prefer_e2=prefer)
        for r in picked:
            selected_ids.add((ds, r["schema_id"]))

        # selection_probability: within-cell inverse size (design weight)
        cells = _cells(recs)
        cell_size = {k: len(v) for k, v in cells.items()}
        n_pick_cell: dict[tuple[str, str], int] = defaultdict(int)
        for r in picked:
            n_pick_cell[(r["size_tier"], r["complexity_tier"])] += 1

        for r in recs:
            key = (r["size_tier"], r["complexity_tier"])
            n_cell = cell_size.get(key, 0)
            n_sel = n_pick_cell.get(key, 0)
            # Probability a record from this cell is selected under our design.
            prob = (n_sel / n_cell) if n_cell else 0.0
            selected = (ds, r["schema_id"]) in selected_ids
            rows.append(
                {
                    "dataset": ds,
                    "schema_id": r["schema_id"],
                    "tables": r["tables"],
                    "columns": r["columns"],
                    "foreign_keys": r["foreign_keys"],
                    "composite_foreign_keys": r["composite_foreign_keys"],
                    "unique_constraints": r["unique_constraints"],
                    "size_tier": r["size_tier"],
                    "complexity_tier": r["complexity_tier"],
                    "selected": int(selected),
                    "selection_probability": round(prob, 6) if selected else round(prob, 6),
                    "e2_deepseek_basic_available": int(bool(r.get("e2_deepseek_basic_available"))),
                    "constraint_score": r.get("constraint_score"),
                    "database": r.get("database"),
                    "text_number": r.get("text_number"),
                }
            )
    rows.sort(key=lambda x: (x["dataset"], x["schema_id"]))
    return rows


def write_manifest(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "dataset",
        "schema_id",
        "tables",
        "columns",
        "foreign_keys",
        "composite_foreign_keys",
        "unique_constraints",
        "size_tier",
        "complexity_tier",
        "selected",
        "selection_probability",
        "e2_deepseek_basic_available",
        "constraint_score",
        "database",
        "text_number",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fields})


def selected_records(population: list[dict], manifest: list[dict]) -> list[dict]:
    want = {(r["dataset"], r["schema_id"]) for r in manifest if int(r["selected"]) == 1}
    out = [r for r in population if (r["dataset"], r["schema_id"]) in want]
    out.sort(key=lambda x: (x["dataset"], str(x["schema_id"])))
    return out
