# E0 - Text -> Schema from gold NL (Table V, `tab:e0_overall`)

**Paper table label:** `tab:e0_overall`

| | |
|---|---|
| Datasets | RSchema (518); SchemaBench (239) |
| Models | CodeLlama-13B, Llama-3.1-8B, DeepSeek-Coder-6.7B (open, local archives); Claude Sonnet 4.6, GPT-5.4-mini (paper only) |
| Metrics | nGED, Halluc (lower better); Tables / Attributes / Domain / Entity / Referential F1 (micro) |
| Prompts | prompts/constructor.txt |

## Artefacts used (offline)

Predictions (symlinks, may dangle on other machines):
- `results/predictions/e0/rschema_exp4_{codellama13b,llama31,deepseek}`
- `results/predictions/e0/schemabench_exp2_{codellama13b,llama31,deepseek}`
- `results/predictions/e0/rschema_papermethods, schemabench_papermethods (PaperMethods runs)`

Archived metrics:
- results/metrics/archived/e0_rschema_exp4_evaluation.json (+ _report.txt)
- results/baselines/e0_schemabench_papermethods_evaluation.json

## Status (honest)

RSchema: open models compared (MISMATCH on several cells; see results/metrics/reproduced/E0_cells.csv); SchemaBench: only few_shot corrected-parser baselines exist (MISMATCH expected); Claude/GPT BLOCKED.


## Run

```bash
python experiments/E0/evaluate.py            # offline comparison, writes results/metrics/reproduced/E0_*.csv
python experiments/E0/evaluate.py --recompute   # + re-evaluate RSchema preds with src/ (deterministic)
python experiments/E0/evaluate.py --vendored    # + run third_party/evaluate_exp4_text2schema.py (SCHEMABRIDGE_ROOT)
python experiments/E0/run.py                 # refuses to generate; prints how to use archived predictions
```

Status codes: `PASS`, `MISMATCH` (outside tolerance 0.0005, 0.005 for BLEU-4), `PARTIAL`, `BLOCKED` (artefact missing; never filled with invented numbers).
