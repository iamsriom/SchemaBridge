# E1 - Schema -> Text (Table VII, `tab:e1_s2t`)

**Paper table label:** `tab:e1_s2t`

| | |
|---|---|
| Datasets | RSchema (518); SchemaBench (239); Enterprise-145 (145, SCR only) |
| Models | CodeLlama-13B, Llama-3.1-8B, DeepSeek-Coder (open); Claude Sonnet 4.6, GPT-5.4-mini (paper only) |
| Metrics | BLEU-4 (0-100), ROUGE-L, BERTScore-F1, SCR (schema coverage) for Basic (B) and Detailed (D) describer prompts |
| Prompts | prompts/describer_basic.txt, prompts/describer_detailed.txt |

## Artefacts used (offline)

Predictions (symlinks, may dangle on other machines):
- `results/predictions/e1/rschema_schema2text_{codellama13b,llama31,deepseek}`
- `results/predictions/e1/schemabench_schema2text_{codellama13b,llama31,deepseek}`

Archived metrics:
- results/metrics/archived/e1_rschema_schema2text_evaluation.json (matches the paper DETAILED columns 9/9; BERTScore skipped)

## Status (honest)

RSchema Detailed BLEU/ROUGE/SCR for the 3 open models PASS; Basic, BERTScore, Claude/GPT, SchemaBench, Enterprise-145 BLOCKED.


## Run

```bash
python experiments/E1/evaluate.py            # offline comparison, writes results/metrics/reproduced/E1_*.csv

python experiments/E1/run.py                 # refuses to generate; prints how to use archived predictions
```

Status codes: `PASS`, `MISMATCH` (outside tolerance 0.0005, 0.005 for BLEU-4), `PARTIAL`, `BLOCKED` (artefact missing; never filled with invented numbers).
