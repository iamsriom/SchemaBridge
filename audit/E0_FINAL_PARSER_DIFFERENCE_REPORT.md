# E0 Final Parser Difference Report

**Date:** 2026-11-11  
**Compared commits:** `e6f7f0c` (last reviewed / pre–F1–F6) → working tree on `icde2027-e0-verified` (F1–F6 + comment-prefix CREATE recovery)  
**Predictions:** unchanged SHA-256 manifests under `results/predictions/e0/{rschema_exp4_*,schemabench_exp2_*}`  
**Gold:** unchanged `datasets/rschema/{annotation,annotation_ddl}.jsonl`, `datasets/schemabench/annotation_ddl.jsonl`

## 1. What changed in the parser

| Fix | Scientific intent | Effect |
|---|---|---|
| **F1** `DEFAULT ''` quote masking | Apostrophe in empty default must not desync quote state | SchemaBench **gold** recovers +157 columns (18791 → 18948); no table loss |
| **F2** unterminated `CREATE TABLE` | Body ends at next header; later tables not swallowed | Restores Llama/DeepSeek multi-table dumps previously collapsed |
| **F3** hyphenated/slashed bare names | `Sign-in`, `users/teams` parse as identifiers | Small SB gold/pred recoveries |
| **F4** UNIQUE/CONSTRAINT word-boundary | `unique_code` is a column, not a constraint | Tiny Entity shifts |
| **F5** literal `\n` DDL | Unescape when escaped newlines dominate | **19** SchemaBench Claude files: 0 → full column sets |
| **F6** `ALTER TABLE … ADD FOREIGN KEY` | Count ALTER-added FKs | Small Referential gains |
| **F7 (this pass)** header scan on original DDL | `--Foreachtable:CREATE TABLE` must not be wiped by comment masking | Restores DeepSeek compact one-line tables (35 RSchema + 3 SchemaBench preds) |

Same parser, all models — no model-specific branches.

## 2. Prediction / gold identity

- Direct prediction trees: **3,785** JSON files (5×518 + 5×239); manifests recorded in `audit/E0_FINAL_INDEPENDENT_VERIFICATION.csv`.
- No prediction regeneration for this report; only parser/evaluator re-score.

## 3. SchemaBench Claude Attributes 0.275 → 0.358

**Cause:** F5 (literal `\n`), not metric retuning.

| | Pre-F5 (`e6f7f0c`) | Post-repair |
|---|---:|---:|
| Attr G/P/M | 18791 / 12814 / 4345 | 18948 / 15964 / 6244 |
| Attr micro-F1 | 0.275 | 0.358 |
| nGED | 0.601 | 0.574 |

**Evidence:** 19 Claude SchemaBench DDLs store the entire schema as one line with literal `\n`. Pre-F5 parser emitted **0 columns** for those files while still listing tables via the empty-body fallback.

Representative recoveries (`audit/e0_final_parser_diff/claude_sb_examples.json`):

| ID | Pred cols old→new | Example newly matched `(table, column)` |
|---|---:|---|
| SB-009 | 0 → 207 | `(accessorie, categoryid)`, `(accessorie, companyid)`, `(accessorie, id)` |
| SB-114 | 0 → 215 | `(allstarfull, gameid)`, `(allstarfull, playerid)` |
| SB-133 | 0 → 191 | `(callcenter, cccallcenterid)`, `(callcenter, cccity)` |
| SB-017 | 0 → 195 | `(account, bankname)`, `(account, companyid)` |

Gold columns also rose slightly (+157 from F1 on SB gold). Matched attributes rose by **+1899**, which dominates the F1 gain. This is correct recovery of emitted DDL, not favourable Claude-specific scoring.

## 4. DeepSeek RSchema: candidate 0.579 nGED was a regression

After F1–F6 alone, header discovery ran on **comment-masked** text. DeepSeek often emits:

```text
--Foreachtable:CREATE TABLE `t` (`id` int(11) NOT NULL, ...)
```

Masking treated the whole line as a `--` comment → `iter_ddl_table_bodies` yielded **0 bodies** → fallback listed table names with **0 columns**. Example `0406.json`: 18 tables / **0** columns (post-F1–F6) vs 18 / **71** (after F7).

| RSchema DeepSeek | Candidate (F1–F6 only) | Final (F1–F7) | Pre-F1–F6 `e6f7f0c` |
|---|---:|---:|---:|
| nGED | 0.579 | **0.561** | 0.561 |
| Attributes | 0.427 | **0.443** | 0.442 |
| Domain | 0.146 | **0.150** | 0.150 |
| Entity | 0.377 | **0.391** | 0.389 |
| Ref | 0.177 | **0.184** | 0.183 |

The candidate DeepSeek drop vs GitHub was therefore **not** a justified scientific improvement; it was an empty-column regression on 31–35 files. Final values restore those columns while retaining F1–F6 gold/pred fixes (hence small deltas vs `e6f7f0c`, e.g. Entity 0.389→0.391).

SchemaBench DeepSeek similarly moves 0.734→**0.731** nGED and Attr 0.184→**0.185** after F7.

## 5. Why Claude SB improved but DeepSeek RSchema did not “get better from favouritism”

- Claude SB gain: previously **unparsed** emitted columns (F5).
- DeepSeek RSchema candidate worsening: previously **parsed** columns incorrectly dropped (masking bug), now restored.
- Both use the identical `metadata_from_ddl(..., legacy=False)` path.

## 6. Protocol unchanged

Micro F1 \(2M/(G+P)\), Hall4 over T/A/E/R, names-only nGED, Domain on 381/239 genuine DDL, empty failures → nGED=1 and Hall contribution 0. Verified in `audit/E0_FINAL_INDEPENDENT_VERIFICATION.csv` (**70/70** vs locked FINAL).

## 7. Artifacts

- `audit/e0_final_parser_diff/summary.csv`
- `audit/e0_final_parser_diff/per_schema_top_deltas.csv`
- `audit/e0_final_parser_diff/claude_sb_examples.json`
- `audit/e0_final_parser_diff/gold_sb_recovery.json`
- `audit/E0_FINAL_INDEPENDENT_VERIFICATION.csv`
- `results/metrics/reproduced/E0_TABLE_{V,VI}_FINAL.*`
