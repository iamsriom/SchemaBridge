#!/usr/bin/env python3
"""E1 offline evaluation: Schema2Text metrics (Table VII inputs).  No API, no generation.

For every (dataset, prompt, model) it aligns ``NNNN.json`` predictions with the gold records by
serial / schema id and computes

* BLEU-4   corpus-level sacrebleu, CORRECT layout ``corpus_bleu(hyps, [refs])``,
* ROUGE-L  mean F1 (rouge-score, stemming),
* BERTScore F1 (roberta-large, no IDF, no rescaling; ``--skip-bertscore`` to omit),
* SCR      macro-averaged Schema Coverage Rate against the gold DDL.

Enterprise-145 has no gold natural language: BLEU / ROUGE-L / BERTScore are N/A, only SCR is
computed.  Missing / unreadable / errored / empty hypotheses follow ``--fail-policy``:
``score`` (default) keeps the schema with an empty hypothesis (all metrics see ""), ``skip``
drops it from every metric.  Files are written ONLY below ``--out-dir`` (git-ignored by default):

    <out-dir>/<dataset>_<prompt>_<model>/metrics.json
    <out-dir>/<dataset>_<prompt>_<model>/per_record.csv
    <out-dir>/e1_summary.csv          (rows are upserted per dataset/prompt/model)

Hardcoded reference scores do not exist anywhere in this script.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import datasets_io as dio  # noqa: E402
from src import inference_clients as ic  # noqa: E402
from src import nl_metrics as nlm  # noqa: E402
from src import prompt_assets as pa  # noqa: E402
from src import repro_io as rio  # noqa: E402

DEFAULT_PRED_PARENT = ROOT / "experiments" / "E1" / "outputs"
DEFAULT_OUT_DIR = ROOT / "experiments" / "E1" / "outputs" / "metrics"
MODEL_CHOICES = tuple(ic.DESCRIBER_KEYS) + ("all",)
PROMPT_CHOICES = rio.PROMPT_VARIANTS + ("all",)
SUMMARY_FIELDS = ("dataset", "model", "prompt", "n_gold", "n_scored", "n_failed", "fail_policy",
                  "bleu4", "rougeL", "bertscore_f1", "scr_macro")
RECORD_FIELDS = ("serial", "schema_id", "status", "failure_reason", "scr", "scr_matched", "scr_total", "hyp_chars")


def sanitized_hyp(entry: dict | None) -> tuple[str, str | None]:
    """``(hypothesis, failure_reason)``; the hypothesis is "" for unusable entries."""
    reason = rio.nl_failure(entry)
    if reason is not None:
        return "", reason
    return nlm.sanitize_nl_text(entry["nl_text"]), None


def evaluate_combo(dataset: str, model: str, prompt: str, pred_dir: Path, *, data_root: str | None,
                   fail_policy: str, skip_bertscore: bool, device: str, strict: bool = True) -> tuple[dict, list[dict]]:
    """Return ``(metrics_json, per_record_rows)`` for one run directory."""
    gold = dio.load_dataset(dataset, data_root, strict=strict)
    preds = rio.load_prediction_dir(pred_dir)
    aligned = rio.align_predictions(gold, preds)

    rows: list[dict] = []
    kept: list[tuple[dio.GoldRecord, str]] = []
    n_failed = 0
    for rec, entry, align_reason in aligned:
        hyp, reason = sanitized_hyp(entry)
        reason = align_reason or reason
        failed = reason is not None
        n_failed += failed
        scr = nlm.schema_coverage_rate(rec.ddl, hyp)
        rows.append({
            "serial": rec.serial, "schema_id": rec.schema_id,
            "status": ("skipped" if fail_policy == "skip" else "scored_empty") if failed else "ok",
            "failure_reason": reason or "", "scr": scr["coverage"], "scr_matched": scr["matched"],
            "scr_total": scr["total"], "hyp_chars": len(hyp),
        })
        if failed and fail_policy == "skip":
            continue
        kept.append((rec, hyp))

    hyps = [h for _, h in kept]
    ddls = [r.ddl for r, _ in kept]
    metrics: dict[str, float | None] = {"bleu4": None, "rougeL": None, "bertscore_f1": None, "scr_macro": None}
    not_applicable: list[str] = []
    skipped: list[str] = []
    n_text = 0
    if hyps:
        metrics["scr_macro"] = nlm.compute_scr_macro(hyps, ddls)
    if dataset == "enterprise145":
        not_applicable = ["bleu4", "rougeL", "bertscore_f1"]
    else:
        pairs = [(h, r.gold_nl) for r, h in kept if r.gold_nl]
        n_text = len(pairs)
        if pairs:
            t_hyps, t_refs = [p[0] for p in pairs], [p[1] for p in pairs]
            metrics["bleu4"] = nlm.compute_bleu(t_hyps, t_refs)
            metrics["rougeL"] = nlm.compute_rougeL(t_hyps, t_refs)
            if skip_bertscore:
                skipped.append("bertscore_f1")
            else:
                metrics["bertscore_f1"] = nlm.compute_bertscore(t_hyps, t_refs, device=device)
    out = {
        "experiment": "E1", "dataset": dataset, "model": model, "model_id": ic.MODELS[model].model_id,
        "prompt": prompt, "prompt_style": rio.PROMPT_STYLE[prompt],
        "prompt_sha256": pa.EXPECTED_SHA256[prompt], "fail_policy": fail_policy,
        "n_gold": len(gold), "n_predictions_found": sum(1 for _, e, _ in aligned if e is not None),
        "n_failed": n_failed, "n_scored": len(kept), "n_text_metric_pairs": n_text,
        "metrics": metrics, "not_applicable": not_applicable, "skipped": skipped,
        "bleu_layout": "corpus_bleu(hyps, [refs])", "bertscore_model": nlm.BERTSCORE_MODEL,
        "scr_aggregation": "macro", "pred_dir": str(pred_dir),
    }
    return out, rows


def summary_row(m: dict) -> dict:
    return {"dataset": m["dataset"], "model": m["model"], "prompt": m["prompt"], "n_gold": m["n_gold"],
            "n_scored": m["n_scored"], "n_failed": m["n_failed"], "fail_policy": m["fail_policy"],
            **{k: m["metrics"][k] for k in ("bleu4", "rougeL", "bertscore_f1", "scr_macro")}}


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="E1 offline Schema2Text evaluation (BLEU / ROUGE-L / BERTScore / SCR).")
    ap.add_argument("--dataset", choices=rio.DATASET_CHOICES, required=True)
    ap.add_argument("--model", choices=MODEL_CHOICES, required=True)
    ap.add_argument("--prompt", choices=PROMPT_CHOICES, required=True)
    ap.add_argument("--pred-dir", default=None,
                    help="directory with NNNN.json (default experiments/E1/outputs/<dataset>_<prompt>_<model>/ ; "
                         "with several combinations this is a PARENT of <dataset>_<prompt>_<model>/ folders)")
    ap.add_argument("--data-root", default=None,
                    help=f"dataset root (overrides ${dio.DATA_ROOT_ENV}; packaged datasets/ is the fallback)")
    ap.add_argument("--out-dir", default=None,
                    help="metrics output directory (default experiments/E1/outputs/metrics/, git-ignored)")
    ap.add_argument("--device", default="cpu", help="device for BERTScore (cpu, cuda, mps; default cpu)")
    ap.add_argument("--skip-bertscore", action="store_true", help="do not compute BERTScore (no torch needed)")
    ap.add_argument("--fail-policy", choices=("score", "skip"), default="score",
                    help="missing/invalid hypotheses: score = empty hypothesis (default), skip = drop the schema")
    return ap


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    datasets = rio.expand(args.dataset, rio.DATASETS)
    models = rio.expand(args.model, ic.DESCRIBER_KEYS)
    prompts = rio.expand(args.prompt, rio.PROMPT_VARIANTS)
    multi = len(datasets) * len(models) * len(prompts) > 1
    try:
        out_dir = rio.assert_ignored_out_dir(args.out_dir or DEFAULT_OUT_DIR)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    summary: list[dict] = []
    n_missing_dirs = 0
    for d in datasets:
        for p in prompts:
            for m in models:
                combo = rio.combo_name(d, p, m)
                pred_dir = rio.combo_dir(args.pred_dir, DEFAULT_PRED_PARENT, combo, multi=multi)
                if not pred_dir.is_dir():
                    n_missing_dirs += 1
                    print(f"[skip] {combo}: prediction directory not found: {pred_dir}")
                    continue
                try:
                    metrics, rows = evaluate_combo(d, m, p, pred_dir, data_root=args.data_root,
                                                   fail_policy=args.fail_policy, skip_bertscore=args.skip_bertscore,
                                                   device=args.device)
                except ImportError as e:
                    print(f"error: missing metric dependency ({e}); install sacrebleu, rouge-score and "
                          "(for BERTScore) bert-score + torch, or pass --skip-bertscore", file=sys.stderr)
                    return 3
                except (FileNotFoundError, ValueError, KeyError) as e:
                    print(f"error: {e}", file=sys.stderr)
                    return 2
                rio.write_json(out_dir / combo / "metrics.json", metrics)
                rio.write_csv(out_dir / combo / "per_record.csv", rows, RECORD_FIELDS)
                summary.append(summary_row(metrics))
                mm = metrics["metrics"]
                fmt = lambda v: "N/A" if v is None else f"{v:.4f}"  # noqa: E731
                print(f"[{combo}] gold={metrics['n_gold']} scored={metrics['n_scored']} failed={metrics['n_failed']} "
                      f"BLEU={fmt(mm['bleu4'])} ROUGE-L={fmt(mm['rougeL'])} "
                      f"BERTScore={fmt(mm['bertscore_f1'])} SCR={fmt(mm['scr_macro'])}")
    if summary:
        rio.upsert_csv(out_dir / "e1_summary.csv", summary, SUMMARY_FIELDS, ("dataset", "model", "prompt"))
        print(f"wrote metrics under {out_dir}")
    elif n_missing_dirs:
        print("no prediction directory found; nothing evaluated", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
