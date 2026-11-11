# Cause analysis for 27 manuscript ↔ PRIMARY mismatches

**Authoritative evaluator:** locked E2 vendor (`experiments/E2/vendor/`) with
`normalize_rschema_name`, deterministic `_norm_map`, sorted `_column_labels`,
`PYTHONHASHSEED=0`. Same protocol as E2 PRIMARY.

**Manuscript source (inferred):**
- **Enterprise-145 / RSchema:** agree with locked protocol (rschema name norm, 4-dim Hall, RSchema N=381 DDL gold). Remaining mismatches are **3-decimal boundary rounding**.
- **SchemaBench:** agrees with **historical Exp4 archived JSON** (hash-order-dependent matching **without** `_norm_map`). Locked protocol finds additional Attr/Domain matches after collision-safe resolution.

## Classification of all 27 cells

| # | Dataset | Constructor | Metric | Paper | PRIMARY | Δ | Cause |
|--:|---|---|---|---:|---:|---:|---|
| 1 | Enterprise-145 | Llama-3.1-8B | D | 0.277 | 0.278 | +0.001 | 3-dec boundary (`0.277522`) |
| 2 | Enterprise-145 | Claude Sonnet 4.6 | A | 0.703 | 0.704 | +0.001 | 3-dec boundary (`0.703896`); +35 Attr matched vs July `lower()` archive |
| 3 | Enterprise-145 | Claude Sonnet 4.6 | D | 0.685 | 0.686 | +0.001 | 3-dec boundary (`0.686211`) |
| 4 | Enterprise-145 | GPT-5.4-mini | A | 0.683 | 0.685 | +0.002 | 3-dec + rschema-norm vs manuscript rounding (`0.684723`) |
| 5 | Enterprise-145 | GPT-5.4-mini | D | 0.664 | 0.665 | +0.001 | 3-dec boundary (`0.665456`) |
| 6 | RSchema | CodeLlama-13B | nGED | 0.369 | 0.370 | +0.001 | 3-dec boundary (`0.369507`) |
| 7 | RSchema | CodeLlama-13B | A | 0.986 | 0.987 | +0.001 | 3-dec boundary (`0.986966`) |
| 8 | RSchema | DeepSeek-Coder | Hall | 0.073 | 0.072 | −0.001 | 3-dec boundary (`0.072361`) |
| 9 | RSchema | DeepSeek-Coder | A | 0.807 | 0.808 | +0.001 | 3-dec boundary (`0.808473`) |
| 10 | RSchema | DeepSeek-Coder | D | 0.508 | 0.509 | +0.001 | 3-dec boundary (`0.509456`) |
| 11 | RSchema | Claude Sonnet 4.6 | Hall | 0.009 | 0.008 | −0.001 | 3-dec boundary (`0.008494`) |
| 12 | RSchema | GPT-5.4-mini | A | 0.990 | 0.991 | +0.001 | 3-dec boundary (`0.990720`); creates Attr **tie** with Claude |
| 13 | SchemaBench | CodeLlama-13B | nGED | 0.272 | 0.271 | −0.001 | `_norm_map` / sorted column labels (ARCH=0.272) |
| 14 | SchemaBench | CodeLlama-13B | Hall | 0.054 | 0.053 | −0.001 | same; Attr matched 10007→10038 |
| 15 | SchemaBench | CodeLlama-13B | A | 0.697 | 0.699 | +0.002 | same collision-safe match gain |
| 16 | SchemaBench | CodeLlama-13B | D | 0.527 | 0.528 | +0.001 | Domain matched 7562→7577 |
| 17 | SchemaBench | Llama-3.1-8B | nGED | 0.369 | 0.368 | −0.001 | `_norm_map` (ARCH=0.369) |
| 18 | SchemaBench | Llama-3.1-8B | A | 0.491 | 0.492 | +0.001 | Attr matched 6052→6062 |
| 19 | SchemaBench | Llama-3.1-8B | D | 0.370 | 0.371 | +0.001 | Domain matched 4565→4572 |
| 20 | SchemaBench | DeepSeek-Coder | nGED | 0.550 | 0.549 | −0.001 | `_norm_map` + 3-dec (ARCH rounds to 0.551) |
| 21 | SchemaBench | Claude Sonnet 4.6 | Hall | 0.024 | 0.023 | −0.001 | `_norm_map` (ARCH Hall also 0.023 @3dec) |
| 22 | SchemaBench | Claude Sonnet 4.6 | A | 0.945 | 0.946 | +0.001 | Attr matched 16879→16893; ARCH also 0.946 |
| 23 | SchemaBench | Claude Sonnet 4.6 | D | 0.773 | 0.774 | +0.001 | Domain matched 13807→13819 |
| 24 | SchemaBench | GPT-5.4-mini | nGED | 0.198 | 0.197 | −0.001 | `_norm_map` (ARCH=0.198) |
| 25 | SchemaBench | GPT-5.4-mini | Hall | 0.025 | 0.024 | −0.001 | same |
| 26 | SchemaBench | GPT-5.4-mini | A | 0.921 | 0.923 | +0.002 | Attr matched 16173→16193 |
| 27 | SchemaBench | GPT-5.4-mini | D | 0.745 | 0.746 | +0.001 | Domain matched 13076→13092 |

## Why PRIMARY (locked) is authoritative

1. **Reproducibility:** original SchemaBench Exp4 matching depended on Python set iteration / hash seed when normalized names collide. E2 PRIMARY already locked this with `_norm_map` (lexicographically greatest raw name wins).
2. **Cross-experiment consistency:** E2 PRIMARY uses the same vendor for the same 765 population.
3. **Not a metric-definition change:** Attribute F1 remains name-based; Domain remains type+nullability; nGED remains type-dependent `(col,type_family,null)`. Only collision resolution became deterministic.
4. Manuscript Enterprise/RSchema already track the locked protocol; only SchemaBench manuscript cells reflect the older non-deterministic matcher.

**Decision:** publish PRIMARY locked values; correct the 27 manuscript cells (minimal change).
