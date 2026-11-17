# E4 Final Verification Audit — ICDE 2027 SchemaBridge

**Audit date:** 2026-11-11 / 2026-11-12
**Integration:** PRIMARY values frozen in `experiments/E4/verified_values.py` (joint Domain, pooled).
**Session:** `screen -S e4_final_audit`
**Verdict summary (post-approval):** E4 Split / Recovery **VERIFIED** under joint Domain; manuscript drop-ins in `latex/`.

---

## Provenance (authoritative artifacts)

| Role | Path |
|---|---|
| E4/Exp5 evaluator | `/data/Text2ER/analyze_exp3_inferability.py` |
| Domain-fact helper (Exp5 main path) | `/data/Text2ER/exp3_domain_facts.py` |
| Shared joint Domain matcher (structural F1) | `/data/Text2ER/evaluate_cases_full.py` → `count_domain_both` |
| Masking | `/data/Text2ER/structural_imputation_pipeline.py`, `MASKING_VERIFICATION.md` |
| Exp5 outputs (2026-07-10) | `/data/A_Final_Result/Exp5/` |
| Direct GPT-4o-mini preds | `.../Cases_GPT4omini/*Mask_T`, `SchemaBench/Experiment3_GPT4omini/*`, `RSchema.../Experiment3_Gpt4omini/*` |
| Round-trip preds | `CasesTranslations`, `Experiment3_Translations` (describers: Enterprise mistral/codellama/deepseek/llama31; SB/RSchema codellama13b/llama31/deepseek) |
| Gold | Enterprise `Text2ER/schema`, SchemaBench `annotation_ddl.jsonl`, RSchema `annotation.jsonl` |
| This audit | `/data/SchemaBridge/results/metrics/reproduced/E4_AUDIT/` |

**Datasets:** Enterprise-145 + SchemaBench-239 + RSchema-518 (pooled micro / unique-element as noted).
**Constructor:** GPT-4o-mini. **No LLM re-inference** was run.

---

## Evaluation formulas (as implemented / verified)

### Inferability
Heuristic labels `inferable` / `weak_inferable` / `non_inferable`; main tables aggregate **weak → non_inferable**.

### Split recall (observed-case Direct)
\[
\mathrm{Recall}=\frac{\#\text{matched eligible gold elements}}{\#\text{eligible gold elements}}
\]
Micro over Direct evaluation rows (includes rare duplicate Direct rows for Entity/FK).

### Recovery (inferable only)
- **Gold N:** unique eligible inferable gold elements with a Direct prediction.
- **Direct:** unique-element Direct recall on that set.
- **RT:** for each gold element, mean match indicator over **available describers**; then micro-average those per-element means (equal element weight; schemas with more describers do **not** get extra weight beyond having more describer samples inside the per-element mean).
- **Retention:** `RT / Direct` at full precision, then round to 3 d.p.

### Domain matching
- **Exp5 evaluator (artifacted):** per-**fact** domain facts (`domain_fact`), not joint column match.
- **Paper claim / shared structural metric:** joint **DATA_TYPE family ∧ nullability** per column (`count_domain_both`).
- Manuscript Domain cells **do not** match Exp5 domain-fact output; they match a **SchemaBench-centric joint** subset (see below).

---

## A. E4 Split verification

| Dimension | Group | Manuscript recall | Recomputed recall | Manuscript Gold N | Recomputed Gold N | Status |
|---|---|---|---|---|---|---|
| MT Tables | Inferable | 0.350 | 0.350 | 2,555 | 2,555 | MATCH |
| MT Tables | Non-inferable | 0.197 | 0.197 | 4,272 | 4,272 | MATCH |
| MA Attributes | Inferable | 0.611 | 0.611 | 9,254 | 9,254 | MATCH |
| MA Attributes | Non-inferable | 0.187 | 0.187 | 42,594 | 42,594 | MATCH |
| MD Domain | Inferable | 0.409 | see Domain notes | 1,574 | see Domain notes | MISMATCH |
| MD Domain | Non-inferable | 0.479 | see Domain notes | 35,573 | see Domain notes | MISMATCH |
| ME Entity | Inferable | 0.872 | 0.871 | 2,161 | 2,161 | MISMATCH |
| ME Entity | Non-inferable | 0.635 | 0.447 | 2,608 | 2,608 | MISMATCH |
| MR Referential | Inferable | 0.687 | 0.687 | 4,214 | 4,214 | MATCH |
| MR Referential | Non-inferable | 0.288 | 0.288 | 1,246 | 1,246 | MATCH |

**Recomputed Split source:** Direct micro over `/data/A_Final_Result/Exp5/exp3_inferability_eval.csv` (tables/attributes/entity/fk). Entity Inf: \(1882/2161=0.8709→0.871\). Entity NonInf: \(1165/2608=0.4467→0.447\).

### Domain notes (Split)
| Protocol | Inf recall (N) | Non-inf recall (N) |
|---|---|---|
| Manuscript | 0.409 (1,574) | 0.479 (35,573) |
| Exp5 domain_facts (evaluator artifact) | 0.425 (14,284) | 0.611 (242,556) |
| Joint, SchemaBench only (reproduces Inf / Recovery Domain) | 0.409 (1,574) | 0.687 (19,508)* |
| Joint, Enterprise+SchemaBench (reproduces NonInf **N**=35,573) | — | 0.473 (35,573)* |
| Joint, all datasets, backtick-safe labels (paper definition, corrected pop.) | **0.196 (8,578)** | **0.451 (36,669)** |

\*Older joint pass without full backtick normalization; SchemaBench Inf \(644/1574=0.4091\); Ent+SB NonInf \(16818/35573=0.4728\) (manuscript prints 0.479).

**Conclusion:** Manuscript Domain Inf Gold N / recall are **SchemaBench-only**. NonInf Gold N is **Enterprise+SchemaBench with SchemaBench label double-counting**, excluding RSchema. This is **not** the pooled three-dataset protocol used for MT/MA/ME/MR.

---

## B. E4 Recovery verification

| Dimension | Metric | Manuscript | Recomputed | Difference | Status |
|---|---|---|---|---|---|
| MT Tables | Gold N | 2555 | 2555 | 0 | MATCH |
| MT Tables | Direct | 0.350 | 0.350 | −0.0005 | MATCH |
| MT Tables | RT | 0.120 | 0.120 | +0.0001 | MATCH |
| MT Tables | Retention | 0.344 | 0.344 | −0.0004 | MATCH |
| MA Attributes | Gold N | 9254 | 9254 | 0 | MATCH |
| MA Attributes | Direct | 0.611 | 0.611 | −0.0001 | MATCH |
| MA Attributes | RT | 0.487 | 0.487 | +0.0001 | MATCH |
| MA Attributes | Retention | 0.797 | 0.797 | +0.0004 | MATCH |
| MD Domain | Gold N | 1574 | 8578 (joint pooled) / 14284 (facts) | — | MISMATCH |
| MD Domain | Direct | 0.409 | 0.196 joint / 0.425 facts | — | MISMATCH |
| MD Domain | RT | 0.032 | 0.049 joint / 0.197 facts | — | MISMATCH |
| MD Domain | Retention | 0.078 | 0.251 joint / 0.463 facts | — | MISMATCH |
| ME Entity | Gold N | 2087 | 2087 | 0 | MATCH |
| ME Entity | Direct | 0.878 | 0.877 | −0.0011 | MISMATCH |
| ME Entity | RT | 0.625 | 0.624 | −0.0010 | MISMATCH |
| ME Entity | Retention | 0.712 | 0.712 | −0.0003 | MATCH |
| MR Referential | Gold N | 4197 | 4197 | 0 | MATCH |
| MR Referential | Direct | 0.688 | 0.688 | +0.0001 | MATCH |
| MR Referential | RT | 0.444 | 0.444 | −0.0001 | MATCH |
| MR Referential | Retention | 0.645 | 0.645 | +0.0002 | MATCH |

Manuscript Domain Recovery equals **SchemaBench-only** joint: Direct \(0.4091\), RT \(0.0318\), Retention \(0.0776\).

---

## C. Audit explanation

### Pairing / averaging
- Direct and RT use the **same unique inferable gold elements** for T/A/E/R Recovery.
- RT = mean over elements of (mean over available describers). Missing describers affect only that element’s inner average; they do not drop the element from Gold N when at least one describer exists (all Recovery T/A/E/R elements had ≥1 RT output).
- This is **not** pooled micro over all RT rows (that underweights Enterprise’s 4 describers relative to per-element averaging for Entity/FK).

### Entity / Referential cross-table differences — JUSTIFIED
| | Split Gold N | Recovery Gold N | Cause |
|---|---|---|---|
| Entity | 2,161 | 2,087 | Split micro-counts Direct eval rows with **37 duplicate keys / +74 rows** (identical repeated Direct evaluations, e.g. `Bench`); Recovery deduplicates to unique `(dataset,schema,element)`. |
| Referential | 4,214 | 4,197 | Same pattern (**12** dup keys / **+17** rows). |

Paired Direct was correctly recomputed on the unique set (Entity \(1830/2087=0.8769\); FK \(2888/4197=0.6881\)).

### Why T/A keep the same Gold N
No material Direct-row duplication for tables/attributes; unique Direct population equals Split micro N (2,555 / 9,254).

### Domain metric definition — INCONSISTENT
1. Exp5 `analyze_exp3_inferability.py` scores **domain_fact** rows.
2. Paper / shared SchemaBridge Domain uses **joint type+nullability**.
3. Manuscript Domain cells follow neither pooled protocol; they follow a SchemaBench-centric joint extract.

### Entity non-inferable 0.635 — ERROR
Authoritative Exp5: \(1165/2608=0.447\). Value **0.635** does not arise from E4 Direct Entity non-inferable; likely transcription (Cases3 attr recall 0.6358 exists elsewhere).

---

## D. Corrected LaTeX (minimal necessary)

See `latex/tab_e4_split_corrected.tex` and `latex/tab_e4_recovery_corrected.tex`.

**Policy used for corrections:**
- T/A/E/R: Exp5 Direct / unique Recovery with verified RT formula; Entity Inf Split \(0.871\); Entity NonInf \(0.447\); Entity Recovery Direct/RT \(0.877\)/\(0.624\).
- Domain: **joint type+nullability**, backtick-safe column inferability, **all three datasets**, same RT formula → Inf \(0.196\) (\(8578\)), NonInf \(0.451\) (\(36669\)); Recovery Gold N \(8578\), Direct \(0.196\), RT \(0.049\), Retention \(0.251\).

If the camera-ready instead keeps the Exp5 **domain_fact** evaluator, substitute Domain Split \(0.425\) (\(14284\)) / \(0.611\) (\(242556\)) and Recovery \(14284\), \(0.425\), \(0.197\), \(0.463\), and revise the Domain prose away from “joint type+nullability.”

### Interpretation (minimal rewrite)
The quoted paragraph correctly restricts the Inf>NonInf claim to tables, attributes, entity, and FKs. **Add one sentence** acknowledging Domain as the exception (Inf < NonInf under both domain-fact and joint column protocols). Replace Entity non-inferable discussion if it assumed \(0.635\).

Suggested insertion after the first sentence:

> Domain is the exception: non-inferable columns are recovered more often than heuristically inferable ones under joint type-and-nullability matching, indicating that the inferability heuristic does not track Domain difficulty.

---

## E. Final verdict

| Item | Verdict |
|---|---|
| E4 Split | **NEEDS CORRECTION** |
| E4 Recovery | **NEEDS CORRECTION** |
| Domain metric definition | **INCONSISTENT** (paper joint vs Exp5 domain_facts; manuscript cells = SchemaBench-centric joint) |
| Direct/RT pairing | **VALID** (for T/A/E/R; Domain manuscript pairing is SchemaBench-only) |
| Cross-table population differences | **JUSTIFIED** (Entity/FK unique vs duplicated Direct rows) |
| Manuscript interpretation | **NEEDS MINIMAL REVISION** (acknowledge Domain exception; fix any reliance on Entity non-inf 0.635) |
