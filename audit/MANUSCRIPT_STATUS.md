# Manuscript status

**Generated:** 2026-10-30

## Finding

No ICDE 2027 LaTeX manuscript (`main.tex`, `Text2Schema_ICDE_2027`, or any `*.tex`) exists anywhere under `/data`, `/home/ubuntu`, or related mounts searched for this audit.

## Authoritative numerical sources used instead

| Source | Path | Role |
|---|---|---|
| Paper table dump (E0/E1/E2) | `results/baselines/paper_methods_vs_paper_tables_comparison.txt` | Published Table V / VII / VIII numbers typed from paper screenshots |
| Frozen JSON of those numbers | `configs/paper_reference_values.json` | Machine-readable targets for `reproduce_tables.py` |
| Fig 5 prior audit | `figures/fig5_*.md`, `figures/fig5_heatmap_values_diagnostic.csv` | Priority-C verdict; diagnostic 3-model heatmap only |
| LaTeX labels from audit brief | User task text (this session) | `tab:e0_overall`, `tab:e1_s2t`, `tab:e2_roundtrip`, `tab:e3_overall`, `tab:e4_*`, `tab:e5_cost`, `fig:e0_heatmap`, … |

## Limitation

Exact paper reproduction **cannot be claimed** for tables/figures whose numbers are not in the comparison dump (E3 constructor isolation, E4 published masking tables, E5 cost, size-cliff, trajectories, FK-support). Those are marked **BLOCKED** pending the manuscript and matching artifacts.
