# E3 Reproducibility Audit — Constructor Isolation (`tab:e3_overall`)

**Status:** VERIFIED (PRIMARY 765)  
**Evaluator:** `evaluate_e3_primary.py` (locked E2 vendor, `PYTHONHASHSEED=0`)  
**Log:** `logs/evaluate_e3_primary.log` (EXIT:0)  
**Population:** 145 + 381 + 239 = **765** × 5 = **3,825**

---

## A. Provenance

Paper E3 lives on disk under historical **`Exp4`** trees (not `A_Final_Result/Exp3`, which is direct gold-NL Text2Schema).

| Stage | Path / entry point |
|---|---|
| Frozen detailed NL | `LLMTranslations/Exp2/Schema2Text2_gpt54mini`, `RSchema_ExpResults4/Experiment2/schema2text_gpt54mini`, `Text2ER/SchemaBench/Experiment/schema2text_gpt54mini` |
| Describer prompt | `SchemaBridge/prompts/describer_detailed.txt` |
| Constructor prompt | `SchemaBridge/prompts/constructor.txt` / Exp4 `SYSTEM_PROMPT` |
| Inference | `rschema_exp4_text2schema_experiment2_allLLM.py` (+ sonnet/gpt batch); SchemaBench/Enterprise `*_exp4_*` twins |
| Predictions | `*/Exp4/text2schema_*` and `LLMTranslations/Exp4/Text2Schema2_*` |
| Gold | Enterprise `Text2ER/schema`; RSchema `annotation_ddl.jsonl` (381); SchemaBench `annotation_ddl.jsonl` |
| Metrics | `experiments/E2/vendor/evaluate_text2schema2.py` + `evaluate_exp4_text2schema.py` |

Full inventory: `provenance/E3_SOURCE_INVENTORY.md`.

**Original vs later:** Prediction JSON/TXT under `*/Exp4/` are the original experimental artifacts (model_id + `source_schema2text_llm=gpt54mini` embedded). July 2026 `A_Final_Result/Exp4/exp4_combined_results.txt` is a **historical N=518 / 5-dim-Hall / lowercasing** aggregate and is **not** the PRIMARY paper table. This audit re-evaluates original predictions with the E2 PRIMARY protocol.

---

## B. Constructor isolation

Content hashes of embedded `nl_text` were compared to frozen `.txt` descriptions at schema-ID level for all 15 groups.

| Dataset | Frozen available | Identical across 5 constructors + frozen |
|---|---:|---:|
| Enterprise-145 | 145/145 | **145/145** |
| RSchema (381) | 381/381 | **381/381** |
| SchemaBench | 239/239 | **239/239** |
| **Total** | **765** | **765/765** |

- Every prediction records `source_schema2text_llm=gpt54mini`.
- No NL regeneration, substitution, or constructor-specific prompt forks detected.
- RSchema constructors have predictions for all 518 IDs; PRIMARY evaluates the 381 DDL-matched subset (same IDs for all five).

**Verdict: constructor isolation holds.**

Evidence: `isolation/isolation_summary.json`, `isolation/isolation_schema_hashes.csv`.

---

## C. Completeness (15 groups)

All 15 groups: expected N available, 0 missing predictions in PRIMARY population, NL match 100%, gold coverage 100%.

| Dataset | Constructor | N | Pred JSON | Missing | Emptyish | NL match |
|---|---|---:|---:|---:|---:|---:|
| Enterprise-145 | all five | 145 | 145 | 0 | 0–3* | 145 |
| RSchema | all five | 381 | 518 on disk | 0 | 0 | 381 |
| SchemaBench | all five | 239 | 239 | 0 | 0–3† | 239 |

\* Enterprise emptyish = comment-only DDL on empty-gold schemas (`archive`, `ctu_vondreli`, `tmp`) → nGED 0 (both empty).  
† SchemaBench DeepSeek: 3 emptyish scored against gold (remain in N).

Details: `inventory/group_completeness.csv`.

---

## D. Metrics audit

| Metric | Definition verified | Notes |
|---|---|---|
| **nGED** | `edit / (g_size + p_size)`; size = tables + `(col,type_family,null)` + FKs; mean over schemas | **Type-dependent** via column labels. Empty↔empty → 0 |
| **Hall.** | Mean of micro FP rates on **T,A,E,R** only | Domain excluded (matches paper; July Exp4 combine wrongly used 5 dims) |
| **F1 T/A/D/E/R** | Micro ΣG/ΣP/ΣM then P/R/F1 | Same locked vendor as E0/E2 PRIMARY |
| **Domain** | type-family + nullability | |
| **Entity** | PK + UNIQUE (single/multi) | |
| **Referential** | FK edges (single/multi) | |

Protocol matches E2 PRIMARY (`provenance/evaluation_protocol.md`).

---

## E. Cell verification (105)

Independently recomputed from original predictions.

| Status | Cells | Notes |
|---|---:|---|
| **MATCH** @ 3-dec | **78** | Exact agreement with manuscript values |
| **MISMATCH** @ 3-dec | **27** | All \|Δ\| ≤ 0.002; typical ±0.001 rounding / collision-safe map |
| **UNVERIFIABLE** | **0** | |

Full table: `metrics/E3_CELL_COMPARISON_105.csv`.

Largest mismatches (still tiny): SchemaBench CodeLlama Attr 0.697→0.699; GPT Attr 0.921→0.923. No ranking-changing discrepancy except one **tie**: RSchema Attr GPT also reaches 0.991 (paper listed 0.990).

---

## F. Methodological discrepancies (explained, not bugs)

### 1. RSchema: near-perfect T/A/E/R but nGED ≈ 0.47 for Claude/GPT

nGED column nodes include **`(name, type_family, nullability)`**, while Attribute F1 matches **names only**. Claude/GPT recover names/PKs/FKs almost perfectly (Attr F1 ≥ 0.991) but Domain F1 ≈ 0.35 → large type/null edits → nGED ≈ 0.47. CodeLlama Domain F1 0.483 yields best nGED 0.370 despite slightly lower structural F1. **Mathematically consistent** with the implemented metric.

### 2. RSchema ranking: CodeLlama best nGED, Claude best F1

Verified. Domain F1 order (CodeLlama/DeepSeek ≫ Claude/GPT) tracks nGED order. Hallucination and T/A/E/R favor Claude. Both rankings are supported; they optimize different objectives.

### 3. Enterprise Claude: nGED 0.047 vs Table F1 0.758

nGED is a **per-schema mean**; F1 is **micro** over all elements. Claude: **109/145** schemas with nGED=0 (median 0); Table precision 0.979 but recall only 0.619 — large incomplete schemas dominate micro F1, not mean nGED. **Consistent.**

### 4. SchemaBench Claude/GPT strong across dimensions

Verified from original Exp4 predictions; population 239 complete; isolation intact.

### 5. Historical N=518 trap

Filtering archived Exp4 per-schema scores to 381 IDs reproduces paper T/A/E/R/Hall but **not** Domain/nGED, because those archived scores used **synthetic** `annotation.jsonl` gold. PRIMARY re-eval against `annotation_ddl.jsonl` recovers Domain and nGED.

---

## G. Corrected LaTeX

See `latex/tab_e3_overall_verified.tex` (values = independent recomputation @ 3-dec; bold = best-in-dataset, ties shared).

**Bold change vs manuscript:** RSchema Attributes — GPT-5.4-mini also bold (tie 0.991 with Claude).

### Minimal paper corrections

1. Replace `tab:e3_overall` body with verified tex (27 cells change by ±0.001–0.002; one bold tie).
2. State population explicitly: Enterprise 145, RSchema **381 DDL-matched**, SchemaBench 239 (total 765).
3. State Hallucination = mean of Tables/Attributes/Entity/Referential FP rates (**Domain excluded**).
4. Optionally note nGED uses type/nullability-labeled columns (explains RSchema nGED vs Attr F1).
5. Do **not** cite `A_Final_Result/Exp4/exp4_combined_results.txt` as the paper table (wrong N, wrong Hall dims, wrong Enterprise name norm).

No E0/E1/E2/E4/E5 files were modified. No predictions overwritten. No APIs called.

---

## H. Final audit verdict

1. **15/15** groups complete and independently verifiable.
2. Cells: **78 MATCH**, **27 MISMATCH** (±0.002), **0 UNVERIFIABLE**.
3. **Yes** — all five constructors received exactly the same 765 frozen GPT-5.4-mini detailed descriptions (hash-verified).
4. Original scripts: Exp4 Text2Schema runners; predictions under `*/Exp4/`; PRIMARY metrics via locked E2 vendor on 381 DDL gold.
5. nGED / Hall / F1 follow the stated definitions (Hall 4-dim; nGED type-aware; F1 micro).
6. Reported model rankings **supported**; only Attr bold tie added on RSchema.
7. **Ready for ICDE submission** after swapping in the verified table and the four minimal wording fixes above.


---

## I. Final verification (publication gate)

### Determinism
Two independent `PYTHONHASHSEED=0` runs produced **bit-identical** full-precision metrics
(`determinism/DETERMINISM_PASS.json`, sha256 `ac35fad647cbaac57fd98e862b0031c4be0bf197834522785a9bbff28c67b3c5`).

### nGED consistency across experiments
| Experiment | nGED column labels | Notes |
|---|---|---|
| **E0** | **Names only** (`names_only=True`) | Type-independent |
| **E2 / E3** | `(col, type_family, nullability)` | Type-dependent (Exp4 vendor) |

The paper must not describe E0 and E3 nGED as identical formalisms.

### Authoritative vs manuscript
PRIMARY locked values are authoritative. The 27 manuscript deltas (≤0.002) are
documented in `metrics/E3_27_MISMATCH_CAUSES.md` (3-dec boundaries + SchemaBench
`_norm_map` collision-safe matching).

### Publication
Frozen NL and Exp4 predictions are **checksummed but not shipped**. Public-repo
users need private dumps to re-run evaluation.
