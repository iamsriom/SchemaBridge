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
Dry-run is the default and never touches the network or reads a key. Paid models work, opt-in: they require
BOTH `--execute` and `--confirm-paid` (in code: `get_client(..., dry_run=False, confirm_paid=True)`, otherwise
`PaidCallNotConfirmed`) and the key in the environment (`ANTHROPIC_API_KEY` / `OPENAI_API_KEY`, otherwise
`MissingApiKey`). Keys are read only from the environment and never printed or stored; this repository
contains none. Calls are billed per token by the provider, so start with `--limit 1`. The `anthropic` /
`openai` SDKs are imported lazily (`pip install anthropic openai`). For `gpt-5*` model ids the OpenAI client
sends `max_completion_tokens` (other OpenAI models: `max_tokens`).
