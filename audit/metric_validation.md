# Metric validation

**Generated:** 2026-10-30

## Structural dimensions (manuscript intent)

| Dim | Definition in Exp4 / Text2Schema2 | Implemented in `src/` |
|---|---|---|
| T Tables | Normalized table identifiers | Yes |
| A Attributes | Table-qualified column identifiers (via per-table sets + name norm) | Yes |
| D Domain | (table, col, type family, nullability) | Yes — **not** equal to Attribute F1 when typed DDL present |
| E Entity | PRIMARY KEY + UNIQUE (incl. composite) | Yes |
| R Referential | Directed FK (src table, src cols, tgt table, tgt cols) | Yes |

## Aggregation (critical)

- **Paper E0 open-weight RSchema Exp4 report:** micro-aggregate — sum gold / recreated / matched across schemas, then P/R/F1.
- **PaperMethods baselines:** macro mean of per-schema F1; failures → F1=0, nGED=1, Halluc=1.
- **Do not** average per-schema F1 and call it micro.
- **Do not** set Domain F1 = Attribute F1 unless predictions lack SQL types (PaperMethods synthetic DDL case — documented inflation).

## Other metrics

| Metric | Definition / notes | Status |
|---|---|---|
| Hallucination rate | (recreated − matched) / recreated; 0 if recreated=0 | Per-dimension available; **paper single Halluc column aggregation not recovered** → E0 Halluc BLOCKED |
| nGED | Symmetric-diff edit cost / (gold_size + pred_size); docstring in vendored code wrongly said max() | Library follows **code** (sum) |
| SCR | Schema coverage of NL vs gold schema (table/column mention heuristics) | E1 archived; substring false-positive risk noted historically — semantics not silently changed |
| BLEU-4 | 0–100 corpus scale in archived E1 | Matches paper detailed for RSchema open models |
| ROUGE-L | F1 | Matches paper detailed for RSchema open models |
| BERTScore-F1 | Documented model; **skipped** in archived E1 JSON (`skip_bertscore: true`) | BLOCKED for exact paper match |

## Empty / failure policies

| Case | Treatment |
|---|---|
| Empty gold & empty pred sets | P=R=F1=1.0 for that dimension set-F1 helper (unit-tested); structural Exp4 path uses count triples |
| Empty pred only | P=0, R=0, F1=0 when gold>0 |
| Empty gold only | R=0; P undefined→0 in micro helper when matched=0 |
| Parse failure / missing output | Exp4 Skip (RSchema archived Skip=0); PaperMethods zero-score inclusion |
| Duplicate predictions | Last/serial file wins by path sort — not observed as an issue in Exp4 |

## Sensitivity

Dimensions where both gold and predicted element counts are zero contribute 0 matched and 0 hallucination rate; they must not be dropped silently from micro denominators when other schemas contribute. Unit tests cover empty-set PRF.

## Bugs discovered during audit

1. **Vendored `parse_ddl_fks` + `IF NOT EXISTS`:** source table can become `"IF"` — fixed in default `src` mode; `legacy=True` preserves bug.
2. **Vendored `evaluate_one` hash-order nondeterminism:** set iteration → ~1e-4 metric jitter — `src` uses sorted tie-break.
3. **Archived Exp4 JSON (2026-06-15) predates SchemaBench DDL parser fix:** recompute lifts CodeLlama Entity 0.278 → **0.3005** (matches paper 0.301).
4. **PaperMethods Domain == Attributes** when no real SQL types — not comparable to Table V Domain.
