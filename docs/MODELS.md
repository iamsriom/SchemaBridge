# Models

Open: CodeLlama-13B, Llama-3.1-8B, DeepSeek-Coder-6.7B.
Closed: Claude Sonnet 4.6, GPT-5.4-mini, GPT-4o-mini (constructor).

| key | model id | provider | paid |
|---|---|---|---|
| `codellama13b` | `codellama/CodeLlama-13b-Instruct-hf` | Hugging Face (local) | no |
| `llama31` | `meta-llama/Meta-Llama-3.1-8B-Instruct` | Hugging Face (local) | no |
| `deepseek` | `deepseek-ai/deepseek-coder-6.7b-instruct` | Hugging Face (local) | no |
| `sonnet46` | `claude-sonnet-4-6` | Anthropic (`ANTHROPIC_API_KEY`) | yes |
| `gpt54mini` | `gpt-5.4-mini` | OpenAI (`OPENAI_API_KEY`) | yes |
| `gpt4omini` | `gpt-4o-mini` (E2 constructor only) | OpenAI (`OPENAI_API_KEY`) | yes |

Settings: temperature 0.2; max new tokens 3072 (open models), 1024 basic / 2048 detailed (APIs), 16384 (constructor).
Paid models require `--execute --confirm-paid`; dry-run is the default and never touches the network.
Keys are read only from the environment.
