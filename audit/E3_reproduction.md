# E3 reproduction — Constructor isolation

**Status: VERIFIED (PRIMARY 765)**

See `results/metrics/reproduced/E3_AUDIT/E3_AUDIT_REPORT.md` and `docs/REPRODUCE_E3.md`.

- Frozen GPT-5.4-mini detailed descriptions and Exp4 constructor predictions exist on the evaluation host (checksummed; not shipped in git).
- Evaluator: `experiments/E3/evaluate_e3_primary.py` (locked E2 vendor).
- Constructor isolation: 765/765 hash-identical.
- Cells vs manuscript: 78 MATCH / 27 MISMATCH (≤0.002) / 0 UNVERIFIABLE.

Historical note: `results/predictions/e3/rschema_cases_describer` remains masking (**E4**), not E3.
