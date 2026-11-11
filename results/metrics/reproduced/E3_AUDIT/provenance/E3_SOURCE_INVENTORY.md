# E3 Source Inventory — Constructor Isolation (`tab:e3_overall`)

## Naming map (critical)

Paper **E3** (constructor isolation) was historically executed under folders named **`Exp4`**.

| Paper name | Historical disk name | Role |
|---|---|---|
| E3 | `*/Exp4/text2schema_*` + `Schema2Text2_gpt54mini` / `schema2text_gpt54mini` | Frozen GPT-5.4-mini detailed NL → five constructors |
| E2 | `*/Experiment2/text2schema_gpt4omini_schema2text_*` | Describer ablation; GPT-4o-mini constructor |
| (not E3) | `A_Final_Result/Exp3/` | **Direct** Text2Schema from gold NL (different experiment) |
| (not E3) | `RSchema_ExpResults4/Experiment3/Case1Q*` | Structural masking → paper **E4** |

SchemaBridge stubs under `experiments/E3/` previously marked E3 BLOCKED because they looked for an `e3/` tree instead of `Exp4/`.

## Pipeline (PRIMARY)

```
Gold schema
  → GPT-5.4-mini DETAILED Schema2Text (frozen)
  → identical NL to each of 5 constructors
  → predicted DDL/metadata
  → locked E2 vendor evaluator (normalize_rschema_name)
  → nGED + Hall(T,A,E,R) + micro F1(T,A,D,E,R)
```

Population: **145 + 381 + 239 = 765** (×5 = **3,825** evaluations).

RSchema PRIMARY uses genuine DDL IDs from `annotation_ddl.jsonl` via
`E2_AUDIT/manifests/RSCHEMA_381_ELIGIBLE.csv`. Historical July 2026 Exp4
aggregates used **N=518** synthetic gold from `annotation.jsonl` and are **not**
the paper PRIMARY table.

## 1. Frozen GPT-5.4-mini detailed descriptions (E1 detailed outputs)

| Dataset | Path | Count | Content hash (16) |
|---|---|---:|---|
| Enterprise-145 | `/data/LLMTranslations/Exp2/Schema2Text2_gpt54mini/` | 145 `.txt`/`.json` | `c461bac5f89db14b` |
| RSchema | `/data/RSchema_ExpResults4/Experiment2/schema2text_gpt54mini/` | 518 (381 used) | `c8571cb03432df26` |
| SchemaBench | `/data/Text2ER/SchemaBench/Experiment/schema2text_gpt54mini/` | 239 | `05bb919ddebd57a5` |

Prompt (identical text): `/data/SchemaBridge/prompts/describer_detailed.txt`  
Original generators:

- RSchema: `/data/RSchema_ExpResults4/Code/rschema_exp2_schema2text_api.py` (`SYSTEM_PROMPT_SCHEMA2TEXT2`)
- SchemaBench: `/data/Text2ER/SchemaBench/Code/schemabench_exp4_schema2text_api.py`
- Enterprise: `/data/Text2ER/experiments/schema2text2_api.py`

## 2. Text2Schema constructor prompt

- Canonical: `SYSTEM_PROMPT` in `/data/RSchema_ExpResults4/Code/rschema_exp4_text2schema_gpt4omini.py`
- SchemaBridge copy: `/data/SchemaBridge/prompts/constructor.txt`
- User message builder: `_build_user_content(nl_text, database)` in `rschema_exp4_text2schema_allLLM.py`

No model-specific prompt forks were found for the five constructors (same system prompt; decoding configs differ).

## 3. Constructor inference scripts

| Constructor | Model ID | Runner (RSchema) | Decoding |
|---|---|---|---|
| CodeLlama-13B | `codellama/CodeLlama-13b-Instruct-hf` | `rschema_exp4_text2schema_experiment2_allLLM.py` | HF temp=0.1, max_new=2048 |
| Llama-3.1-8B | `meta-llama/Meta-Llama-3.1-8B-Instruct` | same | same |
| DeepSeek-Coder | `deepseek-ai/deepseek-coder-6.7b-instruct` | same | same |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | `rschema_exp4_text2schema_sonnet46_batch.py` | Batch API temp=0.2 |
| GPT-5.4-mini | `gpt-5.4-mini` | `rschema_exp4_text2schema_gpt54mini_batch.py` | Batch API temp=0.2 |

SchemaBench: `/data/Text2ER/SchemaBench/Code/schemabench_exp4_text2schema_*`  
Enterprise: `/data/Text2ER/experiments/text2schema_exp4_*` / `LLMTranslations` Exp4 outputs

## 4. Predictions (original experimental run)

| Dataset | Directory pattern | Files / constructor |
|---|---|---|
| Enterprise-145 | `/data/LLMTranslations/Exp4/Text2Schema2_{llm}/` | 145 json+txt |
| RSchema | `/data/RSchema_ExpResults4/Exp4/text2schema_{llm}/` | 518 json+txt (PRIMARY uses 381) |
| SchemaBench | `/data/Text2ER/SchemaBench/Exp4/text2schema_{llm}/` | 239 json+txt |

Each JSON embeds `nl_text`, `source_schema2text_llm=gpt54mini`, `model_id`, `ddl`, `metadata`.

## 5. Gold references (PRIMARY)

| Dataset | Gold | N |
|---|---|---:|
| Enterprise-145 | `/data/Text2ER/schema/{name}.sql` + `.metadata.json` | 145 |
| RSchema | `/data/RSchema/annotation_ddl.jsonl` (381 IDs) | 381 |
| SchemaBench | `/data/SchemaBench/Dataset/annotation_ddl.jsonl` | 239 |

## 6. Metric implementation (locked)

Vendor (same as E2 PRIMARY): `/data/SchemaBridge/experiments/E2/vendor/`

| Metric | Function / definition |
|---|---|
| Element scores | `evaluate_text2schema2.evaluate_one` |
| Micro aggregate | `evaluate_exp4_text2schema.agg_element` |
| nGED | `normalized_graph_edit_distance` — tables + `(col,type_family,null)` + FK edges; `edit/(g_size+p_size)` |
| Hallucination | mean of micro FP rates over **T,A,E,R** (Domain excluded) |
| Name norm | `normalize_rschema_name` |

Independent runner: `E3_AUDIT/evaluate_e3_primary.py`  
Log: `E3_AUDIT/logs/evaluate_e3_primary.log` (EXIT:0)

## 7. Historical aggregates (not PRIMARY)

- `/data/A_Final_Result/Exp4/combine_exp4_results.py` + `exp4_combined_results.txt` — N=518 RSchema, Hall averaged over **5** dims including Domain, Enterprise used `strip().lower()` norm → **does not match** paper `tab:e3_overall`.
- Per-dataset `*/Exp4/Result/*_evaluation.json` — same historical protocol.

## 8. This audit outputs

All under `/data/SchemaBridge/results/metrics/reproduced/E3_AUDIT/`:

- `metrics/E3_PRIMARY_FINAL.csv`, `E3_CELL_COMPARISON_105.csv`, `E3_PRIMARY_RESULTS.json`, `E3_CASE_LEVEL.jsonl`
- `isolation/isolation_summary.json`, `isolation_schema_hashes.csv`
- `inventory/group_completeness.csv`
- `latex/tab_e3_overall_verified.tex`
- `E3_AUDIT_REPORT.md`, `E3_MATCH_COUNTS.json`
