#!/usr/bin/env python3
"""SCR (E1) vs structural F1 (E2) correlation figures from LOCAL metrics CSVs.

Reads ``e1_summary.csv`` (written by ``experiments/E1/evaluate.py``) and ``e2_summary.csv``
(``experiments/E2/evaluate.py``) found below ``--metrics-dir``, pairs rows by
(dataset, model, prompt) and draws, per F1 dimension, a scatter plot of SCR against F1 with the
Pearson r, its two-sided p-value / significance label and the least-squares regression line.

Figures are written ONLY below ``--out-dir`` (default ``figures/generated/``, git-ignored).
``--synthetic`` draws a clearly watermarked demo from random numbers (no metrics needed).
No reference values are embedded.  Statistics are pure Python (no scipy); matplotlib is imported
lazily and only for drawing.
"""
from __future__ import annotations

import argparse
import math
import random
import sys
from pathlib import Path
from typing import Iterable, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import repro_io as rio  # noqa: E402
from src.metrics import ELEMENTS  # noqa: E402

DEFAULT_OUT_DIR = ROOT / "figures" / "generated"
DEFAULT_METRICS_DIR = ROOT / "results" / "metrics" / "local"


# --------------------------------------------------------------------------- statistics


def _betacf(a: float, b: float, x: float, max_iter: int = 300, eps: float = 3e-14) -> float:
    """Continued fraction for the regularised incomplete beta function (modified Lentz)."""
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, max_iter + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h


def betainc(a: float, b: float, x: float) -> float:
    """Regularised incomplete beta function I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    ln_front = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x)
    front = math.exp(ln_front)
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def pearson_p_value(r: float, n: int) -> float:
    """Two-sided p-value of H0: rho = 0 for sample correlation ``r`` over ``n`` pairs."""
    if n < 3 or math.isnan(r):
        return float("nan")
    if abs(r) >= 1.0 - 1e-12:  # numerically perfect correlation
        return 0.0
    df = n - 2
    t2 = r * r * df / (1.0 - r * r)
    return betainc(df / 2.0, 0.5, df / (df + t2))


def compute_pearson(x: Sequence[float], y: Sequence[float]) -> tuple[float, float, int]:
    """``(r, two_sided_p, n)``; ``r``/``p`` are NaN when undefined (n < 3 or zero variance)."""
    if len(x) != len(y):
        raise ValueError(f"length mismatch: {len(x)} vs {len(y)}")
    n = len(x)
    if n < 2:
        return float("nan"), float("nan"), n
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    if sxx <= 0.0 or syy <= 0.0:
        return float("nan"), float("nan"), n
    r = max(-1.0, min(1.0, sxy / math.sqrt(sxx * syy)))
    return r, pearson_p_value(r, n), n


def linreg(x: Sequence[float], y: Sequence[float]) -> tuple[float, float, float]:
    """Least-squares ``y = slope * x + intercept``; returns ``(slope, intercept, r_squared)``."""
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("need two equally long sequences with at least 2 points")
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((a - mx) ** 2 for a in x)
    if sxx <= 0.0:
        raise ValueError("x has zero variance")
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    slope = sxy / sxx
    intercept = my - slope * mx
    syy = sum((b - my) ** 2 for b in y)
    r2 = 1.0 if syy <= 0.0 else (sxy * sxy) / (sxx * syy)
    return slope, intercept, r2


def significance_label(p: float) -> str:
    """``***`` p<0.001, ``**`` p<0.01, ``*`` p<0.05, ``n.s.`` otherwise (``n/a`` if undefined)."""
    if p is None or math.isnan(p):
        return "n/a"
    return "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "n.s."


# --------------------------------------------------------------------------- data


def _float(v) -> float | None:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(f) else f


def find_csv(metrics_dir: str | Path, name: str) -> Path | None:
    hits = sorted(Path(metrics_dir).rglob(name))
    return hits[0] if hits else None


def pair_rows(e1_rows: Iterable[dict], e2_rows: Iterable[dict], *, datasets: Sequence[str] | None = None) -> list[dict]:
    """Join E1 SCR with E2 F1 by (dataset, model, prompt); rows lacking either value are dropped."""
    e2 = {(r["dataset"], r["describer_model"], r["prompt"]): r for r in e2_rows}
    out = []
    for r in e1_rows:
        key = (r["dataset"], r["model"], r["prompt"])
        if datasets and r["dataset"] not in datasets:
            continue
        o = e2.get(key)
        scr = _float(r.get("scr_macro"))
        if o is None or scr is None:
            continue
        row = {"dataset": key[0], "model": key[1], "prompt": key[2], "scr": scr}
        for e in ELEMENTS:
            row[e] = _float(o.get(f"f1_{e}"))
        out.append(row)
    return out


def synthetic_pairs(n: int = 24, seed: int = 0) -> list[dict]:
    """Random demo data (NOT results): SCR in [0.5, 1], F1 loosely increasing with SCR plus noise."""
    rng = random.Random(seed)
    rows = []
    for i in range(n):
        scr = 0.5 + 0.5 * rng.random()
        row = {"dataset": "synthetic", "model": f"m{i % 5}", "prompt": "basic" if i % 2 else "detailed", "scr": scr}
        for k, e in enumerate(ELEMENTS):
            row[e] = max(0.0, min(1.0, 0.2 + 0.6 * scr * (1 - 0.1 * k) + rng.gauss(0, 0.06)))
        rows.append(row)
    return rows


# --------------------------------------------------------------------------- plotting


def plot_scr_vs_f1(rows: Sequence[dict], out_dir: Path, *, dims: Sequence[str] = ELEMENTS, synthetic: bool = False,
                   formats: Sequence[str] = ("png",)) -> list[Path]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_dir.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, len(dims), figsize=(3.4 * len(dims), 3.4), squeeze=False)
    for ax, dim in zip(axes[0], dims):
        pts = [(r["scr"], r[dim]) for r in rows if r.get(dim) is not None]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        ax.scatter(xs, ys, s=18, alpha=0.8)
        r, p, n = compute_pearson(xs, ys)
        title = f"{dim}\nn={n}"
        if n >= 3 and not math.isnan(r):
            slope, intercept, _ = linreg(xs, ys)
            lo, hi = min(xs), max(xs)
            ax.plot([lo, hi], [slope * lo + intercept, slope * hi + intercept], color="crimson", lw=1.5)
            title = f"{dim}\nr={r:.2f}, p={p:.3g} {significance_label(p)} (n={n})"
        ax.set_title(title, fontsize=8)
        ax.set_xlabel("SCR (E1, macro)")
        ax.set_ylabel(f"micro-F1 {dim} (E2)")
    if synthetic:
        fig.suptitle("SYNTHETIC DEMO - random numbers, not results", color="red", fontsize=10)
    fig.tight_layout()
    paths = []
    for fmt in formats:
        path = out_dir / f"scr_vs_f1{'_synthetic' if synthetic else ''}.{fmt}"
        fig.savefig(path, dpi=200)
        paths.append(path)
    plt.close(fig)
    return paths


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="SCR (E1) vs F1 (E2) Pearson/regression figures from local metrics CSVs.")
    ap.add_argument("--metrics-dir", default=str(DEFAULT_METRICS_DIR),
                    help="directory searched recursively for e1_summary.csv and e2_summary.csv "
                         "(default results/metrics/local/)")
    ap.add_argument("--e1-csv", default=None, help="explicit e1_summary.csv (overrides the search)")
    ap.add_argument("--e2-csv", default=None, help="explicit e2_summary.csv (overrides the search)")
    ap.add_argument("--dataset", choices=rio.DATASETS + ("all",), default="all",
                    help="restrict the points to one dataset (default all)")
    ap.add_argument("--out-dir", default=None, help="figure directory (default figures/generated/, git-ignored)")
    ap.add_argument("--format", nargs="+", default=["png"], choices=["png", "pdf", "svg"], help="figure formats")
    ap.add_argument("--synthetic", action="store_true",
                    help="draw a watermarked demo from random numbers (ignores --metrics-dir)")
    ap.add_argument("--seed", type=int, default=0, help="seed for --synthetic (default 0)")
    return ap


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        out_dir = rio.assert_ignored_out_dir(args.out_dir or DEFAULT_OUT_DIR)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if args.synthetic:
        rows = synthetic_pairs(seed=args.seed)
    else:
        e1 = Path(args.e1_csv) if args.e1_csv else find_csv(args.metrics_dir, "e1_summary.csv")
        e2 = Path(args.e2_csv) if args.e2_csv else find_csv(args.metrics_dir, "e2_summary.csv")
        if not e1 or not e2 or not e1.is_file() or not e2.is_file():
            print("error: need e1_summary.csv and e2_summary.csv (run experiments/E1/evaluate.py and "
                  "experiments/E2/evaluate.py with --out-dir below --metrics-dir), or use --synthetic",
                  file=sys.stderr)
            return 2
        rows = pair_rows(rio.read_csv(e1), rio.read_csv(e2),
                         datasets=None if args.dataset == "all" else [args.dataset])
        if len(rows) < 3:
            print(f"error: only {len(rows)} paired (dataset, model, prompt) rows; need >= 3", file=sys.stderr)
            return 1
    try:
        paths = plot_scr_vs_f1(rows, out_dir, synthetic=args.synthetic, formats=args.format)
    except ImportError:
        print("error: matplotlib is required for plotting (pip install matplotlib)", file=sys.stderr)
        return 3
    for dim in ELEMENTS:
        xs = [r["scr"] for r in rows if r.get(dim) is not None]
        ys = [r[dim] for r in rows if r.get(dim) is not None]
        r, p, n = compute_pearson(xs, ys)
        print(f"{dim:12s} n={n:3d} r={r:+.3f} p={p:.4g} {significance_label(p)}")
    print("wrote " + ", ".join(str(p) for p in paths))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
