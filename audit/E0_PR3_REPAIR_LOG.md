# E0 PR #3 Repair Log

**PR:** https://github.com/iamsriom/SchemaBridge/pull/3  
**Branch:** `icde2027-e0-verified`  
**Base commit at start:** `d0eed4a455aa2a84c0ec42c60b3088aca54fb758`  
**Started:** 2026-11-11

## Phase 1 — Preserve evidence

### Git / merge state
- `mergeable=CONFLICTING`, `mergeStateStatus=DIRTY`.
- `origin/main` has divergent commit `96557da` ("Reproduce E0 Text2Schema inference and evaluation") not in E0 branch.
- Conflicts (merge-tree): `.github/workflows/e0-tests.yml`, `.gitignore`, `experiments/E0/README.md` (and likely more overlapping E0 files).
- Working tree clean at start of repair; no force-push / reset / cleanup of research dirs.
- Historical archives retained under `results/metrics/archived/`, `results/baselines/`, `/data/A_Final_Result/Exp3/`.

### Non-negotiable rules for this repair
- Scientific correctness over manuscript numbers.
- No SchemaAgent multi-agent upload.
- No substitution of `prompt_conditions_v2` for PaperMethods.
- Distinguish VERIFIED_FROM_PREDICTIONS / ARCHIVE / REGENERATED / MISMATCH / BLOCKED.

---

## Investigation entries

(Entries appended chronologically below.)

### 2026-11-11 — Table V mismatch audit (41 cells), no evaluator change

**Task:** classify every `Table=V, Status=MISMATCH` cell (cause codes A–H) and decide whether the current evaluator is scientifically correct. Evaluator was **not** modified to match the manuscript; predictions were **not** regenerated.

**Deliverables**
- `audit/E0_TABLE_V_MISMATCH_CLASSIFICATION.csv` — 41 rows (`Diff_Paper_Genuine = Paper − Genuine`).
- `audit/E0_TABLE_V_DIAGNOSTIC.md` — priority cases with DDL examples, protocol checks, defect list.
- `audit/e0_table_v_mismatch/` — `historical_rerun_cells.csv` (+2 reports), `ablation_waterfall.csv`, `ablation_p1.csv`, `counterfactual_parser_fixes.csv`, `evaluator_at_commit_b626767_table_v.csv`, `sample_schema_crosscheck.csv`.
- `experiments/E0/{audit_table_v_mismatch,audit_counterfactual_run,audit_cf_parser_patch,audit_sample_crosscheck,audit_old_commit_rescore,classify_table_v_mismatches}.py` (offline, read-only on `src/`).
- `tests/test_e0_independent_audit.py` — 7 hand-computed protocol tests (pass) + 9 strict-xfail defect tests (`pytest --runxfail` fails them). Full suite: 218 passed, 9 xfailed.

**Method:** SHA-256 identity of all 7,576 prediction files vs originals (identical) → ran the historical Exp4 evaluators unchanged on those trees (max |Δ| vs archived Exp3 = 0.0017) → toggled the current code one factor at a time (waterfall; end state = `E0_TABLE_V_FINAL.csv` to 5e-7) → counterfactual parser fixes → re-scored Table V with the evaluator at repo commit `b626767`.

**Cause distribution (primary):** A 0 · B 2 · C 14 · D 0 · E 8 · **F 15** · H 2 (= 41). G is a secondary tag on 29 cells (manuscript equals the historical evaluator's output on the same predictions).

**Findings**
1. Protocol items (micro F1, Domain 381/239, Hall4, names-only nGED, empty-prediction policy, macro-mean nGED) are implemented as the manuscript states; independently verified.
2. RSchema Claude/GPT nGED 0.78/0.777, Hall, Domain 0.123/0.133 are **stale Exp3 values** (typed nGED vs synthetic varchar gold; Hall5; Domain vs synthetic 518-schema gold). Per-schema typed nGED is identical in both evaluators (20/20 sampled schemas). Current values are robust to parser defects (≤0.001) → safe to update.
3. Llama / DeepSeek RSchema and Llama SchemaBench manuscript cells equal the evaluator at commit `b626767` (prediction-JSON structure). Commit `257b65d` made DDL authoritative, exposing **F2** (unterminated `CREATE TABLE` bodies swallow later tables: Llama −298 RS tables, −196 SB tables); the current Llama values are wrong, not the protocol.
4. SchemaBench Claude Entity 0.345 vs 0.285: ≈0.053 of the 0.060 gap is **F5** (DDL emitted with literal `\n` → 0 columns/constraints parsed in 19 Claude files), 0.008 is F1–F3; with fixes the current parser reproduces the historical counts (866 vs 865 matched). PK/UNIQUE convention differences (inline PK+UNIQUE counted once vs twice; plain `UNIQUE(...)`, composite PK) are tiny.
5. Genuine parser defects (flagged, **not fixed**): F1 `DEFAULT ''` quote desync (SchemaBench gold loses 75 tables/494 columns), F2 unterminated bodies, F3 hyphenated table names, F4 column names starting `UNIQUE`/`CONSTRAINT`, F5 escaped-newline DDL, F6 `ALTER TABLE … ADD CONSTRAINT FOREIGN KEY` ignored. Also: `legacy=True` is not a faithful historical port (SB gold FKs 1378 vs 2802).

**Verdict:** the evaluator's *protocol* is correct; its *DDL parser* is not yet scientifically correct. Do not treat Genuine values of the 15 F-cells, nor SchemaBench E-cells (further 0.01–0.04 shift), as final until F1–F4 (and F5/F6 policy) are fixed in a separate, test-backed commit.

**Open items:** SchemaBench DeepSeek manuscript row (6 cells, ≤0.004 from genuine) matches no available evaluator state → attributed to a parser revision with low confidence. Historical re-run is `PYTHONHASHSEED`-dependent (±5e-4).

## 2026-11-11 — Parser repair + PR reconciliation (continued)

### Parser defects F1–F6 fixed in `src/schema_parser.py`
- F1: mid-identifier apostrophe requires *immediate* predecessor (DEFAULT '' safe).
- F2: unterminated CREATE TABLE body ends at next header.
- F3: hyphenated/slashed bare table names in headers.
- F4: UNIQUE/CONSTRAINT word-boundary; CHECK requires `(` so Check-in_Time survives.
- F5: unescape literal `\n` when they outnumber real newlines.
- F6: ALTER TABLE … ADD FOREIGN KEY counted.

### Comparison / CI
- Fixed Domain N/A vs numeric logic in `build_e0_paper_comparison.py`.
- Added `--verify` / `--allow-archive` modes.
- CI checks all five Direct models + V↔VI equality + lock.

### Baselines
- Packaged standalone `run_baselines.py` + `_shared/{local_llm_handler,json_extract}.py`.
- Full REGENERATED_NEW_RUN campaign launched (6 GPU wave1: CodeLlama×3 + Llama×3; DeepSeek queued).
- Historical PaperMethods trees still missing; archive provisional for prompting until regen completes.

### Manuscript
- Recommended Direct values locked in `E0_CURRENT_MANUSCRIPT_VALUES.json`.
- Previous hybrid saved as `E0_PREVIOUS_HYBRID_MANUSCRIPT_VALUES.json`.
- Corrections draft: `E0_MANUSCRIPT_CORRECTIONS.md`.

### Merge state
- PR dirty vs `origin/main` (workflow/gitignore/README); merge after this commit.

## 2026-11-11 — Merge + partial-regen guard + lock rounding

- Merged `origin/main` into `icde2027-e0-verified` (`c5e05e1`); conflicts resolved keeping E0 repair tree.
- Bugfix: incomplete `REGENERATED_NEW_RUN` trees must not enter Table VI (would score missing IDs as empty). `evaluate_baseline` now falls back to `ARCHIVE_AGGREGATE` until coverage is complete.
- Relocked manuscript targets with proper 3dp rounding; Claude RSchema Domain 0.207→0.208.
- Wave1 regeneration (CodeLlama×3 + Llama×3) continues on cuda:0–5; DeepSeek queued for after free GPUs (resume from partial jsonl).
- Comparison: VERIFY PASS with `--allow-archive` (100 PASS + 54 PASS_ARCHIVE).
