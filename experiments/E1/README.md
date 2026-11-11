# E1 - Schema -> Text (Table VII, `tab:e1_s2t`)

**Paper table label:** `tab:e1_s2t`

| | |
|---|---|
| Datasets | Enterprise-145 (N=145, SCR only); SchemaBench (N=239); RSchema (N=381 DDL-matched of 518 logical) |
| Models | open: CodeLlama-13B (`codellama13b`), Llama-3.1-8B (`llama31`), DeepSeek-Coder-6.7B (`deepseek`); paid APIs: Claude Sonnet 4.6 (`sonnet46`), GPT-5.4-mini (`gpt54mini`) |
| Prompts | `basic` = `prompts/describer_basic.txt` (`schema2text1`), `detailed` = `prompts/describer_detailed.txt` (`schema2text2`) |
| Metrics | BLEU-4 (0-100, sacrebleu `corpus_bleu(hyps, [refs])`), ROUGE-L, BERTScore-F1 (roberta-large), SCR (macro) |

Prompt SHA-256 (verified on every load by `src/prompt_assets.py`):

| prompt | sha256 |
|---|---|
| basic | `e1422bc806119c375d89e44759feee44f13eb2717335154ad3c9ca933b6e6c20` |
| detailed | `f09fc8cae8d8ec73deb79f8bc7c2e71842d5fd35e92d833a02954b539755622d` |
| constructor (E2) | `392a396f7073bc015d206460055f7e3b8a3c94a21ed09c059bc47c13d3884ad4` |

> The describer prompt files differ from earlier revisions of this repository. E3-E5 read the same
> files; they are not modified by the E1/E2 reproduction code.

## Modes

* **Offline (default)**: score existing `NNNN.json` descriptions (archived or locally generated).
* **Online (opt-in)**: `run.py --execute` generates descriptions. Open models run locally (GPU).
  `sonnet46` / `gpt54mini` are paid APIs and work with BOTH `--execute --confirm-paid` plus
  `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` in the environment (never read from files, printed or stored;
  no keys ship with this repository). Billing is per token by the provider: start with `--limit 1`;
  `--skip-existing` (default) never re-bills finished schemas. Without `--execute` everything is a free
  dry-run; `--execute` for a paid model without `--confirm-paid`, or without the key, exits with code 2
  before any request.
* Every record carries the provenance E2 verifies: `llm`, `model_id`, `prompt_style` and
  `generation.prompt_variant` / `prompt_sha256`.

All generated files go to git-ignored locations (`experiments/E1/outputs/`, or any path outside the repo).

## Commands

```bash
# 0. validate populations (145/239/381/518) and write RSCHEMA_381_ELIGIBLE.csv
python experiments/E1/prepare_dataset.py --out-dir experiments/E1/outputs/datasets

# 1. generation - dry-run (default), then execute
python experiments/E1/run.py --dataset rschema --model llama31 --prompt detailed
python experiments/E1/run.py --dataset rschema --model llama31 --prompt detailed --execute
python experiments/E1/run.py --dataset schemabench --model sonnet46 --prompt basic --execute --confirm-paid

# 2. offline evaluation
python experiments/E1/evaluate.py --dataset rschema --model llama31 --prompt detailed --skip-bertscore
python experiments/E1/evaluate.py --dataset all --model all --prompt all --pred-dir experiments/E1/outputs

# 3. LaTeX skeleton of Table VII from the local metrics
python experiments/E1/generate_table_vii.py --metrics-dir experiments/E1/outputs/metrics
```

`--dataset all` / `--model all` / `--prompt all` expand to every combination; `--out-dir` / `--pred-dir`
then name a *parent* directory containing one `<dataset>_<prompt>_<model>/` folder per combination.

Serials: RSchema file names `NNNN` are positions in the 518-record `annotation.jsonl`, so the 381
DDL-matched schemas are **not** numbered 0001..0381. Use `--limit N` for smoke tests.

Evaluation of archived artefacts against the paper's tolerance bands (legacy comparison harness):
`python scripts/reproduce_tables.py --experiment E1 --offline`.

See `docs/REPRODUCE_E1_E2.md` for the complete guide.
