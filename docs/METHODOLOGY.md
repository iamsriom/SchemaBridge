# Methodology

Metrics in src/metrics.py and src/evaluator.py. June 2026 archives and current src can differ slightly.

## E1 - Schema -> Text (`src/nl_metrics.py`)

* **BLEU-4**: `sacrebleu.corpus_bleu(hyps, [refs])` - one reference stream containing every reference.
  The historical `corpus_bleu(hyps, [[r] for r in refs])` (one stream per record) is a bug and gives wrong scores.
* **ROUGE-L**: mean F1 per schema, Porter stemming (`rouge-score`).
* **BERTScore**: F1, `roberta-large`, English, no IDF weighting, no baseline rescaling.
* **SCR (schema coverage rate)**: for each schema the fraction of gold DDL table and column identifiers
  (case/underscore/quote-insensitive) that occur in the description; **macro** average over schemas.
* Enterprise-145 has no gold text: BLEU, ROUGE-L and BERTScore are N/A, only SCR is reported.
* Failed/missing hypotheses: `--fail-policy score` evaluates them as empty text, `skip` removes them.

## E2 - round trip (`src/evaluator.py`)

* Gold: genuine DDL (RSchema = 381 DDL-matched schemas; never the synthetic varchar DDL of the 518 logical annotations).
* Per dimension (Tables, Attributes, Domain, Entity, Referential) the gold/recreated/matched counts of all
  schemas are summed and micro-F1 is computed; nGED is averaged over schemas.
* Entity = PRIMARY KEY + UNIQUE constraints (composite keys compared as column sets); Referential = directed
  FK edges (composite FKs compared column-wise).
* Failed/missing reconstruction (`--fail-policy score`): `empty_prediction_against_gold` - gold counts kept,
  recreated = matched = 0, nGED = 1. `skip` drops the schema.
