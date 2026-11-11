# E1 Code Provenance Report (`tab:e1_s2t`)

**Audit date:** 2026-11-11  
**Scope:** Schema verbalization (Schema2Text), Basic (B) / Detailed (D)  
**Status:** Independently verified offline; publishable under `experiments/E1/`

## Pipeline (verified)

```
Gold schema (DDL)
  → Describer SYSTEM_PROMPT (schema2text1 = B | schema2text2 = D)
  → Generated NL (*.txt + *.json)
  → sanitize_nl_text + validate_nl_text
  → Metrics:
       BLEU-4  = sacrebleu.corpus_bleu(hyps, [refs])   # correct layout
       ROUGE-L = rouge_score RougeScorer(['rougeL'], use_stemmer=True).fmeasure mean
       BERTScore-F1 = bert_score.score(..., lang='en') → roberta-large, mean F1
       SCR = |{e ∈ Tables∪Columns : norm(e) occurs in norm(NL)}| / |E|
  → Macro / corpus aggregation → Table tab:e1_s2t
```

## Generation scripts and prompts

| Role | Path | Notes |
|---|---|---|
| Basic prompt (short summary) | Host: `Text2ER/experiments/schema2text1_allLLM.py` / `schema2text1_api.py` | `SYSTEM_PROMPT` = one short paragraph |
| Detailed prompt (exhaustive paragraph) | Host: `Text2ER/experiments/schema2text2_allLLM.py` / `schema2text2_api.py` | Exhaustive single-paragraph integrity coverage |
| RSchema Detailed open runner | Host: `Text2ER/RSchema_ExpResults4/Code/rschema_exp4_schema2text_allLLM.py` | Imports schema2text2 prompt; writes Experiment2 |
| Unused 5-section prompt | Host: `Text2ER/schema2text_detailed_pipeline.py` | **Not** used for Table VII |
| **Repo Basic (B)** | `prompts/describer_basic.txt` | schema2text1 short; SHA256(strip) `e1422bc806119c375d89e44759feee44f13eb2717335154ad3c9ca933b6e6c20` |
| **Repo Detailed (D)** | `prompts/describer_detailed.txt` | schema2text2 exhaustive; SHA256(strip) `f09fc8cae8d8ec73deb79f8bc7c2e71842d5fd35e92d833a02954b539755622d` |

> **Correction (2026-11-11):** earlier repo copies had Basic/Detailed swapped / used a 5-section Detailed stub. Published files above match the paper B/D SYSTEM_PROMPT texts.

## Authoritative prediction corpora (all 30 groups complete)

| Dataset | Prompt | Directory pattern | N files / model | Eval N |
|---|---|---|---:|---:|
| Enterprise-145 | B | `/data/LLMTranslations/Exp1/Schema2Text1_{llm}/` | 145 txt+json | 145 SCR-only |
| Enterprise-145 | D | `/data/LLMTranslations/Exp2/Schema2Text2_{llm}/` | 145 txt+json | 145 SCR-only |
| RSchema | B | `/data/RSchema_ExpResults4/Exp1/schema2text_{llm}/` | 518 | **381** |
| RSchema | D | `/data/RSchema_ExpResults4/Experiment2/schema2text_{llm}/` | 518 | **381** |
| SchemaBench | B | `/data/SchemaBench/Exp1/schema2text_{llm}/` | 239 | 239 |
| SchemaBench | D | `/data/SchemaBench/Experiment/schema2text_{llm}/` | 239 | 239 |

`llm ∈ {codellama13b, llama31, deepseek, sonnet46, gpt54mini}`.

### Do not use (stale / incomplete / wrong prompt)

| Path | Why |
|---|---|
| **`SchemaBridge/results/predictions/e1/schemabench_*`** | **Stale Detailed open run** (Experiment4 lineage); empty `nl_text` on 12–44 schemas; **never** use for `tab:e1_s2t` |
| `SchemaBridge/results/predictions/e1/rschema_*` | Open models only; Detailed (Experiment2) content; missing Basic + Claude/GPT |
| `RSchema_ExpResults3/schema2text_*` | Older “MANDATORY COVERAGE” prompt — not paper B/D |
| `LLMTranslations/Exp{1,2}/Schema2Text{1,2}_{codellama,mistral,GPT4omini}` | Extra models / pseudo-refs, not the five paper describers |
| `SchemaBench/Experiment4/` | Incomplete / OOM-truncated Detailed tree behind the stale `schemabench_*` dumps |

## Gold references

| Dataset | Gold NL | Gold DDL for SCR | Eval N |
|---|---|---|---:|
| Enterprise-145 | **none** (lexical metrics n/a) | Host `/data/Text2ER/schema/*.sql` (SCR only) | 145 |
| RSchema | `datasets/rschema/annotation.jsonl` field `question` | `datasets/rschema/annotation_ddl.jsonl` only | **381** |
| SchemaBench | `datasets/schemabench/annotation_ddl.jsonl` `question` | same file `answer` | 239 |

381 IDs = ID intersection of `annotation.jsonl` with `annotation_ddl.jsonl` (not positional truncation).

## Evaluators (published)

| Function / script | Path |
|---|---|
| Offline independent recompute | `audit/e1_independent_reproduce.py` |
| Wrapper | `experiments/E1/evaluate.py` → writes `experiments/E1/outputs/verified/` |
| Corrected GPU generate / evaluate | `experiments/E1/run_e1_corrected_gpu.py`, `evaluate_e1_corrected.py` |
| Metric helpers | `experiments/E1/reproduce_table_vii.py` (`compute_bleu` uses correct `[refs]` layout) |
| Historical NL evaluator (archive) | `third_party/evaluate_exp4_schema2text_nl.py` — contains the **buggy** `[[r] for r in refs]` layout |
| Verified numbers | `experiments/E1/outputs/verified/MANUSCRIPT_VALUES.json` |

## Historical BLEU bug

`ref_lists = [[r] for r in refs]; sacrebleu.corpus_bleu(hyps, ref_lists)` under SacreBLEU 2.6.0 effectively scores the first hypothesis only and **inflates** BLEU (e.g. 25.42 vs correct 7.63). Correct form: `sacrebleu.corpus_bleu(hyps, [refs])`.

## Model IDs (from prediction JSON `model_id`)

| Display | Checkpoint / API id |
|---|---|
| CodeLlama-13B | `codellama/CodeLlama-13b-Instruct-hf` |
| Llama-3.1-8B | `meta-llama/Meta-Llama-3.1-8B-Instruct` |
| DeepSeek-Coder | `deepseek-ai/deepseek-coder-6.7b-instruct` |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` |
| GPT-5.4-mini | `gpt-5.4-mini` |

## Data redistribution

Bundled `datasets/rschema/` and `datasets/schemabench/` JSONL are the evaluation gold used by this repo. Host prediction dumps under `/data/{RSchema_ExpResults4,SchemaBench,LLMTranslations}/` are **not** published (large, may contain model outputs under third-party terms). Reproduce metrics offline against local archives or regenerate open-weight Detailed cells with `run_e1_corrected_gpu.py`.
