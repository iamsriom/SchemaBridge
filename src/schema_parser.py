"""DDL parsing for SchemaBridge (self-contained; no ``/data`` paths or third-party imports).

This module ports the *corrected* SchemaBench DDL parser from
``third_party/evaluate_exp4_text2schema.py`` (``metadata_from_ddl``,
``iter_ddl_table_bodies``, ``_parse_data_type``, ``ensure_prediction_metadata``) and the
constraint extractors from ``third_party/evaluate_text2schema2.py``
(``parse_ddl_primary_unique``, ``parse_ddl_fks``).

Two parsing modes
-----------------
``legacy=True``
    Bit-for-bit behaviour of the vendored parser.  Use this to reproduce archived Exp4
    numbers.  Known limitations of the vendored code (kept on purpose in this mode):

    * columns are split on newlines (single-line ``CREATE TABLE t (a int, b int)`` is
      parsed as ONE column);
    * columns whose type is not in ``_TYPE_RE`` (``json``, ``blob``, ``enum`` ...) are
      silently dropped;
    * plain table-level ``UNIQUE (a, b)`` and ``CONSTRAINT x UNIQUE (a)`` are *not*
      counted as UNIQUE constraints (only ``UNIQUE KEY/INDEX ... (cols)`` and inline
      ``col type UNIQUE``);
    * FK source table is "last ``CREATE TABLE <word>`` before the FK", which yields the
      word ``IF`` for ``CREATE TABLE IF NOT EXISTS t`` and cannot read names with spaces;
    * doubled-quote escapes (``\\`a\\`\\`b\\```) and ``schema.table`` qualifiers are not
      understood; parentheses inside quoted strings/comments confuse the body scanner.

``legacy=False`` (default)
    Same semantics for ordinary DDL, plus fixes for the 13 mandatory regression cases:
    ``IF NOT EXISTS``, missing ``ENGINE``, inline PRIMARY KEY / UNIQUE, composite PK /
    FK, quoted names with spaces, backtick identifiers, FK direction, nullability,
    data-type normalisation, escaped identifiers, and several constraints in one
    statement.  Columns are split on top-level commas (quote/paren/comment aware).

Conventions
-----------
``legacy=True`` nullability (historical):
    ``IS_NULLABLE`` is ``"YES"`` only if the column text contains ``NULL`` and not
    ``NOT NULL`` (so ``DEFAULT NULL`` -> YES, bare ``a int`` -> NO).

``legacy=False`` nullability (authoritative E0 / MySQL-dialect recovery):
    * Explicit ``NOT NULL`` -> ``NO`` (``NULLABILITY_STATUS=explicit_not_null``).
    * Inline ``PRIMARY KEY`` -> ``NO`` (``NULLABILITY_STATUS=primary_key``).
    * Explicit ``NULL`` (and not ``NOT NULL``) -> ``YES`` (``explicit_null``).
    * Otherwise bare column -> ``YES`` (``dialect_default``; MySQL default nullable).
    * Unsupported/placeholder type with no clear null clause -> ``IS_NULLABLE=""``
      and ``NULLABILITY_STATUS=unknown`` (excluded from Domain agreement).

``COLUMN_KEY`` is ``PRI``/``UNI`` only for *inline* ``PRIMARY KEY``/``UNIQUE``.
Table-level keys are returned by :func:`parse_ddl_primary_unique`.
``integer`` is normalised to ``int`` and ``int`` gets ``COLUMN_TYPE='int(11)'``.

Lenient identifier recovery (``legacy=False`` only, documented dataset rule):
    Unquoted names may contain ``-``, ``/``, and mid-identifier ``'``
    (e.g. ``Check-in_Time``, ``State/Province``, ``User's_Last_Login``).
    A ``'`` preceded by an identifier character is *not* treated as a string
    delimiter when masking/splitting, so subsequent columns are not swallowed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Iterator

# --------------------------------------------------------------------------- regexes

# Vendored / legacy type set (must stay frozen for bit-for-bit archive reproduction).
_LEGACY_TYPE_RE = re.compile(
    r"\b(varchar|char|text|int|integer|tinyint|smallint|mediumint|bigint|"
    r"float|double|decimal|numeric|real|datetime|date|time|timestamp|bool|boolean)\b",
    re.IGNORECASE,
)
# Authoritative E0 type set: includes blob/json/enum/binary and common text variants.
_ROBUST_TYPE_RE = re.compile(
    r"\b(varchar|nvarchar|char|nchar|text|tinytext|mediumtext|longtext|"
    r"int|integer|tinyint|smallint|mediumint|bigint|"
    r"float|double|decimal|numeric|real|"
    r"datetime|date|time|timestamp|year|bool|boolean|bit|"
    r"blob|tinyblob|mediumblob|longblob|binary|varbinary|"
    r"json|enum|set)\b",
    re.IGNORECASE,
)
# Back-compat alias used by older tests / imports.
_TYPE_RE = _ROBUST_TYPE_RE

# Vendored header pattern (legacy mode).
_LEGACY_HEADER_RE = re.compile(
    r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?"
    r"(?:[`\"]([^`\"]+)[`\"]|([A-Za-z_][\w$]*))"
    r"\s*\(",
    re.IGNORECASE,
)
# Kept for callers that still reference the old compiled pattern names.
_CREATE_TABLE_HEADER_RE = _LEGACY_HEADER_RE
_TABLE_RE = _LEGACY_HEADER_RE

# One SQL identifier: `a b`, "a b", [a b] or bare word.  Doubled delimiters escape.
_IDENT = r"(?:`(?:[^`]|``)+`|\"(?:[^\"]|\"\")+\"|\[[^\]]+\]|[^\W\d][\w$]*)"
# Lenient bare column/table tokens for dataset recovery (hyphen, slash, mid-word apostrophe).
_LENIENT_BARE_IDENT = r"[A-Za-z_][\w$/\-]*(?:'[A-Za-z_][\w$/\-]*)*"
_ROBUST_COL_NAME = (
    r"(?:`(?:[^`]|``)+`|\"(?:[^\"]|\"\")+\"|\[[^\]]+\]|" + _LENIENT_BARE_IDENT + r")"
)
_ROBUST_HEADER_RE = re.compile(
    r"CREATE\s+(?:(?:GLOBAL\s+|LOCAL\s+)?(?:TEMP|TEMPORARY)\s+)?TABLE\s+"
    r"(?:IF\s+NOT\s+EXISTS\s+)?"
    r"(?:(?:" + _IDENT + r")\s*\.\s*)*"
    r"(" + _IDENT + r")\s*\(",
    re.IGNORECASE,
)

_INT_TYPES = frozenset({"int", "tinyint", "smallint", "mediumint", "bigint", "integer"})
_STR_TYPES = frozenset({"varchar", "nvarchar", "char", "nchar", "text", "tinytext", "mediumtext", "longtext"})
_BINARY_TYPES = frozenset({"blob", "tinyblob", "mediumblob", "longblob", "binary", "varbinary"})

_SKIP_PREFIXES = (
    "PRIMARY KEY",
    "FOREIGN KEY",
    "UNIQUE",
    "KEY ",
    "CONSTRAINT",
    "CHECK ",
    "INDEX ",
)
_ROBUST_SKIP_PREFIXES = _SKIP_PREFIXES + ("FULLTEXT", "SPATIAL")

# Placeholder / non-types seen in RSchema DDL that must not become VARCHAR(255).
_UNSUPPORTED_TYPE_TOKENS = frozenset({"null", "none", "unknown", "n/a", "na"})


# --------------------------------------------------------------------------- helpers


def unquote_identifier(token: str) -> str:
    """Strip one layer of ``\\`..\\```, ``".."``, ``'..'`` or ``[..]`` and unescape doubles.

    >>> unquote_identifier('`a``b`')
    'a`b'
    >>> unquote_identifier('"Order Items"')
    'Order Items'
    """
    t = (token or "").strip()
    if len(t) >= 2:
        if t[0] == t[-1] and t[0] in "`\"'":
            q = t[0]
            return t[1:-1].replace(q + q, q)
        if t[0] == "[" and t[-1] == "]":
            return t[1:-1]
    return t


def _prev_nonspace(text: str, i: int) -> str:
    j = i - 1
    while j >= 0 and text[j] in " \t":
        j -= 1
    return text[j] if j >= 0 else ""


def _apostrophe_is_string_delimiter(text: str, i: int) -> bool:
    """True if ``text[i]`` is a SQL string quote, not a mid-identifier apostrophe.

    Dataset-recovery rule (robust mode): an apostrophe immediately after an
    identifier character (``User's_Name``) is part of the identifier.
    """
    prev = _prev_nonspace(text, i)
    if prev and (prev.isalnum() or prev in "_$"):
        return False
    return True


def _mask_noise(text: str, *, lenient_apostrophe: bool = True) -> str:
    """Return ``text`` with quoted spans, strings and comments replaced by spaces.

    Length is preserved so indices into the masked text are valid for the original.
    Delimiters of quoted spans are kept (as the quote char) so that tokenisation of the
    original string is not disturbed; only the *inner* characters are blanked.

    With ``lenient_apostrophe=True`` (default, robust path), mid-identifier ``'`` does
    not open a string span, preventing subsequent columns from disappearing.
    """
    out = list(text)
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch == "-" and text.startswith("--", i):
            j = text.find("\n", i)
            j = n if j == -1 else j
            for k in range(i, j):
                out[k] = " "
            i = j
        elif ch == "/" and text.startswith("/*", i):
            j = text.find("*/", i + 2)
            j = n if j == -1 else j + 2
            for k in range(i, j):
                out[k] = " "
            i = j
        elif ch == "'" and lenient_apostrophe and not _apostrophe_is_string_delimiter(text, i):
            i += 1
        elif ch in "`\"'":
            j = i + 1
            while j < n:
                if text[j] == ch:
                    if j + 1 < n and text[j + 1] == ch:  # doubled quote = escape
                        j += 2
                        continue
                    break
                if ch == "'" and text[j] == "\\" and j + 1 < n:
                    j += 2
                    continue
                j += 1
            for k in range(i + 1, min(j, n)):
                out[k] = " "
            i = j + 1
        else:
            i += 1
    return "".join(out)


def _split_top_level(body: str, *, lenient_apostrophe: bool = True) -> list[str]:
    """Split ``body`` on commas at paren depth 0, ignoring quotes/strings/comments."""
    masked = _mask_noise(body, lenient_apostrophe=lenient_apostrophe)
    parts: list[str] = []
    depth = 0
    start = 0
    for i, ch in enumerate(masked):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        elif ch == "," and depth == 0:
            parts.append(body[start:i])
            start = i + 1
    parts.append(body[start:])
    return [p for p in parts]


def _strip_comments(body: str, *, lenient_apostrophe: bool = True) -> str:
    """Remove ``--`` and ``/* */`` comments while leaving quoted text untouched."""
    out: list[str] = []
    i, n = 0, len(body)
    while i < n:
        ch = body[i]
        if ch == "-" and body.startswith("--", i):
            j = body.find("\n", i)
            i = n if j == -1 else j
        elif ch == "/" and body.startswith("/*", i):
            j = body.find("*/", i + 2)
            i = n if j == -1 else j + 2
        elif ch == "'" and lenient_apostrophe and not _apostrophe_is_string_delimiter(body, i):
            out.append(ch)
            i += 1
        elif ch in "`\"'":
            j = i + 1
            while j < n:
                if body[j] == ch:
                    if j + 1 < n and body[j + 1] == ch:
                        j += 2
                        continue
                    break
                if ch == "'" and body[j] == "\\" and j + 1 < n:
                    j += 2
                    continue
                j += 1
            out.append(body[i : j + 1])
            i = j + 1
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def _split_ident_list(text: str) -> list[str]:
    """``"`a`, `b c`"`` -> ``['a', 'b c']`` (top-level comma split + unquote)."""
    return [unquote_identifier(p) for p in _split_top_level(text) if p.strip()]


# --------------------------------------------------------------------------- types


def _parse_data_type(line: str, *, legacy: bool = False) -> tuple[str, str]:
    """Return ``(DATA_TYPE, COLUMN_TYPE)`` for the text following a column name.

    ``integer`` -> ``int``; ``int`` -> ``int(11)``; ``varchar/char/decimal/numeric`` keep
    their ``(args)``.

    * ``legacy=True``: unknown/absent type falls back to ``("varchar", "varchar(255)")``
      (vendored behaviour).
    * ``legacy=False``: unknown/absent type returns ``("", "")`` — never invent a type.
    """
    rx = _LEGACY_TYPE_RE if legacy else _ROBUST_TYPE_RE
    m = rx.search(line)
    if not m:
        return ("varchar", "varchar(255)") if legacy else ("", "")
    dtype = m.group(1).lower()
    if dtype == "integer":
        dtype = "int"
    if dtype == "nvarchar":
        dtype = "varchar"
    if dtype == "nchar":
        dtype = "char"
    col_type = dtype
    paren = re.search(r"\(([^)]+)\)", line)
    if paren and dtype in ("varchar", "char", "decimal", "numeric", "enum", "set", "binary", "varbinary"):
        col_type = f"{dtype}({paren.group(1)})"
    elif dtype == "int":
        col_type = "int(11)"
    return dtype, col_type


def _infer_nullability(rest: str, *, legacy: bool, inline_pri: bool) -> tuple[str, str]:
    """Return ``(IS_NULLABLE, NULLABILITY_STATUS)``.

    See module docstring for legacy vs MySQL-dialect robust rules.
    """
    has_not_null = bool(re.search(r"\bNOT\s+NULL\b", rest, re.IGNORECASE))
    has_null = bool(re.search(r"\bNULL\b", rest, re.IGNORECASE)) and not has_not_null
    if legacy:
        if has_null:
            return "YES", "explicit_null"
        return "NO", "legacy_default_not_null"
    if has_not_null:
        return "NO", "explicit_not_null"
    if inline_pri:
        return "NO", "primary_key"
    if has_null:
        return "YES", "explicit_null"
    return "YES", "dialect_default"


# --------------------------------------------------------------------------- tables


def _body_end_legacy(ddl: str, start: int) -> int:
    depth = 1
    i = start
    while i < len(ddl) and depth:
        ch = ddl[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        i += 1
    return i


def _body_end_robust(ddl: str, start: int) -> int:
    masked = _mask_noise(ddl[start:], lenient_apostrophe=True)
    depth = 1
    i = 0
    while i < len(masked) and depth:
        ch = masked[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        i += 1
    return start + i


def iter_ddl_table_bodies(ddl: str, *, legacy: bool = False) -> Iterator[tuple[str, str]]:
    """Yield ``(table_name, body)`` for each ``CREATE TABLE`` in ``ddl``.

    Handles ``IF NOT EXISTS`` and statements without ``ENGINE=``.  Empty/blank input
    yields nothing.  In robust mode table names are unquoted/unescaped and may be
    schema-qualified (the last identifier is the table name).
    """
    if not (ddl or "").strip():
        return
    if legacy:
        for m in _LEGACY_HEADER_RE.finditer(ddl):
            table = (m.group(1) or m.group(2) or "").strip()
            if not table:
                continue
            start = m.end()
            i = _body_end_legacy(ddl, start)
            yield table, ddl[start : i - 1]
        return
    # Use finditer so a malformed / unclosed first table cannot suppress later
    # CREATE TABLE headers.  Some LLM outputs place ``ENGINE=...`` inside the
    # column list (comma before ENGINE, missing ``)``); paren-depth scanning then
    # swallows the rest of the file.  Clamp the body at the next CREATE TABLE.
    matches = list(_ROBUST_HEADER_RE.finditer(ddl))
    for idx, m in enumerate(matches):
        table = unquote_identifier(m.group(1)).strip()
        start = m.end()
        paren_end = _body_end_robust(ddl, start)
        next_start = matches[idx + 1].start() if idx + 1 < len(matches) else None
        if next_start is not None and paren_end > next_start:
            # Unclosed body would absorb the next table — truncate before it.
            body = ddl[start:next_start]
            # Drop a trailing comma left by ``PRIMARY KEY (...), ENGINE=...`` patterns.
            body = re.sub(r",\s*$", "", body.rstrip())
            # If ENGINE leaked into the body without a closing paren, strip it.
            body = re.sub(
                r",?\s*ENGINE\s*=.*$",
                "",
                body,
                flags=re.IGNORECASE | re.DOTALL,
            )
            if table:
                yield table, body
        else:
            if table:
                yield table, ddl[start : max(start, paren_end - 1)]


def _name_and_rest(text: str, *, legacy: bool = False) -> tuple[str, str] | None:
    """Split a column definition into ``(unquoted_name, rest)`` (no type requirement)."""
    if text.upper().startswith(_ROBUST_SKIP_PREFIXES if not legacy else _SKIP_PREFIXES):
        return None
    if legacy:
        m = re.match(r"(" + _IDENT + r")\s+(.+)", text)
    else:
        m = re.match(r"(" + _ROBUST_COL_NAME + r"|'(?:[^']|'')+')\s+(.+)", text)
    if not m:
        return None
    return unquote_identifier(m.group(1)), m.group(2)


def _first_token(rest: str) -> str:
    m = re.match(r"([A-Za-z_][\w$]*)", (rest or "").strip())
    return (m.group(1).lower() if m else "")


def _column_item_to_obj(
    item: str, ord_pos: int, *, legacy: bool
) -> dict[str, Any] | None:
    line = item.strip().rstrip(",")
    if not line:
        return None
    upper = line.upper()
    if upper.startswith(_SKIP_PREFIXES if legacy else _ROBUST_SKIP_PREFIXES):
        return None
    if legacy:
        col_match = re.match(r"[`'\"]([^`'\"]+)[`'\"]\s+(.+)|(\w+)\s+(.+)", line)
        if not col_match:
            return None
        if col_match.group(1) is not None:
            col_name, rest = col_match.group(1), col_match.group(2)
        else:
            col_name, rest = col_match.group(3), col_match.group(4)
        if not _LEGACY_TYPE_RE.search(rest):
            return None
        dtype, col_type = _parse_data_type(rest, legacy=True)
        type_status = "ok"
        nullable, null_status = _infer_nullability(rest, legacy=True, inline_pri=False)
        # preserve exact legacy YES/NO rule (ignore primary_key special-case)
        nullable = (
            "YES"
            if re.search(r"\bNULL\b", rest, re.IGNORECASE)
            and not re.search(r"\bNOT\s+NULL\b", rest, re.IGNORECASE)
            else "NO"
        )
        null_status = "explicit_null" if nullable == "YES" else "legacy_default_not_null"
    else:
        # Keep newlines out of the name/rest match but do not collapse the item before
        # top-level splitting — splitting already happened.
        line_n = re.sub(r"\s+", " ", line)
        col_match = re.match(r"(" + _ROBUST_COL_NAME + r"|'(?:[^']|'')+')\s+(.+)", line_n)
        if not col_match:
            return None
        col_name, rest = unquote_identifier(col_match.group(1)), col_match.group(2)
        inline_pri = bool(re.search(r"\bPRIMARY\s+KEY\b", rest, re.IGNORECASE))
        if _ROBUST_TYPE_RE.search(rest):
            dtype, col_type = _parse_data_type(rest, legacy=False)
            type_status = "ok"
            nullable, null_status = _infer_nullability(rest, legacy=False, inline_pri=inline_pri)
        else:
            # Recover structural column for unsupported/placeholder types; never invent VARCHAR.
            tok = _first_token(rest)
            if tok in _UNSUPPORTED_TYPE_TOKENS or tok:
                dtype, col_type = "", ""
                type_status = "unsupported"
                # Strip the placeholder type token before reading nullability clauses so
                # ``AccountID null`` is *unknown*, not ``explicit_null``.
                rest_clauses = re.sub(
                    r"^\s*(?:" + "|".join(sorted(_UNSUPPORTED_TYPE_TOKENS, key=len, reverse=True)) + r")\b",
                    "",
                    rest,
                    count=1,
                    flags=re.IGNORECASE,
                ).strip()
                if re.search(r"\bNOT\s+NULL\b", rest_clauses, re.IGNORECASE):
                    nullable, null_status = "NO", "explicit_not_null"
                elif re.search(r"\bNULL\b", rest_clauses, re.IGNORECASE):
                    nullable, null_status = "YES", "explicit_null"
                elif inline_pri or re.search(r"\bPRIMARY\s+KEY\b", rest_clauses, re.IGNORECASE):
                    nullable, null_status = "NO", "primary_key"
                else:
                    nullable, null_status = "", "unknown"
            else:
                return None
    col_key = ""
    if re.search(r"\bPRIMARY\s+KEY\b", rest, re.IGNORECASE):
        col_key = "PRI"
    elif re.search(r"\bUNIQUE\b", rest, re.IGNORECASE):
        col_key = "UNI"
    return {
        "COLUMN_NAME": col_name,
        "ORDINAL_POSITION": ord_pos,
        "COLUMN_DEFAULT": None,
        "IS_NULLABLE": nullable,
        "NULLABILITY_STATUS": null_status,
        "DATA_TYPE": dtype,
        "TYPE_STATUS": type_status,
        "CHARACTER_MAXIMUM_LENGTH": 255 if dtype in ("varchar", "char") else None,
        "NUMERIC_PRECISION": None,
        "NUMERIC_SCALE": None,
        "COLUMN_TYPE": col_type,
        "COLUMN_KEY": col_key,
        "EXTRA": "",
        "COLUMN_COMMENT": "",
    }


def metadata_from_ddl(ddl: str, database: str = "", *, legacy: bool = False) -> dict:
    """Build ``{"database", "tables", "columns_by_table"}`` metadata from DDL text.

    ``columns_by_table[t]`` is a list of information-schema style column dicts
    (``COLUMN_NAME``, ``DATA_TYPE``, ``IS_NULLABLE`` ...).  Empty/blank DDL gives empty
    ``tables``/``columns_by_table``.  If no table body could be parsed but ``CREATE TABLE``
    headers exist, tables are listed with empty column lists (legacy fallback).
    """
    if not (ddl or "").strip():
        return {"database": database, "tables": [], "columns_by_table": {}}

    tables: list[str] = []
    columns_by_table: dict[str, list[dict]] = {}

    for table, body in iter_ddl_table_bodies(ddl, legacy=legacy):
        tables.append(table)
        col_objs: list[dict] = []
        ord_pos = 0
        if legacy:
            items = body.split("\n")
        else:
            items = _split_top_level(_strip_comments(body))
        for item in items:
            obj = _column_item_to_obj(item, ord_pos + 1, legacy=legacy)
            if obj is None:
                continue
            ord_pos += 1
            col_objs.append(obj)
        columns_by_table[table] = col_objs

    if not tables:
        rx = _LEGACY_HEADER_RE
        tables = [
            (m.group(1) or m.group(2) or "").strip()
            for m in rx.finditer(ddl)
            if (m.group(1) or m.group(2))
        ]
        columns_by_table = {t: [] for t in tables}

    return {"database": database, "tables": tables, "columns_by_table": columns_by_table}


def ensure_prediction_metadata(pred_meta: dict, pred_ddl: str, database: str = "", *, legacy: bool = False) -> dict:
    """Return prediction metadata with DDL as the authoritative structural source when present.

    E0 predictions are SQL DDL. When ``pred_ddl`` contains parseable ``CREATE TABLE``
    statements, structural tables/columns come from :func:`metadata_from_ddl`. Supplied
    JSON metadata is compared for diagnostics and never silently preferred when it would
    drop DDL columns or invent metadata-only tables that contradict the DDL.

    When DDL is empty/missing, the (possibly empty) JSON metadata is returned unchanged
    so older empty-failure dumps remain evaluable.
    """
    meta = dict(pred_meta or {})
    ddl = (pred_ddl or "").strip()
    if not ddl:
        meta.setdefault("database", database or meta.get("database") or "")
        meta.setdefault("tables", list(meta.get("tables") or []))
        meta.setdefault("columns_by_table", dict(meta.get("columns_by_table") or {}))
        return meta

    parsed = metadata_from_ddl(
        ddl, database=database or meta.get("database") or "", legacy=legacy
    )
    mismatches: list[str] = []
    meta_tables = [str(t) for t in (meta.get("tables") or [])]
    parsed_tables = list(parsed.get("tables") or [])
    meta_cbt = meta.get("columns_by_table") or {}
    parsed_cbt = parsed.get("columns_by_table") or {}

    meta_col_n = sum(len(v or []) for v in meta_cbt.values())
    parsed_col_n = sum(len(v or []) for v in parsed_cbt.values())
    if meta_tables and set(map(str.lower, meta_tables)) != set(map(str.lower, parsed_tables)):
        mismatches.append(
            f"table_set_mismatch meta={sorted(meta_tables)} ddl={sorted(parsed_tables)}"
        )
    if meta_col_n and meta_col_n != parsed_col_n:
        mismatches.append(f"column_count_mismatch meta={meta_col_n} ddl={parsed_col_n}")

    # Type conflicts on shared (table, column) names — diagnostic only.
    for t in parsed_tables:
        pcols = {str(c.get("COLUMN_NAME") or "").lower(): c for c in (parsed_cbt.get(t) or [])}
        # find matching meta table (case-insensitive)
        mt = next((x for x in meta_cbt if str(x).lower() == str(t).lower()), None)
        if mt is None:
            continue
        for mc in meta_cbt.get(mt) or []:
            name = str(mc.get("COLUMN_NAME") or "").lower()
            if not name or name not in pcols:
                continue
            md = (mc.get("DATA_TYPE") or "").strip().lower()
            pd = (pcols[name].get("DATA_TYPE") or "").strip().lower()
            if md and pd and md != pd:
                mismatches.append(f"type_mismatch {t}.{name}: meta={md} ddl={pd}")

    out = {
        "database": parsed.get("database") or meta.get("database") or database or "",
        "tables": parsed_tables,
        "columns_by_table": parsed_cbt,
    }
    if mismatches:
        out["_metadata_ddl_mismatches"] = mismatches
    return out


# --------------------------------------------------------------------------- constraints

_LEGACY_FK_RE = re.compile(
    r"FOREIGN\s+KEY\s+\(([^)]+)\)\s+REFERENCES\s+[`']?(\w+)[`']?\s*\(([^)]+)\)",
    re.IGNORECASE,
)
_ROBUST_FK_RE = re.compile(
    r"FOREIGN\s+KEY\s*(?:" + _IDENT + r"\s*)?\(([^)]+)\)\s*REFERENCES\s+"
    r"(?:(?:" + _IDENT + r")\s*\.\s*)*(" + _IDENT + r")\s*(?:\(([^)]+)\))?",
    re.IGNORECASE,
)
_INLINE_REF_RE = re.compile(
    r"\bREFERENCES\s+(?:(?:" + _IDENT + r")\s*\.\s*)*(" + _IDENT + r")\s*(?:\(([^)]+)\))?",
    re.IGNORECASE,
)

FKTuple = tuple[str, list[str], str, list[str]]


def parse_ddl_fks(ddl: str, *, legacy: bool = False) -> tuple[list[FKTuple], int]:
    """Extract foreign keys as ``(from_table, from_cols, to_table, to_cols)`` tuples.

    Direction is always *referencing* -> *referenced*.  Returns ``(fks, n_composite)``.
    Robust mode also reads inline ``col type REFERENCES t(col)`` and ``FOREIGN KEY idx (..)``.
    """
    fks: list[FKTuple] = []
    if legacy:
        for m in _LEGACY_FK_RE.finditer(ddl):
            from_cols = [c.strip().strip("`'").strip() for c in m.group(1).split(",")]
            to_table = m.group(2).strip("`'")
            to_cols = [c.strip().strip("`'").strip() for c in m.group(3).split(",")]
            from_table = ""
            chunk = ddl[: m.start()]
            last = list(re.finditer(r"CREATE\s+TABLE\s+[`']?(\w+)[`']?", chunk, re.IGNORECASE))
            if last:
                from_table = last[-1].group(1).strip("`'")
            if from_table:
                fks.append((from_table, from_cols, to_table, to_cols))
    else:
        for table, body in iter_ddl_table_bodies(ddl):
            clean = _strip_comments(body)
            for item in _split_top_level(clean):
                text = re.sub(r"\s+", " ", item.strip())
                if not text:
                    continue
                m = _ROBUST_FK_RE.search(text)
                if m:
                    cols = _split_ident_list(m.group(1))
                    to_table = unquote_identifier(m.group(2))
                    to_cols = _split_ident_list(m.group(3)) if m.group(3) else []
                    fks.append((table, cols, to_table, to_cols))
                    continue
                # inline column-level REFERENCES (single column)
                nr = _name_and_rest(text)
                im = _INLINE_REF_RE.search(text)
                if nr is not None and im:
                    to_table = unquote_identifier(im.group(1))
                    to_cols = _split_ident_list(im.group(2)) if im.group(2) else []
                    fks.append((table, [nr[0]], to_table, to_cols))
    composite = sum(1 for _, cols, _, _ in fks if len(cols) > 1)
    return fks, composite


def parse_ddl_primary_unique(
    ddl: str, *, legacy: bool = False
) -> tuple[list[tuple[str, list[str]]], list[tuple[str, list[str]]]]:
    """Extract PRIMARY KEY and UNIQUE constraints as ``(table, [cols])`` lists.

    Covers table-level (``PRIMARY KEY (a, b)``) and inline (``a int PRIMARY KEY``) forms.
    Robust mode additionally counts plain ``UNIQUE (cols)`` / ``CONSTRAINT x UNIQUE (cols)``
    (the vendored parser ignores those, see module docstring).
    """
    primaries: list[tuple[str, list[str]]] = []
    uniques: list[tuple[str, list[str]]] = []
    for table, body in iter_ddl_table_bodies(ddl, legacy=legacy):
        if legacy:
            scan = body
            for pk in re.finditer(r"PRIMARY\s+KEY\s*\(([^)]+)\)", scan, re.IGNORECASE):
                cols = [c.strip().strip("`'\"") for c in pk.group(1).split(",")]
                if cols:
                    primaries.append((table, cols))
            for uq in re.finditer(
                r"UNIQUE\s+(?:KEY|INDEX)\s+(?:[`'\"]?\w+[`'\"]?\s*)?\(([^)]+)\)",
                scan,
                re.IGNORECASE,
            ):
                cols = [c.strip().strip("`'\"") for c in uq.group(1).split(",")]
                if cols:
                    uniques.append((table, cols))
            for line in body.split("\n"):
                line = line.strip().rstrip(",")
                if not line:
                    continue
                if line.upper().startswith(_SKIP_PREFIXES):
                    continue
                col_match = re.match(r"[`'\"]([^`'\"]+)[`'\"]|(\w+)", line)
                if not col_match:
                    continue
                col_name = (col_match.group(1) or col_match.group(2) or "").strip()
                rest = line[col_match.end() :]
                if re.search(r"\bPRIMARY\s+KEY\b", rest, re.IGNORECASE):
                    primaries.append((table, [col_name]))
                elif re.search(r"\bUNIQUE\b", rest, re.IGNORECASE):
                    uniques.append((table, [col_name]))
            continue

        for item in _split_top_level(_strip_comments(body)):
            text = re.sub(r"\s+", " ", item.strip())
            if not text:
                continue
            pk = re.match(
                r"(?:CONSTRAINT\s+(?:" + _IDENT + r")\s+)?PRIMARY\s+KEY\s*\(([^)]+)\)",
                text,
                re.IGNORECASE,
            )
            if pk:
                primaries.append((table, _split_ident_list(pk.group(1))))
                continue
            uq = re.match(
                r"(?:CONSTRAINT\s+(?:" + _IDENT + r")\s+)?UNIQUE(?:\s+(?:KEY|INDEX))?\s*"
                r"(?:" + _IDENT + r"\s*)?\(([^)]+)\)",
                text,
                re.IGNORECASE,
            )
            if uq:
                uniques.append((table, _split_ident_list(uq.group(1))))
                continue
            nr = _name_and_rest(text)
            if nr is None:
                continue
            name, rest = nr
            if re.search(r"\bPRIMARY\s+KEY\b", rest, re.IGNORECASE):
                primaries.append((table, [name]))
            elif re.search(r"\bUNIQUE\b", rest, re.IGNORECASE):
                uniques.append((table, [name]))
    return primaries, uniques


def extract_schema_from_metadata(
    meta: dict,
) -> tuple[set[str], dict[str, set[str]], dict[str, dict[str, dict]]]:
    """Flatten metadata into ``(tables, columns_by_table, info_by_table)``.

    ``info_by_table[t][col]`` holds lowercase ``DATA_TYPE``/``COLUMN_TYPE`` and uppercase
    ``IS_NULLABLE``/``COLUMN_KEY``.  If a column name repeats within a table the last
    definition wins (vendored behaviour).
    """
    tables = set((meta or {}).get("tables", []))
    cols_by_table: dict[str, set[str]] = {}
    info_by_table: dict[str, dict[str, dict]] = {}
    for t, cols in ((meta or {}).get("columns_by_table") or {}).items():
        cols_set: set[str] = set()
        info: dict[str, dict] = {}
        for c in cols:
            name = c.get("COLUMN_NAME") or ""
            cols_set.add(name)
            info[name] = {
                "DATA_TYPE": (c.get("DATA_TYPE") or "").lower(),
                "IS_NULLABLE": (c.get("IS_NULLABLE") or "").upper(),
                "NULLABILITY_STATUS": (c.get("NULLABILITY_STATUS") or "").lower(),
                "TYPE_STATUS": (c.get("TYPE_STATUS") or ("ok" if c.get("DATA_TYPE") else "unsupported")).lower(),
                "COLUMN_KEY": (c.get("COLUMN_KEY") or "").upper(),
                "COLUMN_TYPE": (c.get("COLUMN_TYPE") or "").lower(),
            }
        cols_by_table[t] = cols_set
        info_by_table[t] = info
    return tables, cols_by_table, info_by_table


# --------------------------------------------------------------------------- structured

@dataclass
class Column:
    name: str
    dtype: str
    column_type: str = ""
    nullable: bool = True
    primary_key: bool = False
    unique: bool = False


@dataclass
class ForeignKey:
    columns: list[str]
    ref_table: str
    ref_columns: list[str]


@dataclass
class Table:
    name: str
    columns: list[Column] = field(default_factory=list)
    primary_key: list[list[str]] = field(default_factory=list)
    unique: list[list[str]] = field(default_factory=list)
    foreign_keys: list[ForeignKey] = field(default_factory=list)


@dataclass
class Schema:
    tables: list[Table] = field(default_factory=list)

    def table_names(self) -> list[str]:
        return [t.name for t in self.tables]

    def table(self, name: str) -> Table | None:
        for t in self.tables:
            if t.name == name:
                return t
        return None


def parse_ddl(ddl: str, *, legacy: bool = False) -> Schema:
    """Parse DDL into a :class:`Schema` (tables, columns, PK/UNIQUE, FKs).

    ``Table.primary_key`` is a list of key column-lists (usually length 0 or 1);
    ``Table.unique`` likewise for UNIQUE constraints.
    """
    meta = metadata_from_ddl(ddl, legacy=legacy)
    pks, uqs = parse_ddl_primary_unique(ddl, legacy=legacy)
    fks, _ = parse_ddl_fks(ddl, legacy=legacy)
    schema = Schema()
    for t in meta["tables"]:
        tbl = Table(name=t)
        for c in meta["columns_by_table"].get(t, []):
            tbl.columns.append(
                Column(
                    name=c["COLUMN_NAME"],
                    dtype=c["DATA_TYPE"],
                    column_type=c["COLUMN_TYPE"],
                    nullable=(c.get("IS_NULLABLE") or "").upper() == "YES",
                    primary_key=c["COLUMN_KEY"] == "PRI",
                    unique=c["COLUMN_KEY"] == "UNI",
                )
            )
        tbl.primary_key = [cols for tn, cols in pks if tn == t]
        tbl.unique = [cols for tn, cols in uqs if tn == t]
        tbl.foreign_keys = [ForeignKey(c, rt, rc) for tn, c, rt, rc in fks if tn == t]
        schema.tables.append(tbl)
    return schema


def schema_to_dict(schema: Schema) -> dict[str, Any]:
    """Serialize a :class:`Schema` to a JSON-friendly dict."""
    return {
        "tables": [
            {
                "name": t.name,
                "columns": [
                    {
                        "name": c.name,
                        "dtype": c.dtype,
                        "column_type": c.column_type,
                        "nullable": c.nullable,
                        "primary_key": c.primary_key,
                        "unique": c.unique,
                    }
                    for c in t.columns
                ],
                "primary_key": [list(k) for k in t.primary_key],
                "unique": [list(k) for k in t.unique],
                "foreign_keys": [
                    {
                        "columns": list(fk.columns),
                        "ref_table": fk.ref_table,
                        "ref_columns": list(fk.ref_columns),
                    }
                    for fk in t.foreign_keys
                ],
            }
            for t in schema.tables
        ]
    }
