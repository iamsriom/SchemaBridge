# E4 reproduction — Masking / structural inferability

**Status: VERIFIED (PRIMARY)**

## Paper intent

Five masks (MT–MR); Direct GPT-4o-mini and Round-trip tracks; tables `tab:e4_split`, `tab:e4_recovery`; Domain = joint type + nullability.

## PRIMARY artifacts

| Piece | Location |
|---|---|
| Verified metrics | `results/metrics/reproduced/E4_AUDIT/metrics/` |
| Corrected LaTeX | `results/metrics/reproduced/E4_AUDIT/latex/` |
| Audit report | `results/metrics/reproduced/E4_AUDIT/E4_FINAL_VERIFICATION_REPORT.md` |
| Evaluator entry | `experiments/E4/evaluate.py` |
| Frozen values | `experiments/E4/verified_values.py` |
| Masking reference | `third_party/MASKING_VERIFICATION.md` |

## Commands

```bash
python3 experiments/E4/evaluate.py
python3 experiments/E4/generate_tables.py
pytest -q tests/test_e4_primary.py
```

See `docs/REPRODUCE_E4.md`.

## Historical (not PRIMARY)

- Exp5 `domain_facts` Domain scoring
- SchemaBench-only Domain extracts (0.409 / 1,574)
- Archived Cases3 aggregates (`results/metrics/archived/e4_*`)
