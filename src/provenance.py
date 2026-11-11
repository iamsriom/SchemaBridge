"""Strict E1 -> E2 provenance checks (no network, no heavy imports, no results).

E2 reconstructs schemas from the Schema2Text descriptions produced by E1.  A directory of E1
descriptions is only accepted as the input of a given ``(dataset, describer, prompt)`` E2 run if
every record *proves* where it came from:

* ``id`` equals the gold schema id,
* ``llm`` equals the describer key (the ``MODELS`` keys of :mod:`src.inference_clients`; no
  aliasing -- e.g. ``claude_sonnet_4_6`` is NOT silently relabelled ``sonnet46``),
* ``model_id`` equals ``MODELS[describer].model_id``,
* ``prompt_style`` equals ``PROMPT_STYLE[prompt]``,
* ``generation.prompt_variant`` equals ``prompt`` (checked if present),
* ``generation.prompt_sha256`` equals the pinned hash of the describer prompt,
* ``nl_text`` is usable and no ``error`` is recorded.

Modes
-----
``strict`` (default)  every required provenance field must be present AND correct.
``legacy``            fields that are *missing* are allowed (a warning is returned for each); a field
                      that is present but WRONG is still rejected.  Only used with the explicit
                      ``--allow-legacy-e1`` flag of ``experiments/E2/run.py``.

Directory level (:func:`check_directory`): duplicate schema ids across prediction files are an
error; in strict mode mixed ``prompt_style`` values inside one directory are an error too.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from . import inference_clients as ic
from . import prompt_assets as pa
from . import repro_io as rio
from .datasets_io import GoldRecord

MODES = ("strict", "legacy")


class ProvenanceError(ValueError):
    """An E1 description record (or directory) does not match the requested E1 provenance."""


def _gen(entry: Mapping[str, Any]) -> Mapping[str, Any]:
    g = entry.get("generation")
    return g if isinstance(g, Mapping) else {}


def _blank(v: Any) -> bool:
    return v is None or (isinstance(v, str) and not v.strip())


def validate_e1_description(
    entry: Mapping[str, Any] | None,
    *,
    gold: GoldRecord,
    dataset: str,
    describer: str,
    prompt: str,
    mode: str = "strict",
) -> list[str]:
    """Validate one E1 record against the requested ``(dataset, describer, prompt)``.

    Raises :class:`ProvenanceError` on any mismatch (and, in strict mode, on any missing
    provenance field).  Returns the list of warnings -- always empty in strict mode; in legacy
    mode one entry per missing provenance field.
    """
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}, got {mode!r}")
    if describer not in ic.DESCRIBER_KEYS:
        raise ProvenanceError(f"unknown describer {describer!r}; expected one of {sorted(ic.DESCRIBER_KEYS)}")
    if prompt not in rio.PROMPT_STYLE:
        raise ProvenanceError(f"unknown prompt {prompt!r}; expected one of {sorted(rio.PROMPT_STYLE)}")
    if not isinstance(entry, Mapping):
        raise ProvenanceError("E1 entry is missing or not a JSON object")
    if entry.get("error"):
        raise ProvenanceError(f"E1 entry carries an error: {str(entry['error'])[:120]}")

    strict = mode == "strict"
    warnings: list[str] = []

    def check(field: str, actual: Any, expected: Any, *, required: bool) -> None:
        if _blank(actual):
            if required and strict:
                raise ProvenanceError(f"missing provenance field {field!r} (strict mode; expected {expected!r})")
            if required:
                warnings.append(f"legacy E1 record: {field} missing (not verified)")
            return
        if str(actual) != str(expected):
            raise ProvenanceError(f"{field} mismatch: record has {actual!r}, expected {expected!r}")

    # identity (always required: it is the alignment key, not just provenance)
    if _blank(entry.get("id")):
        raise ProvenanceError(f"missing 'id' (expected {gold.schema_id!r})")
    check("id", entry.get("id"), gold.schema_id, required=True)
    if not _blank(entry.get("dataset")):
        check("dataset", entry.get("dataset"), dataset, required=False)

    spec = ic.MODELS[describer]
    gen = _gen(entry)
    check("llm", entry.get("llm"), describer, required=True)
    check("model_id", entry.get("model_id"), spec.model_id, required=True)
    check("prompt_style", entry.get("prompt_style"), rio.PROMPT_STYLE[prompt], required=True)
    check("generation.prompt_variant", gen.get("prompt_variant"), prompt, required=False)
    check("generation.prompt_sha256", gen.get("prompt_sha256"), pa.EXPECTED_SHA256[prompt], required=True)

    reason = rio.nl_failure(dict(entry))
    if reason is not None:
        raise ProvenanceError(f"E1 description not usable: {reason}")
    return warnings


def entry_provenance(entry: Mapping[str, Any], *, describer: str, prompt: str, mode: str,
                     warnings: Sequence[str] = ()) -> dict:
    """Provenance fields to copy into an E2 output record (only values that were verified)."""
    gen = _gen(entry)
    verified = {
        "source_schema2text_llm": describer,
        "source_model_id": entry.get("model_id") or None,
        "source_prompt_style": entry.get("prompt_style") or None,
        "source_prompt_variant": gen.get("prompt_variant") or None,
        "source_prompt_sha256": gen.get("prompt_sha256") or None,
    }
    return {
        **verified,
        "source_provenance_mode": mode,
        "source_provenance_warnings": list(warnings),
    }


def check_directory(
    preds: Mapping[str, tuple[dict | None, str | None]],
    *,
    prompt: str,
    mode: str = "strict",
) -> None:
    """Directory-level checks over every readable prediction file.

    * the same schema ``id`` in two files -> :class:`ProvenanceError` (always),
    * more than one distinct ``prompt_style`` -> :class:`ProvenanceError` (strict mode only).
    """
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}, got {mode!r}")
    seen: dict[str, str] = {}
    styles: dict[str, str] = {}
    for stem, (data, _err) in sorted(preds.items()):
        if not data:
            continue
        sid = data.get("id")
        if not _blank(sid):
            if str(sid) in seen:
                raise ProvenanceError(f"duplicate schema id {str(sid)!r} in {seen[str(sid)]}.json and {stem}.json")
            seen[str(sid)] = stem
        style = data.get("prompt_style")
        if not _blank(style):
            styles.setdefault(str(style), stem)
    if mode == "strict" and len(styles) > 1:
        raise ProvenanceError(
            "mixed prompt_style values in the E1 directory: "
            + ", ".join(f"{s} (first in {stem}.json)" for s, stem in sorted(styles.items()))
            + f"; expected only {rio.PROMPT_STYLE[prompt]!r}"
        )


__all__ = ["MODES", "ProvenanceError", "check_directory", "entry_provenance", "validate_e1_description"]
