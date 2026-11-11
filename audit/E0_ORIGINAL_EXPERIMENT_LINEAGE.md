# E0 Original Experiment Lineage

Generated during ICDE 2027 reproducibility verification on the research server.
Protocol target: **current manuscript** Tables V–VI (genuine Domain / Hall4 / names-only nGED), **not** the older `configs/paper_reference_values.json` draft.

## Naming map

| Paper | On-disk label |
|---|---|
| E0 Direct Text2Schema (Table V) | `/data/A_Final_Result/Exp3/` (combined archive); predictions under Exp4 / SchemaBench Experiment2 |
| E0 baselines (Table VI) | LLM4DBdesign PaperMethods (`one_shot` / `one_shot_cot` / `few_shot`) + Direct rows |

## Direct Text2Schema (Table V)

### Generation

| Dataset | Models | Original script | Settings (from source) |
|---|---|---|---|
| RSchema (518) | CodeLlama-13B, Llama-3.1-8B, DeepSeek-Coder-6.7B | `/data/RSchema_ExpResults4/Code/rschema_exp4_text2schema_allLLM.py` | `temperature=0.1`, `max_new_tokens=2048`, `top_p=1.0`, `do_sample=False` when T≤0.1 |
| RSchema | Claude Sonnet 4.6 | `/data/RSchema_ExpResults4/Code/rschema_exp4_text2schema_sonnet46_batch.py` | API batch; exact snapshot unknown |
| RSchema | GPT-5.4-mini | `/data/RSchema_ExpResults4/Code/rschema_exp4_text2schema_gpt54mini_batch.py` | API batch; exact snapshot unknown |
| SchemaBench (239) | open-weight trio | `/data/Text2ER/SchemaBench/Code/rschema_exp4_text2schema_allLLM.py` | same prompt family / decoding as RSchema |
| SchemaBench | Claude / GPT-5.4-mini | `schemabench_exp4_text2schema_{sonnet46,gpt54mini}_batch.py` | API batch |

**Prompt:** MySQL-style DDL + structured metadata JSON constructor prompt.
SchemaBridge copy: `prompts/e0/direct.txt` (byte-identical to historical `SYSTEM_PROMPT` aside from trailing newline).
Also mirrored at `prompts/constructor.txt`.

**Input:** gold natural-language `question` field only (no gold DDL in constructor input). Verified in generation scripts.

### Predictions (original → packaged)

| Dataset | Model | Original path | Packaged path | Records | Tree match |
|---|---|---|---|---:|---|
| RSchema | CodeLlama-13B | `/data/RSchema_ExpResults4/Experiments/text2schema_codellama13b/` | `results/predictions/e0/rschema_exp4_codellama13b/` | 518 | identical |
| RSchema | Llama-3.1-8B | `.../text2schema_llama31/` | `.../rschema_exp4_llama31/` | 518 | identical |
| RSchema | DeepSeek-Coder-6.7B | `.../text2schema_deepseek/` | `.../rschema_exp4_deepseek/` | 518 | identical |
| RSchema | Claude Sonnet 4.6 | `.../text2schema_sonnet46/` | `.../rschema_exp4_claude_sonnet_4_6/` | 518 | copied for this release |
| RSchema | GPT-5.4-mini | `.../text2schema_gpt54mini/` | `.../rschema_exp4_gpt_5_4_mini/` | 518 | copied for this release |
| SchemaBench | CodeLlama-13B | `/data/Text2ER/SchemaBench/Experiment2/text2schema_codellama13b/` | `.../schemabench_exp2_codellama13b/` | 239 | identical |
| SchemaBench | Llama-3.1-8B | `.../text2schema_llama31/` | `.../schemabench_exp2_llama31/` | 239 | identical |
| SchemaBench | DeepSeek-Coder-6.7B | `.../text2schema_deepseek/` | `.../schemabench_exp2_deepseek/` | 239 | `0001.json` restored from original (SB copy had a failed parse) |
| SchemaBench | Claude Sonnet 4.6 | `.../text2schema_sonnet46/` | `.../schemabench_exp2_claude_sonnet_4_6/` | 239 | copied for this release |
| SchemaBench | GPT-5.4-mini | `.../text2schema_gpt54mini/` | `.../schemabench_exp2_gpt_5_4_mini/` | 239 | copied for this release |

See `audit/E0_DIRECT_PREDICTION_VERIFICATION.csv` for hashes.

### Evaluation

| Stage | Path | Notes |
|---|---|---|
| Historical Exp4 evaluator | `/data/RSchema_ExpResults4/Code/evaluate_exp4_text2schema.py` | Used for June-2026 Exp3 archive (`exp3_combined_results.txt`). Uses synthetic Domain for untyped gold logical schemas; 5-dim hallucination; typed nGED variant. |
| Combined archive | `/data/A_Final_Result/Exp3/exp3_combined_results.txt` | Older Table V draft numbers |
| Current protocol evaluator | `src/{evaluator,metrics,schema_parser,normalization}.py` + `experiments/E0/reproduce_genuine_tables.py` | Micro F1; Domain on 381 DDL IDs; Hall4; names-only nGED |

### Gold references

| Corpus | N | Path | SHA256 |
|---|---:|---|---|
| RSchema logical | 518 | `datasets/rschema/annotation.jsonl` | `3ab18c248076f2df…` (matches `/data/RSchema/annotation.jsonl`) |
| RSchema DDL (Domain) | 381 | `datasets/rschema/annotation_ddl.jsonl` | `ce17d9aac0acba21…` (381/518 ID subset) |
| SchemaBench DDL | 239 | `datasets/schemabench/annotation_ddl.jsonl` | `2bdc9459cdacc10b…` |

## PaperMethods baselines (Table VI)

### Generation (prompting methods only; SchemaAgent excluded)

| Method | Code | Prompt function | Demonstrations |
|---|---|---|---|
| One-shot | `LLM4DBdesign` `agent_format.fully_decode` (`base_direct`) + `run_local_full.py` | `get_direct_prompt` | 1 fixed example |
| One-shot+CoT | `base_cot` | `get_cot_prompt` | 1 fixed example + Thinking Step |
| Few-shot | `base_direct --few-shot` | `get_direct_few_shot_prompt` | 3 fixed examples |

Packaged (SchemaAgent stripped): `experiments/E0/original_benchmarks/{one_shot,one_shot_cot,few_shot}/`.
Prompts: `prompts/e0/{one_shot,one_shot_cot,few_shot}.txt` + `examples_manifest.json`.

Historical local settings (from `agent_format` / runners): `temperature=0`, `max_tokens=4096`.

### Predictions — **MISSING** (per-schema trees)

Canonical trees expected at:

- `/data/LLM4DBdesign_PaperMethods/{codellama13b,llama31,deepseek}/{one_shot,one_shot_cot,few_shot}/results.jsonl`
- SchemaBridge `results/predictions/e0/rschema_papermethods/...`

**Status: unrecoverable on this host** (directory deleted; not in GitHub; not in archives/agent stores; exhaustive `/` search 2026-11-11).

Near-miss only: `/data/LLM4DBdesign/outputs/prompt_conditions_v2/*.jsonl` (518×9) — **different failure counts** (e.g. CodeLlama one_shot zeros 199 vs archived 3), must not be relabeled as PaperMethods.

### Archived aggregate scores (survive; used as ARCHIVE_AGGREGATE)

| Artifact | Path | SHA-256 (prefix) |
|---|---|---|
| RSchema PaperMethods eval | `results/baselines/e0_rschema_papermethods_evaluation.json` (2026-10-12) | `644d8217beac7510…` |
| RSchema PaperMethods report | `results/baselines/e0_rschema_papermethods_report.txt` | `c21c38ab6b938209…` |
| SchemaBench PaperMethods eval | `results/baselines/e0_schemabench_papermethods_evaluation.json` | `c7a38a9021a9d598…` |
| Comparison vs older paper draft | `results/baselines/paper_methods_vs_paper_tables_comparison.txt` | `c70fcf08d3d6b8e3…` |

Original scorer: `third_party/evaluate_paper_methods_exp4_metrics.py` (macro means + embedded `f1_micro` / G·P·M counts).

`reproduce_genuine_tables.py` falls back to ARCHIVE_AGGREGATE when trees are missing:
micro T/A/E/R + Hall4 from pooled counts; nGED = archived historical macro mean.

### SchemaAgent

Multi-agent path in `agent_format.py` (`expert_analyse` / quality-control loops) is **excluded** from this release. Table VI does not include SchemaAgent rows.

## Table mapping

| Table | Source of reported cells | Offline recompute |
|---|---|---|
| Table V | Current manuscript values in `audit/E0_CURRENT_MANUSCRIPT_VALUES.json` | `python3 experiments/E0/reproduce_genuine_tables.py` on Direct prediction trees |
| Table VI Direct rows | Must equal Table V RSchema rows | Copied from Table V in reproduce script |
| Table VI One-shot / CoT / Few-shot | Current manuscript; historically PaperMethods trees | **ARCHIVE_AGGREGATE** from pooled G/P/M (full per-schema recompute **BLOCKED** until trees recovered) |

## Important provenance caveat

`configs/paper_reference_values.json` stores an **earlier** Table V draft (≈ Exp3 archive: e.g. CodeLlama RSchema nGED 0.734, Domain 0.217).
The **current** manuscript uses the genuine-gold protocol for at least some open-weight cells (e.g. CodeLlama nGED 0.583, Domain 0.115), but several closed-model cells still match the older draft. Full cell-level status: `audit/E0_PAPER_COMPARISON.csv` and `audit/E0_VERIFICATION_REPORT.md`.
