# E2 Source Inventory

Host: `server2` (`130.225.37.244`). No new LLM inference. Constructor: **GPT-4o-mini**.

## Prediction directories (30 cells = 3 datasets × 5 describers × 2 prompts)

| Dataset | Prompt | Describer | Pred dir | NL dir | JSON count | Population |
|---|---|---|---|---|---:|---|
| Enterprise-145 | basic | CodeLlama-13B | `/data/LLMTranslations/Exp1/Text2Schema1_codellama13b` | `/data/LLMTranslations/Exp1/Schema2Text1_codellama13b` | 145 | enterprise_145 |
| SchemaBench | basic | CodeLlama-13B | `/data/SchemaBench/Exp1/text2schema_gpt4omini_schema2text_codellama13b` | `/data/SchemaBench/Exp1/schema2text_codellama13b` | 239 | schemabench_239 |
| RSchema | basic | CodeLlama-13B | `/data/RSchema_ExpResults4/Exp1/text2schema_gpt4omini_schema2text_codellama13b` | `/data/RSchema_ExpResults4/Exp1/schema2text_codellama13b` | 518 | genuine_ddl_381 |
| Enterprise-145 | basic | Llama-3.1-8B | `/data/LLMTranslations/Exp1/Text2Schema1_llama31` | `/data/LLMTranslations/Exp1/Schema2Text1_llama31` | 145 | enterprise_145 |
| SchemaBench | basic | Llama-3.1-8B | `/data/SchemaBench/Exp1/text2schema_gpt4omini_schema2text_llama31` | `/data/SchemaBench/Exp1/schema2text_llama31` | 239 | schemabench_239 |
| RSchema | basic | Llama-3.1-8B | `/data/RSchema_ExpResults4/Exp1/text2schema_gpt4omini_schema2text_llama31` | `/data/RSchema_ExpResults4/Exp1/schema2text_llama31` | 518 | genuine_ddl_381 |
| Enterprise-145 | basic | DeepSeek-Coder | `/data/LLMTranslations/Exp1/Text2Schema1_deepseek` | `/data/LLMTranslations/Exp1/Schema2Text1_deepseek` | 145 | enterprise_145 |
| SchemaBench | basic | DeepSeek-Coder | `/data/SchemaBench/Exp1/text2schema_gpt4omini_schema2text_deepseek` | `/data/SchemaBench/Exp1/schema2text_deepseek` | 239 | schemabench_239 |
| RSchema | basic | DeepSeek-Coder | `/data/RSchema_ExpResults4/Exp1/text2schema_gpt4omini_schema2text_deepseek` | `/data/RSchema_ExpResults4/Exp1/schema2text_deepseek` | 518 | genuine_ddl_381 |
| Enterprise-145 | basic | Claude Sonnet 4.6 | `/data/LLMTranslations/Exp1/Text2Schema1_sonnet46` | `/data/LLMTranslations/Exp1/Schema2Text1_sonnet46` | 145 | enterprise_145 |
| SchemaBench | basic | Claude Sonnet 4.6 | `/data/SchemaBench/Exp1/text2schema_gpt4omini_schema2text_sonnet46` | `/data/SchemaBench/Exp1/schema2text_sonnet46` | 239 | schemabench_239 |
| RSchema | basic | Claude Sonnet 4.6 | `/data/RSchema_ExpResults4/Exp1/text2schema_gpt4omini_schema2text_sonnet46` | `/data/RSchema_ExpResults4/Exp1/schema2text_sonnet46` | 518 | genuine_ddl_381 |
| Enterprise-145 | basic | GPT-5.4-mini | `/data/LLMTranslations/Exp1/Text2Schema1_gpt54mini` | `/data/LLMTranslations/Exp1/Schema2Text1_gpt54mini` | 145 | enterprise_145 |
| SchemaBench | basic | GPT-5.4-mini | `/data/SchemaBench/Exp1/text2schema_gpt4omini_schema2text_gpt54mini` | `/data/SchemaBench/Exp1/schema2text_gpt54mini` | 239 | schemabench_239 |
| RSchema | basic | GPT-5.4-mini | `/data/RSchema_ExpResults4/Exp1/text2schema_gpt4omini_schema2text_gpt54mini` | `/data/RSchema_ExpResults4/Exp1/schema2text_gpt54mini` | 518 | genuine_ddl_381 |
| Enterprise-145 | detailed | CodeLlama-13B | `/data/LLMTranslations/Exp2/Text2Schema2_codellama13b` | `/data/LLMTranslations/Exp2/Schema2Text2_codellama13b` | 145 | enterprise_145 |
| SchemaBench | detailed | CodeLlama-13B | `/data/Text2ER/SchemaBench/Experiment/text2schema_gpt4omini_schema2text_codellama13b` | `/data/Text2ER/SchemaBench/Experiment/schema2text_codellama13b` | 239 | schemabench_239 |
| RSchema | detailed | CodeLlama-13B | `/data/RSchema_ExpResults4/Experiment2/text2schema_gpt4omini_schema2text_codellama13b` | `/data/RSchema_ExpResults4/Experiment2/schema2text_codellama13b` | 518 | genuine_ddl_381 |
| Enterprise-145 | detailed | Llama-3.1-8B | `/data/LLMTranslations/Exp2/Text2Schema2_llama31` | `/data/LLMTranslations/Exp2/Schema2Text2_llama31` | 145 | enterprise_145 |
| SchemaBench | detailed | Llama-3.1-8B | `/data/Text2ER/SchemaBench/Experiment/text2schema_gpt4omini_schema2text_llama31` | `/data/Text2ER/SchemaBench/Experiment/schema2text_llama31` | 239 | schemabench_239 |
| RSchema | detailed | Llama-3.1-8B | `/data/RSchema_ExpResults4/Experiment2/text2schema_gpt4omini_schema2text_llama31` | `/data/RSchema_ExpResults4/Experiment2/schema2text_llama31` | 518 | genuine_ddl_381 |
| Enterprise-145 | detailed | DeepSeek-Coder | `/data/LLMTranslations/Exp2/Text2Schema2_deepseek` | `/data/LLMTranslations/Exp2/Schema2Text2_deepseek` | 145 | enterprise_145 |
| SchemaBench | detailed | DeepSeek-Coder | `/data/Text2ER/SchemaBench/Experiment/text2schema_gpt4omini_schema2text_deepseek` | `/data/Text2ER/SchemaBench/Experiment/schema2text_deepseek` | 239 | schemabench_239 |
| RSchema | detailed | DeepSeek-Coder | `/data/RSchema_ExpResults4/Experiment2/text2schema_gpt4omini_schema2text_deepseek` | `/data/RSchema_ExpResults4/Experiment2/schema2text_deepseek` | 518 | genuine_ddl_381 |
| Enterprise-145 | detailed | Claude Sonnet 4.6 | `/data/LLMTranslations/Exp2/Text2Schema2_sonnet46` | `/data/LLMTranslations/Exp2/Schema2Text2_sonnet46` | 145 | enterprise_145 |
| SchemaBench | detailed | Claude Sonnet 4.6 | `/data/Text2ER/SchemaBench/Experiment/text2schema_gpt4omini_schema2text_sonnet46` | `/data/Text2ER/SchemaBench/Experiment/schema2text_sonnet46` | 239 | schemabench_239 |
| RSchema | detailed | Claude Sonnet 4.6 | `/data/RSchema_ExpResults4/Experiment2/text2schema_gpt4omini_schema2text_sonnet46` | `/data/RSchema_ExpResults4/Experiment2/schema2text_sonnet46` | 518 | genuine_ddl_381 |
| Enterprise-145 | detailed | GPT-5.4-mini | `/data/LLMTranslations/Exp2/Text2Schema2_gpt54mini` | `/data/LLMTranslations/Exp2/Schema2Text2_gpt54mini` | 145 | enterprise_145 |
| SchemaBench | detailed | GPT-5.4-mini | `/data/Text2ER/SchemaBench/Experiment/text2schema_gpt4omini_schema2text_gpt54mini` | `/data/Text2ER/SchemaBench/Experiment/schema2text_gpt54mini` | 239 | schemabench_239 |
| RSchema | detailed | GPT-5.4-mini | `/data/RSchema_ExpResults4/Experiment2/text2schema_gpt4omini_schema2text_gpt54mini` | `/data/RSchema_ExpResults4/Experiment2/schema2text_gpt54mini` | 518 | genuine_ddl_381 |

## Roots by experiment family

- Enterprise Basic: `/data/LLMTranslations/Exp1/Text2Schema1_<describer>/`
- Enterprise Detailed: `/data/LLMTranslations/Exp2/Text2Schema2_<describer>/`
- RSchema Basic: `/data/RSchema_ExpResults4/Exp1/text2schema_gpt4omini_schema2text_<describer>/`
- RSchema Detailed: `/data/RSchema_ExpResults4/Experiment2/text2schema_gpt4omini_schema2text_<describer>/`
- SchemaBench Basic: `/data/SchemaBench/Exp1/text2schema_gpt4omini_schema2text_<describer>/`
- SchemaBench Detailed: `/data/Text2ER/SchemaBench/Experiment/text2schema_gpt4omini_schema2text_<describer>/` (byte-identical copy also under `/data/SchemaBench/Experiment/`)

## Excluded (not E2)

- `/data/*/Exp4/` and `text2schema_<describer>/` trees: **E3** constructor isolation (varying constructor).
- E0 direct construction and E4 masking trees: excluded.

## NL provenance check (embedded `nl_text` vs E1 `.txt`)

| Dataset | Prompt | Model | nl_match | nl_mismatch |
|---|---|---|---:|---:|
| Enterprise-145 | basic | codellama13b | 145 | 0 |
| SchemaBench | basic | codellama13b | 239 | 0 |
| RSchema | basic | codellama13b | 381 | 0 |
| Enterprise-145 | basic | llama31 | 145 | 0 |
| SchemaBench | basic | llama31 | 239 | 0 |
| RSchema | basic | llama31 | 381 | 0 |
| Enterprise-145 | basic | deepseek | 145 | 0 |
| SchemaBench | basic | deepseek | 239 | 0 |
| RSchema | basic | deepseek | 381 | 0 |
| Enterprise-145 | basic | sonnet46 | 145 | 0 |
| SchemaBench | basic | sonnet46 | 239 | 0 |
| RSchema | basic | sonnet46 | 381 | 0 |
| Enterprise-145 | basic | gpt54mini | 145 | 0 |
| SchemaBench | basic | gpt54mini | 239 | 0 |
| RSchema | basic | gpt54mini | 381 | 0 |
| Enterprise-145 | detailed | codellama13b | 145 | 0 |
| SchemaBench | detailed | codellama13b | 239 | 0 |
| RSchema | detailed | codellama13b | 381 | 0 |
| Enterprise-145 | detailed | llama31 | 145 | 0 |
| SchemaBench | detailed | llama31 | 239 | 0 |
| RSchema | detailed | llama31 | 381 | 0 |
| Enterprise-145 | detailed | deepseek | 145 | 0 |
| SchemaBench | detailed | deepseek | 239 | 0 |
| RSchema | detailed | deepseek | 381 | 0 |
| Enterprise-145 | detailed | sonnet46 | 145 | 0 |
| SchemaBench | detailed | sonnet46 | 239 | 0 |
| RSchema | detailed | sonnet46 | 381 | 0 |
| Enterprise-145 | detailed | gpt54mini | 145 | 0 |
| SchemaBench | detailed | gpt54mini | 239 | 0 |
| RSchema | detailed | gpt54mini | 381 | 0 |

Total mismatches across PRIMARY cells: 0.
