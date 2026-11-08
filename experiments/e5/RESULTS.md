# E5 Results — Scalability and Cost

Generated from `/data/SchemaBridge/experiments/e5/outputs`.

## Run metadata

```json
{
  "finished_utc": "2026-11-06T09:09:08.468053+00:00",
  "mode": "full",
  "n_schemas": 120,
  "n_per_schema_rows": 1080,
  "n_raw_rows": 798,
  "n_failures": 1002,
  "spend": {
    "max_spend_usd": 25.0,
    "spent_usd": 0.0,
    "remaining_usd": 25.0
  },
  "openai_available": false,
  "openai_reason": "AuthenticationError: Error code: 401 - {'error': {'message': 'Incorrect API key provided: [redacted]. You can find your API key at https://platform.openai.com/account/api-keys.', 'type': 'invalid_request_error', 'code': 'invalid_api_key', 'param': None}, 'status': 401}",
  "anthropic_available": false,
  "anthropic_reason": "ANTHROPIC_API_KEY missing",
  "deepseek_ready": true,
  "elapsed_s": 30.09917974472046,
  "execution_env": {
    "concurrency": 1,
    "seed": 42,
    "host": "text2er-new",
    "python": "/data/Text2ER/.venv/bin/python"
  }
}
```

## E5-A Scalability (main: size tier = All)

| Dataset | Model | Prompt | N | Ref F1 | Domain F1 | nGED | p50(s) | p95(s) | Cost | Succ% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| enterprise145 | claude_sonnet_4_6 | basic | 41 | 0.000 | 0.002 | 0.976 | 13.21 | 13.21 | 0.017 | 2.4 |
| enterprise145 | claude_sonnet_4_6 | detailed | 41 | 0.000 | 0.002 | 0.976 | 15.32 | 15.32 | 0.021 | 2.4 |
| enterprise145 | deepseek | basic | 40 | 0.000 | 0.000 | 1.000 | 41.78 | 55.43 | N/A | 0.0 |
| enterprise145 | deepseek | detailed | 40 | 0.000 | 0.000 | 1.000 | 103.31 | 316.34 | N/A | 0.0 |
| enterprise145 | gpt_5_4_mini | basic | 40 | 0.000 | 0.000 | 1.000 | N/A | N/A | N/A | 0.0 |
| enterprise145 | gpt_5_4_mini | detailed | 40 | 0.000 | 0.000 | 1.000 | N/A | N/A | N/A | 0.0 |
| rschema | claude_sonnet_4_6 | basic | 41 | 0.026 | 0.032 | 0.951 | 22.88 | 26.03 | 0.020 | 4.9 |
| rschema | claude_sonnet_4_6 | detailed | 41 | 0.013 | 0.016 | 0.976 | 25.75 | 25.75 | 0.038 | 2.4 |
| rschema | deepseek | basic | 40 | 0.887 | 0.146 | 0.634 | 46.78 | 97.51 | 0.0018 | 100.0 |
| rschema | deepseek | detailed | 40 | 0.000 | 0.000 | 1.000 | 77.97 | 269.17 | N/A | 0.0 |
| rschema | gpt_5_4_mini | basic | 40 | 0.013 | 0.016 | 0.975 | 22.02 | 22.02 | 0.0023 | 2.5 |
| rschema | gpt_5_4_mini | detailed | 40 | 0.013 | 0.016 | 0.975 | 20.48 | 20.48 | 0.0032 | 2.5 |
| schemabench | claude_sonnet_4_6 | basic | 41 | 0.013 | 0.009 | 0.951 | 17.94 | 19.54 | 0.015 | 4.9 |
| schemabench | claude_sonnet_4_6 | detailed | 41 | 0.007 | 0.004 | 0.976 | 19.99 | 19.99 | 0.029 | 2.4 |
| schemabench | deepseek | basic | 40 | 0.611 | 0.383 | 0.453 | 42.10 | 42.62 | 0.0032 | 95.0 |
| schemabench | deepseek | detailed | 40 | 0.000 | 0.000 | 1.000 | 75.08 | 270.58 | N/A | 0.0 |
| schemabench | gpt_5_4_mini | basic | 40 | 0.007 | 0.004 | 0.975 | 13.12 | 13.12 | 0.0019 | 2.5 |
| schemabench | gpt_5_4_mini | detailed | 40 | 0.007 | 0.004 | 0.975 | 14.41 | 14.41 | 0.0028 | 2.5 |

## E5-A Scalability (extended by size tier)

| Dataset | Model | Prompt | Size | N | Ref F1 | Domain F1 | nGED | p50 | Cost | Succ% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| enterprise145 | claude_sonnet_4_6 | basic | Large | 8 | 0.000 | 0.000 | 1.000 | N/A | N/A | 0.0 |
| enterprise145 | claude_sonnet_4_6 | basic | Medium | 12 | 0.000 | 0.000 | 1.000 | N/A | N/A | 0.0 |
| enterprise145 | claude_sonnet_4_6 | basic | Small | 21 | 0.000 | 0.018 | 0.952 | 13.21 | 0.017 | 4.8 |
| enterprise145 | claude_sonnet_4_6 | detailed | Large | 8 | 0.000 | 0.000 | 1.000 | N/A | N/A | 0.0 |
| enterprise145 | claude_sonnet_4_6 | detailed | Medium | 12 | 0.000 | 0.000 | 1.000 | N/A | N/A | 0.0 |
| enterprise145 | claude_sonnet_4_6 | detailed | Small | 21 | 0.000 | 0.018 | 0.952 | 15.32 | 0.021 | 4.8 |
| enterprise145 | deepseek | basic | Large | 8 | 0.000 | 0.000 | 1.000 | 41.78 | N/A | 0.0 |
| enterprise145 | deepseek | basic | Medium | 12 | 0.000 | 0.000 | 1.000 | 42.76 | N/A | 0.0 |
| enterprise145 | deepseek | basic | Small | 20 | 0.000 | 0.000 | 1.000 | 36.45 | N/A | 0.0 |
| enterprise145 | deepseek | detailed | Large | 8 | 0.000 | 0.000 | 1.000 | 341.36 | N/A | 0.0 |
| enterprise145 | deepseek | detailed | Medium | 12 | 0.000 | 0.000 | 1.000 | 148.41 | N/A | 0.0 |
| enterprise145 | deepseek | detailed | Small | 20 | 0.000 | 0.000 | 1.000 | 62.57 | N/A | 0.0 |
| enterprise145 | gpt_5_4_mini | basic | Large | 8 | 0.000 | 0.000 | 1.000 | N/A | N/A | 0.0 |
| enterprise145 | gpt_5_4_mini | basic | Medium | 12 | 0.000 | 0.000 | 1.000 | N/A | N/A | 0.0 |
| enterprise145 | gpt_5_4_mini | basic | Small | 20 | 0.000 | 0.000 | 1.000 | N/A | N/A | 0.0 |
| enterprise145 | gpt_5_4_mini | detailed | Large | 8 | 0.000 | 0.000 | 1.000 | N/A | N/A | 0.0 |
| enterprise145 | gpt_5_4_mini | detailed | Medium | 12 | 0.000 | 0.000 | 1.000 | N/A | N/A | 0.0 |
| enterprise145 | gpt_5_4_mini | detailed | Small | 20 | 0.000 | 0.000 | 1.000 | N/A | N/A | 0.0 |
| rschema | claude_sonnet_4_6 | basic | Large | 1 | 0.000 | 0.000 | 1.000 | N/A | N/A | 0.0 |
| rschema | claude_sonnet_4_6 | basic | Medium | 12 | 0.000 | 0.000 | 1.000 | N/A | N/A | 0.0 |
| rschema | claude_sonnet_4_6 | basic | Small | 28 | 0.049 | 0.065 | 0.929 | 22.88 | 0.020 | 7.1 |
| rschema | claude_sonnet_4_6 | detailed | Large | 1 | 0.000 | 0.000 | 1.000 | N/A | N/A | 0.0 |
| rschema | claude_sonnet_4_6 | detailed | Medium | 12 | 0.000 | 0.000 | 1.000 | N/A | N/A | 0.0 |
| rschema | claude_sonnet_4_6 | detailed | Small | 28 | 0.025 | 0.033 | 0.964 | 25.75 | 0.038 | 3.6 |
| rschema | deepseek | basic | Large | 1 | 0.000 | 0.030 | 0.793 | 109.87 | 0.0047 | 100.0 |
| rschema | deepseek | basic | Medium | 12 | 0.937 | 0.175 | 0.620 | 47.44 | 0.0026 | 100.0 |
| rschema | deepseek | basic | Small | 27 | 0.969 | 0.136 | 0.635 | 34.19 | 0.0013 | 100.0 |
| rschema | deepseek | detailed | Large | 1 | 0.000 | 0.000 | 1.000 | 316.25 | N/A | 0.0 |
| rschema | deepseek | detailed | Medium | 12 | 0.000 | 0.000 | 1.000 | 79.41 | N/A | 0.0 |
| rschema | deepseek | detailed | Small | 27 | 0.000 | 0.000 | 1.000 | 63.07 | N/A | 0.0 |
| rschema | gpt_5_4_mini | basic | Large | 1 | 0.000 | 0.000 | 1.000 | N/A | N/A | 0.0 |
| rschema | gpt_5_4_mini | basic | Medium | 12 | 0.000 | 0.000 | 1.000 | N/A | N/A | 0.0 |
| rschema | gpt_5_4_mini | basic | Small | 27 | 0.025 | 0.034 | 0.963 | 22.02 | 0.0023 | 3.7 |
| rschema | gpt_5_4_mini | detailed | Large | 1 | 0.000 | 0.000 | 1.000 | N/A | N/A | 0.0 |
| rschema | gpt_5_4_mini | detailed | Medium | 12 | 0.000 | 0.000 | 1.000 | N/A | N/A | 0.0 |
| rschema | gpt_5_4_mini | detailed | Small | 27 | 0.025 | 0.034 | 0.963 | 20.48 | 0.0032 | 3.7 |
| schemabench | claude_sonnet_4_6 | basic | Large | 7 | 0.000 | 0.000 | 1.000 | N/A | N/A | 0.0 |
| schemabench | claude_sonnet_4_6 | basic | Medium | 16 | 0.000 | 0.000 | 1.000 | N/A | N/A | 0.0 |
| schemabench | claude_sonnet_4_6 | basic | Small | 18 | 0.069 | 0.050 | 0.889 | 17.94 | 0.015 | 11.1 |
| schemabench | claude_sonnet_4_6 | detailed | Large | 7 | 0.000 | 0.000 | 1.000 | N/A | N/A | 0.0 |
| schemabench | claude_sonnet_4_6 | detailed | Medium | 16 | 0.000 | 0.000 | 1.000 | N/A | N/A | 0.0 |
| schemabench | claude_sonnet_4_6 | detailed | Small | 18 | 0.035 | 0.025 | 0.944 | 19.99 | 0.029 | 5.6 |
| schemabench | deepseek | basic | Large | 7 | 0.462 | 0.305 | 0.576 | 42.25 | 0.0061 | 71.4 |
| schemabench | deepseek | basic | Medium | 16 | 0.602 | 0.442 | 0.467 | 42.40 | 0.0040 | 100.0 |
| schemabench | deepseek | basic | Small | 17 | 0.939 | 0.395 | 0.388 | 37.41 | 0.0016 | 100.0 |
| schemabench | deepseek | detailed | Large | 7 | 0.000 | 0.000 | 1.000 | 308.04 | N/A | 0.0 |
| schemabench | deepseek | detailed | Medium | 16 | 0.000 | 0.000 | 1.000 | 64.30 | N/A | 0.0 |
| schemabench | deepseek | detailed | Small | 17 | 0.000 | 0.000 | 1.000 | 97.91 | N/A | 0.0 |
| schemabench | gpt_5_4_mini | basic | Large | 7 | 0.000 | 0.000 | 1.000 | N/A | N/A | 0.0 |
| schemabench | gpt_5_4_mini | basic | Medium | 16 | 0.000 | 0.000 | 1.000 | N/A | N/A | 0.0 |
| schemabench | gpt_5_4_mini | basic | Small | 17 | 0.036 | 0.025 | 0.941 | 13.12 | 0.0019 | 5.9 |
| schemabench | gpt_5_4_mini | detailed | Large | 7 | 0.000 | 0.000 | 1.000 | N/A | N/A | 0.0 |
| schemabench | gpt_5_4_mini | detailed | Medium | 16 | 0.000 | 0.000 | 1.000 | N/A | N/A | 0.0 |
| schemabench | gpt_5_4_mini | detailed | Small | 17 | 0.036 | 0.025 | 0.941 | 14.41 | 0.0028 | 5.9 |

## E5-B Cost--Fidelity

| Dataset | Constructor | N | T | A | D | E | R | nGED | Cost | p50 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| enterprise145 | claude_sonnet_4_6 | 41 | 0.007 | 0.002 | 0.002 | 0.008 | 0.000 | 0.976 | 0.021 | 15.32 |
| enterprise145 | gpt_4o_mini | 40 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 | N/A | N/A |
| enterprise145 | gpt_5_4_mini | 40 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 | N/A | N/A |
| rschema | claude_sonnet_4_6 | 41 | 0.020 | 0.016 | 0.016 | 0.020 | 0.013 | 0.976 | 0.038 | 25.75 |
| rschema | gpt_4o_mini | 40 | 0.020 | 0.016 | 0.016 | 0.020 | 0.013 | 0.975 | 0.0032 | 17.03 |
| rschema | gpt_5_4_mini | 40 | 0.020 | 0.016 | 0.016 | 0.020 | 0.013 | 0.975 | 0.0068 | 6.85 |
| schemabench | claude_sonnet_4_6 | 41 | 0.010 | 0.004 | 0.004 | 0.011 | 0.007 | 0.976 | 0.029 | 19.99 |
| schemabench | gpt_4o_mini | 40 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 | N/A | N/A |
| schemabench | gpt_5_4_mini | 40 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 | N/A | N/A |

## E5-C Prompt efficiency

| Dataset | Describer | N | RefB | RefD | nGEDB | nGEDD | CostB | CostD | ΔCost | ΔRef | Marg$/pp |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| enterprise145 | claude_sonnet_4_6 | 40 | 0.000 | 0.000 | 0.000 | 0.000 | 0.017 | 0.021 | 0.0035 | 0.000 | N/A |
| enterprise145 | deepseek | 40 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| enterprise145 | gpt_5_4_mini | 40 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| rschema | claude_sonnet_4_6 | 40 | 1.000 | 1.000 | 0.000 | 0.000 | 0.032 | 0.038 | 0.0062 | 0.000 | N/A |
| rschema | deepseek | 40 | 0.887 | N/A | 0.634 | N/A | 0.0018 | N/A | N/A | N/A | N/A |
| rschema | gpt_5_4_mini | 40 | 1.000 | 1.000 | 0.000 | 0.000 | 0.0023 | 0.0032 | 0.0010 | 0.000 | N/A |
| schemabench | claude_sonnet_4_6 | 40 | 1.000 | 1.000 | 0.000 | 0.000 | 0.023 | 0.029 | 0.0052 | 0.000 | N/A |
| schemabench | deepseek | 40 | 0.674 | N/A | 0.424 | N/A | 0.0032 | N/A | N/A | N/A | N/A |
| schemabench | gpt_5_4_mini | 40 | 1.000 | 1.000 | 0.000 | 0.000 | 0.0019 | 0.0028 | 0.0010 | 0.000 | N/A |

## Pareto-optimal configurations

- **gpt_5_4_mini/basic**: cost=0.0021, ref_f1=0.006
- **deepseek/basic**: cost=0.0025, ref_f1=0.572

## Reliability summary (E5-A rows)

- Attempted pipeline rows: 726
- Desc OK: 90
- Parsed/reconstructed OK: 90
- Truncated describer: 0
- Reused describer: 80
- Reused constructor: 78
- Failure rows logged: 762

