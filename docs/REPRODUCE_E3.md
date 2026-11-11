# Reproducing E3 (Constructor Isolation)

PRIMARY population: **765** schemata (Enterprise 145, RSchema genuine DDL **381**, SchemaBench 239) × 5 constructors = **3,825**.

## Requirements

- Python 3.10+
- `pip install -r requirements.txt`
- Local original artifacts (not in git):
  - Frozen NL: see `results/metrics/reproduced/E3_AUDIT/provenance/E3_SOURCE_INVENTORY.md`
  - Predictions: historical `*/Exp4/text2schema_*` and `LLMTranslations/Exp4/Text2Schema2_*`
  - Gold: `Text2ER/schema`, `RSchema/annotation_ddl.jsonl`, SchemaBench `annotation_ddl.jsonl`
- Optional: `SCHEMA_BRIDGE_DATA=/data` if the data root is not `/data`

Verify checksums against `provenance/artifact_checksums_summary.json` before trusting numbers.

## Commands

```bash
pip install -r requirements.txt

# Dual-run determinism (optional but recommended)
PYTHONHASHSEED=0 python3 experiments/E3/evaluate.py
PYTHONHASHSEED=0 python3 experiments/E3/evaluate.py
# Compare results/metrics/reproduced/E3_AUDIT/metrics/E3_PRIMARY_FINAL.csv across runs

python3 experiments/E3/generate_table.py
pytest -q tests/test_e3_primary.py
```

Do **not** call `experiments/E3/run.py` for generation — it refuses paid inference by design.

## Published outputs

| File | Role |
|---|---|
| `E3_AUDIT/E3_AUDIT_REPORT.md` | Scientific audit report |
| `E3_AUDIT/metrics/E3_PRIMARY_FINAL.csv` | 15-group aggregates |
| `E3_AUDIT/metrics/E3_CELL_COMPARISON_105.csv` | Manuscript vs PRIMARY |
| `E3_AUDIT/metrics/E3_27_MISMATCH_CAUSES.md` | Cause of each ±0.001–0.002 cell |
| `E3_AUDIT/latex/tab_e3_overall_verified.tex` | Verified LaTeX table |
| `E3_AUDIT/isolation/` | Constructor-isolation hashes |
| `E3_AUDIT/inventory/group_completeness.csv` | Per-group counts |
| `E3_AUDIT/provenance/` | Paths, protocol, checksums |

## Notes

- Historical `A_Final_Result/Exp4` (N=518, 5-dim Hall) is **not** PRIMARY.
- SchemaBench manuscript cells that differ by ≤0.002 from PRIMARY reflect the older hash-order Attr matcher; PRIMARY uses locked `_norm_map` (same as E2).
- **nGED:** E3/E2 are type-dependent; E0 is names-only — do not mix definitions in prose.
