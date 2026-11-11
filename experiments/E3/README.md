# E3 — Constructor isolation (Table IX, `tab:e3_overall`)

**Paper table labels:** `tab:e3_overall` / `tab:e3_constructor`

| | |
|---|---|
| Datasets | Enterprise-145 (N=145); SchemaBench (N=239); RSchema (N=381 genuine DDL — PRIMARY, not synthetic 518) |
| Fixed describer | GPT-5.4-mini (`gpt54mini`) + **Detailed** prompt only (`prompts/describer_detailed.txt`) |
| Constructors | `codellama13b`, `llama31`, `deepseek`, `sonnet46`, `gpt54mini` |
| Constructor prompt | `prompts/constructor.txt` (same Text2Schema prompt as E2) |
| Metrics | mean nGED; mean Hall. (5-dim micro FP); micro-F1 for Tables / Attributes / Domain / Entity / Referential |

Constructor prompt SHA-256: `392a396f7073bc015d206460055f7e3b8a3c94a21ed09c059bc47c13d3884ad4`
Detailed describer SHA-256: `f09fc8cae8d8ec73deb79f8bc7c2e71842d5fd35e92d833a02954b539755622d`

## Protocol

Every constructor reconstructs from the **same** original GPT-5.4-mini Detailed description for a given schema. Isolation is verified by hashing `nl_text` across constructors (`validate_inputs.py`).

Empty gold + empty reconstruction ⇒ **valid**, nGED = 0. Invalid/missing reconstructions ⇒ nGED = 1 and zero recreations under `--fail-policy score` (default).

## Modes

* **Offline evaluation (default path for published numbers):** load local reconstructions; no LLM.
* **Dry-run inference (default for `run.py`):** validate constructor payloads; no network / no GPU weights.
* **Open-weight execute:** `--execute` for CodeLlama / Llama-3.1 / DeepSeek only.
* **Paid API constructors** (`sonnet46`, `gpt54mini`): execute paths are **disabled** in this package (dry-run payload sizing only). Supply locally generated reconstructions to evaluate offline.

## Commands

```bash
# 0. dataset eligibility (reuses E1)
python experiments/E1/prepare_dataset.py --out-dir experiments/E1/outputs/datasets

# 1. fixed descriptions (from E1 Detailed GPT-5.4-mini — generate locally or load existing)
python experiments/E3/prepare_inputs.py --dataset rschema \
    --descriptions-dir experiments/E1/outputs/rschema_detailed_gpt54mini

# 2. constructors (dry-run first)
python experiments/E3/run.py --dataset rschema --constructor llama31 \
    --descriptions-dir experiments/E1/outputs/rschema_detailed_gpt54mini
python experiments/E3/run.py --dataset rschema --constructor llama31 \
    --descriptions-dir experiments/E1/outputs/rschema_detailed_gpt54mini --execute

# 3. isolation check
python experiments/E3/validate_inputs.py --dataset rschema \
    --descriptions-dir experiments/E1/outputs/rschema_detailed_gpt54mini \
    --pred-parent experiments/E3/outputs

# 4. offline evaluation
python experiments/E3/evaluate.py --dataset rschema --constructor llama31 \
    --pred-dir experiments/E3/outputs/rschema_detailed_llama31
python experiments/E3/evaluate.py --dataset all --constructor all --pred-dir experiments/E3/outputs

# 5. LaTeX skeleton of Table IX from local metrics (values stay local)
python experiments/E3/generate_table_ix.py --metrics-dir experiments/E3/outputs/metrics
```

Outputs are git-ignored (`experiments/E3/outputs/`). **This repository ships no experimental scores, predictions, or Table IX numbers.**

## What is *not* E3

`results/predictions/e3/rschema_cases_describer` is historical **masking** describer output (paper **E4**). Kept for migration traceability only.

See `docs/REPRODUCE_E3.md` and `audit/E3_reproduction.md`.
