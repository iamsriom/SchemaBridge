"""Metric primitives for the five-element schema evaluation (T, A, D, E, R).

Everything here is pure arithmetic on counts or label sets, except
:func:`normalized_graph_edit_distance`, which first derives label sets from metadata/DDL.

Empty-set policies (read before comparing numbers!)
---------------------------------------------------
The paper pipeline uses **different** conventions at different aggregation levels; each
helper documents which one it implements:

``micro`` aggregation (:func:`micro_prf`, :func:`micro_aggregate`)
    Counts are summed over all schemas first.  Empty denominators give ``0.0``:
    ``precision = matched / recreated`` (0 if ``recreated == 0``),
    ``recall = matched / gold`` (0 if ``gold == 0``), ``F1 = 0`` if ``P + R == 0``,
    ``hallucination_rate = max(0, recreated - matched) / recreated`` (0 if ``recreated == 0``).
    This is what produces the paper's E0/E2 F1 columns.

per-schema vacuous policy (:func:`set_prf` with ``empty="vacuous"``)
    Used by the original per-schema scorers: an empty *gold* gives recall ``1.0`` and an
    empty *prediction* gives precision ``1.0``; both empty -> P = R = F1 = 1.0.
    ``empty="zero"`` instead returns 0.0 for any empty denominator (micro convention).

zero-score policy for failed predictions (:func:`zero_scored_schema_metrics`)
    Historical PaperMethods macro policy: missing/failed/empty prediction as
    ``F1 = 0, nGED = 1.0, hallucination = 1.0`` and still divide by all gold schemas.
    Authoritative E0 (Table V) instead scores failures as an *empty prediction*
    against the retained gold (gold counts included in micro F1; nGED = 1;
    per-dimension Hall. rates stay 0 because Recreated = 0) and reports
    :func:`aggregate_hallucination_micro`.

nGED (:func:`normalized_graph_edit_distance`)
    ``edit_cost / max(gold_size + pred_size, 1)`` where size = #tables + #column labels +
    #FK edges.  Both graphs empty -> 0.0.  NOTE: the vendored docstring says
    ``max(gold_size, pred_size, 1)`` but the *code* (and the report text) divide by the
    **sum** of the two sizes; this module follows the code, since that is what produced
    the archived numbers.
"""

from __future__ import annotations

from typing import Any, Callable, Iterable

from .normalization import normalize_rschema_name, type_family
from .schema_parser import extract_schema_from_metadata, parse_ddl_fks

ELEMENTS = ("tables", "attributes", "domain", "entity", "referential")

# Authoritative E0 Hall. aggregate (Tables V–VI): Domain excluded so RSchema /
# SchemaBench remain comparable without synthetic type agreement.
HALLUCINATION_DIMS = ("tables", "attributes", "entity", "referential")

NameFn = Callable[[str], str]


# --------------------------------------------------------------------------- PRF helpers


def f1_score(precision: float, recall: float) -> float:
    """Harmonic mean; ``0.0`` when ``precision + recall == 0``."""
    if precision + recall <= 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def set_prf(gold: Iterable[Any], pred: Iterable[Any], *, empty: str = "vacuous") -> dict[str, float]:
    """Precision/recall/F1 between two collections (compared as sets).

    ``empty="vacuous"`` (default): empty gold -> recall 1.0, empty pred -> precision 1.0,
    so two empty sets score 1.0/1.0/1.0.  ``empty="zero"``: empty denominators -> 0.0
    (so two empty sets score 0/0/0), matching micro-aggregation.
    """
    if empty not in ("vacuous", "zero"):
        raise ValueError("empty must be 'vacuous' or 'zero'")
    g, p = set(gold), set(pred)
    tp = len(g & p)
    vac = 1.0 if empty == "vacuous" else 0.0
    precision = tp / len(p) if p else vac
    recall = tp / len(g) if g else vac
    return {"precision": precision, "recall": recall, "f1": f1_score(precision, recall)}


def hallucination_rate(recreated: int, matched: int) -> float:
    """``max(0, recreated - matched) / recreated``; ``0.0`` when nothing was recreated."""
    if recreated <= 0:
        return 0.0
    return max(0, recreated - matched) / recreated


def micro_prf(gold: int, recreated: int, matched: int) -> dict[str, float | int]:
    """Micro P/R/F1 + hallucination from *summed* counts (empty denominators -> 0.0).

    Returns the same fields as the vendored ``agg_element``: gold, recreated, matched,
    hallucinated, hallucination_rate, precision, recall, f1.
    """
    hall = max(0, recreated - matched)
    precision = matched / recreated if recreated else 0.0
    recall = matched / gold if gold else 0.0
    return {
        "gold": gold,
        "recreated": recreated,
        "matched": matched,
        "hallucinated": hall,
        "hallucination_rate": hall / recreated if recreated else 0.0,
        "precision": precision,
        "recall": recall,
        "f1": f1_score(precision, recall),
    }


def micro_f1(gold: int, recreated: int, matched: int) -> float:
    """Micro F1 from gold/recreated/matched counts (0.0 if any denominator is empty)."""
    return float(micro_prf(gold, recreated, matched)["f1"])


def micro_aggregate(items: list[dict], key: str) -> dict[str, float | int]:
    """Sum ``items[i][key]['gold'|'recreated'|'matched']`` and return :func:`micro_prf`.

    An empty ``items`` list yields all-zero counts and metrics.
    """
    g = sum(s[key]["gold"] for s in items)
    r = sum(s[key]["recreated"] for s in items)
    m = sum(s[key]["matched"] for s in items)
    return micro_prf(g, r, m)


def micro_aggregate_all(items: list[dict]) -> dict[str, dict]:
    """:func:`micro_aggregate` for each of the five elements."""
    return {k: micro_aggregate(items, k) for k in ELEMENTS}


def aggregate_hallucination_micro(
    items: list[dict],
    *,
    dims: tuple[str, ...] | None = None,
) -> float:
    """Unweighted mean of dimension-wise *micro* false-positive rates (E0 Hall.).

    Default dimensions are :data:`HALLUCINATION_DIMS` = ``(T, A, E, R)`` — Domain is
    **excluded** so Hall. is comparable across RSchema and SchemaBench without
    synthetic type/nullability agreement.

    For each dimension ``d``, counts are summed over all evaluated schemata first:
    ``H_d = max(0, Σ P_{i,d} − Σ M_{i,d}) / Σ P_{i,d}`` (0 if the denominator is 0).
    Reported Hallucination: ``H = (1/|dims|) Σ_d H_d``.

    Empty / failed predictions contribute ``P=0, M=0`` and do **not** inflate ``H``
    (unlike the historical PaperMethods macro policy that forced Hall.=1).

    Pass ``dims=ELEMENTS`` to recover the historical five-dimensional mean (audit only).
    """
    use_dims = dims if dims is not None else HALLUCINATION_DIMS
    if not use_dims:
        return 0.0
    aggregates = micro_aggregate_all(items)
    return sum(
        hallucination_rate(aggregates[d]["recreated"], aggregates[d]["matched"]) for d in use_dims
    ) / len(use_dims)


def aggregate_hallucination_micro_5dim(items: list[dict]) -> float:
    """Historical E0 Hall.: mean of five micro FP rates including Domain (audit only)."""
    return aggregate_hallucination_micro(items, dims=ELEMENTS)


def macro_mean(values: Iterable[float]) -> float:
    """Arithmetic mean; ``0.0`` for an empty input."""
    vals = list(values)
    return sum(vals) / len(vals) if vals else 0.0


# --------------------------------------------------------------------------- exact match / difficulty


def is_exact_match(tables: dict, attributes: dict, domain: dict, entity: dict, referential: dict) -> bool:
    """True when gold == recreated == matched for all five elements.

    Two completely empty schemas count as an exact match (0 == 0 == 0).
    """
    for row in (tables, attributes, domain, entity, referential):
        if not (row.get("gold", 0) == row.get("recreated", 0) == row.get("matched", 0)):
            return False
    return True


def schema_difficulty(table_count: int, column_count: int) -> str:
    """easy: <=3 tables & <=30 columns; medium: <=15 & <=150; otherwise hard."""
    if table_count <= 3 and column_count <= 30:
        return "easy"
    if table_count <= 15 and column_count <= 150:
        return "medium"
    return "hard"


# --------------------------------------------------------------------------- zero-score policy


def zero_scored_schema_metrics() -> dict[str, Any]:
    """Per-schema metrics for a failed/missing/empty prediction (PaperMethods zero policy).

    F1 = 0 on every element, nGED = 1.0 (worst), hallucination = 1.0 (worst).  Counts are
    left at zero because the macro means of the policy do not use them.
    """
    return {
        "per_schema_f1": {k: 0.0 for k in ELEMENTS},
        "normalized_graph_edit_distance": 1.0,
        "hallucination_rate_by_dimension": {k: 1.0 for k in ELEMENTS},
        "per_schema_hallucination": 1.0,
        "scored_as_zero": True,
    }


# --------------------------------------------------------------------------- nGED


def column_labels(
    meta: dict,
    name_fn: NameFn = normalize_rschema_name,
    *,
    names_only: bool = False,
) -> dict[str, set]:
    """``table_norm ->`` attribute label set from metadata.

    Default labels are ``(col_norm, type_family, nullable YES/NO)``.
    With ``names_only=True`` (authoritative E0 structural nGED), labels are just
    ``col_norm`` — no synthetic type/nullability contribution.

    Missing nullability defaults to ``"NO"``.  If two raw tables normalise to the same
    key the later one overwrites the earlier (vendored behaviour).
    """
    out: dict[str, set] = {}
    tables, cols_by_table, info = extract_schema_from_metadata(meta)
    for t in sorted(tables, reverse=True):  # deterministic under normalisation collisions
        tn = name_fn(t)
        labels: set = set()
        for col in cols_by_table.get(t, set()):
            cn = name_fn(col)
            if names_only:
                labels.add(cn)
            else:
                inf = info.get(t, {}).get(col, {})
                labels.add(
                    (cn, type_family(inf.get("DATA_TYPE") or ""), (inf.get("IS_NULLABLE") or "NO").upper())
                )
        out[tn] = labels
    return out


def fk_edges(
    ddl: str, name_fn: NameFn = normalize_rschema_name, *, legacy: bool = False
) -> set[tuple[str, tuple[str, ...], str, tuple[str, ...]]]:
    """Directed FK edges ``(src_table, src_cols, dst_table, dst_cols)``, names normalised."""
    fks, _ = parse_ddl_fks(ddl, legacy=legacy)
    return {
        (
            name_fn(t),
            tuple(name_fn(c) for c in cols),
            name_fn(tt),
            tuple(name_fn(c) for c in refs),
        )
        for t, cols, tt, refs in fks
    }


def graph_size(tables: set, attrs: dict[str, set], fks: set) -> int:
    """#table nodes + #column labels + #FK edges."""
    return len(tables) + sum(len(v) for v in attrs.values()) + len(fks)


def graph_edit_cost(
    g_attrs: dict[str, set],
    p_attrs: dict[str, set],
    g_fks: set,
    p_fks: set,
) -> tuple[int, int]:
    """Return ``(edit_cost, normaliser)`` for two schema graphs given as label sets.

    edit_cost = |table symmetric difference|
              + column-label symmetric difference on tables present in both
              + all column labels of tables present in only one side
              + |FK symmetric difference|.
    normaliser = ``max(gold_size + pred_size, 1)``.
    """
    g_tables, p_tables = set(g_attrs), set(p_attrs)
    table_edits = len(g_tables ^ p_tables)
    both = g_tables & p_tables
    attr_edits = sum(len(g_attrs[t] ^ p_attrs[t]) for t in both)
    attr_edits += sum(len(g_attrs[t]) for t in g_tables - p_tables)
    attr_edits += sum(len(p_attrs[t]) for t in p_tables - g_tables)
    fk_edits = len(g_fks ^ p_fks)
    denom = max(graph_size(g_tables, g_attrs, g_fks) + graph_size(p_tables, p_attrs, p_fks), 1)
    return table_edits + attr_edits + fk_edits, denom


def normalized_graph_edit_distance(
    gold_meta: dict,
    gold_ddl: str,
    pred_meta: dict,
    pred_ddl: str,
    *,
    name_fn: NameFn = normalize_rschema_name,
    legacy: bool = False,
    names_only: bool = False,
) -> float:
    """nGED in ``[0, 1]`` (lower is better, 0 = identical under ``name_fn``).

    Adapted from ``evaluate_exp4_text2schema.normalized_graph_edit_distance``; see the
    module docstring for the empty-graph policy and the normaliser.

    ``names_only=True``: attribute labels are column names only (E0 genuine structural
    nGED — excludes type family / nullability, including synthetic RSchema types).
    """
    cost, denom = graph_edit_cost(
        column_labels(gold_meta, name_fn, names_only=names_only),
        column_labels(pred_meta, name_fn, names_only=names_only),
        fk_edges(gold_ddl, name_fn, legacy=legacy),
        fk_edges(pred_ddl, name_fn, legacy=legacy),
    )
    return cost / denom


__all__ = [
    "ELEMENTS",
    "HALLUCINATION_DIMS",
    "aggregate_hallucination_micro",
    "aggregate_hallucination_micro_5dim",
    "column_labels",
    "f1_score",
    "fk_edges",
    "graph_edit_cost",
    "graph_size",
    "hallucination_rate",
    "is_exact_match",
    "macro_mean",
    "micro_aggregate",
    "micro_aggregate_all",
    "micro_f1",
    "micro_prf",
    "normalized_graph_edit_distance",
    "schema_difficulty",
    "set_prf",
    "zero_scored_schema_metrics",
]
