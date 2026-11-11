# E0 Workspace Comparison — Recovery vs GitHub PR #3

**Date:** 2026-11-11
**Recovery:** `/Users/xv76wk/Desktop/Cursor_History_Recovery_20261110_215800/SchemaBridge_E3_patch_repo`
**GitHub worktree:** `/Users/xv76wk/Desktop/research/SchemaBridge-e0-verified` @ `icde2027-e0-verified` (`d0eed4a` prior to this verification pass)
**PR:** https://github.com/iamsriom/SchemaBridge/pull/3 (base `main`, **CONFLICTING**)

## Path discovery

| Candidate | Present? |
|---|---|
| `SchemaBridge_E3_patch_repo/` (recovery) | Yes |
| `~/Desktop/research/SchemaBridge` | Yes (was on `research/e1-e2-reproduction-code`; E0 work uses dedicated worktree) |
| `/data/RSchema_ExpResults4/` | **No** on this host |
| `/data/Text2ER/SchemaBench/` | **No** |
| `/data/LLM4DBdesign/` | **No** |
| `/data/LLM4DBdesign_PaperMethods/` | **No** |

## Classification of key files

| Component | Classification | Notes |
|---|---|---|
| `prompts/constructor.txt` | **IDENTICAL** | SHA-256 `392a396f…4ad4` (matches required hash). Trailing newline vs embedded `SYSTEM_PROMPT` in original Exp4 script (strip-equal). |
| `prompts/e0/direct.txt` | **NEWER_IMPLEMENTATION** (GitHub only) | Byte-identical to `constructor.txt`. |
| `prompts/e0/{one_shot,one_shot_cot,few_shot}.txt` | **NEWER_IMPLEMENTATION** (GitHub only) | PaperMethods prompt texts recovered into PR; absent from recovery checkout. |
| `src/metrics.py` | **IDENTICAL** | Shared genuine-protocol metrics. |
| `src/schema_parser.py` | **IDENTICAL** | |
| `src/evaluator.py` | **IDENTICAL** | |
| `src/normalization.py` | **IDENTICAL** | |
| `experiments/E0/evaluate.py` | **IDENTICAL** | |
| `experiments/E0/run_direct_api.py` | **IDENTICAL** | Closed Direct API (temp 0.2 / 4096); not used for historical open Exp4 trees. |
| `experiments/E0/config.yaml` | **IDENTICAL** | |
| `experiments/E0/reproduce_genuine_tables.py` | **NEWER_IMPLEMENTATION** (GitHub) | +164 lines vs recovery: `ARCHIVE_AGGREGATE` PaperMethods fallback from pooled G/P/M. |
| `experiments/E0/README.md` | **NEWER_IMPLEMENTATION** (GitHub) | Expanded protocol / status docs. |
| `tests/test_e0_protocol.py` | **IDENTICAL** | |
| `scripts/build_e0_paper_comparison.py` | **NEWER_IMPLEMENTATION** (GitHub only) | Had Domain-branch comparator defect (Direct Domain forced to `--`); fixed in this pass. |
| `scripts/reproduce_e0_offline.sh` | **NEWER_IMPLEMENTATION** (GitHub only) | |
| `audit/E0_VERIFICATION_REPORT.md` + paper comparison artifacts | **NEWER_IMPLEMENTATION** (GitHub only) | Recovery's `audit/E0_reproduction.md` is older PARTIAL narrative. |
| `src/prompt_assets.py` | **OLDER_IMPLEMENTATION** / recovery-only | Not required by current E0 entry points (`run_direct_api` loads `prompts/constructor.txt` directly). Do **not** copy blindly. |
| `experiments/E0/original_benchmarks/**` | **NEWER_IMPLEMENTATION** (GitHub only) | Historical Exp4 / PaperMethods code packaged without SchemaAgent multi-agent. |
| Open-weight Direct preds (6 trees) | **IDENTICAL** | Byte-identical JSON trees for CodeLlama/Llama/DeepSeek × RSchema/SchemaBench (0 mismatches). |
| Claude / GPT Direct preds (4 trees) | **NEWER_IMPLEMENTATION** (GitHub only) | Recovery incorrectly described these as missing/BLOCKED; PR has full 518+239. **Do not overwrite with recovery.** |
| Datasets `annotation*.jsonl` | **IDENTICAL counts** | RSchema 518 / 381; SchemaBench 239. |

## Transcript evidence (historical; not executable proof)

| Extract | Useful for |
|---|---|
| `20260616_*_NL_questions_schema_generation.txt` | RSchema Exp4 HF run; greedy `do_sample=False` when temp≤0.1; `max_new_tokens` 4096→2048 mid-run; SYSTEM_PROMPT from `text2schema_allLLM.py`. |
| `20260617_*_Natural_language_to_schema_conversion.txt` | SchemaBench Experiment2 text2schema (239). |
| `20260707_*_Schema_to_text_prompts.txt` | Constructor + describer prompt recovery. |
| `20260927_*_Text_to_schema_results.txt` | PaperMethods one-shot/CoT/few-shot narratives; per-schema trees still missing. |

## What recovery should / should not contribute

**Useful from recovery (evidence only):**
- Transcript provenance for decoding settings and prompt lineage.
- Confirmation that open-weight trees match GitHub (already identical).
- Older `E0_reproduction.md` as a historical status snapshot.

**Superseded / do not reintroduce:**
- Claim that Claude/GPT E0 preds are absent.
- Older `reproduce_genuine_tables.py` without archive-aggregate fallback.
- Copying incomplete prediction sets over PR trees.
- Reintroducing SchemaAgent multi-agent code (correctly excluded).

## Verdict for Phase 1

PR #3 is the authoritative E0 codebase and artifact set. Recovery is a supporting evidence archive. Minimal future diffs should target bugs/tests/docs in the GitHub branch only.
