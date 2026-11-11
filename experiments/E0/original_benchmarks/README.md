# E0 original benchmarking code (LLM4DBdesign / Exp4)

This directory packages the **historical generation and evaluation scripts** used for E0, with provenance notes.

## Included

| Path | Role |
|---|---|
| `direct/` | RSchema + SchemaBench Direct Text2Schema generators (HF + API batch) |
| `one_shot/`, `one_shot_cot/`, `few_shot/` | Prompt helpers + thin `baseline_decode.py` (base_direct / base_cot only) |
| `evaluation/` | Historical Exp4 evaluator, Exp3 combiner, PaperMethods Exp4-metrics scorer |
| `prompts/` | Snapshot of Direct / one-shot / CoT / few-shot prompt text |

## Excluded

- **SchemaAgent multi-agent implementation** (not successfully reproduced; not required for Table VI prompting baselines).
- Live API keys / local HF caches.

## Hard-coded paths

Original scripts often reference `/data/...` or `/mnt/text2er-data/...`. For offline **metric** reproduction prefer:

```bash
python3 experiments/E0/reproduce_genuine_tables.py
```

which uses the portable SchemaBridge datasets + prediction trees.

## Licensing

Upstream LLM4DBdesign files retain their original headers/license. Redistributed here solely for scientific reproducibility of the prompting baselines and Direct constructors.
