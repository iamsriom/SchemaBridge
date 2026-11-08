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
| **E0** | Text2Schema from NL | [docs/experiments/E0.md](docs/experiments/E0.md) | PARTIAL / MISMATCH — open RSchema archived; closed missing |
| **E1** | Schema verbalization | [docs/experiments/E1.md](docs/experiments/E1.md) | PARTIAL — RSchema open detailed BLEU/ROUGE/SCR match |
| **E2** | Round-trip preservation | [docs/experiments/E2.md](docs/experiments/E2.md) | PARTIAL — RSchema open detailed mostly matches |
| **E3** | Constructor isolation | [docs/experiments/E3.md](docs/experiments/E3.md) | UNVERIFIED — frozen descriptions missing |
| **E4** | Masking / inferability | [docs/experiments/E4.md](docs/experiments/E4.md) | UNVERIFIED — Tables X–XI not recovered |
| **E5** | Scalability and cost | [docs/experiments/E5.md](docs/experiments/E5.md) | REPRODUCED, PROVENANCE INCOMPLETE (N=30) |

Evidence: [`audit/PHASE12_VERIFICATION_REPORT.md`](audit/PHASE12_VERIFICATION_REPORT.md).

## Quick start (offline)

```bash
git clone https://github.com/iamsriom/SchemaBridge.git
cd SchemaBridge
pip install -r requirements.txt
python scripts/reproduce_tables.py --all --offline
python scripts/reproduce_tables.py --experiment E0 --recompute
python scripts/offline_e1_rschema_detailed.py
pytest -q
```

Open-weight E0–E2 predictions are real files under `results/predictions/` (not host symlinks). SchemaAgent / PaperMethods trees are excluded.

## Live inference

Copy `.env.example` to `.env` and set keys only if you opt into paid runs under `experiments/e5_small/` or `experiments/*/run.py`.

## Citation

See [`CITATION.cff`](CITATION.cff). GitHub identity is separate from paper authorship.
