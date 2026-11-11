# E0 Verification Report

**Branch:** `icde2027-e0-verified`
**Scope:** Tables V–VI only (E0 Text2Schema).
**Rule:** Current manuscript targets from `audit/E0_CURRENT_MANUSCRIPT_VALUES.json`; older `configs/paper_reference_values.json` is **not** the acceptance target.
**Experiment status:** **PARTIAL** (Direct COMPLETE; PaperMethods trees missing → ARCHIVE_AGGREGATE for prompting rows).

## Executive verdict

| Table | PASS | PASS_ARCHIVE | MISMATCH | MISMATCH_ARCHIVE | BLOCKED |
|---|---:|---:|---:|---:|---:|
| V (70 cells) | 29 | 0 | 41 | 0 | 0 |
| VI (84 cells) | 20 | 30 | 10 | 24 | 0 |

- Offline Direct recompute is **deterministic** (two consecutive runs identical byte-for-byte on `E0_TABLE_{V,VI}_FINAL.csv`).
- All 10 Direct prediction trees (757 JSON files) **hash-match** original Exp4 / SchemaBench Experiment2 directories.
- PaperMethods per-schema `results.jsonl` trees remain **unrecoverable** on this host.
- Table VI prompting rows use **ARCHIVE_AGGREGATE** recomputation from pooled G/P/M in `results/baselines/e0_rschema_papermethods_evaluation.json` (2026-10-12). This is **not** a full per-schema genuine-protocol re-score.
- Scientifically recommended Table V numbers: `results/metrics/reproduced/E0_TABLE_V_FINAL.csv`.

Cell-level file: `audit/E0_PAPER_COMPARISON.csv`.

## Protocol verified in code

| Item | Implementation | Match to current manuscript text |
|---|---|---|
| Structural F1 micro over T/A/D/E/R | `src/metrics.py` + `reproduce_genuine_tables.py` | Yes |
| Identifier normalization | lowercasing; strip quotes/spaces/`_`/`-` | Yes |
| RSchema Domain on 381 DDL IDs | `annotation_ddl.jsonl` intersection | Yes |
| No synthetic VARCHAR Domain gold | genuine DDL only | Yes |
| Hallucination 4-dim mean T/A/E/R | Domain excluded; empty P→0 | Yes |
| E0 nGED names-only | `names_only=True` | Yes (Direct); archive nGED is historical macro |
| Empty prediction failure policy | nGED=1; Hall not forced to 1 | Yes |
| Baseline Domain | `--` | Yes |
| Data leakage check | constructor receives NL `question` only | Yes |
| SchemaAgent | excluded from release and Table VI | Yes |

## Prediction recovery

### Direct (byte-identical to originals)

| Dataset | Model | Present | Original path | Status |
|---|---|---:|---|---|
| RSchema | CodeLlama-13B | 518/518 | `/data/RSchema_ExpResults4/Experiments/text2schema_codellama13b/` | ORIGINAL |
| RSchema | Llama-3.1-8B | 518/518 | `.../text2schema_llama31/` | ORIGINAL |
| RSchema | DeepSeek-Coder-6.7B | 518/518 | `.../text2schema_deepseek/` | ORIGINAL |
| RSchema | Claude Sonnet 4.6 | 518/518 | `.../text2schema_sonnet46/` | ORIGINAL |
| RSchema | GPT-5.4-mini | 518/518 | `.../text2schema_gpt54mini/` | ORIGINAL |
| SchemaBench | CodeLlama-13B | 239/239 | `/data/Text2ER/SchemaBench/Experiment2/text2schema_codellama13b/` | ORIGINAL |
| SchemaBench | Llama-3.1-8B | 239/239 | `.../text2schema_llama31/` | ORIGINAL |
| SchemaBench | DeepSeek-Coder-6.7B | 239/239 | `.../text2schema_deepseek/` | ORIGINAL |
| SchemaBench | Claude Sonnet 4.6 | 239/239 | `.../text2schema_sonnet46/` | ORIGINAL |
| SchemaBench | GPT-5.4-mini | 239/239 | `.../text2schema_gpt54mini/` | ORIGINAL |

### Baselines (PaperMethods)

| Model | Method | `results.jsonl` | Archive G/P/M | Zero (archive) | Usable status |
|---|---|---|---|---:|---|
| CodeLlama-13B | one_shot / cot / few_shot | MISSING | Yes | 3 / 24 / 4 | ARCHIVE_AGGREGATE |
| Llama-3.1-8B | one_shot / cot / few_shot | MISSING | Yes | 1 / 10 / 1 | ARCHIVE_AGGREGATE |
| DeepSeek-Coder-6.7B | one_shot / cot / few_shot | MISSING | Yes | 3 / 38 / 0 | ARCHIVE_AGGREGATE |

`prompt_conditions_v2` (518×9) is a **near-miss only** — failure counts differ (e.g. CodeLlama one_shot 199 vs archived 3). Do not substitute.

## Recommended scientifically justified Table V

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

### Substantive Table V mismatch notes

1. **CodeLlama (both datasets):** all 14 cells PASS — manuscript matches genuine protocol.
2. **Llama-3.1 Tables/nGED:** manuscript still tracks hybrid/older Exp3 cells (RSchema Tables 0.572 / nGED 0.628). Genuine: Tables 0.554, nGED 0.637.
3. **Claude / GPT-5.4-mini RSchema nGED/Hall/Domain:** manuscript matches older Exp3 evaluator (nGED ~0.78, Domain ~0.12); genuine recompute yields nGED ~0.55–0.56 and Domain ~0.21–0.22.
4. **SchemaBench Claude/GPT:** broader structural deltas under corrected parser vs June-2026 Exp4 report.
5. **DeepSeek:** small 3dp / parser deltas on several cells.

## Table VI archive recomputation

When trees are missing, prompting metrics are derived as:

| Metric | Archive derivation |
|---|---|
| T/A/E/R | micro F1 = `2M/(G+P)` from pooled counts (= stored `f1_micro`) |
| Hall | mean of T/A/E/R `hallucinated/recreated` (P=0 → 0) |
| nGED | archived `mean_normalized_graph_edit_distance` (**historical macro**; cannot recompute names-only without trees) |
| Domain | `--` |

Archive SHA-256: `644d8217beac7510dbd0d5ad24d0076da8b851ac5d92275bf919ed963771b1ca`

**PASS_ARCHIVE (30)** cells match manuscript within 0.0005 / 3dp.
**MISMATCH_ARCHIVE (24)** are mostly ≤0.003 (Attributes systematically ~0.001 higher in manuscript; a few nGED/Hall rounding differences). Largest: DeepSeek Few-shot Attributes (−0.0025), DeepSeek One-shot Attributes (−0.0029), DeepSeek Few-shot nGED (+0.0021).

Direct VI rows mirror Table V (20 PASS / 10 MISMATCH).

## Independent checks

- Built-in 10-schema seed=42 validation: PASS.
- `pytest`: 215 passed.
- Two full offline recomputes: identical Table V/VI FINAL CSVs.
- Gold: RSchema logical 518, DDL 381, SchemaBench 239; IDs join-verified.

## Reproduction commands (reviewer)

```bash
git clone https://github.com/iamsriom/SchemaBridge.git
cd SchemaBridge
git checkout icde2027-e0-verified
bash scripts/reproduce_e0_offline.sh
```

Outputs: `results/metrics/reproduced/E0_TABLE_{V,VI}_FINAL.*`, `audit/E0_PAPER_COMPARISON.csv`.

## Remaining blockers / smallest fixes

1. **Recover PaperMethods `results.jsonl` trees** from external backup → place under `results/predictions/e0/rschema_papermethods/<model>/<method>/` → re-run `reproduce_genuine_tables.py` for full per-schema names-only nGED / Hall4.
2. **Update manuscript Table V** to `E0_TABLE_V_FINAL.csv` (or document intentional hybrid cells for Claude/GPT/Llama).
3. **Align Table VI Direct rows** with corrected Table V RSchema after (2).
4. **Attributes rounding on Table VI:** manuscript Attributes are ~0.001 above archive `f1_micro`; prefer archive micro values or recover trees to re-score.
5. Do **not** mark E0 COMPLETE while trees are missing or hybrid manuscript cells remain unexplained.
6. Do **not** substitute `prompt_conditions_v2` for PaperMethods.


## Independent verification addendum (2026-11-11)

Performed against recovery workspace + this branch without regenerating predictions or paid API calls.

### CodeLlama-13B RSchema pilot — VERIFIED

| Metric | Full precision | Round-3 | Manuscript | Status |
|---|---:|---:|---:|---|
| nGED | 0.583048 | 0.583 | 0.583 | PASS |
| Hallucination | 0.668598 | 0.669 | 0.669 | PASS |
| Tables F1 | 0.553864 | 0.554 | 0.554 | PASS |
| Attributes F1 | 0.414443 | 0.414 | 0.414 | PASS |
| Domain F1 | 0.114962 | 0.115 | 0.115 | PASS |
| Entity F1 | 0.300543 | 0.301 | 0.301 | PASS |
| Referential F1 | 0.139797 | 0.140 | 0.140 | PASS |

G/P/M: Tables 2436/2753/1437; Attr 11705/13138/5148; Entity 2435/2902/802; Ref 2146/2289/310; Domain(381) 8410/9509/1030.

Artifacts: `audit/E0_CODELLAMA_PILOT_CHECKPOINT.json`, `audit/E0_CODELLAMA_MANUAL_VALIDATION.csv` (10 unique records; manual table/attr set counts agree with evaluator).

### Workspace comparison

See `audit/E0_WORKSPACE_COMPARISON.md` and `audit/E0_CONSTRUCTOR_VERIFICATION.md`.

Recovery open-weight trees are **byte-identical** to this branch. Claude/GPT trees exist **only** here — do not overwrite from recovery.

### Comparator fix

`scripts/build_e0_paper_comparison.py`: Table VI Domain branch no longer coerces Direct Domain paper values to `"--"` before comparison. Baseline Domain remains `"--"`. Tests in `tests/test_e0_paper_comparison.py`.

### Table V independent audit

`audit/E0_TABLE_V_INDEPENDENT_AUDIT.csv`: **29 PASS / 41 MISMATCH** vs current manuscript targets under genuine protocol. CodeLlama (both datasets) fully PASS. Remaining mismatches are manuscript/protocol lineage issues, not missing predictions.

### Status unchanged

Experiment remains **PARTIAL**: Direct offline COMPLETE; PaperMethods per-schema trees still missing (ARCHIVE_AGGREGATE). Do not merge as E0 COMPLETE.


## Forensic root-cause addendum (2026-11-11 evening)

See `audit/E0_FORENSIC_FINDINGS.md`, `audit/E0_ORIGINAL_PAPER_RESULT_LINEAGE.md`,
`audit/E0_HISTORICAL_REPRODUCTION.csv`, `audit/E0_PROTOCOL_ABLATION.csv`,
`audit/E0_ROOT_CAUSE_MATRIX.csv`.

Summary: manuscript Table V is a hybrid of Exp3 historical metrics (typed nGED,
synthetic Domain, Hall5) and later genuine-protocol cells. Claude/GPT gaps are
explained by protocol change on identical predictions. Parser bug for unclosed
`ENGINE=`-inside-table DDL fixed in `src/schema_parser.py`.
