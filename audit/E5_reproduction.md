# E5 reproduction — Cost and latency (`tab:e5_cost`)

**Status: BLOCKED**

## Required

- API usage logs (input/output tokens)
- Pricing assumptions + date
- Mean latency per schema
- Treatment of failed calls

## Found

| Evidence | Usable for `tab:e5_cost`? |
|---|---|
| PaperMethods `elapsed_s` per record (local HF) | Wall-clock only; not API $ cost |
| Batch `elapsed_s` in SchemaBench/RSchema gpt4omini logs | Parallel batch totals; not per-schema billed cost |
| `deepseek_api_client.py` prints usage | Not persisted into prediction JSON |
| Anthropic / OpenAI billing exports | **Absent** |

## Notes

- Zero API billing ≠ zero compute cost
- No tokenizer/pricing freeze documented for closed models
- Figure 5 / heatmap is **`fig:e0_heatmap` (E0)**, not E5 — do not conflate

## Verdict

**BLOCKED** — distinguish any future reconstructed estimates from observed charges.
