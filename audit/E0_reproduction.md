# E0 reproduction — Text2Schema from gold NL

**Status: PARTIAL / MISMATCH / BLOCKED (not PASS overall)**

## Scope

- Datasets: RSchema 518 + SchemaBench 239
- Models claimed: CodeLlama-13B, Llama-3.1-8B, DeepSeek-Coder-6.7B, Claude Sonnet 4.6, GPT-5.4-mini
- Tables: `tab:e0_overall`, `tab:e0_baselines`, `fig:e0_heatmap`

## What reproduces

| Artifact | Result |
|---|---|
| Archived Exp4 micro JSON vs Exp4 report text | **PASS** (all 3 open models) |
| SchemaBench few_shot corrected baselines JSON vs report | **PASS** |
| RSchema DeepSeek vs paper (most cells) | **PASS** within 0.0005 (Domain 0.2149 vs 0.214 fails archived comparison) |
| CodeLlama Entity after `--recompute` | **0.3005 ≈ paper 0.301 PASS** |

## Material mismatches (archived Exp4 micro vs paper)

| Model | Metric | Paper | Archived | Δ |
|---|---|---:|---:|---:|
| CodeLlama | Entity F1 | 0.301 | 0.278 | −0.023 |
| CodeLlama | nGED | 0.734 | 0.733 | −0.001 |
| Llama | nGED | 0.764 | 0.775 | +0.011 |
| Llama | Attr F1 | 0.375 | 0.350 | −0.025 |
| Llama | Domain F1 | 0.181 | 0.167 | −0.014 |
| Llama | Entity F1 | 0.169 | 0.180 | +0.011 |

**Interpretation:** The June-2026 archived Exp4 evaluator/parser combination does **not** fully reproduce the published RSchema open-weight row. Offline recompute with the corrected library recovers CodeLlama Entity; Llama Attr/Domain/nGED remain unresolved (no alternate prediction tree found).

## SchemaBench `tab:e0_overall` block

Paper block (e.g. CodeLlama nGED 0.831 …) **does not match** corrected few_shot macro means (nGED 0.901 …). Fig5 audit states the older manuscript block is not the validation target for corrected few_shot — **MISMATCH** if paper still prints the old block.

## Closed models

Claude Sonnet 4.6 and GPT-5.4-mini: **0/518 and 0/239 per-schema predictions** — **BLOCKED**. gpt-4o-mini trees exist but are the wrong model.

## Hallucination column

Paper single Halluc number: aggregation not recovered from local candidates — **BLOCKED** for all models.

## Baselines (`tab:e0_baselines`)

Local PaperMethods one_shot / CoT / few_shot / schema_agent scores exist for RSchema and SchemaBench. Domain F1 == Attr F1 on PaperMethods. schema_agent near floor after zeroing failures. Exact paper baseline table not on disk as LaTeX — treat local reports as reproducible baselines, not verified paper cells.

## Figure `fig:e0_heatmap`

Five-constructor heatmap **BLOCKED** (Priority C). Diagnostic 3-model matrix in `figures/fig5_heatmap_values_diagnostic.csv` must **not** be labeled as the published five-model figure.

## Prompt / decoding

Constructor prompt extracted to `prompts/constructor.txt` from SchemaBench Exp4 scripts. Temperature 0.1 / max tokens 2048 recorded in historical scripts; closed-model snapshots unknown.
