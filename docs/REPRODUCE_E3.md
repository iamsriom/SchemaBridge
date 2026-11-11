# Reproducing E3 (Constructor Isolation — Table IX)

Complete, command-checked guide for the E3 reproduction code in this repository.

**This repository ships CODE ONLY.** It does not contain experimental scores, prediction dumps,
reconstructed schemas, LaTeX tables with numbers, plots, or API caches. Everything you generate
locally must land under git-ignored paths (`experiments/E3/outputs/`, `experiments/E1/outputs/`,
`figures/generated/`, `**/latex_generated/`, `results/metrics/local/`, `/outputs/`).

Every command below matches the corresponding script’s `--help`.

---

## A. Environment setup

| Resource | Guidance |
|---|---|
| OS | Linux or macOS; CUDA Linux for open-weight GPU constructors |
| Python | 3.10+ (3.11 tested for unit tests) |
| Core libs | `pyyaml`, `numpy`, `pytest` (`requirements.txt`) |
| Open-weight inference | `transformers`, `accelerate`; optional `bitsandbytes` for `--load-in-4bit` |
| Paid APIs | `anthropic`, `openai` (dry-run only in this package; execute disabled) |
| GPU | ~24+ GB VRAM preferred for CodeLlama-13B fp16; 8B/6.7B ~16 GB; 4-bit may reduce VRAM |
| Disk | Model weights (~10–25 GB each) + dataset DDL + local outputs |

```bash
git clone https://github.com/iamsriom/SchemaBridge.git
cd SchemaBridge
git checkout research/e3-constructor-reproducibility   # or main once merged

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install transformers accelerate   # open-weight --execute
# optional: pip install bitsandbytes anthropic openai

python -c "from src.prompt_assets import verify_all_prompts; print(verify_all_prompts())"
pytest -q tests/test_e3_*.py tests/test_e2_structural_repro.py tests/test_e1_prompts.py
```

Checkpoints / decoding (historical Exp4):

| key | model id | provider | T | max tokens |
|---|---|---|---:|---:|
| `codellama13b` | `codellama/CodeLlama-13b-Instruct-hf` | HF | 0.1 | 1536 |
| `llama31` | `meta-llama/Meta-Llama-3.1-8B-Instruct` | HF (gated) | 0.1 | 2048 |
| `deepseek` | `deepseek-ai/deepseek-coder-6.7b-instruct` | HF | 0.1 | 4096 |
| `sonnet46` | `claude-sonnet-4-6` | Anthropic (paid; execute disabled) | 0.1 | 4096 |
| `gpt54mini` | `gpt-5.4-mini` | OpenAI (paid; execute disabled) | 0.2† | 16384 |

† Enterprise Exp4 Batch used 0.2; some SchemaBench sync scripts used 0.1. Dated API snapshots were not archived — exact historical bit-identity is not claimed for closed models.

Constructor prompt SHA-256: `392a396f7073bc015d206460055f7e3b8a3c94a21ed09c059bc47c13d3884ad4`
Detailed describer SHA-256: `f09fc8cae8d8ec73deb79f8bc7c2e71842d5fd35e92d833a02954b539755622d`

## B. Dataset acquisition

Packaged loaders under `datasets/`:

| Dataset | Packaged path | N (PRIMARY) | Notes |
|---|---|---|---|
| Enterprise-145 | `datasets/enterprise145/schema/` | **145** | includes three empty-gold placeholders |
| RSchema | `datasets/rschema/annotation.jsonl` + `annotation_ddl.jsonl` | **381** of 518 | genuine DDL ∩ logical IDs |
| SchemaBench | `datasets/schemabench/annotation_ddl.jsonl` | **239** | |

Upstream / licensing: follow each dataset’s original distribution terms. Do not assume unrestricted
redistribution of raw gold outside this package’s existing `datasets/` tree. Server-style layout
via `--data-root` / `SCHEMABRIDGE_DATA_ROOT` is also accepted (see E1/E2 docs).

## C. Dataset preprocessing

```bash
python experiments/E1/prepare_dataset.py --out-dir experiments/E1/outputs/datasets
python experiments/E1/prepare_dataset.py --no-write   # validate + print only
```

RSchema PRIMARY = 381 genuine-DDL matches (serials = 1-based positions in the 518-record file).
Never use “first 381 of 518” truncation. Synthetic all-`varchar(255)` DDL is **not** PRIMARY gold.
Empty gold schemata (Enterprise `archive` / `ctu_vondreli` / `tmp`) are retained.

## D. Generate fixed GPT-5.4-mini Detailed descriptions

E3 reuses the verified E1 Detailed pipeline with `--model gpt54mini --prompt detailed`.

```bash
# Dry-run (default) — sizes payloads; paid execute is disabled in this package
python experiments/E1/run.py --dataset rschema --model gpt54mini --prompt detailed

# Inventory / completeness of a local description directory
python experiments/E3/prepare_inputs.py --dataset rschema \
    --descriptions-dir experiments/E1/outputs/rschema_detailed_gpt54mini \
    --write-manifest --out-dir experiments/E3/outputs/manifests
```

Place locally generated `NNNN.json` / `NNNN.txt` under
`experiments/E1/outputs/<dataset>_detailed_gpt54mini/`. Do **not** use Basic descriptions or
E2 GPT-4o-mini reconstructions as E3 inputs.

## E. Run each E3 constructor

```bash
# Dry-run (default)
python experiments/E3/run.py --dataset DATASET --constructor MODEL \
    --descriptions-dir LOCAL_DIR --out-dir LOCAL_OUT --dry-run

# Open-weight execute (CodeLlama / Llama-3.1 / DeepSeek)
python experiments/E3/run.py --dataset rschema --constructor llama31 \
    --descriptions-dir experiments/E1/outputs/rschema_detailed_gpt54mini \
    --execute --device auto --dtype float16
# optional: --load-in-4bit

# All open constructors, one dataset
python experiments/E3/run.py --dataset schemabench --constructor all \
    --descriptions-dir experiments/E1/outputs/schemabench_detailed_gpt54mini
```

Paid constructors (`sonnet46`, `gpt54mini`) refuse `--execute` here; dry-run still validates
payloads. Supply offline reconstructions to evaluate. Resume defaults to `--skip-existing`.
Successful originals are never overwritten; forced retries write `NNNN.retry.json` sidecars.

## F. Verify constructor isolation

```bash
python experiments/E3/validate_inputs.py --dataset rschema \
    --descriptions-dir experiments/E1/outputs/rschema_detailed_gpt54mini \
    --pred-parent experiments/E3/outputs
```

For each schema id, the SHA-256 of the fixed description must equal each constructor record’s
`nl_sha256` (or hashed `nl_text`). Mismatched ids or different description text abort with a
non-zero exit.

## G. Evaluate E3 (offline)

```bash
python experiments/E3/evaluate.py --dataset rschema --constructor llama31 \
    --pred-dir experiments/E3/outputs/rschema_detailed_llama31

python experiments/E3/evaluate.py --dataset all --constructor all \
    --pred-dir experiments/E3/outputs --fail-policy score
```

Required local inputs: gold via `datasets/` (or `--data-root`); reconstructions as `NNNN.json`
with `id`, `ddl`, optional `metadata` / `nl_text` / `nl_sha256`.

| Case | Policy (`--fail-policy score`) |
|---|---|
| Empty gold + empty reconstruction | valid; nGED = 0 |
| Nonempty gold + empty / malformed / missing | nGED = 1; recreations = 0 |
| Hallucination dim with Recreated = 0 | rate 0 for that dimension |
| Table Hall. | mean of five micro `(R−M)/R` rates (T/A/D/E/R) |

Outputs: `experiments/E3/outputs/metrics/<combo>/metrics.json`, `per_schema.csv`, `e3_summary.csv`.

## H. Generate Table IX locally

```bash
python experiments/E3/generate_table_ix.py --metrics-dir experiments/E3/outputs/metrics
# -> experiments/E3/outputs/latex_generated/table_ix.tex   (git-ignored; no baked-in scores)
```

## I. Validate reproduction

```bash
pytest -q tests/test_e3_structural.py tests/test_e3_cli_dryrun.py
python experiments/E3/prepare_inputs.py --dataset all --limit 1
python experiments/E3/run.py --dataset enterprise145 --constructor all --limit 1 --write-plan \
    --out-dir experiments/E3/outputs
python experiments/E3/validate_inputs.py --dataset enterprise145 --limit 1 \
    --descriptions-dir experiments/E1/outputs/enterprise145_detailed_gpt54mini \
    --pred-parent experiments/E3/outputs || true
python experiments/E3/generate_table_ix.py --metrics-dir experiments/E3/outputs/metrics
```

## J. Troubleshooting

| Symptom | What to check |
|---|---|
| Missing datasets | `experiments/E1/prepare_dataset.py`; `--data-root` / `SCHEMABRIDGE_DATA_ROOT` |
| Wrong HF snapshot | Use exact ids above; do not silently substitute another checkpoint |
| CUDA OOM | `--load-in-4bit`, smaller `--limit`, single constructor |
| Quantization failures | Install matching `bitsandbytes` + CUDA torch |
| API auth / rate limits | Paid execute disabled; offline evaluate only |
| Interrupted runs | `--skip-existing` / `--resume`; sidecars for retries |
| Invalid DDL | Parsed as failure → nGED=1 under `score` |
| Missing descriptions | `prepare_inputs.py` inventory; regenerate via E1 |
| Wrong schema joins | `validate_inputs.py` id + hash checks |
| Empty-schema handling | empty+empty is valid (nGED=0), not a failure |
| Hall. zero denominators | Recreated=0 → rate 0 (by design) |
| Dependency conflicts | fresh venv; pin `transformers`/`torch` to your CUDA stack |

## Distinctions

| Layer | What it means |
|---|---|
| Verified historical research implementation | Recovered Exp4 protocol + audited evaluator (empty-gold fix, 5-dim Hall.) |
| Public checkout tests | Synthetic unit/integration tests; dry-run CLIs; no paid inference |
| Full experimental reproduction | Needs datasets, HF weights and/or privately generated closed-model outputs |

Do not confuse E3 with `results/predictions/e3/rschema_cases_describer` (paper **E4** masking).
