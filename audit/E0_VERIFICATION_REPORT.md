# E0 Verification Report

**Branch intent:** `icde2027-e0-verified`
**Scope:** Tables V–VI only (E0 Text2Schema).
**Rule:** Current manuscript targets from `audit/E0_CURRENT_MANUSCRIPT_VALUES.json`; older `configs/paper_reference_values.json` is **not** the acceptance target.

## Executive verdict

- Table V (70 cells): **PASS=29**, **MISMATCH=41**, **BLOCKED=0**
- Table VI (84 cells): **PASS=12**, **MISMATCH=9**, **BLOCKED=63**
- Offline Direct recompute is **deterministic** (two consecutive runs identical).
- PaperMethods baseline prediction trees are **missing** → Table VI prompting rows **BLOCKED** for independent re-scoring.
- Scientifically recommended Table V numbers are the **genuine-protocol recomputation** in `results/metrics/reproduced/E0_TABLE_V_FINAL.csv`.

## Protocol verified in code

| Item | Implementation | Match to current manuscript text |
|---|---|---|
| Structural F1 micro over T/A/D/E/R | `src/metrics.py` + `reproduce_genuine_tables.py` | Yes |
| Identifier normalization | lowercasing; strip quotes/spaces/`_`/`-` | Yes |
| RSchema Domain on 381 DDL IDs | `annotation_ddl.jsonl` intersection | Yes |
| No synthetic VARCHAR Domain gold | genuine DDL only | Yes |
| Hallucination 4-dim mean T/A/E/R | Domain excluded; empty P→0 | Yes |
| E0 nGED names-only | `names_only=True` | Yes |
| Empty prediction failure policy | nGED=1; Hall not forced to 1 | Yes |
| Baseline Domain | `--` | Yes (when baselines available) |
| Data leakage check | constructor receives NL `question` only | Yes |

## Prediction recovery

### Direct

| Dataset | Model | Present | Matches original tree | Status |
|---|---|---:|---|---|
| RSchema | CodeLlama-13B | 518/518 | True | ORIGINAL |
| RSchema | Llama-3.1-8B | 518/518 | True | ORIGINAL |
| RSchema | DeepSeek-Coder-6.7B | 518/518 | True | ORIGINAL |
| RSchema | Claude Sonnet 4.6 | 518/518 | True | ORIGINAL |
| RSchema | GPT-5.4-mini | 518/518 | True | ORIGINAL |
| SchemaBench | CodeLlama-13B | 239/239 | True | ORIGINAL |
| SchemaBench | Llama-3.1-8B | 239/239 | True | ORIGINAL |
| SchemaBench | DeepSeek-Coder-6.7B | 239/239 | True | ORIGINAL |
| SchemaBench | Claude Sonnet 4.6 | 239/239 | True | ORIGINAL |
| SchemaBench | GPT-5.4-mini | 239/239 | True | ORIGINAL |

### Baselines (PaperMethods)

| Model | Method | PaperMethods present | Near-miss v2 lines | Usable for Table VI |
|---|---|---|---:|---|
| CodeLlama-13B | one_shot | False | 518 | False |
| CodeLlama-13B | one_shot_cot | False | 518 | False |
| CodeLlama-13B | few_shot | False | 518 | False |
| Llama-3.1-8B | one_shot | False | 518 | False |
| Llama-3.1-8B | one_shot_cot | False | 518 | False |
| Llama-3.1-8B | few_shot | False | 518 | False |
| DeepSeek-Coder-6.7B | one_shot | False | 518 | False |
| DeepSeek-Coder-6.7B | one_shot_cot | False | 518 | False |
| DeepSeek-Coder-6.7B | few_shot | False | 518 | False |

## Table V cell comparison

Recomputed with: `python3 experiments/E0/reproduce_genuine_tables.py`

| Dataset | Model | Metric | Paper | Recomputed | Round3 | Diff | Status |
|---|---|---|---:|---:|---:|---:|---|
| RSchema | CodeLlama-13B | nged | 0.583 | 0.583048 | 0.583 | +0.000048 | PASS |
| RSchema | CodeLlama-13B | halluc | 0.669 | 0.668598 | 0.669 | -0.000402 | PASS |
| RSchema | CodeLlama-13B | tables | 0.554 | 0.553864 | 0.554 | -0.000136 | PASS |
| RSchema | CodeLlama-13B | attributes | 0.414 | 0.414443 | 0.414 | +0.000443 | PASS |
| RSchema | CodeLlama-13B | domain | 0.115 | 0.114962 | 0.115 | -0.000038 | PASS |
| RSchema | CodeLlama-13B | entity | 0.301 | 0.300543 | 0.301 | -0.000457 | PASS |
| RSchema | CodeLlama-13B | referential | 0.140 | 0.139797 | 0.140 | -0.000203 | PASS |
| RSchema | Llama-3.1-8B | nged | 0.628 | 0.636531 | 0.637 | +0.008531 | MISMATCH |
| RSchema | Llama-3.1-8B | halluc | 0.695 | 0.690834 | 0.691 | -0.004166 | MISMATCH |
| RSchema | Llama-3.1-8B | tables | 0.572 | 0.553957 | 0.554 | -0.018043 | MISMATCH |
| RSchema | Llama-3.1-8B | attributes | 0.363 | 0.362929 | 0.363 | -0.000071 | PASS |
| RSchema | Llama-3.1-8B | domain | 0.113 | 0.115808 | 0.116 | +0.002808 | MISMATCH |
| RSchema | Llama-3.1-8B | entity | 0.191 | 0.190616 | 0.191 | -0.000384 | PASS |
| RSchema | Llama-3.1-8B | referential | 0.090 | 0.090200 | 0.090 | +0.000200 | PASS |
| RSchema | DeepSeek-Coder-6.7B | nged | 0.562 | 0.561173 | 0.561 | -0.000827 | MISMATCH |
| RSchema | DeepSeek-Coder-6.7B | halluc | 0.595 | 0.594497 | 0.594 | -0.000503 | MISMATCH |
| RSchema | DeepSeek-Coder-6.7B | tables | 0.566 | 0.566998 | 0.567 | +0.000998 | MISMATCH |
| RSchema | DeepSeek-Coder-6.7B | attributes | 0.441 | 0.442319 | 0.442 | +0.001319 | MISMATCH |
| RSchema | DeepSeek-Coder-6.7B | domain | 0.149 | 0.149578 | 0.150 | +0.000578 | MISMATCH |
| RSchema | DeepSeek-Coder-6.7B | entity | 0.389 | 0.389425 | 0.389 | +0.000425 | PASS |
| RSchema | DeepSeek-Coder-6.7B | referential | 0.183 | 0.182785 | 0.183 | -0.000215 | PASS |
| RSchema | Claude Sonnet 4.6 | nged | 0.780 | 0.560110 | 0.560 | -0.219890 | MISMATCH |
| RSchema | Claude Sonnet 4.6 | halluc | 0.687 | 0.634103 | 0.634 | -0.052897 | MISMATCH |
| RSchema | Claude Sonnet 4.6 | tables | 0.602 | 0.602117 | 0.602 | +0.000117 | PASS |
| RSchema | Claude Sonnet 4.6 | attributes | 0.400 | 0.401247 | 0.401 | +0.001247 | MISMATCH |
| RSchema | Claude Sonnet 4.6 | domain | 0.123 | 0.208065 | 0.208 | +0.085065 | MISMATCH |
| RSchema | Claude Sonnet 4.6 | entity | 0.407 | 0.406880 | 0.407 | -0.000120 | PASS |
| RSchema | Claude Sonnet 4.6 | referential | 0.201 | 0.202625 | 0.203 | +0.001625 | MISMATCH |
| RSchema | GPT-5.4-mini | nged | 0.777 | 0.553126 | 0.553 | -0.223874 | MISMATCH |
| RSchema | GPT-5.4-mini | halluc | 0.660 | 0.604860 | 0.605 | -0.055140 | MISMATCH |
| RSchema | GPT-5.4-mini | tables | 0.600 | 0.600489 | 0.600 | +0.000489 | PASS |
| RSchema | GPT-5.4-mini | attributes | 0.433 | 0.433385 | 0.433 | +0.000385 | PASS |
| RSchema | GPT-5.4-mini | domain | 0.133 | 0.222830 | 0.223 | +0.089830 | MISMATCH |
| RSchema | GPT-5.4-mini | entity | 0.399 | 0.399414 | 0.399 | +0.000414 | PASS |
| RSchema | GPT-5.4-mini | referential | 0.221 | 0.224765 | 0.225 | +0.003765 | MISMATCH |
| SchemaBench | CodeLlama-13B | nged | 0.795 | 0.795215 | 0.795 | +0.000215 | PASS |
| SchemaBench | CodeLlama-13B | halluc | 0.777 | 0.776746 | 0.777 | -0.000254 | PASS |
| SchemaBench | CodeLlama-13B | tables | 0.351 | 0.350751 | 0.351 | -0.000249 | PASS |
| SchemaBench | CodeLlama-13B | attributes | 0.126 | 0.125547 | 0.126 | -0.000453 | PASS |
| SchemaBench | CodeLlama-13B | domain | 0.067 | 0.066643 | 0.067 | -0.000357 | PASS |
| SchemaBench | CodeLlama-13B | entity | 0.184 | 0.184275 | 0.184 | +0.000275 | PASS |
| SchemaBench | CodeLlama-13B | referential | 0.081 | 0.080729 | 0.081 | -0.000271 | PASS |
| SchemaBench | Llama-3.1-8B | nged | 0.813 | 0.820570 | 0.821 | +0.007570 | MISMATCH |
| SchemaBench | Llama-3.1-8B | halluc | 0.769 | 0.768364 | 0.768 | -0.000636 | MISMATCH |
| SchemaBench | Llama-3.1-8B | tables | 0.365 | 0.342080 | 0.342 | -0.022920 | MISMATCH |
| SchemaBench | Llama-3.1-8B | attributes | 0.106 | 0.106320 | 0.106 | +0.000320 | PASS |
| SchemaBench | Llama-3.1-8B | domain | 0.057 | 0.057337 | 0.057 | +0.000337 | PASS |
| SchemaBench | Llama-3.1-8B | entity | 0.140 | 0.139523 | 0.140 | -0.000477 | PASS |
| SchemaBench | Llama-3.1-8B | referential | 0.061 | 0.060707 | 0.061 | -0.000293 | PASS |
| SchemaBench | DeepSeek-Coder-6.7B | nged | 0.747 | 0.746051 | 0.746 | -0.000949 | MISMATCH |
| SchemaBench | DeepSeek-Coder-6.7B | halluc | 0.653 | 0.652773 | 0.653 | -0.000227 | PASS |
| SchemaBench | DeepSeek-Coder-6.7B | tables | 0.401 | 0.397267 | 0.397 | -0.003733 | MISMATCH |
| SchemaBench | DeepSeek-Coder-6.7B | attributes | 0.150 | 0.151341 | 0.151 | +0.001341 | MISMATCH |
| SchemaBench | DeepSeek-Coder-6.7B | domain | 0.080 | 0.080853 | 0.081 | +0.000853 | MISMATCH |
| SchemaBench | DeepSeek-Coder-6.7B | entity | 0.216 | 0.217054 | 0.217 | +0.001054 | MISMATCH |
| SchemaBench | DeepSeek-Coder-6.7B | referential | 0.129 | 0.130742 | 0.131 | +0.001742 | MISMATCH |
| SchemaBench | Claude Sonnet 4.6 | nged | 0.685 | 0.610905 | 0.611 | -0.074095 | MISMATCH |
| SchemaBench | Claude Sonnet 4.6 | halluc | 0.643 | 0.624541 | 0.625 | -0.018459 | MISMATCH |
| SchemaBench | Claude Sonnet 4.6 | tables | 0.530 | 0.520910 | 0.521 | -0.009090 | MISMATCH |
| SchemaBench | Claude Sonnet 4.6 | attributes | 0.278 | 0.267898 | 0.268 | -0.010102 | MISMATCH |
| SchemaBench | Claude Sonnet 4.6 | domain | 0.192 | 0.172182 | 0.172 | -0.019818 | MISMATCH |
| SchemaBench | Claude Sonnet 4.6 | entity | 0.345 | 0.284882 | 0.285 | -0.060118 | MISMATCH |
| SchemaBench | Claude Sonnet 4.6 | referential | 0.264 | 0.255243 | 0.255 | -0.008757 | MISMATCH |
| SchemaBench | GPT-5.4-mini | nged | 0.760 | 0.685317 | 0.685 | -0.074683 | MISMATCH |
| SchemaBench | GPT-5.4-mini | halluc | 0.685 | 0.665684 | 0.666 | -0.019316 | MISMATCH |
| SchemaBench | GPT-5.4-mini | tables | 0.466 | 0.463734 | 0.464 | -0.002266 | MISMATCH |
| SchemaBench | GPT-5.4-mini | attributes | 0.217 | 0.219543 | 0.220 | +0.002543 | MISMATCH |
| SchemaBench | GPT-5.4-mini | domain | 0.144 | 0.135175 | 0.135 | -0.008825 | MISMATCH |
| SchemaBench | GPT-5.4-mini | entity | 0.255 | 0.241083 | 0.241 | -0.013917 | MISMATCH |
| SchemaBench | GPT-5.4-mini | referential | 0.175 | 0.171441 | 0.171 | -0.003559 | MISMATCH |

### Recommended scientifically justified Table V (genuine protocol)

| Dataset | Model | nGED | Hall | T | A | D | E | R |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| RSchema | CodeLlama-13B | 0.583 | 0.669 | 0.554 | 0.414 | 0.115 | 0.301 | 0.140 |
| RSchema | Llama-3.1-8B | 0.637 | 0.691 | 0.554 | 0.363 | 0.116 | 0.191 | 0.090 |
| RSchema | DeepSeek-Coder-6.7B | 0.561 | 0.594 | 0.567 | 0.442 | 0.150 | 0.389 | 0.183 |
| RSchema | Claude Sonnet 4.6 | 0.560 | 0.634 | 0.602 | 0.401 | 0.208 | 0.407 | 0.203 |
| RSchema | GPT-5.4-mini | 0.553 | 0.605 | 0.600 | 0.433 | 0.223 | 0.399 | 0.225 |
| SchemaBench | CodeLlama-13B | 0.795 | 0.777 | 0.351 | 0.126 | 0.067 | 0.184 | 0.081 |
| SchemaBench | Llama-3.1-8B | 0.821 | 0.768 | 0.342 | 0.106 | 0.057 | 0.140 | 0.061 |
| SchemaBench | DeepSeek-Coder-6.7B | 0.746 | 0.653 | 0.397 | 0.151 | 0.081 | 0.217 | 0.131 |
| SchemaBench | Claude Sonnet 4.6 | 0.611 | 0.625 | 0.521 | 0.268 | 0.172 | 0.285 | 0.255 |
| SchemaBench | GPT-5.4-mini | 0.685 | 0.666 | 0.464 | 0.220 | 0.135 | 0.241 | 0.171 |

### Substantive mismatch notes (Table V)

1. **CodeLlama (both datasets):** all 14 cells PASS — manuscript CodeLlama rows match the genuine protocol.
2. **Llama-3.1 Tables/nGED:** manuscript Tables 0.572 / nGED 0.628 still track the older Exp3 archive mixed with some genuine Attr/Entity cells (**hybrid row**). Genuine: Tables 0.554, nGED 0.637 (RSchema).
3. **Claude / GPT-5.4-mini RSchema nGED/Hall/Domain:** manuscript values match the old Exp3 evaluator; genuine recompute yields nGED ~0.55–0.56 and Domain ~0.21–0.22.
4. **SchemaBench Claude/GPT:** broader structural deltas under the corrected parser versus the June-2026 Exp4 report.
5. **DeepSeek:** small 3dp / parser deltas on several cells; Entity/Referential mostly PASS on RSchema.

## Table VI cell comparison

| Dataset | Model | Method | Metric | Paper | Recomputed | Diff | Status |
|---|---|---|---|---:|---:|---:|---|
| RSchema | CodeLlama-13B | One-shot | nged | 0.613 | -- | -- | BLOCKED |
| RSchema | CodeLlama-13B | One-shot | halluc | 0.728 | -- | -- | BLOCKED |
| RSchema | CodeLlama-13B | One-shot | tables | 0.587 | -- | -- | BLOCKED |
| RSchema | CodeLlama-13B | One-shot | attributes | 0.379 | -- | -- | BLOCKED |
| RSchema | CodeLlama-13B | One-shot | domain | -- | -- | -- | BLOCKED |
| RSchema | CodeLlama-13B | One-shot | entity | 0.130 | -- | -- | BLOCKED |
| RSchema | CodeLlama-13B | One-shot | referential | 0.034 | -- | -- | BLOCKED |
| RSchema | CodeLlama-13B | One-shot+CoT | nged | 0.668 | -- | -- | BLOCKED |
| RSchema | CodeLlama-13B | One-shot+CoT | halluc | 0.737 | -- | -- | BLOCKED |
| RSchema | CodeLlama-13B | One-shot+CoT | tables | 0.580 | -- | -- | BLOCKED |
| RSchema | CodeLlama-13B | One-shot+CoT | attributes | 0.344 | -- | -- | BLOCKED |
| RSchema | CodeLlama-13B | One-shot+CoT | domain | -- | -- | -- | BLOCKED |
| RSchema | CodeLlama-13B | One-shot+CoT | entity | 0.047 | -- | -- | BLOCKED |
| RSchema | CodeLlama-13B | One-shot+CoT | referential | 0.004 | -- | -- | BLOCKED |
| RSchema | CodeLlama-13B | Few-shot | nged | 0.540 | -- | -- | BLOCKED |
| RSchema | CodeLlama-13B | Few-shot | halluc | 0.589 | -- | -- | BLOCKED |
| RSchema | CodeLlama-13B | Few-shot | tables | 0.600 | -- | -- | BLOCKED |
| RSchema | CodeLlama-13B | Few-shot | attributes | 0.461 | -- | -- | BLOCKED |
| RSchema | CodeLlama-13B | Few-shot | domain | -- | -- | -- | BLOCKED |
| RSchema | CodeLlama-13B | Few-shot | entity | 0.355 | -- | -- | BLOCKED |
| RSchema | CodeLlama-13B | Few-shot | referential | 0.118 | -- | -- | BLOCKED |
| RSchema | CodeLlama-13B | Direct | nged | 0.583 | 0.583048 | +0.000048 | PASS |
| RSchema | CodeLlama-13B | Direct | halluc | 0.669 | 0.668598 | -0.000402 | PASS |
| RSchema | CodeLlama-13B | Direct | tables | 0.554 | 0.553864 | -0.000136 | PASS |
| RSchema | CodeLlama-13B | Direct | attributes | 0.414 | 0.414443 | +0.000443 | PASS |
| RSchema | CodeLlama-13B | Direct | domain | 0.115 | 0.114962 | -0.000038 | PASS |
| RSchema | CodeLlama-13B | Direct | entity | 0.301 | 0.300543 | -0.000457 | PASS |
| RSchema | CodeLlama-13B | Direct | referential | 0.140 | 0.139797 | -0.000203 | PASS |
| RSchema | Llama-3.1-8B | One-shot | nged | 0.602 | -- | -- | BLOCKED |
| RSchema | Llama-3.1-8B | One-shot | halluc | 0.714 | -- | -- | BLOCKED |
| RSchema | Llama-3.1-8B | One-shot | tables | 0.564 | -- | -- | BLOCKED |
| RSchema | Llama-3.1-8B | One-shot | attributes | 0.399 | -- | -- | BLOCKED |
| RSchema | Llama-3.1-8B | One-shot | domain | -- | -- | -- | BLOCKED |
| RSchema | Llama-3.1-8B | One-shot | entity | 0.221 | -- | -- | BLOCKED |
| RSchema | Llama-3.1-8B | One-shot | referential | 0.086 | -- | -- | BLOCKED |
| RSchema | Llama-3.1-8B | One-shot+CoT | nged | 0.670 | -- | -- | BLOCKED |
| RSchema | Llama-3.1-8B | One-shot+CoT | halluc | 0.764 | -- | -- | BLOCKED |
| RSchema | Llama-3.1-8B | One-shot+CoT | tables | 0.553 | -- | -- | BLOCKED |
| RSchema | Llama-3.1-8B | One-shot+CoT | attributes | 0.334 | -- | -- | BLOCKED |
| RSchema | Llama-3.1-8B | One-shot+CoT | domain | -- | -- | -- | BLOCKED |
| RSchema | Llama-3.1-8B | One-shot+CoT | entity | 0.067 | -- | -- | BLOCKED |
| RSchema | Llama-3.1-8B | One-shot+CoT | referential | 0.020 | -- | -- | BLOCKED |
| RSchema | Llama-3.1-8B | Few-shot | nged | 0.547 | -- | -- | BLOCKED |
| RSchema | Llama-3.1-8B | Few-shot | halluc | 0.638 | -- | -- | BLOCKED |
| RSchema | Llama-3.1-8B | Few-shot | tables | 0.585 | -- | -- | BLOCKED |
| RSchema | Llama-3.1-8B | Few-shot | attributes | 0.461 | -- | -- | BLOCKED |
| RSchema | Llama-3.1-8B | Few-shot | domain | -- | -- | -- | BLOCKED |
| RSchema | Llama-3.1-8B | Few-shot | entity | 0.373 | -- | -- | BLOCKED |
| RSchema | Llama-3.1-8B | Few-shot | referential | 0.146 | -- | -- | BLOCKED |
| RSchema | Llama-3.1-8B | Direct | nged | 0.628 | 0.636531 | +0.008531 | MISMATCH |
| RSchema | Llama-3.1-8B | Direct | halluc | 0.695 | 0.690834 | -0.004166 | MISMATCH |
| RSchema | Llama-3.1-8B | Direct | tables | 0.572 | 0.553957 | -0.018043 | MISMATCH |
| RSchema | Llama-3.1-8B | Direct | attributes | 0.363 | 0.362929 | -0.000071 | PASS |
| RSchema | Llama-3.1-8B | Direct | domain | 0.113 | 0.115808 | +0.002808 | MISMATCH |
| RSchema | Llama-3.1-8B | Direct | entity | 0.191 | 0.190616 | -0.000384 | PASS |
| RSchema | Llama-3.1-8B | Direct | referential | 0.090 | 0.090200 | +0.000200 | PASS |
| RSchema | DeepSeek-Coder-6.7B | One-shot | nged | 0.718 | -- | -- | BLOCKED |
| RSchema | DeepSeek-Coder-6.7B | One-shot | halluc | 0.722 | -- | -- | BLOCKED |
| RSchema | DeepSeek-Coder-6.7B | One-shot | tables | 0.406 | -- | -- | BLOCKED |
| RSchema | DeepSeek-Coder-6.7B | One-shot | attributes | 0.321 | -- | -- | BLOCKED |
| RSchema | DeepSeek-Coder-6.7B | One-shot | domain | -- | -- | -- | BLOCKED |
| RSchema | DeepSeek-Coder-6.7B | One-shot | entity | 0.246 | -- | -- | BLOCKED |
| RSchema | DeepSeek-Coder-6.7B | One-shot | referential | 0.115 | -- | -- | BLOCKED |
| RSchema | DeepSeek-Coder-6.7B | One-shot+CoT | nged | 0.848 | -- | -- | BLOCKED |
| RSchema | DeepSeek-Coder-6.7B | One-shot+CoT | halluc | 0.838 | -- | -- | BLOCKED |
| RSchema | DeepSeek-Coder-6.7B | One-shot+CoT | tables | 0.251 | -- | -- | BLOCKED |
| RSchema | DeepSeek-Coder-6.7B | One-shot+CoT | attributes | 0.169 | -- | -- | BLOCKED |
| RSchema | DeepSeek-Coder-6.7B | One-shot+CoT | domain | -- | -- | -- | BLOCKED |
| RSchema | DeepSeek-Coder-6.7B | One-shot+CoT | entity | 0.091 | -- | -- | BLOCKED |
| RSchema | DeepSeek-Coder-6.7B | One-shot+CoT | referential | 0.046 | -- | -- | BLOCKED |
| RSchema | DeepSeek-Coder-6.7B | Few-shot | nged | 0.528 | -- | -- | BLOCKED |
| RSchema | DeepSeek-Coder-6.7B | Few-shot | halluc | 0.582 | -- | -- | BLOCKED |
| RSchema | DeepSeek-Coder-6.7B | Few-shot | tables | 0.600 | -- | -- | BLOCKED |
| RSchema | DeepSeek-Coder-6.7B | Few-shot | attributes | 0.479 | -- | -- | BLOCKED |
| RSchema | DeepSeek-Coder-6.7B | Few-shot | domain | -- | -- | -- | BLOCKED |
| RSchema | DeepSeek-Coder-6.7B | Few-shot | entity | 0.419 | -- | -- | BLOCKED |
| RSchema | DeepSeek-Coder-6.7B | Few-shot | referential | 0.188 | -- | -- | BLOCKED |
| RSchema | DeepSeek-Coder-6.7B | Direct | nged | 0.562 | 0.561173 | -0.000827 | MISMATCH |
| RSchema | DeepSeek-Coder-6.7B | Direct | halluc | 0.595 | 0.594497 | -0.000503 | MISMATCH |
| RSchema | DeepSeek-Coder-6.7B | Direct | tables | 0.566 | 0.566998 | +0.000998 | MISMATCH |
| RSchema | DeepSeek-Coder-6.7B | Direct | attributes | 0.441 | 0.442319 | +0.001319 | MISMATCH |
| RSchema | DeepSeek-Coder-6.7B | Direct | domain | 0.149 | 0.149578 | +0.000578 | MISMATCH |
| RSchema | DeepSeek-Coder-6.7B | Direct | entity | 0.389 | 0.389425 | +0.000425 | PASS |
| RSchema | DeepSeek-Coder-6.7B | Direct | referential | 0.183 | 0.182785 | -0.000215 | PASS |

### Table VI notes

- **Prompting methods BLOCKED:** original PaperMethods `results.jsonl` trees are not on disk. Do not substitute `prompt_conditions_v2`.
- Archived aggregate JSON retains historical macro scores and micro G/P/M counts but cannot replace per-schema re-scoring under the final protocol.
- **Direct rows** must equal Table V RSchema; Table VI Direct mismatches mirror Table V mismatches.

## Independent checks

- Built-in 10-schema seed=42 validation: PASS.
- `pytest`: 215 passed.
- Two full offline recomputes: identical Table V metrics.

## Remaining blockers / smallest fixes

1. Recover PaperMethods prediction trees from external backup → `results/predictions/e0/rschema_papermethods/<model>/<method>/results.jsonl` → re-run reproduce script.
2. Update manuscript Table V to `E0_TABLE_V_FINAL.csv` (or document intentional hybrid cells).
3. Align Table VI Direct rows with corrected Table V RSchema rows after (2).
4. Do **not** mark E0 COMPLETE while baseline trees are missing or hybrid manuscript cells remain unexplained.
