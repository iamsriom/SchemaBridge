"""Historical JSON schema extraction for PaperMethods baselines.

Provenance: LLM4DBdesign/utils.py::extract_json_from_text and helpers.
"""
from __future__ import annotations

import ast
import json
import re
from typing import Any

def _balanced_brace_slice(text: str, start: int) -> str | None:
    """Return substring from first `{` at start through its matching `}`."""
    if start >= len(text) or text[start] != "{":
        return None
    depth = 0
    in_str = False
    escape = False
    quote = ""
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == quote:
                in_str = False
            continue
        if ch in ("'", '"'):
            in_str = True
            quote = ch
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


def _repair_llm_json(raw: str) -> str:
    """Fix common LLM JSON mistakes (missing commas between properties)."""
    repaired = raw.replace("`", "")
    repaired = re.sub(r"(\])\s*\n\s*(['\"])", r"\1,\n\2", repaired)
    repaired = re.sub(r"(\})\s*\n\s*(['\"])", r"\1,\n\2", repaired)
    repaired = re.sub(r"(\])\s+(['\"])", r"\1, \2", repaired)
    repaired = re.sub(r"(\})\s+(['\"])", r"\1, \2", repaired)
    return repaired


def _try_parse_dict(raw: str) -> dict | None:
    import ast

    variants = [raw, raw.replace("`", ""), _repair_llm_json(raw)]
    for attempt in variants:
        try:
            val = json.loads(attempt)
            if isinstance(val, dict):
                return val
        except json.JSONDecodeError:
            pass
        try:
            val = ast.literal_eval(attempt)
            if isinstance(val, dict):
                return val
        except (SyntaxError, ValueError):
            pass
        try:
            val = json.loads(attempt.replace("'", '"'))
            if isinstance(val, dict):
                return val
        except json.JSONDecodeError:
            pass
    return None


def _extract_wrapped_schema(text: str) -> dict | None:
    """Pull out the dict under a top-level 'schema' key even if outer JSON is broken."""
    for m in re.finditer(r"""['"]schema['"]\s*:\s*""", text, re.IGNORECASE):
        rest = text[m.end() :].lstrip()
        if not rest.startswith("{"):
            continue
        chunk = _balanced_brace_slice(rest, 0)
        if not chunk:
            continue
        inner = _try_parse_dict(chunk)
        if inner and _count_tables(inner) >= 1:
            return {"schema": inner}
    return None


_META_KEYS = {
    "Attributes", "Attribute", "Primary key", "Foreign key", "schema",
    "属性", "主键", "外键",
}

_TABLE_ATTR_KEYS = ("Attributes", "Attribute", "属性")


def _count_tables(d: dict) -> int:
    if not isinstance(d, dict):
        return 0
    return sum(
        1 for v in d.values()
        if isinstance(v, dict) and any(k in v for k in _TABLE_ATTR_KEYS)
    )


_TESTCASE_KEYS = {
    "Insert Test case", "Update Test case", "Query Test case", "Delete Test case",
    "Insert Test Case", "Update Test Case", "Query Test Case", "Delete Test Case",
}


def _looks_like_test_cases(d: dict) -> bool:
    keys = set(d.keys())
    return bool(keys & _TESTCASE_KEYS) or (
        "Insert Test case" in str(d)[:200] and "schema" not in d
    )


def _schema_score(d: dict) -> int:
    if _looks_like_test_cases(d):
        return -2000
    if set(d.keys()).issubset(_META_KEYS):
        return -1000

    if "schema" in d and isinstance(d["schema"], dict):
        if _looks_like_test_cases(d["schema"]):
            return -2000
        table_like = _count_tables(d["schema"])
        if table_like >= 1:
            return 10000 + table_like * 10

    # SchemaAgent LogicalDesigner wraps tables in "output"
    for wrap in ("output", "pred_schema"):
        inner = d.get(wrap)
        if isinstance(inner, dict):
            if _looks_like_test_cases(inner):
                continue
            table_like = _count_tables(inner)
            if table_like >= 1:
                return 9000 + table_like * 10
            if any("Entity Set" in str(k) for k in inner):
                return 4000

    table_like = _count_tables(d)
    if table_like >= 2:
        return 5000 + table_like * 10
    if table_like == 1:
        return 100
    if any("Entity Set" in str(k) for k in d):
        return 3000
    if d and all(
        isinstance(v, dict) and not any(k in v for k in _TABLE_ATTR_KEYS) and len(v) <= 2
        for v in d.values()
    ):
        return -1000
    return -100


def _parse_dict_strict(raw: str) -> dict | None:
    """json.loads, then ast.literal_eval. Does not rewrite schema content."""
    import ast

    if not raw:
        return None
    try:
        val = json.loads(raw)
        if isinstance(val, dict):
            return val
    except json.JSONDecodeError:
        pass
    try:
        val = ast.literal_eval(raw)
        if isinstance(val, dict):
            return val
    except (SyntaxError, ValueError, MemoryError):
        pass
    return None


def _strip_fences(text: str) -> str:
    return re.sub(r"```(?:python|json)?", "", text, flags=re.IGNORECASE)


def extract_json_from_text(text):
    if not text or text.strip() in ("ERROR.", "ERROR"):
        return {}

    cleaned = _strip_fences(text)
    found: list[dict] = []
    for src in (cleaned, text):
        for m in re.finditer(r"\{", src):
            chunk = _balanced_brace_slice(src, m.start())
            if not chunk or len(chunk) <= 10:
                continue
            # Prefer strict parse; fall back to historical _try_parse_dict /
            # _repair_llm_json already present in LLM4DBdesign/utils.py for
            # LLM dicts with missing commas / mixed quotes.
            parsed = _parse_dict_strict(chunk) or _try_parse_dict(chunk)
            if parsed:
                found.append(parsed)

    schema_like = [d for d in found if _schema_score(d) >= 0]
    if not schema_like:
        print("没有匹配到json" if not found else "没有匹配到有效schema json")
        return {}

    best = schema_like[-1]
    schema_key = next((k for k in best if str(k).lower() == "schema" and isinstance(best[k], dict)), None)
    if schema_key is not None:
        if schema_key != "schema":
            best = dict(best)
            best["schema"] = best.pop(schema_key)
        return best
    for wrap in ("output", "pred_schema"):
        inner = best.get(wrap)
        if isinstance(inner, dict) and _count_tables(inner) >= 1:
            return {"schema": inner}
    if _count_tables(best) >= 1:
        return {"schema": best}
    return best





