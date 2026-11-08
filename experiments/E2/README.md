# E2 - Round trip Schema -> Text -> Schema (Table VIII, `tab:e2_roundtrip`)

**Paper table label:** `tab:e2_roundtrip`

| | |
|---|---|
| Datasets | RSchema (518); SchemaBench (239); Enterprise-145 (145) |
| Models | Describers: CodeLlama-13B, Llama-3.1-8B, DeepSeek-Coder (open), Claude Sonnet 4.6, GPT-5.4-mini; constructor fixed to GPT-4o-mini |
| Metrics | nGED; Tables / Attributes / Domain / Entity / Referential micro F1; Basic (B) and Detailed (D) describers |
| Prompts | prompts/describer_basic.txt, prompts/describer_detailed.txt, prompts/constructor.txt |

## Artefacts used (offline)

Predictions (symlinks, may dangle on other machines):
- `results/predictions/e2/rschema_rt_{codellama13b,llama31,deepseek}`
- `results/predictions/e2/schemabench_rt_{codellama13b,llama31,deepseek} (INCOMPLETE: 216/195/227 of 239)`

Archived metrics:
- results/metrics/archived/e2_rschema_roundtrip_evaluation.json (+ _report.txt)

## Status (honest)

RSchema Detailed: most cells PASS, a few MISMATCH at the 0.0005 tolerance; SchemaBench incomplete -> BLOCKED; Enterprise-145, Basic, Claude/GPT BLOCKED.


## Run

```bash
python experiments/E2/evaluate.py            # offline comparison, writes results/metrics/reproduced/E2_*.csv

python experiments/E2/run.py                 # refuses to generate; prints how to use archived predictions
```

Status codes: `PASS`, `MISMATCH` (outside tolerance 0.0005, 0.005 for BLEU-4), `PARTIAL`, `BLOCKED` (artefact missing; never filled with invented numbers).
