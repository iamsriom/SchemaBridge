# E5 — Scalability and Cost

Executable SchemaBridge experiment answering E5-RQ1/RQ2/RQ3.

## Commands

```bash
cd /data/SchemaBridge
/data/Text2ER/.venv/bin/python -m experiments.e5.run --mode sample-only
/data/Text2ER/.venv/bin/python -m experiments.e5.run --mode pilot
/data/Text2ER/.venv/bin/python -m experiments.e5.run --mode full
/data/Text2ER/.venv/bin/python -m experiments.e5.run --mode full --enable-deepseek-local  # new DeepSeek gens
/data/Text2ER/.venv/bin/python -m experiments.e5.report
pytest -q experiments/e5/tests
```

Spend cap: `E5_MAX_SPEND_USD` (default `$25`).

## Outputs

- `outputs/sample_manifest.csv`
- `outputs/e5_raw_runs.csv`, `e5_per_schema.csv`, `e5_scalability.csv`, `e5_cost_fidelity.csv`, `e5_prompt_efficiency.csv`, `e5_failures.csv`
- `RESULTS.md`, `paper_e5.tex`
- `tables/*.tex`, `figures/*.{pdf,png}`
- `repository_audit.md`, `pricing.json`

## Credential status (this host)

- OpenAI key in `/data/openai_api.txt`: **401 invalid** → GPT-5.4-mini / GPT-4o-mini live calls N/A
- Anthropic: **missing** → Claude Sonnet 4.6 N/A
- DeepSeek-Coder-6.7B: local weights OK; E1/E2 basic archives reused for fidelity
