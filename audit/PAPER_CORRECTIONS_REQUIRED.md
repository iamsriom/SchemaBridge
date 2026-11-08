# Paper corrections required

**Manuscript LaTeX is not in this workspace.** Corrections below target the numerical dump in `results/baselines/paper_methods_vs_paper_tables_comparison.txt` (Table V / VII / VIII) and claims from prior Fig5 audits. Provide exact LaTeX only where labels are known.

## Do not auto-edit the manuscript

Apply manually after author review.

---

## A. `tab:e0_overall` — RSchema open-weight

### A1. Prefer corrected-parser recomputation for CodeLlama Entity

Archived Exp4 (2026-06-15) Entity **0.278** ≠ paper **0.301**.  
Offline recompute (SchemaBridge `src`, legacy-corrected parser): Entity **0.3005** → rounds to **0.301**.

Recommended: state that Table V RSchema open rows are recomputed with the corrected DDL/entity parser, and replace any text that cites the June micro report’s Entity 0.278 as final.

### A2. Llama-3.1 row still unreproduced

Even after recompute:

| Metric | Paper | Recomputed | Action |
|---|---:|---:|---|
| nGED | 0.764 | ≈0.774 | Investigate alternate preds or correct paper |
| Attributes | 0.375 | ≈0.347 | Same |
| Domain | 0.181 | ≈0.165 | Same |
| Entity | 0.169 | ≈0.170 | Near match after recompute |

**Do not** silently patch Llama numbers without locating matching predictions.

### A3. Hallucination column

Aggregation definition not recovered. Either publish the exact formula (mean of 5 dim rates vs macro of per-schema mean) with reproducible code, or withdraw the column until defined.

### A4. Claude / GPT-5.4-mini rows

No per-schema files. Options: (1) release predictions and recompute, or (2) remove rows / mark unavailable. **Do not** keep point estimates without artifacts.

---

## B. `tab:e0_overall` — SchemaBench

Paper block (e.g. CodeLlama nGED **0.831**, Tables **0.351**, Entity **0.182**) ≠ corrected few_shot (nGED **0.901**, Tables **0.373**, Entity **0.191**).

Choose one:
1. Update Table V SchemaBench to corrected few_shot macro (zeros included), or  
2. Document and release the exact older prediction+parser that produced 0.831…

---

## C. `fig:e0_heatmap` (Figure 5)

- Cannot publish five-constructor heatmap without Claude/GPT per-schema E0.
- Large–Medium cell is **not empty** (n=1, mean F1≈0.219 under 3-model diagnostic).
- Large tier count **53**, not 50.
- Forbid claim “every large-schema cell F1 ≤ 0.15”.

Suggested caption if releasing diagnostic only:

```latex
% NOT the camera-ready five-model figure
\caption{Diagnostic mean structural $F_1$ over three open-weight constructors only. Claude Sonnet 4.6 and GPT-5.4-mini per-schema E0 predictions are unavailable.}
```

---

## D. `tab:e1_s2t` / `tab:e2_roundtrip`

- RSchema open **Detailed** columns largely match archives; disclose BERTScore skipped in archive; disclose Basic archive missing.
- SchemaBench / Enterprise / closed-model cells lack releasable complete artifacts — mark or regenerate.
- E2 cells differing at ~0.001 may be rounding or older parser — recompute with shared evaluator before camera-ready.

---

## E. `tab:e3_overall`, `tab:e4_*`, `tab:e5_cost`

No on-disk paper numbers + missing core artifacts (E3 fixed GPT-5.4-mini descriptions; E5 billing logs; E4 incomplete across 902). **Withdraw or regenerate** before camera-ready.

---

## F. Domain integrity baselines

PaperMethods Domain F1 == Attributes F1 (no SQL types). Do not present as comparable to Table V Domain without a typed-DDL baseline.
