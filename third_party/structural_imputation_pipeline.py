#!/usr/bin/env python3
"""
Structural Imputation (Ablation) Pipeline for Text2ER PhD research.

Reads ground-truth SQL DDL files, applies 5 masking functions to hide specific
schema elements, passes masked DDLs to CodeLlama (Hugging Face) to generate
Natural Language descriptions, and saves outputs to Case1Q1_T .. Case1Q5_T.

Mask 1: Hidden Table
Mask 2: Hidden Attributes (keep only PK/FK/REFERENCES)
Mask 3: Hidden Domain Integrity (strip types, NOT NULL, DEFAULT)
Mask 4: Hidden Entity Integrity (strip PRIMARY KEY, UNIQUE)
Mask 5: Hidden Referential Integrity (strip FOREIGN KEY, REFERENCES)
"""

from __future__ import annotations

import argparse
import gc
import json
import logging
import os
import random
import re
import sys
import torch
from pathlib import Path

# -----------------------------------------------------------------------------
# Paths and configuration
# -----------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR
# Input: gold SQL DDL files (use --schema-dir to override)
DEFAULT_SCHEMA_DIR = PROJECT_ROOT / "schemas"
# Output base: save under /data/LLMTranslations/Cases (Case1Q1_T .. Case1Q5_T)
BASE_OUT = Path("/data/LLMTranslations/Cases")

# Case name -> output subdirectory
CASE_OUTPUT_DIRS = {
    "Case1Q1_T": "Case1Q1_T",  # Mask 1: Hidden Table
    "Case1Q2_T": "Case1Q2_T",  # Mask 2: Hidden Attributes
    "Case1Q3_T": "Case1Q3_T",  # Mask 3: Hidden Domain Integrity
    "Case1Q4_T": "Case1Q4_T",  # Mask 4: Hidden Entity Integrity
    "Case1Q5_T": "Case1Q5_T",  # Mask 5: Hidden Referential Integrity
    "Case1Q6_T": "Case1Q6_T",  # Mask 6: All table names removed (replaced with table_1, table_2, ...)
}

# Prompt and LLMs (aligned with schema2text1_allLLM.py)
SYSTEM_PROMPT = """Summarize this database schema in one short paragraph of plain English: what it is for, main tables, and how they relate. Human-readable only. Do not output any SQL, DDL, CREATE TABLE, or code—reply with only that one paragraph of plain English."""

LLM_CONFIG = {
    "codellama": "codellama/CodeLlama-7b-Instruct-hf",
    "mistral": "mistralai/Mistral-7B-Instruct-v0.2",
}

DDL_MAX_CHARS = 60_000
# Was 512: too small for large schemas (truncated summaries → model echoes DDL → placeholder .txt).
MAX_NEW_TOKENS = 2500
CACHE_CLEAR_EVERY_N = 5
# Minimum prompt tokens reserved for system + "Schema:\n" + safety margin (fits DDL below this).
_MIN_PROMPT_OVERHEAD_TOKENS = 256

# HF token for gated models (e.g. Meta CodeLlama)
def _load_hf_token() -> str | None:
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if token:
        return token.strip()
    api_file = PROJECT_ROOT / "huggingface_api.txt"
    if api_file.is_file():
        return api_file.read_text().strip() or None
    return None


HF_TOKEN = _load_hf_token()

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )


log = logging.getLogger(__name__)


# =============================================================================
# Step 2: The 5 Masking Functions (regex-based; adjust for SQLite/MySQL)
# =============================================================================

def _find_table_blocks(ddl: str) -> list[tuple[int, int, str]]:
    """
    Find all CREATE TABLE ... ( ... ); blocks. Returns list of (start, end, block_text).
    Handles nested parentheses (e.g. CHECK constraints) by counting parens.
    """
    blocks = []
    pattern = re.compile(r"\bCREATE\s+TABLE\s+", re.IGNORECASE)
    pos = 0
    while True:
        m = pattern.search(ddl, pos)
        if not m:
            break
        start = m.start()
        # Find opening paren of column list (after table name)
        open_paren = ddl.find("(", m.end())
        if open_paren == -1:
            pos = m.end()
            continue
        depth = 1
        i = open_paren + 1
        while i < len(ddl) and depth > 0:
            if ddl[i] == "(":
                depth += 1
            elif ddl[i] == ")":
                depth -= 1
            i += 1
        if depth != 0:
            pos = m.end()
            continue
        # Include everything after the closing ")" up to and including the terminator (;\n or \n;\n)
        end = i
        rest = ddl[i:]
        # Match either ";\n" on same line as ) or "\n;\n" on next line
        match_trailing = re.match(r"[\s\S]*?(?:;\s*\n|\n;\s*\n)", rest)
        if match_trailing:
            end = i + match_trailing.end()
        else:
            # Fallback: include up to next ";" (newline may be missing at EOF)
            idx = rest.find(";")
            if idx >= 0:
                end = i + idx + 1
        blocks.append((start, end, ddl[start:end]))
        pos = end
    return blocks


def _extract_table_name_from_create_line(line: str) -> str | None:
    """Extract table name from first line of a CREATE TABLE block. Returns None if not matched."""
    m = re.match(r"\s*CREATE\s+TABLE\s+[`']?(\w+)[`']?\s*\(", line, re.IGNORECASE)
    return m.group(1).strip("`'") if m else None


def mask_table(ddl: str, rng: random.Random | None = None) -> str:
    """
    Mask 1: Hide one table.
    Find all CREATE TABLE blocks, randomly select exactly one and remove it.
    If the schema has only one table, skip masking (return original).
    """
    if rng is None:
        rng = random.Random()
    blocks = _find_table_blocks(ddl)
    if len(blocks) <= 1:
        log.debug("mask_table: only one or zero tables, skipping mask")
        return ddl
    idx = rng.randint(0, len(blocks) - 1)
    start, end, _ = blocks[idx]
    return ddl[:start].rstrip() + "\n\n" + ddl[end:].lstrip()


def mask_all_table_names(ddl: str) -> str:
    """
    New case: Remove all table names. Replace every table name with a placeholder
    (table_1, table_2, ...) only in CREATE TABLE and in REFERENCES so column names
    that match a table name are left unchanged (only table-name contexts are masked).
    """
    blocks = _find_table_blocks(ddl)
    if not blocks:
        return ddl
    # Collect table names in order of first appearance
    seen: set[str] = set()
    table_names_ordered: list[str] = []
    for _start, _end, block in blocks:
        first_line = block.split("\n")[0]
        name = _extract_table_name_from_create_line(first_line)
        if name and name not in seen:
            seen.add(name)
            table_names_ordered.append(name)
    if not table_names_ordered:
        return ddl
    # Map each name to placeholder (table_1, table_2, ...)
    name_to_placeholder = {name: f"table_{i+1}" for i, name in enumerate(table_names_ordered)}
    # Replace longest names first so substrings are not wrong (e.g. "user" vs "user_roles")
    sorted_names = sorted(name_to_placeholder.keys(), key=len, reverse=True)
    result = ddl
    for orig in sorted_names:
        repl = name_to_placeholder[orig]
        escaped = re.escape(orig)
        # Only replace where the name is used as a table identifier: followed by \s*\(
        # CREATE TABLE `name` ( or CREATE TABLE name (
        result = re.sub(
            r"(CREATE\s+TABLE\s+)[`']?" + escaped + r"[`']?(\s*\()",
            r"\g<1>`" + repl + r"`\g<2>",
            result,
            flags=re.IGNORECASE,
        )
        # REFERENCES `name` ( or REFERENCES name (
        result = re.sub(
            r"(REFERENCES\s+)[`']?" + escaped + r"[`']?(\s*\()",
            r"\g<1>`" + repl + r"`\g<2>",
            result,
            flags=re.IGNORECASE,
        )
    return result


def mask_attributes(ddl: str) -> str:
    """
    Mask 2: Hide attributes — keep only lines that define or reference
    Primary Keys, Foreign Keys, or References. Remove standard data columns
    (e.g. `name` varchar(50)).
    """
    blocks = _find_table_blocks(ddl)
    if not blocks:
        return ddl
    result = []
    pos = 0
    for start, end, block in blocks:
        result.append(ddl[pos:start])
        lines = block.split("\n")
        kept = []
        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or stripped.startswith("--"):
                kept.append(line)
                continue
            # Always keep first line of block (CREATE TABLE `name` ( )
            if i == 0 and re.match(r"^\s*CREATE\s+TABLE\s+", line, re.IGNORECASE):
                kept.append(line)
                continue
            # Keep: PRIMARY KEY, FOREIGN KEY, REFERENCES, or constraint lines containing them
            if re.search(r"\bPRIMARY\s+KEY\b", stripped, re.IGNORECASE):
                kept.append(line)
            elif re.search(r"\bFOREIGN\s+KEY\b", stripped, re.IGNORECASE):
                kept.append(line)
            elif re.search(r"\bREFERENCES\s+", stripped, re.IGNORECASE):
                kept.append(line)
            # Keep closing ); line
            elif stripped.startswith(")") or stripped == ");":
                kept.append(line)
            # Drop: plain column definitions (no PK/FK/REFERENCES)
            else:
                continue
        kept_text = "\n".join(kept)
        # Ensure we have parentheses; if everything was stripped, keep an empty shell (do NOT revert)
        if not re.search(r"\([\s\S]*\)", kept_text):
            kept_text = re.sub(r"\(.*\)", "()", block, flags=re.DOTALL)
        result.append(kept_text)
        pos = end
    result.append(ddl[pos:])
    return "".join(result)


# Common SQL data types and nullability (extend for your dialect)
TYPE_PATTERN = re.compile(
    r"\b(?:BIGINT|INT(?:EGER)?|TINYINT|SMALLINT|MEDIUMINT|INT\d*)\b",
    re.IGNORECASE,
)
TYPE_PATTERN_2 = re.compile(
    r"\b(?:VARCHAR\s*\(\s*\d+\s*\)|CHAR\s*\(\s*\d+\s*\)|CHARACTER\s+VARYING\s*\(\s*\d+\s*\))",
    re.IGNORECASE,
)
TYPE_PATTERN_3 = re.compile(
    r"\b(?:TEXT|MEDIUMTEXT|LONGTEXT|TINYTEXT|BLOB|MEDIUMBLOB|LONGBLOB)\b",
    re.IGNORECASE,
)
TYPE_PATTERN_4 = re.compile(
    r"\b(?:DATE|DATETIME|TIMESTAMP|TIME|YEAR)\b",
    re.IGNORECASE,
)
TYPE_PATTERN_5 = re.compile(
    r"\b(?:DECIMAL\s*\(\s*\d+\s*,\s*\d+\s*\)|NUMERIC\s*\(\s*\d+\s*,\s*\d+\s*\)|FLOAT|DOUBLE|REAL)\b",
    re.IGNORECASE,
)
TYPE_PATTERN_6 = re.compile(
    r"\b(?:ENUM\s*\([^)]+\)|SET\s*\([^)]+\))\b",
    re.IGNORECASE,
)
NULLABILITY_PATTERN = re.compile(
    r"\b(?:NOT\s+NULL|NULL)\b",
    re.IGNORECASE,
)
DEFAULT_PATTERN = re.compile(
    r"\bDEFAULT\s+(?:CURRENT_TIMESTAMP|NULL|\d+|'[^']*'|\"[^\"]*\")\b",
    re.IGNORECASE,
)
AUTO_INCREMENT_PATTERN = re.compile(r"\bAUTO_INCREMENT\b", re.IGNORECASE)


def mask_domain_integrity(ddl: str) -> str:
    """
    Mask 3: Hide domain integrity.
    Remove data types (INT, VARCHAR, TEXT, DATE, DECIMAL, etc.) and
    nullability (NOT NULL, NULL, DEFAULT ...). Output looks like pseudo-code:
    CREATE TABLE users ( id PRIMARY KEY, email, created_at );
    """
    def strip_type_and_nullability(line: str) -> str:
        s = line
        for pat in (
            TYPE_PATTERN_5,
            TYPE_PATTERN_4,
            TYPE_PATTERN_3,
            TYPE_PATTERN_2,
            TYPE_PATTERN_6,
            TYPE_PATTERN,
        ):
            s = pat.sub("", s)
        s = NULLABILITY_PATTERN.sub("", s)
        s = DEFAULT_PATTERN.sub("", s)
        s = AUTO_INCREMENT_PATTERN.sub("", s)
        # Collapse multiple spaces and trim trailing/leading commas/spaces
        s = re.sub(r"\s+", " ", s).strip()
        s = re.sub(r",\s*,", ",", s)
        s = re.sub(r"^\s*,\s*", "", s)
        s = re.sub(r"\s*,\s*$", "", s)
        return s

    lines = ddl.split("\n")
    out = []
    for line in lines:
        if "CREATE TABLE" in line.upper() or line.strip().startswith(")"):
            out.append(line)
            continue
        # KEY and CONSTRAINT lines have no data types; leave them unchanged to avoid breaking (e.g. KEY `name` (`col`))
        if re.search(r"\b(?:KEY\s+|CONSTRAINT\s+)\b", line, re.IGNORECASE):
            out.append(line)
            continue
        if re.search(r"\b(?:PRIMARY\s+KEY|FOREIGN\s+KEY|REFERENCES|UNIQUE)\b", line, re.IGNORECASE):
            out.append(strip_type_and_nullability(line))
        else:
            # Plain column: keep only identifier (first token, possibly backticked)
            col_match = re.match(r"^(\s*)([`\w]+)(\s*,?)", line)
            if col_match:
                out.append(col_match.group(1) + col_match.group(2) + col_match.group(3))
            else:
                out.append(strip_type_and_nullability(line))
    return "\n".join(out)


def mask_entity_integrity(ddl: str) -> str:
    """
    Mask 4: Hide entity integrity.
    Remove all PRIMARY KEY and UNIQUE constraints:
    - Inline: `id` int PRIMARY KEY -> `id` int
    - Table-level: CONSTRAINT pk_name PRIMARY KEY (col1, col2) -> remove line or constraint
    """
    lines = ddl.split("\n")
    out = []
    for line in lines:
        # Remove table-level CONSTRAINT ... PRIMARY KEY (...)
        if re.search(r"\bCONSTRAINT\s+\S+\s+PRIMARY\s+KEY\s*\([^)]+\)", line, re.IGNORECASE):
            continue
        # Remove standalone PRIMARY KEY (col1, col2) line
        if re.match(r"^\s*PRIMARY\s+KEY\s*\([^)]+\)\s*,?\s*$", line, re.IGNORECASE):
            continue
        # Remove UNIQUE (col) or UNIQUE KEY ...
        if re.match(r"^\s*UNIQUE\s+(?:KEY\s+)?(?:\([^)]+\)|\S+)\s*,?\s*$", line, re.IGNORECASE):
            continue
        if re.search(r"\bCONSTRAINT\s+\S+\s+UNIQUE\s+", line, re.IGNORECASE):
            continue
        # Inline: strip PRIMARY KEY and UNIQUE from column line
        s = re.sub(r"\bPRIMARY\s+KEY\b", "", line, flags=re.IGNORECASE)
        s = re.sub(r"\bUNIQUE\b", "", s, flags=re.IGNORECASE)
        s = re.sub(r"\s+,", ",", s)
        s = re.sub(r",\s*,", ",", s)
        s = re.sub(r"\s+", " ", s).strip()
        if s and s != ",":
            out.append(s)
    # Remove trailing comma before closing paren (left when last line was a removed constraint)
    result = "\n".join(out)
    return re.sub(r",\s*\)", ")", result)


def mask_referential_integrity(ddl: str) -> str:
    """
    Mask 5: Hide referential integrity.
    Remove all FOREIGN KEY definitions and REFERENCES. Keep the column
    definitions (e.g. `user_id` int) but strip the structural link.
    """
    lines = ddl.split("\n")
    out = []
    for line in lines:
        # Remove entire line if it is only FOREIGN KEY (...) REFERENCES ...
        if re.match(
            r"^\s*(?:CONSTRAINT\s+\S+\s+)?FOREIGN\s+KEY\s*\([^)]+\)\s+REFERENCES\s+",
            line,
            re.IGNORECASE,
        ):
            continue
        # Inline REFERENCES parent(col) or parent(col1, col2) — remove "REFERENCES ..." from column line
        s = re.sub(r"\s+REFERENCES\s+\S+(?:\s*\(\s*[^)]+\s*\))?\s*,?\s*$", " ", line, flags=re.IGNORECASE)
        s = re.sub(r"\s+REFERENCES\s+\S+(?:\s*\(\s*[^)]+\s*\))?", "", s, flags=re.IGNORECASE)
        s = re.sub(r"\s+", " ", s).strip()
        s = re.sub(r",\s*$", ",", s).strip()  # preserve trailing comma for column list
        if s and s != ",":
            out.append(s)
    # Remove trailing comma before closing paren (left when last line was a removed FK)
    result = "\n".join(out)
    return re.sub(r",\s*\)", ")", result)


# -----------------------------------------------------------------------------
# Step 3: LLM integration (Hugging Face; device_map='auto' spreads over GPUs)
# -----------------------------------------------------------------------------
def _load_model_and_tokenizer(model_id: str):
    """Load model and tokenizer with device_map='auto' (multi-GPU)."""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    kwargs = {"trust_remote_code": True}
    if HF_TOKEN:
        kwargs["token"] = HF_TOKEN
    tokenizer = AutoTokenizer.from_pretrained(model_id, **kwargs)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map="auto",
        torch_dtype="auto",
        **kwargs,
    )
    return model, tokenizer


def _build_generation_prompt(masked_ddl: str, system_prompt: str, tokenizer) -> str:
    """Same string that will be tokenized for generate (chat template or Llama INST)."""
    user_content = f"Schema:\n{masked_ddl}"
    full_user = f"{system_prompt}\n\n{user_content}" if system_prompt else user_content
    messages = [{"role": "user", "content": full_user}]
    if hasattr(tokenizer, "apply_chat_template") and getattr(tokenizer, "chat_template", None) is not None:
        try:
            return tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        except Exception:
            pass
    if system_prompt:
        return f"<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{user_content} [/INST]\n"
    return f"<s>[INST] {user_content} [/INST]\n"


def _prompt_token_len(text: str, tokenizer) -> int:
    return len(tokenizer(text, add_special_tokens=True)["input_ids"])


def _max_input_tokens(model, max_new_tokens: int) -> int:
    """Input budget so input + generation fits model context (conservative)."""
    mp = getattr(model.config, "max_position_embeddings", None) or 4096
    # Keep bounded for VRAM (KV cache scales with seq_len × max_new during generate).
    mp = min(int(mp), 4096)
    return max(512, mp - max_new_tokens - _MIN_PROMPT_OVERHEAD_TOKENS)


def _fit_masked_ddl_to_context(
    masked_ddl: str,
    tokenizer,
    system_prompt: str,
    max_input_tokens: int,
) -> str:
    """
    Shrink masked DDL so the full prompt fits max_input_tokens, without cutting mid–CREATE TABLE
    when possible (avoids corrupting the schema snippet shown to the model).
    """
    if len(masked_ddl) > DDL_MAX_CHARS:
        masked_ddl = masked_ddl[:DDL_MAX_CHARS] + "\n\n... [DDL truncated by character limit]"

    def fits(ddl: str) -> bool:
        prompt = _build_generation_prompt(ddl, system_prompt, tokenizer)
        return _prompt_token_len(prompt, tokenizer) <= max_input_tokens

    if fits(masked_ddl):
        return masked_ddl

    blocks = _find_table_blocks(masked_ddl)
    if not blocks:
        lo, hi = 0, len(masked_ddl)
        best = masked_ddl[: min(hi, 4000)]
        while lo <= hi:
            mid = (lo + hi) // 2
            cand = masked_ddl[:mid].rstrip()
            if mid < len(masked_ddl):
                cand += "\n\n-- [DDL truncated for model context length]"
            if fits(cand):
                best = cand
                lo = mid + 1
            else:
                hi = mid - 1
        return best

    preamble = masked_ddl[: blocks[0][0]]
    n = len(blocks)
    for k in range(n, 0, -1):
        chunk = preamble + "".join(masked_ddl[s:e] for s, e, _ in blocks[:k])
        if k < n:
            chunk += f"\n\n-- [{n - k} more tables omitted for context length; summarize the visible schema.]"
        if fits(chunk):
            return chunk

    first = masked_ddl[blocks[0][0] : blocks[0][1]]
    lo, hi = 0, len(first)
    best = first[:2000]
    while lo <= hi:
        mid = (lo + hi) // 2
        cand = preamble + first[:mid].rstrip()
        if mid < len(first):
            cand += "\n\n-- [Table truncated]"
        if fits(cand):
            best = cand
            lo = mid + 1
        else:
            hi = mid - 1
    return best


def generate_translation(
    model,
    tokenizer,
    masked_ddl: str,
    system_prompt: str = SYSTEM_PROMPT,
) -> str:
    """
    Generate natural language description of the masked DDL (schema2text1-style prompt).
    """
    import torch

    mp = getattr(model.config, "max_position_embeddings", 4096) or 4096
    max_new = min(MAX_NEW_TOKENS, max(256, mp // 5))
    max_in = _max_input_tokens(model, max_new)
    masked_ddl = _fit_masked_ddl_to_context(masked_ddl, tokenizer, system_prompt, max_in)

    text = _build_generation_prompt(masked_ddl, system_prompt, tokenizer)
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=max_in)
    device = next(model.parameters()).device
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=max_new,
            do_sample=True,
            temperature=0.2,
            pad_token_id=tokenizer.eos_token_id,
        )
    reply = tokenizer.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    return extract_nl_summary(reply.strip())


# Words that indicate natural-language description (not DDL)
_NL_INDICATOR_WORDS = re.compile(
    r"\b(the|this|schema|table|tables|database|contains|stores|relates|records|"
    r"fields|data|for|with|and|describes|tracks|manages|links|information|about)\b",
    re.IGNORECASE,
)


def extract_nl_summary(reply: str) -> str:
    """
    Extract natural-language summary from model output. CodeLlama (and similar) often
    continue the schema as DDL instead of summarizing; we truncate at code and keep
    only the part that looks like a description.
    """
    if not reply:
        return "[Empty model response.]"
    # Truncate at first CREATE TABLE (model continuing the schema)
    idx = re.search(r"\bCREATE\s+TABLE\b", reply, re.IGNORECASE)
    if idx:
        reply = reply[: idx.start()].rstrip()
    # Model output may be a mid-schema fragment (e.g. "MENT COMMENT '...',\n  `col` datetime NOT NULL")
    if re.match(r"^(?:MENT\s+)?COMMENT\s+['\"]", reply.strip(), re.IGNORECASE):
        return "[Model returned schema/code continuation instead of summary.]"
    if re.match(r"^[^a-zA-Z]*`\w+`\s+(?:datetime|int|varchar|char|decimal|timestamp|tinyint|smallint|bigint)\s", reply.strip(), re.IGNORECASE):
        return "[Model returned schema/code continuation instead of summary.]"
    # Truncate at DDL constraint/code patterns (model output mid-schema fragment)
    for pat in [
        r"\bREFERENCES\s+`",  # REFERENCES `table`
        r"\bCONSTRAINT\s+`",  # CONSTRAINT `name`
        r"\)\s*REFERENCES\s+",  # ) REFERENCES
        r"\bON\s+DELETE\s+(?:NO\s+ACTION|CASCADE|SET\s+NULL)",  # ON DELETE ...
        r"\bON\s+UPDATE\s+(?:NO\s+ACTION|CASCADE)",  # ON UPDATE ...
        r";\s*\n\s*\n",
        r"\)\s*ENGINE=",
        r"COMMENT='[^']*'\s*;\s*$",
        r"COMMENT\s+['\"]",  # COMMENT '... or COMMENT " (model continued with column comment)
    ]:
        m = re.search(pat, reply, re.IGNORECASE)
        if m:
            reply = reply[: m.start()].rstrip()
    # Keep full remaining text: multi-paragraph NL is valid for large schemas (do not drop para 2+).
    stripped = reply.strip()
    if not stripped:
        return "[Empty model response.]"
    # Clearly DDL: engine/charset/collate or leading DDL fragment
    if (
        "COLLATE=" in stripped
        or "CHARSET=" in stripped
        or "ENGINE=" in stripped
        or re.search(r"^\s*(utf8| COMMENT=|\w+_general_ci)", stripped, re.IGNORECASE)
    ):
        return "[Model returned schema/code continuation instead of summary.]"
    if re.match(r"^[^a-zA-Z]*`\w*`?\s*\)", stripped):
        return "[Model returned schema/code continuation instead of summary.]"
    # Remaining REFERENCES/CONSTRAINT with backtick = code leak
    if re.search(r"\b(REFERENCES|CONSTRAINT|FOREIGN\s+KEY)\s+`", stripped, re.IGNORECASE):
        return "[Model returned schema/code continuation instead of summary.]"
    # Short fragment: only treat as code if it has no NL indicators
    if len(stripped) < 80 and ("`" in stripped or stripped.endswith(")")):
        if not _NL_INDICATOR_WORDS.search(stripped):
            return "[Model returned schema/code continuation instead of summary.]"
    # If we have at least one sentence (period or 40+ chars) and an NL word, keep it
    if _NL_INDICATOR_WORDS.search(stripped) and (len(stripped) >= 40 or "." in stripped):
        return stripped
    return stripped if stripped else "[Empty model response.]"


def cases_nl_is_unusable(nl_text: str) -> bool:
    """True when Cases/*.txt should be re-generated (placeholder, empty, or leaked DDL fragment)."""
    t = (nl_text or "").strip()
    if not t:
        return True
    if t.startswith("["):
        return True
    u = t.lstrip()
    if u.startswith("`"):
        return True
    if u.upper().startswith("CREATE TABLE"):
        return True
    return False


# -----------------------------------------------------------------------------
# Step 4: Main execution loop
# -----------------------------------------------------------------------------
def get_output_subdir(case_name: str, llm_name: str) -> str:
    """Output dir name: Case1Q1_T_codellama, Case1Q1_T_mistral, etc."""
    return f"{case_name}_{llm_name}"


def ensure_directories(schema_dir: Path, base_out: Path, llm_names: list[str]) -> None:
    schema_dir.mkdir(parents=True, exist_ok=True)
    base_out.mkdir(parents=True, exist_ok=True)
    for case_name in CASE_OUTPUT_DIRS:
        for llm_name in llm_names:
            (base_out / get_output_subdir(case_name, llm_name)).mkdir(parents=True, exist_ok=True)
    log.info("Output dirs: %s", [base_out / get_output_subdir(c, l) for c in CASE_OUTPUT_DIRS for l in llm_names][:10])


def get_sql_files(schema_dir: Path) -> list[Path]:
    return sorted(schema_dir.glob("*.sql"))


def run_pipeline(
    schema_dir: Path,
    base_out: Path,
    seed: int | None = None,
    limit: int | None = None,
    llm_names: list[str] | None = None,
    case_name: str | None = None,
) -> None:
    if llm_names is None:
        llm_names = list(LLM_CONFIG.keys())
    ensure_directories(schema_dir, base_out, llm_names)
    sql_files = get_sql_files(schema_dir)
    if not sql_files:
        log.warning("No .sql files in %s. Add DDL files or a dummy schema for testing.", schema_dir)
        return
    if limit is not None and limit > 0:
        sql_files = sql_files[:limit]
    rng = random.Random(seed)
    all_cases = [
        ("Case1Q1_T", mask_table),
        ("Case1Q2_T", mask_attributes),
        ("Case1Q3_T", mask_domain_integrity),
        ("Case1Q4_T", mask_entity_integrity),
        ("Case1Q5_T", mask_referential_integrity),
        ("Case1Q6_T", mask_all_table_names),
    ]
    if case_name:
        cases = [(c, fn) for c, fn in all_cases if c == case_name]
        if not cases:
            log.error("Unknown case: %s. Valid: %s", case_name, [c for c, _ in all_cases])
            return
        log.info("Running only case: %s", case_name)
    else:
        cases = all_cases

    for llm_name in llm_names:
        model_id = LLM_CONFIG[llm_name]
        model = None
        tokenizer = None
        try:
            log.info("[%s] Clearing cache and loading %s (device_map=auto)...", llm_name, model_id)
            gc.collect()
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except Exception:
                pass
            try:
                model, tokenizer = _load_model_and_tokenizer(model_id)
            except Exception as e:
                err_msg = str(e).lower()
                if "gated" in err_msg or "401" in err_msg or "access" in err_msg or "restricted" in err_msg:
                    log.error("[%s] SKIP: Model gated. Set HF_TOKEN or huggingface_api.txt.", llm_name)
                    continue
                raise
            total_queries = 0
            for sql_path in sql_files:
                log.info("[%s] Processing %s", llm_name, sql_path.name)
                try:
                    gold_ddl = sql_path.read_text(encoding="utf-8")
                except Exception as e:
                    log.exception("Failed to read %s: %s", sql_path.name, e)
                    continue
                base_name = sql_path.stem
                out_txt_name = f"{base_name}.txt"
                out_json_name = f"{base_name}.json"
                for case_name, mask_fn in cases:
                    out_dir = base_out / get_output_subdir(case_name, llm_name)
                    txt_path = out_dir / out_txt_name
                    json_path = out_dir / out_json_name
                    try:
                        if case_name == "Case1Q1_T":
                            masked = mask_fn(gold_ddl, rng=rng)
                        else:
                            masked = mask_fn(gold_ddl)
                        translation = generate_translation(
                            model, tokenizer, masked, system_prompt=SYSTEM_PROMPT
                        )
                        txt_path.write_text(translation, encoding="utf-8")
                        out_obj = {
                            "schema_file": sql_path.name,
                            "schema_stem": base_name,
                            "case": case_name,
                            "llm": llm_name,
                            "model_id": model_id,
                            "nl_text": translation,
                            "masked_ddl": masked,
                        }
                        json_path.write_text(
                            json.dumps(out_obj, indent=2, ensure_ascii=False, default=str),
                            encoding="utf-8",
                        )
                        total_queries += 1
                        log.info("  [%s] %s -> %s, %s", llm_name, case_name, txt_path.name, json_path.name)
                    except Exception as e:
                        log.exception("  [%s] %s ERROR for %s: %s", llm_name, case_name, sql_path.name, e)
                        try:
                            txt_path.write_text(f"[ERROR: {e!s}]\n", encoding="utf-8")
                            json_path.write_text(
                                json.dumps(
                                    {
                                        "schema_file": sql_path.name,
                                        "schema_stem": base_name,
                                        "case": case_name,
                                        "llm": llm_name,
                                        "error": str(e),
                                        "nl_text": None,
                                    },
                                    indent=2,
                                    ensure_ascii=False,
                                    default=str,
                                ),
                                encoding="utf-8",
                            )
                        except Exception:
                            pass
                    if total_queries > 0 and total_queries % CACHE_CLEAR_EVERY_N == 0:
                        try:
                            import torch
                            if torch.cuda.is_available():
                                torch.cuda.empty_cache()
                            log.info("  [%s] Cache cleared after %d queries.", llm_name, total_queries)
                        except Exception:
                            pass
        finally:
            if model is not None:
                del model
            if tokenizer is not None:
                del tokenizer
            gc.collect()
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except Exception:
                pass
            log.info("[%s] Unloaded. Done.", llm_name)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Structural Imputation pipeline: mask DDL, translate with codellama+mistral, save per-case per-LLM.",
    )
    parser.add_argument(
        "--schema-dir",
        type=Path,
        default=DEFAULT_SCHEMA_DIR,
        help="Directory containing .sql DDL files (default: Text2ER/schemas/)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=BASE_OUT,
        help="Base output directory (default: /data/LLMTranslations/Cases/)",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed for Mask 1 (hide one table)")
    parser.add_argument("--limit", type=int, default=None, help="Process only first N .sql files")
    parser.add_argument(
        "--llm",
        type=str,
        default=None,
        choices=list(LLM_CONFIG.keys()),
        help="Run only this LLM (default: all).",
    )
    parser.add_argument(
        "--case",
        type=str,
        default=None,
        choices=list(CASE_OUTPUT_DIRS.keys()),
        help="Run only this case (default: all cases).",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose (debug) logging")
    args = parser.parse_args()

    setup_logging(verbose=args.verbose)
    if HF_TOKEN:
        try:
            from huggingface_hub import login
            login(token=HF_TOKEN)
        except Exception:
            pass

    schema_dir = args.schema_dir if args.schema_dir.is_absolute() else PROJECT_ROOT / args.schema_dir
    base_out = args.output_dir if args.output_dir.is_absolute() else PROJECT_ROOT / args.output_dir
    # Run mistral first, then codellama (when not using --llm)
    llm_names = [args.llm] if args.llm else ["mistral", "codellama"]

    run_pipeline(
        schema_dir=schema_dir,
        base_out=base_out,
        seed=args.seed,
        limit=args.limit,
        llm_names=llm_names,
        case_name=args.case,
    )
    log.info("Pipeline finished.")


if __name__ == "__main__":
    main()
