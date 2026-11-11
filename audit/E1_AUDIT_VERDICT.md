# E1 Final Audit Verdict (`tab:e1_s2t`)

**Date:** 2026-11-11  
**Artifacts:** `audit/E1_CODE_PROVENANCE.md`, `experiments/E1/outputs/verified/`, `audit/E1_VERIFIED_TABLE.tex`, `audit/E1_PAPER_TEXT_AUDIT.md`

## Verdict

**VERIFIED.** All 90 applicable cells of `tab:e1_s2t` independently recomputed from authoritative prediction trees with correct corpus BLEU, RSchema N=381, SchemaBench N=239, Enterprise SCR-only. The locked manuscript values in `experiments/E1/outputs/verified/MANUSCRIPT_VALUES.json` match recomputed scores at reporting precision (BLEU ±0.005; others ±0.0005).

| Status vs locked manuscript | Count |
|---|---:|
| **MATCH** | **90** |
| **MISMATCH** | **0** |
| **UNVERIFIABLE** | **0** |

## Manuscript corrections (9 cells)

An earlier brief carried stale SchemaBench Detailed open BLEU/ROUGE/BERT and Llama Basic SCR display values that do **not** match a fresh correct-API recompute on `/data/SchemaBench/Experiment/` (and Exp1 for Basic SCR). Those cells were corrected to the recomputed values; see `experiments/E1/outputs/verified/E1_BRIEF_CORRECTIONS.csv`.

| Cell | Brief | Verified |
|---|---:|---:|
| SchemaBench CodeLlama D BLEU | 2.34 | **2.30** |
| SchemaBench Llama D BLEU | 4.09 | **3.67** |
| SchemaBench DeepSeek D BLEU | 1.71 | **1.66** |
| SchemaBench CodeLlama D ROUGE | 0.145 | **0.147** |
| SchemaBench Llama D ROUGE | 0.175 | **0.173** |
| SchemaBench DeepSeek D ROUGE | 0.141 | **0.144** |
| SchemaBench CodeLlama D BERT | 0.802 | **0.803** |
| SchemaBench DeepSeek D BERT | 0.792 | **0.793** |
| SchemaBench Llama B SCR | 0.404 | **0.405** |

All other cells preserved the brief / locked numbers.

## Generation completeness

| Dataset | Expected | Available | Evaluated | Missing |
|---|---:|---:|---:|---:|
| Enterprise-145 × 5 × 2 | 145 | 145 | 145 | 0 |
| RSchema × 5 × 2 | 381 (of 518 files) | 381 | 381 | 0 |
| SchemaBench × 5 × 2 | 239 | 239 | 239 | 0 |

Basic = `Exp1` / `Schema2Text1`; Detailed = `Experiment2` / `Schema2Text2` / `SchemaBench/Experiment`.  
**Excluded:** `results/predictions/e1/schemabench_*` (stale Experiment4).

## Methodological notes

1. Correct BLEU: `sacrebleu.corpus_bleu(hyps, [refs])` (SacreBLEU 2.6.0). Historical `[[r] for r in refs]` is buggy.
2. RSchema denominator is **381** DDL-matched IDs, not 518.
3. Repo prompts now match paper B/D (`describer_basic.txt` / `describer_detailed.txt`).
4. Near-1.0 Detailed SCR for Claude/GPT is real identifier coverage, not a parse error.

**E1 is submission-ready with the verified table.** Do not ship historical 518 / buggy-BLEU numbers or stale `schemabench_*` dumps.
