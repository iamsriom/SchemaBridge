# SchemaBridge E5 Existing-Results Audit

**Mode:** Offline recovery and verification only. **No new LLM inference.**  
**Date:** 2026-11-06  
**Package:** `experiments/e5_existing_results_audit/`

---

## 1. Repository audit summary

| Item | Finding |
|---|---|
| Manuscript `.tex` on disk | **Absent** in SchemaBridge; numbers recovered from `configs/paper_reference_values.json` and `audit/*_reproduction.md` |
| Datasets | Enterprise-145 (145), RSchema (518), SchemaBench (239) = **902** |
| E0 open-weight predictions | Complete for CodeLlama / Llama-3.1 / DeepSeek on RSchema (518) and SchemaBench (239) |
| E0 closed models | **0** per-schema predictions for Claude Sonnet 4.6 / GPT-5.4-mini |
| E1 open-weight NL | Present for RSchema + SchemaBench (3 open models); closed models absent |
| E2 open-weight round-trips | RSchema **518/518** detailed→GPT-4o-mini; SchemaBench **incomplete** (DeepSeek 195, CodeLlama 216, Llama 227 of 239) |
| E3 | **BLOCKED** — no GPT-5.4-mini fixed descriptions / constructor trees |
| E4 | Diagnostic archives partial; not used for E5 fidelity |
| E5 prior package | `experiments/e5/` contains sample reuse + tiny API pilots; aggregate CSVs **zero-fill unexecuted rows** |
| E0 latency 390.5 / 141.7 / 67.6 / 15.3 s | **Not found** as raw per-schema logs under `/data` (manuscript claim only) |
| Provider billing for archived E0–E2 | **Absent** (`audit/E5_reproduction.md`: BLOCKED) |

Authoritative fidelity sources for open E2 RSchema Detailed:  
`results/metrics/archived/e2_rschema_roundtrip_*` (reproduced in `results/metrics/reproduced/E2_cells.csv`).

---

## 2. E0–E5 implementations (concise)

| Exp | Role |
|---|---|
| **E0** | Direct Text2Schema from gold NL → DDL; constructors vary; metrics micro F1 + nGED + hallucination |
| **E1** | Schema2Text (basic/detailed) from gold DDL → NL; BLEU/ROUGE/BERTScore/SCR |
| **E2** | Round-trip: E1 NL → **fixed GPT-4o-mini** constructor → DDL; isolates describer quality |
| **E3** | Fixed GPT-5.4-mini **detailed** NL → vary constructors; isolates constructor quality |
| **E4** | Mask one structural dimension (1Q1–1Q5); direct vs round-trip recovery |
| **E5** | Scalability (size/complexity strata) + latency/token/cost; should reuse E0–E3, not invent a new fidelity protocol |

---

## 3. Existing data coverage

See `table_A_coverage.csv`.

**Complete / reusable for paper numbers:**

- E0 open fidelity (with known archived↔paper mismatches for some Llama/CodeLlama cells — see §4)
- E2 RSchema Detailed open fidelity (mostly PASS vs paper)
- E2 size-tier recomputation from open predictions (`table_C_e2_scalability.csv`)
- E5 DeepSeek-basic archive reuse: RSchema **N=40**, SchemaBench **N=38 valid** (2 missing archives)
- E5 API pilots: GPT-5.4-mini B/D on 1 RS + 1 SB schema; Claude basic on 1 RS + 1 SB; E5-B N=1 cells
- DeepSeek Schema2Text latency remount: **N=5×2 prompts × 3 datasets** (`table_latency_deepseek_s2t_remount.csv`)

**Not available:**

- E0 closed-model predictions, tokens, billed cost
- E0 open-weight per-schema latency/cost logs matching manuscript seconds
- E1/E2 provider usage for archived GPT-4o-mini reconstructions
- E3 entire experiment
- Enterprise-145 E2/E5 archive reuse (no wired predictions)
- Full-sample closed-model round-trips

---

## 4. Verification of manuscript results

### E0 fidelity
- Open models: local predictions exist; `audit/E0_reproduction.md` documents **PARTIAL / MISMATCH** vs paper for several RSchema Llama/CodeLlama cells; DeepSeek mostly PASS.
- Closed models: paper values exist only in `paper_reference_values.json` — **not independently recomputable**.

### E0 latency / tokens / cost (manuscript claims)
| Model | RSchema s | SchemaBench s | On-disk raw source |
|---|---:|---:|---|
| CodeLlama-13B | 390.5 | 415.0 | **NOT FOUND** |
| Llama-3.1-8B | 380.3 | 421.7 | **NOT FOUND** |
| DeepSeek-Coder | 141.7 | 178.0 | **NOT FOUND** |
| Claude Sonnet 4.6 | 67.6 | 98.7 | **NOT FOUND** |
| GPT-5.4-mini | 15.3 | 31.3 | **NOT FOUND** |

**Verdict:** Treat as **unverified manuscript claims**. Do not present as recovered measurements.

### E2 Detailed open (RSchema)
Archived report vs paper: largely PASS within 0.0005; a few MISMATCH cells (e.g., DeepSeek Attr 0.948 vs 0.950). SchemaBench E2 metrics archive missing; prediction coverage incomplete.

### E5 DeepSeek sample — zero-fill bug
Previously reported SchemaBench Ref=0.611 / Dom=0.383 / nGED=0.453 used **all 40 sample slots**, including 2 unexecuted archives scored as empty (gold counted, pred 0, nGED=1).

| Aggregate | Ref F1 | Domain F1 | nGED | N |
|---|---:|---:|---:|---:|
| **Correct (valid only)** | **0.674** | **0.451** | **0.424** | **38** |
| Zero-filled (misleading) | 0.611 | 0.383 | 0.453 | 40 |
| RSchema (valid) | 0.887 | 0.146 | 0.634 | 40 |

RSchema values match the previously reported figures (all 40 present).

### E5 aggregate CSVs in `experiments/e5/outputs/e5_cost_fidelity.csv`
These pool N=40/120 with ~1 successful pilot → artificially tiny F1 (~0.003–0.02). **Do not cite.** Use attempted-only rows in `table_E_e5_roundtrip_efficiency.csv`.

---

## 5. E0 inference efficiency

See `table_B_e0_efficiency.csv`.

- **Fidelity:** from `paper_reference_values.json` (closed) + archived open predictions.
- **Latency / tokens / $:** **N/A** on disk. Manuscript seconds listed only as unverified claims.
- E0 is **direct Text2Schema**, not round-trip cost — do not mix with E2.

---

## 6. E2 structural scalability

See `table_C_e2_scalability.csv` (recomputed offline from E2 prediction JSONs using paper size tiers: Small ≤5 tables ∧ ≤50 columns; Medium ≤15 ∧ ≤150; else Large). Constructor fixed: GPT-4o-mini. Prompt: **detailed** (only archived open round-trips).

### DeepSeek-Coder describer (authoritative open full run)

| Dataset | Size | N | Tables | Attr | Domain | Entity | Ref | nGED |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| RSchema | Small | 381 | 0.994 | 0.965 | 0.166 | 0.948 | 0.920 | 0.614 |
| RSchema | Medium | 136 | 0.990 | 0.934 | 0.148 | 0.915 | 0.921 | 0.600 |
| RSchema | Large | 1 | 1.000 | 0.370 | 0.030 | 0.000 | 0.000 | 0.793 |
| RSchema | All | 518 | 0.993 | 0.950 | 0.158 | 0.928 | 0.916† | 0.611 |
| SchemaBench | Small | 83 | 0.983 | 0.908 | 0.537 | 0.875 | 0.864 | 0.324 |
| SchemaBench | Medium | 99 | 0.986 | 0.830 | 0.477 | 0.760 | 0.769 | 0.400 |
| SchemaBench | Large | 13 | 0.991 | 0.787 | 0.508 | 0.684 | 0.654 | 0.402 |
| SchemaBench | All | 195‡ | 0.987 | 0.843 | 0.496 | 0.771 | 0.764 | 0.368 |

† All-aggregate Ref slightly differs from archived report 0.911 (use archived report for “All” paper cells; size strata are recomputed).  
‡ SchemaBench DeepSeek predictions incomplete (195/239).

**Finding:** On SchemaBench, Ref F1 declines Small→Large (0.864→0.654). On RSchema, Small/Medium Ref stay high (~0.92); the single Large schema collapses. Domain F1 remains low on RSchema across sizes.

---

## 7. E3 constructor comparison

**BLOCKED.** See `table_D_e3_constructor.csv` and `audit/E3_reproduction.md`.  
No local GPT-5.4-mini detailed description set and no five-constructor reconstruction tree. Tiny E5-B pilots (N=1) must not be presented as E3.

---

## 8. E5 existing pilot / full results

See `table_E_e5_roundtrip_efficiency.csv`.

| Status | What |
|---|---|
| Full sample reuse | DeepSeek basic→GPT-4o-mini: RS N=40, SB N=38; Enterprise **not executed** |
| Pilot (billed) | GPT-5.4-mini B/D × {RS,SB} N=1 each; Claude basic × {RS,SB} N=1; perfect F1 on those tiny schemata |
| Pilot E5-B | N=1 constructor cells; not comparable to full E3 |
| Missing usage | Archived E2 GPT-4o-mini constructor calls: no provider bills |

Estimated GPT-4o-mini constructor cost from archived text (DeepSeek sample): ~$0.0018/schema (RS), ~$0.0032/schema (SB) — **tokenizer/pricing estimate**, not a provider invoice. DeepSeek $ = N/A (open-weight).

---

## 9. Basic vs detailed efficiency

See `table_F_basic_vs_detailed_full.csv`.

**Full-dataset fidelity (paper dump; cost N/A):** On RSchema, detailed prompting raises Ref F1 for all describers (e.g., CodeLlama 0.602→0.812; Claude 0.403→0.955; GPT-5.4-mini 0.418→0.958). DeepSeek Domain F1 **drops** detailed (0.208→0.158) while Ref rises (0.867→0.911).

**Pilot cost (N=1 matched):** GPT-5.4-mini detailed costs ~+$0.001/schema vs basic on both RS and SB; fidelity already saturated (Ref=1.0, nGED=0) on those two small schemata — **not** evidence of a general cost–benefit.

Claude detailed round-trips with GPT-4o-mini constructor were not completed in the pilot (basic only for Claude→GPT-4o-mini).

---

## 10. Missing data and inconsistencies

1. Manuscript E0 latency/cost not recoverable from artifacts.  
2. Closed-model E0/E1/E2 predictions absent.  
3. E3 fully absent.  
4. SchemaBench E2 incomplete; no archived metrics JSON.  
5. Enterprise-145 not in E5 archive-reuse path.  
6. `e5_cost_fidelity.csv` / prior SB E5 numbers **zero-fill** unexecuted work.  
7. E2 Basic open archives BLOCKED (only Detailed on disk).  
8. Paper “All” Ref vs recomputed Ref minor drift — prefer archived evaluator JSON for published All cells.

---

## 11. What genuinely needs rerunning (only if paper requires it)

| Need | Why | Inference required? |
|---|---|---|
| Verify E0 latency/cost table | No raw logs | **Yes**, or obtain original host logs / billing exports |
| E3 full table | No artifacts | **Yes** (902 × 5 constructors) — expensive |
| E2 Basic open + closed full | Archives missing | **Yes** for missing cells |
| Enterprise E2/E5 | No archives | **Yes** if Enterprise rows required |
| Closed full E5 cost study | Only N=1 pilots | **Yes** for dataset-scale claims |

**Not required** to support a revised E5 section that: (a) reports E2 size scalability from open Detailed archives, (b) reports DeepSeek sample fidelity with correct N, (c) reports pilot billed costs as pilots, (d) marks E0 latency as unavailable / manuscript-only.

---

## 12. Recommended compact E5 tables

1. **`tab:e5_cost`** — DeepSeek sample + verified pilots + N/A for missing (see `tables/e5_cost_table.tex`)  
2. **`tab:e5_scalability`** — E2 DeepSeek (and optionally CodeLlama/Llama) Small/Medium/Large  
3. Extended appendix in `e5_extended_results.tex` (coverage + prompt fidelity without inventing $)

---

## 13. Final ICDE-ready E5 subsection

See `paper_e5.tex` in this folder.

---

## Reproduce (offline)

```bash
/data/Text2ER/.venv/bin/python experiments/e5_existing_results_audit/scripts/reproduce_audit.py
```

No API keys required. Does not modify original prediction trees or `experiments/e5/outputs/` source rows.
