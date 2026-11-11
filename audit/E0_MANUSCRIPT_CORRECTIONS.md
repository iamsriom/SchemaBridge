# E0 Minimal Manuscript Corrections (Tables V–VI)

**Basis:** post–parser-repair genuine protocol with comment-prefix CREATE recovery  
(`audit/E0_RECOMMENDED_VALUES.json` = `audit/E0_CURRENT_MANUSCRIPT_VALUES.json`).

**Do not** retain hybrid Exp3 typed-nGED / synthetic-Domain cells for Claude/GPT.  
**Do not** use the intermediate F1–F6-only DeepSeek candidate row (nGED 0.579); that row
dropped columns on `--Foreachtable:CREATE TABLE` lines (fixed; see
`audit/E0_FINAL_PARSER_DIFFERENCE_REPORT.md`).

Paste-ready subsection: `audit/E0_FINAL_SECTION.tex`.

## A. Corrected Table V (3dp from `E0_TABLE_V_FINAL.csv`)

| Dataset | Model | nGED | Hall | T | A | D | E | R |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| RSchema | CodeLlama-13B | 0.583 | 0.669 | 0.554 | 0.414 | 0.115 | 0.301 | 0.141 |
| RSchema | Llama-3.1-8B | 0.615 | 0.696 | 0.572 | 0.377 | 0.121 | 0.199 | 0.104 |
| RSchema | DeepSeek-Coder-6.7B | 0.561 | 0.595 | 0.566 | 0.443 | 0.150 | 0.391 | 0.184 |
| RSchema | Claude Sonnet 4.6 | 0.560 | 0.635 | 0.602 | 0.401 | 0.208 | 0.407 | 0.204 |
| RSchema | GPT-5.4-mini | 0.553 | 0.605 | 0.600 | 0.433 | 0.223 | 0.399 | 0.225 |
| SchemaBench | CodeLlama-13B | 0.794 | 0.773 | 0.350 | 0.125 | 0.067 | 0.183 | 0.082 |
| SchemaBench | Llama-3.1-8B | 0.810 | 0.768 | 0.363 | 0.112 | 0.061 | 0.145 | 0.063 |
| SchemaBench | DeepSeek-Coder-6.7B | 0.731 | 0.641 | 0.398 | 0.185 | 0.100 | 0.240 | 0.128 |
| SchemaBench | Claude Sonnet 4.6 | 0.574 | 0.598 | 0.530 | 0.358 | 0.247 | 0.345 | 0.263 |
| SchemaBench | GPT-5.4-mini | 0.675 | 0.651 | 0.465 | 0.245 | 0.159 | 0.255 | 0.174 |

## B. Table VI Direct = Table V RSchema; prompting = ARCHIVE

See `audit/E0_FINAL_SECTION.tex` Table `tab:e0_baselines`. Prompting nGED is historical macro mean.

## C. Claim check

| Claim | Verdict |
|---|---|
| Requirements under-specify constraints | Supported (max Ref 0.263; Domain ≪ Tables) |
| No model exceeds ~0.27 referential F1 | Supported |
| DeepSeek strong among open-weight | Supported (best open Hall/Attr on RSchema; nGED 0.561) |
| Claude strong on SchemaBench | Supported (best on all columns) |
| Few-shot beats Direct on same nGED | **Not claimable** until names-only regen |
| One-shot CoT hurts structural F1 | Directionally supported by archive micro F1 |
