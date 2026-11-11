"""Dataset loaders for the E1/E2 reproduction (read-only; nothing is written on import).

Populations
-----------
* ``enterprise145``: 145 schemas from ``schema/index.json`` + ``<safe_name>.sql``; no gold NL.
* ``schemabench``  : 239 records of ``annotation_ddl.jsonl`` (gold NL = ``question``).
* ``rschema``      : the 381 records whose IDs occur in BOTH ``annotation.jsonl`` and
  ``annotation_ddl.jsonl`` (genuine DDL).  Serials are 1-based positions in the full
  518-record ``annotation.jsonl`` (so they are NOT contiguous 1..381).
  ``load_rschema_logical_518`` lists all 518 logical annotations separately.

Data roots
----------
Searched in this order: explicit ``data_root`` argument (CLI ``--data-root``), the
``SCHEMABRIDGE_DATA_ROOT`` environment variable, then the packaged ``datasets/`` directory.
Each root may use the packaged layout or the archival server layout
(``RSchema/``, ``SchemaBench/Dataset/``, ``Text2ER/schema/``).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGED_DATASETS = REPO_ROOT / "datasets"
DATA_ROOT_ENV = "SCHEMABRIDGE_DATA_ROOT"
DEFAULT_MANIFEST_DIR = REPO_ROOT / "outputs"  # git-ignored

EXPECTED_COUNTS = {
    "enterprise145": 145,
    "schemabench": 239,
    "rschema": 381,
    "rschema_logical": 518,
}
DATASET_LABELS = {
    "enterprise145": "Enterprise-145",
    "schemabench": "SchemaBench",
    "rschema": "RSchema",
}


@dataclass(frozen=True)
class GoldRecord:
    dataset: str
    serial: str
    schema_id: str
    gold_nl: str
    ddl: str
    ddl_source: str
    safe_name: str
    database: str


@dataclass(frozen=True)
class LogicalRecord:
    """One of the 518 RSchema logical annotations (``has_ddl`` marks the 381 with real DDL)."""

    serial: str
    schema_id: str
    gold_nl: str
    safe_name: str
    has_ddl: bool


# --------------------------------------------------------------------------- roots / paths

def data_roots(data_root: str | os.PathLike | None = None) -> list[Path]:
    """Ordered, de-duplicated candidate roots: explicit, env, packaged."""
    roots: list[Path] = []
    for cand in (data_root, os.environ.get(DATA_ROOT_ENV) or None, PACKAGED_DATASETS):
        if cand is None:
            continue
        p = Path(cand).expanduser()
        if p not in roots:
            roots.append(p)
    return roots


_LAYOUTS: dict[str, tuple[str, ...]] = {
    "rschema/annotation.jsonl": ("rschema/annotation.jsonl", "RSchema/annotation.jsonl", "annotation.jsonl"),
    "rschema/annotation_ddl.jsonl": (
        "rschema/annotation_ddl.jsonl",
        "RSchema/annotation_ddl.jsonl",
        "annotation_ddl.jsonl",
    ),
    "schemabench/annotation_ddl.jsonl": (
        "schemabench/annotation_ddl.jsonl",
        "SchemaBench/annotation_ddl.jsonl",
        "SchemaBench/Dataset/annotation_ddl.jsonl",
        "annotation_ddl.jsonl",
    ),
    "enterprise145/schema": (
        "enterprise145/schema",
        "Text2ER/schema",
        "schema",
    ),
}


def resolve_path(key: str, data_root: str | os.PathLike | None = None) -> Path:
    """First existing path for logical ``key`` over all data roots."""
    tried: list[Path] = []
    for root in data_roots(data_root):
        for rel in _LAYOUTS[key]:
            p = root / rel
            tried.append(p)
            if key == "enterprise145/schema":
                if (p / "index.json").is_file():
                    return p
            elif p.is_file():
                return p
    raise FileNotFoundError(f"could not locate {key!r}; tried: " + ", ".join(str(t) for t in tried))


# --------------------------------------------------------------------------- helpers

def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with Path(path).open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _ddl_text(answer: object) -> str:
    return answer.strip() if isinstance(answer, str) else ""


def count_tables(ddl: str) -> int:
    return len(re.findall(r"CREATE\s+TABLE", ddl, re.IGNORECASE))


def _check_count(name: str, records: Sequence, strict: bool) -> None:
    expected = EXPECTED_COUNTS[name]
    if strict and len(records) != expected:
        raise ValueError(f"{name}: expected {expected} records, found {len(records)}")


# --------------------------------------------------------------------------- loaders

def load_rschema_ddl_by_id(data_root: str | os.PathLike | None = None) -> dict[str, str]:
    out: dict[str, str] = {}
    for rec in load_jsonl(resolve_path("rschema/annotation_ddl.jsonl", data_root)):
        rid, ddl = rec.get("id"), _ddl_text(rec.get("answer"))
        if rid and ddl:
            out[str(rid)] = ddl
    return out


def load_rschema_logical_518(
    data_root: str | os.PathLike | None = None, *, strict: bool = True
) -> list[LogicalRecord]:
    """All logical annotations, in file order (serial = 1-based position)."""
    ann = load_jsonl(resolve_path("rschema/annotation.jsonl", data_root))
    ddl_ids = set(load_rschema_ddl_by_id(data_root))
    out = [
        LogicalRecord(
            serial=f"{i:04d}",
            schema_id=str(rec.get("id") or ""),
            gold_nl=(rec.get("question") or "").strip(),
            safe_name=f"rschema_{i:04d}",
            has_ddl=str(rec.get("id") or "") in ddl_ids,
        )
        for i, rec in enumerate(ann, start=1)
    ]
    _check_count("rschema_logical", out, strict)
    return out


def load_rschema_381(data_root: str | os.PathLike | None = None, *, strict: bool = True) -> list[GoldRecord]:
    """Intersection of annotation.jsonl and annotation_ddl.jsonl IDs (genuine DDL)."""
    ddl_by_id = load_rschema_ddl_by_id(data_root)
    out: list[GoldRecord] = []
    for i, rec in enumerate(load_jsonl(resolve_path("rschema/annotation.jsonl", data_root)), start=1):
        rid = str(rec.get("id") or "")
        if rid not in ddl_by_id:
            continue
        safe = f"rschema_{i:04d}"
        out.append(
            GoldRecord(
                dataset="RSchema",
                serial=f"{i:04d}",
                schema_id=rid,
                gold_nl=(rec.get("question") or "").strip(),
                ddl=ddl_by_id[rid],
                ddl_source="annotation_ddl",
                safe_name=safe,
                database=safe,
            )
        )
    _check_count("rschema", out, strict)
    return out


def load_schemabench(data_root: str | os.PathLike | None = None, *, strict: bool = True) -> list[GoldRecord]:
    out: list[GoldRecord] = []
    for i, rec in enumerate(load_jsonl(resolve_path("schemabench/annotation_ddl.jsonl", data_root)), start=1):
        ddl = _ddl_text(rec.get("answer"))
        safe = f"schemabench_{i:04d}"
        out.append(
            GoldRecord(
                dataset="SchemaBench",
                serial=f"{i:04d}",
                schema_id=str(rec.get("id") or ""),
                gold_nl=(rec.get("question") or "").strip(),
                ddl=ddl,
                ddl_source="annotation_ddl" if ddl else "missing",
                safe_name=safe,
                database=safe,
            )
        )
    _check_count("schemabench", out, strict)
    return out


def load_enterprise145(data_root: str | os.PathLike | None = None, *, strict: bool = True) -> list[GoldRecord]:
    """Enterprise-145: gold_nl is empty by design (no gold natural language exists)."""
    schema_dir = resolve_path("enterprise145/schema", data_root)
    idx = json.loads((schema_dir / "index.json").read_text(encoding="utf-8"))
    out: list[GoldRecord] = []
    for i, ds in enumerate(idx.get("datasets", []), start=1):
        safe = ds.get("safe_name") or Path(str(ds.get("ddl_file", ""))).stem
        ddl_path = schema_dir / (ds.get("ddl_file") or f"{safe}.sql")
        ddl = ddl_path.read_text(encoding="utf-8") if ddl_path.is_file() else ""
        out.append(
            GoldRecord(
                dataset="Enterprise-145",
                serial=f"{i:04d}",
                schema_id=str(ds.get("id", safe)),
                gold_nl="",
                ddl=ddl,
                ddl_source="enterprise_sql" if ddl else "missing",
                safe_name=safe,
                database=str(ds.get("database") or safe),
            )
        )
    _check_count("enterprise145", out, strict)
    return out


LOADERS = {
    "enterprise145": load_enterprise145,
    "schemabench": load_schemabench,
    "rschema": load_rschema_381,
}


def load_dataset(
    name: str, data_root: str | os.PathLike | None = None, *, strict: bool = True
) -> list[GoldRecord]:
    key = name.lower().replace("-", "").replace("_", "")
    key = {"enterprise": "enterprise145"}.get(key, key)
    if key not in LOADERS:
        raise KeyError(f"unknown dataset {name!r}; expected one of {sorted(LOADERS)}")
    return LOADERS[key](data_root, strict=strict)


def load_all(data_root: str | os.PathLike | None = None, *, strict: bool = True) -> dict[str, list[GoldRecord]]:
    return {k: fn(data_root, strict=strict) for k, fn in LOADERS.items()}


# --------------------------------------------------------------------------- manifests

def manifest_row(rec: GoldRecord) -> dict:
    """Metadata-only row (no DDL / NL text, only hashes and sizes)."""
    row = {k: v for k, v in asdict(rec).items() if k not in ("gold_nl", "ddl")}
    row["n_tables"] = count_tables(rec.ddl)
    row["ddl_sha256"] = hashlib.sha256(rec.ddl.encode("utf-8")).hexdigest()
    row["has_gold_nl"] = bool(rec.gold_nl)
    return row


def _assert_output_dir_ok(out_dir: Path) -> Path:
    out_dir = Path(out_dir).resolve()
    try:
        rel = out_dir.relative_to(REPO_ROOT)
    except ValueError:
        return out_dir  # outside the repo tree: always fine
    if "outputs" not in rel.parts:
        raise ValueError(
            f"refusing to write manifests inside the repo tree outside an 'outputs/' directory: {out_dir}"
        )
    return out_dir


def write_manifest(
    records: Iterable[GoldRecord], dataset: str, out_dir: str | os.PathLike | None = None
) -> Path:
    """Write ``<out_dir>/manifest_<dataset>.jsonl`` (default ``outputs/``, git-ignored)."""
    target = _assert_output_dir_ok(Path(out_dir) if out_dir else DEFAULT_MANIFEST_DIR)
    target.mkdir(parents=True, exist_ok=True)
    path = target / f"manifest_{dataset}.jsonl"
    with path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(manifest_row(rec), ensure_ascii=False) + "\n")
    return path


def prepare_manifests(
    data_root: str | os.PathLike | None = None,
    out_dir: str | os.PathLike | None = None,
    datasets: Sequence[str] = ("enterprise145", "schemabench", "rschema"),
) -> dict[str, Path]:
    """Explicit helper (never called on import) to emit metadata manifests."""
    return {name: write_manifest(load_dataset(name, data_root), name, out_dir) for name in datasets}


def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Inspect datasets / emit metadata manifests (no results).")
    ap.add_argument("--data-root", default=None, help=f"overrides ${DATA_ROOT_ENV}; packaged datasets/ is the fallback")
    ap.add_argument("--dataset", choices=sorted(LOADERS), action="append", help="default: all")
    ap.add_argument("--write-manifests", action="store_true", help="write metadata manifests under --out-dir")
    ap.add_argument("--out-dir", default=None, help="default: <repo>/outputs (git-ignored)")
    args = ap.parse_args(argv)
    names = args.dataset or sorted(LOADERS)
    for name in names:
        recs = load_dataset(name, args.data_root)
        print(f"{DATASET_LABELS[name]}: {len(recs)} schemas")
        if args.write_manifests:
            print("  manifest ->", write_manifest(recs, name, args.out_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
