#!/usr/bin/env python3
"""
RSchema Exp4 Text2Schema via API models (same prompt as rschema_exp4_text2schema_allLLM.py).

Reads NL questions from RSchema/annotation.jsonl and writes:
    <DATA_ROOT>/RSchema_ExpResults4/Experiments/text2schema_<llm>/NNNN.txt
    <DATA_ROOT>/RSchema_ExpResults4/Experiments/text2schema_<llm>/NNNN.json

Examples:
    python rschema_exp4_text2schema_api.py --dry-run
    python rschema_exp4_text2schema_api.py --llm sonnet46 --limit 2
    python rschema_exp4_text2schema_api.py --all-llms
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from tqdm import tqdm

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_ROOT = Path("/data") if Path("/data").is_dir() else SCRIPT_DIR.parent.parent
TEXT2ER_ROOT = DATA_ROOT / "Text2ER"
RSCHEMA_DIR = DATA_ROOT / "RSchema"
BASE_OUT = DATA_ROOT / "RSchema_ExpResults4" / "Experiments"
ANNOTATION_PATH = RSCHEMA_DIR / "annotation.jsonl"
MAX_TOKENS = 4096

sys.path.insert(0, str(SCRIPT_DIR))
import rschema_exp4_text2schema_allLLM as t2s  # noqa: E402

SYSTEM_PROMPT = t2s.SYSTEM_PROMPT

LLM_CONFIG: dict[str, dict[str, str]] = {
    "sonnet46": {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-6",
    },
    "gpt54mini": {
        "provider": "openai",
        "model_id": "gpt-5.4-mini",
    },
}

ANTHROPIC_KEY_CANDIDATES = [
    DATA_ROOT / "anthropic_api.txt",
    TEXT2ER_ROOT / "anthropic_api.txt",
    Path("/data/anthropic_api.txt"),
]
OPENAI_KEY_CANDIDATES = [
    DATA_ROOT / "openai_api.txt",
    TEXT2ER_ROOT / "openai_api.txt",
    Path("/data/openai_api.txt"),
]


def load_api_key(provider: str) -> str:
    import os

    if provider == "anthropic":
        env = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        candidates = ANTHROPIC_KEY_CANDIDATES
    else:
        env = os.environ.get("OPENAI_API_KEY", "").strip()
        candidates = OPENAI_KEY_CANDIDATES
    if env:
        return env
    for path in candidates:
        if path.is_file():
            key = path.read_text(encoding="utf-8").strip()
            if key:
                return key
    print(f"Error: {provider} API key not found.", file=sys.stderr)
    sys.exit(1)


def record_already_done(out_dir: Path, text_number: int) -> bool:
    _, out_json = t2s.output_paths(out_dir, text_number)
    if not out_json.is_file():
        return False
    try:
        data = json.loads(out_json.read_text(encoding="utf-8"))
    except Exception:
        return False
    return bool((data.get("ddl") or "").strip()) and not data.get("error")


def call_anthropic(client, model_id: str, user_content: str, max_tokens: int = MAX_TOKENS) -> str:
    response = client.messages.create(
        model=model_id,
        max_tokens=max_tokens,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
        temperature=0.1,
    )
    parts = []
    for block in response.content:
        if getattr(block, "type", None) == "text":
            parts.append(block.text)
    text = "".join(parts).strip()
    if not text:
        raise ValueError("Empty Anthropic response")
    return text


def call_openai(client, model_id: str, user_content: str, max_tokens: int = MAX_TOKENS) -> str:
    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.1,
        max_completion_tokens=max_tokens,
    )
    raw = (response.choices[0].message.content or "").strip()
    if not raw:
        raise ValueError("Empty OpenAI response")
    return raw


def parse_schema_response(raw: str, database: str) -> dict:
    out = t2s.extract_json_from_response(raw)
    if not isinstance(out, dict) or "ddl" not in out:
        raise ValueError("Model response missing 'ddl'")
    if "metadata" not in out:
        out["metadata"] = {"database": database, "tables": [], "columns_by_table": {}}
    return t2s._sanitize_schema_result(out, database)


def text_to_schema_api(
    provider: str,
    client,
    model_id: str,
    nl_text: str,
    database: str,
    max_retries: int = 3,
) -> dict:
    user_content = t2s._build_user_content(nl_text, database)
    last_err: Exception | None = None
    last_raw: str | None = None
    for attempt in range(max_retries):
        try:
            if provider == "anthropic":
                raw = call_anthropic(client, model_id, user_content)
            else:
                raw = call_openai(client, model_id, user_content)
            last_raw = raw
            return parse_schema_response(raw, database)
        except (json.JSONDecodeError, ValueError) as e:
            last_err = e
            fb = last_raw and (
                t2s._extract_ddl_from_broken_response(last_raw)
                or t2s._ddl_only_fallback(last_raw, database)
            )
            if fb and attempt + 1 == max_retries:
                return t2s._sanitize_schema_result(fb, database)
            if attempt + 1 == max_retries:
                raise last_err
        except Exception as e:
            last_err = e
            err = str(e).lower()
            if any(k in err for k in ("rate", "429", "overloaded", "timeout")) and attempt + 1 < max_retries:
                time.sleep(min(60, 2 ** (attempt + 1)))
                continue
            if attempt + 1 == max_retries:
                raise last_err
            time.sleep(1.0)
    raise last_err or ValueError("text_to_schema_api failed")


def run_llm(
    llm_name: str,
    records: list[dict],
    base_out: Path,
    skip_existing: bool,
    limit: int | None,
    sleep_s: float,
    dry_run: bool = False,
) -> dict:
    cfg = LLM_CONFIG[llm_name]
    provider = cfg["provider"]
    model_id = cfg["model_id"]
    out_dir = base_out / f"text2schema_{llm_name}"
    out_dir.mkdir(parents=True, exist_ok=True)

    if limit and limit > 0:
        records = records[:limit]

    if dry_run:
        return {
            "llm": llm_name,
            "model_id": model_id,
            "provider": provider,
            "records": len(records),
            "out_dir": str(out_dir),
        }

    if provider == "anthropic":
        import anthropic

        client = anthropic.Anthropic(api_key=load_api_key("anthropic"))
    else:
        from openai import OpenAI

        client = OpenAI(api_key=load_api_key("openai"))

    ok = err_count = skipped = 0
    pbar = tqdm(records, desc=f"[{llm_name}]", unit="rec", dynamic_ncols=True, file=sys.stderr)

    for i, rec in enumerate(pbar, 1):
        text_number = int(rec.get("_text_number") or i)
        if skip_existing and record_already_done(out_dir, text_number):
            skipped += 1
            pbar.set_postfix(ok=ok, err=err_count, skip=skipped, refresh=False)
            continue

        nl_text = (rec.get("question") or "").strip()
        rid = rec.get("id") or f"row_{i}"
        if not nl_text:
            skipped += 1
            continue

        database = t2s._database_name(rec)
        try:
            result = text_to_schema_api(provider, client, model_id, nl_text, database)
            t2s._save_record_result(
                out_dir, llm_name, model_id, rid, text_number, nl_text, database, result
            )
            ok += 1
            pbar.set_postfix(ok=ok, err=err_count, skip=skipped, refresh=True)
        except Exception as e:
            err_count += 1
            t2s._save_record_result(
                out_dir, llm_name, model_id, rid, text_number, nl_text, database, None, str(e)
            )
            pbar.set_postfix(ok=ok, err=err_count, skip=skipped, refresh=True)

        if sleep_s > 0:
            time.sleep(sleep_s)

    return {
        "llm": llm_name,
        "model_id": model_id,
        "provider": provider,
        "ok": ok,
        "err": err_count,
        "skipped": skipped,
        "out_dir": str(out_dir),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="RSchema Exp4 text2schema via API")
    parser.add_argument("--llm", choices=list(LLM_CONFIG.keys()), help="Single LLM key")
    parser.add_argument("--all-llms", action="store_true", help="Run all configured API LLMs")
    parser.add_argument("--input", type=Path, default=ANNOTATION_PATH)
    parser.add_argument("--output-dir", type=Path, default=BASE_OUT)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-skip-existing", action="store_true")
    parser.add_argument("--sleep", type=float, default=0.05, help="Seconds between API calls")
    args = parser.parse_args()

    if not args.input.is_file():
        print("Error: input not found:", args.input, file=sys.stderr)
        sys.exit(1)

    llms = list(LLM_CONFIG.keys()) if args.all_llms or not args.llm else [args.llm]
    records = t2s.load_jsonl(args.input)
    skip_existing = not args.no_skip_existing

    print("RSchema Exp4 text2schema (API, same prompt as HF allLLM)")
    print(f"  Input : {args.input}")
    print(f"  Output: {args.output_dir}/text2schema_<llm>/")
    print(f"  LLMs  : {llms}")
    print(f"  Records: {len(records)}")

    if args.dry_run:
        for name in llms:
            stats = run_llm(name, records, args.output_dir, skip_existing, args.limit, args.sleep, dry_run=True)
            print(f"  {stats['llm']}: {stats['records']} records -> {stats['out_dir']} ({stats['model_id']})")
        return

    args.output_dir.mkdir(parents=True, exist_ok=True)
    all_stats: list[dict] = []
    t0 = time.time()
    for name in llms:
        print(f"\n=== {name} ({LLM_CONFIG[name]['model_id']}) ===", flush=True)
        stats = run_llm(name, records, args.output_dir, skip_existing, args.limit, args.sleep)
        all_stats.append(stats)
        print(
            f"[{name}] done: ok={stats['ok']} err={stats['err']} skipped={stats['skipped']}",
            flush=True,
        )

    log_dir = DATA_ROOT / "RSchema_ExpResults4" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    summary_path = log_dir / f"exp4_text2schema_api_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    summary = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "elapsed_s": round(time.time() - t0, 1),
        "prompt": "rschema_exp4_text2schema_allLLM SYSTEM_PROMPT",
        "output_dir": str(args.output_dir),
        "llms": all_stats,
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nSummary: {summary_path}")


if __name__ == "__main__":
    main()
