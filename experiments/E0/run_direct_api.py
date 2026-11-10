#!/usr/bin/env python3
"""Canonical E0 Direct Text2Schema runner for closed API models.

Reads gold NL ``question`` only (never gold DDL). Writes the same contract as
open-weight Exp4/Exp2 dumps::

    results/predictions/e0/rschema_exp4_<llm>/NNNN.{txt,json}
    results/predictions/e0/schemabench_exp2_<llm>/NNNN.{txt,json}

Constructor system prompt: ``prompts/constructor.txt`` (identical contract to
the original Direct open-weight experiments).

Credentials (never logged / printed)::

    OPENAI_API_KEY or /data/openai_api.txt
    ANTHROPIC_API_KEY or /data/anthropic.txt

Paid inference requires explicit ``--confirm-paid``. Dry-run performs no requests.

Examples::

    python experiments/E0/run_direct_api.py --dry-run
    python experiments/E0/run_direct_api.py --limit 1 --confirm-paid
    python experiments/E0/run_direct_api.py --dataset rschema --llm claude_sonnet_4_6 --confirm-paid
    python experiments/E0/run_direct_api.py --dataset schemabench --llm gpt_5_4_mini --confirm-paid
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

DATA_ROOT = Path("/data")
PROMPT_PATH = ROOT / "prompts" / "constructor.txt"
PRED_ROOT = ROOT / "results" / "predictions" / "e0"

OPENAI_KEY_CANDIDATES = [
    DATA_ROOT / "openai_api.txt",
    ROOT / "openai_api.txt",
    DATA_ROOT / "Text2ER" / "openai_api.txt",
]
ANTHROPIC_KEY_CANDIDATES = [
    DATA_ROOT / "anthropic.txt",
    DATA_ROOT / "anthropic_api.txt",
    ROOT / "anthropic.txt",
    DATA_ROOT / "Text2ER" / "anthropic.txt",
]

CLOSED_MODELS: dict[str, dict[str, str]] = {
    "claude_sonnet_4_6": {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-6",
        "display": "Claude Sonnet 4.6",
        "rschema_dir": "rschema_exp4_claude_sonnet_4_6",
        "schemabench_dir": "schemabench_exp2_claude_sonnet_4_6",
    },
    "gpt_5_4_mini": {
        "provider": "openai",
        "model_id": "gpt-5.4-mini",
        "display": "GPT-5.4-mini",
        "rschema_dir": "rschema_exp4_gpt_5_4_mini",
        "schemabench_dir": "schemabench_exp2_gpt_5_4_mini",
    },
}

DATASETS = {
    "rschema": {
        "annotation": ROOT / "datasets" / "rschema" / "annotation.jsonl",
        "prefix": "rschema",
        "dir_key": "rschema_dir",
    },
    "schemabench": {
        "annotation": ROOT / "datasets" / "schemabench" / "annotation_ddl.jsonl",
        "prefix": "schemabench",
        "dir_key": "schemabench_dir",
    },
}

DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_TOKENS = 4096
DEFAULT_SLEEP = 0.15
DEFAULT_RETRIES = 2
DEFAULT_BACKOFF = 2.0


def load_constructor_prompt(path: Path = PROMPT_PATH) -> str:
    if not path.is_file():
        raise SystemExit(f"Constructor prompt missing: {path}")
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise SystemExit(f"Constructor prompt empty: {path}")
    return text


def _read_key_file(candidates: list[Path]) -> str | None:
    for p in candidates:
        if p.is_file():
            key = p.read_text(encoding="utf-8").strip()
            if key:
                return key
    return None


def load_openai_key() -> str:
    key = os.environ.get("OPENAI_API_KEY", "").strip() or _read_key_file(OPENAI_KEY_CANDIDATES)
    if not key:
        raise SystemExit(
            "OpenAI API key not found. Set OPENAI_API_KEY or create a local openai_api.txt "
            "(see docs; never commit credentials)."
        )
    return key


def load_anthropic_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip() or _read_key_file(ANTHROPIC_KEY_CANDIDATES)
    if not key:
        raise SystemExit(
            "Anthropic API key not found. Set ANTHROPIC_API_KEY or create a local anthropic.txt "
            "(see docs; never commit credentials)."
        )
    return key


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    text_number = 0
    with path.open(encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"{path}:{i}: {e}") from e
            text_number += 1
            rec["_text_number"] = text_number
            rows.append(rec)
    return rows


def serial_stem(text_number: int) -> str:
    return f"{text_number:04d}"


def output_paths(out_dir: Path, text_number: int) -> tuple[Path, Path]:
    stem = serial_stem(text_number)
    return out_dir / f"{stem}.txt", out_dir / f"{stem}.json"


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def extract_json_from_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```\s*$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        if start == -1:
            raise
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    return json.loads(text[start : i + 1])
        raise


def _extract_ddl_from_broken_response(text: str) -> dict | None:
    idx = text.find('"ddl"')
    if idx == -1:
        return None
    idx = text.find('"', idx + 5)
    if idx == -1:
        return None
    start = idx + 1
    parts: list[str] = []
    i = start
    while i < len(text):
        c = text[i]
        if c == "\\" and i + 1 < len(text):
            parts.append(text[i : i + 2])
            i += 2
            continue
        if c == '"':
            j = i + 1
            while j < len(text) and text[j] in " \t\n\r":
                j += 1
            if j < len(text) and (text[j] in ",}" or text[j : j + 10] == '"metadata"'):
                break
        parts.append(c)
        i += 1
    else:
        return None
    ddl = "".join(parts).replace("\\n", "\n").replace('\\"', '"').strip()
    if "CREATE TABLE" not in ddl.upper():
        return None
    tables = re.findall(r"CREATE\s+TABLE\s+[`']?(\w+)[`']?", ddl, re.IGNORECASE)
    tables = list(dict.fromkeys(tables))
    return {
        "ddl": ddl,
        "metadata": {"database": "", "tables": tables, "columns_by_table": {t: [] for t in tables}},
    }


def _ddl_only_fallback(text: str, database: str) -> dict | None:
    m = re.search(r"(CREATE\s+TABLE[\s\S]*)", text, re.IGNORECASE)
    if not m:
        return None
    ddl = re.sub(r"```.*$", "", m.group(1).strip(), flags=re.DOTALL).strip()
    if not ddl:
        return None
    tables = re.findall(r"CREATE\s+TABLE\s+[`']?(\w+)[`']?", ddl, re.IGNORECASE)
    tables = list(dict.fromkeys(tables))
    return {
        "ddl": f"-- Schema for database: {database}\n{ddl}",
        "metadata": {
            "database": database,
            "tables": tables,
            "columns_by_table": {t: [] for t in tables},
        },
    }


def database_name(record: dict, prefix: str) -> str:
    if record.get("database"):
        return str(record["database"])
    n = record.get("_text_number")
    if n is not None:
        return f"{prefix}_{int(n):04d}"
    rid = str(record.get("id") or "schema")
    return f"{prefix}_{rid[:12]}"


def build_user_content(nl_text: str, database: str) -> str:
    return "\n".join(
        [
            f"Database name: {database}",
            "",
            "Natural language description:",
            nl_text,
        ]
    )


def prediction_is_valid(data: dict) -> bool:
    ddl = (data.get("ddl") or "").strip()
    return bool(ddl) and not data.get("error") and "CREATE TABLE" in ddl.upper()


def record_done(out_dir: Path, text_number: int) -> bool:
    out_txt, out_json = output_paths(out_dir, text_number)
    if not out_txt.is_file() or not out_json.is_file():
        return False
    try:
        data = json.loads(out_json.read_text(encoding="utf-8"))
    except Exception:
        return False
    return prediction_is_valid(data)


def sanitize_result(result: dict, database: str) -> dict:
    ddl = (result.get("ddl") or "").strip()
    metadata = result.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {"database": database, "tables": [], "columns_by_table": {}}
    metadata.setdefault("database", database)
    if not metadata.get("tables") and ddl:
        tables = re.findall(r"CREATE\s+TABLE\s+[`']?(\w+)[`']?", ddl, re.IGNORECASE)
        metadata["tables"] = list(dict.fromkeys(tables))
    if "columns_by_table" not in metadata:
        metadata["columns_by_table"] = {t: [] for t in metadata.get("tables") or []}
    return {"ddl": ddl, "metadata": metadata}


def save_record(
    out_dir: Path,
    llm_name: str,
    model_id: str,
    rid: str,
    text_number: int,
    nl_text: str,
    database: str,
    result: dict | None,
    error: str | None = None,
) -> None:
    out_txt, out_json = output_paths(out_dir, text_number)
    if result:
        ddl = result.get("ddl", "") or ""
        metadata = result.get("metadata") or {}
        if isinstance(metadata, dict):
            metadata.setdefault("database", database)
            if "tables" not in metadata and "columns_by_table" in metadata:
                metadata["tables"] = list(metadata["columns_by_table"].keys())
        else:
            metadata = {"database": database, "tables": [], "columns_by_table": {}}
        out_obj = {
            "text_number": text_number,
            "id": rid,
            "llm": llm_name,
            "model_id": model_id,
            "database": database,
            "question": nl_text,
            "ddl": ddl,
            "metadata": metadata,
        }
        atomic_write_text(out_txt, ddl)
    else:
        # Never echo secrets; keep error text short and local.
        safe_err = _redact_secrets(str(error or "unknown error"))
        out_obj = {
            "text_number": text_number,
            "id": rid,
            "llm": llm_name,
            "model_id": model_id,
            "database": database,
            "question": nl_text,
            "error": safe_err,
            "ddl": None,
            "metadata": {"database": database, "tables": [], "columns_by_table": {}},
        }
        atomic_write_text(out_txt, f"[ERROR: {safe_err}]\n")
    atomic_write_text(
        out_json,
        json.dumps(out_obj, indent=2, default=str, ensure_ascii=False) + "\n",
    )


_SECRET_RE = re.compile(r"(sk-[A-Za-z0-9_\-]{8,}|sk-ant-[A-Za-z0-9_\-]{8,})")


def _redact_secrets(text: str) -> str:
    return _SECRET_RE.sub("[REDACTED]", text)


def call_openai(client: Any, model_id: str, system: str, user: str, *, temperature: float, max_tokens: int) -> str:
    kwargs: dict[str, Any] = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
    }
    try:
        resp = client.chat.completions.create(**kwargs, max_completion_tokens=max_tokens)
    except Exception:
        resp = client.chat.completions.create(**kwargs, max_tokens=max_tokens)
    return (resp.choices[0].message.content or "").strip()


def call_anthropic(client: Any, model_id: str, system: str, user: str, *, max_tokens: int) -> str:
    # Claude Sonnet 4.6 on this stack: temperature is not an accepted Messages.create arg.
    resp = client.messages.create(
        model=model_id,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(getattr(b, "text", "") or "" for b in (resp.content or [])).strip()


def text_to_schema(
    call_fn: Callable[[str, str], str],
    system_prompt: str,
    nl_text: str,
    database: str,
    max_retries: int = DEFAULT_RETRIES,
    backoff_s: float = DEFAULT_BACKOFF,
) -> dict:
    user = build_user_content(nl_text, database)
    last_err: Exception | None = None
    last_raw: str | None = None
    for attempt in range(max_retries + 1):
        try:
            raw = call_fn(system_prompt, user)
            last_raw = raw
            if not raw:
                raise ValueError("Empty model response")
            out = extract_json_from_response(raw)
            if not isinstance(out, dict) or "ddl" not in out:
                raise ValueError("Model response missing 'ddl'")
            if "metadata" not in out:
                out["metadata"] = {"database": database, "tables": [], "columns_by_table": {}}
            return sanitize_result(out, database)
        except Exception as e:  # noqa: BLE001 — retry transport + parse failures
            last_err = e
            if attempt >= max_retries:
                fb = last_raw and (
                    _extract_ddl_from_broken_response(last_raw)
                    or _ddl_only_fallback(last_raw, database)
                )
                if fb:
                    return sanitize_result(fb, database)
                break
            time.sleep(backoff_s * (2**attempt))
    raise last_err or RuntimeError("text_to_schema failed")


def make_clients(needed: set[str]) -> dict[str, Any]:
    clients: dict[str, Any] = {}
    if "openai" in needed:
        from openai import OpenAI

        clients["openai"] = OpenAI(api_key=load_openai_key())
    if "anthropic" in needed:
        try:
            import anthropic
        except ImportError as e:
            raise SystemExit(
                "Optional dependency missing: anthropic. Install with "
                "`pip install anthropic openai` for live Direct API runs."
            ) from e
        clients["anthropic"] = anthropic.Anthropic(api_key=load_anthropic_key())
    return clients


def rebuild_index(out_dir: Path) -> int:
    rows: list[dict] = []
    for p in sorted(out_dir.glob("[0-9][0-9][0-9][0-9].json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not prediction_is_valid(data):
            continue
        rows.append(
            {
                "text_number": int(data.get("text_number") or int(p.stem)),
                "id": data.get("id"),
                "file": p.stem,
            }
        )
    atomic_write_text(
        out_dir / "index.jsonl",
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + ("\n" if rows else ""),
    )
    return len(rows)


def run_one(
    *,
    dataset: str,
    llm_name: str,
    records: list[dict],
    clients: dict[str, Any],
    system_prompt: str,
    skip_existing: bool,
    sleep_s: float,
    temperature: float,
    max_tokens: int,
    max_retries: int,
    backoff_s: float,
) -> dict[str, Any]:
    meta = CLOSED_MODELS[llm_name]
    ds = DATASETS[dataset]
    out_dir = PRED_ROOT / meta[ds["dir_key"]]
    out_dir.mkdir(parents=True, exist_ok=True)
    provider = meta["provider"]
    model_id = meta["model_id"]
    client = clients[provider]

    def call_fn(system: str, user: str) -> str:
        if provider == "openai":
            return call_openai(
                client, model_id, system, user, temperature=temperature, max_tokens=max_tokens
            )
        return call_anthropic(client, model_id, system, user, max_tokens=max_tokens)

    stats = {"ok": 0, "err": 0, "skipped": 0, "empty_q": 0, "failed_ids": []}
    print(
        f"\n[{dataset}/{llm_name}] model_id={model_id} provider={provider} "
        f"temp={temperature} max_tokens={max_tokens} -> {out_dir} (n={len(records)})",
        flush=True,
    )

    for i, rec in enumerate(records, 1):
        rid = rec.get("id") or f"row_{i}"
        text_number = int(rec.get("_text_number") or i)
        if skip_existing and record_done(out_dir, text_number):
            stats["skipped"] += 1
            continue
        nl_text = (rec.get("question") or "").strip()
        if not nl_text:
            stats["empty_q"] += 1
            continue
        database = database_name(rec, ds["prefix"])
        t0 = time.time()
        try:
            result = text_to_schema(
                call_fn,
                system_prompt,
                nl_text,
                database,
                max_retries=max_retries,
                backoff_s=backoff_s,
            )
            save_record(out_dir, llm_name, model_id, rid, text_number, nl_text, database, result)
            stats["ok"] += 1
            print(
                f"  [{llm_name}] [{i}/{len(records)}] {serial_stem(text_number)} "
                f"OK ({time.time()-t0:.1f}s)",
                flush=True,
            )
        except Exception as e:
            save_record(
                out_dir, llm_name, model_id, rid, text_number, nl_text, database, None, str(e)
            )
            stats["err"] += 1
            stats["failed_ids"].append(rid)
            print(
                f"  [{llm_name}] [{i}/{len(records)}] {serial_stem(text_number)} "
                f"ERROR id={rid}: {_redact_secrets(str(e))}",
                file=sys.stderr,
                flush=True,
            )
        if sleep_s > 0:
            time.sleep(sleep_s)

    n_index = rebuild_index(out_dir)
    print(
        f"[{dataset}/{llm_name}] done: ok={stats['ok']} err={stats['err']} "
        f"skipped={stats['skipped']} empty_q={stats['empty_q']} index={n_index}",
        flush=True,
    )
    if stats["failed_ids"]:
        print(f"[{dataset}/{llm_name}] failed_ids={stats['failed_ids']}", file=sys.stderr, flush=True)
    return stats


def main() -> int:
    ap = argparse.ArgumentParser(
        description="E0 Direct gold-NL Text2Schema via Claude Sonnet 4.6 / GPT-5.4-mini"
    )
    ap.add_argument("--dataset", action="append", choices=list(DATASETS), dest="datasets")
    ap.add_argument("--llm", action="append", choices=list(CLOSED_MODELS), dest="llms")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true", help="No API requests")
    ap.add_argument(
        "--confirm-paid",
        action="store_true",
        help="Required opt-in for live paid API calls",
    )
    ap.add_argument("--no-skip-existing", action="store_true")
    ap.add_argument("--sleep", type=float, default=DEFAULT_SLEEP)
    ap.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE)
    ap.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    ap.add_argument("--max-retries", type=int, default=DEFAULT_RETRIES)
    ap.add_argument("--backoff", type=float, default=DEFAULT_BACKOFF)
    ap.add_argument("--prompt", type=Path, default=PROMPT_PATH)
    args = ap.parse_args()

    datasets = args.datasets or list(DATASETS)
    llms = args.llms or list(CLOSED_MODELS)
    skip_existing = not args.no_skip_existing
    system_prompt = load_constructor_prompt(args.prompt)

    print("=" * 72)
    print("E0 Direct Text2Schema (closed API)")
    print(f"  Prompt    : {args.prompt}")
    print(f"  Pred root : {PRED_ROOT}")
    print(f"  Datasets  : {datasets}")
    print(f"  Models    : {llms}")
    print(f"  Decoding  : temperature={args.temperature} max_tokens={args.max_tokens}")
    print("=" * 72)

    if args.dry_run:
        for ds in datasets:
            ann = DATASETS[ds]["annotation"]
            n = sum(1 for line in ann.open() if line.strip()) if ann.is_file() else 0
            lim = min(n, args.limit) if args.limit else n
            print(f"  {ds}: {ann} ({n} records; would process {lim})")
            for llm in llms:
                out = PRED_ROOT / CLOSED_MODELS[llm][DATASETS[ds]["dir_key"]]
                print(f"    -> {out}")
        print("Dry-run complete (no API calls).")
        return 0

    if not args.confirm_paid:
        print(
            "Refusing paid inference without --confirm-paid.\n"
            "Use --dry-run to inspect paths, or pass --confirm-paid to opt in.",
            file=sys.stderr,
        )
        return 2

    needed = {CLOSED_MODELS[m]["provider"] for m in llms}
    clients = make_clients(needed)

    all_stats: list[dict] = []
    t0 = time.time()
    for ds in datasets:
        ann = DATASETS[ds]["annotation"]
        if not ann.is_file():
            print(f"Error: missing annotation {ann}", file=sys.stderr)
            return 1
        records = load_jsonl(ann)
        if args.limit and args.limit > 0:
            records = records[: args.limit]
        for llm in llms:
            stats = run_one(
                dataset=ds,
                llm_name=llm,
                records=records,
                clients=clients,
                system_prompt=system_prompt,
                skip_existing=skip_existing,
                sleep_s=args.sleep,
                temperature=args.temperature,
                max_tokens=args.max_tokens,
                max_retries=args.max_retries,
                backoff_s=args.backoff,
            )
            all_stats.append({"dataset": ds, "llm": llm, **stats})

    summary = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "prompt": str(args.prompt),
        "datasets": datasets,
        "llms": {
            m: {
                "model_id": CLOSED_MODELS[m]["model_id"],
                "provider": CLOSED_MODELS[m]["provider"],
            }
            for m in llms
        },
        "decoding": {
            "temperature": args.temperature,
            "max_tokens": args.max_tokens,
            "max_retries": args.max_retries,
            "backoff": args.backoff,
            "sleep": args.sleep,
        },
        "stats": [
            {k: v for k, v in s.items() if k != "failed_ids"}
            | {"n_failed_ids": len(s.get("failed_ids") or [])}
            for s in all_stats
        ],
        "elapsed_s": round(time.time() - t0, 1),
        "pred_root": str(PRED_ROOT),
    }
    log_dir = ROOT / "audit" / "e0_gold_requirement_verification"
    log_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_path = log_dir / f"E0_DIRECT_API_RUN_{stamp}.json"
    # Local summary only — never commit.
    atomic_write_text(summary_path, json.dumps(summary, indent=2) + "\n")
    print(f"\nFinished in {summary['elapsed_s']}s. Local summary: {summary_path}")
    any_err = any(s.get("err", 0) > 0 for s in all_stats)
    return 2 if any_err else 0


if __name__ == "__main__":
    raise SystemExit(main())
