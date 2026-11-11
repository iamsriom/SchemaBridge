# E0 Constructor Verification (Phase 2)

## Prompt identity

| Artifact | SHA-256 | Notes |
|---|---|---|
| `prompts/constructor.txt` | `392a396f7073bc015d206460055f7e3b8a3c94a21ed09c059bc47c13d3884ad4` | Required hash — **PASS** |
| `prompts/e0/direct.txt` | same | Byte-identical copy for PaperMethods packaging |
| Embedded `SYSTEM_PROMPT` in `original_benchmarks/direct/rschema_exp4_text2schema_allLLM.py` | strip-equal | Differs only by trailing newline vs file |

## User message (verified in code)

```text
Database name: <db>

Natural language description:
<gold question>
```

Sources: `_build_user_content` in Exp4 HF script; `run_direct_api.py` builder.

## Leakage checks

1. Gold DDL / `answer` never appended to the constructor user message.
2. No hidden reference table-name hint in Direct gold-NL path (optional hint exists only in some round-trip E2 scripts — not used here).
3. Saved prediction JSON stores the NL `question` field; spot-check of CodeLlama 518/518 found **0** files with `CREATE TABLE` inside `question`.
4. Scorer uses **DDL-authoritative** structure (`legacy=False`); JSON metadata is compared for mismatches, not preferred when DDL parses.

## Decoding settings actually used

| Prediction set | Settings | Evidence |
|---|---|---|
| Open-weight Exp4 (CodeLlama / Llama / DeepSeek) | `do_sample=False` when `GENERATION_TEMPERATURE <= 0.1` (so **temperature 0.1 does not affect sampling**); `max_new_tokens=2048` (some early records may have used 4096 before mid-run change); `top_p=1.0` only if sampling | Original script + transcript `20260616_*` |
| Closed Direct API runner (current package) | temp **0.2**, max_tokens **4096** | `experiments/E0/config.yaml`, `run_direct_api.py` |
| Historical Claude/GPT saved trees | Produced by Exp4 API/batch scripts under `original_benchmarks/direct/`; packaged trees hash-verified as ORIGINAL in `audit/E0_DIRECT_PREDICTION_VERIFICATION.csv` | Do not regenerate for this verification |

## Model identifiers (open Exp4)

| Key | HF id | Notes |
|---|---|---|
| codellama13b | `codellama/CodeLlama-13b-Instruct-hf` | 2×GPU fp16 |
| llama31 | `meta-llama/Meta-Llama-3.1-8B-Instruct` | 2×GPU fp16 |
| deepseek | `deepseek-ai/deepseek-coder-6.7b-instruct` | 1×GPU fp16 |
| mixtral | Mixtral-8x7B 4-bit | **Not** in Table V |

## Output contract

Predictions are `NNNN.json` + `NNNN.txt` with fields: `text_number`, `id`, `llm`, `model_id`, `database`, `question`, `ddl`, `metadata`. TXT/JSON DDL equality after CRLF/whitespace normalization required for resume / coverage COMPLETE.
