# E2 — Round-Trip Preservation (Table VIII, `tab:e2_roundtrip`)

Schema → Text (E1 Basic/Detailed) → Schema with **fixed GPT-4o-mini** constructor.

| | |
|---|---|
| **PRIMARY population** | Enterprise-145 **145** + RSchema genuine DDL **381** + SchemaBench **239** = **765** |
| Describers | CodeLlama-13B, Llama-3.1-8B, DeepSeek-Coder, Claude Sonnet 4.6, GPT-5.4-mini |
| Prompts | `prompts/describer_basic.txt`, `prompts/describer_detailed.txt` |
| Constructor | `prompts/constructor.txt` (`gpt-4o-mini`, T=0.2) |
| Metrics | mean nGED; micro F1 for Tables / Attributes / Domain / Entity / Referential |
| Verified artifacts | `results/metrics/reproduced/E2_AUDIT/` |

## Authoritative offline reproduction

Original GPT-4o-mini reconstruction trees are **not** shipped in git (~0.14 GiB JSON).
Place them at the paths in `results/metrics/reproduced/E2_AUDIT/provenance/prediction_manifest.csv`
(checksums in `source_hashes.json`).

```bash
# Validate gold + RSchema-381 manifest
python3 experiments/E2/prepare_dataset.py

# Recompute all 30 groups → E2_AUDIT/metrics/
PYTHONHASHSEED=0 python3 experiments/E2/evaluate_table_viii_full.py
# or: python3 experiments/E2/evaluate.py

# Build Overleaf table
PYTHONHASHSEED=0 python3 experiments/E2/generate_table_viii.py

pytest -q tests/test_e2_primary.py tests/test_metrics.py
```

Generation is disabled:

```bash
python3 experiments/E2/run.py   # refuses API / paid inference
```

## Metric definitions (PRIMARY)

- **nGED** = edit_cost / max(gold_size + pred_size, 1); arithmetic mean over the population; failures → 1.0.
- **Micro F1** aggregates gold/predicted/matched counts over the population, then P/R/F1 (not a macro mean of per-schema F1).
- **Domain** requires type-family compatibility **and** nullability agreement.
- **Failures** (empty/unparseable): matched=0, recreated=0, gold retained, schema stays in N.

Deterministic name-collision handling is implemented under `experiments/E2/vendor/` (sorted maps). Prefer `PYTHONHASHSEED=0`.

## What is *not* PRIMARY

| Artifact | Role |
|---|---|
| `results/metrics/archived/e2_rschema_roundtrip_evaluation.json` | Historical RSchema **N=518** Detailed open-model archive |
| `/data/A_Final_Result/Exp2/a.txt` | July 2026 Detailed-only table (RSchema N=518) |
| `results/predictions/e2/schemabench_rt_*` | Incomplete package copies — do not use |
| `tab:e2_combined_prf1` | Historical macro-average; **not** recomputed for PRIMARY |

## Trajectory figure

`results/metrics/reproduced/E2_AUDIT/figures/cmp_chart4_trajectory.{png,pdf}` — mean of five micro-F1 dimensions by size×content over the **765** PRIMARY schemata (caption must not claim 902).
