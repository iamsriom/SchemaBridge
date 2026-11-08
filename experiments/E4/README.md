# E4 — Masking and structural inferability

**Paper:** `tab:e4_split`, `tab:e4_fk_support`, `tab:e4_by_dataset`, `fig:e4_recall`, `fig:e4_retention`  
**Status: PARTIAL / BLOCKED vs paper**

## Objective

Hide one structural dimension at a time (1Q1–1Q5) and measure direct vs round-trip recovery.

## Local artifacts

- Masking code: `third_party/structural_imputation_pipeline.py`
- Definitions: `third_party/MASKING_VERIFICATION.md`
- Enterprise cases: `results/predictions/e4/`
- RSchema masked describers (1Q2–1Q6): via `results/predictions/e3/rschema_cases_describer`
- Archived aggregates: `results/metrics/archived/e4_*.json`

SchemaBench masking: **absent**.

## Commands

```bash
python experiments/E4/evaluate.py
python scripts/reproduce_tables.py --experiment E4 --offline
```

See `audit/E4_reproduction.md`.
