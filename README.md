# SchemaBridge

**A Unified Benchmark for Relational Schema Design, Comprehension, and Structural Preservation Using Large Language Models**

Paper: *How well do LLMs comprehend and design relational database schemata?*  
Status: Submitted to **ICDE 2027** (not an accepted publication).

Academic authors: Sriom Chakrabarti, Sean Bin Yang, Arijit Khan, Sebastian Link.

## Research overview

| Task | Mapping |
|---|---|
| **Text2Schema** | Natural language requirements → relational schema |
| **Schema2Text** | Relational schema → natural language description |
| **Schema→Text→Schema** | Structural preservation through natural language |

## Benchmark overview

- **902** schemata: Enterprise-145 (145), RSchema (518), SchemaBench (239).
- Open-weight and closed LLM constructors / describers.
- Five structural fidelity dimensions (T/A/D/E/R), plus nGED, hallucination rate, and Schema2Text text metrics.

## Experiments

| ID | Objective | Docs | Verification |
|----|-----------|------|--------------|
| **E0** | Text2Schema from NL | [docs/experiments/E0.md](docs/experiments/E0.md) | Direct reproducible from private saved predictions; prompting baselines PARTIAL |
| **E1** | Schema verbalization | [docs/experiments/E1.md](docs/experiments/E1.md) | VERIFIED — full `tab:e1_s2t` (B/D × 3 corpora) |
| **E2** | Round-trip preservation | [docs/experiments/E2.md](docs/experiments/E2.md) | VERIFIED — PRIMARY 765 (145/381/239); see `E2_AUDIT/` |
| **E3** | Constructor isolation | [docs/experiments/E3.md](docs/experiments/E3.md) | UNVERIFIED — frozen descriptions missing |
| **E4** | Masking / inferability | [docs/experiments/E4.md](docs/experiments/E4.md) | UNVERIFIED — Tables X–XI not recovered |
| **E5** | Scalability and cost | [docs/experiments/E5.md](docs/experiments/E5.md) | REPRODUCED, PROVENANCE INCOMPLETE (N=30) |

## Quick start (offline)

```bash
git clone https://github.com/iamsriom/SchemaBridge.git
cd SchemaBridge
pip install -r requirements.txt
python3 -m pytest -q

# E0 gold + protocol checks (no predictions required)
python3 experiments/E0/reproduce_genuine_tables.py --validate-only --skip-pytest

# Tables V+VI from private prediction dumps (not published in git)
export PRED_ROOT=/path/to/private/e0-predictions
python3 experiments/E0/reproduce_genuine_tables.py \
  --pred-root "$PRED_ROOT" --write-gpm --skip-pytest --strict
```

See [`experiments/E0/README.md`](experiments/E0/README.md) for prediction layout, Direct API, baselines, and metric definitions.

### E2 PRIMARY (offline; original GPT-4o-mini trees required locally)

```bash
python3 experiments/E2/prepare_dataset.py
PYTHONHASHSEED=0 python3 experiments/E2/evaluate_table_viii_full.py
PYTHONHASHSEED=0 python3 experiments/E2/generate_table_viii.py
```

Details: [`experiments/E2/README.md`](experiments/E2/README.md), [`docs/REPRODUCE_E1_E2.md`](docs/REPRODUCE_E1_E2.md).


## Live E0 Direct inference (paid; optional)

```bash
pip install openai anthropic   # optional providers
export OPENAI_API_KEY=...      # or local openai_api.txt
export ANTHROPIC_API_KEY=...   # or local anthropic.txt

python3 experiments/E0/run_direct_api.py --dry-run
python3 experiments/E0/run_direct_api.py --limit 1 --confirm-paid
```

Never commit API keys or generated `results/predictions/` / `results/metrics/` dumps.

## Citation

See [`CITATION.cff`](CITATION.cff). GitHub identity is separate from paper authorship.
