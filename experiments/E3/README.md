# E3 — Constructor isolation

**Paper:** `tab:e3_overall`  
**Status: BLOCKED**

## Objective

Hold the natural-language description fixed (GPT-5.4-mini, detailed prompt) and vary only the constructor, measuring structural preservation (nGED, Halluc, T/A/D/E/R).

## Required inputs (missing)

- Fixed detailed descriptions for each gold schema
- Per-constructor reconstructions from those identical strings
- Model IDs / decoding parameters for each constructor

## What is *not* E3

`results/predictions/e3/rschema_cases_describer` is historical **masking** describer output (paper **E4**). Kept for migration traceability only.

## Commands

```bash
python experiments/E3/evaluate.py   # reports BLOCKED / inventory only
python experiments/E3/run.py        # refuses online generation by default
```

See `audit/E3_reproduction.md`.
