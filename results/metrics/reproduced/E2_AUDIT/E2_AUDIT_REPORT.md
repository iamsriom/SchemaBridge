# E2 PRIMARY Audit Report (ICDE 2027)

**Evaluator:** `experiments/E2/evaluate_table_viii_full.py` (locked vendor, deterministic name maps)  
**Log:** `logs/evaluate_primary_locked.log` (EXIT:0)  
**Population:** 145 + 381 + 239 = **765**

## Scientific verdict

| Item | Result |
|---|---|
| Groups evaluated | **30/30** |
| Unique numerical cells | **180** |
| Independently recomputed from original predictions | **Yes** |
| Cross-process determinism (PYTHONHASHSEED) | **Pass** after collision-safe maps |
| Failed reconstructions scored | **9** files across 5 groups (see `provenance/failed_reconstructions_parsed.json`) |
| `tab:e2_combined_prf1` | **Historical only** — not PRIMARY |

### Versus prior draft PRIMARY table (pre-determinism-lock)

| Status | Cells |
|---|---:|
| MATCH @ 3-dec | 139 |
| MISMATCH @ 3-dec | 41 (almost all ±0.001) |
| UNVERIFIABLE | 0 |

Material earlier claim that Enterprise Claude/GPT Detailed nGED should move 0.101→0.099 / 0.108→0.106 is **withdrawn**: those drifts were hash-seed nondeterminism. Locked evaluation confirms **0.101** and **0.108**.

### Versus July 2026 Detailed-only / RSchema N=518

Not interchangeable with PRIMARY. See `metrics/HISTORICAL_N518_NOTE.json` and `/data/A_Final_Result/Exp2/a.txt`.

## Failures (scored nGED=1, F1 contribution 0)

| Dataset | Prompt | Model | Files |
|---|---|---|---|
| Enterprise-145 | basic | sonnet46 | `tmp.json` |
| Enterprise-145 | basic | gpt54mini | `archive.json`, `ctu_vondreli.json`, `tmp.json` |
| Enterprise-145 | detailed | sonnet46 | `archive.json`, `ctu_vondreli.json` |
| Enterprise-145 | detailed | gpt54mini | `archive.json`, `tmp.json` |
| RSchema | detailed | gpt54mini | `0147.json` (JSON parse error) |

## Outputs

- `metrics/E2_PRIMARY_FINAL.csv` — full precision + 3-dec
- `metrics/E2_CELL_COMPARISON_180.csv` — vs prior draft
- `latex/tab_e2_roundtrip_verified.tex` — Overleaf-ready
- `figures/cmp_chart4_trajectory.{png,pdf}`
- `provenance/prediction_manifest.csv`, `source_hashes.json`, `evaluation_protocol.md`
