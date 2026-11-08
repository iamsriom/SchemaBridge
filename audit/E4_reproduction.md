# E4 reproduction — Masking / structural inferability

**Status: PARTIAL (artifacts) / BLOCKED (vs paper tables)**

## Paper intent

Five masks: 1Q1 tables, 1Q2 non-key attrs, 1Q3 domain, 1Q4 entity, 1Q5 referential; direct GPT-4o-mini and round-trip tracks; tables `tab:e4_split`, `tab:e4_fk_support`, `tab:e4_by_dataset`, figures recall/retention.

## What exists

| Piece | Location | Notes |
|---|---|---|
| Masking code | `third_party/structural_imputation_pipeline.py`, `MASKING_VERIFICATION.md` | 1Q1–1Q6 definitions |
| Enterprise RT translations | `results/predictions/e4/enterprise_cases_translations` | CodeLlama/Mistral describers → GPT-4o-mini |
| RSchema masked describer outs | `results/predictions/e3/rschema_cases_describer` (hist. Exp3) | 1Q2–1Q6 only; **no** scored reconstructions |
| Cases3 alternate family | `e4_cases3_results.json` | Table/Attr Case 0–75% hide; n=1143 |
| Analysis summary | `e4_cases_analysis_summary.json` | Inferability reports under Text2ER |

## SchemaBench masking

**None found.**

## Leakage / denominator audits

- Mask functions strip designated DDL aspects; metadata leakage not exhaustively proven for every track — see `MASKING_VERIFICATION.md`
- Domain-fact counting (per column vs per property) **not settled** against a manuscript definition — report archived aggregates only
- Evidence-supported FKs ≠ semantic correctness (FK graph analysis exists; do not auto-promote)

## Paper table match

No `tab:e4_*` numbers in the on-disk paper dump → **cannot PASS/MISMATCH** published cells. Offline export: `results/metrics/reproduced/E4_archived_cases_aggregates.csv`.
