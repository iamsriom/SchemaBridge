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

* Dry-run is the default. Generation is opt-in: `--execute`; paid Anthropic/OpenAI models (E1 `sonnet46` /
  `gpt54mini`, E2 constructor `gpt4omini`) work with `--execute --confirm-paid` (both required). Keys come from
  `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` in the environment only (no keys in the repository). Paid calls are
  billed per token by the provider; start with `--limit 1`.
* E2 verifies strict E1 provenance (describer `llm` / `model_id`, `prompt_style`, prompt sha256, unique ids,
  one prompt style per directory; `--allow-legacy-e1` only tolerates missing fields).
* E2 empty schemas: an explicit empty reconstruction is valid; per-schema statuses are `ok`, `valid_empty`,
  `incorrect_empty`, `scored_failure`, `skipped` (a missing file is never a valid empty schema).
* RSchema population = 381 DDL-matched schemas (serials = positions in the 518-record file).
* Prompts are hash-verified (`src/prompt_assets.py`): basic `e1422bc8...6c20`, detailed `f09fc8ca...622d`,
  constructor `392a396f...84ad4`.
* BLEU uses `corpus_bleu(hyps, [refs])`; the old `[[r] for r in refs]` layout was a bug.
* All generated predictions, metrics, tables and figures are git-ignored (`experiments/E*/outputs/`,
  `figures/generated/`, `results/metrics/local/`, `**/latex_generated/`, `**/api_cache/`).
* Tests: `pytest -q tests/test_e1_*.py tests/test_e2_*.py tests/test_inference_clients_mocked.py tests/test_plot_pearson.py`
  (synthetic, offline; SDKs are mocked, no keys or network). CI: `.github/workflows/e1-e2-reproduction-tests.yml`.
