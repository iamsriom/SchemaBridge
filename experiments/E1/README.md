# E1 — Schema2Text (Schema verbalization)

Paper table: Table VII (`tab:e1_s2t`).

Verified offline reproduction for **Basic (B)** and **Detailed (D)** across Enterprise-145,
RSchema-381, and SchemaBench-239. Metrics: corpus BLEU-4, ROUGE-L, BERTScore-F1, SCR.

Raw model prediction dumps, API secrets, and HF caches are **not** published.

## A. Experiment overview

| Item | Specification |
|------|----------------|
| Task | Schema2Text: DDL → single-paragraph natural-language description |
| Datasets | Enterprise-145 (SCR only); RSchema **381** DDL-matched; SchemaBench 239 |
| Models | CodeLlama-13B, Llama-3.1-8B, DeepSeek-Coder; Claude Sonnet 4.6; GPT-5.4-mini |
| Basic prompt | `prompts/describer_basic.txt` — short summary (schema2text1); SHA256(strip) `e1422bc8…` |
| Detailed prompt | `prompts/describer_detailed.txt` — exhaustive paragraph (schema2text2); SHA256(strip) `f09fc8ca…` |
| Metrics | Corpus BLEU-4, mean ROUGE-L F1, mean BERTScore-F1 (`roberta-large`), macro SCR |
| BLEU layout | `sacrebleu.corpus_bleu(hyps, [refs])` — **not** `[[r] for r in refs]` |

## B. Authoritative predictions (host archives)

| Dataset | Basic | Detailed |
|---------|-------|----------|
| Enterprise | `/data/LLMTranslations/Exp1/Schema2Text1_<llm>/` | `/data/LLMTranslations/Exp2/Schema2Text2_<llm>/` |
| RSchema | `/data/RSchema_ExpResults4/Exp1/schema2text_<llm>/` | `/data/RSchema_ExpResults4/Experiment2/schema2text_<llm>/` |
| SchemaBench | `/data/SchemaBench/Exp1/schema2text_<llm>/` | `/data/SchemaBench/Experiment/schema2text_<llm>/` |

**Never use** `results/predictions/e1/schemabench_*` (stale Experiment4 / empty NL).

## C. Installation

```bash
git clone https://github.com/iamsriom/SchemaBridge.git
cd SchemaBridge

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r experiments/E1/requirements-e1-ci.txt   # metrics + tests
# Full GPU stack (optional): pip install -r experiments/E1/requirements-e1.txt
```

Validated metric versions: `sacrebleu==2.6.0`, `rouge-score==0.1.2`, `bert-score==0.3.12`.

## D. Offline table recompute (preferred verification)

Point the auditor at host archives (defaults under `/data/...` as in `config.yaml`):

```bash
python experiments/E1/evaluate.py            # BLEU / ROUGE / SCR
# python experiments/E1/evaluate.py --bert   # + BERTScore (GPU recommended)
```

Writes `experiments/E1/outputs/verified/` (comparison CSV, coverage, TeX, manuscript JSON).

Locked verified numbers: `experiments/E1/outputs/verified/MANUSCRIPT_VALUES.json`.

## E. Open-weight Detailed regeneration (optional)

```bash
python experiments/E1/run_e1_corrected_gpu.py --dataset all --model all --dry-run
CUDA_VISIBLE_DEVICES=0,1 python experiments/E1/run_e1_corrected_gpu.py \
  --dataset SchemaBench --model llama31 --generate
python experiments/E1/evaluate_e1_corrected.py --bertscore-device cuda:0
```

NF4 OOM recovery: `recover_oom_4bit.py`. Multi-GPU helper: `launch_e1_corrected_screen.sh`.

## F. Metrics

| Metric | Configuration |
|--------|----------------|
| BLEU-4 | `sacrebleu.corpus_bleu(hyps, [refs]).score` |
| ROUGE-L | `RougeScorer(["rougeL"], use_stemmer=True)`; mean F1 |
| BERTScore-F1 | `bert_score.score(..., lang="en")` → `roberta-large`; mean F1 |
| SCR | Macro-mean identifier coverage; empty hyp → 0 |

Denominators: Enterprise **145**, RSchema **381**, SchemaBench **239**. Failed / empty generations stay in the population.

## G. Verified outputs (committed)

```text
experiments/E1/outputs/verified/
  MANUSCRIPT_VALUES.json
  E1_REPRODUCTION_COMPARISON.csv
  tab_e1_s2t_verified.tex
  e1_coverage.csv
  e1_comparison_correct_bleu.csv
```

## H. Tests

```bash
pip install -r experiments/E1/requirements-e1-ci.txt
python -m pytest -q \
  experiments/E1/test_e1_smoke.py \
  experiments/E1/test_e1_corrected.py \
  experiments/E1/test_reproduce_table_vii.py
```

## Provenance

See `audit/E1_CODE_PROVENANCE.md`, `audit/E1_AUDIT_VERDICT.md`, and `docs/experiments/E1.md`.
Respect upstream dataset licenses; do not redistribute restricted host prediction dumps.
