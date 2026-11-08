# Figure 5 — Final validation

Generated: 2026-10-28

## Decision: Priority C

**Figure 5 is NOT ready for publication.**

| Priority | Condition | Status |
|---|---|---|
| A | Five constructors recovered + validated | **FAIL** — Claude / GPT-5.4-mini per-schema E0 missing |
| B | Proprietary missing but RSchema E0 table reconciled | **FAIL** — RSchema CodeLlama Entity / Llama Attr (etc.) unreproduced |
| C | RSchema discrepancy unresolved → do not mark ready | **SELECTED** |

No validated final heatmap is declared. Candidate three-model numbers below are
**diagnostic only** (see `fig5_heatmap_values.csv`); they must not be treated as the
ICDE Figure 5 replacement.

---

## Step 3 methodology checks (3 open-weight constructors)

| Check | Result |
|---|---|
| Same E0 preds as E0 overall table? | **Partial.** SchemaBench few_shot matches expected table. RSchema Exp4 is the only local complete set but **does not** match published RSchema E0 rows → Fig5/table consistency **FAIL** |
| 757 gold schemata exactly once | **PASS** (518+239); heatmap schema_count sum = 757 |
| Size rules (≤5&≤50 / ≤15&≤150 / else) | **PASS** (applied to corrected gold) |
| Complexity \(s=2\min(f,10)+3c+\min(u,5)+(1/5)\max(0,n_{col}/n_{tab}-10)\) | **PASS**; Easy \(s<4\), Medium \(4\le s<10\), Hard \(s\ge10\) |
| Per-schema structural F1 = mean of 5 dim F1s | **PASS** (tables, attributes, domain, entity, referential) |
| Cell = mean over schema–model pairs (equal model weight) | **PASS** among the 3 available models; paper claims 5 |
| Failures scored consistently (empty→zero / zero policy) | **PASS** for SchemaBench few_shot zeros; RSchema Exp4 Skip=0 |
| Corrected gold parsing | **PASS** for SchemaBench; RSchema structured gold unaffected |

### Large–Medium

- Unique schemata: **1** (`SchemaBench` / `SB-155`, 19 tables, 69 columns, \(s=5.0\))
- Mean structural F1 (3 models): **0.219**
- Per-model: CodeLlama 0.295, Llama 0.161, DeepSeek 0.200
- Historical “empty cell” claim is **false** after corrected parsing/grouping

### Forbidden claim

Do **not** state that every large-schema cell has F1 ≤ 0.15.
Large–Medium = 0.219 refutes that claim.

Large tier size: **53** (not 50).

---

## Candidate 3×3 (NOT validated for publication)

Models: CodeLlama-13B, Llama-3.1-8B, DeepSeek-Coder-6.7B only.

Mean structural \(F_1\) (3dp):

| | Easy | Medium | Hard |
|---|---:|---:|---:|
| Small | 0.209 | 0.344 | 0.340 |
| Medium | 0.206 | 0.256 | 0.275 |
| Large | 0.112 | 0.219 | 0.122 |

Unique schema counts:

| | Easy | Medium | Hard |
|---|---:|---:|---:|
| Small | 85 | 316 | 63 |
| Medium | 40 | 15 | 185 |
| Large | 28 | 1 | 24 |

Per-model overall mean structural F1 (all 757 schemata): CodeLlama 0.307, DeepSeek 0.304, Llama 0.249.

### Scoring / aggregation definitions

1. Per schema–model: \(F_1\) on each of five dimensions via Exp4/Text2Schema2 strict matching; `mean_structural_f1 = mean(five F1s)`.
2. Per heatmap cell: arithmetic mean of `mean_structural_f1` over all schema–model pairs in the cell (equal weight).
3. Missing SchemaBench few_shot preds scored as zero (PaperMethods policy).

### Reproduction commands

```bash
python3 /data/experiments/fig5_corrected_e0/tests/test_fig5_parsers_and_strata.py
python3 /data/experiments/fig5_corrected_e0/recompute_fig5.py
```

### Recommended caption (only after Priority A or B clears)

```
Figure 5. E0 mean structural $F_1$ by gold schema size (rows) and constraint
complexity (columns). Cell values average per-schema means of the five
dimensional $F_1$ scores over the listed constructors. Size and complexity
use the paper definitions on corrected gold schemata ($N=757$; Large $n=53$).
```

Do **not** claim five constructors until Claude/GPT per-schema E0 files exist and
RSchema E0 overall is reconciled.

---

## Step 5 — Separate change causes

Do **not** interpret 3-model candidate cells vs historical 5-model Figure 5 as
“parser-only” deltas.

| Cause | Effect on Fig 5 |
|---|---|
| **Parser corrections** (SchemaBench DDL) | Reclassifies some gold size/complexity; fixes entity/domain gold counts; enables Large–Medium n=1 (`SB-155`); changes SchemaBench few_shot overall metrics |
| **Gold-schema grouping changes** | Large tier 50→53; Large–Medium empty→1; Small/Medium cell membership shifts |
| **Different model set** | Historical Fig 5 = 5 constructors; candidate = 3 open-weight only → **not comparable** as a parser delta |
| **Different / unresolved evaluation lineage (RSchema)** | Published RSchema E0 rows ≠ Exp4 micro for CodeLlama Entity / Llama Attr–Domain–Entity–nGED; Fig5 cannot claim consistency with the printed table |

---

## Validation status

**FAIL — Priority C — no publication-ready Figure 5 dataset.**

Required for upgrade to Priority B: exact reproduction of all seven RSchema
open-weight E0 metrics from archived preds+scripts (or a documented manuscript
correction of those metrics to Exp4).

Required for Priority A: additionally recover Claude Sonnet 4.6 and GPT-5.4-mini
per-schema E0 predictions for both datasets.
