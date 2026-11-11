#!/usr/bin/env python3
"""
SchemaBench Text2Schema: NL questions from annotation_ddl.jsonl -> DDL + metadata.

Reads only the natural-language "question" field from SchemaBench/Dataset/annotation_ddl.jsonl
(all 518 records). Gold DDL answers are NOT fed to the LLM — only the NL question.

Uses the SYSTEM_PROMPT from Text2ER/experiments2/text2schema_allLLM.py (lines 75-101).

Output layout:
    <DATA_ROOT>/SchemaBench/Experiment/text2schema_<llm>/0001.txt   (DDL)
    <DATA_ROOT>/SchemaBench/Experiment/text2schema_<llm>/0001.json  (full record)

LLMs on 4-GPU host (smart pack: 3 parallel in wave 1, mixtral in wave 2):
    codellama13b (2 GPU fp16), llama31, deepseek (1 GPU each), mixtral (4-bit)

Examples:
    python rschema_exp4_text2schema_allLLM.py --dry-run
    python rschema_exp4_text2schema_allLLM.py --limit 2 --llm deepseek
    python rschema_exp4_text2schema_allLLM.py --limit 2 --parallel-llms --gpus-per-llm 2
    python rschema_exp4_text2schema_allLLM.py --parallel-llms --gpus-per-llm 2 --require-gpu
"""

from __future__ import annotations

import argparse
import gc
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

from tqdm import tqdm

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_ROOT = Path("/data") if Path("/data").is_dir() else SCRIPT_DIR.parent.parent
TEXT2ER_ROOT = DATA_ROOT / "Text2ER"
DATASET_DIR = DATA_ROOT / "SchemaBench" / "Dataset"
ANNOTATION_PATH = DATASET_DIR / "annotation_ddl.jsonl"
BASE_OUT = DATA_ROOT / "SchemaBench" / "Experiment"
HF_CACHE_ROOT = TEXT2ER_ROOT / "hf_cache"
TORCH_CACHE_ROOT = DATA_ROOT / "torch_cache"
TMP_ROOT = DATA_ROOT / "tmp"

TRANSLATOR_CONFIG: dict[str, str] = {
    "codellama13b": "codellama/CodeLlama-13b-Instruct-hf",
    "llama31": "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "mixtral": "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "deepseek": "deepseek-ai/deepseek-coder-6.7b-instruct",
}

NEEDS_4BIT: set[str] = {"mixtral"}

LLM_GPU_REQUIREMENTS: dict[str, int] = {
    "deepseek": 1,       # 6.7B fp16 fits 1xT4
    "llama31": 2,        # 8B fp16 needs 2xT4
    "mixtral": 1,        # 4-bit fits 1xT4
    "codellama13b": 2,   # 13B fp16 needs 2xT4
}

MAX_NEW_TOKENS = 2048
MAX_INPUT_TOKENS = 4096
CACHE_CLEAR_EVERY_N = 10
STOP_CHECK_EVERY_N = 48
GENERATION_TEMPERATURE = 0.1
GENERATION_TOP_P = 1.0

SYSTEM_PROMPT = """You are an expert at inferring relational database schemas from natural language descriptions.

Your task is to output a valid database schema that matches the description. You must respond with exactly one JSON object (no markdown, no extra text) with two keys:

1. "ddl": A string containing MySQL-style DDL. Use this exact format:
   - Start with a comment: -- Schema for database: <DatabaseName>
   - For each table: CREATE TABLE `table_name` ( ... ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
   - Include column definitions with types (e.g. int(11), varchar(255), datetime, char(6)).
   - Use NOT NULL or DEFAULT NULL as appropriate.
   - Include PRIMARY KEY and FOREIGN KEY constraints. Use CONSTRAINT names like `table_ibfk_1`, REFERENCES with ON DELETE CASCADE ON UPDATE CASCADE where logical.
   - Use backticks for table and column names.

2. "metadata": A JSON object with this exact structure:
   - "database": string (database name)
   - "tables": array of table names (strings)
   - "columns_by_table": object mapping each table name to an array of column objects. Each column object must have:
     COLUMN_NAME, ORDINAL_POSITION (1-based), COLUMN_DEFAULT (null or string), IS_NULLABLE ("YES" or "NO"),
     DATA_TYPE, CHARACTER_MAXIMUM_LENGTH (number or null), NUMERIC_PRECISION (number or null), NUMERIC_SCALE (number or null),
     COLUMN_TYPE (e.g. "int(11)", "varchar(255)"), COLUMN_KEY ("PRI", "MUL", "UNI", or ""), EXTRA (string), COLUMN_COMMENT (string).

Infer table and column names that fit the description. Use snake_case for names. Be consistent with the narrative (e.g. accident ID linking tables). Output only the raw JSON object."""


def _load_hf_token() -> str | None:
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if token:
        return token.strip()
    for p in (
        DATA_ROOT / "huggingface_api.txt",
        TEXT2ER_ROOT / "huggingface_api.txt",
        SCRIPT_DIR / "huggingface_api.txt",
    ):
        if p.is_file():
            t = p.read_text().strip()
            if t:
                return t
    return None


HF_TOKEN = _load_hf_token()


def _init_data_paths() -> None:
    hf_home = HF_CACHE_ROOT
    hub_cache = hf_home / "hub"
    os.environ.setdefault("HF_HOME", str(hf_home))
    os.environ.setdefault("HUGGINGFACE_HUB_CACHE", str(hub_cache))
    os.environ.setdefault("TRANSFORMERS_CACHE", str(hub_cache))
    os.environ.setdefault("TORCH_HOME", str(TORCH_CACHE_ROOT))
    os.environ.setdefault("TMPDIR", str(TMP_ROOT))
    os.environ.setdefault("XDG_CACHE_HOME", str(DATA_ROOT / "cache"))
    for p in (hub_cache, TORCH_CACHE_ROOT, TMP_ROOT, DATA_ROOT / "cache"):
        p.mkdir(parents=True, exist_ok=True)


_init_data_paths()


def _sanitize_model_text(text: str) -> str:
    """Fix SentencePiece/GPT-BPE space markers (Ġ, ▁, Ċ) leaked into decoded text."""
    if not text:
        return text
    text = text.replace("\u0120", " ")
    text = text.replace("\u010a", "\n")
    text = text.replace("Ċ", "\n")
    text = text.replace("▁", " ")
    return text


def _record_is_valid(out_json: Path) -> bool:
    if not out_json.is_file():
        return False
    try:
        data = json.loads(out_json.read_text(encoding="utf-8"))
    except Exception:
        return False
    return bool((data.get("ddl") or "").strip()) and not data.get("error")


def _response_is_degenerate(raw: str) -> bool:
    if not raw or len(raw.strip()) < 20:
        return True
    cleaned = _sanitize_model_text(raw).strip().lower()
    if "ddl" not in cleaned and "create table" not in cleaned:
        return True
    try:
        obj = extract_json_from_response(raw)
    except Exception:
        return True
    return not (isinstance(obj, dict) and (obj.get("ddl") or "").strip())


def _sanitize_ddl(ddl: str) -> str:
    """Clean DDL: BPE markers and stray backslashes from malformed JSON line escapes."""
    ddl = _sanitize_model_text(ddl)
    # JSON "\\\n" between lines -> newline + backslash + newline in parsed ddl.
    ddl = re.sub(r"\n\\\s*\n", "\n", ddl)
    ddl = re.sub(r"^\s*\\\s*$", "", ddl, flags=re.MULTILINE)
    ddl = re.sub(r"\\\s*\n", "\n", ddl)
    ddl = re.sub(r"\n{3,}", "\n\n", ddl)
    return ddl.strip()


def _sanitize_schema_result(result: dict, database: str) -> dict:
    ddl = _sanitize_ddl(result.get("ddl", "") or "")
    result["ddl"] = ddl
    metadata = result.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {"database": database, "tables": [], "columns_by_table": {}}
    metadata.setdefault("database", database)
    if not metadata.get("tables") and ddl:
        tables = re.findall(r"CREATE\s+TABLE\s+[`']?(\w+)[`']?", ddl, re.IGNORECASE)
        metadata["tables"] = list(dict.fromkeys(tables))
    result["metadata"] = metadata
    return result


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    text_number = 0
    with path.open(encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"{path}:{i}: {e}") from e
            text_number += 1
            rec["_text_number"] = text_number
            rows.append(rec)
    return rows


def serial_stem(text_number: int) -> str:
    return f"{text_number:04d}"


def output_paths(out_dir: Path, text_number: int) -> tuple[Path, Path]:
    stem = serial_stem(text_number)
    return out_dir / f"{stem}.txt", out_dir / f"{stem}.json"


def extract_json_from_response(text: str) -> dict:
    text = _sanitize_model_text(text).strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```\s*$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        start = text.find("{")
        if start == -1:
            raise
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start : i + 1])
                    except json.JSONDecodeError:
                        break
        if "Expecting ','" in str(e) and hasattr(e, "pos") and e.pos is not None:
            try:
                repaired = text[: e.pos] + "," + text[e.pos :]
                return json.loads(repaired)
            except json.JSONDecodeError:
                pass
        repair = _repair_truncated_json(text[start:])
        if repair:
            return json.loads(repair)
        raise


def _extract_ddl_from_broken_response(text: str) -> dict | None:
    idx = text.find('"ddl"')
    if idx == -1:
        return None
    idx = text.find('"', idx + 5)
    if idx == -1:
        return None
    start = idx + 1
    parts: list[str] = []
    i = start
    while i < len(text):
        c = text[i]
        if c == "\\" and i + 1 < len(text):
            parts.append(text[i : i + 2])
            i += 2
            continue
        if c == '"':
            j = i + 1
            while j < len(text) and text[j] in " \t\n\r":
                j += 1
            if j < len(text) and (text[j] in ",}" or text[j : j + 10] == '"metadata"'):
                break
        parts.append(c)
        i += 1
    else:
        return None
    ddl = _sanitize_ddl("".join(parts).replace("\\n", "\n").replace('\\"', '"'))
    tables = re.findall(r"CREATE\s+TABLE\s+[`']?(\w+)[`']?", ddl, re.IGNORECASE)
    tables = list(dict.fromkeys(tables))
    return {
        "ddl": ddl,
        "metadata": {"database": "", "tables": tables, "columns_by_table": {t: [] for t in tables}},
    }


def _repair_truncated_json(fragment: str) -> str | None:
    if '"ddl"' not in fragment:
        return None
    suffix = '", "metadata": {"database": "", "tables": [], "columns_by_table": {}}}'
    closed = fragment.rstrip()
    if not closed.endswith('"'):
        closed += '"'
    closed += suffix
    try:
        json.loads(closed)
        return closed
    except json.JSONDecodeError:
        return None


def _ddl_only_fallback(text: str, database: str) -> dict | None:
    m = re.search(r"(CREATE\s+TABLE[\s\S]*)", text, re.IGNORECASE)
    if not m:
        return None
    ddl = _sanitize_ddl(m.group(1).strip())
    ddl = re.sub(r"```.*$", "", ddl, flags=re.DOTALL).strip()
    if not ddl:
        return None
    tables = re.findall(r"CREATE\s+TABLE\s+[`']?(\w+)[`']?", ddl, re.IGNORECASE)
    tables = list(dict.fromkeys(tables))
    return {
        "ddl": f"-- Schema for database: {database}\n{ddl}",
        "metadata": {
            "database": database,
            "tables": tables,
            "columns_by_table": {t: [] for t in tables},
        },
    }


def log_gpu_status() -> int:
    import torch

    if not torch.cuda.is_available():
        print("  CUDA: not available", flush=True)
        return 0
    n = torch.cuda.device_count()
    print(f"  CUDA (PyTorch): {n} GPU(s) visible", flush=True)
    for i in range(n):
        props = torch.cuda.get_device_properties(i)
        mem_gib = props.total_memory / (1024**3)
        print(f"    [{i}] {props.name} — {mem_gib:.1f} GiB", flush=True)
    return n


def _build_max_memory() -> dict | None:
    import torch

    if not torch.cuda.is_available():
        return None
    max_memory: dict = {}
    for i in range(torch.cuda.device_count()):
        props = torch.cuda.get_device_properties(i)
        gib = max(1, int(props.total_memory * 0.92 / (1024**3)))
        max_memory[i] = f"{gib}GiB"
    return max_memory


def _gpu_groups_for_parallel_llms(
    llm_names: list[str],
    gpus_per_llm: int = 1,
) -> dict[str, str]:
    import torch

    n_gpu = torch.cuda.device_count()
    if n_gpu == 0 or not llm_names:
        return {name: "" for name in llm_names}
    gpus_per_llm = max(1, min(gpus_per_llm, n_gpu))
    out: dict[str, str] = {}
    for i, name in enumerate(llm_names):
        start = (i * gpus_per_llm) % n_gpu
        indices = [(start + j) % n_gpu for j in range(gpus_per_llm)]
        out[name] = ",".join(str(g) for g in indices)
    return out


def _parallel_llm_waves(llm_names: list[str], gpus_per_llm: int = 1) -> list[list[str]]:
    import torch

    n_gpu = torch.cuda.device_count()
    if n_gpu == 0 or not llm_names:
        return [llm_names]
    gpus_per_llm = max(1, min(gpus_per_llm, n_gpu))
    max_parallel = max(1, n_gpu // gpus_per_llm)
    waves: list[list[str]] = []
    for i in range(0, len(llm_names), max_parallel):
        waves.append(llm_names[i : i + max_parallel])
    return waves


def _pack_llm_waves_smart(
    llm_names: list[str],
    gpus_per_model: dict[str, int],
    total_gpus: int,
) -> list[list[str]]:
    """Bin-pack LLMs into waves that use available GPUs (largest models first)."""
    if not llm_names:
        return []
    order = sorted(llm_names, key=lambda n: gpus_per_model.get(n, 1), reverse=True)
    waves: list[list[str]] = []
    remaining = order
    while remaining:
        wave: list[str] = []
        used = 0
        still: list[str] = []
        for name in remaining:
            need = gpus_per_model.get(name, 1)
            if used + need <= total_gpus:
                wave.append(name)
                used += need
            else:
                still.append(name)
        if not wave:
            wave = [remaining[0]]
            still = remaining[1:]
        waves.append(wave)
        remaining = still
    return waves


def _assign_gpus_in_wave(
    wave: list[str],
    gpus_per_model: dict[str, int],
) -> dict[str, str]:
    groups: dict[str, str] = {}
    idx = 0
    for name in wave:
        need = gpus_per_model.get(name, 1)
        groups[name] = ",".join(str(idx + j) for j in range(need))
        idx += need
    return groups


def load_model_and_tokenizer(translator_name: str, model_id: str):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    token_kwargs: dict = {}
    if HF_TOKEN:
        token_kwargs["token"] = HF_TOKEN

    tokenizer = AutoTokenizer.from_pretrained(
        model_id, trust_remote_code=True, **token_kwargs
    )
    if tokenizer.pad_token_id is None and tokenizer.eos_token_id is not None:
        tokenizer.pad_token_id = tokenizer.eos_token_id

    use_4bit = translator_name in NEEDS_4BIT
    n_gpu = torch.cuda.device_count() if torch.cuda.is_available() else 0
    if use_4bit or n_gpu <= 1:
        device_map: str | dict = {"": 0}
    else:
        device_map = "auto"
    model_kwargs: dict = {
        "trust_remote_code": True,
        "device_map": device_map,
        "attn_implementation": "sdpa",
        "low_cpu_mem_usage": True,
        **token_kwargs,
    }
    if not use_4bit and n_gpu > 1:
        max_mem = _build_max_memory()
        if max_mem:
            model_kwargs["max_memory"] = max_mem

    if use_4bit:
        try:
            from transformers import BitsAndBytesConfig

            bnb_cfg = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.float16,
            )
            model_kwargs["quantization_config"] = bnb_cfg
        except Exception as e:
            print(
                f"[{translator_name}] WARN: 4-bit quant unavailable ({e}); trying fp16.",
                file=sys.stderr,
                flush=True,
            )
            model_kwargs["torch_dtype"] = torch.float16
    else:
        model_kwargs["torch_dtype"] = torch.float16

    model = AutoModelForCausalLM.from_pretrained(model_id, **model_kwargs)
    return model, tokenizer


class _StopOnCompleteJson:
    """Stop once a parseable JSON object with ddl is produced (checked every N tokens)."""

    def __init__(self, tokenizer, prompt_len: int, check_every: int = STOP_CHECK_EVERY_N):
        self.tokenizer = tokenizer
        self.prompt_len = prompt_len
        self.check_every = max(1, check_every)
        self._steps = 0

    def __call__(self, input_ids, scores, **kwargs) -> bool:
        self._steps += 1
        if self._steps % self.check_every != 0:
            return False
        text = self.tokenizer.decode(
            input_ids[0][self.prompt_len :],
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        )
        text = _sanitize_model_text(text).strip()
        if '"ddl"' not in text or not text.endswith("}"):
            return False
        try:
            obj = extract_json_from_response(text)
            return isinstance(obj, dict) and "ddl" in obj
        except Exception:
            return False


def generate_json_reply(
    model,
    tokenizer,
    system_prompt: str,
    user_content: str,
    max_new_tokens: int = MAX_NEW_TOKENS,
    force_sample: bool = False,
) -> str:
    import torch
    from transformers import StoppingCriteriaList

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]
    text: str | None = None
    if hasattr(tokenizer, "apply_chat_template") and getattr(tokenizer, "chat_template", None):
        try:
            text = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        except Exception:
            text = None
    if text is None:
        combined = f"{system_prompt}\n\n{user_content}"
        text = f"<s>[INST] {combined} [/INST]\n"

    inputs = tokenizer(
        text, return_tensors="pt", truncation=True, max_length=MAX_INPUT_TOKENS
    )
    device = next(model.parameters()).device
    inputs = {k: v.to(device) for k, v in inputs.items()}

    gen_kwargs: dict = {
        "max_new_tokens": max_new_tokens,
        "pad_token_id": tokenizer.pad_token_id or tokenizer.eos_token_id,
        "repetition_penalty": 1.0,
    }
    if force_sample:
        gen_kwargs.update({"do_sample": True, "temperature": 0.3, "top_p": 0.95})
        gen_kwargs["max_new_tokens"] = min(max_new_tokens, 1536)
    elif GENERATION_TEMPERATURE <= 0.1:
        gen_kwargs["do_sample"] = False
    else:
        gen_kwargs.update(
            {
                "do_sample": True,
                "temperature": GENERATION_TEMPERATURE,
                "top_p": GENERATION_TOP_P,
            }
        )
    prompt_len = inputs["input_ids"].shape[1]
    if not force_sample:
        stop = StoppingCriteriaList([_StopOnCompleteJson(tokenizer, prompt_len)])
        gen_kwargs["stopping_criteria"] = stop

    with torch.inference_mode():
        out = model.generate(**inputs, **gen_kwargs)
    return _sanitize_model_text(
        tokenizer.decode(
            out[0][prompt_len:],
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        )
    ).strip()


def _build_user_content(nl_text: str, database: str) -> str:
    return "\n".join(
        [
            f"Database name: {database}",
            "",
            "Natural language description:",
            nl_text,
        ]
    )


def text_to_schema_with_llm(
    model,
    tokenizer,
    nl_text: str,
    database: str,
    max_retries: int = 4,
    max_new_tokens: int = MAX_NEW_TOKENS,
) -> dict:
    user_content = _build_user_content(nl_text, database)
    last_err: Exception | None = None
    last_raw: str | None = None
    for attempt in range(max_retries):
        content = user_content
        if attempt > 0:
            content = (
                user_content
                + "\n\nRespond with one complete JSON object containing non-empty "
                + '"ddl" and "metadata" fields. Do not output an empty object.'
            )
        try:
            raw = generate_json_reply(
                model,
                tokenizer,
                SYSTEM_PROMPT,
                content,
                max_new_tokens=max_new_tokens,
                force_sample=attempt > 0,
            )
            last_raw = raw
            if not raw or _response_is_degenerate(raw):
                raise ValueError("Empty or degenerate model response")
            out = extract_json_from_response(raw)
            if not isinstance(out, dict) or "ddl" not in out:
                raise ValueError("Model response missing 'ddl'")
            if "metadata" not in out:
                out["metadata"] = {"database": database, "tables": [], "columns_by_table": {}}
            return _sanitize_schema_result(out, database)
        except (json.JSONDecodeError, ValueError) as e:
            last_err = e
            gc.collect()
            try:
                import torch

                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except Exception:
                pass
            if attempt + 1 == max_retries:
                fb = last_raw and (
                    _extract_ddl_from_broken_response(last_raw)
                    or _ddl_only_fallback(last_raw, database)
                )
                if fb:
                    return _sanitize_schema_result(fb, database)
                raise last_err
    raise last_err  # type: ignore[misc]


def _database_name(record: dict) -> str:
    n = record.get("_text_number")
    if n is not None:
        return f"schemabench_{int(n):04d}"
    rid = record.get("id") or "schema"
    return f"schemabench_{str(rid)[:12]}"


def _save_record_result(
    out_dir: Path,
    llm_name: str,
    model_id: str,
    rid: str,
    text_number: int,
    nl_text: str,
    database: str,
    result: dict | None,
    error: str | None = None,
) -> None:
    out_txt, out_json = output_paths(out_dir, text_number)
    if result:
        ddl = result.get("ddl", "") or ""
        metadata = result.get("metadata") or {}
        if isinstance(metadata, dict):
            metadata.setdefault("database", database)
            if "tables" not in metadata and "columns_by_table" in metadata:
                metadata["tables"] = list(metadata["columns_by_table"].keys())
        else:
            metadata = {"database": database, "tables": [], "columns_by_table": {}}
        out_txt.write_text(ddl, encoding="utf-8")
        out_obj = {
            "text_number": text_number,
            "id": rid,
            "llm": llm_name,
            "model_id": model_id,
            "database": database,
            "question": nl_text,
            "ddl": ddl,
            "metadata": metadata,
        }
    else:
        out_txt.write_text(f"[ERROR: {error}]\n", encoding="utf-8")
        out_obj = {
            "text_number": text_number,
            "id": rid,
            "llm": llm_name,
            "model_id": model_id,
            "database": database,
            "question": nl_text,
            "error": error,
            "ddl": None,
            "metadata": {"database": database, "tables": [], "columns_by_table": {}},
        }
    out_json.write_text(
        json.dumps(out_obj, indent=2, default=str, ensure_ascii=False),
        encoding="utf-8",
    )


def print_results_summary(base_out: Path, llm_name: str, records: list[dict]) -> None:
    out_dir = base_out / f"text2schema_{llm_name}"
    print("\n" + "=" * 72)
    print(f"Results summary ({llm_name})")
    print("=" * 72)
    for i, rec in enumerate(records, 1):
        rid = rec.get("id") or f"row_{i}"
        text_number = int(rec.get("_text_number") or i)
        path = out_dir / f"{serial_stem(text_number)}.json"
        if not path.is_file():
            print(f"\n[text {text_number:04d}] id={rid}: (no output)")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("error"):
            print(f"\n[text {text_number:04d}] id={rid}: ERROR — {data['error']}")
            continue
        meta = data.get("metadata") or {}
        tables = meta.get("tables") or list((meta.get("columns_by_table") or {}).keys())
        ddl = data.get("ddl") or ""
        n_tables = len(tables) if tables else ddl.lower().count("create table")
        preview = "\n".join(ddl.splitlines()[:8])
        if len(ddl.splitlines()) > 8:
            preview += "\n  ..."
        print(f"\n[text {text_number:04d}] id={rid} -> {path.name}")
        print(f"    tables ({n_tables}): {', '.join(tables) if tables else '(parsed from DDL)'}")
        print(f"    DDL preview:\n{preview}")


def run_one_llm(
    llm_name: str,
    model_id: str,
    records: list[dict],
    base_out: Path,
    skip_existing: bool,
    max_new_tokens: int,
) -> None:
    import torch

    out_dir = base_out / f"text2schema_{llm_name}"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[{llm_name}] Clearing cache...", flush=True)
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    quant = "4-bit nf4" if llm_name in NEEDS_4BIT else "fp16"
    print(f"[{llm_name}] Loading {model_id} (device_map=auto, {quant})...", flush=True)
    t0 = time.time()
    try:
        model, tokenizer = load_model_and_tokenizer(llm_name, model_id)
    except Exception as e:
        err = str(e).lower()
        if any(k in err for k in ("gated", "401", "403", "access", "restricted")):
            print(
                f"[{llm_name}] SKIP: gated model — accept license at "
                f"https://huggingface.co/{model_id} and set HF_TOKEN or huggingface_api.txt",
                file=sys.stderr,
            )
            return
        print(f"[{llm_name}] FATAL load: {e}", file=sys.stderr)
        return
    print(f"[{llm_name}] Loaded in {time.time() - t0:.1f}s", flush=True)

    ok = err_count = skipped = 0
    pbar = tqdm(
        records,
        desc=f"[{llm_name}]",
        unit="rec",
        dynamic_ncols=False,
        mininterval=10.0,
        file=sys.stderr,
    )
    manifest: list[dict] = []
    for i, rec in enumerate(pbar, 1):
        rid = rec.get("id") or f"row_{i}"
        text_number = int(rec.get("_text_number") or i)
        _, out_json = output_paths(out_dir, text_number)
        if skip_existing and _record_is_valid(out_json):
            skipped += 1
            pbar.set_postfix(ok=ok, err=err_count, skip=skipped, refresh=False)
            continue

        nl_text = (rec.get("question") or "").strip()
        if not nl_text:
            skipped += 1
            tqdm.write(f"  [{llm_name}] text {text_number:04d} SKIP (empty question)")
            pbar.set_postfix(ok=ok, err=err_count, skip=skipped, refresh=False)
            continue

        database = _database_name(rec)
        t_q = time.time()
        print(
            f"  [{llm_name}] text {text_number:04d} START generate "
            f"(max_new_tokens={max_new_tokens})",
            flush=True,
        )
        try:
            result = text_to_schema_with_llm(
                model,
                tokenizer,
                nl_text,
                database,
                max_new_tokens=max_new_tokens,
            )
            _save_record_result(
                out_dir, llm_name, model_id, rid, text_number, nl_text, database, result
            )
            ok += 1
            manifest.append({"text_number": text_number, "id": rid, "file": serial_stem(text_number)})
            elapsed = time.time() - t_q
            print(
                f"  [{llm_name}] text {text_number:04d} DONE in {elapsed:.0f}s -> {out_json.name}",
                flush=True,
            )
            pbar.set_postfix(ok=ok, err=err_count, skip=skipped, last_s=f"{elapsed:.0f}", refresh=True)
        except Exception as e:
            err_count += 1
            elapsed = time.time() - t_q
            print(
                f"  [{llm_name}] text {text_number:04d} ERROR after {elapsed:.0f}s: {e}",
                flush=True,
            )
            _save_record_result(
                out_dir, llm_name, model_id, rid, text_number, nl_text, database, None, str(e)
            )
            pbar.set_postfix(ok=ok, err=err_count, skip=skipped, refresh=True)

        total = ok + err_count
        if total > 0 and total % CACHE_CLEAR_EVERY_N == 0 and torch.cuda.is_available():
            torch.cuda.empty_cache()

    pbar.close()
    if manifest:
        (out_dir / "index.jsonl").write_text(
            "\n".join(json.dumps(m, ensure_ascii=False) for m in manifest) + "\n",
            encoding="utf-8",
        )

    del model
    del tokenizer
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    print(f"[{llm_name}] Done: {ok} OK, {err_count} errors -> {out_dir}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="SchemaBench: annotation_ddl.jsonl NL questions -> schema via open LLMs"
    )
    parser.add_argument("--limit", type=int, default=None, help="Max records per LLM (smoke test)")
    parser.add_argument(
        "--llm",
        type=str,
        default=None,
        choices=list(TRANSLATOR_CONFIG.keys()),
        help="Run one LLM. Default: all four.",
    )
    parser.add_argument(
        "--show-results",
        action="store_true",
        help="Print DDL summary after run.",
    )
    parser.add_argument("--input", type=Path, default=ANNOTATION_PATH)
    parser.add_argument("--output-dir", type=Path, default=BASE_OUT)
    parser.add_argument("--no-skip-existing", action="store_true")
    parser.add_argument("--max-new-tokens", type=int, default=MAX_NEW_TOKENS)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--parallel-llms",
        action="store_true",
        help="Run LLMs in parallel subprocesses (2 GPUs each on 4-GPU host).",
    )
    parser.add_argument(
        "--gpus-per-llm",
        type=int,
        default=None,
        help="GPUs per worker (default: 2 when 4+ GPUs visible, else 1).",
    )
    parser.add_argument(
        "--require-gpu",
        action="store_true",
        help="Exit if no CUDA GPU is visible.",
    )
    args = parser.parse_args()

    if not args.input.is_file():
        print("Error: input not found:", args.input, file=sys.stderr)
        sys.exit(1)

    if HF_TOKEN:
        try:
            from huggingface_hub import login

            login(token=HF_TOKEN)
        except Exception:
            pass

    records = load_jsonl(args.input)
    if args.limit and args.limit > 0:
        records = records[: args.limit]

    args.output_dir.mkdir(parents=True, exist_ok=True)

    llms = (
        {args.llm: TRANSLATOR_CONFIG[args.llm]}
        if args.llm
        else TRANSLATOR_CONFIG
    )

    if args.dry_run:
        print(f"Dry run OK: {len(records)} records from {args.input}")
        print(f"LLMs: {list(llms.keys())}")
        for i, rec in enumerate(records[:5], 1):
            rid = rec.get("id", "?")
            q = rec.get("question") or ""
            print(f"  [{i}] id={rid} q_len={len(q)} preview={q[:80]!r}...")
        for name in llms:
            print(f"  -> {args.output_dir / f'text2schema_{name}'}")
        return

    print("=" * 72)
    print("SchemaBench Text2Schema (annotation_ddl.jsonl)")
    print(f"  Data root : {DATA_ROOT}")
    print(f"  HF cache  : {os.environ.get('HF_HOME', HF_CACHE_ROOT)}")
    print(f"  Input     : {args.input} ({len(records)} records, NL questions only)")
    print(f"  Output    : {args.output_dir.resolve()}")
    print(f"  LLMs      : {list(llms.keys())}")
    print(
        f"  max_new_tokens={args.max_new_tokens}, max_input={MAX_INPUT_TOKENS}, "
        f"temperature={GENERATION_TEMPERATURE}"
    )
    n_gpu = log_gpu_status()
    if args.require_gpu and n_gpu == 0:
        print("Error: --require-gpu set but no CUDA devices visible.", file=sys.stderr)
        sys.exit(2)
    print("=" * 72)

    show_results = args.show_results or (args.limit is not None and 0 < args.limit <= 10)

    if args.parallel_llms and len(llms) > 1:
        import torch

        if not torch.cuda.is_available() or torch.cuda.device_count() < 2:
            print("WARN: --parallel-llms needs 2+ GPUs; falling back to sequential.", flush=True)
            args.parallel_llms = False

    if args.parallel_llms and len(llms) > 1:
        llm_names = list(llms.keys())
        use_smart_pack = args.gpus_per_llm is None and n_gpu >= 4
        if use_smart_pack:
            gpus_per_model = {n: LLM_GPU_REQUIREMENTS.get(n, 1) for n in llm_names}
            waves = _pack_llm_waves_smart(llm_names, gpus_per_model, n_gpu)
            print(
                f"Parallel LLM workers: smart pack on {n_gpu} GPU(s), "
                f"{len(waves)} wave(s), per-model GPU map:",
                flush=True,
            )
            for n, g in gpus_per_model.items():
                print(f"    {n}: {g} GPU(s)", flush=True)
        else:
            gpus_per_llm = args.gpus_per_llm if args.gpus_per_llm is not None else (2 if n_gpu >= 4 else 1)
            waves = _parallel_llm_waves(llm_names, gpus_per_llm)
            print(
                f"Parallel LLM workers: {gpus_per_llm} GPU(s) each, "
                f"{len(waves)} wave(s), CUDA_VISIBLE_DEVICES per process:",
                flush=True,
            )
        for wave_idx, wave in enumerate(waves, 1):
            if use_smart_pack:
                groups = _assign_gpus_in_wave(wave, gpus_per_model)
            else:
                groups = _gpu_groups_for_parallel_llms(wave, gpus_per_llm)
            print(f"  Wave {wave_idx}/{len(waves)}:", flush=True)
            for name, gpus in groups.items():
                print(f"    {name}: {gpus or 'CPU'}", flush=True)

        base_cmd = [
            sys.executable,
            str(Path(__file__).resolve()),
            "--input",
            str(args.input),
            "--output-dir",
            str(args.output_dir),
            "--max-new-tokens",
            str(args.max_new_tokens),
        ]
        if args.limit:
            base_cmd.extend(["--limit", str(args.limit)])
        if args.no_skip_existing:
            base_cmd.append("--no-skip-existing")

        failed: list[tuple[str, int]] = []
        for wave_idx, wave in enumerate(waves, 1):
            if use_smart_pack:
                groups = _assign_gpus_in_wave(wave, gpus_per_model)
            else:
                groups = _gpu_groups_for_parallel_llms(wave, gpus_per_llm)
            procs: list[tuple[str, subprocess.Popen]] = []
            for name in wave:
                env = os.environ.copy()
                if groups[name]:
                    env["CUDA_VISIBLE_DEVICES"] = groups[name]
                cmd = base_cmd + ["--llm", name]
                print(
                    f"Starting worker (wave {wave_idx}): {name} -> GPUs {groups[name] or 'CPU'}",
                    flush=True,
                )
                procs.append((name, subprocess.Popen(cmd, env=env)))
            for name, proc in procs:
                rc = proc.wait()
                if rc != 0:
                    failed.append((name, rc))
                    print(f"Worker {name} exited with code {rc}", file=sys.stderr, flush=True)
        if failed:
            print(f"FAILED workers: {failed}", file=sys.stderr)
            sys.exit(1)
    else:
        for name, model_id in llms.items():
            run_one_llm(
                llm_name=name,
                model_id=model_id,
                records=records,
                base_out=args.output_dir,
                skip_existing=not args.no_skip_existing,
                max_new_tokens=args.max_new_tokens,
            )

    if show_results:
        for name in llms:
            print_results_summary(args.output_dir, name, records)
    print("\nAll LLMs finished.", flush=True)


if __name__ == "__main__":
    main()
