# E0 Table V mismatch diagnostic

**Audit date:** 2026-11-11 (offline; no predictions regenerated, `src/` not modified)
**Scope:** all 41 `Table=V, Status=MISMATCH` cells of `audit/E0_PAPER_COMPARISON.csv`
**Cell-level result:** `audit/E0_TABLE_V_MISMATCH_CLASSIFICATION.csv` (`Diff_Paper_Genuine = Paper − Genuine`; `Historical` = historical evaluator re-run, Hall = its 5-dimension mean)

## 1. Verdict

| Question | Answer |
|---|---|
| Does the current evaluator implement the manuscript protocol? | **Yes** — micro F1, Domain on 381 DDL refs, Hall4 (T/A/E/R), names-only nGED, empty-prediction policy all confirmed by hand-computed tests (§3). |
| Is it scientifically correct end to end? | **No, not yet.** The *protocol* is right but the DDL *parser* has six genuine defects (F1–F6, §7) that silently drop tables/columns/constraints from gold and predictions. Nine independent failing cases are committed as strict-`xfail` tests. |
| Which mismatches are "paper is stale"? | 10 cells (RSchema Claude/GPT nGED, Hall, Domain; SchemaBench Claude/GPT nGED, Hall). The paper carries the Exp3/Exp4 value, computed with a different metric definition or gold. For the six RSchema cells the current value is robust to every parser defect (≤0.001 shift). |
| Which are "current evaluator is wrong"? | 15 cells (cause **F**): Llama-3.1 both datasets, SchemaBench Claude/GPT structural cells. Fixing the parser moves them toward the paper. |

Cause distribution of the 41 cells (primary technical cause):

| A snapshot | B gold | C parser/normalisation | D aggregation | E metric def. | **F defect** | G stale | H rounding |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 2 | 14 | 0 | 8 | **15** | (29 secondary) | 2 |

`G` is recorded as a *secondary* tag in `Evidence` (`also_G`) whenever the manuscript value equals the historical evaluator's output on the same predictions (29 of 41 cells, tolerance 0.0015 = 3-dp rounding + the vendored evaluator's `PYTHONHASHSEED` tie-break noise).

## 2. Evidence base and what was actually run

| Step | Result |
|---|---|
| Prediction identity | SHA-256 of every file (7,576) in the 10 trees under `results/predictions/e0/{rschema_exp4_*,schemabench_exp2_*}` vs `/data/RSchema_ExpResults4/Experiments/text2schema_*` and `/data/Text2ER/SchemaBench/Experiment2/text2schema_*`: **all identical**. Gold JSONL files (`annotation.jsonl`, `annotation_ddl.jsonl`, SchemaBench `annotation_ddl.jsonl`) are also byte-identical to `/data/RSchema`, `/data/SchemaBench/Dataset`. ⇒ **cause A = 0 for the current trees.** |
| Historical evaluator re-run | `/data/RSchema_ExpResults4/Code/evaluate_exp4_text2schema.py` and `/data/Text2ER/SchemaBench/Code/evaluate_exp4_text2schema.py` run unchanged (`PYTHONHASHSEED=0`) on those trees → `historical_rerun_cells.csv` + two report `.txt`. Max |re-run − archived Exp3 combined| over 70 cells = **0.0017** (mean 0.0004; hash-order noise). So the archive *is* the historical evaluator on these snapshots. |
| Archive staleness | `results/metrics/archived/e0_rschema_exp4_evaluation.json` (2026-06-15, only 3 LLMs) is an older snapshot: Llama nGED 0.7751 vs 0.7643 now, CodeLlama Entity 0.278 vs 0.301. The paper does **not** use these (it uses the 2026-06-28 Exp3 numbers). |
| Current-code waterfall | `ablation_waterfall.csv`: current code toggled one factor at a time (W2 typed/Hall5/synthetic Domain → W3 names-only nGED → W4 Domain-DDL gold → W5 Hall4). W5 reproduces `E0_TABLE_V_FINAL.csv` to 5e-7 for all 70 cells. |
| Paper-protocol hypothesis P1 | `ablation_p1.csv`: genuine protocol, but prediction structure taken from the prediction JSON `metadata` (the pre-DDL-authoritative behaviour). **P1 reproduces 7/7 paper cells for RSchema CodeLlama/Llama/DeepSeek and SchemaBench CodeLlama/Llama.** |
| Counterfactual parser fixes | `counterfactual_parser_fixes.csv`: unchanged `reproduce_genuine_tables.evaluate_direct_*` after in-process monkey-patches (`experiments/E0/audit_cf_parser_patch.py`). Diagnostic only. |
| Per-schema cross-check | `sample_schema_crosscheck.csv`: 10 seeded schemas × {Claude, GPT} × {RSchema, SchemaBench}, both evaluators. RSchema: historical typed nGED == current typed nGED **to 4 dp on 20/20 schemas**; names-only is 0.19–0.20 lower on average. |
| Repo history | `src/` is byte-identical from `257b65d` to HEAD; `reproduce_genuine_tables.py` checked out at `257b65d`, `edcc543`, `96557da` reproduces today's `E0_TABLE_V_FINAL.csv` exactly (70/70 cells each). **The first commit `b626767` (2026-11-10 14:05) differs** (`ensure_prediction_metadata` prefers prediction-JSON metadata; Domain eligibility rule) and its Table V (`evaluator_at_commit_b626767_table_v.csv`, run offline via `audit_old_commit_rescore.py`) reproduces **35/35 manuscript cells** for RSchema CodeLlama/Llama/DeepSeek and SchemaBench CodeLlama/Llama (39/70 overall vs 29/70 for HEAD) — all 12 mismatching cells of those five rows equal that evaluator. Commit `257b65d` ("Fix E0 evaluation coverage…") switched to DDL-authoritative structure, which exposed defect F2. The manuscript's SchemaBench DeepSeek/Claude/GPT cells match **no** repo state (0/7 each): they come from the pre-repo Exp3/Exp4 evaluator (G). |

Reproduce: `python3 experiments/E0/audit_table_v_mismatch.py` (waterfall; add `--extra-only` for P1), `python3 experiments/E0/audit_counterfactual_run.py {none,apos_unterm,all,all5}`, `python3 experiments/E0/audit_sample_crosscheck.py <hist_rschema.json> <hist_sb.json>`, `python3 experiments/E0/classify_table_v_mismatches.py`.

## 3. Protocol conformance of the current evaluator

Tests: `tests/test_e0_independent_audit.py` (hand-computed expectations; 7 pass, 9 strict-xfail = defects).

| Manuscript protocol item | Status | Independent check |
|---|---|---|
| Micro F1 (sum G/P/M, then F1) | ✔ | two-schema case: G=6,P=3,M=3 → F1 = 2/3, macro would be 0.70 |
| Domain on 381 DDL IDs (RSchema), 239 (SchemaBench) | ✔ | `E0_TABLE_V_FINAL.csv` `domain_n` 381/239; DDL ids ⊂ logical ids; logical gold is varchar-only (so it must not be a Domain gold) |
| Hall4 = mean of T/A/E/R micro FP rates, Domain excluded | ✔ | synthetic item: 0.5,0.5,0,0 → 0.25 even with Domain FP = 1.0 |
| nGED names-only | ✔ | type/nullability flip → 0.0 names-only, >0 typed; hand value 1/5 for one missing column |
| Empty / failed prediction | ✔ | nGED = 1.0, recreated = 0, gold counts retained, Hall not forced to 1 |
| Aggregation of nGED | ✔ | macro mean over schemas — identical to the historical evaluator ⇒ **no D-type difference** |
| DDL parsing completeness | ✘ | defects F1–F6 (§7) |

## 4. Priority cases

### 4.1 RSchema Claude: nGED 0.780 vs 0.560, Domain 0.123 vs 0.208  (E, B; also G)

| | Paper | Historical re-run | Current typed/synthetic (W2) | Current names-only (W3) | Genuine (Domain on DDL gold) |
|---|---:|---:|---:|---:|---:|
| nGED | 0.780 | 0.7795 | 0.7791 | **0.5601** | 0.5601 |
| Domain F1 | 0.123 | 0.1236 (G/P/M 11705/16253/1728) | 0.1242 | 0.1242 | **0.2081** (8410/11901/2113) |
| Hall | 0.687 | 0.6874 (5-dim) | 0.6859 | 0.6859 | 0.6341 (Hall4) |

* The paper numbers are the historical evaluator's numbers; the current evaluator reproduces them to ≤0.0015 when the two protocol changes are switched off. Parser defects move the genuine value by ≤0.001 (`cfF1235`), so the **current value is trustworthy**.
* **nGED (E).** Historical labels are `(name, type_family, NULL/NOT NULL)`. RSchema gold is synthetic `varchar(255) NOT NULL`, so every typed LLM column (int, decimal, datetime, nullable) is a label mismatch. Hand check, schema `0115` (gold 2 tables/5 cols/1 FK, pred 2/5/1; graph sizes 8+8):
  * gold `unit(unit_id varchar NOT NULL, unit_name varchar NOT NULL, benchmark_testing_id varchar NOT NULL)`, `benchmark_testing(…)`;
  * pred `unit(unit_id int NOT NULL, unit_name varchar NOT NULL, benchmark_testing_type_id int NOT NULL)`, `benchmark_testing_type(…)`.
  * names-only: tables Δ=2, `unit` cols Δ=2, unmatched-table cols 4, FK Δ=2 → 10/16 = **0.625**; typed: `unit_id` and the FK column also differ in type → Δ=4 → 12/16 = **0.750**. Code gives 0.6250 / 0.7500.
* **Domain (B).** Paper/historical score Domain against the synthetic logical gold (518 schemas, 11,705 columns, all varchar NOT NULL), so a correctly typed `unit_id INTEGER` is a Domain miss. The genuine protocol uses the real DDL gold (381 schemas, 8,410 typed columns). Gold example for the same schema `0115`: real gold is `Unit_ID INTEGER PRIMARY KEY, Unit_Name VARCHAR(255)`, synthetic gold is ``unit_id varchar(255) NOT NULL``.
* **Hall.** 5-dim → Hall4 shifts −0.0377 (E); swapping the Domain gold inside the 5-dim mean shifts −0.0141 (B).

### 4.2 RSchema GPT-5.4-mini: nGED 0.777 vs 0.553, Domain 0.133 vs 0.223  (E, B; also G)

Same mechanism. nGED: historical 0.7769, current typed 0.7765, names-only **0.5531**. Domain: historical 11705/13439/1672 → 0.1330; genuine 8410/9873/2037 → **0.2228**. Hall 0.660 → 0.6049 (Hall4). Referential 0.221 vs 0.2248 (C): the historical FK regex attributes `ALTER TABLE … ADD CONSTRAINT FOREIGN KEY` clauses to the *last* `CREATE TABLE` (e.g. GPT `0446`: 9 FKs attributed to `crop_evaluations`), the current parser ignores ALTER FKs (defect F6, 11 FKs in total for this model).

### 4.3 RSchema Llama-3.1: Tables 0.572 vs 0.554, nGED 0.628 vs 0.637  (F)

| | Paper | Historical | Genuine | P1 (JSON structure) | Genuine + F1–F3 fix |
|---|---:|---:|---:|---:|---:|
| Tables F1 | 0.572 | 0.5721 (2436/2588/1437) | 0.5540 (2436/2290/1309) | 0.5721 | **0.5721 (2436/2588/1437)** |
| nGED | 0.628 | 0.7643 (typed) | 0.6365 | **0.6283** | 0.6149 |
| Hall | 0.695 | 0.7309 | 0.6908 | **0.6950** | 0.6958 |
| Domain | 0.113 | 0.1812 | 0.1158 | **0.1128** | 0.1209 |

*Predicted tables:* the current evaluator sees 2,290, the DDL contains **2,588 `CREATE TABLE` statements**, and the fixed parser recovers exactly 2,588 (hash-for-hash the historical count). Root cause (defect **F2**), example `rschema_exp4_llama31/0009.json`:

```sql
CREATE TABLE `candidates` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  ...
  PRIMARY KEY (`id`),
  ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;      -- no closing ")" for the table
CREATE TABLE `voters` ( ...
```

Llama regularly omits the closing `)` before `ENGINE` (74/518 schemas). The current `iter_ddl_table_bodies` balances parentheses, so the first body never closes and swallows every later `CREATE TABLE` (parsed tables for `0009`: `['candidates']`, header count 4).

**JSON metadata vs DDL (old scorer).** The historical `ensure_prediction_metadata` keeps the prediction JSON `metadata` whenever it exists: `tables` always came from the JSON list (all 518 Llama files carry it), `columns_by_table` from the JSON if non-empty (20 files) else from a regex DDL splitter that treats every header independently and tolerates the missing `)`. The current code ignores JSON structure and parses only DDL. In the 74 Llama schemas JSON-table-list ≠ DDL-table-list, and **all 74** are DDL truncations (`both=74`), so JSON was right there. P1 (genuine protocol + JSON structure) reproduces **all seven** paper cells of this row exactly (0.628/0.695/0.572/0.363/0.113/0.191/0.090). Hence the paper row = "genuine protocol, JSON table list" (it is exactly the evaluator at commit `b626767`, which reproduces this row 7/7) and the current deviation is defect F2 exposed by the `257b65d` switch to DDL-authoritative structure, not a protocol difference. (Note P1 itself is a hybrid — JSON tables but truncated DDL columns — so the fully-fixed value, last column, differs from both; Attr 0.363 → 0.377.)

*File identity.* `rschema_exp4_llama31/*` (1,037 files) and `schemabench_exp2_llama31/*` (479) hash-match the originals; Llama's JSON `metadata.tables` are non-empty in all files. The older archived Exp4 report (June 15) disagrees with the tree for Llama only (nGED 0.7751 vs 0.7643; Attr 0.350 vs 0.374) → that report is a superseded snapshot; the 06-28 Exp3 archive matches the re-run (≤0.0017).

### 4.4 SchemaBench Claude: Entity 0.345 vs 0.285  (F; also G)

Entity G/P/M (`PRIMARY KEY` + `UNIQUE` constraint occurrences):

| Variant | Gold | Recreated | Matched | F1 |
|---|---:|---:|---:|---:|
| Paper / historical evaluator | 2481 | 2529 | 865 | 0.3453 |
| Current (genuine) | 2414 | 2051 | 636 | 0.2849 |
| + F1/F2/F3 fixed | 2484 | 2140 | 677 | 0.2928 |
| + F1/F2/F3/F5 fixed | 2484 | 2529 | 866 | **0.3455** |

So ≈ 0.053 of the 0.060 gap is **F5** (escaped newlines) and 0.008 is F1–F3; with all fixes the current parser lands on the historical count (2529 recreated, 866 vs 865 matched).

* **F5 example** (`schemabench_exp2_claude_sonnet_4_6/0004.json`, 19 of 239 Claude files, 20 DeepSeek, 4 GPT): the model's DDL contains the two characters `\` `n` instead of line breaks:
  ``CREATE TABLE `users` (\n  `user_id` int(11) NOT NULL AUTO_INCREMENT,\n  `username` …,\n  PRIMARY KEY (`user_id`)\n) ENGINE=…``
  The 21 tables are recognised, but every column item starts with `\n`, so **0 columns and 0 PK/UNIQUE/FK are parsed** (JSON metadata is empty too). The historical PK regex runs over the raw body and still finds the 20 PKs. Unescaping (with the other fixes) recovers 149 columns for this file; across the 19 Claude files ≈ 2,990 columns (Claude Attributes F1 0.268 → 0.358).
* **F1 example** (gold `SB-106`, 14 `CREATE TABLE`): 

  ```sql
  CREATE TABLE `circuits` (
    `circuitId` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `circuitRef` varchar(255) NOT NULL DEFAULT '',     -- '' desynchronises quote masking
    ...
  ```
  `_apostrophe_is_string_delimiter` skips spaces backwards, so the opening `'` after `DEFAULT ` is taken as a mid-identifier apostrophe and ignored, while the second `'` opens a string that runs to the next quote anywhere later. Current parse: 1 table / 2 columns; correct: 14 / 98. Gold SchemaBench loses **75 tables** (2545 vs 2620) and **494 columns** in `SB-080/089/106/116/143`, which also deflates recall denominators for every SchemaBench cell.

PK / UNIQUE / inline / composite counting differences between the two parsers (SchemaBench gold, 2481 historical vs 2414 current vs 2484 fixed):

| Construct | Historical (`schema_classification`) | Current (`src/schema_parser`) | Effect |
|---|---|---|---|
| table-level `PRIMARY KEY (a,b)` composite | one tuple, columns sorted | same | none |
| inline `col … PRIMARY KEY` | counted unless col already in table-level PK | counted | none |
| inline `col … PRIMARY KEY … UNIQUE` (same column; `SB-155 House.id`, `SB-170 exchanges.date`) | PK **and** UNIQUE (2) | `elif` → PK only (1) | −2 gold; convention difference (C), not a defect — worth stating in the paper |
| plain `UNIQUE (a,b)` / `CONSTRAINT x UNIQUE (…)` | counted | counted | none (the `src` docstring claim that the vendored parser ignores them is wrong) |
| table names with space/slash/parens (`Order Details`, `users/teams`, `(tagger)`, `Metadata - Countries`) | header regex `(\w+)` misreads (e.g. `Country Code`→`Country`) | read correctly | +5 gold PKs (current better) |
| table lost to F1 (SB-080/089/106/116/143) | counted | **missing** | −73 gold PKs (defect); ±5 further PKs are header-name edge cases that cancel |
| column named `unique_code … PRIMARY KEY` (`SB-225 course`) | counted | dropped: `UNIQUE` prefix test treats it as a constraint line (**F4**) | −1 |

### 4.5 SchemaBench GPT-5.4-mini: nGED 0.760 vs 0.685  (E; also G)

Historical 0.7587; current typed 0.7765; names-only **0.6853** (E: −0.0912). Typed labels carry type family and nullability; for DDL gold the current parser treats a bare `col type` as nullable (MySQL dialect) whereas the legacy rule treats it as NOT NULL, which also changes Domain matching (§5). The parser structure residual (+0.0178 hist→current) comes from F1 (gold tables lost) and F5 (4 GPT files with escaped newlines); fixing F1–F3/F5 would move the genuine value a further −0.0104 to 0.6749. Hall 0.685 → 0.6657 (Hall4, E).

## 5. Remaining families

* **RSchema DeepSeek (5 cells: C×3, H×2).** P1 reproduces all seven paper cells (nGED 0.5625, Hall 0.5952, Tables 0.5655, Attr 0.4412, Domain 0.1490); differences are ≤0.0014 and concentrated in few schemas where the JSON structure differs from the DDL (e.g. `0180`: JSON lists `['pizza_shop']`, DDL has 4 tables; `0307`: DDL truncated by F1/F2, 5 tables lost; `0420` contains escaped newlines). Hall (−0.000503) and Domain (−0.000578) lie within 1e-4 of the paper's printed rounding interval → **H**.
* **RSchema Claude/GPT Attr, Ref (C).** ≤0.0038. In the waterfall the legacy→robust parser step moves Claude Attr +0.0010 and Ref +0.0011, GPT Ref +0.0037; GPT's Ref difference is dominated by `ALTER TABLE … ADD CONSTRAINT FOREIGN KEY` clauses (historical regex misattributes them, current parser ignores them, F6). The vendored evaluator's set-iteration tie-break noise (±5e-4) adds to the residual.
* **SchemaBench Llama (F×3).** Same F2 mechanism: 29 schemas, 196 tables lost (27 with the missing-`)` pattern); P1 reproduces 7/7 paper cells.
* **SchemaBench DeepSeek (C×6).** Paper lies within 0.004 of genuine but is reproduced by neither P1 (0/7) nor the historical evaluator; not explainable from available evaluator states → attributed to a parser revision (**confidence: low**). Note the current values are themselves affected by F5 (20 files; Attr would move +0.033).
* **SchemaBench Claude/GPT structural cells (F×8, C×2).** Paper = historical output; current differs mainly through F1 (gold −75 tables, predicted tables lost) and F5; fixing them closes ≥50% of the gap for Tables/Domain/Entity/Ref (GPT Attr and Domain are net C: nullability rule and typing differences dominate).

## 6. Causes not observed

* **A (snapshot):** none — trees are byte-identical to the originals; only the superseded June-15 archive differs.
* **D (aggregation):** none — F1 is micro in both; nGED is a macro mean in both; Hall is "mean over dimensions of micro rates" in both (only the *set* of dimensions differs → E).

## 7. Genuine defects in `src/schema_parser.py` (flagged, not fixed)

Each has a minimal failing case in `tests/test_e0_independent_audit.py::TestGenuineDefects` (`xfail(strict=True)`; `pytest --runxfail` shows the failures).

| ID | Defect | Minimal case | Measured impact |
|---|---|---|---|
| F1 | `_apostrophe_is_string_delimiter` skips spaces → `DEFAULT ''` / `'a)b'` desynchronises masking | `CREATE TABLE a (x varchar(3) DEFAULT '', y int); CREATE TABLE b (z int);` → tables `['a']`, 1 column | SchemaBench gold −75 tables/−494 columns (5 schemas); Claude SB −88 pred tables |
| F2 | Unterminated body swallows later tables | `…PRIMARY KEY (x),\n ENGINE=InnoDB;\nCREATE TABLE b (…` → `['a']` | Llama RS −298 tables (74 schemas), Llama SB −196 (29) |
| F3 | Header regex rejects unquoted `-`/`/` names | `CREATE TABLE Sign-in (a int, b int);` → no table | 7 RSchema-DDL gold tables (Domain gold 8410 → 8442 columns when fixed) |
| F4 | Column names starting `UNIQUE`/`CONSTRAINT`/`FULLTEXT`/`SPATIAL` skipped | `unique_code VARCHAR(30) NOT NULL PRIMARY KEY` | 7 gold column lines; 0 predictions |
| F5 | Escaped (`\n`) DDL → 0 columns/constraints | file `0004` above | SB Claude 19, DeepSeek 20, GPT 4, RS DeepSeek 1 files; Claude SB Attr +0.090, Entity +0.061 |
| F6 | `ALTER TABLE … ADD CONSTRAINT FOREIGN KEY` ignored | see test | ≤34 FKs per model (≈1–3% of FKs) |

F5 and F6 are partly policy questions (the DDL is not valid SQL as emitted / FKs outside `CREATE TABLE`); F1–F4 are unambiguous parse errors on valid or near-valid DDL. Also: `legacy=True` is **not** a bit-for-bit port of the historical evaluator (SchemaBench gold FKs: historical 2802, `legacy=True` 1378, current 2708) — do not use it as "Historical".

## 8. Recommendations

1. Do **not** tune the evaluator toward the manuscript. Fix F1–F4 (and decide F5/F6 policy) in a separate commit with the xfail markers removed, then regenerate `E0_TABLE_V_FINAL.csv`.
2. Update now (parser-robust, |shift| ≤ 0.001): RSchema Claude nGED 0.560, Hall 0.634, Domain 0.208; GPT nGED 0.553, Hall 0.605, Domain 0.223 — the manuscript values are stale (E/B, G).
3. Hold the other 35 cells until the parser fix; in particular Llama (F), SchemaBench Claude/GPT (E cells shift a further 0.01–0.04) and DeepSeek.
4. State in the paper: Domain gold = 381 real-DDL refs; nGED names-only; Hall4; inline `PRIMARY KEY … UNIQUE` counted once.

## 9. Limitations

* "Historical" is the historical evaluator re-run with `PYTHONHASHSEED=0`; the vendored code is hash-order dependent (±5e-4), hence the 0.0015 equality tolerance.
* Counterfactual patches are in-process approximations of fixes (not a production patch); they quantify defects but are not themselves validated Table V values.
* The origin of the manuscript's exact SchemaBench-DeepSeek row could not be reproduced from any available state.
