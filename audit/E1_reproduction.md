# E1 reproduction — Schema2Text

**Status: PARTIAL**

## Claimed coverage

902 schemata × 5 describers × 2 prompts (basic/detailed), minus failures.

## What we have

| Dataset | Open basic | Open detailed | Claude/GPT | Metrics archive |
|---|---|---|---|---|
| RSchema | not separately archived | 518×3 preds; metrics match paper **Detailed** BLEU/ROUGE/SCR | MISSING | `e1_rschema_schema2text_evaluation.json` (`skip_bertscore: true`) |
| SchemaBench | preds 239×3 | same dirs (prompt variant unclear) | MISSING | **no** evaluation JSON |
| Enterprise-145 | partial LLMTranslations | partial | MISSING | paper SCR only; no ref NL → BLEU n/a |

## Matches

RSchema open Detailed vs `tab:e1_s2t`: BLEU-4, ROUGE-L, SCR — **9/9 PASS** (within tolerance).

## Blocked / gaps

- Basic prompt metrics for RSchema not in the archived evaluation file (archive appears Detailed-only)
- BERTScore skipped in archive → cannot verify paper BERT columns
- Claude / GPT describer outputs absent
- SchemaBench and Enterprise reference-metric recomputation not wired
- Enterprise has no reference NL — paper correctly marks BLEU/ROUGE/BERT as n/a; do not fabricate
- SCR substring false-positive risk: not silently “fixed”; needs dedicated diagnostic if manuscript claims change

## Prompt files

- `prompts/describer_basic.txt` — extracted from Exp4 schema2text SYSTEM_PROMPT
- `prompts/describer_detailed.txt` — extracted from Text2ER detailed pipeline
