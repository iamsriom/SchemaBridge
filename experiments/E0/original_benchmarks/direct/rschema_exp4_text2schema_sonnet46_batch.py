#!/usr/bin/env python3
"""
RSchema Exp4: Experiment2 schema2text_gpt54mini NL -> schema via Claude Sonnet 4.6
(Anthropic Batch API, ~50% lower cost).

Same SYSTEM_PROMPT as rschema_exp4_text2schema_gpt4omini.py (lines 46-67).

Input:
    RSchema_ExpResults4/Experiment2/schema2text_gpt54mini/NNNN.json

Output:
    RSchema_ExpResults4/Exp4/text2schema_sonnet46/NNNN.txt
    RSchema_ExpResults4/Exp4/text2schema_sonnet46/NNNN.json

Examples:
    python rschema_exp4_text2schema_sonnet46_batch.py --dry-run
    python rschema_exp4_text2schema_sonnet46_batch.py --limit 3
    python rschema_exp4_text2schema_sonnet46_batch.py --submit-only
    python rschema_exp4_text2schema_sonnet46_batch.py --resume
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_ROOT = Path("/data") if Path("/data").is_dir() else SCRIPT_DIR.parent.parent
SCHEMABENCH_CODE = DATA_ROOT / "SchemaBench" / "Code"
TEXT2ER_EXP = DATA_ROOT / "Text2ER" / "experiments"
for p in (SCRIPT_DIR, SCHEMABENCH_CODE, TEXT2ER_EXP):
    if p.is_dir():
        sys.path.insert(0, str(p))

import rschema_exp4_text2schema_allLLM as t2s  # noqa: E402
import rschema_exp4_text2schema_gpt4omini as gpt4o  # noqa: E402

INPUT_DIR = DATA_ROOT / "RSchema_ExpResults4" / "Experiment2" / "schema2text_gpt54mini"
OUTPUT_BASE = DATA_ROOT / "RSchema_ExpResults4" / "Exp4"
SOURCE_SCHEMA2TEXT_LLM = "gpt54mini"
PREFIX_OUT = "text2schema_"
LOG_DIR = DATA_ROOT / "RSchema_ExpResults4" / "logs"

LLM_NAME = "sonnet46"
MODEL_ID = "claude-sonnet-4-6"
MAX_TOKENS = 16384
TEMPERATURE = 0.2
POLL_INTERVAL_S = 30
BATCH_CHUNK_SIZE = 100
STATE_FILENAME = "batch_state.json"

SYSTEM_PROMPT = gpt4o.SYSTEM_PROMPT

ANTHROPIC_KEY_CANDIDATES = [
    DATA_ROOT / "anthropic_api.txt",
    DATA_ROOT / "Text2ER" / "anthropic_api.txt",
    Path("/data/anthropic_api.txt"),
]


def load_api_key() -> str:
    env = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if env:
        return env
    for path in ANTHROPIC_KEY_CANDIDATES:
        if path.is_file():
            key = path.read_text(encoding="utf-8").strip()
            if key:
                return key
    print("Error: Anthropic API key not found. Set ANTHROPIC_API_KEY or anthropic_api.txt", file=sys.stderr)
    sys.exit(1)


def record_id(rec: dict) -> str:
    return gpt4o.serial_stem(rec["text_number"])


def out_dir_for(base: Path) -> Path:
    d = base / f"{PREFIX_OUT}{LLM_NAME}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def state_path(out_dir: Path) -> Path:
    return out_dir / STATE_FILENAME


def load_state(out_dir: Path) -> dict:
    p = state_path(out_dir)
    if not p.is_file():
        return {"batches": []}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {"batches": []}


def save_state(out_dir: Path, state: dict) -> None:
    state_path(out_dir).write_text(json.dumps(state, indent=2), encoding="utf-8")


def list_inputs(input_dir: Path, limit: int | None = None) -> list[Path]:
    paths = sorted(input_dir.glob("[0-9][0-9][0-9][0-9].json"))
    if limit is not None and limit > 0:
        paths = paths[:limit]
    return paths


def pending_records(
    out_dir: Path,
    json_paths: list[Path],
    skip_existing: bool,
) -> list[tuple[Path, dict]]:
    pending: list[tuple[Path, dict]] = []
    for json_path in json_paths:
        rec = gpt4o.load_input_record(json_path)
        if not rec:
            continue
        if skip_existing and gpt4o.record_done(out_dir, rec["text_number"]):
            continue
        pending.append((json_path, rec))
    return pending


def save_batch_result(
    out_dir: Path,
    rec: dict,
    result: dict | None,
    error: str | None = None,
) -> None:
    gpt4o.save_result(out_dir, SOURCE_SCHEMA2TEXT_LLM, rec, result, error=error)
    out_json = gpt4o.output_paths(out_dir, rec["text_number"])[1]
    if out_json.is_file():
        data = json.loads(out_json.read_text(encoding="utf-8"))
        data["llm"] = LLM_NAME
        data["model_id"] = MODEL_ID
        out_json.write_text(json.dumps(data, indent=2, default=str, ensure_ascii=False), encoding="utf-8")


def parse_schema_response(raw: str, database: str) -> dict:
    out = t2s.extract_json_from_response(raw)
    if not isinstance(out, dict) or "ddl" not in out:
        raise ValueError("Model response missing 'ddl'")
    if "metadata" not in out:
        out["metadata"] = {"database": database, "tables": [], "columns_by_table": {}}
    return t2s._sanitize_schema_result(out, database)


def build_batch_request(rec: dict) -> dict:
    user_content = t2s._build_user_content(rec["nl_text"], rec["database"])
    return {
        "custom_id": record_id(rec),
        "params": {
            "model": MODEL_ID,
            "max_tokens": MAX_TOKENS,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": user_content}],
            "temperature": TEMPERATURE,
        },
    }


def submit_batches(client, pending: list[tuple[Path, dict]], chunk_size: int) -> list[dict]:
    submitted: list[dict] = []
    for start in range(0, len(pending), chunk_size):
        chunk = pending[start : start + chunk_size]
        requests = [build_batch_request(rec) for _, rec in chunk]
        print(f"Submitting batch chunk {start // chunk_size + 1}: {len(requests)} requests...", flush=True)
        batch = client.messages.batches.create(requests=requests)
        rid = record_id
        entry = {
            "batch_id": batch.id,
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "processing_status": batch.processing_status,
            "request_count": len(requests),
            "custom_ids": [rid(rec) for _, rec in chunk],
            "records": {
                rid(rec): {
                    "input_json": str(json_path),
                    "database": rec["database"],
                    "text_number": rec["text_number"],
                    "id": rec.get("id"),
                }
                for json_path, rec in chunk
            },
        }
        submitted.append(entry)
        print(f"  batch_id={batch.id} status={batch.processing_status}", flush=True)
    return submitted


def poll_batch(client, batch_id: str, poll_interval: float) -> object:
    while True:
        batch = client.messages.batches.retrieve(batch_id)
        counts = batch.request_counts
        print(
            f"  [{batch_id}] status={batch.processing_status} "
            f"processing={counts.processing} succeeded={counts.succeeded} "
            f"errored={counts.errored} canceled={counts.canceled} expired={counts.expired}",
            flush=True,
        )
        if batch.processing_status == "ended":
            return batch
        time.sleep(poll_interval)


def extract_text_from_result(result) -> str:
    if result.type != "succeeded":
        raise ValueError(f"Batch item not succeeded: {result.type}")
    message = result.message
    parts: list[str] = []
    for block in message.content:
        if getattr(block, "type", None) == "text":
            parts.append(block.text)
    text = "".join(parts).strip()
    if not text:
        raise ValueError("Empty model response")
    return text


def collect_batch_results(client, batch_entry: dict, out_dir: Path) -> dict:
    batch_id = batch_entry["batch_id"]
    ok = err = 0
    print(f"Collecting results for {batch_id}...", flush=True)

    for line in client.messages.batches.results(batch_id):
        custom_id = line.custom_id
        meta = batch_entry.get("records", {}).get(custom_id, {})
        rec = {
            "text_number": meta.get("text_number") or int(custom_id),
            "database": meta.get("database") or f"rschema_{custom_id}",
            "nl_text": "",
            "id": meta.get("id"),
            "input_json": meta.get("input_json"),
        }
        input_json = meta.get("input_json")
        if input_json:
            loaded = gpt4o.load_input_record(Path(input_json))
            if loaded:
                rec = loaded

        result = line.result
        try:
            if result.type == "succeeded":
                raw = extract_text_from_result(result)
                parsed = parse_schema_response(raw, rec["database"])
                save_batch_result(out_dir, rec, parsed)
                ok += 1
                print(f"  {custom_id} OK", flush=True)
            elif result.type == "errored":
                err_obj = result.error
                msg = getattr(err_obj, "message", str(err_obj))
                save_batch_result(out_dir, rec, None, error=msg)
                err += 1
                print(f"  {custom_id} ERROR: {msg}", flush=True)
            else:
                save_batch_result(out_dir, rec, None, error=f"batch result type: {result.type}")
                err += 1
                print(f"  {custom_id} {result.type}", flush=True)
        except Exception as e:
            fb = None
            try:
                if result.type == "succeeded":
                    raw = extract_text_from_result(result)
                    fb = t2s._extract_ddl_from_broken_response(raw) or t2s._ddl_only_fallback(
                        raw, rec["database"]
                    )
            except Exception:
                pass
            if fb:
                save_batch_result(out_dir, rec, fb)
                ok += 1
                print(f"  {custom_id} OK (fallback)", flush=True)
            else:
                save_batch_result(out_dir, rec, None, error=str(e))
                err += 1
                print(f"  {custom_id} ERROR: {e}", flush=True)

    return {"batch_id": batch_id, "ok": ok, "err": err}


def merge_state(out_dir: Path, new_batches: list[dict]) -> None:
    state = load_state(out_dir)
    existing_ids = {b["batch_id"] for b in state.get("batches", [])}
    for b in new_batches:
        if b["batch_id"] not in existing_ids:
            state.setdefault("batches", []).append(b)
    save_state(out_dir, state)


def run_resume(client, out_dir: Path, poll_interval: float) -> None:
    state = load_state(out_dir)
    batches = state.get("batches", [])
    if not batches:
        print("No batches in state file.", file=sys.stderr)
        sys.exit(1)

    for entry in batches:
        batch_id = entry["batch_id"]
        if entry.get("processing_status") == "collected":
            print(f"Skip already collected batch {batch_id}", flush=True)
            continue
        batch = poll_batch(client, batch_id, poll_interval)
        entry["processing_status"] = batch.processing_status
        if batch.processing_status == "ended":
            stats = collect_batch_results(client, entry, out_dir)
            entry["processing_status"] = "collected"
            entry["stats"] = stats
        save_state(out_dir, state)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="RSchema Exp4 text2schema via Claude Sonnet 4.6 (Anthropic Batch API)"
    )
    parser.add_argument("--input-dir", type=Path, default=INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_BASE)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-skip-existing", action="store_true")
    parser.add_argument("--submit-only", action="store_true")
    parser.add_argument("--collect-only", type=str, default=None, metavar="BATCH_ID")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--poll-interval", type=float, default=POLL_INTERVAL_S)
    parser.add_argument("--chunk-size", type=int, default=BATCH_CHUNK_SIZE)
    args = parser.parse_args()

    out_dir = out_dir_for(args.output_dir)
    skip_existing = not args.no_skip_existing
    json_paths = list_inputs(args.input_dir, args.limit)
    pending = pending_records(out_dir, json_paths, skip_existing)

    print("=" * 72)
    print("RSchema Exp4 Text2Schema — Sonnet 4.6 (Anthropic Batch API)")
    print(f"  Input     : {args.input_dir} ({len(json_paths)} records)")
    print(f"  Output    : {out_dir}")
    print(f"  Source NL : {SOURCE_SCHEMA2TEXT_LLM}")
    print(f"  Model     : {MODEL_ID}")
    print(f"  Pending   : {len(pending)} / {len(json_paths)} schemas")
    print(f"  State     : {state_path(out_dir)}")
    print("=" * 72)

    if args.dry_run:
        for _, rec in pending[:5]:
            print(f"  would submit: {record_id(rec)} nl_len={len(rec['nl_text'])}")
        if len(pending) > 5:
            print(f"  ... and {len(pending) - 5} more")
        return

    if not pending and not args.collect_only and not args.resume:
        print("Nothing to do (all schemas already done).", flush=True)
        return

    import anthropic

    client = anthropic.Anthropic(api_key=load_api_key())
    t0 = time.time()

    if args.collect_only:
        entry = {"batch_id": args.collect_only, "records": {}}
        state = load_state(out_dir)
        for b in state.get("batches", []):
            if b.get("batch_id") == args.collect_only:
                entry = b
                break
        stats = collect_batch_results(client, entry, out_dir)
        for b in state.get("batches", []):
            if b.get("batch_id") == args.collect_only:
                b["processing_status"] = "collected"
                b["stats"] = stats
        save_state(out_dir, state)
        print(f"Collected: ok={stats['ok']} err={stats['err']}")
        return

    if args.resume:
        run_resume(client, out_dir, args.poll_interval)
        print(f"\nFinished in {time.time() - t0:.1f}s")
        return

    if pending:
        new_batches = submit_batches(client, pending, args.chunk_size)
        merge_state(out_dir, new_batches)
        if args.submit_only:
            print(f"\nSubmitted {len(new_batches)} batch(es). Run with --resume to poll and collect.")
            return

        state = load_state(out_dir)
        for entry in new_batches:
            poll_batch(client, entry["batch_id"], args.poll_interval)
            stats = collect_batch_results(client, entry, out_dir)
            entry["processing_status"] = "collected"
            entry["stats"] = stats
            for b in state.get("batches", []):
                if b.get("batch_id") == entry["batch_id"]:
                    b.update(entry)
        save_state(out_dir, state)

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    summary = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "llm": LLM_NAME,
        "model_id": MODEL_ID,
        "api": "anthropic_message_batches",
        "input_dir": str(args.input_dir),
        "output_dir": str(out_dir),
        "elapsed_s": round(time.time() - t0, 1),
        "state_file": str(state_path(out_dir)),
    }
    summary_path = LOG_DIR / f"text2schema_exp4_sonnet46_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nFinished in {summary['elapsed_s']}s. Summary: {summary_path}", flush=True)


if __name__ == "__main__":
    main()
