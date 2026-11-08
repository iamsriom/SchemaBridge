#!/usr/bin/env python3
"""Select exactly 30 schemata for E5-small (seed=42). Prefer DeepSeek E5 sample IDs."""
from __future__ import annotations

import csv
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.e5.gold import load_population  # noqa: E402

SEED = 42
ALLOC = {
    "rschema": {"Small": 5, "Medium": 4, "Large": 1},
    "schemabench": {"Small": 3, "Medium": 3, "Large": 4},
    "enterprise145": {"Small": 3, "Medium": 3, "Large": 4},
}


def deepseek_sample_ids() -> set[tuple[str, str]]:
    path = ROOT / "experiments/e5/outputs/e5_per_schema.csv"
    ids: set[tuple[str, str]] = set()
    if not path.exists():
        return ids
    with path.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if (
                r.get("stage") == "e5a"
                and r.get("describer") == "deepseek"
                and r.get("prompt") == "basic"
                and r.get("reconstruction_valid") == "1"
            ):
                ids.add((r["dataset"], r["schema_id"]))
    return ids


def pick_for_dataset(
    records: list[dict],
    targets: dict[str, int],
    prefer: set[tuple[str, str]],
    rng: random.Random,
) -> list[dict]:
    by_size: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        st = r.get("size_tier") or "INVALID"
        if st == "INVALID":
            continue
        by_size[st].append(r)

    selected: list[dict] = []
    selected_ids: set[str] = set()

    def choose(pool: list[dict], n: int) -> list[dict]:
        if n <= 0 or not pool:
            return []
        pref = [r for r in pool if (r["dataset"], r["schema_id"]) in prefer]
        other = [r for r in pool if (r["dataset"], r["schema_id"]) not in prefer]
        # diversify complexity within preferred then other
        def complexity_shuffle(lst: list[dict]) -> list[dict]:
            by_c: dict[str, list[dict]] = defaultdict(list)
            for r in lst:
                by_c[r.get("complexity_tier") or "Easy"].append(r)
            for v in by_c.values():
                rng.shuffle(v)
            # round-robin Easy/Medium/Hard
            order = ["Easy", "Medium", "Hard"]
            out: list[dict] = []
            while any(by_c[c] for c in order):
                for c in order:
                    if by_c[c]:
                        out.append(by_c[c].pop())
            return out

        ordered = complexity_shuffle(pref) + complexity_shuffle(other)
        # drop already selected
        ordered = [r for r in ordered if r["schema_id"] not in selected_ids]
        return ordered[:n]

    # first pass: target allocation
    shortfall = 0
    leftover_targets: dict[str, int] = {}
    for size, n in targets.items():
        got = choose(by_size.get(size, []), n)
        for r in got:
            selected.append(r)
            selected_ids.add(r["schema_id"])
        miss = n - len(got)
        if miss:
            leftover_targets[size] = miss
            shortfall += miss

    # redistribute shortfall within dataset from other sizes
    if shortfall:
        remaining = [r for size in ("Small", "Medium", "Large") for r in by_size.get(size, []) if r["schema_id"] not in selected_ids]
        # prefer Medium then Small then Large for fill
        remaining.sort(
            key=lambda r: (
                0 if (r["dataset"], r["schema_id"]) in prefer else 1,
                {"Medium": 0, "Small": 1, "Large": 2}.get(r["size_tier"], 9),
                r["schema_id"],
            )
        )
        for r in remaining[:shortfall]:
            selected.append(r)
            selected_ids.add(r["schema_id"])

    selected.sort(key=lambda r: (r["size_tier"], r["schema_id"]))
    return selected


def main() -> None:
    rng = random.Random(SEED)
    pop = load_population()
    prefer = deepseek_sample_ids()
    print(f"DeepSeek preferential IDs available: {len(prefer)}")

    rows = []
    for ds, targets in ALLOC.items():
        recs = [r for r in pop if r["dataset"] == ds]
        picked = pick_for_dataset(recs, targets, prefer, random.Random(SEED + sum(ord(c) for c in ds)))
        print(ds, "picked", len(picked), Counter(r["size_tier"] for r in picked), "prefer_hits", sum(1 for r in picked if (ds, r["schema_id"]) in prefer))
        for r in picked:
            rows.append(
                {
                    "dataset": r["dataset"],
                    "schema_id": r["schema_id"],
                    "database": r.get("database"),
                    "tables": r["tables"],
                    "columns": r["columns"],
                    "foreign_keys": r["foreign_keys"],
                    "size_tier": r["size_tier"],
                    "complexity_tier": r["complexity_tier"],
                    "constraint_score": r.get("constraint_score"),
                    "selection_seed": SEED,
                    "in_deepseek_e5_sample": int((r["dataset"], r["schema_id"]) in prefer),
                }
            )

    assert len(rows) == 30, len(rows)
    out = HERE / "sample_manifest.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("Wrote", out)
    print("Overall size", Counter(r["size_tier"] for r in rows))
    print("Overall complexity", Counter(r["complexity_tier"] for r in rows))
    print("DeepSeek overlap", sum(int(r["in_deepseek_e5_sample"]) for r in rows))


if __name__ == "__main__":
    main()
