# E3 PRIMARY evaluation protocol

## Population
- Enterprise-145: 145 (`/data/Text2ER/schema`)
- RSchema: **381** genuine DDL IDs (`manifests/RSCHEMA_381_ELIGIBLE.csv` ∩ `annotation_ddl.jsonl`)
- SchemaBench: 239 (`annotation_ddl.jsonl`)
- Total: **765** × 5 constructors = **3,825**

## Fixed describer
GPT-5.4-mini **detailed** prompt (`describer_detailed.txt`). Frozen NL directories:
- Enterprise: `LLMTranslations/Exp2/Schema2Text2_gpt54mini`
- RSchema: `RSchema_ExpResults4/Experiment2/schema2text_gpt54mini`
- SchemaBench: `Text2ER/SchemaBench/Experiment/schema2text_gpt54mini`

## Constructors
Vary only the Text2Schema model; prompt = `constructor.txt` / Exp4 `SYSTEM_PROMPT`.

## Metrics
- **nGED**: per-schema `edit_cost / max(g_size + p_size, 1)` then arithmetic mean; column nodes are `(name, type_family, nullability)`; empty↔empty → 0
- **Hall.**: unweighted mean of micro FP rates on **Tables, Attributes, Entity, Referential** (Domain excluded)
- **F1 (T/A/D/E/R)**: micro-aggregate ΣG/ΣP/ΣM then P/R/F1; empty denominators → 0
- **Domain**: type-family + nullability YES/NO
- **Failures**: missing prediction scored as empty pred vs gold (remain in N). Comment-only DDL with empty gold (Enterprise `archive`/`tmp`/`ctu_vondreli`) scores nGED=0

## Determinism
- Vendor: `experiments/E2/vendor/`
- `PYTHONHASHSEED=0`
- `normalize_rschema_name` for all three datasets

## Command
```bash
cd /data/SchemaBridge
PYTHONHASHSEED=0 python3 -u results/metrics/reproduced/E3_AUDIT/evaluate_e3_primary.py
# or via screen:
# screen -S e3_audit
```
