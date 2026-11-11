# E0 Manuscript Corrections (minimal; Phase 7)

**Policy:** Prefer genuine-protocol numbers from `results/metrics/reproduced/E0_TABLE_V_FINAL.csv`. Do not change metric definitions to match older hybrid cells.

## Table V — replace with genuine-protocol values

Use three-decimal rounding of `E0_TABLE_V_FINAL.csv` (declared policy: round-half-up style via `f"{x:.3f}"`).

### RSchema

| Constructor | nGED | Hall | T | A | Dom | Ent | Ref |
|---|---:|---:|---:|---:|---:|---:|---:|
| CodeLlama-13B | 0.583 | 0.669 | 0.554 | 0.414 | 0.115 | 0.301 | 0.140 |
| Llama-3.1-8B | **0.637** | **0.691** | **0.554** | 0.363 | **0.116** | 0.191 | 0.090 |
| DeepSeek-Coder-6.7B | **0.561** | **0.594** | **0.567** | **0.442** | **0.150** | 0.389 | 0.183 |
| Claude Sonnet 4.6 | **0.560** | **0.634** | 0.602 | **0.401** | **0.208** | 0.407 | **0.203** |
| GPT-5.4-mini | **0.553** | **0.605** | 0.600 | 0.433 | **0.223** | 0.399 | **0.225** |

Bold = differs from current manuscript cell beyond 3dp/tolerance.

### SchemaBench

| Constructor | nGED | Hall | T | A | Dom | Ent | Ref |
|---|---:|---:|---:|---:|---:|---:|---:|
| CodeLlama-13B | 0.795 | 0.777 | 0.351 | 0.126 | 0.067 | 0.184 | 0.081 |
| Llama-3.1-8B | **0.821** | 0.768 | **0.342** | 0.106 | 0.057 | 0.140 | 0.061 |
| DeepSeek-Coder-6.7B | **0.746** | 0.653 | **0.397** | **0.151** | **0.081** | **0.217** | **0.131** |
| Claude Sonnet 4.6 | **0.611** | **0.625** | **0.521** | **0.268** | **0.172** | **0.285** | **0.255** |
| GPT-5.4-mini | **0.685** | **0.666** | **0.464** | **0.220** | **0.135** | **0.241** | **0.171** |

## Textual edits in §V-B (smallest)

1. **Open-weight ranking:** Keep DeepSeek as strongest open-weight on RSchema nGED/Hall under genuine protocol (0.561 / 0.594). Update any sentence that cites Llama Tables 0.572 — genuine Tables is **0.554**.
2. **Claude / GPT on RSchema:** Manuscript nGED ~0.78 and Domain ~0.12 reflect an older/hybrid evaluator. Under genuine names-only protocol, Claude/GPT nGED is **~0.55–0.56** and Domain **~0.21–0.22**, i.e. **better** structural nGED and Domain than the printed cells. Rewrite ranking statements accordingly.
3. **SchemaBench Claude:** Entity F1 should be **0.285**, not 0.345.
4. **Requirements under-specify schema content:** Still supported (Domain and Ref remain hardest). No change needed beyond numbers.
5. **Table VI Direct rows:** Must mirror corrected Table V RSchema Direct cells after the Table V update.
6. **Few-shot vs Direct / CoT vs one-shot:** Archive-supported qualitative claims can remain, but label Table VI prompting metrics as **archive-aggregate** until per-schema PaperMethods trees are recovered. Do not equate archive macro nGED with names-only Direct nGED without a caveat.

## Do not claim

- That E0 is COMPLETE while PaperMethods trees are missing.
- That recovery workspace Claude/GPT absence invalidates PR trees (PR trees are newer/complete).
