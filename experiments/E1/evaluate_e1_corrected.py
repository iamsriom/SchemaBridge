#!/usr/bin/env python3
"""Evaluate e1_corrected predictions: full-population (primary) + success-only."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import reproduce_table_vii as e1  # noqa: E402
import run_e1_corrected_gpu as runner  # noqa: E402

OUT_ROOT = ROOT / "results" / "predictions" / "e1_corrected"
AUDIT = ROOT / "audit" / "e1_verification" / "full_gpu_run"
REPRO = ROOT / "results" / "metrics" / "reproduced"
MODELS = ["codellama13b", "llama31", "deepseek"]
DISPLAY = {
    "codellama13b": "CodeLlama-13B",
    "llama31": "Llama-3.1-8B",
    "deepseek": "DeepSeek-Coder",
}


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_preds(dataset: str, model: str, records: list[dict]) -> list[dict]:
    out_dir = runner.out_dir_for(dataset, model)
    rows = []
    for rec in records:
        txt, js = runner.record_paths(out_dir, rec["eval_index"])
        meta = {}
        if js.is_file():
            meta = json.loads(js.read_text(encoding="utf-8"))
        status = meta.get("generation_status")
        hyp = (meta.get("generated_description") or "").strip()
        if not hyp and txt.is_file():
            hyp = runner.sanitize_nl_text(txt.read_text(encoding="utf-8", errors="replace"))
        ok, reason = runner.validate_nl(hyp)
        accounted = js.is_file()
        rows.append(
            {
                **rec,
                "hyp": hyp if ok else "",
                "success": ok,
                "accounted": accounted,
                "generation_status": status,
                "error_type": meta.get("error_type"),
                "model_id": meta.get("model_id"),
                "prompt_hash": meta.get("prompt_hash"),
                "source_ddl_hash": meta.get("source_ddl_hash"),
            }
        )
    return rows


def metrics_for(hyps: list[str], refs: list[str], ddls: list[str], *, skip_bert: bool, device: str):
    out = {}
    bleu = e1.compute_bleu(hyps, refs)
    out["bleu4"] = bleu["bleu_corpus_documented_format"]
    out["bleu_buggy"] = bleu["bleu_corpus_original_format"]
    out["bleu_signature"] = bleu["bleu_signature_documented"]
    out["rougeL"] = e1.compute_rougeL(hyps, refs)["rougeL"]
    # SCR: failed/empty hyp => 0 for nonempty schema
    scrs = []
    for hyp, ddl in zip(hyps, ddls):
        row = e1.schema_coverage_rate(ddl, hyp)
        if row["empty_denominator"]:
            scrs.append(1.0)
        elif not hyp:
            scrs.append(0.0)
        else:
            scrs.append(float(row["coverage"]))
    out["scr"] = sum(scrs) / len(scrs) if scrs else float("nan")
    if not skip_bert:
        # BERTScore: compute only on non-empty; assign 0 to empties; preserve order
        idx_nonempty = [i for i, h in enumerate(hyps) if h.strip()]
        scores = [0.0] * len(hyps)
        if idx_nonempty:
            sub_h = [hyps[i] for i in idx_nonempty]
            sub_r = [refs[i] for i in idx_nonempty]
            import bert_score

            _P, _R, F1 = bert_score.score(
                sub_h, sub_r, lang="en", verbose=False, batch_size=8, device=device
            )
            for j, i in enumerate(idx_nonempty):
                scores[i] = float(F1[j])
        out["bertscore"] = sum(scores) / len(scores) if scores else float("nan")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-bertscore", action="store_true")
    ap.add_argument("--bertscore-device", default="cuda:0")
    args = ap.parse_args()
    skip_bert = args.skip_bertscore

    AUDIT.mkdir(parents=True, exist_ok=True)
    REPRO.mkdir(parents=True, exist_ok=True)

    rs = runner.build_rschema_381()
    sb = runner.build_schemabench_239()
    populations = {"RSchema": rs, "SchemaBench": sb}

    coverage_rows = []
    full_rows = []
    success_rows = []
    failures = []

    for dataset, records in populations.items():
        for model in MODELS:
            preds = load_preds(dataset, model, records)
            n = len(preds)
            n_ok = sum(1 for p in preds if p["success"])
            n_fail = n - n_ok
            n_acc = sum(1 for p in preds if p["accounted"])
            coverage_rows.append(
                {
                    "dataset": dataset,
                    "model": model,
                    "expected": n,
                    "accounted": n_acc,
                    "valid": n_ok,
                    "failed": n_fail,
                    "failure_rate": round(n_fail / n, 4) if n else 0,
                    "missing_files": n - n_acc,
                }
            )
            for p in preds:
                if not p["success"]:
                    failures.append(
                        {
                            "dataset": dataset,
                            "model": model,
                            "schema_id": p["schema_id"],
                            "eval_index": p["eval_index"],
                            "error_type": p.get("error_type") or "MISSING_OR_INVALID",
                            "generation_status": p.get("generation_status"),
                            "accounted": p["accounted"],
                        }
                    )

            # Full population
            hyps = [p["hyp"] for p in preds]
            refs = [p["gold_nl"] for p in preds]
            ddls = [p["ddl"] for p in preds]
            print(f"FULL {dataset} {model} N={n} ok={n_ok}", flush=True)
            m = metrics_for(hyps, refs, ddls, skip_bert=skip_bert, device=args.bertscore_device)
            full_rows.append(
                {
                    "dataset": dataset,
                    "model": model,
                    "display_name": DISPLAY[model],
                    "N": n,
                    "successful": n_ok,
                    "failed": n_fail,
                    **{k: m.get(k) for k in ("bleu4", "rougeL", "bertscore", "scr")},
                    "bleu_signature": m.get("bleu_signature"),
                }
            )

            # Success-only
            ok_preds = [p for p in preds if p["success"]]
            if ok_preds:
                print(f"SUCCESS-ONLY {dataset} {model} N={len(ok_preds)}", flush=True)
                ms = metrics_for(
                    [p["hyp"] for p in ok_preds],
                    [p["gold_nl"] for p in ok_preds],
                    [p["ddl"] for p in ok_preds],
                    skip_bert=skip_bert,
                    device=args.bertscore_device,
                )
            else:
                ms = {"bleu4": None, "rougeL": None, "bertscore": None, "scr": None}
            success_rows.append(
                {
                    "dataset": dataset,
                    "model": model,
                    "display_name": DISPLAY[model],
                    "N": len(ok_preds),
                    "successful": len(ok_preds),
                    "failed": 0,
                    **{k: ms.get(k) for k in ("bleu4", "rougeL", "bertscore", "scr")},
                }
            )

    def write_csv(path: Path, rows: list[dict]):
        if not rows:
            path.write_text("", encoding="utf-8")
            return
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            for r in rows:
                w.writerow(r)

    write_csv(AUDIT / "PREDICTION_COVERAGE.csv", coverage_rows)
    write_csv(AUDIT / "FINAL_FAILURES.csv", failures)
    write_csv(AUDIT / "E1_FULL_POPULATION_METRICS.csv", full_rows)
    write_csv(AUDIT / "E1_SUCCESS_ONLY_METRICS.csv", success_rows)
    write_csv(REPRO / "E1_DETAILED_SUCCESS_ONLY.csv", success_rows)

    # Split CSVs
    write_csv(
        REPRO / "E1_RSCHEMA381_DETAILED.csv",
        [r for r in full_rows if r["dataset"] == "RSchema"],
    )
    write_csv(
        REPRO / "E1_SCHEMABENCH239_DETAILED.csv",
        [r for r in full_rows if r["dataset"] == "SchemaBench"],
    )

    def fmt(metric: str, v):
        if v is None:
            return "--"
        return f"{v:.2f}" if metric == "bleu4" else f"{v:.3f}"

    # LaTeX detailed full-pop
    lines = [
        "% E1 Detailed (Prompt B) — full-population primary results",
        f"% Generated {utcnow()}",
        "% RSchema N=381 genuine DDL only; SchemaBench N=239; failures scored as empty hyp.",
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{E1 Detailed (Prompt~B) full-population metrics. Failed generations scored as empty hypotheses.}",
        "\\label{tab:e1_detailed_fullpop}",
        "\\small",
        "\\begin{tabular}{@{}l l r r r r r r r@{}}",
        "\\toprule",
        "Dataset & Model & N & OK & Fail & BLEU-4 & ROUGE-L & BERT & SCR \\\\",
        "\\midrule",
    ]
    for r in full_rows:
        lines.append(
            f"{r['dataset']} & {r['display_name']} & {r['N']} & {r['successful']} & {r['failed']} & "
            f"{fmt('bleu4', r.get('bleu4'))} & {fmt('rougeL', r.get('rougeL'))} & "
            f"{fmt('bertscore', r.get('bertscore'))} & {fmt('scr', r.get('scr'))} \\\\"
        )
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
    (REPRO / "E1_DETAILED_FULL_POPULATION.tex").write_text("\n".join(lines), encoding="utf-8")

    # Table VII corrected (Detailed columns only filled for open models)
    paper = e1.load_paper()
    t7 = [
        "% Corrected Table VII — verified Detailed open-weight cells (full population).",
        "% Basic and proprietary cells remain --.",
        f"% Generated {utcnow()}",
        "\\begin{table*}[t]",
        "\\centering",
        "\\caption{E1 Schema verbalization (corrected). Detailed (D) = Prompt~B. "
        "RSchema uses N=381 genuine DDL only; SchemaBench N=239. "
        "Failed generations included as empty hypotheses. Basic (B) unavailable.}",
        "\\label{tab:e1_s2t}",
        "\\small",
        "\\setlength{\\tabcolsep}{3.5pt}",
        "\\begin{tabular}{@{}l rr rr rr rr@{}}",
        "\\toprule",
        "Describer & BLEU-4 (B) & BLEU-4 (D) & ROUGE-L (B) & ROUGE-L (D) & BERT (B) & BERT (D) & SCR (B) & SCR (D) \\\\",
        "\\midrule",
    ]

    by = {(r["dataset"], r["model"]): r for r in full_rows}

    def bold_best(vals: dict[str, float | None]) -> set[str]:
        present = {k: v for k, v in vals.items() if v is not None}
        if not present:
            return set()
        best = max(present.values())
        return {k for k, v in present.items() if abs(v - best) < 1e-12}

    for ds, label in [
        ("Enterprise-145", "Enterprise-145"),
        ("RSchema", "RSchema"),
        ("SchemaBench", "SchemaBench"),
    ]:
        t7.append(f"\\multicolumn{{9}}{{@{{}}l}}{{\\emph{{{label}}}}} \\\\")
        winners: dict[str, set[str]] = {}
        if ds in ("RSchema", "SchemaBench"):
            for metric in ("bleu4", "rougeL", "bertscore", "scr"):
                winners[metric] = bold_best({m: by[(ds, m)].get(metric) for m in MODELS})
        for model in list(e1.MODELS):
            name = e1.MODEL_DISPLAY[model]
            if ds == "Enterprise-145" or model not in MODELS:
                t7.append(f"{name} & -- & -- & -- & -- & -- & -- & -- & -- \\\\")
                continue
            r = by[(ds, model)]
            row_cells = [name]
            for metric in ("bleu4", "rougeL", "bertscore", "scr"):
                row_cells.append("--")  # Basic unavailable
                text = fmt(metric, r.get(metric))
                if model in winners.get(metric, set()):
                    text = f"\\textbf{{{text}}}"
                row_cells.append(text)
            t7.append(" & ".join(row_cells) + " \\\\")
        if ds != "SchemaBench":
            t7.append("\\midrule")
    t7 += ["\\bottomrule", "\\end{tabular}", "\\end{table*}", ""]
    (REPRO / "E1_TABLE_VII_CORRECTED.tex").write_text("\n".join(t7), encoding="utf-8")

    # Final report
    report = [
        "# E1 Full GPU Corrected Run — Final Report",
        "",
        f"Generated: {utcnow()}",
        "",
        "## Coverage",
        "",
        "```",
    ]
    for r in coverage_rows:
        report.append(
            f"{r['dataset']:12} {r['model']:14} expected={r['expected']} accounted={r['accounted']} "
            f"valid={r['valid']} failed={r['failed']} missing={r['missing_files']}"
        )
    report += ["```", "", "## Full-population metrics", "", "```"]
    for r in full_rows:
        report.append(
            f"{r['dataset']:12} {r['display_name']:16} N={r['N']} ok={r['successful']} "
            f"BLEU={r.get('bleu4')} ROUGE={r.get('rougeL')} BERT={r.get('bertscore')} SCR={r.get('scr')}"
        )
    report += ["```", ""]
    (AUDIT / "E1_FINAL_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("DONE", dict(Counter((r["dataset"], r["missing_files"] == 0) for r in coverage_rows)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
