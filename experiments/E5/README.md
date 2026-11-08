# E5 — Cost and latency

**Paper:** `tab:e5_cost`  
**Status: BLOCKED**

## Objective

Report mean latency and API cost per schema with frozen pricing and token accounting.

## Artifacts

No billing exports or complete token logs are packaged. Local `elapsed_s` fields are wall-clock only.

**Note:** `fig:e0_heatmap` belongs to E0, not E5. Diagnostic heatmap files live under `figures/`.

## Commands

```bash
python experiments/E5/evaluate.py
python scripts/reproduce_tables.py --experiment E5 --offline
```

See `audit/E5_reproduction.md`.
