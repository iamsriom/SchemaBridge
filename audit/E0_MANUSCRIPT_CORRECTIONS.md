# E0 Manuscript Corrections (post-forensics)

**Canonical protocol:** genuine Domain (RSchema 381 DDL), Hall4, names-only nGED, robust DDL parser.
**Source of numbers:** `results/metrics/reproduced/E0_TABLE_V_FINAL.csv` (after unclosed-table parser fix).

Do **not** mix Exp3 typed-nGED / synthetic-Domain cells into the same table.

## Recommended Table V (3 d.p.)

### RSchema

| Constructor | nGED | Hall | T | A | Dom | Ent | Ref |
|---|---:|---:|---:|---:|---:|---:|---:|
| CodeLlama-13B | 0.583 | 0.669 | 0.554 | 0.414 | 0.115 | 0.301 | 0.140 |
| Llama-3.1-8B | 0.615 | 0.696 | 0.572 | 0.377 | 0.121 | 0.199 | 0.102 |
| DeepSeek-Coder-6.7B | 0.561 | 0.595 | 0.566 | 0.442 | 0.150 | 0.389 | 0.183 |
| Claude Sonnet 4.6 | 0.560 | 0.635 | 0.602 | 0.401 | 0.208 | 0.406 | 0.203 |
| GPT-5.4-mini | 0.553 | 0.605 | 0.600 | 0.433 | 0.223 | 0.399 | 0.225 |

### SchemaBench

| Constructor | nGED | Hall | T | A | Dom | Ent | Ref |
|---|---:|---:|---:|---:|---:|---:|---:|
| CodeLlama-13B | 0.794 | 0.773 | 0.350 | 0.125 | 0.067 | 0.183 | 0.082 |
| Llama-3.1-8B | 0.810 | 0.768 | 0.363 | 0.112 | 0.061 | 0.145 | 0.064 |
| DeepSeek-Coder-6.7B | 0.744 | 0.648 | 0.398 | 0.152 | 0.081 | 0.216 | 0.129 |
| Claude Sonnet 4.6 | 0.601 | 0.620 | 0.530 | 0.275 | 0.180 | 0.286 | 0.262 |
| GPT-5.4-mini | 0.682 | 0.658 | 0.465 | 0.221 | 0.137 | 0.242 | 0.174 |

## Required text edits (§V-B)

1. Replace any Claude/GPT RSchema nGED ~0.78 / Domain ~0.12 with the genuine values above.
2. State explicitly: Domain uses 381 genuine DDL references; Hall excludes Domain; nGED is names-only.
3. Align Table VI Direct rows with Table V RSchema.
4. Optional footnote: Exp3 archive used typed nGED + synthetic Domain (see `e0_exp3_combined_results.txt`); those numbers are superseded.

## Table VI prompting rows

Remain **ARCHIVE_AGGREGATE** until PaperMethods per-schema trees are recovered. Do not claim independent per-schema reproduction.
