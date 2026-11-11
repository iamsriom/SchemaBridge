# E2 Trajectory Figure Audit (`cmp_chart4_trajectory.pdf`)

## Original provenance
- Local copies: `~/Desktop/Text2Schema/Fig/cmp_chart4_trajectory.pdf`, `Diagrams/`, `Downloads/`.
- Classification rules: `/data/SchemaBench/Results/schema_size_content_classification_rules.txt` (`schema_classification.py`).
- Historical plotted values built from `/data/Dataset/text2schema_exp{1,2}_f1_matrix.json` over **unified n=902** (RSchema **518**, including synthetic/non-DDL gold).
- Aggregation (historical + PRIMARY): within each (size×content) cell, compute **micro-F1** on each of the five structural dimensions, then **Mean F1 (5 dims)** = arithmetic mean of those five F1 scores.
- Original figure title claimed “E1 vs E2” / n=902 and legend “E1 Basic / E2 Detailed”; IEEE caption correctly describes **E2** Basic vs Detailed with GPT-4o-mini constructor. Legend naming in the old PDF was misleading.

## PRIMARY recomputation
- Population: Enterprise-145 **145** + RSchema genuine DDL **381** + SchemaBench **239** = **765**.
- Predictions: same E2 GPT-4o-mini trees as Table VIII PRIMARY.
- Failures retained (matched=0, recreated=0 → F1 contribution 0).
- Size: small ≤5 tables & ≤50 cols; medium ≤15 tables & ≤150 cols; else large.
- Content score: `2*min(fk,10)+3*composite_fk+min(unique,5)+max(0,cols/table−10)/5` → easy&lt;4, medium&lt;10, hard≥10.

### Cell counts (PRIMARY vs historical 902)
| size×content | N=765 | N=902 |
|---|---:|---:|
| small×easy | 81 | 86 |
| small×medium | 299 | 368 |
| small×hard | 53 | 71 |
| medium×easy | 17 | 17 |
| medium×medium | 15 | 16 |
| medium×hard | 208 | 251 |
| large×easy | 3 | 3 |
| large×medium | 2 | 2 |
| large×hard | 87 | 88 |

Sparse cells large×easy (n=3) and large×medium (n=2) remain fragile; do not over-interpret within-band spikes there.

## Claim checks
1. **Structural fidelity declines with schema size:** **SUPPORTED.** For all 5 models × {Basic,Detailed}, size-band Mean F1 satisfies small &gt; large (usually small ≥ medium ≥ large; Claude/GPT Detailed have medium slightly above small, but both still ≫ large).
2. **Constraint-sparse (easy) schemata show more over-generation:** **SUPPORTED for referential structure.** Under Detailed prompting, mean `recreated/gold` FK ratio is ~4.0 on easy vs ~0.67 on hard; easy FK precision is low while recall is near-ceiling (constructors emit many unsupported FKs when gold is constraint-sparse). Attribute over-generation is weaker/mixed; the strong signal is referential.

## Figure status
- Regenerated vector PDF **without embedded caption/title**.
- Path: `figures/cmp_chart4_trajectory.pdf`
- Underlying CSV: `results/trajectory_mean_f1_primary.csv`
