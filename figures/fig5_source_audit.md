# Figure 5 — Source audit (proprietary E0 recovery)

Generated: 2026-10-28 (offline; no LLM inference)

## Verdict

**No per-schema E0 Text2Schema predictions for Claude Sonnet 4.6 or GPT-5.4-mini were found** anywhere in the project tree, experiment directories, caches, archives, SQLite stores, or agent stores searched for this audit.

Priority A (five-constructor Figure 5) is **impossible** from existing artifacts.

---

## Search scope

Searched under `/data`, `/data/Text2ER`, `/data/experiments`, `/data/Results`, `/data/RSchema*`, `/data/SchemaBench`, `/data/LLM4DBdesign*`, `/home/ubuntu/.cursor`, and `/run/user/1000/cursor_agent_stores` for:

- Filenames / dirs: `*claude*`, `*sonnet*`, `*gpt5*`, `*gpt-5*`, `*openai*`, `*anthropic*`
- Content: `Claude Sonnet 4.6`, `claude-sonnet-4`, `GPT-5.4-mini`, `gpt-5.4-mini`, `anthropic`
- Formats: `.json`, `.jsonl`, `.csv`, `.parquet`, `.sqlite`/`.db`, `.pkl`, `.zip`/`.tar*`, logs, manifests

## What exists (and what it is not)

| Path | Model | Task | Per-schema DDL from gold NL? | Usable for Fig 5 E0? |
|---|---|---|---|---|
| `/data/RSchema_ExpResults4/Experiments/text2schema_{codellama13b,llama31,deepseek}/` | Open-weight only | E0 Text2Schema (Exp4) | Yes (518×3) | Yes (open-weight) |
| `/data/SchemaBench/PaperMethods/{codellama13b,llama31,deepseek}/few_shot/results.json` | Open-weight only | E0 few-shot | Yes (239×3) | Yes (open-weight) |
| `/data/RSchema_Results/text2schema_gpt4omini/` (518 JSON) | **gpt-4o-mini** | E0-like Text2Schema | Yes | **No** — wrong model (not GPT-5.4-mini) |
| `/data/LLM4DBdesign_PaperMethods/gpt4omini/schema_agent/` | gpt4omini | Schema agent (mostly failed) | Partial / failed | **No** — wrong model + wrong method |
| `/data/RSchema_ExpResults4/Experiment2/text2schema_gpt4omini_schema2text_*` | gpt-4o-mini constructor | **E2** round-trip | N/A for E0 | **No** — E2, not E0 |
| `/data/SchemaBench/Experiment/text2schema_gpt4omini_schema2text_*` | gpt-4o-mini | **E2** | N/A | **No** |

Paper aggregates only (no per-schema files): Claude / GPT-5.4-mini rows in
`/data/LLM4DBdesign_PaperMethods/Results/paper_methods_vs_paper_tables_comparison.txt`
and the manuscript `\label{tab:e0_overall}` table.

## Candidate verification checklist (proprietary)

For Claude Sonnet 4.6 and GPT-5.4-mini:

| Check | Result |
|---|---|
| Belongs to E0 Text2Schema (not E2) | No files |
| Input = dataset original NL requirement | No files |
| Output = reconstructed DDL | No files |
| Predictions per schema | No files |
| Dataset + model identity recorded | No files |
| Schema IDs matchable to gold | No files |

**Coverage: 0 / 518 (RSchema) and 0 / 239 (SchemaBench) for both proprietary constructors.**

## Open-weight coverage (for reference)

| Dataset | Model | Predictions | Gold | Match |
|---|---|---:|---:|---|
| RSchema | CodeLlama-13B | 518 | 518 | 1:1 by `id` |
| RSchema | Llama-3.1-8B | 518 | 518 | 1:1 by `id` |
| RSchema | DeepSeek-Coder-6.7B | 518 | 518 | 1:1 by `id` |
| SchemaBench | CodeLlama-13B few_shot | 239 (zeros for misses) | 239 | by `id` |
| SchemaBench | Llama-3.1-8B few_shot | 239 | 239 | by `id` |
| SchemaBench | DeepSeek-Coder few_shot | 239 | 239 | by `id` |

## Nomenclature note

In the ICDE manuscript LaTeX, E0 overall metrics are table `\label{tab:e0_overall}`
(internally documented as **Table V** in `paper_methods_vs_paper_tables_comparison.txt`).
**Table VII** in that same comparison file is E1 Schema2Text.
This audit uses “E0 overall table” / “Table VII” interchangeably only when referring to the
user-supplied expected E0 numbers (including SchemaBench few-shot corrected values).
