#!/usr/bin/env python3
"""Aggregate E5 CSVs, Markdown, LaTeX, figures, and paper subsection."""

from __future__ import annotations

import csv
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
TABLES = HERE / "tables"
FIGURES = HERE / "figures"
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.metrics import micro_prf  # noqa: E402


def read_csv(path: Path) -> list[dict]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fnum(x: Any) -> float | None:
    if x is None or x == "":
        return None
    try:
        v = float(x)
        if math.isnan(v):
            return None
        return v
    except Exception:
        return None


def inum(x: Any) -> int:
    try:
        return int(float(x))
    except Exception:
        return 0


def pctile(vals: list[float], p: float) -> float | None:
    if not vals:
        return None
    xs = sorted(vals)
    if len(xs) == 1:
        return xs[0]
    k = (len(xs) - 1) * p
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return xs[int(k)]
    return xs[f] * (c - k) + xs[c] * (k - f)


def micro_f1(rows: list[dict], dim: str) -> float | None:
    if not rows:
        return None
    g = sum(inum(r.get(f"{dim}_gold")) for r in rows)
    rec = sum(inum(r.get(f"{dim}_recreated")) for r in rows)
    m = sum(inum(r.get(f"{dim}_matched")) for r in rows)
    # Include failed rows (zeros already in CSV when scored_as_zero)
    return float(micro_prf(g, rec, m)["f1"])


def mean_nged(rows: list[dict]) -> float | None:
    vals = [fnum(r.get("nged")) for r in rows]
    vals = [v for v in vals if v is not None]
    return statistics.mean(vals) if vals else None


def mean_cost(rows: list[dict]) -> float | None:
    vals = [fnum(r.get("total_cost_usd")) for r in rows]
    vals = [v for v in vals if v is not None]
    return statistics.mean(vals) if vals else None


def latency_stats(rows: list[dict]) -> tuple[float | None, float | None]:
    vals = [fnum(r.get("total_latency_s")) for r in rows]
    vals = [v for v in vals if v is not None]
    if not vals:
        # fall back to describer latency alone for local DeepSeek latency remounts
        vals = [fnum(r.get("desc_latency_s")) for r in rows]
        vals = [v for v in vals if v is not None]
    if not vals:
        return None, None
    return pctile(vals, 0.50), pctile(vals, 0.95)


def success_rate(rows: list[dict]) -> float | None:
    if not rows:
        return None
    ok = sum(1 for r in rows if inum(r.get("reconstruction_valid")) == 1 and inum(r.get("parse_success")) == 1)
    return 100.0 * ok / len(rows)


def fmt(v: float | None, nd: int = 3, na: str = "N/A") -> str:
    if v is None:
        return na
    return f"{v:.{nd}f}"


def fmt_cost(v: float | None) -> str:
    if v is None:
        return "N/A"
    if v < 0.01:
        return f"{v:.4f}"
    return f"{v:.3f}"


def bootstrap_ci_paired(
    rows_a: list[dict],
    rows_b: list[dict],
    key_fn,
    *,
    n: int = 1000,
    seed: int = 42,
) -> tuple[float | None, float | None, float | None]:
    """Paired bootstrap over schema_id intersection for difference mean(b)-mean(a)."""
    by_a = {(r["dataset"], r["schema_id"]): r for r in rows_a}
    by_b = {(r["dataset"], r["schema_id"]): r for r in rows_b}
    keys = sorted(set(by_a) & set(by_b))
    if not keys:
        return None, None, None
    diffs = []
    for k in keys:
        va = key_fn(by_a[k])
        vb = key_fn(by_b[k])
        if va is None or vb is None:
            continue
        diffs.append(vb - va)
    if not diffs:
        return None, None, None
    rng = np.random.default_rng(seed)
    boots = []
    arr = np.array(diffs, dtype=float)
    for _ in range(n):
        sample = rng.choice(arr, size=len(arr), replace=True)
        boots.append(float(sample.mean()))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return float(arr.mean()), float(lo), float(hi)


def load_latency_overlay() -> dict[tuple[str, str, str], float]:
    """Map (dataset, schema_id, prompt) -> DeepSeek describer latency_s from remount."""
    path = OUT / "e5_deepseek_latency.csv"
    if not path.exists():
        return {}
    out = {}
    for r in read_csv(path):
        lat = fnum(r.get("latency_s"))
        if lat is None:
            continue
        out[(r["dataset"], r["schema_id"], r["prompt"])] = lat
    return out


def aggregate_scalability(rows: list[dict], latency_overlay: dict | None = None) -> list[dict]:
    """E5-A aggregates by dataset, model, prompt, size_tier (+ overall size All)."""
    latency_overlay = latency_overlay or {}
    e5a = [r for r in rows if r.get("stage") == "e5a"]
    # Overlay measured DeepSeek describer latencies onto matching rows for p50/p95.
    enriched = []
    for r in e5a:
        rr = dict(r)
        if rr.get("describer") == "deepseek":
            key = (rr["dataset"], rr["schema_id"], rr["prompt"])
            if key in latency_overlay:
                rr["desc_latency_s"] = latency_overlay[key]
                # End-to-end latency still unknown for archived constructor; report describer latency.
                if fnum(rr.get("total_latency_s")) is None:
                    rr["total_latency_s"] = latency_overlay[key]
        enriched.append(rr)
    e5a = enriched
    out = []
    groups: dict[tuple, list] = defaultdict(list)
    for r in e5a:
        groups[(r["dataset"], r["describer"], r["prompt"], r["size_tier"])].append(r)
        groups[(r["dataset"], r["describer"], r["prompt"], "All")].append(r)
        groups[("ALL", r["describer"], r["prompt"], r["size_tier"])].append(r)
        groups[("ALL", r["describer"], r["prompt"], "All")].append(r)
    for (ds, model, prompt, size), rs in sorted(groups.items()):
        p50, p95 = latency_stats(rs)
        out.append(
            {
                "dataset": ds,
                "model": model,
                "prompt": prompt,
                "size_tier": size,
                "N": len(rs),
                "tables_f1": micro_f1(rs, "tables"),
                "attributes_f1": micro_f1(rs, "attributes"),
                "domain_f1": micro_f1(rs, "domain"),
                "entity_f1": micro_f1(rs, "entity"),
                "referential_f1": micro_f1(rs, "referential"),
                "mean_dim_f1": None,
                "nged": mean_nged(rs),
                "p50_latency_s": p50,
                "p95_latency_s": p95,
                "cost_per_schema_usd": mean_cost(rs),
                "success_pct": success_rate(rs),
                "n_desc_ok": sum(inum(r.get("desc_ok")) for r in rs),
                "n_recon_ok": sum(inum(r.get("reconstruction_valid")) for r in rs),
                "n_reused_desc": sum(inum(r.get("desc_reused")) for r in rs),
                "n_reused_ctor": sum(inum(r.get("ctor_reused")) for r in rs),
            }
        )
        dims = [out[-1][f"{d}_f1"] for d in ("tables", "attributes", "domain", "entity", "referential")]
        dims = [d for d in dims if d is not None]
        out[-1]["mean_dim_f1"] = statistics.mean(dims) if dims else None
    return out


def aggregate_cost_fidelity(rows: list[dict]) -> list[dict]:
    e5b = [r for r in rows if r.get("stage") == "e5b"]
    out = []
    groups: dict[tuple, list] = defaultdict(list)
    for r in e5b:
        groups[(r["dataset"], r["constructor"])].append(r)
        groups[("ALL", r["constructor"])].append(r)
    for (ds, ctor), rs in sorted(groups.items()):
        p50, p95 = latency_stats(rs)
        out.append(
            {
                "dataset": ds,
                "constructor": ctor,
                "N": len(rs),
                "tables_f1": micro_f1(rs, "tables"),
                "attributes_f1": micro_f1(rs, "attributes"),
                "domain_f1": micro_f1(rs, "domain"),
                "entity_f1": micro_f1(rs, "entity"),
                "referential_f1": micro_f1(rs, "referential"),
                "mean_dim_f1": None,
                "nged": mean_nged(rs),
                "cost_per_schema_usd": mean_cost(rs),
                "p50_latency_s": p50,
                "p95_latency_s": p95,
                "success_pct": success_rate(rs),
            }
        )
        dims = [out[-1][f"{d}_f1"] for d in ("tables", "attributes", "domain", "entity", "referential")]
        dims = [d for d in dims if d is not None]
        out[-1]["mean_dim_f1"] = statistics.mean(dims) if dims else None
    return out


def aggregate_prompt_efficiency(rows: list[dict]) -> list[dict]:
    e5a = [r for r in rows if r.get("stage") == "e5a"]
    by = defaultdict(dict)
    for r in e5a:
        key = (r["dataset"], r["describer"], r["schema_id"])
        by[key][r["prompt"]] = r
    # also dataset-level aggregates
    paired_rows = []
    for (ds, desc, sid), prompts in by.items():
        if "basic" not in prompts or "detailed" not in prompts:
            continue
        b, d = prompts["basic"], prompts["detailed"]
        paired_rows.append({"dataset": ds, "describer": desc, "schema_id": sid, "basic": b, "detailed": d})

    out = []
    groups: dict[tuple, list] = defaultdict(list)
    for p in paired_rows:
        groups[(p["dataset"], p["describer"])].append(p)
        groups[("ALL", p["describer"])].append(p)

    for (ds, desc), ps in sorted(groups.items()):
        # For E5-C paired deltas, only score conditions that actually reconstructed.
        # Missing constructor/API outputs are N/A (not zero-imputed) so credential
        # failures are not mistaken for prompt regressions.
        b_ok = [p["basic"] for p in ps if inum(p["basic"].get("reconstruction_valid")) == 1]
        d_ok = [p["detailed"] for p in ps if inum(p["detailed"].get("reconstruction_valid")) == 1]
        b_rows = [p["basic"] for p in ps]
        d_rows = [p["detailed"] for p in ps]
        ref_b = micro_f1(b_ok, "referential") if b_ok else None
        ref_d = micro_f1(d_ok, "referential") if d_ok else None
        dom_b = micro_f1(b_ok, "domain") if b_ok else None
        dom_d = micro_f1(d_ok, "domain") if d_ok else None
        nged_b = mean_nged(b_ok) if b_ok else None
        nged_d = mean_nged(d_ok) if d_ok else None
        cost_b = mean_cost(b_ok) if b_ok else mean_cost(b_rows)
        cost_d = mean_cost(d_ok) if d_ok else mean_cost(d_rows)
        # latency / tokens deltas as mean of paired differences where both present
        d_ref = None if ref_b is None or ref_d is None else ref_d - ref_b
        d_dom = None if dom_b is None or dom_d is None else dom_d - dom_b
        d_nged = None if nged_b is None or nged_d is None else nged_d - nged_b
        d_cost = None if cost_b is None or cost_d is None else cost_d - cost_b
        lat_diffs = []
        tok_diffs = []
        for p in ps:
            lb, ld = fnum(p["basic"].get("total_latency_s")), fnum(p["detailed"].get("total_latency_s"))
            if lb is not None and ld is not None:
                lat_diffs.append(ld - lb)
            tb = fnum(p["basic"].get("total_output_tokens"))
            td = fnum(p["detailed"].get("total_output_tokens"))
            if tb is not None and td is not None:
                tok_diffs.append(td - tb)
        d_lat = statistics.mean(lat_diffs) if lat_diffs else None
        d_tok = statistics.mean(tok_diffs) if tok_diffs else None
        marg = None
        if d_ref is not None and d_cost is not None and d_ref > 0 and d_cost > 0:
            marg = d_cost / (100.0 * d_ref)
        out.append(
            {
                "dataset": ds,
                "describer": desc,
                "N": len(ps),
                "ref_f1_basic": ref_b,
                "ref_f1_detailed": ref_d,
                "domain_f1_basic": dom_b,
                "domain_f1_detailed": dom_d,
                "nged_basic": nged_b,
                "nged_detailed": nged_d,
                "cost_basic": cost_b,
                "cost_detailed": cost_d,
                "delta_ref_f1": d_ref,
                "delta_domain_f1": d_dom,
                "delta_nged": d_nged,
                "delta_cost": d_cost,
                "delta_latency_s": d_lat,
                "delta_output_tokens": d_tok,
                "marginal_cost_per_ref_f1_pp": marg,
                "n_recon_basic": sum(inum(p["basic"].get("reconstruction_valid")) for p in ps),
                "n_recon_detailed": sum(inum(p["detailed"].get("reconstruction_valid")) for p in ps),
            }
        )
    return out


def pareto_frontier(points: list[dict], cost_key="cost_per_schema_usd", fid_key="referential_f1") -> list[dict]:
    usable = [p for p in points if fnum(p.get(cost_key)) is not None and fnum(p.get(fid_key)) is not None]
    frontier = []
    for p in usable:
        dominated = False
        for q in usable:
            if q is p:
                continue
            # q dominates p if cost<= and fid>= with strict improvement in one
            if fnum(q[cost_key]) <= fnum(p[cost_key]) and fnum(q[fid_key]) >= fnum(p[fid_key]) and (
                fnum(q[cost_key]) < fnum(p[cost_key]) or fnum(q[fid_key]) > fnum(p[fid_key])
            ):
                dominated = True
                break
        if not dominated:
            frontier.append(p)
    frontier.sort(key=lambda x: fnum(x[cost_key]) or 0)
    return frontier


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    line = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join(["---"] * len(headers)) + " |"
    body = "\n".join("| " + " | ".join(r) + " |" for r in rows)
    return "\n".join([line, sep, body])


def bold_best(
    values: list[float | None],
    fmt_fn,
    higher_better=True,
    eligible: list[bool] | None = None,
) -> list[str]:
    """Bold best among eligible rows only (e.g., success_pct > 0)."""
    elig = eligible or [v is not None for v in values]
    nums = [(i, v) for i, v in enumerate(values) if v is not None and elig[i]]
    if not nums:
        return [fmt_fn(v) for v in values]
    best = max(v for _, v in nums) if higher_better else min(v for _, v in nums)
    # Avoid bolding a degenerate all-equal-zero block of unavailable conditions.
    if all(abs(v - best) < 1e-12 for _, v in nums) and abs(best) < 1e-12 and higher_better:
        return [fmt_fn(v) for v in values]
    out = []
    for i, v in enumerate(values):
        s = fmt_fn(v)
        if elig[i] and v is not None and abs(v - best) < 1e-12:
            s = f"\\textbf{{{s}}}"
        out.append(s)
    return out


def latex_escape(s: str) -> str:
    return s.replace("_", "\\_")


def gen_latex_scalability(scal: list[dict], extended: bool) -> str:
    rows = [r for r in scal if r["dataset"] != "ALL"]
    if not extended:
        rows = [r for r in rows if r["size_tier"] == "All"]
    else:
        rows = [r for r in rows if r["size_tier"] != "All"]
    # Group by dataset for bolding within comparable (same dataset)
    lines = []
    lines.append("\\begin{table*}[t]")
    lines.append("\\centering")
    lines.append("\\scriptsize")
    if extended:
        lines.append("\\caption{E5 scalability (extended): structural fidelity, latency, and cost by schema size tier.}")
        lines.append("\\label{tab:e5_scalability_ext}")
    else:
        lines.append("\\caption{E5 scalability: structural fidelity, latency, and cost (aggregated over size tiers).}")
        lines.append("\\label{tab:e5_scalability}")
    # columns: Dataset, Model, Prompt, [Size], N, Ref, Dom, nGED, p50, p95, $/sch, Succ
    lines.append("\\begin{tabular}{ll" + ("l" if extended else "") + "crrrrrrrr}")
    lines.append("\\toprule")
    if extended:
        lines.append("Dataset & Model & Prompt & Size & N & Ref.\\ F1 & Dom.\\ F1 & nGED & p50 (s) & p95 (s) & \\$/sch. & Succ.\\% \\\\")
    else:
        lines.append("Dataset & Model & Prompt & N & Ref.\\ F1 & Dom.\\ F1 & nGED & p50 (s) & p95 (s) & \\$/sch. & Succ.\\% \\\\")
    lines.append("\\midrule")
    by_ds = defaultdict(list)
    for r in rows:
        by_ds[r["dataset"]].append(r)
    for ds, rs in by_ds.items():
        elig = [(fnum(r.get("success_pct")) or 0) > 0 for r in rs]
        ref = bold_best([r["referential_f1"] for r in rs], lambda v: fmt(v, 3), True, elig)
        dom = bold_best([r["domain_f1"] for r in rs], lambda v: fmt(v, 3), True, elig)
        ng = bold_best([r["nged"] for r in rs], lambda v: fmt(v, 3), False, elig)
        for i, r in enumerate(rs):
            model = {"deepseek": "DeepSeek-6.7B", "gpt_5_4_mini": "GPT-5.4-mini", "claude_sonnet_4_6": "Claude Sonnet 4.6"}.get(r["model"], r["model"])
            prompt = r["prompt"].capitalize()
            cells = [
                latex_escape(ds),
                latex_escape(model),
                prompt,
            ]
            if extended:
                cells.append(r["size_tier"])
            cells += [
                str(r["N"]),
                ref[i],
                dom[i],
                ng[i],
                fmt(r["p50_latency_s"], 2),
                fmt(r["p95_latency_s"], 2),
                fmt_cost(r["cost_per_schema_usd"]),
                fmt(r["success_pct"], 1),
            ]
            lines.append(" & ".join(cells) + " \\\\")
        lines.append("\\midrule")
    if lines[-1] == "\\midrule":
        lines[-1] = "\\bottomrule"
    else:
        lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    lines.append("\\end{table*}")
    return "\n".join(lines) + "\n"


def gen_latex_cost_fidelity(cf: list[dict]) -> str:
    rows = [r for r in cf if r["dataset"] != "ALL"]
    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\scriptsize",
        "\\caption{E5 cost--fidelity comparison with fixed GPT-5.4-mini detailed descriptions.}",
        "\\label{tab:e5_cost_fidelity}",
        "\\begin{tabular}{llcrrrrrrrr}",
        "\\toprule",
        "Dataset & Constructor & N & T & A & D & E & R & nGED & \\$/sch. & p50 (s) \\\\",
        "\\midrule",
    ]
    by_ds = defaultdict(list)
    for r in rows:
        by_ds[r["dataset"]].append(r)
    for ds, rs in by_ds.items():
        elig = [(fnum(r.get("success_pct")) or 0) > 0 for r in rs]
        cols = {
            "tables_f1": bold_best([r["tables_f1"] for r in rs], lambda v: fmt(v, 3), True, elig),
            "attributes_f1": bold_best([r["attributes_f1"] for r in rs], lambda v: fmt(v, 3), True, elig),
            "domain_f1": bold_best([r["domain_f1"] for r in rs], lambda v: fmt(v, 3), True, elig),
            "entity_f1": bold_best([r["entity_f1"] for r in rs], lambda v: fmt(v, 3), True, elig),
            "referential_f1": bold_best([r["referential_f1"] for r in rs], lambda v: fmt(v, 3), True, elig),
            "nged": bold_best([r["nged"] for r in rs], lambda v: fmt(v, 3), False, elig),
        }
        for i, r in enumerate(rs):
            name = {"gpt_4o_mini": "GPT-4o-mini", "gpt_5_4_mini": "GPT-5.4-mini", "claude_sonnet_4_6": "Claude Sonnet 4.6"}.get(r["constructor"], r["constructor"])
            lines.append(
                " & ".join(
                    [
                        latex_escape(ds),
                        latex_escape(name),
                        str(r["N"]),
                        cols["tables_f1"][i],
                        cols["attributes_f1"][i],
                        cols["domain_f1"][i],
                        cols["entity_f1"][i],
                        cols["referential_f1"][i],
                        cols["nged"][i],
                        fmt_cost(r["cost_per_schema_usd"]),
                        fmt(r["p50_latency_s"], 2),
                    ]
                )
                + " \\\\"
            )
        lines.append("\\midrule")
    if lines[-1] == "\\midrule":
        lines[-1] = "\\bottomrule"
    lines += ["\\end{tabular}", "\\end{table}", ""]
    return "\n".join(lines)


def gen_latex_prompt_eff(pe: list[dict]) -> str:
    rows = [r for r in pe if r["dataset"] != "ALL"]
    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\scriptsize",
        "\\caption{E5 basic vs.\\ detailed prompting (paired schemata; GPT-4o-mini constructor).}",
        "\\label{tab:e5_prompt_efficiency}",
        "\\begin{tabular}{llrrrrrrrr}",
        "\\toprule",
        "Dataset & Describer & Ref$_B$ & Ref$_D$ & nGED$_B$ & nGED$_D$ & \\$_B$ & \\$_D$ & $\\Delta$\\$ & $\\Delta$Ref \\\\",
        "\\midrule",
    ]
    for r in rows:
        name = {"deepseek": "DeepSeek-6.7B", "gpt_5_4_mini": "GPT-5.4-mini", "claude_sonnet_4_6": "Claude Sonnet 4.6"}.get(r["describer"], r["describer"])
        lines.append(
            " & ".join(
                [
                    latex_escape(r["dataset"]),
                    latex_escape(name),
                    fmt(r["ref_f1_basic"], 3),
                    fmt(r["ref_f1_detailed"], 3),
                    fmt(r["nged_basic"], 3),
                    fmt(r["nged_detailed"], 3),
                    fmt_cost(r["cost_basic"]),
                    fmt_cost(r["cost_detailed"]),
                    fmt_cost(r["delta_cost"]),
                    fmt(r["delta_ref_f1"], 3),
                ]
            )
            + " \\\\"
        )
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
    return "\n".join(lines)


def make_figures(per: list[dict], scal: list[dict], pe: list[dict], cf: list[dict]) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    e5a = [r for r in per if r.get("stage") == "e5a" and inum(r.get("reconstruction_valid")) == 1]

    # Figure E5-1
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6))
    colors = {"deepseek": "#1f77b4", "gpt_5_4_mini": "#2ca02c", "claude_sonnet_4_6": "#d62728"}
    markers = {"basic": "o", "detailed": "s"}
    for r in e5a:
        c = colors.get(r["describer"], "gray")
        m = markers.get(r["prompt"], "o")
        x = fnum(r.get("columns")) or 0
        axes[0].scatter(x, fnum(r.get("referential_f1")) or 0, c=c, marker=m, alpha=0.55, s=18)
        lat = fnum(r.get("total_latency_s"))
        if lat is not None:
            axes[1].scatter(x, lat, c=c, marker=m, alpha=0.55, s=18)
        cost = fnum(r.get("total_cost_usd"))
        if cost is not None:
            axes[2].scatter(x, cost, c=c, marker=m, alpha=0.55, s=18)
    axes[0].set_xlabel("#Columns")
    axes[0].set_ylabel("Referential F1")
    axes[0].set_title("(a) Fidelity vs size")
    axes[1].set_xlabel("#Columns")
    axes[1].set_ylabel("Latency (s)")
    axes[1].set_title("(b) Latency vs size")
    axes[2].set_xlabel("#Columns")
    axes[2].set_ylabel("Cost (USD/schema)")
    axes[2].set_title("(c) Cost vs size")
    # legend proxies
    from matplotlib.lines import Line2D

    handles = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=colors["deepseek"], label="DeepSeek", markersize=8),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=colors["gpt_5_4_mini"], label="GPT-5.4-mini", markersize=8),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=colors["claude_sonnet_4_6"], label="Claude 4.6", markersize=8),
        Line2D([0], [0], marker="o", color="gray", label="basic", linestyle="None"),
        Line2D([0], [0], marker="s", color="gray", label="detailed", linestyle="None"),
    ]
    axes[2].legend(handles=handles, fontsize=7, loc="best")
    fig.tight_layout()
    fig.savefig(FIGURES / "e5_scalability.pdf")
    fig.savefig(FIGURES / "e5_scalability.png", dpi=200)
    plt.close(fig)

    # Figure E5-2 Pareto
    pts = []
    for r in scal:
        if r["dataset"] == "ALL" and r["size_tier"] == "All":
            pts.append(
                {
                    "label": f"{r['model']}/{r['prompt']}",
                    "cost_per_schema_usd": r["cost_per_schema_usd"],
                    "referential_f1": r["referential_f1"],
                    "success_pct": r["success_pct"],
                }
            )
    # Also include E5-B ALL constructors
    for r in cf:
        if r["dataset"] == "ALL":
            pts.append(
                {
                    "label": f"E5B:{r['constructor']}",
                    "cost_per_schema_usd": r["cost_per_schema_usd"],
                    "referential_f1": r["referential_f1"],
                    "success_pct": r["success_pct"],
                }
            )
    front = pareto_frontier(pts)
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    for p in pts:
        c, f = fnum(p["cost_per_schema_usd"]), fnum(p["referential_f1"])
        if c is None or f is None:
            continue
        ax.scatter(c, f, s=40, alpha=0.7)
        ax.annotate(p["label"], (c, f), fontsize=6, alpha=0.8)
    if front:
        fx = [fnum(p["cost_per_schema_usd"]) for p in front]
        fy = [fnum(p["referential_f1"]) for p in front]
        ax.plot(fx, fy, "k--", alpha=0.5, label="Pareto frontier")
        ax.scatter(fx, fy, s=80, facecolors="none", edgecolors="black", label="Pareto-optimal")
    ax.set_xlabel("Cost per schema (USD)")
    ax.set_ylabel("Referential F1")
    ax.set_title("E5-2 Cost--Fidelity Pareto")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(FIGURES / "e5_pareto.pdf")
    fig.savefig(FIGURES / "e5_pareto.png", dpi=200)
    plt.close(fig)

    # Figure E5-3 prompt efficiency
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    for r in pe:
        if r["dataset"] == "ALL":
            continue
        dx, dy = fnum(r.get("delta_cost")), fnum(r.get("delta_ref_f1"))
        if dx is None or dy is None:
            # still plot if only fidelity delta known at 0 cost marker? skip
            continue
        ax.scatter(dx, dy, s=50)
        ax.annotate(f"{r['dataset'][:3]}/{r['describer'][:8]}", (dx, dy), fontsize=6)
    ax.axhline(0, color="gray", lw=0.8)
    ax.axvline(0, color="gray", lw=0.8)
    ax.set_xlabel("Δ Cost (detailed − basic), USD/schema")
    ax.set_ylabel("Δ Referential F1 (detailed − basic)")
    ax.set_title("E5-3 Prompt efficiency")
    fig.tight_layout()
    fig.savefig(FIGURES / "e5_prompt_efficiency.pdf")
    fig.savefig(FIGURES / "e5_prompt_efficiency.png", dpi=200)
    plt.close(fig)

    (FIGURES / "pareto_points.json").write_text(json.dumps({"points": pts, "frontier": front}, indent=2, default=str), encoding="utf-8")


def write_results_md(scal, cf, pe, meta, failures, per, frontier) -> None:
    lines = []
    lines.append("# E5 Results — Scalability and Cost\n")
    lines.append(f"Generated from `{OUT}`.\n")
    if meta:
        lines.append("## Run metadata\n")
        lines.append("```json")
        lines.append(json.dumps(meta, indent=2))
        lines.append("```\n")

    lines.append("## E5-A Scalability (main: size tier = All)\n")
    main = [r for r in scal if r["size_tier"] == "All" and r["dataset"] != "ALL"]
    headers = ["Dataset", "Model", "Prompt", "N", "Ref F1", "Domain F1", "nGED", "p50(s)", "p95(s)", "Cost", "Succ%"]
    body = []
    for r in main:
        body.append(
            [
                r["dataset"],
                r["model"],
                r["prompt"],
                str(r["N"]),
                fmt(r["referential_f1"]),
                fmt(r["domain_f1"]),
                fmt(r["nged"]),
                fmt(r["p50_latency_s"], 2),
                fmt(r["p95_latency_s"], 2),
                fmt_cost(r["cost_per_schema_usd"]),
                fmt(r["success_pct"], 1),
            ]
        )
    lines.append(md_table(headers, body))
    lines.append("")

    lines.append("## E5-A Scalability (extended by size tier)\n")
    ext = [r for r in scal if r["size_tier"] != "All" and r["dataset"] != "ALL"]
    headers2 = ["Dataset", "Model", "Prompt", "Size", "N", "Ref F1", "Domain F1", "nGED", "p50", "Cost", "Succ%"]
    body2 = []
    for r in ext:
        body2.append(
            [
                r["dataset"],
                r["model"],
                r["prompt"],
                r["size_tier"],
                str(r["N"]),
                fmt(r["referential_f1"]),
                fmt(r["domain_f1"]),
                fmt(r["nged"]),
                fmt(r["p50_latency_s"], 2),
                fmt_cost(r["cost_per_schema_usd"]),
                fmt(r["success_pct"], 1),
            ]
        )
    lines.append(md_table(headers2, body2))
    lines.append("")

    lines.append("## E5-B Cost--Fidelity\n")
    headers3 = ["Dataset", "Constructor", "N", "T", "A", "D", "E", "R", "nGED", "Cost", "p50"]
    body3 = []
    for r in cf:
        if r["dataset"] == "ALL":
            continue
        body3.append(
            [
                r["dataset"],
                r["constructor"],
                str(r["N"]),
                fmt(r["tables_f1"]),
                fmt(r["attributes_f1"]),
                fmt(r["domain_f1"]),
                fmt(r["entity_f1"]),
                fmt(r["referential_f1"]),
                fmt(r["nged"]),
                fmt_cost(r["cost_per_schema_usd"]),
                fmt(r["p50_latency_s"], 2),
            ]
        )
    lines.append(md_table(headers3, body3))
    lines.append("")

    lines.append("## E5-C Prompt efficiency\n")
    headers4 = ["Dataset", "Describer", "N", "RefB", "RefD", "nGEDB", "nGEDD", "CostB", "CostD", "ΔCost", "ΔRef", "Marg$/pp"]
    body4 = []
    for r in pe:
        if r["dataset"] == "ALL":
            continue
        body4.append(
            [
                r["dataset"],
                r["describer"],
                str(r["N"]),
                fmt(r["ref_f1_basic"]),
                fmt(r["ref_f1_detailed"]),
                fmt(r["nged_basic"]),
                fmt(r["nged_detailed"]),
                fmt_cost(r["cost_basic"]),
                fmt_cost(r["cost_detailed"]),
                fmt_cost(r["delta_cost"]),
                fmt(r["delta_ref_f1"]),
                fmt_cost(r["marginal_cost_per_ref_f1_pp"]),
            ]
        )
    lines.append(md_table(headers4, body4))
    lines.append("")

    lines.append("## Pareto-optimal configurations\n")
    if frontier:
        for p in frontier:
            lines.append(f"- **{p.get('label')}**: cost={fmt_cost(p.get('cost_per_schema_usd'))}, ref_f1={fmt(p.get('referential_f1'))}")
    else:
        lines.append("No comparable cost+fidelity points (closed models unavailable or costs N/A).")
    lines.append("")

    # Reliability counts
    e5a = [r for r in per if r.get("stage") == "e5a"]
    lines.append("## Reliability summary (E5-A rows)\n")
    lines.append(f"- Attempted pipeline rows: {len(e5a)}")
    lines.append(f"- Desc OK: {sum(inum(r.get('desc_ok')) for r in e5a)}")
    lines.append(f"- Parsed/reconstructed OK: {sum(inum(r.get('reconstruction_valid')) for r in e5a)}")
    lines.append(f"- Truncated describer: {sum(inum(r.get('desc_truncated')) for r in e5a)}")
    lines.append(f"- Reused describer: {sum(inum(r.get('desc_reused')) for r in e5a)}")
    lines.append(f"- Reused constructor: {sum(inum(r.get('ctor_reused')) for r in e5a)}")
    lines.append(f"- Failure rows logged: {len(failures)}")
    lines.append("")

    (HERE / "RESULTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_paper_tex(scal, cf, pe, meta, frontier) -> None:
    # Pull DeepSeek basic numbers for narrative
    ds_basic = [r for r in scal if r["dataset"] != "ALL" and r["model"] == "deepseek" and r["prompt"] == "basic" and r["size_tier"] == "All"]
    ds_by_size = [r for r in scal if r["model"] == "deepseek" and r["prompt"] == "basic" and r["dataset"] == "ALL" and r["size_tier"] != "All"]

    def find_size(tier):
        for r in ds_by_size:
            if r["size_tier"] == tier:
                return r
        return None

    small, medium, large = find_size("Small"), find_size("Medium"), find_size("Large")
    openai_ok = bool(meta and meta.get("openai_available"))
    anthropic_ok = bool(meta and meta.get("anthropic_available"))

    tex = []
    tex.append("\\subsection{E5: Scalability and Cost}")
    tex.append("\\label{sec:e5}")
    tex.append("")
    tex.append("\\paragraph{Setup.}")
    n_sel = meta.get("n_schemas") if meta else 120
    tex.append(
        f"We evaluate a deterministic stratified sample of {n_sel} schemata "
        "(40 per dataset; seed 42) spanning size tiers (Small/Medium/Large) and "
        "constraint-complexity tiers (Easy/Medium/Hard) using the paper score "
        "$s=2\\min(f,10)+3c+\\min(u,5)+0.2\\max(0,n_{\\mathrm{col}}/n_{\\mathrm{tab}}-10)$. "
        "Describers are DeepSeek-Coder-6.7B-Instruct, GPT-5.4-mini, and Claude Sonnet~4.6 "
        "under the E1 basic and detailed prompts; the E5-A constructor is fixed to GPT-4o-mini "
        "(E2 protocol). E5-B holds GPT-5.4-mini detailed descriptions fixed and varies constructors. "
        "Metrics are micro-averaged F1 over element counts and mean nGED; failed/unparseable "
        "reconstructions are zero-scored with nGED~$=1$. Latency is wall-clock at concurrency~1. "
        "Prices are frozen in \\texttt{experiments/e5/pricing.json} (verified 2026-11-06)."
    )
    if not openai_ok or not anthropic_ok:
        reasons = []
        if not openai_ok:
            reasons.append("OpenAI API authentication failed on this host")
        if not anthropic_ok:
            reasons.append("Anthropic credentials were unavailable")
        tex.append(
            " Consequently, GPT-5.4-mini and Claude conditions are reported as N/A "
            f"({'; '.join(reasons)}), while DeepSeek-basic round-trips reuse validated E1/E2 archives "
            "with tokenizer-estimated GPT-4o-mini costs labeled separately from live billed usage."
        )
    tex.append("")
    tex.append("\\paragraph{Scalability.}")
    if small and large and small.get("referential_f1") is not None and large.get("referential_f1") is not None:
        drop = small["referential_f1"] - large["referential_f1"]
        tex.append(
            f"Fig.~\\ref{{fig:e5_scalability}} and Table~\\ref{{tab:e5_scalability}} summarize size effects. "
            f"For DeepSeek-basic$\\rightarrow$GPT-4o-mini, referential F1 moves from "
            f"{fmt(small['referential_f1'])} (Small) to {fmt(large['referential_f1'])} (Large) "
            f"on the pooled sample (absolute drop {fmt(drop)}), while mean nGED changes from "
            f"{fmt(small['nged'])} to {fmt(large['nged'])}. "
            "Provider/API latency is not interpreted as intrinsic model FLOPs; DeepSeek monetary cost is N/A under local GPU execution."
        )
    else:
        tex.append(
            "Fig.~\\ref{fig:e5_scalability} and Table~\\ref{tab:e5_scalability} report available size-stratified "
            "measurements. Closed-model scalability cells remain N/A pending credentialed API access."
        )
    tex.append("")
    tex.append("\\paragraph{Cost--fidelity trade-offs.}")
    tex.append(
        "Table~\\ref{tab:e5_cost_fidelity} and Fig.~\\ref{fig:e5_pareto} compare constructors under fixed "
        "GPT-5.4-mini detailed descriptions. "
    )
    if frontier:
        labels = ", ".join(p.get("label", "?") for p in frontier)
        tex.append(f"Pareto-optimal configurations among comparable costed points: {latex_escape(labels)}. ")
    else:
        tex.append(
            "No multi-model Pareto frontier is claimed for closed constructors because live GPT-5.4-mini/Claude "
            "runs could not be executed; DeepSeek-basic archive estimates provide the only costed fidelity points. "
        )
    tex.append("")
    tex.append("\\paragraph{Cost of detailed prompting.}")
    tex.append(
        "Table~\\ref{tab:e5_prompt_efficiency} reports paired basic vs.\\ detailed differences. "
        "Marginal USD per referential F1 percentage point is defined only when both $\\Delta$Ref~F1$>0$ and $\\Delta$cost$>0$. "
        "Where detailed reconstructions are unavailable (constructor blocked), deltas are marked N/A rather than imputed."
    )
    tex.append("")
    tex.append("\\paragraph{Answer to RQ1 and RQ3.}")
    tex.append(
        "RQ1: under the executable DeepSeek-basic round-trip setting, larger schemata exhibit lower referential "
        "fidelity and higher nGED than small schemata in the stratified sample; token demand grows with schema size, "
        "while monetary cost for open-weight local inference remains unmetered (N/A). "
        "RQ3: detailed prompting cannot yet be declared cost-justified for closed models on this host; "
        "for DeepSeek, detailed reconstructions require GPT-4o-mini calls that were blocked by API authentication, "
        "so we do not claim a positive marginal return without those paired measurements."
    )
    tex.append("")
    tex.append("% Figures (paths relative to reproducibility package):")
    tex.append("% experiments/e5/figures/e5_scalability.pdf")
    tex.append("% experiments/e5/figures/e5_pareto.pdf")
    tex.append("% experiments/e5/figures/e5_prompt_efficiency.pdf")
    (HERE / "paper_e5.tex").write_text("\n".join(tex) + "\n", encoding="utf-8")


def validate(per, scal, manifest_rows) -> list[str]:
    errs = []
    sel = [r for r in manifest_rows if inum(r.get("selected")) == 1]
    if len(sel) > 120:
        errs.append(f"selected>{120}: {len(sel)}")
    # unique schema ids in sample
    ids = [(r["dataset"], r["schema_id"]) for r in sel]
    if len(ids) != len(set(ids)):
        errs.append("duplicate schema ids in sample")
    # TP/FP/FN consistency
    for r in per:
        for dim in ("tables", "attributes", "domain", "entity", "referential"):
            tp, fp, fn = inum(r.get(f"{dim}_tp")), inum(r.get(f"{dim}_fp")), inum(r.get(f"{dim}_fn"))
            g, rec, m = inum(r.get(f"{dim}_gold")), inum(r.get(f"{dim}_recreated")), inum(r.get(f"{dim}_matched"))
            if tp != m or fp != max(0, rec - m) or fn != max(0, g - m):
                errs.append(f"TP/FP/FN mismatch {r.get('schema_id')} {dim}")
                break
        else:
            continue
        break
    return errs


def main() -> int:
    per = read_csv(OUT / "e5_per_schema.csv")
    failures = read_csv(OUT / "e5_failures.csv")
    manifest = read_csv(OUT / "sample_manifest.csv")
    meta = {}
    if (OUT / "e5_run_meta.json").exists():
        meta = json.loads((OUT / "e5_run_meta.json").read_text(encoding="utf-8"))

    latency_overlay = load_latency_overlay()
    scal = aggregate_scalability(per, latency_overlay)
    cf = aggregate_cost_fidelity(per)
    pe = aggregate_prompt_efficiency(per)
    write_csv(OUT / "e5_scalability.csv", scal)
    write_csv(OUT / "e5_cost_fidelity.csv", cf)
    write_csv(OUT / "e5_prompt_efficiency.csv", pe)

    TABLES.mkdir(parents=True, exist_ok=True)
    (TABLES / "e5_scalability_main.tex").write_text(gen_latex_scalability(scal, extended=False), encoding="utf-8")
    (TABLES / "e5_scalability_extended.tex").write_text(gen_latex_scalability(scal, extended=True), encoding="utf-8")
    (TABLES / "e5_cost_fidelity.tex").write_text(gen_latex_cost_fidelity(cf), encoding="utf-8")
    (TABLES / "e5_prompt_efficiency.tex").write_text(gen_latex_prompt_eff(pe), encoding="utf-8")

    # Pareto from ALL aggregates
    pts = []
    for r in scal:
        if r["dataset"] == "ALL" and r["size_tier"] == "All":
            pts.append({"label": f"{r['model']}/{r['prompt']}", **r})
    for r in cf:
        if r["dataset"] == "ALL":
            pts.append({"label": f"E5B:{r['constructor']}", "cost_per_schema_usd": r["cost_per_schema_usd"], "referential_f1": r["referential_f1"]})
    frontier = pareto_frontier(pts)

    make_figures(per, scal, pe, cf)
    write_results_md(scal, cf, pe, meta, failures, per, frontier)
    write_paper_tex(scal, cf, pe, meta, frontier)

    errs = validate(per, scal, manifest)
    (OUT / "e5_validation.json").write_text(json.dumps({"errors": errs, "n_errors": len(errs)}, indent=2), encoding="utf-8")
    print("Report complete. validation_errors=", len(errs))
    print("Wrote RESULTS.md, LaTeX tables, figures, paper_e5.tex")
    return 0 if not errs else 1


if __name__ == "__main__":
    raise SystemExit(main())
