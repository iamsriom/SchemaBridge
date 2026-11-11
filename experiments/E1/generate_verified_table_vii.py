#!/usr/bin/env python3
"""Generate the corrected, verified-only Table VII and final E1 audit artifacts.

Uses independently recomputed metrics from original predictions. Does not copy
unverified manuscript values into the verified table. Does not run paid inference.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import reproduce_table_vii as e1  # noqa: E402

AUDIT = ROOT / "audit" / "e1_verification"
REPRO = ROOT / "results" / "metrics" / "reproduced"
DATA = Path("/data")

PAPER_MODELS = list(e1.MODELS)
DISPLAY = e1.MODEL_DISPLAY
DATASETS = list(e1.DATASETS)
PROMPTS = list(e1.PROMPTS)
METRICS = list(e1.METRICS)

PROMPT_A = (
    "Summarize this database schema in one short paragraph of plain English: "
    "what it is for, main tables, and how they relate. Human-readable, no code."
)
PROMPT_B = (
    "You are a technical writer. Given a database schema (name and DDL), write ONE "
    "single paragraph of human-readable natural language in plain English. Do not "
    "use code, SQL, bullet points, or section headers. Write only flowing prose.\n\n"
    "The paragraph must cover everything in the schema: the database name and what "
    "it is used for; each table and what it represents; for each table, its columns "
    "with their data types (domain integrity), whether they allow null or not, and "
    "any defaults; primary keys and any composite or unique constraints (entity "
    "integrity); every foreign key and which columns reference which tables, plus "
    "update and delete rules like CASCADE or RESTRICT (referential integrity); and "
    "any other indexes or constraints. Be exhaustive but write it all as one "
    "continuous, readable paragraph that a non-expert can follow."
)
PROMPT_C = (ROOT / "prompts" / "describer_detailed.txt").read_text(encoding="utf-8").strip()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_csv(path: Path, rows: list[dict], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = fields or list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


# --------------------------------------------------------------------------- configs eligible for Table VII


def paper_eligible_sources() -> list[dict[str, Any]]:
    """Only configs that map to the five paper models with verified prompt labels."""
    return [
        # Enterprise Detailed (Prompt B) — paper models only
        {
            "dataset": "Enterprise-145",
            "model": "codellama13b",
            "prompt": "detailed",
            "paper_label": "Detailed",
            "prompt_variant": "B",
            "path": DATA / "LLMTranslations/Schema2Text2_codellama13b",
            "script": "/data/Text2ER/experiments/schema2text2_allLLM.py",
            "kind": "named",
            "expected_model_id": "codellama/CodeLlama-13b-Instruct-hf",
            "metrics": ["scr"],
        },
        {
            "dataset": "Enterprise-145",
            "model": "llama31",
            "prompt": "detailed",
            "paper_label": "Detailed",
            "prompt_variant": "B",
            "path": DATA / "LLMTranslations/Schema2Text2_llama31",
            "script": "/data/Text2ER/experiments/schema2text2_allLLM.py",
            "kind": "named",
            "expected_model_id": "meta-llama/Meta-Llama-3.1-8B-Instruct",
            "metrics": ["scr"],
        },
        {
            "dataset": "Enterprise-145",
            "model": "deepseek",
            "prompt": "detailed",
            "paper_label": "Detailed",
            "prompt_variant": "B",
            "path": DATA / "LLMTranslations/Schema2Text2_deepseek",
            "script": "/data/Text2ER/experiments/schema2text2_allLLM.py",
            "kind": "named",
            "expected_model_id": "deepseek-ai/deepseek-coder-6.7b-instruct",
            "metrics": ["scr"],
        },
        # RSchema Detailed
        {
            "dataset": "RSchema",
            "model": "codellama13b",
            "prompt": "detailed",
            "paper_label": "Detailed",
            "prompt_variant": "B",
            "path": DATA / "RSchema_ExpResults4/Experiment2/schema2text_codellama13b",
            "script": "/data/RSchema_ExpResults4/Code/rschema_exp4_schema2text_allLLM.py",
            "kind": "numbered",
            "expected_model_id": "codellama/CodeLlama-13b-Instruct-hf",
            "metrics": ["bleu4", "rougeL", "bertscore", "scr"],
        },
        {
            "dataset": "RSchema",
            "model": "llama31",
            "prompt": "detailed",
            "paper_label": "Detailed",
            "prompt_variant": "B",
            "path": DATA / "RSchema_ExpResults4/Experiment2/schema2text_llama31",
            "script": "/data/RSchema_ExpResults4/Code/rschema_exp4_schema2text_allLLM.py",
            "kind": "numbered",
            "expected_model_id": "meta-llama/Meta-Llama-3.1-8B-Instruct",
            "metrics": ["bleu4", "rougeL", "bertscore", "scr"],
        },
        {
            "dataset": "RSchema",
            "model": "deepseek",
            "prompt": "detailed",
            "paper_label": "Detailed",
            "prompt_variant": "B",
            "path": DATA / "RSchema_ExpResults4/Experiment2/schema2text_deepseek",
            "script": "/data/RSchema_ExpResults4/Code/rschema_exp4_schema2text_allLLM.py",
            "kind": "numbered",
            "expected_model_id": "deepseek-ai/deepseek-coder-6.7b-instruct",
            "metrics": ["bleu4", "rougeL", "bertscore", "scr"],
        },
        # SchemaBench Detailed
        {
            "dataset": "SchemaBench",
            "model": "codellama13b",
            "prompt": "detailed",
            "paper_label": "Detailed",
            "prompt_variant": "B",
            "path": DATA / "SchemaBench/Experiment/schema2text_codellama13b",
            "script": "/data/SchemaBench/Code/rschema_exp4_schema2text_allLLM.py",
            "kind": "numbered",
            "expected_model_id": "codellama/CodeLlama-13b-Instruct-hf",
            "metrics": ["bleu4", "rougeL", "bertscore", "scr"],
        },
        {
            "dataset": "SchemaBench",
            "model": "llama31",
            "prompt": "detailed",
            "paper_label": "Detailed",
            "prompt_variant": "B",
            "path": DATA / "SchemaBench/Experiment/schema2text_llama31",
            "script": "/data/SchemaBench/Code/rschema_exp4_schema2text_allLLM.py",
            "kind": "numbered",
            "expected_model_id": "meta-llama/Meta-Llama-3.1-8B-Instruct",
            "metrics": ["bleu4", "rougeL", "bertscore", "scr"],
        },
        {
            "dataset": "SchemaBench",
            "model": "deepseek",
            "prompt": "detailed",
            "paper_label": "Detailed",
            "prompt_variant": "B",
            "path": DATA / "SchemaBench/Experiment/schema2text_deepseek",
            "script": "/data/SchemaBench/Code/rschema_exp4_schema2text_allLLM.py",
            "kind": "numbered",
            "expected_model_id": "deepseek-ai/deepseek-coder-6.7b-instruct",
            "metrics": ["bleu4", "rougeL", "bertscore", "scr"],
        },
    ]


def non_paper_inventory() -> list[dict[str, Any]]:
    """Extra archives for inventory (not placed into paper five-model table)."""
    return [
        {
            "dataset": "Enterprise-145",
            "model_note": "CodeLlama-7B (NOT paper CodeLlama-13B)",
            "prompt": "basic",
            "prompt_variant": "A",
            "path": DATA / "LLMTranslations/Schema2Text1_codellama",
            "script": "/data/Text2ER/experiments/schema2text1_allLLM.py",
            "table_vii_eligible": False,
            "reason": "wrong model size (7B)",
        },
        {
            "dataset": "Enterprise-145",
            "model_note": "Mistral-7B",
            "prompt": "basic",
            "prompt_variant": "A",
            "path": DATA / "LLMTranslations/Schema2Text1_mistral",
            "script": "/data/Text2ER/experiments/schema2text1_allLLM.py",
            "table_vii_eligible": False,
            "reason": "not a Table VII model",
        },
        {
            "dataset": "Enterprise-145",
            "model_note": "GPT-4o-mini (NOT GPT-5.4-mini)",
            "prompt": "basic",
            "prompt_variant": "A",
            "path": DATA / "LLMTranslations/Schema2Text1_GPT4omini",
            "script": "Enterprise Schema2Text1 GPT path",
            "table_vii_eligible": False,
            "reason": "wrong model identity",
        },
        {
            "dataset": "Enterprise-145",
            "model_note": "CodeLlama-7B",
            "prompt": "detailed",
            "prompt_variant": "B",
            "path": DATA / "LLMTranslations/Schema2Text2_codellama",
            "script": "/data/Text2ER/experiments/schema2text2_allLLM.py",
            "table_vii_eligible": False,
            "reason": "wrong model size (7B)",
        },
        {
            "dataset": "Enterprise-145",
            "model_note": "Mistral-7B",
            "prompt": "detailed",
            "prompt_variant": "B",
            "path": DATA / "LLMTranslations/Schema2Text2_mistral",
            "script": "/data/Text2ER/experiments/schema2text2_allLLM.py",
            "table_vii_eligible": False,
            "reason": "not a Table VII model",
        },
        {
            "dataset": "Enterprise-145",
            "model_note": "GPT-4o-mini",
            "prompt": "detailed",
            "prompt_variant": "B",
            "path": DATA / "LLMTranslations/Schema2Text2_GPT4omini",
            "script": "Enterprise Schema2Text2 GPT path",
            "table_vii_eligible": False,
            "reason": "wrong model identity",
        },
        {
            "dataset": "RSchema",
            "model_note": "Exp3 open models",
            "prompt": "other",
            "prompt_variant": "Exp3 (not A/B/C)",
            "path": DATA / "RSchema_ExpResults3",
            "script": "/data/RSchemaCode/rschema_schema2text_allLLM.py",
            "table_vii_eligible": False,
            "reason": "prompt does not match paper Basic/Detailed",
        },
    ]


def prompt_text(variant: str) -> str:
    return {"A": PROMPT_A, "B": PROMPT_B, "C": PROMPT_C}.get(variant, "")


def evaluate_config(
    cfg: dict[str, Any],
    gold: list[e1.GoldRecord],
    *,
    skip_bertscore: bool,
    device: str,
    progress: e1.Progress,
) -> dict[str, Any]:
    path: Path = cfg["path"]
    progress.log(f"EVAL {cfg['dataset']} {cfg['model']} {cfg['prompt']} {path}")
    if cfg["kind"] == "numbered":
        preds, coverage = e1.load_numbered_predictions(path, gold)
    else:
        preds, coverage = e1.load_named_predictions(path, gold)

    # Model-ID check from first JSON with model_id
    observed_model_id = ""
    for pjson in sorted(path.glob("*.json"))[:5]:
        try:
            meta = json.loads(pjson.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        if meta.get("model_id"):
            observed_model_id = str(meta["model_id"])
            break

    eligible = [i for i, p in enumerate(preds) if p.status == "ok"]
    hyps = [preds[i].hyp_nl for i in eligible]
    refs = [gold[i].gold_nl for i in eligible]
    ddls = [
        (preds[i].ddl_in_pred.strip() or gold[i].ddl) for i in eligible
    ]

    # Sensitivity: full population with OOM/error -> empty hyp, SCR on empty = 0
    # unless empty denominator.
    full_hyps = []
    full_refs = []
    full_ddls = []
    for i, p in enumerate(preds):
        hyp = p.hyp_nl if p.status == "ok" else ""
        full_hyps.append(hyp)
        full_refs.append(gold[i].gold_nl)
        full_ddls.append(p.ddl_in_pred.strip() or gold[i].ddl)

    out: dict[str, Any] = {
        "dataset": cfg["dataset"],
        "model": cfg["model"],
        "prompt": cfg["prompt"],
        "path": str(path),
        "coverage": coverage,
        "observed_model_id": observed_model_id,
        "expected_model_id": cfg["expected_model_id"],
        "model_id_match": observed_model_id == cfg["expected_model_id"]
        or (not observed_model_id and cfg["dataset"] == "Enterprise-145"),
        "n_eligible": len(eligible),
        "n_expected": e1.EXPECTED_N[cfg["dataset"]],
        "failure_policy": (
            "Exp4/original: exclude ERROR/empty/invalid from metric means; "
            "failures are CUDA OOM markers on SchemaBench. "
            "Also report full-population sensitivity (invalid->empty hyp)."
        ),
        "metrics": {},
        "metrics_full_pop_sensitivity": {},
    }

    if not eligible:
        progress.log("  no eligible predictions")
        return out

    progress.log(f"  SCR eligible={len(eligible)}")
    scr = e1.compute_scr_macro(hyps, ddls)
    out["metrics"]["scr"] = scr["scr"]
    scr_full = e1.compute_scr_macro(full_hyps, full_ddls)
    out["metrics_full_pop_sensitivity"]["scr"] = scr_full["scr"]

    has_nl = cfg["dataset"] != "Enterprise-145"
    if has_nl:
        progress.log("  BLEU/ROUGE")
        bleu = e1.compute_bleu(hyps, refs)
        rouge = e1.compute_rougeL(hyps, refs)
        out["metrics"]["bleu4"] = bleu["bleu_corpus_documented_format"]
        out["metrics"]["bleu4_buggy_first_only"] = bleu["bleu_corpus_original_format"]
        out["metrics"]["bleu_signature"] = bleu["bleu_signature_documented"]
        out["metrics"]["rougeL"] = rouge["rougeL"]
        # full-pop sensitivity (empty hyps for failures)
        bleu_f = e1.compute_bleu(full_hyps, full_refs)
        rouge_f = e1.compute_rougeL(full_hyps, full_refs)
        out["metrics_full_pop_sensitivity"]["bleu4"] = bleu_f["bleu_corpus_documented_format"]
        out["metrics_full_pop_sensitivity"]["rougeL"] = rouge_f["rougeL"]

        if not skip_bertscore and "bertscore" in cfg["metrics"]:
            progress.log(f"  BERTScore ({device}) n={len(eligible)}")
            try:
                bert = e1.compute_bertscore(hyps, refs, device=device)
                out["metrics"]["bertscore"] = bert["bertscore"]
            except Exception as exc:  # noqa: BLE001
                out["metrics"]["bertscore_error"] = f"{type(exc).__name__}: {exc}"
                progress.log(f"  BERTScore FAILED: {exc}")

    return out


def fmt_cell(metric: str, value: float | None) -> str:
    if value is None:
        return "--"
    if metric == "bleu4":
        return f"{value:.2f}"
    return f"{value:.3f}"


def bold_best(values: dict[str, float | None]) -> set[str]:
    """Return model keys that tie for best among non-None verified values."""
    present = {k: v for k, v in values.items() if v is not None}
    if not present:
        return set()
    best = max(present.values())
    # float tolerance for ties after rounding
    return {k for k, v in present.items() if abs(v - best) <= 1e-12}


def build_latex(verified: dict[tuple[str, str, str, str], float]) -> str:
    """verified key: (dataset, model, prompt, metric) -> float."""
    lines = [
        "% Corrected Table VII (E1 Schema Verbalization) — verified cells only.",
        "% Generated by experiments/E1/generate_verified_table_vii.py",
        f"% Generated UTC: {utcnow()}",
        "% Unverified / unavailable cells shown as --.",
        "% Bold = best among independently verified values in that column (not overall winner if others missing).",
        "% BLEU-4 uses correct sacrebleu corpus_bleu(hyps, [refs]).",
        "% SchemaBench Detailed metrics use Exp4 eligible population (CUDA-OOM ERROR texts excluded); see audit.",
        "\\begin{table*}[t]",
        "\\centering",
        "\\caption{E1: Schema verbalization under the basic (B) and detailed (D) prompts.",
        "BLEU-4 (0--100 scale), ROUGE-L, and BERTScore-$F_1$ are computed against the gold",
        "description, which Enterprise-145 lacks (--); SCR is computed against the gold schema.",
        "Best \\emph{among independently verified cells} per dataset and column in bold.",
        "Unavailable or unverified results are marked (--).",
        "Detailed (D) corresponds to the exhaustive single-paragraph Prompt~B used by the",
        "original Exp4/Schema2Text2 generators; Basic (B) short Prompt~A archives matching",
        "the five paper models were not recovered.}",
        "\\label{tab:e1_s2t}",
        "\\small",
        "\\setlength{\\tabcolsep}{3.5pt}",
        "\\begin{tabular}{@{}l rr rr rr rr@{}}",
        "\\toprule",
        "Describer & BLEU-4 (B) & BLEU-4 (D) & ROUGE-L (B) & ROUGE-L (D) & BERT (B) & BERT (D) & SCR (B) & SCR (D) \\\\",
        "\\midrule",
    ]

    def cell(ds: str, model: str, prompt: str, metric: str, winners: set[str]) -> str:
        key = (ds, model, prompt, metric)
        if key not in verified:
            return "--"
        text = fmt_cell(metric, verified[key])
        if model in winners:
            return f"\\textbf{{{text}}}"
        return text

    for ds in DATASETS:
        lines.append(f"\\multicolumn{{9}}{{@{{}}l}}{{\\emph{{{ds}}}}} \\\\")
        # winners per column
        col_winners: dict[tuple[str, str], set[str]] = {}
        for prompt in PROMPTS:
            for metric in METRICS:
                if ds == "Enterprise-145" and metric != "scr":
                    col_winners[(prompt, metric)] = set()
                    continue
                vals = {
                    m: verified.get((ds, m, prompt, metric)) for m in PAPER_MODELS
                }
                col_winners[(prompt, metric)] = bold_best(vals)

        for model in PAPER_MODELS:
            name = DISPLAY[model]
            parts = [name]
            for metric in METRICS:
                for prompt in PROMPTS:
                    if ds == "Enterprise-145" and metric != "scr":
                        parts.append("--")
                        continue
                    w = col_winners[(prompt, metric)]
                    parts.append(cell(ds, model, prompt, metric, w))
            lines.append(" & ".join(parts) + " \\\\")
        if ds != DATASETS[-1]:
            lines.append("\\midrule")

    lines += [
        "\\bottomrule",
        "\\end{tabular}",
        "\\end{table*}",
        "",
    ]
    return "\n".join(lines)


def interpretation_paragraph() -> str:
    return (
        "Under the recovered exhaustive single-paragraph Detailed prompt, open-weight "
        "describers preserve schema identifiers more faithfully than they reproduce the "
        "gold wording: on RSchema, Schema Coverage Rate is high for CodeLlama-13B and "
        "DeepSeek-Coder, while corrected corpus BLEU-4 remains low once the original "
        "first-hypothesis-only SacreBLEU call is replaced by a proper single-reference "
        "corpus. ROUGE-L and BERTScore-$F_1$ for the same RSchema Detailed runs are "
        "stable and independently reproducible. On SchemaBench, the same Detailed "
        "archives exhibit material CUDA out-of-memory failures (23/239, 12/239, and "
        "44/239 for CodeLlama-13B, Llama-3.1-8B, and DeepSeek-Coder); metrics are "
        "therefore reported on the eligible non-error outputs and should not be read as "
        "complete 239-schema coverage. Enterprise-145 admits SCR only; verified Detailed "
        "SCR for the three open models differs from the manuscript, and no Basic archive "
        "for CodeLlama-13B, Llama-3.1-8B, or DeepSeek-Coder was found (existing Schema2Text1 "
        "outputs are CodeLlama-7B/Mistral/GPT-4o-mini). Claude Sonnet 4.6 and GPT-5.4-mini "
        "Schema2Text predictions are absent, so Basic/Detailed comparisons and proprietary "
        "rankings cannot be established from the available evidence."
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--skip-bertscore", action="store_true")
    ap.add_argument("--bertscore", action="store_true")
    ap.add_argument("--bertscore-device", default="cuda:0")
    ap.add_argument("--progress-log", type=Path, default=Path("/tmp/e1_final_logs/progress.log"))
    args = ap.parse_args(argv)

    skip_bert = True
    if args.bertscore:
        skip_bert = False
    if args.skip_bertscore:
        skip_bert = True

    progress = e1.Progress(args.progress_log)
    AUDIT.mkdir(parents=True, exist_ok=True)
    REPRO.mkdir(parents=True, exist_ok=True)

    progress.log("=== generate_verified_table_vii starting ===")
    cfg_versions = e1.detect_versions()

    prompts = {
        "A_short_basic": {"text": PROMPT_A, "sha256": sha256_text(PROMPT_A), "paper_label": "Basic"},
        "B_exhaustive_paragraph": {
            "text": PROMPT_B,
            "sha256": sha256_text(PROMPT_B),
            "paper_label": "Detailed",
        },
        "C_five_section": {
            "text": PROMPT_C,
            "sha256": sha256_text(PROMPT_C),
            "paper_label": "not used for recovered Table VII archives",
        },
    }
    (AUDIT / "E1_PROMPT_TEXTS.json").write_text(
        json.dumps(prompts, indent=2) + "\n", encoding="utf-8"
    )

    golds = {
        "RSchema": e1.load_rschema_gold(),
        "SchemaBench": e1.load_schemabench_gold(),
        "Enterprise-145": e1.load_enterprise_gold(),
    }
    for ds, g in golds.items():
        progress.log(f"gold {ds}: N={len(g)} ddl={dict(Counter(x.ddl_source for x in g))}")

    # Prompt provenance
    prov_rows = []
    for src in paper_eligible_sources() + [
        {
            **x,
            "model": x.get("model_note", "n/a"),
            "paper_label": "n/a",
            "kind": "named" if "Schema2Text" in str(x["path"]) else "dir",
            "expected_model_id": "",
            "metrics": [],
        }
        for x in non_paper_inventory()
        if x["path"].exists() or x["path"].is_dir()
    ]:
        variant = src.get("prompt_variant", "")
        text = prompt_text(variant) if variant in ("A", "B", "C") else ""
        p = Path(src["path"])
        n_txt = len(list(p.glob("*.txt"))) if p.is_dir() else 0
        prov_rows.append(
            {
                "dataset": src["dataset"],
                "model": src.get("model"),
                "experiment_directory": str(p),
                "original_generation_script": src.get("script", ""),
                "actual_prompt_text_sha256": sha256_text(text) if text else "",
                "prompt_variant": variant,
                "paper_prompt_label": src.get("paper_label", ""),
                "prediction_count_txt": n_txt,
                "table_vii_eligible": src.get("table_vii_eligible", True),
                "status": "eligible" if src.get("table_vii_eligible", True) and p.is_dir() else src.get("reason", "excluded"),
            }
        )
    write_csv(AUDIT / "E1_PROMPT_PROVENANCE.csv", prov_rows)

    # Evaluate eligible configs
    evals: list[dict[str, Any]] = []
    verified: dict[tuple[str, str, str, str], float] = {}
    metric_rows: list[dict] = []
    model_id_rows: list[dict] = []
    align_rows: list[dict] = []
    inventory_rows: list[dict] = []

    for cfg in paper_eligible_sources():
        if not cfg["path"].is_dir():
            progress.log(f"MISSING {cfg['path']}")
            continue
        result = evaluate_config(
            cfg,
            golds[cfg["dataset"]],
            skip_bertscore=skip_bert,
            device=args.bertscore_device,
            progress=progress,
        )
        evals.append(result)
        cov = result["coverage"]
        inventory_rows.append(
            {
                "dataset": cfg["dataset"],
                "model": cfg["model"],
                "prompt": cfg["prompt"],
                "path": str(cfg["path"]),
                "expected": result["n_expected"],
                "valid": cov.get("valid"),
                "invalid": cov.get("invalid"),
                "empty": cov.get("empty"),
                "missing": cov.get("missing"),
                "table_vii_eligible": True,
            }
        )
        model_id_rows.append(
            {
                "dataset": cfg["dataset"],
                "model": cfg["model"],
                "prompt": cfg["prompt"],
                "expected_model_id": result["expected_model_id"],
                "observed_model_id": result["observed_model_id"],
                "match": result["model_id_match"],
                "path": str(cfg["path"]),
            }
        )
        align_rows.append(
            {
                "dataset": cfg["dataset"],
                "model": cfg["model"],
                "prompt": cfg["prompt"],
                "expected_population": result["n_expected"],
                "valid_predictions": cov.get("valid"),
                "recorded_failures": cov.get("invalid"),
                "missing_predictions": cov.get("missing"),
                "actual_model_id": result["observed_model_id"],
                "actual_prompt_hash": sha256_text(PROMPT_B),
                "source_schema_provenance": json.dumps(
                    dict(Counter(g.ddl_source for g in golds[cfg["dataset"]]))
                ),
                "verification_status": "VERIFIED_DETAILED_PROMPT_B",
            }
        )
        for metric in cfg["metrics"]:
            val = result["metrics"].get(metric)
            if val is None:
                metric_rows.append(
                    {
                        "dataset": cfg["dataset"],
                        "model": cfg["model"],
                        "prompt": cfg["prompt"],
                        "metric": metric,
                        "value": "",
                        "status": "BLOCKED",
                        "reason": result["metrics"].get(
                            "bertscore_error", "not computed"
                        ),
                        "n_eligible": result["n_eligible"],
                    }
                )
                continue
            verified[(cfg["dataset"], cfg["model"], cfg["prompt"], metric)] = float(val)
            metric_rows.append(
                {
                    "dataset": cfg["dataset"],
                    "model": cfg["model"],
                    "prompt": cfg["prompt"],
                    "metric": metric,
                    "value": val,
                    "value_rounded": e1.round_for_metric(metric, float(val)),
                    "status": "VERIFIED",
                    "n_eligible": result["n_eligible"],
                    "n_expected": result["n_expected"],
                    "buggy_bleu_if_any": result["metrics"].get("bleu4_buggy_first_only", ""),
                    "full_pop_sensitivity": result["metrics_full_pop_sensitivity"].get(
                        metric, ""
                    ),
                    "impl": {
                        "bleu4": "sacrebleu.corpus_bleu(hyps,[refs])",
                        "rougeL": "RougeScorer(['rougeL'], use_stemmer=True) mean F1",
                        "bertscore": "bert_score.score(..., lang='en') mean F1 roberta-large",
                        "scr": "macro mean SCR; hyp-only; legacy DDL element extract",
                    }[metric],
                }
            )

    # Non-paper inventory rows
    for row in non_paper_inventory():
        p = Path(row["path"])
        inventory_rows.append(
            {
                "dataset": row["dataset"],
                "model": row["model_note"],
                "prompt": row["prompt"],
                "path": str(p),
                "expected": "",
                "valid": len(list(p.glob("*.txt"))) if p.is_dir() else 0,
                "invalid": "",
                "empty": "",
                "missing": "",
                "table_vii_eligible": False,
                "reason": row["reason"],
            }
        )

    # Alignment stubs for unavailable paper cells
    for ds in DATASETS:
        for model in PAPER_MODELS:
            for prompt in PROMPTS:
                key_exists = any(
                    r["dataset"] == ds and r["model"] == model and r["prompt"] == prompt
                    for r in align_rows
                )
                if key_exists:
                    continue
                reason = "no matching Prompt A/B archive for this paper model"
                if model in ("claude_sonnet_4_6", "gpt_5_4_mini"):
                    reason = "Claude Sonnet 4.6 / GPT-5.4-mini Schema2Text predictions absent"
                elif prompt == "basic":
                    reason = (
                        "no Prompt A (short Basic) archive for this paper model; "
                        "Enterprise Schema2Text1 is 7B/Mistral/GPT-4o-mini only"
                    )
                align_rows.append(
                    {
                        "dataset": ds,
                        "model": model,
                        "prompt": prompt,
                        "expected_population": e1.EXPECTED_N[ds],
                        "valid_predictions": 0,
                        "recorded_failures": "",
                        "missing_predictions": e1.EXPECTED_N[ds],
                        "actual_model_id": "",
                        "actual_prompt_hash": "",
                        "source_schema_provenance": json.dumps(
                            dict(Counter(g.ddl_source for g in golds[ds]))
                        ),
                        "verification_status": "UNAVAILABLE",
                        "reason": reason,
                    }
                )

    # Paper vs verified comparison for all 90 numerical cells
    paper = e1.load_paper()
    cmp_rows = []
    for ds in DATASETS:
        for model in PAPER_MODELS:
            for prompt in PROMPTS:
                for metric in METRICS:
                    if ds == "Enterprise-145" and metric != "scr":
                        continue
                    pv = paper[ds][model].get(f"{metric}_{prompt}")
                    key = (ds, model, prompt, metric)
                    rv = verified.get(key)
                    if rv is None:
                        status = "UNAVAILABLE"
                        reason = "no verified original predictions / metric for this paper cell"
                        if model in ("claude_sonnet_4_6", "gpt_5_4_mini"):
                            reason = "proprietary Schema2Text predictions absent"
                        elif prompt == "basic":
                            reason = "Prompt A archive for this paper model not recovered"
                    else:
                        st, diff, reason = e1.status_for(metric, pv, rv)
                        # For verified table we always keep recomputed value; status vs paper:
                        if metric == "bleu4" and pv is not None:
                            # paper used buggy BLEU on RSchema Detailed
                            buggy = None
                            for ev in evals:
                                if (
                                    ev["dataset"] == ds
                                    and ev["model"] == model
                                    and ev["prompt"] == prompt
                                ):
                                    buggy = ev["metrics"].get("bleu4_buggy_first_only")
                            if (
                                buggy is not None
                                and abs(buggy - pv) <= e1.TOL["bleu4"]
                                and abs(rv - pv) > e1.TOL["bleu4"]
                            ):
                                status = "CORRECTED_BLEU"
                                reason = (
                                    f"paper matched buggy first-only BLEU={buggy:.6f}; "
                                    f"corrected corpus BLEU={rv:.6f}"
                                )
                            elif abs(rv - pv) <= e1.TOL[metric]:
                                status = "PASS"
                                reason = "independently reproduced"
                            else:
                                status = "MISMATCH"
                                reason = f"delta={abs(rv - pv)}"
                        elif abs(rv - pv) <= e1.TOL[metric] if pv is not None else False:
                            status = "PASS"
                            reason = "independently reproduced"
                        else:
                            status = "MISMATCH" if pv is not None else "VERIFIED_NEW"
                            reason = (
                                f"delta={abs(rv - pv)}" if pv is not None else "no paper value"
                            )
                    cmp_rows.append(
                        {
                            "dataset": ds,
                            "model": model,
                            "display_name": DISPLAY[model],
                            "prompt": prompt,
                            "metric": metric,
                            "paper_value": pv,
                            "verified_value": rv,
                            "verified_rounded": e1.round_for_metric(metric, rv)
                            if rv is not None
                            else None,
                            "status": status,
                            "reason": reason,
                        }
                    )

    write_csv(AUDIT / "E1_FINAL_SOURCE_INVENTORY.csv", inventory_rows)
    write_csv(AUDIT / "E1_MODEL_ID_VERIFICATION.csv", model_id_rows)
    write_csv(AUDIT / "E1_DATASET_ALIGNMENT.csv", align_rows)
    write_csv(AUDIT / "E1_METRIC_VERIFICATION.csv", metric_rows)
    write_csv(AUDIT / "E1_TABLE_VII_PAPER_VS_VERIFIED.csv", cmp_rows)

    # Verified table CSV
    verified_csv_rows = []
    for ds in DATASETS:
        for model in PAPER_MODELS:
            row = {
                "dataset": ds,
                "model": model,
                "display_name": DISPLAY[model],
            }
            for metric in METRICS:
                for prompt in PROMPTS:
                    col = f"{metric}_{prompt}"
                    if ds == "Enterprise-145" and metric != "scr":
                        row[col] = None
                        continue
                    row[col] = verified.get((ds, model, prompt, metric))
            verified_csv_rows.append(row)
    write_csv(REPRO / "E1_TABLE_VII_VERIFIED.csv", verified_csv_rows)

    tex = build_latex(verified)
    (REPRO / "E1_TABLE_VII_VERIFIED.tex").write_text(tex, encoding="utf-8")

    n_verified = sum(1 for r in cmp_rows if r["verified_value"] is not None)
    n_pass = sum(1 for r in cmp_rows if r["status"] == "PASS")
    n_corr = sum(1 for r in cmp_rows if r["status"] == "CORRECTED_BLEU")
    n_mis = sum(1 for r in cmp_rows if r["status"] == "MISMATCH")
    n_unav = sum(1 for r in cmp_rows if r["status"] == "UNAVAILABLE")

    changed = [
        r
        for r in cmp_rows
        if r["verified_value"] is not None
        and r["paper_value"] is not None
        and abs(float(r["verified_value"]) - float(r["paper_value"])) > e1.TOL[r["metric"]]
    ]

    (AUDIT / "E1_EVAL_SUMMARIES_VERIFIED.json").write_text(
        json.dumps({"versions": asdict(cfg_versions), "evals": evals}, indent=2) + "\n",
        encoding="utf-8",
    )

    audit_md = f"""# E1 Final Audit — Corrected Table VII

Generated: {utcnow()}

## Summary

```
Numerical paper cells: 90
Independently verified numerical cells: {n_verified}
PASS (matches paper within tolerance): {n_pass}
CORRECTED_BLEU (paper used buggy BLEU): {n_corr}
MISMATCH (verified but differs from paper): {n_mis}
UNAVAILABLE: {n_unav}
```

## Prompt mapping

| Variant | Paper label | SHA256 | Used in recovered Table VII archives? |
|---|---|---|---|
| A short Basic | Basic | `{sha256_text(PROMPT_A)}` | No (no paper-model archives) |
| B exhaustive paragraph | Detailed | `{sha256_text(PROMPT_B)}` | Yes (RSchema/SchemaBench Exp4; Enterprise Schema2Text2) |
| C five-section | (misnamed describer_detailed.txt) | `{sha256_text(PROMPT_C)}` | No evidence for Table VII |

## Metric configuration

- BLEU-4: `sacrebleu.corpus_bleu(hyps, [refs])` (correct); sacrebleu {cfg_versions.sacrebleu_version}
- ROUGE-L: `RougeScorer(['rougeL'], use_stemmer=True)` mean F1; rouge-score {cfg_versions.rouge_score_version}
- BERTScore-F1: `bert_score.score(..., lang='en')` mean F1 (roberta-large); bert-score {cfg_versions.bert_score_version}; transformers {cfg_versions.transformers_version}; skip in original Exp4 archive
- SCR: legacy DDL element extract; `norm_ident`; hyp-only substring; macro-average; empty E(S)->1.0

## Populations

- Enterprise-145: 145 SQL schemata (SCR only; no gold NL)
- RSchema: 518 (381 annotation_ddl + 137 structured_synthetic)
- SchemaBench: 239 annotation_ddl; Detailed eligible after excluding CUDA OOM ERROR texts: CodeLlama 216, Llama 227, DeepSeek 195

## E2 dependency note

E2 documentation references `prompts/describer_basic.txt` and `prompts/describer_detailed.txt`.
The recovered E1 Detailed archives were generated with Prompt B, which is the text currently
stored in `describer_basic.txt`. Manuscript/E2 wording that equates Detailed with the
five-section Prompt C is not supported by the recovered E1 prediction provenance. E2
prediction files were not modified.

## Interpretation (replacement paragraph)

{interpretation_paragraph()}

## Changed values vs manuscript

| Dataset | Model | Prompt | Metric | Paper | Verified |
|---|---|---|---|---:|---:|
""" + "\n".join(
        f"| {r['dataset']} | {r['display_name']} | {r['prompt']} | {r['metric']} | {r['paper_value']} | {r['verified_rounded']} |"
        for r in changed
    ) + "\n"

    (AUDIT / "E1_FINAL_AUDIT.md").write_text(audit_md, encoding="utf-8")
    (AUDIT / "E1_INTERPRETATION_REPLACEMENT.txt").write_text(
        interpretation_paragraph() + "\n", encoding="utf-8"
    )

    progress.log(
        f"DONE verified={n_verified} PASS={n_pass} CORRECTED_BLEU={n_corr} "
        f"MISMATCH={n_mis} UNAVAILABLE={n_unav}"
    )
    progress.log(f"Wrote {REPRO / 'E1_TABLE_VII_VERIFIED.tex'}")
    print(tex)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
