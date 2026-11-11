#!/usr/bin/env python3
"""
Combine Exp3 (direct Text2Schema) evaluation results:
  RSchema (518)       — RSchema_ExpResults4/Experiments/Results
  SchemaBench (239)   — Text2ER/SchemaBench/Experiment2/Results

Outputs: A_Final_Result/Exp3/exp3_combined_results.txt
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

DATA_ROOT = Path("/data")
OUT_DIR = DATA_ROOT / "A_Final_Result" / "Exp3"

DATASETS = {
    "rschema": {
        "label": "RSchema",
        "n": 518,
        "json": DATA_ROOT / "RSchema_ExpResults4/Experiments/Results/text2schema_exp4_evaluation.json",
        "txt": DATA_ROOT / "RSchema_ExpResults4/Experiments/Results/text2schema_exp4_report.txt",
    },
    "schemabench": {
        "label": "SchemaBench",
        "n": 239,
        "json": DATA_ROOT / "Text2ER/SchemaBench/Experiment2/Results/text2schema_exp4_evaluation.json",
        "txt": DATA_ROOT / "Text2ER/SchemaBench/Experiment2/Results/text2schema_exp4_report.txt",
    },
}

LLMS = ("codellama13b", "llama31", "deepseek", "sonnet46", "gpt54mini")

LLM_LABEL = {
    "codellama13b": "CodeLlama-13B",
    "llama31": "Llama-3.1",
    "deepseek": "DeepSeek",
    "sonnet46": "Claude Sonnet 4.6",
    "gpt54mini": "GPT-5.4-mini",
}

METRICS_SECTION = """
Direct Text2Schema (gold NL → schema vs gold DDL/metadata):
  Tbl/Attr/Dom/Ent/Ref F1 — micro-aggregate Precision/Recall/F1 over five structural dimensions
  Hall.Rate — mean hallucination rate across dimensions: (Recreated − Matched) / Recreated
  nGED      — normalized graph edit distance on tables, columns, FK edges (lower is better)
  Exact Match — (SchemaBench only) per-schema boolean: all five elements perfectly match gold counts
""".strip()

CLASSIFICATION_RULES = """
Schema classification (unified across datasets):
  Size (structural scale):
    small  = table_count ≤ 5 AND column_count ≤ 50
    medium = not small AND table_count ≤ 15 AND column_count ≤ 150
    large  = everything else
  Content complexity (constraint richness, orthogonal to size):
    content_score = 2*min(fk_count,10) + 3*composite_fk_count + min(unique_count,5) + max(0, cols_per_table-10)/5
    easy   = content_score < 4
    medium = 4 ≤ content_score < 10
    hard   = content_score ≥ 10
""".strip()


def _fmt(v: float | None, w: int = 8, decimals: int = 4) -> str:
    if v is None:
        return "n/a".rjust(w)
    return f"{v:.{decimals}f}".rjust(w)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_entries(data: dict) -> list[dict]:
    items = data.get("llms") or []
    out: list[dict] = []
    for item in items:
        llm = item.get("llm")
        fe = item.get("five_elements") or {}
        hall = [fe.get(k, {}).get("hallucination_rate", 0.0) for k in ("tables", "attributes", "domain", "entity", "referential")]
        mean_hall = sum(hall) / len(hall) if hall else 0.0
        out.append(
            {
                "llm": llm,
                "n": item.get("total_schemas"),
                "nged": item.get("mean_normalized_graph_edit_distance"),
                "exact_match": item.get("exact_match_count"),
                "hall": mean_hall,
                "tbl_f1": fe.get("tables", {}).get("f1"),
                "attr_f1": fe.get("attributes", {}).get("f1"),
                "dom_f1": fe.get("domain", {}).get("f1"),
                "ent_f1": fe.get("entity", {}).get("f1"),
                "ref_f1": fe.get("referential", {}).get("f1"),
            }
        )
    return out


def extract_report_body(txt_path: Path) -> str:
    if not txt_path.is_file():
        return f"[Source report not found: {txt_path}]\n"
    text = txt_path.read_text(encoding="utf-8")
    markers = ("SUMMARY BY LLM", "PART 1", "====", "----")
    start = 0
    for marker in markers:
        idx = text.find(marker)
        if idx != -1:
            start = idx
            break
    return text[start:].rstrip() + "\n"


def build_cross_dataset_table(all_t2s: dict[str, list[dict]]) -> list[str]:
    lines: list[str] = []
    lines.append("TABLE 1 — Direct Text2Schema overall (all datasets × LLMs)")
    lines.append("-" * 120)
    hdr = (
        f"{'Dataset':<14} {'LLM':<18} {'n':>5} "
        f"{'nGED':>8} {'Hall':>8} {'Tbl':>7} {'Attr':>7} {'Dom':>7} {'Ent':>7} {'Ref':>7}"
    )
    lines.append(hdr)
    lines.append("-" * len(hdr))
    by_llm: dict[str, list[dict]] = {llm: [] for llm in LLMS}

    for ds_key, entries in all_t2s.items():
        cfg = DATASETS[ds_key]
        by_llm_ds = {e["llm"]: e for e in entries}
        for llm in LLMS:
            e = by_llm_ds.get(llm)
            if not e:
                continue
            by_llm[llm].append(e)
            lines.append(
                f"{cfg['label']:<14} {LLM_LABEL.get(llm, llm):<18} {e['n']:>5} "
                f"{_fmt(e['nged'])} {_fmt(e['hall'])} "
                f"{_fmt(e['tbl_f1'], 7, 3)} {_fmt(e['attr_f1'], 7, 3)} "
                f"{_fmt(e['dom_f1'], 7, 3)} {_fmt(e['ent_f1'], 7, 3)} "
                f"{_fmt(e['ref_f1'], 7, 3)}"
            )

    lines.append("")
    lines.append("Macro-average across datasets (unweighted mean per LLM):")
    lines.append("-" * 120)
    lines.append(
        f"{'LLM':<18} {'nGED':>8} {'Hall':>8} {'Tbl':>7} {'Attr':>7} {'Dom':>7} {'Ent':>7} {'Ref':>7}"
    )
    lines.append("-" * 70)
    for llm in LLMS:
        rows = by_llm.get(llm) or []
        if not rows:
            continue

        def avg(key: str) -> float:
            vals = [r[key] for r in rows if r.get(key) is not None]
            return sum(vals) / len(vals) if vals else 0.0

        lines.append(
            f"{LLM_LABEL.get(llm, llm):<18} "
            f"{_fmt(avg('nged'))} {_fmt(avg('hall'))} "
            f"{_fmt(avg('tbl_f1'), 7, 3)} {_fmt(avg('attr_f1'), 7, 3)} "
            f"{_fmt(avg('dom_f1'), 7, 3)} {_fmt(avg('ent_f1'), 7, 3)} "
            f"{_fmt(avg('ref_f1'), 7, 3)}"
        )
    lines.append("")
    return lines


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    all_t2s: dict[str, list[dict]] = {}
    for ds_key, cfg in DATASETS.items():
        if cfg["json"].is_file():
            all_t2s[ds_key] = normalize_entries(load_json(cfg["json"]))

    lines: list[str] = []
    lines.append("Experiment 3 — Combined Results (RSchema + SchemaBench, Direct Text2Schema)")
    lines.append("=" * 120)
    lines.append(f"Generated: {ts}")
    lines.append(f"Output: {OUT_DIR / 'exp3_combined_results.txt'}")
    lines.append("")
    lines.append("Gold datasets:")
    for cfg in DATASETS.values():
        lines.append(f"  • {cfg['label']}  (n={cfg['n']})")
    lines.append(f"LLMs: {', '.join(LLM_LABEL[llm] for llm in LLMS)}")
    lines.append("")
    lines.append("Task: Direct Text2Schema — gold natural language → LLM-generated schema vs gold DDL/metadata")
    lines.append("")
    lines.append("METRICS")
    lines.append("-" * 120)
    lines.append(METRICS_SECTION)
    lines.append("")
    lines.append("CLASSIFICATION")
    lines.append("-" * 120)
    lines.append(CLASSIFICATION_RULES)
    lines.append("")
    lines.append("Source files:")
    for cfg in DATASETS.values():
        lines.append(f"  {cfg['label']:<14} → {cfg['txt']}")
    lines.append("")
    lines.append("=" * 120)
    lines.append("PART I — CROSS-DATASET SUMMARY")
    lines.append("=" * 120)
    lines.append("")
    lines.extend(build_cross_dataset_table(all_t2s))

    roman = ("II", "III")
    for i, (ds_key, cfg) in enumerate(DATASETS.items()):
        lines.append("")
        lines.append("=" * 120)
        lines.append(f"PART {roman[i]} — {cfg['label'].upper()} (n={cfg['n']})")
        lines.append("=" * 120)
        lines.append(f"Source: {cfg['txt']}")
        lines.append("")
        lines.append(extract_report_body(cfg["txt"]))

    lines.append("")
    lines.append("=" * 120)
    lines.append("End of combined report.")
    lines.append("=" * 120)

    out_path = OUT_DIR / "exp3_combined_results.txt"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_path} ({out_path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
