#!/usr/bin/env python3
"""E2 round trip, step 2: GPT-4o-mini constructor (NL description -> DDL + metadata).  DRY-RUN BY DEFAULT.

    python experiments/E2/run.py --dataset rschema --describer-model llama31 --prompt detailed \\
        --e1-pred-dir experiments/E1/outputs/rschema_detailed_llama31                     # dry-run
    python experiments/E2/run.py --dataset rschema --describer-model llama31 --prompt detailed \\
        --e1-pred-dir experiments/E1/outputs/rschema_detailed_llama31 \\
        --execute --confirm-paid                                                          # PAID API

Reads the E1 descriptions (``nl_text`` of ``NNNN.json``) and builds GPT-4o-mini constructor
payloads (``prompts/constructor.txt``, hash-verified).  Dry-run (the default) validates the payloads
and makes no API call.  A real constructor run needs BOTH ``--execute`` and ``--confirm-paid`` (it
costs money) and ``OPENAI_API_KEY`` in the environment (never read from files / printed / stored).

E1 provenance is strict: every description must carry the requested describer (``llm``,
``model_id``), ``prompt_style`` and describer-prompt SHA-256; records with missing or wrong
provenance are NOT sent to the constructor (they become ``missing_e1_description`` error records).
``--allow-legacy-e1`` tolerates *missing* provenance fields (with a recorded warning); wrong ones
are always rejected.  Duplicate schema ids / mixed prompt styles in the E1 directory abort the run.

An empty reconstruction ``{"ddl": "", "metadata": {...}}`` is a valid answer (a genuinely empty
schema) and is stored as a successful record; ``experiments/E2/evaluate.py`` scores it accordingly.
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
from src import provenance as prov  # noqa: E402
from src import repro_io as rio  # noqa: E402

DEFAULT_E1_PARENT = ROOT / "experiments" / "E1" / "outputs"
DEFAULT_OUT_PARENT = ROOT / "experiments" / "E2" / "outputs"
DESCRIBER_CHOICES = tuple(ic.DESCRIBER_KEYS) + ("all",)
PLACEHOLDER_NL = "[placeholder description used only to size a dry-run payload]"


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description="E2 constructor pipeline. Dry-run (default) validates GPT-4o-mini payloads without any API "
        "call; --execute --confirm-paid runs the paid OpenAI constructor (needs OPENAI_API_KEY in the environment).",
    )
    ap.add_argument("--dataset", choices=rio.DATASET_CHOICES, required=True)
    ap.add_argument("--describer-model", choices=DESCRIBER_CHOICES, required=True,
                    help="the E1 describer whose descriptions are reconstructed")
    ap.add_argument("--prompt", choices=rio.PROMPT_VARIANTS, required=True, help="E1 describer prompt")
    ap.add_argument("--e1-pred-dir", default=None,
                    help="E1 directory with NNNN.json descriptions (default experiments/E1/outputs/"
                         "<dataset>_<prompt>_<describer>/ ; with several combinations this is a PARENT of "
                         "<dataset>_<prompt>_<describer>/ folders)")
    ap.add_argument("--data-root", default=None,
                    help=f"dataset root (overrides ${dio.DATA_ROOT_ENV}; packaged datasets/ is the fallback)")
    ap.add_argument("--out-dir", default=None,
                    help="default experiments/E2/outputs/<dataset>_<prompt>_<describer>/ (PARENT when several)")
    ap.add_argument("--limit", type=int, default=None, help="only the first N schemas of each dataset")
    ap.add_argument("--skip-existing", dest="skip_existing", action=argparse.BooleanOptionalAction, default=True,
                    help="skip schemas whose NNNN.json already holds a reconstructed ddl (default: on)")
    ap.add_argument("--max-tokens", type=int, default=None, help="override constructor max tokens (default 16384)")
    ap.add_argument("--max-retries", type=int, default=5,
                    help="extra attempts with exponential backoff on rate limits (default 5)")
    ap.add_argument("--retry-base-delay", type=float, default=2.0, help="initial backoff in seconds (default 2)")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="default behaviour: validate payloads, no API call")
    mode.add_argument("--execute", action="store_true", help="actually call the (paid) constructor")
    ap.add_argument("--confirm-paid", action="store_true",
                    help="REQUIRED with --execute: acknowledges that real, billed OpenAI calls (gpt-4o-mini) are made")
    ap.add_argument("--allow-legacy-e1", action="store_true", default=False,
                    help="accept E1 records whose provenance fields (llm/model_id/prompt_style/prompt sha) are "
                         "MISSING (a warning is recorded); present-but-wrong fields are still rejected. "
                         "Default: strict provenance")
    ap.add_argument("--write-plan", action="store_true", help="dry-run only: write dry_run_plan.json under --out-dir")
    return ap


def build_record(rec: dio.GoldRecord, describer: str, prompt: str, nl_text: str, req: ic.Request | None, *,
                 result: dict | None = None, error: str | None = None, raw: str | None = None,
                 provenance: dict | None = None) -> dict:
    """One E2 JSON record.  ``provenance`` = validated E1 provenance (``src.provenance.entry_provenance``)."""
    out = {
        "text_number": int(rec.serial),
        "id": rec.schema_id,
        "llm": rio.CONSTRUCTOR_KEY,
        "model_id": ic.MODELS[rio.CONSTRUCTOR_KEY].model_id,
        "source_schema2text_llm": describer,
        "source_prompt_style": rio.PROMPT_STYLE[prompt],
        **{k: v for k, v in (provenance or {}).items() if k != "source_schema2text_llm"},
        "database": rec.database,
        "nl_text": nl_text,
        "gold_question": rec.gold_nl,
        "ddl": (result or {}).get("ddl", ""),
        "metadata": (result or {}).get("metadata", {}),
    }
    if error:
        out["error"] = error
        if raw:
            out["raw_response"] = raw[:4000]
    if req is not None:
        out["generation"] = {"prompt_sha256": pa.EXPECTED_SHA256["constructor"],
                             "temperature": req.temperature, "max_tokens": req.max_tokens}
    return out


def _load_descriptions(dataset: str, e1_dir: Path, data_root, limit, *, describer: str, prompt: str,
                       allow_legacy: bool = False):
    """``(gold, items, provenance_by_serial)``; ``items`` = ``[(gold_record, nl_text | None, reason | None)]``.

    Every description is validated with :func:`src.provenance.validate_e1_description` (strict unless
    ``allow_legacy``).  A record that fails validation is reported as missing/invalid
    (``reason = "provenance: ..."``) -- never silently relabelled.  Duplicate schema ids in the
    directory (and, when strict, mixed prompt styles) raise :class:`src.provenance.ProvenanceError`.
    """
    mode = "legacy" if allow_legacy else "strict"
    gold = dio.load_dataset(dataset, data_root)
    gold = gold[:limit] if limit else gold
    preds = rio.load_prediction_dir(e1_dir) if e1_dir.is_dir() else {}
    prov.check_directory(preds, prompt=prompt, mode=mode)
    out, provenance = [], {}
    for rec, entry, align_reason in rio.align_predictions(gold, preds):
        reason = align_reason or rio.nl_failure(entry)
        if reason is None:
            try:
                warnings = prov.validate_e1_description(entry, gold=rec, dataset=dataset, describer=describer,
                                                        prompt=prompt, mode=mode)
                provenance[rec.serial] = prov.entry_provenance(entry, describer=describer, prompt=prompt,
                                                               mode=mode, warnings=warnings)
            except prov.ProvenanceError as e:
                reason = f"provenance: {e}"
        out.append((rec, None if reason else entry["nl_text"], reason))
    return gold, out, provenance


def _request(nl: str, rec: dio.GoldRecord, max_tokens: int | None) -> ic.Request:
    req = ic.build_request(rio.CONSTRUCTOR_KEY, task="constructor", database=rec.database, nl_text=nl)
    return dataclasses.replace(req, max_tokens=max_tokens) if max_tokens else req


def dry_run_one(dataset: str, describer: str, prompt: str, args, e1_dir: Path, out_dir: Path) -> dict:
    gold, items, _prov = _load_descriptions(dataset, e1_dir, args.data_root, args.limit, describer=describer,
                                            prompt=prompt, allow_legacy=args.allow_legacy_e1)
    avail = [(r, nl) for r, nl, why in items if why is None]
    missing = [(r, why) for r, nl, why in items if why is not None]
    total_chars, sizes = 0, []
    for rec, nl in avail:
        req = _request(nl, rec, args.max_tokens)
        total_chars += req.approx_input_chars()
        if len(sizes) < 3:
            sizes.append({"serial": rec.serial, "id": rec.schema_id, "system_chars": len(req.system),
                          "user_chars": len(req.user), "max_tokens": req.max_tokens})
    placeholder = False
    if not sizes and gold:  # still validate the payload assembly
        placeholder = True
        req = _request(PLACEHOLDER_NL, gold[0], args.max_tokens)
        sizes.append({"serial": gold[0].serial, "id": gold[0].schema_id, "system_chars": len(req.system),
                      "user_chars": len(req.user), "max_tokens": req.max_tokens, "placeholder_description": True})
    n_done = sum(rio.is_complete_ddl_record(out_dir / f"{r.serial}.json", r.schema_id) for r in gold) \
        if out_dir.is_dir() else 0
    c = ic.MODELS[rio.CONSTRUCTOR_KEY]
    plan = {
        "experiment": "E2", "dataset": dataset, "describer_model": describer, "prompt": prompt,
        "constructor": c.model_id, "provider": c.provider, "paid": c.paid,
        "n_expected": dio.EXPECTED_COUNTS[dataset], "n_selected": len(gold),
        "e1_dir": str(e1_dir), "e1_dir_exists": e1_dir.is_dir(), "n_descriptions_available": len(avail),
        "n_descriptions_missing": len(missing), "n_already_complete": n_done,
        "n_to_construct": len(avail) - (n_done if args.skip_existing else 0),
        "approx_total_input_chars": total_chars, "constructor_prompt_sha256": pa.EXPECTED_SHA256["constructor"],
        "e1_provenance_mode": "legacy" if args.allow_legacy_e1 else "strict",
        "first_requests": sizes, "out_dir": str(out_dir), "dry_run": True,
    }
    print(f"[dry-run] {dataset} / {prompt} / describer={describer} -> constructor {c.model_id} [{c.provider}, PAID]")
    print(f"  schemas selected={plan['n_selected']} (expected {plan['n_expected']}); E1 dir "
          f"{'found' if plan['e1_dir_exists'] else 'NOT FOUND'}: {e1_dir}")
    print(f"  E1 descriptions: available={len(avail)} missing/invalid={len(missing)}"
          + (f" (first: {missing[0][0].serial}:{missing[0][1]})" if missing else ""))
    print(f"  constructor prompt sha256: {pa.EXPECTED_SHA256['constructor']}")
    for s in sizes:
        print(f"  payload {s['serial']} id={s['id']}: system={s['system_chars']} chars, user={s['user_chars']} chars, "
              f"max_tokens={s['max_tokens']}" + (" (placeholder description)" if placeholder else ""))
    print(f"  resume: {n_done} complete in {out_dir}; to construct: {plan['n_to_construct']} "
          f"| approx total input chars: {total_chars}")
    if args.write_plan:
        path = out_dir / "dry_run_plan.json"
        rio.write_json(path, plan)
        print(f"  wrote plan -> {path}")
    return plan


def execute_one(dataset: str, describer: str, prompt: str, args, e1_dir: Path, out_dir: Path, client) -> int:
    _, items, provenance = _load_descriptions(dataset, e1_dir, args.data_root, args.limit, describer=describer,
                                              prompt=prompt, allow_legacy=args.allow_legacy_e1)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[execute] {dataset} / {prompt} / describer={describer}: {len(items)} schema(s) -> {out_dir}")
    n_ok = n_skip = n_err = 0
    for rec, nl, why in items:
        jpath, tpath = out_dir / f"{rec.serial}.json", out_dir / f"{rec.serial}.txt"
        if args.skip_existing and rio.is_complete_ddl_record(jpath, rec.schema_id):
            n_skip += 1
            continue
        if why is not None:  # no usable description -> explicit error record, no API call
            rio.write_json(jpath, build_record(rec, describer, prompt, "", None, error=f"missing_e1_description:{why}"))
            n_err += 1
            continue
        req = _request(nl, rec, args.max_tokens)
        t0 = time.time()
        try:
            raw = rio.generate_with_backoff(client, req, max_retries=args.max_retries, base_delay=args.retry_base_delay)
            result, reason = rio.parse_constructor_response(raw, allow_empty_ddl=True)
            out = build_record(rec, describer, prompt, nl, req, result=result,
                               error=f"constructor_parse_failed:{reason}" if reason else None, raw=raw,
                               provenance=provenance.get(rec.serial))
        except (ic.PaidCallNotConfirmed, ic.MissingApiKey):
            raise
        except Exception as e:  # noqa: BLE001
            out = build_record(rec, describer, prompt, nl, req, error=f"{type(e).__name__}: {str(e)[:300]}",
                               provenance=provenance.get(rec.serial))
        out.setdefault("generation", {})["elapsed_s"] = round(time.time() - t0, 3)
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
    describers = rio.expand(args.describer_model, ic.DESCRIBER_KEYS)
    multi = len(datasets) * len(describers) > 1
    if args.execute and not args.confirm_paid:
        ap.error(
            "the GPT-4o-mini constructor is a paid API: --execute requires --confirm-paid as well "
            "(real, billed calls). Without --execute the run is a free dry-run."
        )
    if args.write_plan and args.execute:
        ap.error("--write-plan is a dry-run option")
    if args.limit is not None and args.limit < 1:
        ap.error("--limit must be >= 1")
    try:
        pa.verify_all_prompts()
        dirs = {}
        for d in datasets:
            for m in describers:
                combo = rio.combo_name(d, args.prompt, m)
                dirs[(d, m)] = (
                    rio.combo_dir(args.e1_pred_dir, DEFAULT_E1_PARENT, combo, multi=multi),
                    rio.assert_ignored_out_dir(rio.combo_dir(args.out_dir, DEFAULT_OUT_PARENT, combo, multi=multi)),
                )
    except (pa.PromptHashError, ValueError, FileNotFoundError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    print("prompt hashes verified: " + ", ".join(f"{k}={v[:12]}" for k, v in pa.EXPECTED_SHA256.items()))
    print(f"E1 provenance: {'LEGACY (--allow-legacy-e1: missing fields tolerated)' if args.allow_legacy_e1 else 'strict'}")
    if not args.execute:
        print("DRY-RUN: payloads are validated; no API call is made (use --execute --confirm-paid to construct).")
    try:
        if not args.execute:
            for d in datasets:
                for m in describers:
                    dry_run_one(d, m, args.prompt, args, *dirs[(d, m)])
            return 0
        client = ic.get_client(rio.CONSTRUCTOR_KEY, dry_run=False, confirm_paid=args.confirm_paid)  # needs OPENAI_API_KEY
        errors = 0
        for d in datasets:
            for m in describers:
                errors += execute_one(d, m, args.prompt, args, *dirs[(d, m)], client)
        return 1 if errors else 0
    except (ic.PaidCallNotConfirmed, ic.MissingApiKey, ic.ApiMethodsDisabled) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    except (ValueError, FileNotFoundError, KeyError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
