# E0 Verification Report

**Branch:** `icde2027-e0-verified`  
**Updated:** 2026-11-11 (F1–F6 + comment-prefix CREATE recovery)  
**Experiment status:** **PARTIAL** (Direct COMPLETE; Table VI prompting ARCHIVE_AGGREGATE)

## Executive verdict

| Layer | Status |
|---|---|
| Direct predictions (3,785) | VERIFIED_FROM_PREDICTIONS |
| Evaluator protocol | Matches manuscript (micro F1, Domain-381/239, Hall4, names-only nGED) |
| DDL parser | F1–F6 + header-on-original (DeepSeek `--Foreachtable:`) |
| Table V vs lock | **70/70 PASS** (`E0_FINAL_INDEPENDENT_VERIFICATION.csv`) |
| Table VI Direct | Equals Table V RSchema |
| Table VI prompting | PASS_ARCHIVE provisional |
| Candidate DeepSeek 0.579 | **SUPERSEDED** (comment-mask regression) |
| SchemaAgent | Excluded |

## Coverage

- RSchema Direct: 5 × 518 COMPLETE  
- SchemaBench Direct: 5 × 239 COMPLETE  
- No gold DDL in constructor prompts (`run_direct_api.py` reads `question` only)

## Key artifacts

- `results/metrics/reproduced/E0_TABLE_{V,VI}_FINAL.*`
- `audit/E0_CURRENT_MANUSCRIPT_VALUES.json`
- `audit/E0_FINAL_INDEPENDENT_VERIFICATION.csv`
- `audit/E0_FINAL_PARSER_DIFFERENCE_REPORT.md`
- `audit/E0_FINAL_SECTION.tex`
- `audit/E0_PAPER_COMPARISON.csv`
