# E1 reproduction — Schema2Text (`tab:e1_s2t`)

**Status: VERIFIED** — see `E1_AUDIT_VERDICT.md` and `experiments/E1/outputs/verified/`.

## Protocol

- Enterprise-145: SCR only, N=145
- RSchema: N=**381** DDL-matched IDs
- SchemaBench: N=239
- BLEU-4: `sacrebleu.corpus_bleu(hyps, [refs])` (correct layout)
- Basic = Exp1 / Schema2Text1; Detailed = Experiment2 / Schema2Text2 / SchemaBench/Experiment
- **Never** `results/predictions/e1/schemabench_*`

## Quick recompute

```bash
python3 experiments/E1/evaluate.py          # BLEU/ROUGE/SCR → experiments/E1/outputs/verified/
python3 experiments/E1/evaluate.py --bert   # + BERTScore (GPU; use screen)
# equivalent:
python3 audit/e1_independent_reproduce.py
```

## Deliverables

| File | Content |
|---|---|
| `E1_CODE_PROVENANCE.md` | Scripts, prompts, trees, evaluators |
| `experiments/E1/outputs/verified/E1_REPRODUCTION_COMPARISON.csv` | Manuscript vs recomputed (90 MATCH) |
| `experiments/E1/outputs/verified/E1_BRIEF_CORRECTIONS.csv` | 9 brief → manuscript corrections |
| `E1_VERIFIED_TABLE.tex` / `outputs/verified/tab_e1_s2t_verified.tex` | Corrected `tab:e1_s2t` |
| `E1_PAPER_TEXT_AUDIT.md` | Setup LaTeX replacement |
| `E1_AUDIT_VERDICT.md` | Final counts and readiness |

Do **not** regenerate paid-API outputs for this audit; open-weight Detailed regeneration is optional via `experiments/E1/run_e1_corrected_gpu.py`.
