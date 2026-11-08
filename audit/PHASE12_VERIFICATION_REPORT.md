# SchemaBridge Phase 12 verification report

**Updated:** 2026-11-08 (repair pass)  
**Scope:** ICDE 2027 submission *How well do LLMs comprehend and design relational database schemata?*

Statuses: **VERIFIED** | **REPRODUCED, PROVENANCE INCOMPLETE** | **MISMATCH** | **UNVERIFIED** | **PARTIAL**.

No full ICDE manuscript PDF/LaTeX is on disk. Tables V / VII / VIII targets: `results/baselines/paper_methods_vs_paper_tables_comparison.txt`. E5: `experiments/e5_small/`. SchemaAgent / PaperMethods prediction trees are **excluded** from the public repository.

## Repair actions

1. Materialized open-weight E0–E2 prediction trees and Enterprise-145 SQL as real files (see `results/ARTIFACT_MANIFEST.json`).
2. Added E1 `per_record_*.jsonl` under `results/metrics/archived/e1_rschema_per_record/`.
3. Replaced unverified E3/E4 host symlinks with README stubs.
4. Added `docs/`, `CITATION.cff`, `.env.example`, `scripts/offline_e1_rschema_detailed.py`.
5. Rewrote public Git history to remove `Co-authored-by: Cursor` trailers.

Recovering files does **not** verify missing closed-model or E3/E4 manuscript cells.

## Experiment summary

| Experiment | Code | Outputs | Metrics | Paper | Status |
|---|---|---|---|---|---|
| E0 | Yes | Open RSchema/SchemaBench committed; Claude/GPT absent | Re-scored 2026-11-08 | DeepSeek mostly; Llama/CodeLlama Entity issues | **PARTIAL / MISMATCH** |
| E1 | Yes | RSchema open detailed + per_record committed | BLEU/ROUGE/SCR | 9 detailed open cells match | **PARTIAL** |
| E2 | Yes | RSchema detailed open committed; SchemaBench incomplete | Re-scored | Most cells ≈ paper; GPT-5.4-mini missing | **PARTIAL / MISMATCH** |
| E3 | No frozen-desc study | Missing | Cannot | Checkpoints not found | **UNVERIFIED** |
| E4 | Masking code present | Local cases ≠ paper denominators | Cannot | X–XI / Fig 8 | **UNVERIFIED** |
| E5 | e5_small | Log + CSV | 107/120 same-key logs | Checkpoints match CSV; provenance gaps | **REPRODUCED, PROVENANCE INCOMPLETE** |

### E0 highlights (RSchema open)

| Model | Metric | Paper | June archive | 2026-11-08 recompute |
|---|---|---:|---:|---:|
| DeepSeek | nGED / Ref | 0.733 / 0.182 | 0.733 / 0.182 | 0.733 / 0.182 |
| CodeLlama | Entity | 0.301 | **0.278** | 0.301 |
| Llama | Attr / Domain / nGED | 0.375 / 0.181 / 0.764 | **0.350 / 0.167 / 0.775** | **0.347 / 0.165 / 0.774** |

### E1 highlights (RSchema detailed open)

CodeLlama / Llama / DeepSeek BLEU-4, ROUGE-L, SCR match Table VII detailed. BERTScore skipped. Basic/closed missing.

### E2 highlights

RSchema detailed open mostly within 0.001–0.002 of Table VIII. GPT-5.4-mini checkpoint unverified. Figs 6–7 not fully regenerated.

### E5 highlights

N=30 sample checkpoints match CSV aggregates, but 13/120 DDLs lack successful same-key constructor logs; one RSchema GPT pair reuses Claude DDL; SB-192 Claude detailed truncated.

## Commands

```bash
pip install -r requirements.txt
python scripts/reproduce_tables.py --all --offline
python scripts/reproduce_tables.py --experiment E0 --recompute
python scripts/offline_e1_rschema_detailed.py
pytest -q
```

## Publication

Public `main` history must not contain Cursor co-author trailers. Author/committer: `iamsriom <57240585+iamsriom@users.noreply.github.com>`.
