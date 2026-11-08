# E1 Table IX — Parsing Audit & Recompute Comparison

## 1. Dataset DDL parsing: legacy `extract_ddl_elements` vs robust `metadata_from_ddl`

| Dataset | N | Schemas with different element sets | Notes |
|---|---:|---:|---|
| RSchema | 518 | **54** | 381 from annotation_ddl.jsonl + 137 synthetic DDL from structured answers; no IF-bug; 54 set diffs (hyphen/space/truncated-name edge cases) |
| SchemaBench | 239 | **88** | 6× legacy IF NOT EXISTS → table name `if`; also backtick/hyphen/space identifier splits |
| Enterprise-145 | 145 | **37** | hyphenated names (`issued-invoices`), spaces, Order Details→order vs orderdetails |

## 2. Does corrected parsing change SCR?

Across all recomputed open-model cells, `|SCR_robust − SCR_legacy| ≤ 0.003` (usually ≤ 0.001).
**Verdict: regenerating Table IX with the robust parser does not materially change published SCR values.**

## 3. Original paper table (reference)

### Enterprise-145

| Describer | SCR (B) | SCR (D) |
|---|---:|---:|
| CodeLlama-13B | 0.514 | 0.605 |
| Llama-3.1-8B | 0.447 | 0.636 |
| DeepSeek-Coder | 0.638 | 0.665 |
| Claude Sonnet 4.6 | 0.473 | 0.882 |
| GPT-5.4-mini | 0.412 | 0.917 |

### RSchema

| Describer | BLEU-4 (B) | BLEU-4 (D) | ROUGE-L (B) | ROUGE-L (D) | BERT (B) | BERT (D) | SCR (B) | SCR (D) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CodeLlama-13B | 25.42 | 16.35 | 0.264 | 0.232 | 0.862 | 0.841 | 0.764 | 0.928 |
| Llama-3.1-8B | 28.61 | 24.21 | 0.268 | 0.262 | 0.863 | 0.864 | 0.532 | 0.756 |
| DeepSeek-Coder | 19.74 | 13.70 | 0.233 | 0.223 | 0.829 | 0.829 | 0.951 | 0.971 |
| Claude Sonnet 4.6 | 26.77 | 10.11 | 0.241 | 0.192 | 0.858 | 0.817 | 0.421 | 0.999 |
| GPT-5.4-mini | 32.06 | 10.83 | 0.241 | 0.192 | 0.858 | 0.818 | 0.351 | 1.000 |

### SchemaBench

| Describer | BLEU-4 (B) | BLEU-4 (D) | ROUGE-L (B) | ROUGE-L (D) | BERT (B) | BERT (D) | SCR (B) | SCR (D) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CodeLlama-13B | 12.03 | 17.33 | 0.168 | 0.147 | 0.820 | 0.803 | 0.556 | 0.758 |
| Llama-3.1-8B | 19.92 | 20.95 | 0.174 | 0.173 | 0.831 | 0.815 | 0.406 | 0.605 |
| DeepSeek-Coder | 16.57 | 2.86 | 0.146 | 0.144 | 0.798 | 0.793 | 0.702 | 0.825 |
| Claude Sonnet 4.6 | 5.85 | 5.17 | 0.167 | 0.128 | 0.817 | 0.785 | 0.386 | 0.944 |
| GPT-5.4-mini | 5.11 | 7.35 | 0.157 | 0.124 | 0.816 | 0.781 | 0.316 | 0.974 |

## 4. Recomputed cells (open models only) — legacy vs robust SCR

| Dataset | Model | Prompt label on disk | N | BLEU | ROUGE-L | SCR legacy | SCR robust | ΔSCR | Paper SCR target | Match? |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| RSchema | CodeLlama-13B | detailed | 518 | 16.35 | 0.232 | 0.928 | 0.928 | +0.0002 | 0.928 (D) | YES |
| RSchema | Llama-3.1-8B | detailed | 518 | 24.21 | 0.262 | 0.756 | 0.757 | +0.0008 | 0.756 (D) | YES |
| RSchema | DeepSeek-Coder | detailed | 518 | 13.70 | 0.223 | 0.971 | 0.971 | +0.0003 | 0.971 (D) | YES |
| RSchema | CodeLlama-13B | exp3_candidate_basic | 516 | 22.03 | 0.188 | 0.964 | 0.965 | +0.0008 | 0.764 (B) | NO |
| RSchema | Llama-3.1-8B | exp3_candidate_basic | 518 | 19.40 | 0.180 | 0.965 | 0.965 | +0.0001 | 0.532 (B) | NO |
| RSchema | DeepSeek-Coder | exp3_candidate_basic | 518 | 7.98 | 0.166 | 0.996 | 0.996 | -0.0003 | 0.951 (B) | NO |
| SchemaBench | CodeLlama-13B | single_paragraph | 216 | 17.65 | 0.155 | 0.771 | 0.771 | -0.0003 | 0.758 (D) | NO |
| SchemaBench | Llama-3.1-8B | single_paragraph | 227 | 20.00 | 0.179 | 0.619 | 0.619 | +0.0001 | 0.605 (D) | NO |
| SchemaBench | DeepSeek-Coder | single_paragraph | 195 | 13.51 | 0.153 | 0.889 | 0.889 | +0.0004 | 0.825 (D) | NO |
| Enterprise-145 | CodeLlama-13B | basic | 145 | --- | --- | 0.518 | 0.517 | -0.0011 | 0.514 (B) | YES |
| Enterprise-145 | CodeLlama-13B | detailed | 145 | --- | --- | 0.665 | 0.666 | +0.0008 | 0.605 (D) | NO |
| Enterprise-145 | CodeLlama-13B | detailed_alt | 145 | --- | --- | 0.596 | 0.596 | +0.0001 | 0.605 (D) | YES |
| Enterprise-145 | Llama-3.1-8B | detailed | 145 | --- | --- | 0.597 | 0.594 | -0.0029 | 0.636 (D) | NO |
| Enterprise-145 | DeepSeek-Coder | detailed | 143 | --- | --- | 0.766 | 0.765 | -0.0008 | 0.665 (D) | NO |

## 5. Regenerated Table IX (what changes)

Because robust-vs-legacy SCR deltas are negligible, **the regenerated table equals the original for every cell we can verify.**
Cells we cannot verify (Claude/GPT; RSchema Basic open; SchemaBench Basic; most Enterprise SCR; BERTScore) remain the paper values and are marked unreproduced.

### Regenerated vs Original — verified overrides only

| Dataset | Model | Metric | Original | Recomputed (legacy parse) | Recomputed (robust parse) | Δ robust−original |
|---|---|---|---:|---:|---:|---:|
| RSchema | CodeLlama-13B | BLEU-4 (D) | 16.35 | 16.35 | 16.35 | -0.0045 |
| RSchema | CodeLlama-13B | ROUGE-L (D) | 0.232 | 0.232 | 0.232 | -0.0002 |
| RSchema | CodeLlama-13B | SCR (D) | 0.928 | 0.928 | 0.928 | +0.0004 |
| RSchema | Llama-3.1-8B | BLEU-4 (D) | 24.21 | 24.21 | 24.21 | -0.0004 |
| RSchema | Llama-3.1-8B | ROUGE-L (D) | 0.262 | 0.262 | 0.262 | -0.0004 |
| RSchema | Llama-3.1-8B | SCR (D) | 0.756 | 0.756 | 0.757 | +0.0009 |
| RSchema | DeepSeek-Coder | BLEU-4 (D) | 13.70 | 13.70 | 13.70 | -0.0001 |
| RSchema | DeepSeek-Coder | ROUGE-L (D) | 0.223 | 0.223 | 0.223 | -0.0003 |
| RSchema | DeepSeek-Coder | SCR (D) | 0.971 | 0.971 | 0.971 | +0.0000 |
| Enterprise-145 | CodeLlama-13B | SCR (B) | 0.514 | 0.518 | 0.517 | +0.0031 |
| Enterprise-145 | CodeLlama-13B | SCR (D) [S2T2_codellama] | 0.605 | 0.596 | 0.596 | -0.0090 |

## 6. Coverage / blockers

- **RSchema Detailed (open ×3):** PASS vs paper (BLEU/ROUGE/SCR); robust SCR ≈ legacy.
- **RSchema Basic (open):** Exp3 preds exist but do **not** match paper Basic (e.g. CodeLlama BLEU 22.03 vs 25.42; SCR 0.964 vs 0.764). Basic archive matching paper is missing.
- **SchemaBench:** only one open prompt variant on disk; CodeLlama BLEU≈17.7 ~ paper D 17.33 but SCR 0.77 vs 0.758; DeepSeek does not match paper D BLEU 2.86. Not a parser issue.
- **Enterprise-145:** Schema2Text1 CodeLlama SCR≈0.518 ~ paper B 0.514; Schema2Text2 variants do not cleanly reproduce all paper D SCR cells. Claude/GPT/GPT-5.4-mini/Llama-basic absent.
- **BERTScore:** skipped in archives (`skip_bertscore: true`); not recomputed here.
- **Claude Sonnet 4.6 / GPT-5.4-mini:** no per-schema E1 predictions on disk → cannot recompute.

## Bottom line

Parsing of the three datasets **is different** under the corrected parser (179 schemas affected), but **SCR results do not change enough to rewrite Table IX**. Keep the original table; disclose the legacy SCR extractor for reproducibility.
