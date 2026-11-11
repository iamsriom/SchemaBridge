# E2 - Round trip Schema -> Text -> Schema (Table VIII, `tab:e2_roundtrip`)

**Paper table label:** `tab:e2_roundtrip`

| | |
|---|---|
| Datasets | Enterprise-145 (N=145); SchemaBench (N=239); RSchema (N=381 genuine DDL - the PRIMARY population, not the synthetic 518) |
| Describers | `codellama13b`, `llama31`, `deepseek`, `sonnet46`, `gpt54mini` (descriptions come from E1) |
| Constructor | GPT-4o-mini (`gpt4omini`), `prompts/constructor.txt`, T=0.2, 16384 max tokens |
| Metrics | micro-F1 for Tables / Attributes / Domain / Entity / Referential, mean nGED; basic (B) and detailed (D) describer prompts |

Constructor prompt SHA-256: `392a396f7073bc015d206460055f7e3b8a3c94a21ed09c059bc47c13d3884ad4`
(describer hashes: see `experiments/E1/README.md`).

## Modes

* **Offline (default)**: evaluate existing reconstructed `NNNN.json` (archived or local).
* **Dry-run (default for `run.py`)**: validates every constructor payload; no API call, no key needed.
* **Online (opt-in, PAID)**: `run.py --execute --confirm-paid` sends the E1 descriptions to GPT-4o-mini
  and works as documented; it needs BOTH flags and `OPENAI_API_KEY` in the environment (never read from
  files, printed or stored; no keys ship with this repository). Calls are billed by OpenAI per token:
  try `--limit 1` first; `--skip-existing` (default) never re-bills finished schemas.

## E1 -> E2 provenance (strict by default)

Each E1 `NNNN.json` must prove it was produced by the requested `--describer-model` and `--prompt`:
`id` = gold schema id, `llm` = describer key, `model_id` = that model's id, `prompt_style`
(`schema2text1` / `schema2text2`) and `generation.prompt_sha256` = pinned hash (plus
`generation.prompt_variant` when present), usable `nl_text`, no `error`. Anything else is treated as a
missing description (error record, no API call) and is never relabelled. Duplicate schema ids and mixed
prompt styles inside one E1 directory abort the run. `--allow-legacy-e1` accepts old files whose provenance
fields are *missing* (with a recorded warning); *wrong* fields are always rejected. The validated provenance
is written into each E2 record (`source_*` fields).

## Empty schemas and statuses

A reconstruction `{"ddl": "", "metadata": {...}}` is a valid answer, stored as a successful record.
`evaluate.py` writes a `status` per schema:

* `ok`: non-empty reconstruction, `evaluate_schema_pair`;
* `valid_empty`: successful empty/comment-only DDL and the gold is empty too (nGED = 0, not a failure);
* `incorrect_empty`: successful empty DDL but the gold is non-empty (natural nGED via `evaluate_schema_pair`, not a failure);
* `scored_failure` (`--fail-policy score`, default): missing file / error / unparseable / id mismatch. All five F1
  dimensions keep the gold counts with recreated = matched = 0, and nGED = 1;
* `skipped` (`--fail-policy skip`): the same failures, dropped from every aggregate.

A missing file is never a valid empty schema.

## Commands

```bash
# 1. construct (dry-run first, then paid execute)
python experiments/E2/run.py --dataset rschema --describer-model llama31 --prompt detailed \
    --e1-pred-dir experiments/E1/outputs/rschema_detailed_llama31
python experiments/E2/run.py --dataset rschema --describer-model llama31 --prompt detailed \
    --e1-pred-dir experiments/E1/outputs/rschema_detailed_llama31 --execute --confirm-paid
# (old E1 files without provenance fields: add --allow-legacy-e1)

# 2. offline evaluation
python experiments/E2/evaluate.py --dataset rschema --describer-model llama31 --prompt detailed \
    --pred-dir experiments/E2/outputs/rschema_detailed_llama31
python experiments/E2/evaluate.py --dataset all --describer-model all --prompt all --pred-dir experiments/E2/outputs

# 3. LaTeX skeleton of Table VIII from the local metrics
python experiments/E2/generate_table_viii.py --metrics-dir experiments/E2/outputs/metrics
```

Outputs are git-ignored (`experiments/E2/outputs/`). Legacy archive comparison:
`python scripts/reproduce_tables.py --experiment E2 --offline`.

See `docs/REPRODUCE_E1_E2.md` for the complete guide.
