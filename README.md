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
| **E0** | Text2Schema from NL | [docs/experiments/E0.md](docs/experiments/E0.md) | Offline Tables V–VI (genuine-gold); closed Direct via API runner |
| **E1** | Schema verbalization | [experiments/E1/README.md](experiments/E1/README.md) | Open-weight Detailed (Prompt B) reproducible on RSchema-381 + SchemaBench-239 |
| **E2** | Round-trip preservation | [docs/experiments/E2.md](docs/experiments/E2.md) | PARTIAL — RSchema open detailed mostly matches |
| **E3** | Constructor isolation | [docs/experiments/E3.md](docs/experiments/E3.md) | UNVERIFIED — frozen descriptions missing |
| **E4** | Masking / inferability | [docs/experiments/E4.md](docs/experiments/E4.md) | UNVERIFIED — Tables X–XI not recovered |
| **E5** | Scalability and cost | [docs/experiments/E5.md](docs/experiments/E5.md) | REPRODUCED, PROVENANCE INCOMPLETE (N=30) |

## Quick start (offline)

```bash
git clone https://github.com/iamsriom/SchemaBridge.git
cd SchemaBridge
pip install -r requirements.txt
python3 -m pytest -q

# Authoritative E0 Tables V+VI from local prediction dumps
python3 experiments/E0/evaluate.py
```

See [`experiments/E0/README.md`](experiments/E0/README.md) for the full E0 pipeline (Direct API, baselines, metric definitions).

## E1 Schema2Text (open-weight Detailed)

```bash
pip install -r experiments/E1/requirements-e1.txt
python3 experiments/E1/run_e1_corrected_gpu.py --dataset all --model all --dry-run
# CUDA_VISIBLE_DEVICES=0,1 python3 experiments/E1/run_e1_corrected_gpu.py --dataset SchemaBench --model llama31 --generate
# python3 experiments/E1/evaluate_e1_corrected.py --bertscore-device cuda:0
```

Full instructions: [`experiments/E1/README.md`](experiments/E1/README.md). Predictions and metrics stay local (gitignored).

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
