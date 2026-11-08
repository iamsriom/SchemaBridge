# Dataset validation

**Generated:** 2026-10-30

## Collections

| Collection | Expected | Observed | Gold path in SchemaBridge | Notes |
|---|---:|---:|---|---|
| Enterprise-145 | 145 | 145 `.sql` (+ metadata) | `datasets/enterprise145/schema` (symlink) | No file literally named Enterprise; CTU-style SQL corpus under Text2ER/schema |
| RSchema | 518 | 518 unique `id` in `annotation.jsonl` | `datasets/rschema/annotation.jsonl` | Structured gold answer; synthetic DDL used in Exp4 |
| SchemaBench | 239 | 239 unique `id` in `annotation_ddl.jsonl` | `datasets/schemabench/annotation_ddl.jsonl` | Gold DDL string in `answer` |
| **Total** | **902** | **902** | | |

## Experiment coverage (from configs + artifacts, manuscript absent)

| Experiment | Paper intent | Local coverage |
|---|---|---|
| E0 | RSchema 518 + SchemaBench 239 = 757 | Open-weight preds present; Claude/GPT missing |
| E1–E3 | generally all 902 | Open-weight RSchema strong; SchemaBench/Enterprise/closed incomplete |
| E4 | masking across gold collections | Enterprise-145 strongest; RSchema describer-only 1Q2–1Q6; SchemaBench none |
| E5 | cost/latency | No usage logs |

## Integrity checks

- RSchema IDs: 518 unique — **PASS**
- SchemaBench IDs: 239 unique — **PASS**
- RSchema `annotation_ddl.jsonl`: **381** rows only (not 518) — do not use as sole gold for E0
- Requirement↔schema pairing: Exp4 predictions keyed by gold `id` / serial — spot-checked 1:1 for RSchema open models
- Duplicate records across collections: IDs are collection-local; no shared ID namespace assumed
- Invalid/empty DDL: SchemaBench parser regression covered in `tests/test_parser.py`; empty preds scored under PaperMethods zero policy

## Inclusion / exclusion

- E0 open-weight RSchema Exp4: Skip=0 / 518 for all three models (archived report)
- SchemaBench PaperMethods few_shot: failures included as F1=0, nGED=1 (macro)
- SchemaBench E2 round-trip: incomplete (216 / 227 / 195 of 239) — **exclude from paper claims until completed**
