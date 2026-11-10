# E0 — Text → Schema from gold NL (`tab:e0_overall`, `tab:e0_baselines`)

Canonical offline evaluator: `reproduce_genuine_tables.py` (also via `evaluate.py`).
Canonical closed Direct inference: `run_direct_api.py` (also via `run.py --online --confirm-paid`).

| | |
|---|---|
| Datasets | RSchema (518 logical; Domain on 381 matched DDL); SchemaBench (239 DDL) |
| Table V models | CodeLlama-13B, Llama-3.1-8B, DeepSeek-Coder-6.7B, Claude Sonnet 4.6, GPT-5.4-mini |
| Optional | GPT-4o-mini (`--include-gpt4o-mini`) |
| Direct preds | `results/predictions/e0/rschema_exp4_*`, `schemabench_exp2_*` |
| Baseline preds | `results/predictions/e0/{rschema,schemabench}_papermethods` |
| Constructor prompt | [`prompts/constructor.txt`](../../prompts/constructor.txt) |

## Protocol (FINAL)

| Metric | Definition |
|---|---|
| Structural F1 (T/A/E/R) | Micro-averaged; RSchema vs 518 logical; SchemaBench vs 239 DDL |
| Domain F1 | Micro over typed gold columns with known nullability; RSchema 381 DDL IDs; SchemaBench 239. Baselines: `--` |
| Hallucination | \(H=\frac14\sum_{d\in\{T,A,E,R\}}\max(0,P_d-M_d)/P_d\) micro; Domain excluded |
| nGED | Structural `names_only=True` (no type/nullability in labels) |
| Nullability | MySQL dialect; bare → YES; NOT NULL / inline PK → NO |
| Failures | Empty prediction kept in population; nGED=1; Hall not forced to 1 |
| Parser | `legacy=False` |

Never substitute `configs/paper_reference_values.json` for missing prediction files.

## Offline evaluation (no credentials)

```bash
pip install -r requirements.txt
python3 -m pytest -q
python3 experiments/E0/evaluate.py
# equivalent:
python3 experiments/E0/reproduce_genuine_tables.py
python3 experiments/E0/reproduce_genuine_tables.py --validate-only
python3 experiments/E0/reproduce_genuine_tables.py --dataset rschema
python3 experiments/E0/reproduce_genuine_tables.py --model 'CodeLlama-13B' --skip-pytest
python3 experiments/E0/reproduce_genuine_tables.py --write-gpm --no-render
python3 experiments/E0/reproduce_genuine_tables.py --strict   # exit 2 if Direct dirs incomplete
python3 experiments/E0/reproduce_genuine_tables.py --include-gpt4o-mini   # optional
```

Outputs (local, gitignored): `results/metrics/reproduced/E0_TABLE_{V,VI}_FINAL.*`

## Closed Direct inference (paid; opt-in)

Keys (never commit): `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`, or local `/data/openai_api.txt` and `/data/anthropic.txt`.

Optional deps: `pip install openai anthropic`

```bash
python3 experiments/E0/run_direct_api.py --help
python3 experiments/E0/run_direct_api.py --dry-run

# Smoke (1 record × default models × both datasets)
python3 experiments/E0/run_direct_api.py --limit 1 --confirm-paid

# Per model / dataset
python3 experiments/E0/run_direct_api.py --dataset rschema --llm claude_sonnet_4_6 --confirm-paid
python3 experiments/E0/run_direct_api.py --dataset rschema --llm gpt_5_4_mini --confirm-paid
python3 experiments/E0/run_direct_api.py --dataset schemabench --llm claude_sonnet_4_6 --confirm-paid
python3 experiments/E0/run_direct_api.py --dataset schemabench --llm gpt_5_4_mini --confirm-paid

# Resume-safe (skips valid NNNN.json + NNNN.txt)
python3 experiments/E0/run_direct_api.py --confirm-paid
```

Wrapper:

```bash
python3 experiments/E0/run.py
python3 experiments/E0/run.py --online --confirm-paid --limit 1
```

Prediction layout matches open-weight dumps: `NNNN.txt` (DDL) + `NNNN.json` with
`text_number`, `id`, `llm`, `model_id`, `database`, `question`, `ddl`, `metadata`.

## Open-weight Direct / prompting baselines

Open-weight Direct dumps under `results/predictions/e0/rschema_exp4_*` and
`schemabench_exp2_*` were produced with the original Exp4 HF runners (local GPU).
PaperMethods one-shot / one-shot+CoT / few-shot dumps live under
`results/predictions/e0/{rschema,schemabench}_papermethods/` (logical/untyped → Domain `--`).

Regenerating open-weight models from scratch requires those external scripts and
GPU weights; this package evaluates their saved predictions offline.

## Limitations

- Closed Direct API runs incur provider cost and need network + credentials.
- Incomplete closed prediction directories are reported as incomplete (dirs skipped), not filled from manuscript aggregates.
- E1–E5 are unchanged by this E0 package update.
