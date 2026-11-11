#!/usr/bin/env python3
"""Unified two-axis schema classification: size (small/medium/large) and content (easy/medium/hard)."""
from __future__ import annotations

import re
from dataclasses import dataclass

SIZE_LABELS = ("small", "medium", "large")
CONTENT_LABELS = ("easy", "medium", "hard")

CONTENT_SCORE_EASY_MAX = 4
CONTENT_SCORE_HARD_MIN = 10

CLASSIFICATION_METRICS_SECTION = """
  Size (structural scale, unified across datasets):
    small  = table_count ≤ 5 AND column_count ≤ 50
    medium = not small AND table_count ≤ 15 AND column_count ≤ 150
    large  = everything else

  Content complexity (constraint richness, orthogonal to size):
    content_score = 2*min(fk_count,10) + 3*composite_fk_count + min(unique_count,5) + max(0, cols_per_table-10)/5
    easy   = content_score < 4
    medium = 4 ≤ content_score < 10
    hard   = content_score ≥ 10
"""


@dataclass
class GoldFeatures:
    table_count: int
    column_count: int
    fk_count: int
    composite_fk_count: int
    pk_count: int
    unique_count: int
    cols_per_table: float
    constraint_density: float
    content_score: float


_CREATE_TABLE_RE = re.compile(
    r"CREATE\s+TABLE(?:\s+IF\s+NOT\s+EXISTS)?\s+[`']?(\w+)[`'\"]?\s*",
    re.IGNORECASE,
)


def parse_ddl_fks(ddl: str) -> tuple[list[tuple[str, list[str], str, list[str]]], int]:
    fks: list[tuple[str, list[str], str, list[str]]] = []
    pattern = re.compile(
        r"FOREIGN\s+KEY\s*\(([^)]+)\)\s+REFERENCES\s+[`']?\(?[`']?(\w+)[`'\"]?\)?[`']?\s*\(([^)]+)\)",
        re.IGNORECASE,
    )
    for m in pattern.finditer(ddl or ""):
        from_cols = [c.strip().strip("`'").strip() for c in m.group(1).split(",")]
        to_table = m.group(2).strip("`'")
        to_cols = [c.strip().strip("`'").strip() for c in m.group(3).split(",")]
        from_table = ""
        pos = m.start()
        chunk = (ddl or "")[:pos]
        last_create = list(_CREATE_TABLE_RE.finditer(chunk))
        if last_create:
            from_table = last_create[-1].group(1).strip("`'")
        if from_table:
            fks.append((from_table, from_cols, to_table, to_cols))
    composite_count = sum(1 for _, from_cols, _, _ in fks if len(from_cols) > 1)
    return fks, composite_count


def _split_create_table_blocks(ddl: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    pattern = re.compile(
        r"CREATE\s+TABLE(?:\s+IF\s+NOT\s+EXISTS)?\s+[`']?(\w+)[`'\"]?\s*\(",
        re.IGNORECASE,
    )
    for m in pattern.finditer(ddl or ""):
        table = m.group(1).strip("`'")
        start = m.end()
        depth = 1
        i = start
        while i < len(ddl) and depth > 0:
            ch = ddl[i]
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            i += 1
        body = ddl[start : i - 1] if depth == 0 else ddl[start:]
        blocks.append((table, body))
    return blocks


def _split_column_definitions(body: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    for ch in body:
        if ch == "(":
            depth += 1
            current.append(ch)
        elif ch == ")":
            depth -= 1
            current.append(ch)
        elif ch == "," and depth == 0:
            part = "".join(current).strip()
            if part:
                parts.append(part)
            current = []
        else:
            current.append(ch)
    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return parts


def _first_column_name(part: str) -> str | None:
    m = re.match(r"\s*[`'\"]?(\w+)[`'\"]?", part.strip())
    return m.group(1) if m else None


def _mask_backtick_identifiers(text: str) -> str:
    return re.sub(r"`[^`]*`", "``", text)


def _parse_table_primary_unique(table: str, body: str) -> tuple[list[tuple[str, list[str]]], list[tuple[str, list[str]]]]:
    primaries: list[tuple[str, list[str]]] = []
    uniques: list[tuple[str, list[str]]] = []
    table_level_pk_cols: list[list[str]] = []

    for pk in re.finditer(r"PRIMARY\s+KEY\s*\(([^)]+)\)", body, re.IGNORECASE):
        cols = [c.strip().strip("`'\" ") for c in pk.group(1).split(",") if c.strip()]
        if cols:
            primaries.append((table, cols))
            table_level_pk_cols.append(cols)

    table_level_pk_flat = {c.lower() for cols in table_level_pk_cols for c in cols}

    for part in _split_column_definitions(body):
        if re.search(r"\bPRIMARY\s+KEY\b(?!\s*\()", part, re.IGNORECASE):
            col = _first_column_name(part)
            if col and col.lower() not in table_level_pk_flat:
                primaries.append((table, [col]))

    for uq in re.finditer(
        r"UNIQUE\s+(?:KEY|INDEX)\s+(?:[`'\"]?\w+[`'\"]?\s*)?\(([^)]+)\)|(?<!KEY\s)(?<!INDEX\s)\bUNIQUE\s*\(([^)]+)\)",
        body,
        re.IGNORECASE,
    ):
        col_str = uq.group(1) or uq.group(2)
        cols = [c.strip().strip("`'\" ") for c in col_str.split(",") if c.strip()]
        if cols:
            uniques.append((table, cols))

    for part in _split_column_definitions(body):
        masked = _mask_backtick_identifiers(part)
        if re.search(r"\bUNIQUE\s+(?:KEY|INDEX)\b", masked, re.IGNORECASE):
            continue
        if re.search(r"\bUNIQUE\s*\(", masked, re.IGNORECASE):
            continue
        if re.search(r"\bUNIQUE\b", masked, re.IGNORECASE):
            col = _first_column_name(part)
            if col:
                uniques.append((table, [col]))

    return primaries, uniques


def parse_ddl_primary_unique(ddl: str) -> tuple[list[tuple[str, list[str]]], list[tuple[str, list[str]]]]:
    primaries: list[tuple[str, list[str]]] = []
    uniques: list[tuple[str, list[str]]] = []
    for table, body in _split_create_table_blocks(ddl):
        pk, uq = _parse_table_primary_unique(table, body)
        primaries.extend(pk)
        uniques.extend(uq)
    return primaries, uniques


def extract_features_from_rschema_answer(answer: dict) -> GoldFeatures:
    table_count = 0
    column_count = 0
    fk_count = 0
    composite_fk_count = 0
    pk_count = 0
    unique_count = 0

    for _table_name, tdef in (answer or {}).items():
        if not isinstance(tdef, dict):
            continue
        table_count += 1
        attrs = list(tdef.get("Attributes") or [])
        column_count += len(attrs)
        if tdef.get("Primary key"):
            pk_count += 1
        fks = tdef.get("Foreign key") or {}
        if isinstance(fks, dict):
            fk_count += len(fks)
            for _from_attr, ref in fks.items():
                if isinstance(ref, dict) and len(ref) > 1:
                    composite_fk_count += 1

    cols_per_table = column_count / table_count if table_count else 0.0
    constraint_density = (pk_count + unique_count + fk_count) / table_count if table_count else 0.0
    content_score = compute_content_score(fk_count, composite_fk_count, unique_count, cols_per_table)
    return GoldFeatures(
        table_count=table_count,
        column_count=column_count,
        fk_count=fk_count,
        composite_fk_count=composite_fk_count,
        pk_count=pk_count,
        unique_count=unique_count,
        cols_per_table=cols_per_table,
        constraint_density=constraint_density,
        content_score=content_score,
    )


def extract_gold_features(
    ddl: str,
    table_count: int,
    column_count: int,
    *,
    rschema_answer: dict | None = None,
) -> GoldFeatures:
    if rschema_answer is not None:
        return extract_features_from_rschema_answer(rschema_answer)

    if table_count <= 0:
        table_count = len(re.findall(r"CREATE\s+TABLE", ddl or "", re.IGNORECASE))
    if column_count <= 0 and ddl:
        _, cols_by_table, _ = _columns_from_ddl(ddl)
        column_count = sum(len(v) for v in cols_by_table.values())

    fks, composite_fk_count = parse_ddl_fks(ddl or "")
    primaries, uniques = parse_ddl_primary_unique(ddl or "")
    fk_count = len(fks)
    pk_count = len(primaries)
    unique_count = len(uniques)
    cols_per_table = column_count / table_count if table_count else 0.0
    constraint_density = (pk_count + unique_count + fk_count) / table_count if table_count else 0.0
    content_score = compute_content_score(fk_count, composite_fk_count, unique_count, cols_per_table)
    return GoldFeatures(
        table_count=table_count,
        column_count=column_count,
        fk_count=fk_count,
        composite_fk_count=composite_fk_count,
        pk_count=pk_count,
        unique_count=unique_count,
        cols_per_table=cols_per_table,
        constraint_density=constraint_density,
        content_score=content_score,
    )


def _columns_from_ddl(ddl: str) -> tuple[set[str], dict[str, set[str]], dict]:
    tables: set[str] = set()
    cols_by_table: dict[str, set[str]] = {}
    table_pattern = re.compile(r"CREATE\s+TABLE\s+[`']?(\w+)[`']?\s*\(", re.IGNORECASE)
    for m in table_pattern.finditer(ddl):
        tables.add(m.group(1).strip("`'"))
    for t in tables:
        cols_by_table[t] = set()
    return tables, cols_by_table, {}


def compute_content_score(
    fk_count: int,
    composite_fk_count: int,
    unique_count: int,
    cols_per_table: float,
) -> float:
    return (
        2 * min(fk_count, 10)
        + 3 * composite_fk_count
        + min(unique_count, 5)
        + max(0.0, cols_per_table - 10) / 5
    )


def classify_size(table_count: int, column_count: int) -> str:
    if table_count <= 5 and column_count <= 50:
        return "small"
    if table_count <= 15 and column_count <= 150:
        return "medium"
    return "large"


def classify_content(content_score: float) -> str:
    if content_score < CONTENT_SCORE_EASY_MAX:
        return "easy"
    if content_score < CONTENT_SCORE_HARD_MIN:
        return "medium"
    return "hard"


def classify_schema(
    ddl: str,
    table_count: int,
    column_count: int,
    *,
    rschema_answer: dict | None = None,
) -> dict:
    features = extract_gold_features(
        ddl,
        table_count,
        column_count,
        rschema_answer=rschema_answer,
    )
    size = classify_size(features.table_count, features.column_count)
    content = classify_content(features.content_score)
    return {
        "size": size,
        "content": content,
        "content_score": features.content_score,
        "difficulty": size,
        "gold_features": {
            "table_count": features.table_count,
            "column_count": features.column_count,
            "fk_count": features.fk_count,
            "composite_fk_count": features.composite_fk_count,
            "pk_count": features.pk_count,
            "unique_count": features.unique_count,
            "cols_per_table": features.cols_per_table,
            "constraint_density": features.constraint_density,
        },
    }


def schema_difficulty(table_count: int, column_count: int) -> str:
    """Deprecated alias: returns size label for backward compatibility."""
    return classify_size(table_count, column_count)


def _empty_element_row() -> dict:
    return {
        "gold": 0,
        "recreated": 0,
        "matched": 0,
        "hallucinated": 0,
        "hallucination_rate": 0.0,
        "precision": 0.0,
        "recall": 0.0,
        "f1": 0.0,
    }


def aggregate_five_elements_by_field(
    all_items: list[dict],
    field: str,
    labels: tuple[str, ...],
    agg_element,
    five_element_names: list[tuple[str, str]],
) -> tuple[dict[str, int], dict[str, dict]]:
    empty = {k: _empty_element_row() for k, _ in five_element_names}
    counts: dict[str, int] = {}
    fe_by: dict[str, dict] = {}
    for label in labels:
        items = [s for s in all_items if s.get(field) == label]
        counts[label] = len(items)
        fe_by[label] = (
            {k: agg_element(items, k) for k, _ in five_element_names} if items else dict(empty)
        )
    return counts, fe_by


def aggregate_size_content_matrix(
    all_items: list[dict],
    agg_element,
    five_element_names: list[tuple[str, str]],
) -> dict[str, dict[str, dict]]:
    empty = {k: _empty_element_row() for k, _ in five_element_names}
    matrix: dict[str, dict[str, dict]] = {}
    for sz in SIZE_LABELS:
        matrix[sz] = {}
        for ct in CONTENT_LABELS:
            items = [s for s in all_items if s.get("size") == sz and s.get("content") == ct]
            nged = [s["normalized_graph_edit_distance"] for s in items if "normalized_graph_edit_distance" in s]
            matrix[sz][ct] = {
                "count": len(items),
                "mean_normalized_graph_edit_distance": sum(nged) / len(nged) if nged else 0.0,
                "five_elements": (
                    {k: agg_element(items, k) for k, _ in five_element_names} if items else dict(empty)
                ),
            }
    return matrix
