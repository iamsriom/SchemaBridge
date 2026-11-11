"""Counterfactual DDL-parser patches for the E0 Table V audit (diagnostic ONLY).

``src/schema_parser.py`` is NOT modified; ``apply()`` monkey-patches the *imported module* in
the current process so the effect of each suspected defect can be measured on the real
prediction trees / gold DDL.  Flags:

  fix_apostrophe  F1  a ``'`` after a space (``DEFAULT ''``) opens a string; only a ``'``
                      *immediately* after an identifier character is mid-identifier
  fix_unterminated F2 a table body that never closes ends at the next CREATE TABLE header
  fix_header      F3  unquoted names with ``-`` / ``/`` are accepted in CREATE TABLE headers
  fix_unescape    F5  literal two-character ``\\n`` / ``\\t`` in DDL are real whitespace

Never import this from production code.
"""
import re
import src.schema_parser as sp  # noqa: E402 (repo root must be on sys.path)

_orig_mask = sp._mask_noise

def _apostrophe_is_string_delimiter_fixed(text, i):
    # mid-identifier apostrophe only when *immediately* preceded by an identifier char
    prev = text[i-1] if i > 0 else ""
    if prev and (prev.isalnum() or prev in "_$"):
        return False
    return True

def iter_bodies_fixed(ddl, *, legacy=False):
    if legacy:
        yield from _orig_iter(ddl, legacy=True); return
    if not (ddl or "").strip():
        return
    if UNESCAPE:
        ddl = ddl.replace("\\n", "\n").replace("\\t", "\t")
    masked = sp._mask_noise(ddl, lenient_apostrophe=True)
    heads = list(sp._ROBUST_HEADER_RE.finditer(masked))
    for k, m in enumerate(heads):
        # table name from original text (masking blanks quoted inner chars)
        mo = sp._ROBUST_HEADER_RE.match(ddl, m.start())
        if mo is None:
            continue
        table = sp.unquote_identifier(mo.group(1)).strip()
        start = mo.end()
        limit = heads[k+1].start() if k + 1 < len(heads) else len(ddl)
        depth, i = 1, start
        while i < limit and depth:
            ch = masked[i]
            if ch == "(": depth += 1
            elif ch == ")": depth -= 1
            i += 1
        end = i
        body = ddl[start:max(start, end-1)] if depth == 0 else ddl[start:end]
        if table:
            yield table, body

_orig_iter = sp.iter_ddl_table_bodies
UNESCAPE = False

_HEADER_FIXED = re.compile(
    r"CREATE\s+(?:(?:GLOBAL\s+|LOCAL\s+)?(?:TEMP|TEMPORARY)\s+)?TABLE\s+"
    r"(?:IF\s+NOT\s+EXISTS\s+)?"
    r"(?:(?:" + sp._IDENT + r")\s*\.\s*)*"
    r"(" + sp._IDENT + r"|" + sp._LENIENT_BARE_IDENT + r")\s*\(",
    re.IGNORECASE,
)

def apply(fix_apostrophe=True, fix_unterminated=True, fix_header=False, fix_unescape=False):
    global UNESCAPE
    UNESCAPE = fix_unescape
    if fix_header:
        sp._ROBUST_HEADER_RE = _HEADER_FIXED
    if fix_apostrophe:
        sp._apostrophe_is_string_delimiter = _apostrophe_is_string_delimiter_fixed
    if fix_unterminated:
        sp.iter_ddl_table_bodies = iter_bodies_fixed
