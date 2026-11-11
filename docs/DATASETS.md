# Datasets

Enterprise-145 (145), RSchema (381 DDL-matched of 518 logical annotations), SchemaBench (239).

| Dataset | E1 / E2 population | Gold text | Gold DDL |
|---|---|---|---|
| Enterprise-145 | 145 | none (SCR only in E1) | `datasets/enterprise145/schema/*.sql` |
| SchemaBench | 239 | `question` | `annotation_ddl.jsonl` |
| RSchema | **381** | `question` | `annotation_ddl.jsonl` (genuine DDL) |

RSchema: `annotation.jsonl` has 518 logical annotations; 381 of them have genuine DDL in `annotation_ddl.jsonl`
(matched by `id`) and form the E1/E2 population. The remaining 137 only admit a synthetic varchar(255) DDL and are
excluded. File serials (`NNNN`) are the 1-based positions in the 518-record file, so they are not contiguous.
`python experiments/E1/prepare_dataset.py` validates 145/239/381/518 and writes `RSCHEMA_381_ELIGIBLE.csv`
(`schema_id, serial_in_518, eval_index, database`) into a git-ignored directory.

Data roots are searched in this order: `--data-root`, `$SCHEMABRIDGE_DATA_ROOT`, packaged `datasets/`.
