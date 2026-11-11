# Reproducing E1 (Schema2Text) and E2 (Schema2Text2Schema)

Complete, command-checked guide for the E1/E2 reproduction code in this repository.

**This repository ships CODE ONLY.** It does not contain experimental scores, prediction dumps,
reconstructed schemas, LaTeX tables with numbers, plots, or API caches. Everything you generate
locally must land under git-ignored paths (`experiments/E1/outputs/`, `experiments/E2/outputs/`,
`figures/generated/`, `**/latex_generated/`, `results/metrics/local/`, `/outputs/`).

Every command below matches the corresponding script’s `--help`.

---

## A. Requirements

| Resource | Guidance |
|---|---|
| OS | Linux or macOS recommended; CUDA Linux for open-weight GPU runs |
| Python | 3.10+ (3.11 tested for unit tests) |
| Core libs | `pyyaml`, `numpy`, `pytest` (`requirements.txt`) |
| E1 text metrics | `sacrebleu==2.6.0`, `rouge-score`, optional `bert-score==0.3.12` + `torch` |
| Open-weight inference | `transformers`, `accelerate`; optional `bitsandbytes` for `--load-in-4bit` |
| Paid APIs | `anthropic`, `openai`; keys only via env vars |
| GPU (open describers) | ~24+ GB VRAM preferred for CodeLlama-13B at fp16; 8B/6.7B fit on ~16 GB; 4-bit may reduce VRAM |
| Disk | Model weights (~10–25 GB each) + dataset DDL + local outputs |
| Network | Only when downloading HF checkpoints or calling paid APIs |

Checkpoints / API model ids:

| key | model id | role |
|---|---|---|
| `codellama13b` | `codellama/CodeLlama-13b-Instruct-hf` | E1 describer |
| `llama31` | `meta-llama/Meta-Llama-3.1-8B-Instruct` | E1 describer (gated) |
| `deepseek` | `deepseek-ai/deepseek-coder-6.7b-instruct` | E1 describer |
| `sonnet46` | `claude-sonnet-4-6` | E1 describer (paid) |
| `gpt54mini` | `gpt-5.4-mini` | E1 describer (paid) |
| `gpt4omini` | `gpt-4o-mini` | E2 constructor (paid) |

Decoding defaults: temperature **0.2**; max tokens 3072 (HF), 1024/2048 (API basic/detailed), 16384 (constructor).

## B. Installation

```bash
git clone https://github.com/iamsriom/SchemaBridge.git
cd SchemaBridge
git checkout research/e1-e2-reproduction-code   # or the merged main once accepted

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install sacrebleu==2.6.0 rouge-score matplotlib
# optional:
pip install bert-score==0.3.12 torch            # BERTScore
pip install transformers accelerate             # open-weight --execute
pip install anthropic openai                    # paid --execute --confirm-paid

python -c "from src.prompt_assets import verify_all_prompts; print(verify_all_prompts())"
pytest -q tests/test_e1_prompts.py tests/test_e1_datasets.py tests/test_e2_structural_repro.py
```

Nothing beyond the standard library is required for `--help`, dry-runs, dataset preparation, SCR, or structural F1/nGED.

## C. Dataset acquisition

Packaged copies used by the offline loaders live under `datasets/`:

| Dataset | Packaged path | N (PRIMARY) | Notes |
|---|---|---|---|
| Enterprise-145 | `datasets/enterprise145/schema/` | **145** | DDL + `index.json`; **no** gold NL → BLEU/ROUGE/BERTScore N/A |
| RSchema | `datasets/rschema/annotation.jsonl` + `annotation_ddl.jsonl` | **381** of 518 | genuine DDL ∩ logical IDs |
| SchemaBench | `datasets/schemabench/annotation_ddl.jsonl` | **239** | gold NL = `question` |

Upstream / licensing: follow each dataset’s original distribution terms. RSchema and SchemaBench
annotations packaged here are the research dumps used by SchemaBridge; Enterprise-145 SQL schemas
are under `datasets/enterprise145/schema/`. If you maintain a server-style layout, point
`--data-root` / `SCHEMABRIDGE_DATA_ROOT` at a root containing `RSchema/`, `SchemaBench/Dataset/`,
and `Text2ER/schema/` — the loaders accept either layout.

Do **not** assume every corpus is redistributable under every license; check your institutional
agreement before republishing raw gold data outside this package’s existing `datasets/` tree.

## D. Dataset preparation

RSchema has **518** logical annotations (`annotation.jsonl`) but only **381** have genuine DDL in
`annotation_ddl.jsonl` (matched by `id`). The remaining 137 would require synthetic
all-`varchar(255)` DDL and are excluded from the verified E1/E2 PRIMARY population. Serials
(`NNNN`) are 1-based positions in the 518-record file (not contiguous 1..381). Never use
“first 381 of 518” truncation.

```bash
python experiments/E1/prepare_dataset.py --out-dir experiments/E1/outputs/datasets
python experiments/E1/prepare_dataset.py --no-write   # validate + print only
```

Writes `RSCHEMA_381_ELIGIBLE.csv` with `schema_id,serial_in_518,eval_index,database` (metadata only).

Expected counts: Enterprise-145=145, SchemaBench=239, RSchema PRIMARY=381, RSchema logical=518.

## E. Run E1 inference

**Paid API methods are disabled** in this package (Claude / GPT-5.4-mini describers and the GPT-4o-mini constructor cannot be executed). Dry-run still sizes requests. Live generation is open-weight HF only; evaluate saved predictions offline.


Dry-run is the default (no model load, no API call):

```bash
python experiments/E1/run.py --dataset rschema --model llama31 --prompt detailed
python experiments/E1/run.py --dataset rschema --model llama31 --prompt detailed \
  --write-plan --out-dir experiments/E1/outputs/plan
```

Open-weight generation (GPU; explicit `--execute`):

```bash
python experiments/E1/run.py --dataset enterprise145 --model codellama13b --prompt basic --execute
python experiments/E1/run.py --dataset enterprise145 --model codellama13b --prompt detailed --execute
python experiments/E1/run.py --dataset rschema --model llama31 --prompt basic --execute
python experiments/E1/run.py --dataset rschema --model llama31 --prompt detailed --execute
python experiments/E1/run.py --dataset schemabench --model deepseek --prompt basic --execute
python experiments/E1/run.py --dataset schemabench --model deepseek --prompt detailed --execute
```

Paid APIs (`sonnet46` / `gpt54mini`) **cannot be executed** from this package; `--execute` is refused even with `--confirm-paid`. Dry-run still works for request sizing.


Useful flags: `--limit N`, `--skip-existing` / `--no-skip-existing` / `--resume`, `--device`, `--dtype`,
`--load-in-4bit`, `--max-tokens`, `--max-retries`, `--retry-base-delay`, `--data-root`, `--out-dir`.
Default outputs: `experiments/E1/outputs/<dataset>_<prompt>_<model>/NNNN.{txt,json}`.

Prompt styles in JSON: basic → `schema2text1`, detailed → `schema2text2`. Prompt SHA-256 is verified
on every run (`basic=e1422bc8…`, `detailed=f09fc8ca…622d`).

## F. Run E1 evaluation

```bash
python experiments/E1/evaluate.py --dataset rschema --model llama31 --prompt detailed \
  --pred-dir experiments/E1/outputs/rschema_detailed_llama31 --skip-bertscore

python experiments/E1/evaluate.py --dataset all --model all --prompt all \
  --pred-dir experiments/E1/outputs --device cuda:0
```

Metrics:

- **BLEU-4**: `sacrebleu.corpus_bleu(hyps, [refs])` — correct single reference-stream layout
- **ROUGE-L**: mean F1 with stemming
- **BERTScore-F1**: `roberta-large`, `idf=False`, `rescale_with_baseline=False`
- **SCR**: macro-averaged schema coverage over gold DDL identifiers

Enterprise-145: SCR only (no gold NL). Failures under `--fail-policy score` (default) contribute empty
hypotheses; `skip` drops them. Writes `metrics.json`, `per_record.csv`, `e1_summary.csv` under
`--out-dir` (default `experiments/E1/outputs/metrics/`). **Do not commit those files.**

## G. Run E2 reconstruction

**Live GPT-4o-mini constructor API calls are disabled.** Use dry-run to validate payloads, or evaluate already-saved reconstructions with `experiments/E2/evaluate.py`.


```bash
# dry-run: validate constructor payloads from E1 descriptions (no API)
python experiments/E2/run.py --dataset rschema --describer-model llama31 --prompt detailed \
  --e1-pred-dir experiments/E1/outputs/rschema_detailed_llama31

# live constructor API is disabled; evaluate saved reconstructions offline instead
# python experiments/E2/evaluate.py --dataset rschema --describer-model llama31 --prompt detailed \
#   --pred-dir experiments/E2/outputs/rschema_detailed_llama31
```

Supports `--skip-existing`, `--limit` in dry-run. Live constructor execution is disabled.
Missing/invalid E1 descriptions become error records without calling the API. Outputs:
`experiments/E2/outputs/<dataset>_<prompt>_<describer>/NNNN.{json,txt}` with `ddl` + `metadata`.

You can also evaluate already-saved reconstructions without any API call (section H).

## H. Run E2 evaluation

```bash
python experiments/E2/evaluate.py --dataset rschema --describer-model llama31 --prompt detailed \
  --pred-dir experiments/E2/outputs/rschema_detailed_llama31 --fail-policy score
```

PRIMARY gold = genuine DDL (RSchema **381**, not synthetic 518). Metrics: micro-F1 for Tables,
Attributes, Domain, Entity, Referential + mean nGED. Failed/unparseable predictions under `score`:
gold counts kept, recreated=matched=0 ⇒ F1 loss; **nGED = 1**. Outputs under
`experiments/E2/outputs/metrics/` (git-ignored).

## I. Generate publication tables locally

```bash
python experiments/E1/generate_table_vii.py --metrics-dir experiments/E1/outputs/metrics
python experiments/E2/generate_table_viii.py --metrics-dir experiments/E2/outputs/metrics
python scripts/generate_e1_e2_tables.py \
  --e1-metrics-dir experiments/E1/outputs/metrics \
  --e2-metrics-dir experiments/E2/outputs/metrics \
  --out-dir experiments/E1/outputs/latex_generated
```

Generators contain **no baked-in scores**. Missing cells render as `--`; Enterprise text metrics as `N/A`.
**Do not commit** generated `.tex` tables.

## J. Generate figures locally

```bash
python scripts/plot_e1_e2_figures.py \
  --e1-csv experiments/E1/outputs/metrics/e1_summary.csv \
  --e2-csv experiments/E2/outputs/metrics/e2_summary.csv \
  --out-dir figures/generated

python scripts/plot_e1_e2_figures.py --synthetic --out-dir figures/generated
```

Produces SCR–F1 scatter plots with Pearson \(r\), two-sided p-value labels (`***/**/*/n.s.`), and
least-squares regression lines. **Publish plotting source only; do not commit plots.**

## K. Verify reproduction

```bash
# prompt hashes
python -c "from src.prompt_assets import verify_all_prompts; print(verify_all_prompts())"

# dataset sizes + 381 derivation
python experiments/E1/prepare_dataset.py --no-write

# dry-runs (no network / no paid calls)
python experiments/E1/run.py --dataset all --model all --prompt basic --limit 1
python experiments/E2/run.py --dataset all --describer-model all --prompt basic --limit 1

# methodology unit tests (synthetic fixtures only)
pytest -q tests/test_e1_nl_metrics.py tests/test_e1_prompts.py tests/test_e1_datasets.py \
  tests/test_e2_structural_repro.py tests/test_e1_e2_cli_dryrun.py tests/test_plot_pearson.py
```

Checks covered by tests: BLEU reference layout, ROUGE/SCR, prompt selection + hashes, schema-ID
alignment, missing gold NL for Enterprise, resume/skip logic (dry), SQL parser, type/nullability,
composite PK/UNIQUE, directed FKs, micro-F1, nGED failure=1, population filtering, Pearson/regression,
CLI `--help` / dry-run flags vs this document.

Ordinary unit tests do **not** require proprietary prediction corpora.

## L. Troubleshooting

| Symptom | Fix |
|---|---|
| CUDA OOM | reduce batch/limit; `--dtype float16`; try `--load-in-4bit`; use a larger GPU |
| Missing HF model / gated Llama | `huggingface-cli login`; ensure disk space under HF cache |
| Missing API credentials | `export OPENAI_API_KEY=...` / `ANTHROPIC_API_KEY=...` (env only) |
| Rate limits / 429 | raise `--max-retries` / `--retry-base-delay`; re-run (skip-existing keeps finished IDs) |
| Interrupted run | re-run with default `--skip-existing` |
| Invalid / empty DDL reconstructions | scored as failures (nGED=1) under `--fail-policy score` |
| Missing gold NL (Enterprise) | expected — only SCR is defined |
| Schema alignment errors | ensure prediction `id` matches gold; use serial `NNNN` files from the same population |
| BERTScore cache / download | set `HF_HOME`; or pass `--skip-bertscore` |
| `PromptHashError` | restore `prompts/describer_*.txt` / `constructor.txt`; do not edit pinned hashes |
| Wrong BLEU | use `corpus_bleu(hyps, [refs])` — never `[[r] for r in refs]` |
| Refusing to write outputs | put `--out-dir` under `outputs/`, `figures/generated/`, `latex_generated/`, or outside the repo |
| Dependency conflicts | use a fresh `.venv`; pin `sacrebleu==2.6.0`, `bert-score==0.3.12` |

---

### Library map

| Path | Role |
|---|---|
| `experiments/E1/run.py` | Schema2Text generation |
| `experiments/E1/evaluate.py` | BLEU / ROUGE / BERTScore / SCR |
| `experiments/E1/prepare_dataset.py` | counts + 381 eligibility CSV |
| `experiments/E1/generate_table_vii.py` | local Table VII LaTeX |
| `experiments/E2/run.py` | GPT-4o-mini constructor |
| `experiments/E2/evaluate.py` | 5-dim micro-F1 + nGED |
| `experiments/E2/generate_table_viii.py` | local Table VIII LaTeX |
| `src/nl_metrics.py` | text metrics |
| `src/evaluator.py` / `src/metrics.py` | structural metrics |
| `src/schema_parser.py` / `src/normalization.py` | DDL parse + name norm |
| `src/prompt_assets.py` / `src/inference_clients.py` | prompts + clients |
| `scripts/plot_e1_e2_figures.py` | SCR–F1 figures |
| `prompts/describer_basic.txt` / `describer_detailed.txt` / `constructor.txt` | verified prompts |
