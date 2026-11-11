# E3 — Constructor Isolation (`tab:e3_overall`)

Hold the natural-language description fixed (**GPT-5.4-mini**, detailed prompt) and vary only the Text2Schema constructor.

| | |
|---|---|
| **PRIMARY population** | Enterprise-145 **145** + RSchema genuine DDL **381** + SchemaBench **239** = **765** |
| Evaluations | 765 × 5 constructors = **3,825** |
| Describer (fixed) | GPT-5.4-mini detailed (`prompts/describer_detailed.txt`) |
| Constructors | CodeLlama-13B, Llama-3.1-8B, DeepSeek-Coder, Claude Sonnet 4.6, GPT-5.4-mini |
| Constructor prompt | `prompts/constructor.txt` |
| Metrics | mean nGED; Hall. = mean of micro FP rates on **T/A/E/R**; micro F1 for T/A/D/E/R |
| Verified artifacts | `results/metrics/reproduced/E3_AUDIT/` |
| Status | **VERIFIED** (PRIMARY) |

## Authoritative offline reproduction

Original Exp4 constructor predictions and frozen GPT-5.4-mini descriptions are **not** shipped in git (private experimental dumps). Place them at the paths listed in
`results/metrics/reproduced/E3_AUDIT/provenance/E3_SOURCE_INVENTORY.md`
(checksums in `provenance/artifact_checksums_summary.json` and `provenance/checksums/*.csv`).

```bash
# Recompute all 15 groups → E3_AUDIT/metrics/
PYTHONHASHSEED=0 python3 experiments/E3/evaluate.py

# Build Overleaf table
python3 experiments/E3/generate_table.py

pytest -q tests/test_e3_primary.py
```

Generation is disabled:

```bash
python3 experiments/E3/run.py   # refuses API / paid inference
```

## Metric definitions (PRIMARY)

- **nGED** = edit_cost / max(gold_size + pred_size, 1); arithmetic mean over the population.
  Column nodes are `(name, type_family, nullability)` — **type-dependent** (same as E2 Exp4 vendor; **unlike** E0 names-only nGED).
  Empty gold + empty prediction → 0.
- **Hallucination** = unweighted mean of micro FP rates over Tables, Attributes, Entity, Referential (**Domain excluded**).
- **Micro F1** aggregates gold/predicted/matched over the population, then P/R/F1.
- **Domain** requires type-family compatibility **and** nullability agreement.
- **Attribute F1** is name-based (table-qualified after `normalize_rschema_name`).
- Missing predictions remain in N (scored as empty pred vs gold).

Deterministic name-collision handling uses `experiments/E2/vendor/` (`_norm_map`, sorted maps). Prefer `PYTHONHASHSEED=0`.

## What is *not* E3 / not PRIMARY

| Artifact | Role |
|---|---|
| `A_Final_Result/Exp4/exp4_combined_results.txt` | Historical N=518 / 5-dim Hall / Enterprise `lower()` — **not** PRIMARY |
| `A_Final_Result/Exp3/` | Direct gold-NL Text2Schema (different experiment) |
| `results/predictions/e3/rschema_cases_describer` | Historical **masking** → paper **E4** |
| Historical SchemaBench Exp4 evaluation JSON | Hash-order-dependent Attr matching (superseded by locked `_norm_map`) |

## Constructor isolation

All five constructors receive identical frozen NL (hash-verified for 765/765 PRIMARY schemata).
See `E3_AUDIT/isolation/isolation_summary.json`.
