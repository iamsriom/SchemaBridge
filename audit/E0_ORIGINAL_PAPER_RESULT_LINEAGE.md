# E0 Original Paper Result Lineage

**Scope:** Table V (`tab:e0_overall`) Direct Text2Schema.
**Question:** Where did the manuscript numbers come from, and which evaluator produced them?

## Executive finding

The current ICDE manuscript Table V is a **hybrid**:

| Cell class | Count (approx.) | Source |
|---|---:|---|
| Matches Exp3 historical archive only | ~25 | `/data/A_Final_Result/Exp3/exp3_combined_results.txt` (2026-06-28) |
| Matches genuine protocol only | ~10 | Post-Exp3 genuine Domain / Hall4 / names-only nGED |
| Agree under both | ~10 | Structurally stable cells (e.g. many Tables/Entity) |
| Mixed / intermediate | ~25 | Partial updates or near-ties |

**Claude / GPT large gaps are not prediction changes.** The same packaged prediction trees, scored with the historical Exp4 evaluator, reproduce Claude RSchema nGED **0.7794 ≈ paper 0.780** and GPT **0.7769 ≈ paper 0.777**.

## End-to-end lineage (historical Exp3 path)

```
Prediction NNNN.json/.txt
  → evaluate_exp4_text2schema.py  (RSchema logical gold OR SchemaBench DDL gold)
  → text2schema_exp4_evaluation.json / text2schema_exp4_report.txt
  → combine_exp3_results.py
  → /data/A_Final_Result/Exp3/exp3_combined_results.txt   [PACKAGED: results/metrics/archived/e0_exp3_combined_results.txt]
  → manuscript Table V (selected cells; especially Claude/GPT)
```

### 1. Prediction files

| Dataset | Model | Original path | Packaged path |
|---|---|---|---|
| RSchema | CodeLlama / Llama / DeepSeek / Claude / GPT | `/data/RSchema_ExpResults4/Experiments/text2schema_<llm>/` | `results/predictions/e0/rschema_exp4_*` |
| SchemaBench | same models | `/data/Text2ER/SchemaBench/Experiment2/text2schema_<llm>/` | `results/predictions/e0/schemabench_exp2_*` |

Generation: Exp4 HF/API scripts under `experiments/E0/original_benchmarks/direct/`.
Input: gold NL `question` only. Constructor prompt SHA-256 `392a396f…4ad4`.

### 2. Historical evaluator

| Item | Value |
|---|---|
| Script | `/data/RSchema_ExpResults4/Code/evaluate_exp4_text2schema.py` |
| Packaged | `experiments/E0/original_benchmarks/evaluation/evaluate_exp4_text2schema.py` + working DDL parser in `third_party/evaluate_exp4_text2schema.py` |
| Pairwise scorer | `evaluate_text2schema2.evaluate_one` |
| RSchema gold | `annotation.jsonl` **logical** answer → **synthetic** `varchar(255) NOT NULL` DDL |
| SchemaBench gold | Experiment2 DDL references |
| Domain | matched types+nullability against synthetic gold; **Domain gold count = attribute count** (RSchema 11705) |
| Hallucination | **5-dim** mean including Domain (`combine_exp3_results.normalize_entries`) |
| nGED | **typed**: column labels `(name, type_family, nullable)`; denom = gold_size+pred_size |

### 3. Combined archive (definitive manuscript source for Claude/GPT)

File: `results/metrics/archived/e0_exp3_combined_results.txt`
Generated: **2026-06-28 23:15:34 UTC**
Sources cited in header:

- RSchema → `/data/RSchema_ExpResults4/Experiments/Results/text2schema_exp4_report.txt`
- SchemaBench → `/data/Text2ER/SchemaBench/Experiment2/Results/text2schema_exp4_report.txt`

Combiner: `experiments/E0/original_benchmarks/evaluation/combine_exp3_results.py`

### 4. Exact manuscript values recovered from Exp3 TABLE 1

| Dataset | Model | Metric | Exp3 value | Paper |
|---|---|---|---:|---:|
| RSchema | Claude Sonnet 4.6 | nGED | 0.7796 | 0.780 |
| RSchema | Claude Sonnet 4.6 | Domain | 0.123 | 0.123 |
| RSchema | GPT-5.4-mini | nGED | 0.7769 | 0.777 |
| RSchema | GPT-5.4-mini | Domain | 0.133 | 0.133 |
| RSchema | Llama-3.1 | Tables | 0.572 | 0.572 |
| SchemaBench | Claude Sonnet 4.6 | Entity | 0.345 | 0.345 |

### 5. Genuine-protocol path (later; used for CodeLlama paper cells)

```
Same predictions
  → experiments/E0/reproduce_genuine_tables.py
  → Domain on 381 DDL IDs; Hall4; names_only nGED; legacy=False parser
  → E0_TABLE_V_FINAL.csv
  → manuscript cells for CodeLlama (and some other open-weight cells)
```

Example: CodeLlama RSchema nGED paper **0.583** matches genuine **0.583048**, **not** Exp3 **0.7335**.

## Unknowns

| Step | Status |
|---|---|
| Exact git commit / calendar date when hybrid Table V was assembled in LaTeX | **UNKNOWN** (no single table-generation commit recovered that mixes both) |
| Closed-model API decoding snapshot (temp/max_tokens) | **UNKNOWN** beyond batch scripts |
| Whether every SchemaBench Exp3 cell used identical Experiment2 gold bytes as packaged `annotation_ddl.jsonl` | **PARTIAL** (Entity matches; some Ref cells diverge under hist repro) |
