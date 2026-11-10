"""Identifier / type / name normalisation used by every SchemaBridge metric.

Two levels of name normalisation exist, and which one is used matters for reproducing
published numbers:

* :func:`normalize_identifier` -- *strict*: lowercase + strip one layer of quotes.  This is
  the default of the original Text2Schema2 evaluator (``normalize_name``).
* :func:`normalize_rschema_name` -- *RSchema-style*: additionally removes spaces,
  underscores and hyphens, drops a few plural-ish suffixes and a trailing ``s``.  The
  Exp4 evaluators (RSchema **and** SchemaBench) monkey-patch the strict function with this
  one, so all E0/E2 numbers in the paper use RSchema-style matching.
  Ported verbatim from ``RSchemaCode/evaluate_rschema_predictions.py``.
"""

from __future__ import annotations

import re
from typing import Callable

NameFn = Callable[[str], str]

INT_TYPES = frozenset({"int", "tinyint", "smallint", "mediumint", "bigint", "integer"})
STR_TYPES = frozenset(
    {"varchar", "nvarchar", "char", "nchar", "text", "tinytext", "mediumtext", "longtext"}
)
BINARY_TYPES = frozenset({"blob", "tinyblob", "mediumblob", "longblob", "binary", "varbinary"})

# Exact tuples used by the vendored ``evaluate_one`` domain check (note: no "integer").
_LEGACY_INT_TYPES = frozenset({"int", "tinyint", "smallint", "mediumint", "bigint"})


def normalize_identifier(name: str | None) -> str:
    """Lowercase an identifier and strip one layer of quoting.

    Handles ``\\`x\\```, ``"x"``, ``'x'`` and ``[x]`` (with doubled-delimiter escapes);
    outer whitespace is stripped first.  ``None`` becomes ``""``.

    >>> normalize_identifier('`Users`')
    'users'
    >>> normalize_identifier('"Order Items"')
    'order items'
    """
    s = (name or "").strip()
    if len(s) >= 2:
        if s[0] == s[-1] and s[0] in "`\"'":
            q = s[0]
            s = s[1:-1].replace(q + q, q)
        elif s[0] == "[" and s[-1] == "]":
            s = s[1:-1]
    return s.strip().lower()


def normalize_rschema_name(s: str | None) -> str:
    """RSchema-style name normalisation (ported verbatim).

    Gold ``'Airplane Number'`` must match predicted ``'airplane_number'`` or
    ``'airplanes'``:  lowercase, drop whitespace/``_``/``-``, strip one of the suffixes
    ``members, member, details, records, record`` (when the remaining stem is longer than
    2 chars), then drop a single trailing ``s`` (not ``ss``) when longer than 3 chars.
    """
    s = re.sub(r"[\s_\-]+", "", (s or "").strip().lower())
    for suf in ("members", "member", "details", "records", "record"):
        if len(s) > len(suf) + 2 and s.endswith(suf):
            s = s[: -len(suf)]
            break
    if len(s) > 3 and s.endswith("s") and not s.endswith("ss"):
        s = s[:-1]
    return s


def type_family(dtype: str | None) -> str:
    """Collapse SQL types to a family: ``int`` / ``str`` / ``binary`` / lowercase type.

    ``int``-family: int, integer, tinyint, smallint, mediumint, bigint.
    ``str``-family: varchar, nvarchar, char, nchar, text, tiny/medium/longtext.
    ``binary``-family: blob variants, binary, varbinary.
    Empty / unknown types return ``""`` (never invent a family).
    Everything else is returned lowercased (so ``decimal`` != ``float`` != ``datetime``).
    """
    d = (dtype or "").strip().lower()
    if not d:
        return ""
    if d in INT_TYPES:
        return "int"
    if d in STR_TYPES:
        return "str"
    if d in BINARY_TYPES:
        return "binary"
    return d


def types_compatible(gold_type: str | None, pred_type: str | None, *, legacy: bool = False) -> bool:
    """True when two ``DATA_TYPE`` values agree up to type family.

    ``legacy=True`` reproduces the vendored ``evaluate_one`` which does *not* treat the
    literal string ``integer`` as part of the int family (the parser never emits it, but
    LLM-provided JSON metadata can).

    Empty / unsupported types never match (no fabricated Domain agreement).
    """
    g = (gold_type or "").lower()
    p = (pred_type or "").lower()
    if not g or not p:
        return False
    if g == p:
        return True
    if legacy:
        if g in _LEGACY_INT_TYPES and p in _LEGACY_INT_TYPES:
            return True
        return g in STR_TYPES and p in STR_TYPES
    gf, pf = type_family(g), type_family(p)
    if not gf or not pf:
        return False
    return gf == pf


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def normalize_ddl(ddl: str) -> str:
    """Light DDL normalisation: drop blank and ``--`` comment lines, collapse whitespace, lowercase."""
    lines = []
    for line in (ddl or "").splitlines():
        line = line.strip()
        if not line or line.startswith("--"):
            continue
        lines.append(line)
    return normalize_whitespace(" ".join(lines)).lower()
