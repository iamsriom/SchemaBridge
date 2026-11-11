# E0 Forensic Findings — Paper vs Current Reproduction

## 1. How were the original paper numbers generated?

Primarily from the **June 2026 Exp3 combined archive** produced by:

1. Exp4 Direct predictions (gold NL → constructor → DDL+metadata).
2. `evaluate_exp4_text2schema.py` with **logical synthetic Domain gold**, **typed nGED**, **5-dim Hall**.
3. `combine_exp3_results.py` → `exp3_combined_results.txt`.

Later, **some open-weight cells** (notably CodeLlama) were updated to the **genuine protocol** (381 DDL Domain, Hall4, names-only nGED) without updating Claude/GPT cells. Table V is therefore hybrid.

Evidence: `audit/E0_ORIGINAL_PAPER_RESULT_LINEAGE.md`, `audit/E0_HISTORICAL_REPRODUCTION.csv`.

## 2. Why do the numbers differ now?

Controlled ablations on **identical predictions** (`audit/E0_PROTOCOL_ABLATION.csv`):

### A. nGED (Claude 0.780 → 0.560)

| Variant | Claude nGED |
|---|---:|
| Historical typed | 0.779 |
| Names-only only | **0.560** |
| Paper | 0.780 |
| Current genuine | 0.560 |

**Cause:** typed column labels `(name, type, nullability)` vs names-only. Δ ≈ −0.219 explains the entire gap. Not a different prediction run.

### B. Domain (Claude 0.123 → 0.208)

| Variant | Claude Domain |
|---|---:|
| Historical synthetic (G=11705 on 518) | 0.124 |
| Genuine DDL Domain (381 IDs) | **0.208** |
| Paper | 0.123 |

**Cause:** synthetic VARCHAR gold on all logical attributes vs genuine typed DDL + known nullability on 381 schemas. Δ ≈ +0.084 explains the gap.

### C. Hallucination

Historical Hall = mean of **5** rates including Domain.
Current Hall = mean of **4** rates excluding Domain.
Ablation ΔHall ≈ −0.05 for Claude matches paper 0.687 → current ~0.635.

### D. Parser (Llama Tables 0.572 vs prior genuine 0.554)

`legacy=False` failed to discover later `CREATE TABLE` headers when LLM DDL left `ENGINE=` inside an unclosed table body (`PRIMARY KEY (...), ENGINE=...`). Historical/legacy finditer still found all tables.

**Bug fixed** in `src/schema_parser.py` (clamp body at next CREATE TABLE). After fix, Llama Tables F1 = **0.572054 = paper 0.572**.

### E. Aggregation

Both historical and current use **micro** F1 (`2M/(G+P)` on summed counts). Macro is not the Table V Direct discrepancy driver.

### F. Predictions

Open-weight trees byte-identical to recovery. Claude/GPT trees are the Exp4 originals used for Exp3. **No evidence** that paper used a different Claude/GPT prediction generation for these cells.

## 3. Is the current implementation wrong, or was the paper using an older evaluation?

| Issue | Classification |
|---|---|
| Claude/GPT nGED & Domain gaps | **Methodology / provenance** — paper cells are Exp3 historical; current matches declared genuine protocol |
| CodeLlama match | Paper already uses genuine protocol for those cells |
| Llama Tables pre-fix | **Genuine parser bug** (fixed) |
| Hybrid Table V | **Historical table transcription / incomplete migration** to genuine protocol |

Newer is correct **relative to the methodology text** (genuine Domain, Hall4, names-only nGED).
Older is correct **as a reproduction of Exp3 archive numbers**.

## 4. Why CodeLlama matches but Claude/GPT do not?

CodeLlama manuscript cells were migrated to genuine protocol (nGED 0.583, Domain 0.115).
Claude/GPT manuscript cells were **left at Exp3** (nGED ~0.78, Domain ~0.12).
Same current evaluator + same prediction packaging → CodeLlama PASS, Claude/GPT MISMATCH.

Ablations show the Claude/GPT gaps are almost entirely nGED definition + Domain gold definition—not model-specific scoring bugs.

## 5. Which results should the final manuscript contain?

**One consistent protocol for all Direct models:**

- Micro F1; Domain on genuine DDL (RSchema 381 / SchemaBench 239).
- Hallucination: 4-dim T/A/E/R.
- nGED: names-only structural.
- Parser: robust `legacy=False` **with** unclosed-table recovery (post-fix).

Authoritative numbers: `results/metrics/reproduced/E0_TABLE_V_FINAL.csv`
Legacy Exp3 numbers may be archived as a separate analysis, not mixed into Table V.

See `audit/E0_MANUSCRIPT_CORRECTIONS.md`.

## 6. 5% acceptance (vs genuine protocol)

From `audit/E0_ROOT_CAUSE_MATRIX.csv` after parser fix:

- Within 5% relative vs **new/genuine**: **55 / 70**
- Outside 5%: **15 / 70** (mostly Exp3 Claude/GPT nGED/Domain/Hall and a few Llama/SchemaBench residuals)

Outside-5% cells are **not** fixed by changing the evaluator to match paper; they require **manuscript updates** to genuine values.

Vs historical Exp3 reproduction, Exp3-provenance cells largely fall within 5% (Claude/GPT RSchema essentially exact).

## 7. Can PR #3 be merged?

**Not as E0 COMPLETE / manuscript-consistent** while Table V still prints Exp3 Claude/GPT cells under a genuine-protocol methods section.

PR can remain open with:

- Honest PARTIAL status.
- Forensic artifacts documenting hybrid provenance.
- Parser bugfix + tests.
- Recommended Table V = `E0_TABLE_V_FINAL.csv`.

Merge to `main` only after manuscript Table V is updated (or methods explicitly declare a dual protocol—which is not recommended).

## Per-schema stage example (Claude RSchema, metric nGED)

| Stage | Historical | Current genuine | First diverge? |
|---|---|---|---|
| Input NL / ID | same | same | no |
| Prediction bytes | same | same | no |
| Gold | logical synthetic types | logical for T/A/E/R; Domain uses DDL 381 | Domain path |
| Parse | hist DDL parser | robust parser (+fix) | minor |
| nGED labels | (col, type, null) | names only | **YES — primary nGED cause** |
| Aggregate | mean over 518 | mean over 518 | no |
