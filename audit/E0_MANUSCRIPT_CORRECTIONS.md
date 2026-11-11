# E0 Minimal Manuscript Corrections (Tables V–VI)

**Basis:** post–parser-repair genuine protocol (`audit/E0_RECOMMENDED_VALUES.json`).  
**Do not** retain hybrid Exp3 typed-nGED / synthetic-Domain cells for Claude/GPT.

## A. Corrected Table V (LaTeX)

```latex
% tab:e0_overall — values from E0_TABLE_V_FINAL.csv (parser F1–F6 fixed), rounded to 3dp
\begin{tabular}{llccccccc}
\toprule
Dataset & Model & nGED$\downarrow$ & Hall.$\downarrow$ & T & A & D & E & R \\
\midrule
\multirow{5}{*}{RSchema}
 & CodeLlama-13B & 0.583 & 0.669 & 0.554 & 0.414 & 0.115 & 0.301 & 0.141 \\
 & Llama-3.1-8B & 0.615 & 0.696 & 0.572 & 0.377 & 0.121 & 0.199 & 0.104 \\
 & DeepSeek-Coder-6.7B & 0.579 & 0.594 & 0.566 & 0.427 & 0.146 & 0.377 & 0.177 \\
 & Claude Sonnet 4.6 & 0.560 & 0.635 & 0.602 & 0.401 & 0.208 & 0.407 & 0.204 \\
 & GPT-5.4-mini & 0.553 & 0.605 & 0.600 & 0.433 & 0.223 & 0.399 & 0.225 \\
\midrule
\multirow{5}{*}{SchemaBench}
 & CodeLlama-13B & 0.794 & 0.773 & 0.350 & 0.125 & 0.067 & 0.183 & 0.082 \\
 & Llama-3.1-8B & 0.810 & 0.768 & 0.363 & 0.112 & 0.061 & 0.145 & 0.063 \\
 & DeepSeek-Coder-6.7B & 0.734 & 0.641 & 0.398 & 0.184 & 0.100 & 0.239 & 0.127 \\
 & Claude Sonnet 4.6 & 0.574 & 0.598 & 0.530 & 0.358 & 0.247 & 0.345 & 0.263 \\
 & GPT-5.4-mini & 0.675 & 0.651 & 0.465 & 0.245 & 0.159 & 0.255 & 0.174 \\
\bottomrule
\end{tabular}
```

Borderline rounding (full precision → 3dp): Claude RS Domain 0.207507→0.208; Llama Hall 0.695508→0.696; CodeLlama Entity 0.300543→0.301.

## B. Corrected Table VI (LaTeX) — Direct rows locked; prompting provisional

Direct rows **must** equal Table V RSchema. Prompting rows below use ARCHIVE_AGGREGATE until `rschema_papermethods_regenerated` completes; replace with REGENERATED_NEW_RUN numbers then.

```latex
% tab:e0_baselines — Domain = -- for untyped prompting methods
\begin{tabular}{lllccccccc}
\toprule
Model & Method & nGED$\downarrow$ & Hall.$\downarrow$ & T & A & D & E & R \\
\midrule
\multirow{4}{*}{CodeLlama-13B}
 & One-shot & 0.613 & 0.727 & 0.587 & 0.378 & -- & 0.130 & 0.035 \\
 & One-shot+CoT & 0.668 & 0.737 & 0.580 & 0.342 & -- & 0.047 & 0.004 \\
 & Few-shot & 0.541 & 0.589 & 0.600 & 0.460 & -- & 0.356 & 0.119 \\
 & Direct & 0.583 & 0.669 & 0.554 & 0.414 & 0.115 & 0.301 & 0.141 \\
\midrule
\multirow{4}{*}{Llama-3.1-8B}
 & One-shot & 0.603 & 0.714 & 0.564 & 0.398 & -- & 0.221 & 0.086 \\
 & One-shot+CoT & 0.670 & 0.765 & 0.553 & 0.332 & -- & 0.067 & 0.020 \\
 & Few-shot & 0.548 & 0.638 & 0.585 & 0.460 & -- & 0.373 & 0.146 \\
 & Direct & 0.615 & 0.696 & 0.572 & 0.377 & 0.121 & 0.199 & 0.104 \\
\midrule
\multirow{4}{*}{DeepSeek-Coder-6.7B}
 & One-shot & 0.720 & 0.723 & 0.406 & 0.318 & -- & 0.246 & 0.115 \\
 & One-shot+CoT & 0.849 & 0.839 & 0.251 & 0.168 & -- & 0.091 & 0.046 \\
 & Few-shot & 0.530 & 0.583 & 0.600 & 0.476 & -- & 0.419 & 0.186 \\
 & Direct & 0.579 & 0.594 & 0.566 & 0.427 & 0.146 & 0.377 & 0.177 \\
\bottomrule
\end{tabular}
```

**Caveat:** Prompting nGED above is the historical **macro** mean from the 2026-10-12 archive — not names-only per-schema nGED. After regeneration, recompute with the same Direct evaluator and update these cells.

## C. Section V-B claim check (against corrected Direct numbers)

| Claim | Verdict with corrected Table V | Action |
|---|---|---|
| NL requirements under-specify structural constraints | **Still supported** — Entity/Referential remain low (max R=0.263 Claude SB; max E=0.407 Claude RS) | Keep; optionally cite corrected R/E |
| No model exceeds 0.27 referential F1 in E0 | **Still true** (max 0.263 SchemaBench Claude; RSchema max 0.225 GPT) | Keep (was 0.27; still holds) |
| DeepSeek relatively strong among open-weight | **Partially weaker** — RSchema nGED 0.579 (best open) but Tables/Attr no longer dominate all columns; SB Attr 0.184 now best open | Soften to “competitive / best open-weight nGED on RSchema” |
| Claude strong on SchemaBench | **Still supported** — best SB nGED 0.574, Hall 0.598, T/A/D/E/R all strongest among five | Keep; update numbers |
| Few-shot improves nGED vs Direct | **Cannot claim under unified names-only nGED** until regenerated trees are scored | Hold / rephrase after regen; archive macro few-shot nGED < Direct but definitions differ |
| One-shot CoT reduces structural fidelity | **Directionally supported by archive micro F1** (T/A/E/R drop vs one-shot) | Keep for F1; avoid nGED comparison until regen |

## D. Abstract sentences

If the abstract cites Claude SB dominance or open-weight ranking from Table V, update numeric mentions to the corrected table. No abstract rewrite required beyond number alignment.

## E. Section III-E metric definitions

Ensure the camera-ready text states explicitly:
1. E0 nGED is **names-only** (tables + table-qualified attributes + directed FKs).
2. Hallucination is the **4-dim** mean over T/A/E/R (Domain excluded).
3. RSchema Domain uses **381 genuine DDL** refs (not synthetic VARCHAR).
4. Inline `PRIMARY KEY … UNIQUE` on one column is counted **once**.

## F. Reproducibility / limitations

Add: “PaperMethods per-schema prediction trees for Table VI prompting baselines were not recovered from the original server. Offline artifact includes ARCHIVE_AGGREGATE pooled counts and a REGENERATED_NEW_RUN campaign under the packaged baseline runner; regenerated runs are not claimed to be bit-identical to the 2026-10-12 PaperMethods trees.”

## Locked reference update

Replace `audit/E0_CURRENT_MANUSCRIPT_VALUES.json` contents with Direct rows from `E0_RECOMMENDED_VALUES.json` once the camera-ready adopts them. Keep the previous hybrid file as `audit/E0_PREVIOUS_HYBRID_MANUSCRIPT_VALUES.json` for provenance.
