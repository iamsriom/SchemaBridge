# E1 — Schema2Text (Schema verbalization)

Paper table: Table VII (`tab:e1_s2t`).

This directory contains the **verified open-weight Detailed (Prompt B)** reproduction
pipeline for SchemaBridge E1. It generates schema verbalizations and evaluates them
with BLEU-4, ROUGE-L, BERTScore-F1, and Schema Coverage Rate (SCR).

> Generated predictions, metrics, LaTeX tables, and audit logs are **local artifacts**.
> They are gitignored and are not published with this repository.

## A. Experiment overview

| Item | Specification |
|------|----------------|
| Task | Schema2Text: DDL schema → single-paragraph natural-language description |
| Datasets | **RSchema**: 381 genuine DDL schemata (synthetic DDL excluded); **SchemaBench**: 239 DDL schemata |
| Models | `codellama/CodeLlama-13b-Instruct-hf`, `meta-llama/Meta-Llama-3.1-8B-Instruct`, `deepseek-ai/deepseek-coder-6.7b-instruct` |
| Prompt | Detailed **Prompt B** stored in `prompts/describer_basic.txt` (filename is historical; content is the exhaustive single-paragraph prompt) |
| Prompt SHA256 (strip) | `f09fc8cae8d8ec73deb79f8bc7c2e71842d5fd35e92d833a02954b539755622d` |
| Metrics | Corpus BLEU-4, mean ROUGE-L F1, mean BERTScore-F1 (`roberta-large`), macro SCR |
| Decoding | temperature `0.2`, top_p `1.0`, max_new_tokens up to `3072` (subject to memory-safe caps) |

Do **not** use `prompts/describer_detailed.txt` for this configuration; that file holds an unrelated five-section prompt.

## B. Installation

```bash
git clone https://github.com/iamsriom/SchemaBridge.git
cd SchemaBridge

python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip

# Full GPU reproduction stack (install a CUDA-matched torch wheel for your platform first if needed)
pip install -r experiments/E1/requirements-e1.txt

# CPU unit / smoke tests only:
# pip install -r experiments/E1/requirements-e1-ci.txt
```

**Python:** 3.10 recommended (CI uses 3.10).  
**CUDA:** a recent NVIDIA driver with a matching PyTorch CUDA build. The verified run used CUDA 13.0 / PyTorch `2.12.0+cu130`.

Validated metric library versions:

- `sacrebleu==2.6.0`
- `rouge-score==0.1.2`
- `bert-score==0.3.12`

## C. Dataset preparation

Bundled under the repository (relative to repo root):

```text
datasets/rschema/annotation.jsonl          # 518 NL + logical schemas (gold NL)
datasets/rschema/annotation_ddl.jsonl      # 381 genuine DDL records
datasets/schemabench/annotation_ddl.jsonl  # 239 DDL + gold NL
```

**RSchema 381 selection:** keep only annotation IDs that also appear in
`annotation_ddl.jsonl` with a non-empty DDL string. The remaining logical-only
records (structured-synthetic DDL stand-ins) are **excluded**. Ordering follows
`annotation.jsonl`; evaluation indices are `1..381` over the genuine subset.

**SchemaBench 239:** load every record from `annotation_ddl.jsonl` in file order
(`eval_index = 1..239`). Do not drop historically OOM-hard schemata.

Optional: set `SCHEMABRIDGE_DATA_ROOT` to a directory that also contains legacy
Exp4 archives if you want provenance-matched **reuse** of prior predictions:

```text
$SCHEMABRIDGE_DATA_ROOT/RSchema_ExpResults4/Experiment2/schema2text_{codellama13b,llama31,deepseek}/
$SCHEMABRIDGE_DATA_ROOT/SchemaBench/Experiment/schema2text_{codellama13b,llama31,deepseek}/
```

Reuse requires matching `schema_id`, model id, DDL hash, and Prompt B hash, plus a
valid non-error NL string. Otherwise the runner regenerates.

Respect upstream dataset licenses. Do not redistribute restricted corpora beyond
what this repository already ships.

## D. Model setup

Exact Hugging Face checkpoints:

| Key | Checkpoint |
|-----|------------|
| `codellama13b` | `codellama/CodeLlama-13b-Instruct-hf` |
| `llama31` | `meta-llama/Meta-Llama-3.1-8B-Instruct` |
| `deepseek` | `deepseek-ai/deepseek-coder-6.7b-instruct` |

Llama-3.1 is gated. Authenticate without committing tokens:

```bash
export HF_TOKEN=...                 # or: huggingface-cli login
# optional local file (gitignored): ./huggingface_api.txt
```

Models download into the Hugging Face cache (`HF_HOME` / default `~/.cache/huggingface`).

## E. Running the experiment

All commands are run from the **repository root**.

### Plan / resume inspection (no generation)

```bash
python experiments/E1/run_e1_corrected_gpu.py --dataset all --model all --dry-run
```

### Optional reuse from local Exp4 archives

```bash
export SCHEMABRIDGE_DATA_ROOT=/path/to/archives   # optional
python experiments/E1/run_e1_corrected_gpu.py --dataset all --model all --reuse-only
```

### Generate missing predictions (resumable; skips valid outputs)

```bash
# Single model / dataset on selected GPUs
CUDA_VISIBLE_DEVICES=0,1 python experiments/E1/run_e1_corrected_gpu.py \
  --dataset SchemaBench --model codellama13b --generate

CUDA_VISIBLE_DEVICES=2,3 python experiments/E1/run_e1_corrected_gpu.py \
  --dataset SchemaBench --model llama31 --generate

CUDA_VISIBLE_DEVICES=4,5 python experiments/E1/run_e1_corrected_gpu.py \
  --dataset SchemaBench --model deepseek --generate
```

Full RSchema + SchemaBench for one model:

```bash
CUDA_VISIBLE_DEVICES=0,1 python experiments/E1/run_e1_corrected_gpu.py \
  --dataset all --model llama31 --generate
```

Debug with a small slice (does **not** change the full-population protocol; for tooling only):

```bash
python experiments/E1/run_e1_corrected_gpu.py --dataset RSchema --model deepseek --limit 2 --dry-run
```

### NF4 OOM recovery (documented fallback)

If FP16 generation still OOMs on long schemata:

```bash
CUDA_VISIBLE_DEVICES=0,1 python experiments/E1/recover_oom_4bit.py \
  --dataset SchemaBench --model codellama13b
```

This loads the **same checkpoint** in BitsAndBytes NF4, keeps Prompt B / temperature /
top_p, and records `quantization=4bit_nf4_recovery` in prediction metadata.

### Multi-GPU helper script

```bash
# Optional; adjust CL_GPUS / LL_GPUS / DS_GPUS for your machine
chmod +x experiments/E1/launch_e1_corrected_screen.sh
CL_GPUS=0,1 LL_GPUS=2,3 DS_GPUS=4,5 ./experiments/E1/launch_e1_corrected_screen.sh
```

### Evaluate local predictions

```bash
# Full metrics including BERTScore (GPU recommended)
python experiments/E1/evaluate_e1_corrected.py --bertscore-device cuda:0

# Skip BERTScore
python experiments/E1/evaluate_e1_corrected.py --skip-bertscore
```

Primary evaluation uses fixed denominators **N=381** (RSchema) and **N=239**
(SchemaBench). Failed generations are kept in the population as empty hypotheses.

## F. Metrics

| Metric | Configuration |
|--------|----------------|
| BLEU-4 | `sacrebleu.corpus_bleu(hyps, [refs]).score` — documented single-reference layout (**not** `[[r] for r in refs]`) |
| ROUGE-L | `RougeScorer(["rougeL"], use_stemmer=True)`; mean per-record F1 |
| BERTScore-F1 | `bert_score.score(..., lang="en")` → `roberta-large`; mean F1; empty hyps assigned `0` without encoding |
| SCR | Macro-mean schema-identifier coverage of the hypothesis only; empty hyp → `0` when the schema has identifiers |

Empty / failed predictions remain aligned with their gold references for corpus BLEU.

Core implementations live in `reproduce_table_vii.py` (`compute_bleu`, `compute_rougeL`,
`compute_bertscore`, `schema_coverage_rate`) and are used by `evaluate_e1_corrected.py`.

## G. Outputs (local only; not in Git)

```text
results/predictions/e1_corrected/
  rschema381_detailed_{codellama13b,llama31,deepseek}/
  schemabench239_detailed_{codellama13b,llama31,deepseek}/
results/metrics/reproduced/
  E1_RSCHEMA381_DETAILED.csv
  E1_SCHEMABENCH239_DETAILED.csv
  E1_DETAILED_FULL_POPULATION.tex
  E1_TABLE_VII_CORRECTED.tex
audit/e1_verification/full_gpu_run/
  GPU_INVENTORY.json  INFERENCE_CONFIG.json  PREDICTION_COVERAGE.csv  ...
```

Each prediction JSON records `schema_id`, `model_id`, `prompt_hash`, `source_ddl_hash`,
`generation_status`, settings, device, and errors. Runs are resumable: valid files are
not overwritten.

## H. Hardware notes

The verified execution used **six NVIDIA Tesla T4 GPUs** (~15 GiB each):

- FP16 load with `device_map="auto"` and ~13 GiB per visible GPU
- One model job per 2-GPU shard in the reference launcher
- Memory-safe total sequence budgets: CodeLlama `6144`; Llama / DeepSeek `7168`
- `min_new_tokens=512`; OOM retries shrink the budget; NF4 recovery for residual OOMs

The code does **not** require six GPUs. Any number of visible devices works via
`CUDA_VISIBLE_DEVICES` and `device_map="auto"`. A single 16 GB-class GPU can run
8B/6.7B models with the memory-safe caps; 13B often needs multi-GPU or NF4.

## Tests

```bash
# CPU CI / smoke
pip install -r experiments/E1/requirements-e1-ci.txt
python -m pytest -q experiments/E1/test_e1_smoke.py experiments/E1/test_e1_corrected.py experiments/E1/test_reproduce_table_vii.py
```

Synthetic fixtures for smoke tests: `experiments/E1/fixtures/synthetic/` (not experimental results).

## Scripts

| Script | Role |
|--------|------|
| `run_e1_corrected_gpu.py` | Population builders, reuse, FP16 generation, resume |
| `recover_oom_4bit.py` | Documented NF4 recovery pass |
| `evaluate_e1_corrected.py` | Full-population + success-only metrics / TeX |
| `reproduce_table_vii.py` | Metric helpers + optional offline paper-archive auditor |
| `launch_e1_corrected_screen.sh` | Example multi-GPU orchestration |

## Status

Open-weight Detailed (Prompt B) on RSchema-381 and SchemaBench-239 is the supported
reproduction path. Basic prompt archives and proprietary / Enterprise cells are out of
scope for this runner unless you supply matching local predictions separately.
