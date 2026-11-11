"""Pearson / regression helpers of scripts/plot_e1_e2_figures.py on synthetic arrays."""
import math

import pytest

from _synthetic import ROOT, load_script

plot = load_script("scripts/plot_e1_e2_figures.py", "plot_e1_e2")


def test_perfect_positive_and_negative_correlation():
    x = [0.1, 0.2, 0.3, 0.4, 0.5]
    r, p, n = plot.compute_pearson(x, [2 * v + 1 for v in x])
    assert (n, round(r, 12), p) == (5, 1.0, 0.0)
    r, p, _ = plot.compute_pearson(x, [-3 * v for v in x])
    assert round(r, 12) == -1.0 and p == 0.0


def test_known_correlation_value():
    # classic textbook sample: r = 0.8 for these ranks of deviations
    x, y = [1, 2, 3, 4, 5], [2, 1, 4, 3, 5]
    r, p, n = plot.compute_pearson(x, y)
    assert r == pytest.approx(0.8) and n == 5
    t = r * math.sqrt(3 / (1 - r * r))
    assert 0.0 < p < 0.2 and p == pytest.approx(plot.pearson_p_value(r, 5))
    assert t == pytest.approx(2.309401, rel=1e-5)


def test_p_value_matches_closed_forms_for_small_df():
    # df = 1 (Cauchy):  p = 1 - (2/pi) * atan(|t|);  df = 2:  p = 1 - |t| / sqrt(t^2 + 2)
    for r in (0.3, 0.6, -0.9):
        t1 = abs(r) * math.sqrt(1 / (1 - r * r))
        assert plot.pearson_p_value(r, 3) == pytest.approx(1 - 2 / math.pi * math.atan(t1), abs=1e-9)
        t2 = abs(r) * math.sqrt(2 / (1 - r * r))
        assert plot.pearson_p_value(r, 4) == pytest.approx(1 - t2 / math.sqrt(t2 * t2 + 2), abs=1e-9)


def test_undefined_cases_are_nan():
    r, p, _ = plot.compute_pearson([1, 1, 1], [1, 2, 3])
    assert math.isnan(r) and math.isnan(p)
    r, p, n = plot.compute_pearson([1.0], [2.0])
    assert math.isnan(r) and n == 1
    with pytest.raises(ValueError):
        plot.compute_pearson([1, 2], [1])


def test_linreg_exact_line_and_r2():
    x = [0.0, 1.0, 2.0, 3.0]
    slope, intercept, r2 = plot.linreg(x, [2 * v + 0.5 for v in x])
    assert (round(slope, 12), round(intercept, 12), round(r2, 12)) == (2.0, 0.5, 1.0)
    slope, intercept, r2 = plot.linreg([1, 2, 3, 4], [1, 3, 2, 4])
    assert slope == pytest.approx(0.8) and intercept == pytest.approx(0.5) and r2 == pytest.approx(0.64)
    with pytest.raises(ValueError):
        plot.linreg([1, 1], [1, 2])


def test_significance_labels():
    assert [plot.significance_label(p) for p in (0.0005, 0.005, 0.03, 0.2)] == ["***", "**", "*", "n.s."]
    assert plot.significance_label(float("nan")) == "n/a"


def test_pair_rows_joins_on_dataset_model_prompt():
    e1 = [{"dataset": "rschema", "model": "m", "prompt": "basic", "scr_macro": "0.5"},
          {"dataset": "rschema", "model": "m", "prompt": "detailed", "scr_macro": "N/A"},
          {"dataset": "rschema", "model": "z", "prompt": "basic", "scr_macro": "0.9"}]
    e2 = [{"dataset": "rschema", "describer_model": "m", "prompt": "basic", **{f"f1_{e}": "0.25" for e in plot.ELEMENTS}},
          {"dataset": "rschema", "describer_model": "m", "prompt": "detailed", **{f"f1_{e}": "0.1" for e in plot.ELEMENTS}}]
    rows = plot.pair_rows(e1, e2)
    assert len(rows) == 1 and rows[0]["scr"] == 0.5 and rows[0]["tables"] == 0.25


def test_synthetic_pairs_are_reproducible_and_correlated():
    a, b = plot.synthetic_pairs(seed=3), plot.synthetic_pairs(seed=3)
    assert a == b and len(a) == 24
    r, p, n = plot.compute_pearson([row["scr"] for row in a], [row["attributes"] for row in a])
    assert r > 0.5 and p < 0.01 and n == 24


def test_plot_writes_only_to_out_dir(tmp_path):
    pytest.importorskip("matplotlib")
    paths = plot.plot_scr_vs_f1(plot.synthetic_pairs(), tmp_path / "figs", synthetic=True)
    assert [p.name for p in paths] == ["scr_vs_f1_synthetic.png"] and paths[0].stat().st_size > 1000
    assert plot.main(["--synthetic", "--out-dir", str(tmp_path / "cli")]) == 0
    assert plot.main(["--synthetic", "--out-dir", str(ROOT / "scripts")]) == 2  # tracked location refused
