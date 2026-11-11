#!/usr/bin/env python3
"""E3 constructor isolation, step 2: five constructors on fixed GPT-5.4-mini Detailed NL.  DRY-RUN BY DEFAULT.

    python experiments/E3/run.py --dataset rschema --constructor llama31 \\
        --descriptions-dir experiments/E1/outputs/rschema_detailed_gpt54mini

Reads fixed E1 Detailed descriptions (``nl_text`` of ``NNNN.json``) and builds Text2Schema
constructor payloads (``prompts/constructor.txt``, hash-verified).  **Paid Anthropic/OpenAI
API constructors are disabled** in this package: dry-run validates payloads only.
Open-weight HF constructors may use ``--execute``.  Evaluate already-saved reconstructions
with ``experiments/E3/evaluate.py`` (offline).

Every constructor must receive the *same* GPT-5.4-mini Detailed description for a given schema.
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
from src.schema_parser import metadata_from_ddl  # noqa: E402

DEFAULT_DESC_PARENT = ROOT / "experiments" / "E1" / "outputs"
DEFAULT_OUT_PARENT = ROOT / "experiments" / "E3" / "outputs"
FIXED_DESCRIBER = "gpt54mini"
FIXED_PROMPT = "detailed"
CONSTRUCTOR_CHOICES = tuple(ic.E3_CONSTRUCTOR_KEYS) + ("all",)
PLACEHOLDER_NL = "[placeholder description used only to size a dry-run payload]"
DTYPES = ("float16", "bfloat16", "float32")


def e3_combo_name(dataset: str, constructor: str) -> str:
    """``<dataset>_detailed_<constructor>`` — fixed Detailed describer is implicit."""
    return f"{dataset}_{FIXED_PROMPT}_{constructor}"


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description="E3 constructor isolation. Dry-run validates payloads; paid API constructors "
        "are disabled. Open-weight HF constructors may --execute.",
    )
    ap.add_argument("--dataset", choices=rio.DATASET_CHOICES, required=True)
    ap.add_argument("--constructor", choices=CONSTRUCTOR_CHOICES, required=True,
                    help="one of the five Exp4 constructors (or 'all')")
    ap.add_argument("--descriptions-dir", default=None,
                    help="E1 directory with GPT-5.4-mini Detailed NNNN.json descriptions "
                         f"(default experiments/E1/outputs/<dataset>_{FIXED_PROMPT}_{FIXED_DESCRIBER}/ ; "
                         "PARENT of such folders when several datasets)")
    ap.add_argument("--data-root", default=None,
                    help=f"dataset root (overrides ${dio.DATA_ROOT_ENV}; packaged datasets/ is the fallback)")
    ap.add_argument("--out-dir", default=None,
                    help="default experiments/E3/outputs/<dataset>_detailed_<constructor>/ "
                         "(PARENT when several combinations)")
    ap.add_argument("--limit", type=int, default=None, help="only the first N schemas of each dataset")
    ap.add_argument("--schema-id", action="append", default=None,
                    help="restrict to one or more gold schema ids (repeatable)")
    ap.add_argument("--skip-existing", dest="skip_existing", action=argparse.BooleanOptionalAction, default=True,
                    help="skip schemas whose NNNN.json already holds a valid reconstruction (default: on)")
    ap.add_argument("--resume", dest="skip_existing", action="store_const", const=True,
                    help="alias for --skip-existing")
    ap.add_argument("--retry-failed", action="store_true",
                    help="re-run schemas whose existing NNNN.json has an error / is incomplete "
                         "(writes beside the original under NNNN.retry.json when a complete record exists)")
    ap.add_argument("--device", default="auto",
                    help="HF device_map: auto (default), cpu, cuda, cuda:0, ... (open models only)")
    ap.add_argument("--dtype", choices=DTYPES, default="float16", help="HF torch dtype (default float16)")
    ap.add_argument("--load-in-4bit", action="store_true", help="HF only; needs bitsandbytes (CUDA)")
    ap.add_argument("--max-tokens", type=int, default=None, help="override constructor max tokens")
    ap.add_argument("--max-retries", type=int, default=5,
                    help="extra attempts with exponential backoff on rate limits (default 5)")
    ap.add_argument("--retry-base-delay", type=float, default=2.0, help="initial backoff in seconds (default 2)")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="default behaviour: validate payloads, no API/GPU call")
    mode.add_argument("--execute", action="store_true", help="actually call the constructor (open-weight only)")
    ap.add_argument("--confirm-paid", action="store_true",
                    help="DEPRECATED/ignored: paid API constructors are disabled in this package")
    ap.add_argument("--write-plan", action="store_true", help="dry-run only: write dry_run_plan.json under --out-dir")
    return ap


def build_record(
    rec: dio.GoldRecord,
    constructor: str,
    nl_text: str,
    req: ic.Request | None,
    *,
    result: dict | None = None,
    error: str | None = None,
    raw: str | None = None,
    nl_sha256: str | None = None,
) -> dict:
    out = {
        "text_number": int(rec.serial),
        "id": rec.schema_id,
        "llm": constructor,
        "model_id": ic.MODELS[constructor].model_id,
        "source_schema2text_llm": FIXED_DESCRIBER,
        "source_prompt_style": rio.PROMPT_STYLE[FIXED_PROMPT],
        "database": rec.database,
        "nl_text": nl_text,
        "nl_sha256": nl_sha256 or (rio.sha256_text(nl_text) if nl_text else ""),
        "gold_question": rec.gold_nl,
        "ddl": (result or {}).get("ddl", ""),
        "metadata": (result or {}).get("metadata", {}),
    }
    if error:
        out["error"] = error
        if raw:
            out["raw_response"] = raw[:4000]
    if req is not None:
        out["generation"] = {
            "prompt_sha256": pa.EXPECTED_SHA256["constructor"],
            "temperature": req.temperature,
            "max_tokens": req.max_tokens,
            "describer_prompt_sha256": pa.EXPECTED_SHA256[FIXED_PROMPT],
        }
    return out


def _filter_ids(gold: list[dio.GoldRecord], schema_ids: list[str] | None) -> list[dio.GoldRecord]:
    if not schema_ids:
        return gold
    wanted = set(schema_ids)
    out = [r for r in gold if r.schema_id in wanted]
    missing = wanted - {r.schema_id for r in out}
    if missing:
        raise ValueError(f"unknown --schema-id values for dataset: {sorted(missing)}")
    return out


def _load_descriptions(dataset: str, desc_dir: Path, data_root, limit, schema_ids):
    gold = dio.load_dataset(dataset, data_root)
    gold = gold[:limit] if limit else gold
    gold = _filter_ids(gold, schema_ids)
    preds = rio.load_prediction_dir(desc_dir) if desc_dir.is_dir() else {}
    out = []
    for rec, entry, align_reason in rio.align_predictions(gold, preds):
        reason = align_reason or rio.nl_failure(entry)
        out.append((rec, None if reason else entry["nl_text"], reason,
                    None if reason else rio.description_hash(entry)))
    return gold, out


def _request(nl: str, rec: dio.GoldRecord, constructor: str, max_tokens: int | None) -> ic.Request:
    req = ic.build_request(constructor, task="constructor", database=rec.database, nl_text=nl)
    return dataclasses.replace(req, max_tokens=max_tokens) if max_tokens else req


def dry_run_one(dataset: str, constructor: str, args, desc_dir: Path, out_dir: Path) -> dict:
    gold, items = _load_descriptions(dataset, desc_dir, args.data_root, args.limit, args.schema_id)
    avail = [(r, nl, h) for r, nl, why, h in items if why is None]
    missing = [(r, why) for r, nl, why, h in items if why is not None]
    total_chars, sizes = 0, []
    for rec, nl, _h in avail:
        req = _request(nl, rec, constructor, args.max_tokens)
        total_chars += req.approx_input_chars()
        if len(sizes) < 3:
            sizes.append({"serial": rec.serial, "id": rec.schema_id, "system_chars": len(req.system),
                          "user_chars": len(req.user), "max_tokens": req.max_tokens,
                          "temperature": req.temperature, "nl_sha256": rio.sha256_text(nl)})
    placeholder = False
    if not sizes and gold:
        placeholder = True
        req = _request(PLACEHOLDER_NL, gold[0], constructor, args.max_tokens)
        sizes.append({"serial": gold[0].serial, "id": gold[0].schema_id, "system_chars": len(req.system),
                      "user_chars": len(req.user), "max_tokens": req.max_tokens,
                      "temperature": req.temperature, "placeholder_description": True})
    n_done = 0
    if out_dir.is_dir():
        for r in gold:
            g_meta = metadata_from_ddl(r.ddl, database=r.database)
            if rio.is_complete_e3_ddl_record(out_dir / f"{r.serial}.json", r.schema_id,
                                            gold_ddl=r.ddl, gold_meta=g_meta):
                n_done += 1
    c = ic.MODELS[constructor]
    plan = {
        "experiment": "E3", "dataset": dataset, "constructor": constructor,
        "fixed_describer": FIXED_DESCRIBER, "fixed_prompt": FIXED_PROMPT,
        "model_id": c.model_id, "provider": c.provider, "paid": c.paid,
        "n_expected": dio.EXPECTED_COUNTS[dataset], "n_selected": len(gold),
        "descriptions_dir": str(desc_dir), "descriptions_dir_exists": desc_dir.is_dir(),
        "n_descriptions_available": len(avail), "n_descriptions_missing": len(missing),
        "n_already_complete": n_done,
        "n_to_construct": len(avail) - (n_done if args.skip_existing else 0),
        "approx_total_input_chars": total_chars,
        "constructor_prompt_sha256": pa.EXPECTED_SHA256["constructor"],
        "describer_prompt_sha256": pa.EXPECTED_SHA256[FIXED_PROMPT],
        "first_requests": sizes, "out_dir": str(out_dir), "dry_run": True,
    }
    print(f"[dry-run] {dataset} / fixed={FIXED_DESCRIBER}+{FIXED_PROMPT} -> constructor {c.model_id} "
          f"[{c.provider}{', PAID' if c.paid else ''}]")
    print(f"  schemas selected={plan['n_selected']} (expected {plan['n_expected']}); descriptions dir "
          f"{'found' if plan['descriptions_dir_exists'] else 'NOT FOUND'}: {desc_dir}")
    print(f"  descriptions: available={len(avail)} missing/invalid={len(missing)}"
          + (f" (first: {missing[0][0].serial}:{missing[0][1]})" if missing else ""))
    print(f"  constructor prompt sha256: {pa.EXPECTED_SHA256['constructor']}")
    print(f"  temperature={ic.temperature_for(c, 'constructor')} "
          f"max_tokens_default={ic.max_tokens_for(c, 'constructor', None)}")
    for s in sizes:
        print(f"  payload {s['serial']} id={s['id']}: system={s['system_chars']} chars, "
              f"user={s['user_chars']} chars, max_tokens={s['max_tokens']}, T={s['temperature']}"
              + (" (placeholder description)" if placeholder else ""))
    print(f"  resume: {n_done} complete in {out_dir}; to construct: {plan['n_to_construct']} "
          f"| approx total input chars: {total_chars}")
    if args.write_plan:
        path = out_dir / "dry_run_plan.json"
        rio.write_json(path, plan)
        print(f"  wrote plan -> {path}")
    return plan


def execute_one(dataset: str, constructor: str, args, desc_dir: Path, out_dir: Path, client) -> int:
    _, items = _load_descriptions(dataset, desc_dir, args.data_root, args.limit, args.schema_id)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[execute] {dataset} / constructor={constructor}: {len(items)} schema(s) -> {out_dir}")
    n_ok = n_skip = n_err = 0
    for rec, nl, why, nl_hash in items:
        jpath, tpath = out_dir / f"{rec.serial}.json", out_dir / f"{rec.serial}.txt"
        g_meta = metadata_from_ddl(rec.ddl, database=rec.database)
        complete = rio.is_complete_e3_ddl_record(jpath, rec.schema_id, gold_ddl=rec.ddl, gold_meta=g_meta)
        if args.skip_existing and complete and not args.retry_failed:
            n_skip += 1
            continue
        if args.retry_failed and complete:
            # Keep the successful original; write a separately identifiable retry sidecar only if
            # the caller forces a re-generation (we still skip successful records).
            n_skip += 1
            continue
        if why is not None:
            rio.write_json(jpath, build_record(rec, constructor, "", None,
                                              error=f"missing_fixed_description:{why}"))
            n_err += 1
            continue
        req = _request(nl, rec, constructor, args.max_tokens)
        t0 = time.time()
        try:
            raw = rio.generate_with_backoff(client, req, max_retries=args.max_retries,
                                            base_delay=args.retry_base_delay)
            result, reason = rio.parse_constructor_response(raw)
            out = build_record(rec, constructor, nl, req, result=result, nl_sha256=nl_hash,
                               error=f"constructor_parse_failed:{reason}" if reason else None, raw=raw)
        except (ic.PaidCallNotConfirmed, ic.MissingApiKey, ic.ApiMethodsDisabled):
            raise
        except Exception as e:  # noqa: BLE001
            out = build_record(rec, constructor, nl, req, nl_sha256=nl_hash,
                               error=f"{type(e).__name__}: {str(e)[:300]}")
        out.setdefault("generation", {})["elapsed_s"] = round(time.time() - t0, 3)
        # Do not overwrite a previously complete successful record: write sidecar instead.
        if jpath.is_file() and complete:
            jpath = out_dir / f"{rec.serial}.retry.json"
            tpath = out_dir / f"{rec.serial}.retry.txt"
        rio.write_json(jpath, out)
        if out.get("error"):
            n_err += 1
            print(f"  {rec.serial} {rec.schema_id}: ERROR {out['error'][:120]}")
        else:
            tpath.write_text(out["ddl"], encoding="utf-8")
            n_ok += 1
    print(f"  done: constructed={n_ok} skipped_existing={n_skip} errors={n_err}")
    return n_err


def main(argv: Sequence[str] | None = None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)
    datasets = rio.expand(args.dataset, rio.DATASETS)
    constructors = rio.expand(args.constructor, ic.E3_CONSTRUCTOR_KEYS)
    multi = len(datasets) * len(constructors) > 1
    if args.execute:
        paid = [c for c in constructors if ic.MODELS[c].paid]
        if paid:
            ap.error(
                "Paid API methods are disabled: constructors "
                + ", ".join(paid)
                + " cannot be executed from this package. Use dry-run (default) to validate payloads, "
                "or evaluate saved reconstructions with experiments/E3/evaluate.py. "
                "Open-weight HF constructors (codellama13b, llama31, deepseek) may use --execute."
            )
    if args.write_plan and args.execute:
        ap.error("--write-plan is a dry-run option")
    if args.limit is not None and args.limit < 1:
        ap.error("--limit must be >= 1")
    try:
        pa.verify_all_prompts()
        dirs = {}
        for d in datasets:
            for c in constructors:
                combo = e3_combo_name(d, c)
                desc_combo = rio.combo_name(d, FIXED_PROMPT, FIXED_DESCRIBER)
                dirs[(d, c)] = (
                    rio.combo_dir(args.descriptions_dir, DEFAULT_DESC_PARENT, desc_combo, multi=multi),
                    rio.assert_ignored_out_dir(
                        rio.combo_dir(args.out_dir, DEFAULT_OUT_PARENT, combo, multi=multi)
                    ),
                )
    except (pa.PromptHashError, ValueError, FileNotFoundError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    print("prompt hashes verified: " + ", ".join(f"{k}={v[:12]}" for k, v in pa.EXPECTED_SHA256.items()))
    if not args.execute:
        print("DRY-RUN: payloads are validated; no network / GPU weights are used.")
        try:
            for d in datasets:
                for c in constructors:
                    dry_run_one(d, c, args, *dirs[(d, c)])
            return 0
        except (ic.ApiMethodsDisabled, ic.MissingApiKey) as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
        except (ValueError, FileNotFoundError, KeyError) as e:
            print(f"error: {e}", file=sys.stderr)
            return 2

    print("EXECUTE: open-weight HF constructors only.")
    try:
        n_err = 0
        for d in datasets:
            for c in constructors:
                desc_dir, out_dir = dirs[(d, c)]
                client = ic.get_client(
                    c, dry_run=False, load_in_4bit=args.load_in_4bit,
                    device_map=args.device, dtype=args.dtype,
                )
                n_err += execute_one(d, c, args, desc_dir, out_dir, client)
        return 1 if n_err else 0
    except (ic.ApiMethodsDisabled, ic.MissingApiKey) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    except (ValueError, FileNotFoundError, KeyError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
