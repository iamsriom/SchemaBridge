# E5 Repository Audit — SchemaBridge

**Audit date:** 2026-11-06  
**Package root:** `/data/SchemaBridge`  
**New E5 artifacts:** `experiments/e5/` (lowercase; does not modify stub `experiments/E5/`)

## Datasets and gold schemata

| Dataset | n | Gold location | Identifier |
|---|---:|---|---|
| Enterprise-145 | 145 | `datasets/enterprise145/schema` → `/data/Text2ER/schema/*.sql` (+ `*.metadata.json`) | SQL stem (e.g. `Accidents`) |
| RSchema | 518 | `datasets/rschema/annotation.jsonl` (logical); optional DDL in `annotation_ddl.jsonl` (381 typed) | Mongo-style `id` |
| SchemaBench | 239 | `datasets/schemabench/annotation_ddl.jsonl` | `SB-NNN` / record `id` |
| **Total** | **902** | | |

Size tiers (paper / `third_party/recompute_fig5.py`): Small ≤5 tables & ≤50 cols; Medium ≤15 & ≤150; else Large.  
Constraint complexity: `s = 2*min(f,10) + 3*c + min(u,5) + 0.2*max(0, n_col/n_tab - 10)` → Easy `<4`, Medium `[4,10)`, Hard `≥10`.

## Model wrappers and exact model IDs

| Role | Display | Deployed / archived ID | Availability (this host) |
|---|---|---|---|
| Describer (open) | DeepSeek-Coder-6.7B-Instruct | `deepseek-ai/deepseek-coder-6.7b-instruct` | Local HF weights + 6×T4 via `/data/Text2ER/.venv` |
| Describer (closed) | GPT-5.4-mini | `gpt-5.4-mini` (snapshot `gpt-5.4-mini-2026-03-17`) | **Blocked:** `/data/openai_api.txt` returns HTTP 401 |
| Describer (closed) | Claude Sonnet 4.6 | `claude-sonnet-4-6` | **Blocked:** no `ANTHROPIC_API_KEY` / anthropic credential file |
| Constructor (E2/E5-A) | GPT-4o-mini | `gpt-4o-mini` | Archived E2 outputs exist; **new calls blocked** (same 401) |
| Constructor (E5-B) | GPT-5.4-mini / Claude Sonnet 4.6 | as above | **Blocked** (credentials) |

Generation settings (archived scripts): schema2text `temperature=0.2`, `max_new_tokens=3072`; GPT-4o-mini constructor `temperature=0.2`. Prompts: `prompts/describer_basic.txt`, `prompts/describer_detailed.txt`, `prompts/constructor.txt`.

## Existing reusable outputs

| Artifact | Path | Compatible with E5? |
|---|---|---|
| E1 DeepSeek descriptions (basic prompt) | `results/predictions/e1/rschema_schema2text_deepseek` (518), `…/schemabench_schema2text_deepseek` (239) | **Yes for text** — same model ID + basic system prompt as `describer_basic.txt`. **No** token/latency/cost logs. |
| E2 DeepSeek→GPT-4o-mini round-trips | `results/predictions/e2/rschema_rt_deepseek` (518), `…/schemabench_rt_deepseek` (195/239) | **Yes for fidelity** when schema IDs match. Missing usage/latency. |
| E1/E2 CodeLlama / Llama-3.1 | same trees | Out of E5 model list (E5 uses DeepSeek + GPT-5.4-mini + Claude). |
| E3 GPT-5.4-mini fixed descriptions | — | **Absent** (`experiments/E3` BLOCKED). |
| Claude / GPT-5.4-mini per-schema preds | — | **Absent** (paper numbers only). |
| Enterprise round-trips | — | **Absent**. |
| Billing exports | — | **Absent** (`audit/E5_reproduction.md`). |

## Missing information requiring new calls

1. GPT-5.4-mini basic/detailed descriptions and constructor runs (E5-A/B/C).  
2. Claude Sonnet 4.6 all roles.  
3. Fresh GPT-4o-mini reconstructions for DeepSeek **detailed** descriptions and Enterprise.  
4. Provider usage logs (input/output/cached/reasoning tokens) and wall-clock latency for archived E2 constructor calls.  
5. Anthropic credentials; valid OpenAI credentials (current key rejected).

## Evaluator entry points

- Core: `src/evaluator.py` (`evaluate_schema_pair`, `five_element_counts`, `aggregate_schemas`) + `src/metrics.py` (micro F1, mean nGED, zero-score policy).  
- Name matching: `normalize_rschema_name` (strict normalized identifiers).  
- Unparseable / empty prediction: zero element scores, `nGED=1` for nonempty gold (PaperMethods zero policy via `zero_scored_schema_metrics`).  
- E5 wraps this evaluator; does not redefine F1/nGED.

## Reproducibility limitations

- Closed-model rows cannot be regenerated on this host until OpenAI/Anthropic keys work.  
- Archived open-model round-trips lack billed token fields; E5 reports **tokenizer-estimated** tokens/cost for archived GPT-4o-mini I/O where texts exist, clearly labeled `cost_basis=estimated_from_archived_text`.  
- DeepSeek monetary cost is **N/A** (local GPU; no provider invoice). Latency from new local runs is wall-clock, not “intrinsic FLOPs time.”  
- SchemaBench E2 DeepSeek coverage is 195/239; sample prefers covered IDs then redistributes.  
- Stub `experiments/E5/` remains offline BLOCKED; this package is the executable E5.
