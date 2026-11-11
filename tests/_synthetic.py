"""Helpers for the synthetic E1/E2 tests (fabricated toy data only; no research results)."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "synthetic"


def load_script(rel: str, name: str):
    """Import ``experiments/E1/evaluate.py``-style scripts by path (their dirs are not packages)."""
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def corpus() -> dict:
    return json.loads((FIXTURES / "tiny_corpus.json").read_text(encoding="utf-8"))


def _jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")


def build_data_root(tmp_path: Path) -> Path:
    """A tiny data root in the packaged layout.

    * rschema: 4 logical annotations (serial 0002 has no genuine DDL) -> 3 DDL-matched schemas
      with NON-contiguous serials 0001, 0003, 0004.
    * schemabench: the 3 schemas.
    * enterprise145: the 3 schemas as .sql files (no gold text).
    """
    c = corpus()
    s = c["schemas"]
    root = tmp_path / "data"
    logical = [s[0], c["logical_only"], s[1], s[2]]
    _jsonl(root / "rschema" / "annotation.jsonl",
           [{"id": r["id"], "question": r["question"], "answer": {}} for r in logical])
    _jsonl(root / "rschema" / "annotation_ddl.jsonl",
           [{"id": r["id"], "question": r["question"], "answer": r["ddl"]} for r in s])
    _jsonl(root / "schemabench" / "annotation_ddl.jsonl",
           [{"id": f"SB-{i}", "question": r["question"], "answer": r["ddl"]} for i, r in enumerate(s, 1)])
    ent = root / "enterprise145" / "schema"
    ent.mkdir(parents=True)
    index = {"datasets": []}
    for r in s:
        name = r["id"].replace("-", "_")
        (ent / f"{name}.sql").write_text(r["ddl"], encoding="utf-8")
        index["datasets"].append({"id": name, "safe_name": name, "ddl_file": f"{name}.sql", "database": name})
    (ent / "index.json").write_text(json.dumps(index), encoding="utf-8")
    return root


def write_e1_preds(pred_dir: Path, gold, texts: dict[str, str | None], *, errors: dict[str, str] | None = None,
                   describer: str | None = None, prompt: str | None = None) -> None:
    """Write NNNN.json (historical format) for ``gold`` records; ``texts`` maps serial -> nl_text.

    With ``describer`` + ``prompt`` the records carry full, correct E1 provenance (llm, model_id,
    prompt_style, generation.prompt_variant / prompt_sha256) as written by ``experiments/E1/run.py``.
    """
    pred_dir.mkdir(parents=True, exist_ok=True)
    for rec in gold:
        if rec.serial not in texts:
            continue
        d = {"text_number": int(rec.serial), "id": rec.schema_id, "llm": "synthetic", "model_id": "synthetic",
             "database": rec.database, "ddl": rec.ddl, "gold_question": rec.gold_nl, "ddl_source": rec.ddl_source,
             "prompt_style": "schema2text1", "nl_text": texts[rec.serial] or ""}
        if describer and prompt:
            from src import inference_clients as ic
            from src import prompt_assets as pa
            from src import repro_io as rio

            d.update(llm=describer, model_id=ic.MODELS[describer].model_id, prompt_style=rio.PROMPT_STYLE[prompt])
            d["generation"] = {"prompt_variant": prompt, "prompt_sha256": pa.EXPECTED_SHA256[prompt],
                               "temperature": 0.2, "max_tokens": 1024}
        if errors and rec.serial in errors:
            d["error"] = errors[rec.serial]
        (pred_dir / f"{rec.serial}.json").write_text(json.dumps(d), encoding="utf-8")


def write_e2_preds(pred_dir: Path, gold, ddls: dict[str, str | None], *, errors: dict[str, str] | None = None) -> None:
    pred_dir.mkdir(parents=True, exist_ok=True)
    for rec in gold:
        if rec.serial not in ddls:
            continue
        d = {"text_number": int(rec.serial), "id": rec.schema_id, "llm": "gpt4omini", "model_id": "gpt-4o-mini",
             "database": rec.database, "nl_text": "x", "gold_question": rec.gold_nl,
             "ddl": ddls[rec.serial] or "", "metadata": {}}
        if errors and rec.serial in errors:
            d["error"] = errors[rec.serial]
        (pred_dir / f"{rec.serial}.json").write_text(json.dumps(d), encoding="utf-8")
