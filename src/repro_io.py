"""Shared I/O helpers for the E1 / E2 / E3 reproduction CLIs (no results, no network, no heavy imports).

Contents
--------
* output-directory guard (generated files may only go to git-ignored locations),
* ``<dataset>_<prompt>_<model>`` run-directory naming used by every E1/E2/E3 CLI,
* prediction-directory loading and alignment against the gold records (by serial / schema id),
* retry-with-backoff wrapper for rate limits,
* constructor (E2/E3) JSON response parsing,
* E3 empty-gold / empty-reconstruction validity helpers,
* fixed-description hash helpers for constructor isolation,
* small CSV / JSON helpers.
"""

from __future__ import annotations

import csv
import hashlib
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
    """Reason a reconstructed-schema entry is unusable, else ``None``."""
    if entry is None:
        return "missing"
    if entry.get("error") or entry.get("skipped"):
        return "error_field"
    ddl = entry.get("ddl")
    if not isinstance(ddl, str) or not ddl.strip():
        return "empty_ddl"
    return None


def gold_is_empty(ddl: str, meta: dict | None = None) -> bool:
    """True when the gold schema has no tables/columns (Enterprise archive/tmp placeholders)."""
    meta = meta or {}
    tables = meta.get("tables") or []
    cbt = meta.get("columns_by_table") or {}
    n_cols = sum(len(v or []) for v in cbt.values())
    if tables or n_cols:
        return False
    return "CREATE TABLE" not in (ddl or "").upper()


def pred_is_structurally_empty(ddl: str, meta: dict | None = None) -> bool:
    """True when a reconstruction has no CREATE TABLE / no parsed tables or columns."""
    meta = meta or {}
    tables = meta.get("tables") or []
    cbt = meta.get("columns_by_table") or {}
    n_cols = sum(len(v or []) for v in cbt.values())
    if tables or n_cols:
        return False
    text = (ddl or "").strip()
    if not text:
        return True
    return "CREATE TABLE" not in text.upper()


def e3_reconstruction_failure(
    entry: dict | None,
    *,
    gold_ddl: str = "",
    gold_meta: dict | None = None,
) -> str | None:
    """E3 validity: empty-gold + empty-pred is a *valid* reconstruction (nGED=0).

    Malformed/missing nonempty reconstructions still fail.  Comment-only DDL against a
    nonempty gold is a failure.  Error/skipped fields always fail.
    """
    if entry is None:
        return "missing"
    if entry.get("error") or entry.get("skipped"):
        return "error_field"
    ddl = entry.get("ddl")
    if not isinstance(ddl, str):
        return "empty_ddl"
    from .schema_parser import ensure_prediction_metadata, metadata_from_ddl

    g_meta = gold_meta if gold_meta is not None else metadata_from_ddl(gold_ddl or "")
    p_meta = ensure_prediction_metadata(entry.get("metadata") or {}, ddl, database=entry.get("database") or "")
    if gold_is_empty(gold_ddl or "", g_meta) and pred_is_structurally_empty(ddl, p_meta):
        return None
    if not ddl.strip():
        return "empty_ddl"
    if pred_is_structurally_empty(ddl, p_meta):
        return "empty_or_unparseable"
    return None


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
    """True if ``path`` is a readable JSON with a non-empty reconstructed ``ddl`` for ``schema_id``."""
    return _complete(path, schema_id, ddl_failure)


def is_complete_e3_ddl_record(
    path: Path,
    schema_id: str,
    *,
    gold_ddl: str = "",
    gold_meta: dict | None = None,
) -> bool:
    """E3 resume check: allows valid empty-gold + empty-reconstruction records."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return False
    if not isinstance(data, dict) or str(data.get("id") or "") != str(schema_id):
        return False
    return e3_reconstruction_failure(data, gold_ddl=gold_ddl, gold_meta=gold_meta) is None


def sha256_text(text: str) -> str:
    """SHA-256 hex digest of UTF-8 text (used for fixed-description isolation checks)."""
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def description_hash(entry: dict | None) -> str | None:
    """Return the SHA-256 of ``nl_text`` when the entry is a usable description, else ``None``."""
    if nl_failure(entry) is not None:
        return None
    assert entry is not None
    return sha256_text(entry["nl_text"])


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


def parse_constructor_response(text: str) -> tuple[dict | None, str | None]:
    """Parse the constructor reply into ``{"ddl": str, "metadata": dict}``.

    Tolerates markdown fences and leading/trailing prose around the single JSON object.
    Returns ``(obj, None)`` or ``(None, reason)``.
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
    if not isinstance(ddl, str) or not ddl.strip():
        return None, "missing_ddl"
    meta = obj.get("metadata")
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
    "ddl_failure",
    "description_hash",
    "e3_reconstruction_failure",
    "expand",
    "generate_with_backoff",
    "gold_is_empty",
    "is_complete_ddl_record",
    "is_complete_e3_ddl_record",
    "is_complete_nl_record",
    "is_transient_error",
    "load_prediction_dir",
    "nl_failure",
    "parse_constructor_response",
    "pred_is_structurally_empty",
    "read_csv",
    "sha256_text",
    "upsert_csv",
    "write_csv",
    "write_json",
]
