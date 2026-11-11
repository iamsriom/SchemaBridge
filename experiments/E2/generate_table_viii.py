#!/usr/bin/env python3
"""Generate ``tab:e2_roundtrip`` LaTeX from PRIMARY full-precision metrics.

Reads ``results/metrics/reproduced/E2_AUDIT/metrics/full_precision_primary.json``
(or ``--metrics``) and writes a complete table* environment with three-decimal
values and automatic best-value bolding per dataset × prompt × metric column.

Tie rule: values equal after rounding to three decimals are all bold.
nGED: lower is better. Structural F1: higher is better.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_METRICS = ROOT / "results/metrics/reproduced/E2_AUDIT/metrics/full_precision_primary.json"
DEFAULT_OUT = ROOT / "results/metrics/reproduced/E2_AUDIT/latex/tab_e2_roundtrip_verified.tex"

ORDER_DS = ["Enterprise-145", "RSchema", "SchemaBench"]
ORDER_M = [
    ("codellama13b", "CodeLlama-13B"),
    ("llama31", "Llama-3.1-8B"),
    ("deepseek", "DeepSeek-Coder"),
    ("sonnet46", "Claude Sonnet 4.6"),
    ("gpt54mini", "GPT-5.4-mini"),
]
METRICS = [
    ("nged", "mean_nged", False),
    ("tables", "tables_f1", True),
    ("attributes", "attributes_f1", True),
    ("domain", "domain_f1", True),
    ("entity", "entity_f1", True),
    ("referential", "referential_f1", True),
]


def r3(x: float) -> float:
    return round(float(x) + 1e-12, 3)


def load_vals(path: Path) -> dict:
    rows = json.loads(path.read_text())
    out = {}
    for r in rows:
        if r.get("population_label") not in (
            "enterprise_145",
            "schemabench_239",
            "genuine_ddl_381",
            "Enterprise-145",
            "SchemaBench",
            "RSchema",
        ) and r.get("population") not in (145, 239, 381):
            # Keep PRIMARY rows only
            if r.get("population_label") not in (
                "enterprise_145",
                "schemabench_239",
                "genuine_ddl_381",
            ):
                continue
        key = (r["dataset"], r["model"], r["prompt"])
        out[key] = r
    # Prefer explicit PRIMARY labels when duplicates exist
    primary = {
        (r["dataset"], r["model"], r["prompt"]): r
        for r in rows
        if r.get("population_label")
        in ("enterprise_145", "schemabench_239", "genuine_ddl_381")
    }
    return primary or out


def is_best(vals, ds, prompt, metric_key, model, higher: bool) -> bool:
    v = r3(vals[(ds, model, prompt)][metric_key])
    peers = [r3(vals[(ds, m, prompt)][metric_key]) for m, _ in ORDER_M]
    best = max(peers) if higher else min(peers)
    return v == best


def fmt(vals, ds, model, prompt, metric_key, higher: bool) -> str:
    v = r3(vals[(ds, model, prompt)][metric_key])
    s = f"{v:.3f}"
    if is_best(vals, ds, prompt, metric_key, model, higher):
        return f"\\textbf{{{s}}}"
    return s


def render(vals: dict) -> str:
    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\small",
        r"\setlength{\tabcolsep}{3.5pt}",
        r"\renewcommand{\arraystretch}{1.0}",
        r"\caption{E2 Round-Trip Preservation (Text2Schema). Constructor fixed to GPT-4o-mini. Basic (B) vs Detailed (D) describer prompts. nGED lower is better; structural F1 higher is better. Populations: Enterprise-145 ($N{=}145$), RSchema genuine DDL ($N{=}381$), SchemaBench ($N{=}239$). Failed/unparseable reconstructions scored as F1${=}0$, nGED${=}1$.}",
        r"\label{tab:e2_roundtrip}",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{llcccccccccccc}",
        r"\toprule",
        r" &  & \multicolumn{2}{c}{nGED $\downarrow$} & \multicolumn{2}{c}{Tables F1} & \multicolumn{2}{c}{Attributes F1} & \multicolumn{2}{c}{Domain F1} & \multicolumn{2}{c}{Entity F1} & \multicolumn{2}{c}{Referential F1} \\",
        r"\cmidrule(lr){3-4}\cmidrule(lr){5-6}\cmidrule(lr){7-8}\cmidrule(lr){9-10}\cmidrule(lr){11-12}\cmidrule(lr){13-14}",
        r"Dataset & Describer & B & D & B & D & B & D & B & D & B & D & B & D \\",
        r"\midrule",
    ]
    for ds in ORDER_DS:
        for i, (m, disp) in enumerate(ORDER_M):
            left = (
                f"\\multirow{{5}}{{*}}{{{ds}}} & {disp}"
                if i == 0
                else f" & {disp}"
            )
            cells = []
            for _pfx, key, higher in METRICS:
                for prompt in ("basic", "detailed"):
                    cells.append(fmt(vals, ds, m, prompt, key, higher))
            lines.append(left + " & " + " & ".join(cells) + r" \\")
        if ds != ORDER_DS[-1]:
            lines.append(r"\midrule")
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}%",
            r"}",
            r"\end{table*}",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--metrics", type=Path, default=DEFAULT_METRICS)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    vals = load_vals(args.metrics)
    expected = 3 * 5 * 2
    if len(vals) != expected:
        raise SystemExit(f"expected {expected} PRIMARY groups, found {len(vals)}")
    tex = render(vals)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(tex)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
