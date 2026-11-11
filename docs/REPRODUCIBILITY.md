# Reproducibility

```bash
pip install -r requirements.txt
python scripts/reproduce_tables.py --all --offline
python scripts/reproduce_tables.py --experiment E0 --recompute
python scripts/offline_e1_rschema_detailed.py
# E2 PRIMARY (765 = 145/381/239); requires local original GPT-4o-mini trees
python3 experiments/E2/prepare_dataset.py
PYTHONHASHSEED=0 python3 experiments/E2/evaluate_table_viii_full.py
PYTHONHASHSEED=0 python3 experiments/E2/generate_table_viii.py
pytest -q
```

See also `docs/REPRODUCE_E1_E2.md`.
