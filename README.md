
# SchemaBridge

**A Unified Benchmark for Relational Schema Design, Comprehension, and Structural Preservation Using Large Language Models**

**Paper:** *How well do LLMs comprehend and design relational database schemata?*  
**Status:** Submitted to **ICDE 2027** (under review; not an accepted publication).  
**Authors:** Sriom Chakrabarti, Sean Bin Yang, Arijit Khan, and Sebastian Link.

## Overview

Most natural-language database benchmarks assume a relational schema already exists. **SchemaBridge** studies whether large language models (LLMs) can design a schema from requirements, describe an existing schema, and preserve its structure when the description is used to reconstruct it.

| Task | Input → Output | What it tests |
|---|---|---|
| **Text2Schema** | Natural-language requirements → Relational schema | Schema design |
| **Schema2Text** | Relational schema → Natural-language description | Schema comprehension and verbalization |
| **Schema → Text → Schema** | Schema → Description → Reconstructed schema | Round-trip structural preservation |

## Benchmark at a Glance

The benchmark contains **902 schemata** from three collections:

| Dataset | Schemata | Description |
|---|---:|---|
| **Enterprise-145** | 145 | Enterprise relational schemata in DDL format |
| **RSchema** | 518 | Logical schema references, including 381 matched DDL references |
| **SchemaBench** | 239 | Relational schemata paired with natural-language project specifications |
| **Total** | **902** | Experiment populations vary by task |

SchemaBridge evaluates open-weight and proprietary LLMs acting as:

- **Constructors:** Generate relational schemata from natural language.
- **Describers:** Generate natural-language descriptions from relational schemata.

## Evaluation Metrics

SchemaBridge evaluates structural fidelity, schema-level divergence, and natural-language description quality.

### 1. Structural Fidelity

Structural fidelity is evaluated across five dimensions:

| Dimension | Symbol | Description |
|---|---|---|
| **Tables** | T | Recovery of table identifiers |
| **Attributes** | A | Recovery of table-qualified column identifiers |
| **Domain Integrity** | D | Joint matching of data-type families and nullability |
| **Entity Integrity** | E | Recovery of primary-key and UNIQUE constraints |
| **Referential Integrity** | R | Recovery of foreign-key relationships |

Each dimension is evaluated using **precision, recall, and F1-score**, based on normalized structural elements.

Additional metrics include:

- **Normalized Graph Edit Distance (nGED):** Measures structural divergence between generated and gold schemata. Lower is better. E0 uses a type-independent variant for comparability with untyped references and baselines.
- **Hallucination Rate:** Measures reference-relative structural over-generation across tables, attributes, entity integrity, and referential integrity (T/A/E/R). Lower is better.

Structural evaluation uses reference-based matching. Consequently, alternative valid relational designs may be penalized when they differ from the gold schema.

### 2. Schema2Text Evaluation

Schema2Text assesses whether generated natural-language descriptions preserve the information contained in the original relational schema.

Four metrics are used:

| Metric | Description | Better |
|---|---|---|
| **BLEU-4** | Measures n-gram overlap between generated and reference descriptions | Higher ↑ |
| **ROUGE-L** | Measures longest-common-subsequence similarity with reference descriptions | Higher ↑ |
| **BERTScore-F1** | Measures contextual semantic similarity using language-model embeddings | Higher ↑ |
| **Schema Coverage Rate (SCR)** | Measures the proportion of source table and column identifiers explicitly mentioned in the generated description | Higher ↑ |

#### Schema Coverage Rate (SCR)

SCR measures how much schema identifier information is preserved during verbalization.

For a generated description \(T\) and source schema \(S\):

\[
\mathrm{SCR}(T,S)=
\frac{
|\{e\in E(S):\mathrm{norm}(e)\text{ occurs in }\mathrm{norm}(T)\}|
}{
|E(S)|
}
\]

where \(E(S)\) contains the source table and column identifiers.

**Important distinctions:**

- BLEU-4, ROUGE-L, and BERTScore-F1 compare generated descriptions against reference natural language.
- SCR compares generated descriptions directly against source schema identifiers.
- SCR does not verify data types, nullability, primary keys, or foreign-key correctness.
- Round-trip structural F1 evaluates whether these structural properties can be reconstructed.

For **Enterprise-145**, only SCR is reported because no gold natural-language descriptions are available.

For **RSchema** and **SchemaBench**, all four description-quality metrics are reported.

Schema2Text experiments compare **Basic (B)** and **Detailed (D)** prompting strategies.

## Experiments

SchemaBridge consists of six experiments:

| ID | Objective |
|---|---|
| **E0** | **Text2Schema:** Evaluate relational schema generation from natural-language requirements under different prompting strategies |
| **E1** | **Schema2Text:** Evaluate natural-language schema descriptions using BLEU-4, ROUGE-L, BERTScore-F1, and SCR |
| **E2** | **Round-Trip Preservation:** Measure structural fidelity while varying the describer and fixing the constructor |
| **E3** | **Constructor Isolation:** Measure reconstruction performance across constructors using fixed generated descriptions |
| **E4** | **Masking and Inferability:** Evaluate recovery of hidden schema elements from remaining structural evidence |
| **E5** | **Inference Efficiency:** Analyze end-to-end latency, token consumption, and API cost |

Detailed experimental documentation is available in [`docs/experiments/`](docs/experiments/).

## Getting Started

### Installation

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/iamsriom/SchemaBridge.git
cd SchemaBridge

pip install -r requirements.txt
```

Run the available tests:

```bash
python3 -m pytest -q
```

### E0: Schema Design Evaluation

Validate the evaluation protocol without requiring prediction files:

```bash
python3 experiments/E0/reproduce_genuine_tables.py \
  --validate-only --skip-pytest
```

To reproduce E0 results using the original saved prediction files:

```bash
export PRED_ROOT=/path/to/private/e0-predictions

python3 experiments/E0/reproduce_genuine_tables.py \
  --pred-root "$PRED_ROOT" \
  --write-gpm \
  --skip-pytest \
  --strict
```

See [`experiments/E0/README.md`](experiments/E0/README.md) for evaluation details.

### E2: Round-Trip Evaluation

The following commands reproduce E2 structural evaluation using the original locally saved GPT-4o-mini reconstruction outputs:

```bash
python3 experiments/E2/prepare_dataset.py

PYTHONHASHSEED=0 \
python3 experiments/E2/evaluate_table_viii_full.py

PYTHONHASHSEED=0 \
python3 experiments/E2/generate_table_viii.py
```

For additional information:

- [E2 Experiment Documentation](experiments/E2/README.md)
- [E1–E2 Reproducibility Guide](docs/REPRODUCE_E1_E2.md)

### Reproducibility

The public repository provides evaluation implementations, documentation, and available experimental artifacts.

However, **not every experiment can currently be reproduced from a fresh public clone**.

Some evaluations depend on archived model predictions or provider logs stored separately from the repository. The public release does not yet contain all artifacts required for independent end-to-end reproduction of E3 and E4. E0 prompting baselines and E5 provenance also have documented limitations.

See the experiment documentation and audit reports for details.

## Optional: Live E0 Inference

Live model inference is optional and may incur API charges.

Install provider libraries:

```bash
pip install openai anthropic
```

Set the required API credentials:

```bash
export OPENAI_API_KEY=...
export ANTHROPIC_API_KEY=...
```

Run a dry-run validation:

```bash
python3 experiments/E0/run_direct_api.py --dry-run
```

Run a limited paid inference test:

```bash
python3 experiments/E0/run_direct_api.py \
  --limit 1 \
  --confirm-paid
```

**Security:** Never commit API keys, credentials, or sensitive prediction files. Check dataset licensing and redistribution permissions before publishing artifacts.

## Citation

If you use SchemaBridge in your research, please refer to [`CITATION.cff`](CITATION.cff).

**Publication status:** The paper has been submitted to ICDE 2027 and has not been accepted or published as an ICDE proceedings paper.

Academic authorship is defined by the paper's author list and is independent of GitHub repository ownership.
