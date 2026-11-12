# Reproducing E4 (Masking and Inferability)

PRIMARY tables: **`tab:e4_split`**, **`tab:e4_recovery`**.

Domain metric: **joint data-type family and nullability** (pooled across all three datasets).

## Requirements

- Python 3.10+
- `pip install -r requirements.txt`
- For **offline verification of published numbers** (no private dumps): nothing else
- For **optional full recompute** from predictions (not in git):
  - Data root with Enterprise / SchemaBench / RSchema gold and Exp3 masked Direct/RT predictions
  - Sibling `Text2ER` tree providing `analyze_exp3_inferability.py` and `evaluate_cases_full.py`
  - Set `SCHEMA_BRIDGE_DATA` (data root) and optionally `SCHEMA_BRIDGE_TEXT2ER`

## Commands (public clone)

```bash
pip install -r requirements.txt

python3 experiments/E4/evaluate.py
python3 experiments/E4/generate_tables.py
pytest -q tests/test_e4_primary.py
```

Do **not** call `experiments/E4/run.py` for generation — it refuses paid inference by design.

## Published outputs

| File | Role |
|---|---|
| `E4_AUDIT/E4_FINAL_VERIFICATION_REPORT.md` | Scientific audit |
| `E4_AUDIT/metrics/E4_SPLIT_PRIMARY.csv` | Split recalls + Gold N |
| `E4_AUDIT/metrics/E4_RECOVERY_PRIMARY.csv` | Recovery Direct/RT/Retention |
| `E4_AUDIT/latex/tab_e4_split_corrected.tex` | Camera-ready Split table |
| `E4_AUDIT/latex/tab_e4_recovery_corrected.tex` | Camera-ready Recovery table |
| `E4_AUDIT/latex/INTERPRETATION_EVIDENCE_GUIDED.tex` | Evidence-guided paragraph |
| `E4_AUDIT/latex/PAPER_CORRECTIONS_MINIMAL.tex` | Overleaf drop-in notes |
| `results/metrics/reproduced/E4_cells.csv` | Flat cell export |
| `results/metrics/reproduced/E4_summary.csv` | VERIFIED summary row |

## Aggregation (Recovery RT)

1. For each eligible gold element, average the match indicator over available describers.
2. Micro-average those element-level averages.
3. Retention = RT / Direct at full precision; round reported values to three decimals.

## Notes

- Legacy Exp5 **domain_facts** (Inf 0.425 / NonInf 0.611) is **not** the paper Domain definition.
- Do not use SchemaBench-only Domain (0.409 / 1,574) or Entity non-inferable 0.635.
- Entity/Referential Split vs Recovery Gold N differences are intentional (duplicate Direct rows vs unique paired elements).
- Historical Cases3 archives under `results/metrics/archived/e4_*` are a separate study.
