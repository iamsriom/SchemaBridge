# Reproducibility

```bash
pip install -r requirements.txt
python scripts/reproduce_tables.py --all --offline
python scripts/reproduce_tables.py --experiment E0 --recompute
python scripts/offline_e1_rschema_detailed.py
pytest -q
```

## E1 / E2 reproduction code (code only; no results are shipped)

Full guide: [REPRODUCE_E1_E2.md](REPRODUCE_E1_E2.md).

```bash
python experiments/E1/prepare_dataset.py --out-dir experiments/E1/outputs/datasets   # 145 / 239 / 381 / 518
python experiments/E1/run.py --dataset rschema --model llama31 --prompt detailed      # dry-run (default)
python experiments/E1/evaluate.py --dataset rschema --model llama31 --prompt detailed --skip-bertscore
python experiments/E2/run.py --dataset rschema --describer-model llama31 --prompt detailed \
    --e1-pred-dir experiments/E1/outputs/rschema_detailed_llama31                     # dry-run (default)
python experiments/E2/evaluate.py --dataset rschema --describer-model llama31 --prompt detailed \
    --pred-dir experiments/E2/outputs/rschema_detailed_llama31
python scripts/generate_e1_e2_tables.py
python scripts/plot_e1_e2_figures.py --synthetic --out-dir figures/generated
```

* Generation is opt-in: `--execute` (and `--confirm-paid` for Anthropic/OpenAI models). Keys come from
  `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` only.
* RSchema population = 381 DDL-matched schemas (serials = positions in the 518-record file).
* Prompts are hash-verified (`src/prompt_assets.py`): basic `e1422bc8...6c20`, detailed `f09fc8ca...622d`,
  constructor `392a396f...84ad4`.
* BLEU uses `corpus_bleu(hyps, [refs])`; the old `[[r] for r in refs]` layout was a bug.
* All generated predictions, metrics, tables and figures are git-ignored (`experiments/E*/outputs/`,
  `figures/generated/`, `results/metrics/local/`, `**/latex_generated/`, `**/api_cache/`).
* Tests: `pytest -q tests/test_e1_*.py tests/test_e2_structural_repro.py tests/test_plot_pearson.py` (synthetic, offline).

## E3 constructor-isolation reproduction code (code only; no results are shipped)

Full guide: [REPRODUCE_E3.md](REPRODUCE_E3.md).

```bash
python experiments/E3/prepare_inputs.py --dataset rschema \
    --descriptions-dir experiments/E1/outputs/rschema_detailed_gpt54mini
python experiments/E3/run.py --dataset rschema --constructor llama31 \
    --descriptions-dir experiments/E1/outputs/rschema_detailed_gpt54mini              # dry-run
python experiments/E3/validate_inputs.py --dataset rschema \
    --descriptions-dir experiments/E1/outputs/rschema_detailed_gpt54mini \
    --pred-parent experiments/E3/outputs
python experiments/E3/evaluate.py --dataset rschema --constructor llama31 \
    --pred-dir experiments/E3/outputs/rschema_detailed_llama31
python experiments/E3/generate_table_ix.py --metrics-dir experiments/E3/outputs/metrics
```

* Fixed describer = GPT-5.4-mini Detailed; five constructors share identical `nl_text` hashes.
* Empty gold + empty reconstruction ⇒ nGED = 0; Hall. = mean of five micro `(R−M)/R` rates.
* Paid API constructor `--execute` is disabled; open-weight HF `--execute` is available.
* Tests: `pytest -q tests/test_e3_*.py` (synthetic, offline).
