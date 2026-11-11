# Reproducing E1 and E2

## E1 (Schema2Text)

See `experiments/E1/README.md` and the verified E1 release on `main`.

## E2 (Round-Trip / Table VIII)

PRIMARY population: **765** schemata (Enterprise 145, RSchema genuine DDL **381**, SchemaBench 239).

```bash
pip install -r requirements.txt
python3 experiments/E2/prepare_dataset.py
# Requires original GPT-4o-mini trees (paths + SHA-256 in
# results/metrics/reproduced/E2_AUDIT/provenance/)
PYTHONHASHSEED=0 python3 experiments/E2/evaluate_table_viii_full.py
PYTHONHASHSEED=0 python3 experiments/E2/generate_table_viii.py
pytest -q tests/test_e2_primary.py
```

Do **not** use RSchema N=518 synthetic gold or the July 2026 Detailed-only aggregates as PRIMARY.
The combined macro table `tab:e2_combined_prf1` is historical and is not part of the PRIMARY release.

Trajectory figure (N=765): `results/metrics/reproduced/E2_AUDIT/figures/cmp_chart4_trajectory.png`.
