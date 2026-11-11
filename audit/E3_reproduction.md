# E3 reproduction — Constructor isolation

**Status: REPRODUCIBLE (code) — experimental outputs not shipped**

## Paper intent

- Describer **fixed** to GPT-5.4-mini with **Detailed** prompt
- Same NL description for every constructor on a given gold schema
- Vary constructors; report `tab:e3_overall` (nGED, Halluc, T/A/D/E/R)

## What this repository provides

| Artefact | Shipped? |
|---|---|
| Verified constructor prompt + decoding configs | **YES** (`prompts/constructor.txt`, `src/inference_clients.py`) |
| Fixed-description loader / isolation hash checks | **YES** (`experiments/E3/prepare_inputs.py`, `validate_inputs.py`) |
| Five constructor dry-run / HF execute CLIs | **YES** (`experiments/E3/run.py`) |
| Audited structural evaluator (empty-gold + 5-dim Hall.) | **YES** (`experiments/E3/evaluate.py`, shared `src/`) |
| Synthetic tests | **YES** (`tests/test_e3_*.py`) |
| Step-by-step guide | **YES** (`docs/REPRODUCE_E3.md`) |
| Fixed GPT-5.4-mini Detailed descriptions | **NO** (generate/load locally) |
| Per-constructor reconstructions | **NO** |
| Table IX numerical values / LaTeX with scores | **NO** (generate locally via `generate_table_ix.py`) |

## Naming collision

Historical folder `results/predictions/e3/rschema_cases_describer` is **masking/describer**, which maps to paper **E4**, not E3. Kept for migration history only — do not treat as constructor-isolation evidence.

## Methodological notes (final recheck)

- PRIMARY population: Enterprise-145=145, RSchema=381 genuine DDL, SchemaBench=239 (N=765).
- Empty gold + empty reconstruction ⇒ nGED = 0 (valid).
- Hallucination = mean of five micro `(R−M)/R` rates; Recreated=0 → 0.
- Name normalisation: RSchema-style (shared with verified E2 scorer).

## Verdict

Reproduction **implementation** is available in-tree. Offline archive comparison via
`scripts/reproduce_tables.py --experiment E3` remains **BLOCKED** because experimental
predictions and paper cell dumps are intentionally not distributed.
