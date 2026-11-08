# SchemaBridge — Final reproducibility report

**Date:** 2026-10-30  
**Verdict:** **NOT READY FOR PUBLIC RELEASE** as a complete ICDE EAB reproduction package.

## Manuscript

No LaTeX manuscript on disk. Numbers for E0–E2 taken from `paper_methods_vs_paper_tables_comparison.txt`. See `audit/MANUSCRIPT_STATUS.md`.

## Status matrix

| Experiment | Predictions | Code | Metrics | Paper Match | Status |
|---|---|---|---|---|---|
| E0 | Open: yes; Claude/GPT: **missing** | Yes (`src/` + vendored Exp4) | Archived + recomputable | Partial / mismatches | **PARTIAL / MISMATCH / BLOCKED** |
| E1 | RSchema open detailed: yes; else incomplete | Yes (vendored NL eval) | RSchema archived (no BERT) | Detailed open RSchema matches | **PARTIAL** |
| E2 | RSchema open detailed RT: yes; else incomplete | Vendored (older E2 script) | RSchema archived | 14/18 detailed cells | **MISMATCH / BLOCKED** |
| E3 | Constructor-isolation preds: **missing** | N/A | N/A | No paper dump | **BLOCKED** |
| E4 | Enterprise partial; RSchema describer-only; SB none | Masking code present | Cases aggregates | No paper dump | **PARTIAL / BLOCKED** |
| E5 | Cost logs: **missing** | N/A | N/A | No paper dump | **BLOCKED** |

## Key mismatches (E0 RSchema archived vs paper)

| Model | Metric | Paper | Archived | Recomputed (src) |
|---|---|---:|---:|---:|
| CodeLlama | Entity | 0.301 | 0.278 | **0.3005 (PASS)** |
| Llama | Attr | 0.375 | 0.350 | 0.347 |
| Llama | Domain | 0.181 | 0.167 | 0.165 |
| Llama | nGED | 0.764 | 0.775 | 0.774 |

## Tests

```text
pytest -q  →  143 passed
```

Offline `reproduce_tables.py --all` run twice: **identical CSV SHA-256** (17 files).

## Critical blockers for READY

1. Missing Claude / GPT-5.4-mini E0 (and most E1–E3) per-schema predictions  
2. Unresolved Llama RSchema Table V cells  
3. SchemaBench Table V manuscript block vs corrected few_shot  
4. E3 / E5 artifacts absent; E4 incomplete vs 902-schema claim  
5. No manuscript to lock labels, prompts, and aggregation text  

## Commands

```bash
cd /data/SchemaBridge
pip install -r requirements.txt
python scripts/reproduce_tables.py --all --offline
python scripts/reproduce_tables.py --experiment E0 --recompute
pytest -q
```
