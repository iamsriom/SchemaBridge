# E2 Method Audit

Manuscript table: `\label{tab:e2_roundtrip}`.

## Pipeline

```
Gold Schema → E1 Schema2Text (describer) → GPT-4o-mini Text2Schema → reconstructed DDL
```

Constructor verified as `model_id=gpt-4o-mini` / `llm=gpt4omini` in E2 reconstruction JSON.

## Structural dimensions (paper vs implementation)

| Dimension | Element | Matching |
|---|---|---|
| Tables | normalized relation names | exact after `normalize_rschema_name` |
| Attributes | `(table, column)` | exact after name norm |
| Domain | `(table, column, type_family, nullability)` | int/str families; YES/NO nullability; DEFAULT/CHECK excluded |
| Entity | PK + UNIQUE (composites as tuples) | set equality |
| Referential | directed FK `(src_table, src_cols, tgt_table, tgt_cols)` | ON UPDATE/DELETE excluded |

## Micro-averaged F1

Aggregate matched / predicted / gold over the evaluation population, then P/R/F1. Confirmed via `agg_element` (not macro mean of per-schema F1). Empty-set denominators → 0.

## nGED

Symmetric difference of tables + typed attribute labels `(col, type_family, null)` + directed FKs; denominator `max(|G|+|P|, 1)`; mean over schemata; failures → 1.0. Implementation: audited `normalized_graph_edit_distance` in `evaluate_exp4_text2schema.py` (not an external GED library).

## Name normalization

- PRIMARY standardizes on `normalize_rschema_name` for all datasets/prompts.
- Historical Enterprise Detailed (Exp2) used `strip().lower()` only; PRIMARY corrections on Enterprise Detailed partly reflect this standardization.

## FK parser

Uses Text2ER `evaluate_text2schema2.py` with `KEY\s*\(` so SchemaBench `FOREIGN KEY(col)` gold is counted. Older Results copy without `\s*` undercounts gold FKs — not used.

## Offline tests

`E2_REPRODUCIBILITY/tests/test_structural_metrics_final.py` — all PASS (exact tables/attrs, datatype/nullability, composite PK/UNIQUE/FK, micro vs macro, nGED, failures, RSchema-381 ID alignment).

## Paper vs PRIMARY methodology verdict

- Metric definitions match the paper.
- Micro-F1 and nGED formulas match.
- **Population for RSchema diverges:** manuscript numbers track historical **N=518 synthetic DDL**; PRIMARY uses **N=381 genuine DDL**.
- **Failure handling:** paper-declared convention is score-as-fail; some historical reports skipped failures.
