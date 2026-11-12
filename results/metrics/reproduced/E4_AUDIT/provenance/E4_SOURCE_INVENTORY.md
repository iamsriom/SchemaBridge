# E4 source inventory (private artifacts)

These paths are **not** in git. They are required only for optional full recompute.

Set `SCHEMA_BRIDGE_DATA` to the data root (historically `/data`).

| Role | Relative to data root |
|---|---|
| Enterprise gold | `Text2ER/schema/` + `index.json` |
| SchemaBench gold | `SchemaBench/Dataset/annotation_ddl.jsonl` |
| RSchema gold | `RSchema/annotation.jsonl` |
| Enterprise Direct | `LLMTranslations/Cases_GPT4omini/{TableName,Attribute,Domain,Entity,Referential}Mask_T/` |
| SchemaBench Direct | `SchemaBench/Experiment3_GPT4omini/*Mask_T/` |
| RSchema Direct | `Text2ER/RSchema_ExpResults4/Experiment3_Gpt4omini/*Mask_T/` |
| Enterprise RT | `LLMTranslations/CasesTranslations/Case1Q*_*/` |
| SchemaBench RT | `SchemaBench/Experiment3_Translations/Case1Q*_*/` |
| RSchema RT | `Text2ER/RSchema_ExpResults4/Experiment3_Translations/Case1Q*_*/` |
| Historical Exp5 labels/eval | `A_Final_Result/Exp5/exp3_inferability_*.csv` |
| Text2ER analysis code | sibling `Text2ER/analyze_exp3_inferability.py` (via `SCHEMA_BRIDGE_TEXT2ER`) |

PRIMARY manuscript numbers are frozen in `experiments/E4/verified_values.py` and do not require these dumps to **verify** the published tables.
