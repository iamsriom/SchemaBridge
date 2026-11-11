# E2 PRIMARY evaluation protocol

## Population
- Enterprise-145: 145 (`/data/Text2ER/schema`)
- RSchema: **381** genuine DDL IDs from `manifests/RSCHEMA_381_ELIGIBLE.csv` (intersection with `annotation_ddl.jsonl` by schema_id — not positional)
- SchemaBench: 239 (`annotation_ddl.jsonl`)
- Total: **765**

## Constructor
Fixed `gpt-4o-mini`, temperature 0.2, prompt `prompts/constructor.txt`.

## Metrics
- **nGED**: `edit_cost / max(gold_size + pred_size, 1)`; mean over population; failures → 1.0
- **Micro F1** (T/A/D/E/R): aggregate G/P/M then `2PR/(P+R)`; empty denominators → 0
- **Domain**: type-family (int/str families) **and** nullability YES/NO
- **Failures**: missing/empty/unparseable → matched=0, recreated=0, gold retained, remain in N

## Determinism
Vendor parsers under `experiments/E2/vendor/` with:
- sorted table iteration in `_column_labels` (collision-safe)
- deterministic `_norm_map` for name normalization collisions
- `PYTHONHASHSEED=0` recommended

## Command
```bash
PYTHONHASHSEED=0 python3 experiments/E2/evaluate_table_viii_full.py
PYTHONHASHSEED=0 python3 experiments/E2/generate_table_viii.py
```
