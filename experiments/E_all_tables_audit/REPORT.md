# Parser audit across paper Tables IX–XV

**Date:** 2026-11-07  
**Question:** Does correcting DDL parsing (legacy `extract_ddl_elements` / vendored quirks vs robust `metadata_from_ddl`) change the published tables?

**Datasets:** RSchema (518), SchemaBench (239), Enterprise-145 (145)

**Gold parse diffs (element sets):** RSchema 54/518 · SchemaBench 88/239 · Enterprise 37/145

---

## Executive summary

| Table | Experiment | Parser changes numbers? | Regenerated table vs original | Status |
|---|---|---|---|---|
| **IX** | E1 Schema2Text | SCR only; `\|Δ\|≤0.003` | **Identical** | Keep original |
| **X** | E2 Round-trip | RSchema D: tiny; SchemaBench: **large** on Ref | **Keep original** (RSchema D verified; SB/Ent/Basic/closed not reproducibly replaced) | PARTIAL |
| **XII** | E3 Constructor isolation | N/A — no artifacts | **Cannot regenerate** | BLOCKED |
| **XIII–XIV** | E4 Direct recall | N/A — matching artifact absent | **Cannot regenerate** | BLOCKED |
| **XV** | E5 Cost/fidelity (N=30) | Stored = paper; SchemaBench Ref needs **robust** parser | **Identical** (robust) | Keep original |

**Bottom line:** Only Table X (SchemaBench cells) is *sensitive* to the parser, but those cells still do not reproduce the paper from on-disk preds, so **do not rewrite any table from this audit alone**. Tables IX and XV stay as published. XII–XIV remain unreproducible.

---

## Table IX — E1 Schema verbalization

- Metrics: BLEU / ROUGE / BERTScore independent of DDL parse; **SCR** uses table/column name extraction.
- Recomputed open RSchema **Detailed**: PASS vs paper; robust SCR ≈ legacy.
- **Regenerated = original.**

Artifacts: `experiments/E1/outputs/TABLE_IX_parsing_recompute.md`

---

## Table X — E2 Round-trip (constructor = GPT-4o-mini)

### RSchema Detailed (open ×3) — verified

Legacy recompute matches paper within ~0.0005–0.001 on nearly all cells. Robust shifts **Referential** by about **+0.003–0.005** (e.g. CodeLlama Ref 0.812 → 0.817); other dims essentially unchanged.

| Model | Metric | Paper (D) | Legacy | Robust | Δ(R−L) |
|---|---|---:|---:|---:|---:|
| CodeLlama | Ref | 0.812 | 0.812 | 0.817 | +0.005 |
| Llama-3.1 | Ref | 0.660 | 0.660 | 0.663 | +0.003 |
| DeepSeek | Ref | 0.911 | 0.911 | 0.916 | +0.005 |

→ **Not enough to rewrite Table X rankings/bolds for RSchema Detailed.** Keep paper numbers (legacy-aligned).

### SchemaBench — parser-sensitive, paper not reproduced

Incomplete preds (208/222/194 of 239). Legacy vs robust **Referential** jumps by **+0.15–0.21**. Neither mode matches paper B or D within 0.005.

| Model | N | Ref legacy | Ref robust | Paper Ref (D) |
|---|---:|---:|---:|---:|
| CodeLlama | 208 | 0.439 | 0.588 | 0.485 |
| Llama-3.1 | 222 | 0.282 | 0.470 | 0.428 |
| DeepSeek | 194 | 0.550 | 0.764 | 0.629 |

→ **Do not replace SchemaBench rows** with either recompute.

### Enterprise / Basic / Claude / GPT

No verified aligned round-trip archives for paper Table X cells → **BLOCKED**.

**Regenerated Table X = original** (only RSchema D open cells verified; no material rewrite).

---

## Table XII — E3 Constructor isolation

**BLOCKED.** Required artifacts missing:

- Fixed GPT-5.4-mini **detailed** NL for all constructors
- Per-constructor reconstructions from those identical NLs

`results/predictions/e3/rschema_cases_describer` is **E4 masking**, not E3.

**Cannot regenerate Table XII.**

---

## Tables XIII–XIV — E4 Direct recall (inferable / non-inferable)

**BLOCKED vs paper.** On-disk Cases / Cases3 / CasesText2SchemaAnalysis aggregates use **different denominators and recalls** (e.g. archived attr inferable recall ≈0.15 vs paper XIII 0.611; domain non-inf gold count 242 556 not found).

SchemaBench masking: **none found**.

Without the GPT-4o-mini direct-recall artifact that produced XIII/XIV, parser impact cannot be tested.

**Cannot regenerate Tables XIII–XIV.**

---

## Table XV — E5 fidelity + cost (N=30 sample)

Stored `e5_small` micro-Ref / Dom / cost match the screenshot **12/12 cells**.

| Dataset | Describer | Prompt | Paper Ref/Dom/$ | Stored match |
|---|---|---|---|---|
| All 12 cells | GPT / Claude | B/D | as in Table XV | **YES** |

Parser note:

- **RSchema / Enterprise Ref:** legacy = robust on this sample.
- **SchemaBench Ref:** legacy **collapses** (~0.27–0.46) vs robust/stored (~0.83–0.995). Published XV used the **robust** path; do not re-score SchemaBench with legacy.

Costs are API usage — **unaffected by parsing**.

**Regenerated Table XV = original.**

---

## Recommendation

1. **Keep Tables IX, X, XII, XIII, XIV, XV as published** for the manuscript (XII–XIV already depend on proprietary/missing runs).
2. Disclose that SCR / structural metrics historically used the **legacy** DDL extractor for E1/E2 RSchema archives; E5 SchemaBench fidelity requires the **robust** parser.
3. Do **not** silently swap SchemaBench E2 numbers to robust recompute — they still disagree with the paper.
4. E3/E4 need the missing fixed-description / direct-recall dumps before any numeric revision.

## Artifacts

| Path | Content |
|---|---|
| `experiments/E1/outputs/TABLE_IX_parsing_recompute.md` | E1 detail |
| `experiments/E_all_tables_audit/e2_recompute.json` | E2 legacy vs robust |
| `experiments/E_all_tables_audit/e3_status.json` | E3 BLOCKED |
| `experiments/E_all_tables_audit/e4_status.json` | E4 BLOCKED |
| `experiments/E_all_tables_audit/e5_recompute.json` | E5 vs paper + parser |
| `experiments/E_all_tables_audit/REPORT.md` | This file |
