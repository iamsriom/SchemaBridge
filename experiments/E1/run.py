#!/usr/bin/env python3
"""E1 Schema2Text generation (Table VII inputs).  DRY-RUN BY DEFAULT.

    python experiments/E1/run.py --dataset rschema --model llama31 --prompt detailed            # dry-run
    python experiments/E1/run.py --dataset rschema --model llama31 --prompt detailed --execute  # local GPU
    python experiments/E1/run.py --dataset schemabench --model sonnet46 --prompt basic \\
        --execute --confirm-paid                                                                # PAID API

Nothing is generated, downloaded or sent unless ``--execute`` is given; paid providers
(``sonnet46`` -> Anthropic, ``gpt54mini`` -> OpenAI) additionally need ``--confirm-paid`` and an
API key in ``ANTHROPIC_API_KEY`` / ``OPENAI_API_KEY`` (environment only; keys are never read
from files, printed or stored).

Output per schema (``NNNN`` = serial; for RSchema the 1-based position in the 518-record
``annotation.jsonl``, so serials are NOT contiguous for the 381 DDL-matched schemas):

    NNNN.txt   the description
    NNNN.json  text_number, id, llm, model_id, database, ddl, gold_question, ddl_source,
               prompt_style (schema2text1 | schema2text2), nl_text, [error], generation{...}
"""
from __future__ import annotations

import argparse
import dataclasses
import sys
import time
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import datasets_io as dio  # noqa: E402
from src import inference_clients as ic  # noqa: E402
from src import prompt_assets as pa  # noqa: E402
from src import repro_io as rio  # noqa: E402

DEFAULT_OUT_PARENT = ROOT / "experiments" / "E1" / "outputs"
DTYPES = ("float16", "bfloat16", "float32")
MODEL_CHOICES = tuple(ic.DESCRIBER_KEYS) + ("all",)


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description="E1 Schema2Text generation. Dry-run by default: use --execute to generate "
        "(and --confirm-paid for sonnet46 / gpt54mini).",
    )
    ap.add_argument("--dataset", choices=rio.DATASET_CHOICES, required=True)
    ap.add_argument("--model", choices=MODEL_CHOICES, required=True)
    ap.add_argument("--prompt", choices=rio.PROMPT_VARIANTS, required=True,
                    help="basic -> schema2text1, detailed -> schema2text2")
    ap.add_argument("--data-root", default=None,
                    help=f"dataset root (overrides ${dio.DATA_ROOT_ENV}; packaged datasets/ is the fallback)")
    ap.add_argument("--out-dir", default=None,
                    help="default experiments/E1/outputs/<dataset>_<prompt>_<model>/ ; with several "
                         "dataset/model combinations (--dataset all / --model all) this is a PARENT "
                         "directory that receives one <dataset>_<prompt>_<model>/ folder per combination")
    ap.add_argument("--limit", type=int, default=None, help="only the first N schemas of each dataset")
    ap.add_argument("--skip-existing", dest="skip_existing", action=argparse.BooleanOptionalAction,
                    default=True, help="skip schemas whose NNNN.json already has nl_text and no error (default: on)")
    ap.add_argument("--resume", dest="skip_existing", action="store_const", const=True,
                    help="alias for --skip-existing")
    ap.add_argument("--device", default="auto",
                    help="HF device_map: auto (default), cpu, cuda, cuda:0, ... (open models only)")
    ap.add_argument("--dtype", choices=DTYPES, default="float16", help="HF torch dtype (default float16)")
    ap.add_argument("--load-in-4bit", action="store_true", help="HF only; needs bitsandbytes (CUDA)")
    ap.add_argument("--max-tokens", type=int, default=None,
                    help="override max new tokens (default: 3072 open models; 1024 basic / 2048 detailed for APIs)")
    ap.add_argument("--max-retries", type=int, default=5,
                    help="extra attempts with exponential backoff on rate limits / transient errors (default 5)")
    ap.add_argument("--retry-base-delay", type=float, default=2.0, help="initial backoff in seconds (default 2)")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="default behaviour: no generation, no network")
    mode.add_argument("--execute", action="store_true", help="actually generate (required)")
    ap.add_argument("--confirm-paid", action="store_true",
                    help="required with --execute for paid providers (sonnet46, gpt54mini)")
    ap.add_argument("--write-plan", action="store_true",
                    help="dry-run only: write dry_run_plan.json (counts, hashes, sizes; no text) under --out-dir")
    return ap


# --------------------------------------------------------------------------- records


def build_record(rec: dio.GoldRecord, model_key: str, prompt: str, req: ic.Request, *,
                 nl_text: str = "", error: str | None = None) -> dict:
    """One historical-format E1 JSON record."""
    spec = ic.MODELS[model_key]
    out = {
        "text_number": int(rec.serial),
        "id": rec.schema_id,
        "llm": model_key,
        "model_id": spec.model_id,
        "database": rec.database,
        "ddl": rec.ddl,
        "gold_question": rec.gold_nl,
        "ddl_source": rec.ddl_source,
        "prompt_style": rio.PROMPT_STYLE[prompt],
        "nl_text": nl_text,
    }
    if error:
        out["error"] = error
    out["generation"] = {
        "prompt_variant": prompt,
        "prompt_sha256": pa.EXPECTED_SHA256[prompt],
        "temperature": req.temperature,
        "max_tokens": req.max_tokens,
    }
    return out


def _requests(records: Sequence[dio.GoldRecord], model_key: str, prompt: str, max_tokens: int | None):
    for rec in records:
        req = ic.build_request(model_key, task="schema2text", database=rec.database, ddl=rec.ddl, variant=prompt)
        if max_tokens:
            req = dataclasses.replace(req, max_tokens=max_tokens)
        yield rec, req


# --------------------------------------------------------------------------- dry run


def dry_run_one(dataset: str, model_key: str, prompt: str, args, out_dir: Path) -> dict:
    spec = ic.MODELS[model_key]
    all_recs = dio.load_dataset(dataset, args.data_root)
    recs = all_recs[: args.limit] if args.limit else all_recs
    sizes, total_chars, n_trunc = [], 0, 0
    for i, (rec, req) in enumerate(_requests(recs, model_key, prompt, args.max_tokens)):
        total_chars += req.approx_input_chars()
        if "[DDL truncated for length]" in req.user:
            n_trunc += 1
        if i < 3:
            sizes.append({"serial": rec.serial, "id": rec.schema_id, "system_chars": len(req.system),
                          "user_chars": len(req.user), "max_tokens": req.max_tokens,
                          "temperature": req.temperature})
    n_done = sum(rio.is_complete_nl_record(out_dir / f"{r.serial}.json", r.schema_id) for r in recs) \
        if out_dir.is_dir() else 0
    plan = {
        "experiment": "E1", "dataset": dataset, "prompt": prompt, "prompt_style": rio.PROMPT_STYLE[prompt],
        "model": model_key, "model_id": spec.model_id, "provider": spec.provider, "paid": spec.paid,
        "n_expected": dio.EXPECTED_COUNTS[dataset], "n_loaded": len(all_recs), "n_selected": len(recs),
        "n_with_gold_nl": sum(1 for r in recs if r.gold_nl), "n_missing_ddl": sum(1 for r in recs if not r.ddl.strip()),
        "serial_range": [recs[0].serial, recs[-1].serial] if recs else None,
        "n_already_complete": n_done, "n_to_generate": len(recs) - (n_done if args.skip_existing else 0),
        "n_ddl_truncated_for_api": n_trunc, "approx_total_input_chars": total_chars,
        "prompt_sha256": {"describer": pa.EXPECTED_SHA256[prompt]},
        "first_requests": sizes, "out_dir": str(out_dir), "dry_run": True,
    }
    print(f"[dry-run] {dataset} / {prompt} ({plan['prompt_style']}) / {model_key} -> {spec.model_id} "
          f"[{spec.provider}{', PAID' if spec.paid else ''}]")
    print(f"  schemas: loaded={plan['n_loaded']} (expected {plan['n_expected']}) selected={plan['n_selected']} "
          f"with_gold_nl={plan['n_with_gold_nl']} missing_ddl={plan['n_missing_ddl']}")
    if recs:
        print(f"  serials: {recs[0].serial} .. {recs[-1].serial}"
              + ("  (RSchema: positions in the 518-record annotation.jsonl)" if dataset == "rschema" else ""))
    print(f"  prompt sha256 ({prompt}): {pa.EXPECTED_SHA256[prompt]}")
    for s in sizes:
        print(f"  request {s['serial']} id={s['id']}: system={s['system_chars']} chars, "
              f"user={s['user_chars']} chars, max_tokens={s['max_tokens']}, T={s['temperature']}")
    print(f"  resume: {n_done} complete in {out_dir}; to generate: {plan['n_to_generate']}"
          f"  | approx total input chars: {total_chars}"
          + (f" | {n_trunc} DDLs truncated (API limit)" if n_trunc else ""))
    if args.write_plan:
        path = out_dir / "dry_run_plan.json"
        rio.write_json(path, plan)
        print(f"  wrote plan -> {path}")
    return plan


# --------------------------------------------------------------------------- execute


def execute_one(dataset: str, model_key: str, prompt: str, args, out_dir: Path, client) -> int:
    spec = ic.MODELS[model_key]
    all_recs = dio.load_dataset(dataset, args.data_root)
    recs = all_recs[: args.limit] if args.limit else all_recs
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[execute] {dataset} / {prompt} / {model_key} -> {spec.model_id}: {len(recs)} schema(s) -> {out_dir}")
    n_gen = n_skip = n_err = 0
    for rec, req in _requests(recs, model_key, prompt, args.max_tokens):
        jpath, tpath = out_dir / f"{rec.serial}.json", out_dir / f"{rec.serial}.txt"
        if args.skip_existing and rio.is_complete_nl_record(jpath, rec.schema_id):
            n_skip += 1
            continue
        t0 = time.time()
        try:
            text = rio.generate_with_backoff(client, req, max_retries=args.max_retries,
                                             base_delay=args.retry_base_delay)
            out = build_record(rec, model_key, prompt, req, nl_text=text)
            if not text.strip():
                out["error"] = "empty_generation"
        except (ic.PaidCallNotConfirmed, ic.MissingApiKey):
            raise
        except Exception as e:  # noqa: BLE001 - recorded, run continues
            out = build_record(rec, model_key, prompt, req, error=f"{type(e).__name__}: {str(e)[:300]}")
        out["generation"]["elapsed_s"] = round(time.time() - t0, 3)
        rio.write_json(jpath, out)
        if out.get("error"):
            n_err += 1
            print(f"  {rec.serial} {rec.schema_id}: ERROR {out['error'][:120]}")
        else:
            tpath.write_text(out["nl_text"], encoding="utf-8")
            n_gen += 1
            if n_gen % 10 == 0:
                print(f"  ... {n_gen} generated")
    print(f"  done: generated={n_gen} skipped_existing={n_skip} errors={n_err}")
    return n_err


# --------------------------------------------------------------------------- main


def main(argv: Sequence[str] | None = None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)
    datasets = rio.expand(args.dataset, rio.DATASETS)
    models = rio.expand(args.model, ic.DESCRIBER_KEYS)
    multi = len(datasets) * len(models) > 1
    paid = [m for m in models if ic.MODELS[m].paid]
    if args.execute and paid and not args.confirm_paid:
        ap.error(f"{', '.join(paid)} use paid APIs: add --confirm-paid together with --execute "
                 "(or choose an open model)")
    if args.write_plan and args.execute:
        ap.error("--write-plan is a dry-run option")
    if args.limit is not None and args.limit < 1:
        ap.error("--limit must be >= 1")

    try:
        pa.verify_all_prompts()
        dirs = {}
        for d in datasets:
            for m in models:
                dirs[(d, m)] = rio.assert_ignored_out_dir(
                    rio.combo_dir(args.out_dir, DEFAULT_OUT_PARENT, rio.combo_name(d, args.prompt, m), multi=multi))
    except (pa.PromptHashError, ValueError, FileNotFoundError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    print(f"prompt hashes verified: " + ", ".join(f"{k}={v[:12]}" for k, v in pa.EXPECTED_SHA256.items()))
    if not args.execute:
        print("DRY-RUN: nothing is generated or sent (use --execute to generate).")
    try:
        if not args.execute:
            for d in datasets:
                for m in models:
                    dry_run_one(d, m, args.prompt, args, dirs[(d, m)])
            return 0
        errors = 0
        clients: dict[str, object] = {}
        for d in datasets:
            for m in models:
                if m not in clients:
                    clients[m] = ic.get_client(m, dry_run=False, confirm_paid=args.confirm_paid,
                                               load_in_4bit=args.load_in_4bit, device_map=args.device,
                                               dtype=args.dtype)
                errors += execute_one(d, m, args.prompt, args, dirs[(d, m)], clients[m])
        return 1 if errors else 0
    except ic.MissingApiKey as e:
        print(f"error: {e} (keys are read from the environment only)", file=sys.stderr)
        return 2
    except (ValueError, FileNotFoundError, KeyError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
