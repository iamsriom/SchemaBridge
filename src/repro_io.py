"""Shared I/O helpers for the E1 / E2 reproduction CLIs (no results, no network, no heavy imports).

Contents
--------
* output-directory guard (generated files may only go to git-ignored locations),
* ``<dataset>_<prompt>_<model>`` run-directory naming used by every E1/E2 CLI,
* prediction-directory loading and alignment against the gold records (by serial / schema id),
* retry-with-backoff wrapper for rate limits,
* constructor (E2) JSON response parsing (an explicit empty reconstruction is a valid answer),
* empty-schema classification (``ddl_outcome``: ok / valid_empty / incorrect_empty / failed),
* small CSV / JSON helpers.
"""

from __future__ import annotations

import csv
import json
import random
import re
import time
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

from .datasets_io import GoldRecord

REPO_ROOT = Path(__file__).resolve().parents[1]

DATASETS = ("enterprise145", "rschema", "schemabench")
DATASET_CHOICES = DATASETS + ("all",)
PROMPT_VARIANTS = ("basic", "detailed")
PROMPT_STYLE = {"basic": "schema2text1", "detailed": "schema2text2"}
CONSTRUCTOR_KEY = "gpt4omini"

# Repo-relative prefixes (besides any ``outputs`` / ``latex_generated`` / ``api_cache`` path component)
# that are covered by .gitignore and therefore safe for generated files.
_IGNORED_PREFIXES = (("figures", "generated"), ("results", "metrics", "local"))
_IGNORED_PARTS = frozenset({"outputs", "latex_generated", "api_cache"})


# --------------------------------------------------------------------------- output guard


def assert_ignored_out_dir(out_dir: str | Path) -> Path:
    """Return the resolved ``out_dir`` or raise if it is a tracked location inside the repo.

    Generated files are accepted outside the repo tree, or inside it only below a git-ignored
    location (``outputs/``, ``latex_generated/``, ``api_cache/``, ``figures/generated/``,
    ``results/metrics/local/``).
    """
    p = Path(out_dir).expanduser().resolve()
    try:
        rel = p.relative_to(REPO_ROOT)
    except ValueError:
        return p
    parts = rel.parts
    if _IGNORED_PARTS & set(parts):
        return p
    for pref in _IGNORED_PREFIXES:
        if parts[: len(pref)] == pref:
            return p
    raise ValueError(
        f"refusing to write generated files to a tracked repo location: {p}\n"
        "use a path outside the repo or below one of: outputs/, latex_generated/, api_cache/, "
        "figures/generated/, results/metrics/local/"
    )


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: Sequence[dict], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(fieldnames), extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("N/A" if r.get(k) is None else r.get(k)) for k in fieldnames})


def read_csv(path: Path) -> list[dict]:
    with Path(path).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def upsert_csv(path: Path, rows: Sequence[dict], fieldnames: Sequence[str], key_fields: Sequence[str]) -> None:
    """Merge ``rows`` into an existing CSV (rows with the same key are replaced)."""
    merged: dict[tuple, dict] = {}
    if path.is_file():
        for r in read_csv(path):
            merged[tuple(r.get(k, "") for k in key_fields)] = r
    for r in rows:
        merged[tuple(str(r.get(k, "")) for k in key_fields)] = {
            k: ("N/A" if r.get(k) is None else r.get(k)) for k in fieldnames
        }
    write_csv(path, [merged[k] for k in sorted(merged)], fieldnames)


# --------------------------------------------------------------------------- naming


def expand(arg: str, choices: Iterable[str]) -> list[str]:
    """``'all'`` -> every choice (in order); otherwise the single value."""
    return list(choices) if arg == "all" else [arg]


def combo_name(dataset: str, prompt: str, model: str) -> str:
    return f"{dataset}_{prompt}_{model}"


def combo_dir(arg: str | Path | None, default_parent: Path, combo: str, *, multi: bool) -> Path:
    """Directory for one (dataset, prompt, model) run.

    * ``arg is None``      -> ``<default_parent>/<combo>``
    * single combination   -> ``arg`` is used as-is
    * several combinations -> ``arg`` is a parent directory; ``<arg>/<combo>`` is used
    """
    if arg is None:
        return Path(default_parent) / combo
    return Path(arg) / combo if multi else Path(arg)


# --------------------------------------------------------------------------- predictions


def load_prediction_dir(pred_dir: str | Path) -> dict[str, tuple[dict | None, str | None]]:
    """``{stem: (data | None, parse_error | None)}`` for every ``NNNN.json`` in ``pred_dir``."""
    out: dict[str, tuple[dict | None, str | None]] = {}
    for p in sorted(Path(pred_dir).glob("[0-9][0-9][0-9][0-9].json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("top-level JSON value is not an object")
            out[p.stem] = (data, None)
        except Exception as e:  # noqa: BLE001
            out[p.stem] = (None, f"unreadable_json:{type(e).__name__}")
    return out


def align_predictions(
    gold: Sequence[GoldRecord],
    preds: dict[str, tuple[dict | None, str | None]],
) -> list[tuple[GoldRecord, dict | None, str | None]]:
    """One ``(gold, entry, reason)`` per gold record, in gold order.

    Alignment is by file stem == gold serial.  If the entry carries an ``id`` that differs from
    the gold ``schema_id`` the entry is looked up by id instead; if none exists the record is
    reported as ``id_mismatch`` (never silently mis-paired).  ``reason`` is ``None`` when an
    entry was found (its *content* may still be an error record, see :func:`nl_failure`).
    """
    by_id: dict[str, list[dict]] = {}
    for data, _err in preds.values():
        if data and data.get("id"):
            by_id.setdefault(str(data["id"]), []).append(data)
    aligned: list[tuple[GoldRecord, dict | None, str | None]] = []
    for rec in gold:
        data, err = preds.get(rec.serial, (None, "missing_prediction_file"))
        if data is None:
            aligned.append((rec, None, err))
            continue
        pid = data.get("id")
        if pid and str(pid) != rec.schema_id:
            cands = by_id.get(rec.schema_id, [])
            if len(cands) == 1:
                aligned.append((rec, cands[0], None))
            else:
                aligned.append((rec, None, "id_mismatch"))
            continue
        aligned.append((rec, data, None))
    return aligned


def nl_failure(entry: dict | None) -> str | None:
    """Reason a Schema2Text entry is unusable as a hypothesis, else ``None``."""
    if entry is None:
        return "missing"
    if entry.get("error"):
        return "error_field"
    text = entry.get("nl_text")
    if not isinstance(text, str) or not text.strip():
        return "empty_nl_text"
    return None


def ddl_failure(entry: dict | None) -> str | None:
    """Reason a reconstructed-schema entry is unusable, else ``None``.

    Legacy helper: ANY empty ``ddl`` counts as a failure.  Prefer :func:`ddl_outcome`, which
    separates a *valid empty* reconstruction (gold is empty too) from a failed one.
    """
    if entry is None:
        return "missing"
    if entry.get("error") or entry.get("skipped"):
        return "error_field"
    ddl = entry.get("ddl")
    if not isinstance(ddl, str) or not ddl.strip():
        return "empty_ddl"
    return None


# --------------------------------------------------------------------------- empty-schema handling

OUTCOME_STATUSES = ("ok", "valid_empty", "incorrect_empty", "failed")

def _meta_sizes(meta: dict | None) -> tuple[int, int]:
    tables = (meta or {}).get("tables") or []
    cols = (meta or {}).get("columns_by_table") or {}
    n_cols = sum(len(v or []) for v in cols.values()) if isinstance(cols, dict) else 0
    return (len(tables) if isinstance(tables, (list, tuple)) else 0), n_cols


def _blank_or_comment_only(ddl: str | None) -> bool:
    """True for ``''``, whitespace, or text that is nothing but SQL comments."""
    if not isinstance(ddl, str) or not ddl.strip():
        return True
    from .schema_parser import _strip_comments  # lazy: keeps this module cheap to import

    return not _strip_comments(ddl).strip().strip(";").strip()


def gold_is_empty(ddl: str, meta: dict | None = None) -> bool:
    """True if the gold schema has no tables and no columns.

    Uses ``meta`` (``{"tables": [...], "columns_by_table": {...}}``) when given, else the
    metadata parsed from ``ddl`` via :func:`src.schema_parser.metadata_from_ddl`.
    """
    if meta is None:
        from .schema_parser import metadata_from_ddl

        meta = metadata_from_ddl(ddl or "")
    n_tables, n_cols = _meta_sizes(meta)
    return n_tables == 0 and n_cols == 0


def pred_is_structurally_empty(ddl: str, meta: dict | None = None) -> bool:
    """True for an empty / comment-only / table-less reconstruction.

    Empty means: ``ddl`` is blank, comment-only, or has no ``CREATE TABLE`` that parses into tables /
    columns, AND (if ``meta`` is given) ``meta`` lists no tables / columns either.
    """
    if meta is not None and _meta_sizes(meta) != (0, 0):
        return False
    if _blank_or_comment_only(ddl):
        return True
    from .schema_parser import metadata_from_ddl

    return _meta_sizes(metadata_from_ddl(ddl)) == (0, 0)


def ddl_outcome(
    entry: dict | None,
    gold_ddl: str,
    gold_meta: dict | None = None,
    *,
    schema_id: str | None = None,
) -> tuple[str, str | None]:
    """Classify a reconstructed-schema entry against its gold.  Returns ``(status, reason)``.

    ``status``:

    * ``failed``          missing / unreadable entry, ``error`` / ``skipped`` field, no ``ddl`` key,
                          an id that does not match ``schema_id`` (if given), or non-comment text that
                          parses to no schema.  Scored by the fail policy (nGED = 1 under ``score``).
    * ``valid_empty``     a *successful* record (no error, ``ddl`` key present, id matches) whose DDL is
                          empty / comment-only and whose gold is empty too (Case: genuinely empty schema).
    * ``incorrect_empty`` a successful record with an empty DDL against a NON-empty gold.  It is
                          evaluated as an empty prediction through ``evaluate_schema_pair`` (natural
                          nGED), NOT through the forced-failure policy.
    * ``ok``              a successful record with a non-empty reconstruction.

    ``reason`` is ``None`` for ``ok``; otherwise a short code (``missing``, ``error_field``,
    ``missing_ddl``, ``id_mismatch``, ``unparseable_ddl``, ``empty_gold_empty_pred``,
    ``empty_prediction``).  A missing file is NEVER a valid empty reconstruction.
    """
    if not isinstance(entry, dict):
        return "failed", "missing"
    if entry.get("error") or entry.get("skipped"):
        return "failed", "error_field"
    ddl = entry.get("ddl")
    if "ddl" not in entry or not isinstance(ddl, str):
        return "failed", "missing_ddl"
    if schema_id is not None and entry.get("id") is not None and str(entry["id"]) != str(schema_id):
        return "failed", "id_mismatch"

    meta = entry.get("metadata") if isinstance(entry.get("metadata"), dict) else None
    if not pred_is_structurally_empty(ddl, meta):
        return "ok", None

    gold_empty = gold_is_empty(gold_ddl, gold_meta)
    if not _blank_or_comment_only(ddl):
        # text that is neither comments nor a schema: an unparseable answer, not an empty schema
        if gold_empty:
            return "failed", "unparseable_ddl"
        return "incorrect_empty", "empty_prediction"
    if schema_id is not None and entry.get("id") is None:
        return "failed", "missing_id"  # no evidence tying this record to the schema
    if gold_empty:
        return "valid_empty", "empty_gold_empty_pred"
    return "incorrect_empty", "empty_prediction"


def _complete(path: Path, schema_id: str, failure: Callable[[dict | None], str | None]) -> bool:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return False
    return isinstance(data, dict) and failure(data) is None and str(data.get("id") or "") == str(schema_id)


def is_complete_nl_record(path: Path, schema_id: str) -> bool:
    """True if ``path`` is a readable JSON with usable ``nl_text`` for ``schema_id`` (resume check)."""
    return _complete(path, schema_id, nl_failure)


def is_complete_ddl_record(path: Path, schema_id: str) -> bool:
    """Resume check: True if ``path`` holds a finished reconstruction for ``schema_id``.

    Complete = readable JSON object, no ``error`` / ``skipped`` field, ``id`` matches, AND either a
    non-empty ``ddl`` or an explicitly recorded empty reconstruction (``ddl`` key present, possibly
    ``""``, no error).  Missing files, unreadable JSON, error records and records without a ``ddl``
    key are NOT complete (they are retried).
    """
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return False
    if not isinstance(data, dict) or data.get("error") or data.get("skipped"):
        return False
    if str(data.get("id") or "") != str(schema_id):
        return False
    return isinstance(data.get("ddl"), str)


# --------------------------------------------------------------------------- retries

_TRANSIENT = ("rate", "429", "overloaded", "timeout", "timed out", "529", "503", "502", "connection")


def is_transient_error(exc: BaseException) -> bool:
    return any(k in str(exc).lower() for k in _TRANSIENT)


def generate_with_backoff(
    client: Any,
    req: Any,
    *,
    max_retries: int = 5,
    base_delay: float = 2.0,
    max_delay: float = 120.0,
    sleep: Callable[[float], None] = time.sleep,
    jitter: Callable[[], float] = random.random,
) -> str:
    """``client.generate(req)`` retried with exponential backoff (+jitter) on rate-limit-like errors.

    Non-transient errors (bad request, missing key, unconfirmed paid call, ...) are raised
    immediately.  ``max_retries`` is the number of *extra* attempts after the first.
    """
    attempt = 0
    while True:
        try:
            return client.generate(req)
        except Exception as e:  # noqa: BLE001 - SDKs raise many types
            if attempt >= max_retries or not is_transient_error(e):
                raise
            delay = min(max_delay, base_delay * (2**attempt)) * (0.5 + jitter())
            sleep(delay)
            attempt += 1


# --------------------------------------------------------------------------- constructor JSON

_FENCE_RE = re.compile(r"^```[a-zA-Z0-9_-]*\s*\n?(.*?)\n?```\s*$", re.DOTALL)


def parse_constructor_response(text: str, allow_empty_ddl: bool = True) -> tuple[dict | None, str | None]:
    """Parse the constructor reply into ``{"ddl": str, "metadata": dict}``.

    Tolerates markdown fences and leading/trailing prose around the single JSON object.
    Returns ``(obj, None)`` or ``(None, reason)``.

    ``allow_empty_ddl=True`` (default, used by E2): an explicit empty reconstruction
    ``{"ddl": "", "metadata": {...}}`` (``ddl`` a string, ``metadata`` an object) is a SUCCESS with
    ``ddl == ""`` -- a genuinely empty schema is a legitimate answer.  An empty ``ddl`` without a
    ``metadata`` object is still ``missing_ddl`` (indistinguishable from a truncated reply).
    With ``allow_empty_ddl=False`` any empty ``ddl`` is ``missing_ddl`` (legacy behaviour).
    """
    raw = (text or "").strip()
    if not raw:
        return None, "empty_response"
    m = _FENCE_RE.match(raw)
    if m:
        raw = m.group(1).strip()
    obj: Any = None
    try:
        obj = json.loads(raw)
    except Exception:  # noqa: BLE001
        i, j = raw.find("{"), raw.rfind("}")
        if 0 <= i < j:
            try:
                obj = json.loads(raw[i : j + 1])
            except Exception:  # noqa: BLE001
                obj = None
    if not isinstance(obj, dict):
        return None, "invalid_json"
    ddl = obj.get("ddl")
    meta = obj.get("metadata")
    if not isinstance(ddl, str):
        return None, "missing_ddl"
    if not ddl.strip() and not (allow_empty_ddl and isinstance(meta, dict)):
        return None, "missing_ddl"
    return {"ddl": ddl.strip(), "metadata": meta if isinstance(meta, dict) else {}}, None


__all__ = [
    "CONSTRUCTOR_KEY",
    "DATASETS",
    "DATASET_CHOICES",
    "PROMPT_STYLE",
    "PROMPT_VARIANTS",
    "align_predictions",
    "assert_ignored_out_dir",
    "combo_dir",
    "combo_name",
    "OUTCOME_STATUSES",
    "ddl_failure",
    "ddl_outcome",
    "expand",
    "generate_with_backoff",
    "gold_is_empty",
    "is_complete_ddl_record",
    "is_complete_nl_record",
    "is_transient_error",
    "load_prediction_dir",
    "nl_failure",
    "parse_constructor_response",
    "pred_is_structurally_empty",
    "read_csv",
    "upsert_csv",
    "write_csv",
    "write_json",
]
