# E2 reproduction — Schema → Text → Schema round-trip

**Status: MISMATCH / BLOCKED**

## Protocol

- Reuse E1 descriptions (do not regenerate)
- Constructor fixed: **GPT-4o-mini**
- Vary describer / prompt only

## RSchema open Detailed

Archived `e2_rschema_roundtrip_evaluation.json` / report vs paper Detailed:

- **14 / 18 cells PASS**
- MISMATCH examples (tol 0.0005): CodeLlama Domain 0.2235 vs 0.224; Entity 0.8766 vs 0.876; Llama Entity 0.7408 vs 0.739; DeepSeek Attr 0.9483 vs 0.950

Basic columns and Claude/GPT: **BLOCKED** (no matching archives).

## SchemaBench

Predictions incomplete (216 / 227 / 195 of 239) and **no** metrics archive — **BLOCKED**.

## Enterprise-145

Older Text2Schema2 results exist under `/data/Results/Text2Schema2Results` but are not wired into SchemaBridge offline tables as verified `tab:e2_roundtrip` — **BLOCKED** pending alignment.

## Size cliff / trajectory / SCR correlation figures

`tab:e2_sizecliff`, `fig:e2_trajectory`, paired SCR↔F1 correlations: strata scripts partially exist in fig5 tooling; published figure numbers absent — **BLOCKED**. Do not reuse Fig5 size rules as identical to E2 strata without manuscript confirmation.

## Leakage check

Round-trip inputs are schema2text NL folders; constructor scripts historically take NL only. Spot-check: prediction JSON fields are reconstructed DDL/metadata — gold DDL not observed as constructor input in archived Exp2 trees. Full prompt-log audit incomplete without API request dumps.
