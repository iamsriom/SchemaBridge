# E4 — Masking and structural inferability

| | |
|---|---|
| **Paper tables** | `\label{tab:e4_split}`, `\label{tab:e4_recovery}` |
| **Population** | Enterprise-145 + SchemaBench-239 + RSchema-518 (pooled) |
| **Constructor** | GPT-4o-mini (Direct masked-DDL → schema; Round-trip NL → schema) |
| **Describers (RT)** | Enterprise: mistral, CodeLlama, DeepSeek, Llama-3.1; SchemaBench/RSchema: CodeLlama-13B, Llama-3.1, DeepSeek |
| **Masks** | MT tables, MA attributes, MD domain, ME entity, MR referential |
| **Domain** | **Joint** data-type family **and** nullability (not legacy Exp5 `domain_facts`) |
| **Verified artifacts** | `results/metrics/reproduced/E4_AUDIT/` |
| **Status** | **VERIFIED** (PRIMARY) |

## Authoritative offline evaluation

```bash
python3 experiments/E4/evaluate.py
python3 experiments/E4/generate_tables.py
pytest -q tests/test_e4_primary.py
```

Generation is disabled:

```bash
python3 experiments/E4/run.py   # refuses API / paid inference
```

## Metric definitions (PRIMARY)

- **Inferability:** heuristic labels; weak → non-inferable in main tables.
- **Split recall:** Direct micro over eligible gold elements (observed-case).
- **Recovery Gold N / Direct:** unique inferable elements with Direct predictions.
- **RT:** for each element, mean match over available describers; then micro-average element means.
- **Retention:** `RT / Direct` at full precision, then round to 3 d.p.
- **Domain:** joint type-family + nullability per column (shared SchemaBridge Domain definition).
- **Legacy:** Exp5 `domain_facts` scoring remains documented as historical only — do not treat as paper Domain.

Entity/Referential Split Gold N (2,161 / 4,214) exceed Recovery Gold N (2,087 / 4,197) because Split micro-counts rare duplicate Direct evaluation rows; Recovery deduplicates. This is intentional.

## What is *not* PRIMARY

| Artifact | Role |
|---|---|
| Exp5 `domain_facts` Split (0.425 / 0.611) | Historical fact-level Domain — superseded for the paper |
| SchemaBench-only Domain (0.409 / 1,574) | Incorrect mixed population — do not use |
| Entity non-inferable 0.635 | Transcription error; correct is 0.447 |
| `e4_cases3_*` archived aggregates | Alternate Cases3 hiding study — not tab:e4_split |

## Public reproducibility limit

Masked Direct/RT prediction JSON and gold DDL trees are **not** shipped in git (private experimental dumps). Published CSVs and LaTeX under `E4_AUDIT/` are the camera-ready numbers. Optional recompute instructions: [REPRODUCE_E4.md](../../docs/REPRODUCE_E4.md).
