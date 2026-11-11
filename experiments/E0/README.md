# E0 — Text → Schema from gold NL

Canonical offline evaluator: `reproduce_genuine_tables.py` (also via `evaluate.py`).  
Canonical closed Direct inference: `run_direct_api.py` (also via `run.py --online --confirm-paid`).

**E0 Direct is reproducible from original saved predictions kept privately.**  
**PaperMethods prompting baselines remain partially reproducible** until per-schema
`results.jsonl` trees are recovered (archive aggregates are optional local inputs).

| | |
|---|---|
| Datasets | RSchema (518 logical; Domain on 381 matched DDL); SchemaBench (239 DDL) |
| Table V models | CodeLlama-13B, Llama-3.1-8B, DeepSeek-Coder-6.7B, Claude Sonnet 4.6, GPT-5.4-mini |
| Optional | GPT-4o-mini (`--include-gpt4o-mini`) |
| Constructor prompt | [`prompts/constructor.txt`](../../prompts/constructor.txt) |
| Prompting templates | [`prompts/e0/`](../../prompts/e0/), [`original_benchmarks/prompts/`](original_benchmarks/prompts/) |

## Protocol

| Metric | Definition |
|---|---|
| Structural F1 (T/A/E/R) | Micro-averaged; RSchema vs 518 logical; SchemaBench vs 239 DDL |
| Domain F1 | Micro over columns with recognised type **and** known nullability; RSchema 381 genuine DDL IDs; SchemaBench 239. Untyped baselines: `--` |
| Hallucination | \(H=\frac14\sum_{d\in\{T,A,E,R\}}\max(0,P_d-M_d)/P_d\) micro; Domain excluded |
| nGED | Structural `names_only=True` (tables + table-qualified attribute names + directed FK edges) |
| Failures | Empty prediction kept in population; nGED=1; Hall not forced to 1 |
| Parser | `legacy=False` (F1–F6 + `--Foreachtable:CREATE TABLE` recovery); DDL authoritative |

Coverage statuses: `COMPLETE` | `INCOMPLETE` | `INVALID` | `BLOCKED` | `ARCHIVE_AGGREGATE`.  
`--strict` exits nonzero when Direct dirs are incomplete/invalid or required baselines are blocked. Missing predictions are never replaced with fabricated metrics.

## Private prediction layout

Place verified dumps **outside** git (or under a local ignored path) with this layout:

```text
$PRED_ROOT/
  rschema_exp4_codellama13b/NNNN.{json,txt}
  rschema_exp4_llama31/
  rschema_exp4_deepseek/
  rschema_exp4_claude_sonnet_4_6/
  rschema_exp4_gpt_5_4_mini/
  schemabench_exp2_codellama13b/
  schemabench_exp2_llama31/
  schemabench_exp2_deepseek/
  schemabench_exp2_claude_sonnet_4_6/
  schemabench_exp2_gpt_5_4_mini/
  # optional PaperMethods trees / archive JSON (otherwise baselines report BLOCKED)
```

Default `$PRED_ROOT` is `results/predictions/e0/` (gitignored).

## Offline evaluation (no credentials)

```bash
pip install -r requirements.txt
python3 -m pytest -q

# Gold + metric-protocol checks only (no predictions required)
python3 experiments/E0/reproduce_genuine_tables.py --validate-only --skip-pytest

# Regenerate Tables V & VI from private predictions
python3 experiments/E0/reproduce_genuine_tables.py \
  --pred-root "$PRED_ROOT" \
  --write-gpm --skip-pytest --strict

# Helper (uses PRED_ROOT env or results/predictions/e0)
bash scripts/reproduce_e0_offline.sh
```

Outputs (local only, gitignored): `results/metrics/reproduced/E0_TABLE_{V,VI}_FINAL.*`

Without predictions, a full evaluate run reports incomplete/blocked coverage; `--strict` fails.

## Closed Direct inference (paid; opt-in)

```bash
pip install openai anthropic   # optional
export OPENAI_API_KEY=...      # or local openai_api.txt
export ANTHROPIC_API_KEY=...

python3 experiments/E0/run_direct_api.py --dry-run
python3 experiments/E0/run_direct_api.py --limit 1 --confirm-paid
```

Open-weight Direct / PaperMethods regeneration: see `original_benchmarks/`.  
SchemaAgent is **not** shipped. Do not substitute `prompt_conditions_v2`.

## Limitations

- Prediction dumps and numerical tables are **not** published in this repository.
- Table VI One-shot / CoT / Few-shot remain PARTIAL without recovered per-schema PaperMethods trees.
- Paid API and GPU inference are optional and separate from offline evaluation.
