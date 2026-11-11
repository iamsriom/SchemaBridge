#!/usr/bin/env python3
"""Validate E2 PRIMARY gold references and optional local prediction layout.

Does not download or generate predictions. Prints expected directory layout and
checks gold files + the RSchema-381 eligibility manifest.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = Path("/data")
MANIFEST = ROOT / "results/metrics/reproduced/E2_AUDIT/manifests/RSCHEMA_381_ELIGIBLE.csv"

GOLD = {
    "Enterprise-145": DATA / "Text2ER/schema/index.json",
    "RSchema_ddl": DATA / "RSchema/annotation_ddl.jsonl",
    "RSchema_annotation": DATA / "RSchema/annotation.jsonl",
    "SchemaBench": DATA / "SchemaBench/Dataset/annotation_ddl.jsonl",
}

PRED_LAYOUT = """
Expected original GPT-4o-mini reconstruction layout (not shipped in git):

  Enterprise Basic:    /data/LLMTranslations/Exp1/Text2Schema1_<model>/
  Enterprise Detailed: /data/LLMTranslations/Exp2/Text2Schema2_<model>/
  RSchema Basic:       /data/RSchema_ExpResults4/Exp1/text2schema_gpt4omini_schema2text_<model>/
  RSchema Detailed:    /data/RSchema_ExpResults4/Experiment2/text2schema_gpt4omini_schema2text_<model>/
  SchemaBench Basic:   /data/SchemaBench/Exp1/text2schema_gpt4omini_schema2text_<model>/
  SchemaBench Detailed:/data/Text2ER/SchemaBench/Experiment/text2schema_gpt4omini_schema2text_<model>/
                       (byte-identical copy may exist under /data/SchemaBench/Experiment/)

  <model> ∈ {codellama13b, llama31, deepseek, sonnet46, gpt54mini}

See results/metrics/reproduced/E2_AUDIT/provenance/prediction_manifest.csv and
source_hashes.json for SHA-256 manifests of the PRIMARY prediction trees.
"""


def load_jsonl(path: Path) -> list:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--print-layout", action="store_true")
    args = ap.parse_args()
    if args.print_layout:
        print(PRED_LAYOUT)
        return 0

    errors = []
    for name, path in GOLD.items():
        if not path.exists():
            errors.append(f"missing gold: {name} -> {path}")
            continue
        print(f"OK gold {name}: {path}")

    if not MANIFEST.exists():
        errors.append(f"missing RSchema-381 manifest: {MANIFEST}")
    else:
        with MANIFEST.open() as f:
            n = sum(1 for _ in csv.DictReader(f))
        if n != 381:
            errors.append(f"RSchema-381 manifest has {n} rows, expected 381")
        else:
            print(f"OK RSchema-381 manifest: {n} schema IDs")

    # Counts
    if GOLD["Enterprise-145"].exists():
        idx = json.loads(GOLD["Enterprise-145"].read_text())
        n = len(idx.get("datasets") or [])
        print(f"Enterprise-145 datasets: {n}")
        if n != 145:
            errors.append(f"Enterprise index has {n}, expected 145")
    if GOLD["SchemaBench"].exists():
        n = len(load_jsonl(GOLD["SchemaBench"]))
        print(f"SchemaBench records: {n}")
        if n != 239:
            errors.append(f"SchemaBench has {n}, expected 239")
    if GOLD["RSchema_ddl"].exists():
        n = len(load_jsonl(GOLD["RSchema_ddl"]))
        print(f"RSchema annotation_ddl.jsonl records: {n} (eligible PRIMARY subset = 381)")

    print(PRED_LAYOUT)
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 1
    print("PRIMARY gold validation passed (145 / 381 / 239).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
