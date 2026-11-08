#!/usr/bin/env python3
"""Regenerate ``configs/paper_reference_values.json`` from the on-disk text artefacts.

Sources (no manuscript exists on disk; these are the only places the numbers live):

* ``results/baselines/paper_methods_vs_paper_tables_comparison.txt``
    -> ``tab:e0_overall`` (Table V), ``tab:e1_s2t`` (Table VII), ``tab:e2_roundtrip`` (Table VIII)
* ``results/metrics/archived/e0_rschema_exp4_report.txt``
    -> ``e0_rschema_exp4_micro`` (locally reproducible Exp4 micro F1 / mean nGED)
* ``results/baselines/e0_schemabench_papermethods_report.txt``
    -> ``e0_schemabench_fewshot_corrected`` (few_shot rows, corrected parser, zero-scored)

Numbers are copied verbatim (as floats, 3dp / 2dp exactly as printed); nothing is computed.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPARISON = ROOT / "results" / "baselines" / "paper_methods_vs_paper_tables_comparison.txt"
EXP4_REPORT = ROOT / "results" / "metrics" / "archived" / "e0_rschema_exp4_report.txt"
SB_REPORT = ROOT / "results" / "baselines" / "e0_schemabench_papermethods_report.txt"
OUT = ROOT / "configs" / "paper_reference_values.json"

NUM = re.compile(r"^(?:\d+(?:\.\d+)?|n/a)$")


def canon_model(name: str) -> str:
    n = name.lower()
    if "codellama" in n:
        return "codellama13b"
    if "deepseek" in n:
        return "deepseek"
    if "claude" in n:
        return "claude_sonnet_4_6"
    if "gpt" in n:
        return "gpt_5_4_mini"
    if "llama" in n:
        return "llama31"
    raise ValueError(f"unknown model name {name!r}")


def section(text: str, start: str, end: str) -> str:
    i = text.index(start)
    j = text.index(end, i)
    return text[i:j]


def parse_dataset_blocks(block: str, columns: list[str]) -> dict:
    """Parse ``Dataset: X`` blocks; the last ``len(columns)`` tokens of a row are numbers."""
    out: dict[str, dict] = {}
    dataset = None
    for line in block.splitlines():
        m = re.match(r"^Dataset:\s*(.+?)\s*$", line)
        if m:
            dataset = m.group(1)
            out[dataset] = {}
            continue
        if dataset is None or not line.strip() or line.startswith(("Model", "Describer", "---", "===")):
            continue
        toks = line.split()
        if len(toks) <= len(columns) or not all(NUM.match(t) for t in toks[-len(columns):]):
            continue
        name = " ".join(toks[: -len(columns)])
        vals = [None if t == "n/a" else float(t) for t in toks[-len(columns):]]
        out[dataset][canon_model(name)] = {"display_name": name, **dict(zip(columns, vals))}
    return out


def build() -> dict:
    text = COMPARISON.read_text(encoding="utf-8")

    t5 = section(text, "1B. PAPER TABLE V", "1C. E0 COMPARISON")
    e0 = parse_dataset_blocks(t5, ["nged", "halluc", "tables", "attributes", "domain", "entity", "referential"])

    t7 = section(text, "2A. PAPER TABLE VII", "E1 notes")
    e1_cols = [
        "bleu4_basic", "bleu4_detailed", "rougeL_basic", "rougeL_detailed",
        "bertscore_basic", "bertscore_detailed", "scr_basic", "scr_detailed",
    ]
    e1 = parse_dataset_blocks(t7, e1_cols)

    t8 = section(text, "3A. PAPER TABLE VIII", "E2 notes")
    e2_cols = []
    for k in ("nged", "tables", "attributes", "domain", "entity", "referential"):
        e2_cols += [f"{k}_basic", f"{k}_detailed"]
    e2 = parse_dataset_blocks(t8, e2_cols)

    # Exp4 micro report: "codellama13b  518  0  0  0.000  0.733  0.554 0.415 0.217 0.278 0.139"
    exp4: dict[str, dict] = {}
    for line in EXP4_REPORT.read_text(encoding="utf-8").splitlines():
        toks = line.split()
        if len(toks) == 11 and toks[0] in {"codellama13b", "llama31", "deepseek"} and all(NUM.match(t) for t in toks[1:]):
            v = [float(t) for t in toks[1:]]
            exp4[toks[0]] = {
                "evaluated": int(v[0]), "skipped": int(v[1]), "exact_match": int(v[2]),
                "nged": v[4], "tables": v[5], "attributes": v[6], "domain": v[7],
                "entity": v[8], "referential": v[9],
            }

    sb: dict[str, dict] = {}
    pat = re.compile(r"^(CodeLlama|Llama|DeepSeek) few_shot\s+(.*)$")
    for line in SB_REPORT.read_text(encoding="utf-8").splitlines():
        m = pat.match(line)
        if not m:
            continue
        v = [float(t) for t in m.group(2).split()]
        sb[canon_model(m.group(1))] = {
            "evaluated": int(v[0]), "zero_scored": int(v[1]), "nged": v[2], "halluc": v[3],
            "tables": v[4], "attributes": v[5], "domain": v[6], "entity": v[7], "referential": v[8],
        }

    return {
        "_meta": {
            "description": "Published / locally-reproducible reference numbers for SchemaBridge E0-E2.",
            "paper_source": "results/baselines/paper_methods_vs_paper_tables_comparison.txt "
                            "(copied from /data/LLM4DBdesign_PaperMethods/Results/). No ICDE LaTeX manuscript exists on disk.",
            "generated_by": "scripts/build_paper_reference_values.py",
            "tolerance_3dp": 0.0005,
            "tolerance_2dp": 0.005,
            "scales": {
                "bleu4_*": "0-100 (2dp) -> tolerance 0.005",
                "all other metrics": "0-1 (3dp) -> tolerance 0.0005",
            },
            "metric_direction": {
                "lower_is_better": ["nged", "halluc"],
                "higher_is_better": ["tables", "attributes", "domain", "entity", "referential",
                                     "bleu4_*", "rougeL_*", "bertscore_*", "scr_*"],
            },
            "model_keys": {
                "codellama13b": "CodeLlama-13B", "llama31": "Llama-3.1-8B", "deepseek": "DeepSeek-Coder-6.7B",
                "claude_sonnet_4_6": "Claude Sonnet 4.6", "gpt_5_4_mini": "GPT-5.4-mini",
            },
            "notes": [
                "Table VII Enterprise-145 BLEU/ROUGE/BERTScore are 'n/a' in the paper -> stored as null.",
                "tab:e0_overall 'halluc' aggregation is not documented on disk; reproduce_tables marks it BLOCKED.",
            ],
        },
        "tab:e0_overall": {
            "caption": "Table V - E0 Text2Schema from gold NL (paper-reported)",
            "columns": ["nged", "halluc", "tables", "attributes", "domain", "entity", "referential"],
            "datasets": e0,
        },
        "tab:e1_s2t": {
            "caption": "Table VII - E1 Schema2Text, Basic (B) / Detailed (D) describer prompts",
            "columns": e1_cols,
            "datasets": e1,
        },
        "tab:e2_roundtrip": {
            "caption": "Table VIII - E2 round-trip (constructor fixed to GPT-4o-mini)",
            "columns": e2_cols,
            "datasets": e2,
        },
        "e0_rschema_exp4_micro": {
            "caption": "Archived RSchema Exp4 text2schema report (micro F1, mean nGED), corrected parser",
            "source": "results/metrics/archived/e0_rschema_exp4_report.txt",
            "dataset": "RSchema",
            "models": exp4,
        },
        "e0_schemabench_fewshot_corrected": {
            "caption": "SchemaBench PaperMethods few_shot (corrected parser, zero-scored, macro means)",
            "source": "results/baselines/e0_schemabench_papermethods_report.txt",
            "dataset": "SchemaBench",
            "models": sb,
        },
    }


def main() -> int:
    data = build()
    # sanity: expected shapes
    assert set(data["tab:e0_overall"]["datasets"]) == {"RSchema", "SchemaBench"}
    assert all(len(v) == 5 for v in data["tab:e0_overall"]["datasets"].values())
    assert set(data["tab:e1_s2t"]["datasets"]) == {"Enterprise-145", "RSchema", "SchemaBench"}
    assert set(data["tab:e2_roundtrip"]["datasets"]) == {"Enterprise-145", "RSchema", "SchemaBench"}
    assert len(data["e0_rschema_exp4_micro"]["models"]) == 3
    assert len(data["e0_schemabench_fewshot_corrected"]["models"]) == 3
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
