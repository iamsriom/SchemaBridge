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
* **Online (opt-in, PAID)**: `run.py --execute --confirm-paid` sends the E1 descriptions to GPT-4o-mini
  (`OPENAI_API_KEY` from the environment). Without `--execute` the run is a dry-run that validates
  every payload without any API call.

Failed / missing reconstructions (`--fail-policy score`, default): all five F1 dimensions keep the gold
counts with recreated = matched = 0, and nGED = 1. `--fail-policy skip` drops them.

## Commands

```bash
# 1. construct (dry-run first, then paid execute)
python experiments/E2/run.py --dataset rschema --describer-model llama31 --prompt detailed \
    --e1-pred-dir experiments/E1/outputs/rschema_detailed_llama31
python experiments/E2/run.py --dataset rschema --describer-model llama31 --prompt detailed \
    --e1-pred-dir experiments/E1/outputs/rschema_detailed_llama31 --execute --confirm-paid

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
