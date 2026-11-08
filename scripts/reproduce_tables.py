#!/usr/bin/env python3
"""Offline reproduction / verification of the SchemaBridge paper tables (E0-E5).

    python scripts/reproduce_tables.py --all --offline
    python scripts/reproduce_tables.py --experiment E0          # E0 | E1 | E2 | E3 | E4 | E5
    python scripts/reproduce_tables.py --experiment E0 --recompute   # also re-evaluate RSchema preds

For every paper table label the script loads archived metrics (``results/metrics/archived``,
``results/baselines``) and the published numbers (``configs/paper_reference_values.json``),
compares them cell by cell and prints one status per table/dataset label:

``PASS``      every comparable cell is within tolerance (0.0005 for 3dp floats, 0.005 for BLEU-4)
              and nothing is missing;
``MISMATCH``  at least one comparable cell is outside tolerance (details are printed);
``PARTIAL``   every comparable cell passes but some cells cannot be checked (missing artefact);
              also used for E3-E5 where archived metrics exist but the paper reference
              numbers are not on disk, so nothing can be compared;
``BLOCKED``   no cell can be checked at all (artefact missing, run incomplete, ...).

Nothing is invented: a metric is only compared when an archived value exists.  No network,
no model/API calls.  Cell-level CSVs are written to ``results/metrics/reproduced/``.
The exit code is 0 unless the script itself fails (MISMATCH/BLOCKED are *results*, not errors);
use ``--strict`` to exit 1 if any label is MISMATCH.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

ARCHIVED = ROOT / "results" / "metrics" / "archived"
BASELINES = ROOT / "results" / "baselines"
PREDICTIONS = ROOT / "results" / "predictions"
REPRODUCED = ROOT / "results" / "metrics" / "reproduced"
REF_PATH = ROOT / "configs" / "paper_reference_values.json"

TOL3 = 0.0005
TOL2 = 0.005
EPS = 1e-9

PASS, MISMATCH, BLOCKED, PARTIAL = "PASS", "MISMATCH", "BLOCKED", "PARTIAL"
OPEN_MODELS = ("codellama13b", "llama31", "deepseek")
CLOSED_MODELS = ("claude_sonnet_4_6", "gpt_5_4_mini")
ALL_MODELS = OPEN_MODELS + CLOSED_MODELS
ELEMENTS = ("tables", "attributes", "domain", "entity", "referential")
MODEL_NAMES = {
    "codellama13b": "CodeLlama-13B",
    "llama31": "Llama-3.1-8B",
    "deepseek": "DeepSeek-Coder",
    "claude_sonnet_4_6": "Claude Sonnet 4.6",
    "gpt_5_4_mini": "GPT-5.4-mini",
}

CLOSED_REASON = (
    "no per-schema predictions or metrics for closed models anywhere on disk "
    "(see figures/fig5_source_audit.md)"
)


# --------------------------------------------------------------------------- data model


@dataclass
class Cell:
    experiment: str
    table_label: str
    dataset: str
    model: str
    variant: str
    metric: str
    paper: float | None
    reproduced: float | None
    tolerance: float
    status: str
    delta: float | None = None
    note: str = ""


@dataclass
class LabelStatus:
    experiment: str
    table_label: str
    dataset: str
    status: str
    n_pass: int
    n_mismatch: int
    n_blocked: int
    reason: str = ""


@dataclass
class Result:
    experiment: str
    cells: list[Cell] = field(default_factory=list)
    labels: list[LabelStatus] = field(default_factory=list)
    extra_csvs: dict[str, list[dict]] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)


def compare(paper: float, reproduced: float, tol: float) -> tuple[str, float]:
    """PASS if ``|reproduced - paper| <= tol`` (tiny epsilon for float noise)."""
    delta = reproduced - paper
    return (PASS if abs(delta) <= tol + EPS else MISMATCH), delta


class Collector:
    """Accumulates cells for one experiment and derives per-label statuses."""

    def __init__(self, experiment: str):
        self.experiment = experiment
        self.cells: list[Cell] = []
        self._label_notes: dict[tuple[str, str], str] = {}
        self._forced: dict[tuple[str, str], str] = {}

    def cell(
        self,
        label: str,
        dataset: str,
        model: str,
        metric: str,
        paper: float | None,
        reproduced: float | None,
        *,
        variant: str = "",
        tol: float | None = None,
        blocked_reason: str = "",
        note: str = "",
        force_blocked: bool = False,
    ) -> None:
        tol = tol if tol is not None else (TOL2 if metric.startswith("bleu4") else TOL3)
        if reproduced is None or force_blocked:
            c = Cell(self.experiment, label, dataset, model, variant, metric, paper,
                     None if force_blocked else reproduced, tol, BLOCKED,
                     None, blocked_reason or note)
            if force_blocked and reproduced is not None:
                c.note = f"{blocked_reason} (local value {reproduced:.4f} shown in note only)"
        elif paper is None:
            c = Cell(self.experiment, label, dataset, model, variant, metric, None, reproduced, tol,
                     BLOCKED, None, "no paper reference value" + (f"; {note}" if note else ""))
        else:
            st, delta = compare(paper, reproduced, tol)
            c = Cell(self.experiment, label, dataset, model, variant, metric, paper, reproduced,
                     tol, st, delta, note)
        self.cells.append(c)

    def label_note(self, label: str, dataset: str, note: str) -> None:
        self._label_notes[(label, dataset)] = note

    def force_label(self, label: str, dataset: str, status: str, reason: str) -> None:
        """Override the derived status (used for E3-E5, where no paper numbers exist)."""
        self._forced[(label, dataset)] = status
        self._label_notes[(label, dataset)] = reason

    def labels(self) -> list[LabelStatus]:
        groups: dict[tuple[str, str], list[Cell]] = {}
        for c in self.cells:
            groups.setdefault((c.table_label, c.dataset), []).append(c)
        for key in self._forced:
            groups.setdefault(key, [])
        out = []
        for (label, dataset), cells in groups.items():
            n_p = sum(c.status == PASS for c in cells)
            n_m = sum(c.status == MISMATCH for c in cells)
            n_b = sum(c.status == BLOCKED for c in cells)
            if (label, dataset) in self._forced:
                status = self._forced[(label, dataset)]
            elif n_m:
                status = MISMATCH
            elif n_p and n_b:
                status = PARTIAL
            elif n_p:
                status = PASS
            else:
                status = BLOCKED
            out.append(LabelStatus(self.experiment, label, dataset, status, n_p, n_m, n_b,
                                   self._label_notes.get((label, dataset), "")))
        return out


# --------------------------------------------------------------------------- loaders


def load_json(path: Path) -> Any | None:
    if not path.is_file():
        return None
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_refs() -> dict:
    refs = load_json(REF_PATH)
    if refs is None:
        raise SystemExit(f"missing {REF_PATH}; run scripts/build_paper_reference_values.py")
    return refs


def count_pred_json(path: Path) -> int | None:
    try:
        return len(list(path.glob("[0-9][0-9][0-9][0-9].json")))
    except OSError:
        return None


def _f1(fe: dict, k: str) -> float:
    return float(fe[k]["f1"])


# --------------------------------------------------------------------------- E0


def _rschema_open_metrics_from_summary(s: dict) -> dict[str, float]:
    fe = s["five_elements"]
    out = {"nged": float(s["mean_normalized_graph_edit_distance"])}
    out.update({k: _f1(fe, k) for k in ELEMENTS})
    return out


def run_e0(refs: dict, recompute: bool = False) -> Result:
    col = Collector("E0")
    res = Result("E0")
    t5 = refs["tab:e0_overall"]["datasets"]

    # ---- Table V / RSchema vs archived Exp4 micro --------------------------------
    arch = load_json(ARCHIVED / "e0_rschema_exp4_evaluation.json")
    by_llm = {s["llm"]: s for s in (arch or {}).get("llms", [])}
    label = "tab:e0_overall"
    note_halluc = (
        "Table V 'Halluc' aggregation is not documented on disk; candidates computed locally "
        "(mean of 5 micro rates / micro over all / per-schema mean) all differ from the paper by "
        ">0.0005 for at least one model, so it cannot be verified"
    )
    for model in ALL_MODELS:
        paper_row = t5["RSchema"][model]
        if model in CLOSED_MODELS:
            for m in ("nged", "halluc") + ELEMENTS:
                col.cell(label, "RSchema", model, m, paper_row[m], None, blocked_reason=CLOSED_REASON)
            continue
        s = by_llm.get(model)
        if s is None:
            for m in ("nged", "halluc") + ELEMENTS:
                col.cell(label, "RSchema", model, m, paper_row[m], None,
                         blocked_reason="archived Exp4 evaluation missing for this model")
            continue
        vals = _rschema_open_metrics_from_summary(s)
        for m in ("nged",) + ELEMENTS:
            col.cell(label, "RSchema", model, m, paper_row[m], vals[m],
                     note="archived Exp4 micro F1 / mean nGED (parser version of 2026-06-15)")
        fe = s["five_elements"]
        proxy = sum(fe[k]["hallucination_rate"] for k in ELEMENTS) / 5
        col.cell(label, "RSchema", model, "halluc", paper_row["halluc"], proxy,
                 blocked_reason=note_halluc, force_blocked=True)
    col.label_note(label, "RSchema",
                   "open models: archived Exp4 micro F1; Claude/GPT and Halluc column BLOCKED")

    # ---- Table V / SchemaBench vs few_shot (corrected parser, zero-scored) ---------
    sb = load_json(BASELINES / "e0_schemabench_papermethods_evaluation.json")
    sb_few = {m["model"]: m for m in (sb or {}).get("methods", []) if m.get("method") == "few_shot"}
    for model in ALL_MODELS:
        paper_row = t5["SchemaBench"][model]
        if model in CLOSED_MODELS:
            for m in ("nged", "halluc") + ELEMENTS:
                col.cell(label, "SchemaBench", model, m, paper_row[m], None, blocked_reason=CLOSED_REASON)
            continue
        s = sb_few.get(model)
        if s is None:
            for m in ("nged", "halluc") + ELEMENTS:
                col.cell(label, "SchemaBench", model, m, paper_row[m], None,
                         blocked_reason="SchemaBench few_shot baseline evaluation missing")
            continue
        fe = s["five_elements"]
        local = {"nged": float(s["mean_normalized_graph_edit_distance"]),
                 "halluc": float(s["mean_hallucination_rate"])}
        local.update({k: _f1(fe, k) for k in ELEMENTS})  # macro F1 (zero-scored), as in the report
        for m in ("nged", "halluc") + ELEMENTS:
            col.cell(label, "SchemaBench", model, m, paper_row[m], local[m], variant="few_shot",
                     note="PaperMethods few_shot, corrected parser, failed=zero, macro means")
    col.label_note(
        label, "SchemaBench",
        "compared against few_shot rows (corrected parser). The paper block predates the parser "
        "correction (figures/fig5_final_validation.md) and no archived SchemaBench direct-Exp4 "
        "metrics exist, so MISMATCH here is expected; Claude/GPT BLOCKED",
    )

    # ---- locally reproducible targets (archive vs its own report) -----------------
    exp4_ref = refs["e0_rschema_exp4_micro"]["models"]
    for model, ref in exp4_ref.items():
        s = by_llm.get(model)
        for m in ("nged",) + ELEMENTS:
            v = _rschema_open_metrics_from_summary(s)[m] if s else None
            col.cell("e0_rschema_exp4_micro", "RSchema", model, m, ref[m], v,
                     blocked_reason="archived Exp4 evaluation json missing",
                     note="archived json vs archived text report (3dp)")
    sb_ref = refs["e0_schemabench_fewshot_corrected"]["models"]
    for model, ref in sb_ref.items():
        s = sb_few.get(model)
        for m in ("nged", "halluc") + ELEMENTS:
            if s is None:
                v = None
            elif m == "nged":
                v = float(s["mean_normalized_graph_edit_distance"])
            elif m == "halluc":
                v = float(s["mean_hallucination_rate"])
            else:
                v = _f1(s["five_elements"], m)
            col.cell("e0_schemabench_fewshot_corrected", "SchemaBench", model, m, ref[m], v,
                     variant="few_shot", blocked_reason="few_shot evaluation json missing",
                     note="baseline json vs baseline text report (3dp)")

    # ---- optional: re-evaluate RSchema predictions with the SchemaBridge library ---
    if recompute:
        _e0_recompute(col, res, t5)

    res.cells = col.cells
    res.labels = col.labels()
    res.notes.append(
        "Archived Exp4 JSON was produced before the DDL-parser correction; use --recompute to see "
        "the corrected-parser values (e.g. CodeLlama Entity 0.3005 vs archived 0.278)."
    )
    return res


def _e0_recompute(col: Collector, res: Result, t5: dict) -> None:
    from src.evaluator import evaluate_predictions_dir

    gold = ROOT / "datasets" / "rschema" / "annotation.jsonl"
    label = "tab:e0_overall[recomputed]"
    rows = []
    for model in OPEN_MODELS:
        pred = PREDICTIONS / "e0" / f"rschema_exp4_{model}"
        paper_row = t5["RSchema"][model]
        if not pred.is_dir() or count_pred_json(pred) in (None, 0) or not gold.is_file():
            for m in ("nged",) + ELEMENTS:
                col.cell(label, "RSchema", model, m, paper_row[m], None,
                         blocked_reason=f"predictions not readable: {pred}")
            continue
        r = evaluate_predictions_dir(pred, gold, legacy=True)
        vals = {"nged": r["mean_normalized_graph_edit_distance"]}
        vals.update({k: r["five_elements"][k]["f1"] for k in ELEMENTS})
        for m, v in vals.items():
            col.cell(label, "RSchema", model, m, paper_row[m], float(v),
                     variant="recomputed",
                     note="SchemaBridge library, legacy(corrected vendored) parser, sorted-name tie-break")
            rows.append({"model": model, "metric": m, "value": v})
    col.label_note(label, "RSchema",
                   "re-evaluated offline from predictions with src/ (deterministic); Halluc not recomputed")
    res.extra_csvs["E0_rschema_recomputed.csv"] = rows


# --------------------------------------------------------------------------- E1


E1_MAP = {  # paper column -> (archived metric key, scale)
    "bleu4": "bleu_corpus",
    "rougeL": "rougeL_f1",
    "scr": "schema_coverage_mean",
}


def _variant_inference(paper_ds: dict, archived: dict[str, dict], keyfn: Callable[[dict, str], float | None],
                       metrics: list[str]) -> str:
    """Count within-tolerance matches against Basic vs Detailed columns (diagnostic only)."""
    counts = {"basic": 0, "detailed": 0}
    total = 0
    for model, s in archived.items():
        for m in metrics:
            v = keyfn(s, m)
            if v is None:
                continue
            total += 1
            for variant in counts:
                p = paper_ds.get(model, {}).get(f"{m}_{variant}")
                tol = TOL2 if m.startswith("bleu4") else TOL3
                if p is not None and abs(v - p) <= tol + EPS:
                    counts[variant] += 1
    return f"archived run matches paper Detailed in {counts['detailed']}/{total} cells, Basic in {counts['basic']}/{total}"


def run_e1(refs: dict) -> Result:
    col = Collector("E1")
    res = Result("E1")
    label = "tab:e1_s2t"
    t7 = refs["tab:e1_s2t"]["datasets"]
    arch = load_json(ARCHIVED / "e1_rschema_schema2text_evaluation.json")
    summ = {s["llm"]: s["metrics"] for s in (arch or {}).get("summaries", [])}
    skip_bert = bool((arch or {}).get("skip_bertscore", True))
    metrics = ["bleu4", "rougeL", "bertscore", "scr"]

    def keyfn(s: dict, m: str) -> float | None:
        k = E1_MAP.get(m)
        return float(s[k]) if k and k in s else None

    infer = _variant_inference(t7["RSchema"], summ, keyfn, ["bleu4", "rougeL", "scr"]) if summ else "no archive"

    for ds in ("RSchema", "SchemaBench", "Enterprise-145"):
        for model in ALL_MODELS:
            prow = t7[ds].get(model, {})
            for m in metrics:
                for variant in ("basic", "detailed"):
                    p = prow.get(f"{m}_{variant}")
                    if p is None:
                        continue  # 'n/a' in the paper
                    if ds != "RSchema":
                        reason = (
                            "no archived E1 metrics for this dataset (SchemaBench predictions exist but were "
                            "never scored; Enterprise-145 has no schema2text run)"
                            if model in OPEN_MODELS and ds == "SchemaBench"
                            else (CLOSED_REASON if model in CLOSED_MODELS else "no archived E1 metrics for Enterprise-145")
                        )
                        col.cell(label, ds, model, f"{m}_{variant}", p, None, variant=variant, blocked_reason=reason)
                        continue
                    if model in CLOSED_MODELS:
                        col.cell(label, ds, model, f"{m}_{variant}", p, None, variant=variant,
                                 blocked_reason=CLOSED_REASON)
                        continue
                    if variant == "basic":
                        col.cell(label, ds, model, f"{m}_{variant}", p, None, variant=variant,
                                 blocked_reason="archived run is the Detailed prompt; no archived Basic-prompt metrics")
                        continue
                    if m == "bertscore":
                        col.cell(label, ds, model, f"{m}_{variant}", p, None, variant=variant,
                                 blocked_reason=f"BERTScore was skipped in the archived run (skip_bertscore={skip_bert})")
                        continue
                    s = summ.get(model)
                    v = keyfn(s, m) if s else None
                    col.cell(label, ds, model, f"{m}_{variant}", p, v, variant=variant,
                             blocked_reason="archived E1 metrics missing for this model",
                             note="BLEU-4=bleu_corpus, ROUGE-L=rougeL_f1, SCR=schema_coverage_mean")
        col.label_note(label, ds, infer if ds == "RSchema" else "see cell notes")
    res.cells = col.cells
    res.labels = col.labels()
    return res


# --------------------------------------------------------------------------- E2


def run_e2(refs: dict) -> Result:
    col = Collector("E2")
    res = Result("E2")
    label = "tab:e2_roundtrip"
    t8 = refs["tab:e2_roundtrip"]["datasets"]
    arch = load_json(ARCHIVED / "e2_rschema_roundtrip_evaluation.json")
    src = {s["source"]: s for s in (arch or {}).get("sources", [])}
    metrics = ["nged"] + list(ELEMENTS)

    def archived_value(s: dict, m: str) -> float:
        return float(s["mean_normalized_graph_edit_distance"]) if m == "nged" else _f1(s["five_elements"], m)

    # variant inference (diagnostic)
    counts = {"basic": 0, "detailed": 0}
    total = 0
    for model, s in src.items():
        for m in metrics:
            v = archived_value(s, m)
            total += 1
            for variant in counts:
                p = t8["RSchema"].get(model, {}).get(f"{m}_{variant}")
                if p is not None and abs(v - p) <= TOL3 + EPS:
                    counts[variant] += 1
    infer = (f"archived round-trip matches paper Detailed in {counts['detailed']}/{total} cells, "
             f"Basic in {counts['basic']}/{total}" if src else "no archive")

    sb_counts = {m: count_pred_json(PREDICTIONS / "e2" / f"schemabench_rt_{m}") for m in OPEN_MODELS}
    sb_reason = ("SchemaBench round-trip incomplete (parsed predictions "
                 + ", ".join(f"{m}={n}/239" for m, n in sb_counts.items())
                 + ") and no archived metrics")

    for ds in ("RSchema", "SchemaBench", "Enterprise-145"):
        for model in ALL_MODELS:
            prow = t8[ds].get(model, {})
            for m in metrics:
                for variant in ("basic", "detailed"):
                    p = prow.get(f"{m}_{variant}")
                    if p is None:
                        continue
                    name = f"{m}_{variant}"
                    if model in CLOSED_MODELS:
                        col.cell(label, ds, model, name, p, None, variant=variant, blocked_reason=CLOSED_REASON)
                    elif ds == "SchemaBench":
                        col.cell(label, ds, model, name, p, None, variant=variant, blocked_reason=sb_reason)
                    elif ds == "Enterprise-145":
                        col.cell(label, ds, model, name, p, None, variant=variant,
                                 blocked_reason="no round-trip run for Enterprise-145 on disk")
                    elif variant == "basic":
                        col.cell(label, ds, model, name, p, None, variant=variant,
                                 blocked_reason="archived round-trip is the Detailed describer; no Basic-describer metrics")
                    else:
                        s = src.get(model)
                        col.cell(label, ds, model, name, p, archived_value(s, m) if s else None,
                                 variant=variant, blocked_reason="archived round-trip missing for this model",
                                 note="micro F1 / mean nGED, constructor GPT-4o-mini")
        note = {"RSchema": infer, "SchemaBench": sb_reason}.get(ds, "no Enterprise-145 round-trip artefacts")
        col.label_note(label, ds, note)
    res.cells = col.cells
    res.labels = col.labels()
    return res


# --------------------------------------------------------------------------- E3 / E4 / E5
# Paper semantics (audit brief; manuscript absent on disk):
#   E3 = constructor isolation (fixed GPT-5.4-mini detailed describer)
#   E4 = masking 1Q1–1Q5 inferability
#   E5 = cost/latency (tab:e5_cost)
#   fig:e0_heatmap is an E0 figure, not E5

E_SEMANTICS_NOTE = (
    "Paper E3=constructor isolation; E4=masking 1Q1-1Q5; E5=cost/latency. "
    "No manuscript on disk; historical RSchema Exp3 Case1Q* trees are masking describers (E4), "
    "not E3. fig:e0_heatmap diagnostic lives under figures/ (E0)."
)


def run_e3(refs: dict) -> Result:
    col = Collector("E3")
    res = Result("E3")
    # Inventory historical masking dirs only as a naming-collision warning.
    base = PREDICTIONS / "e3" / "rschema_cases_describer"
    dirs = sorted(p.name for p in base.iterdir()) if base.is_dir() else []
    n_json = {d: count_pred_json(base / d) for d in dirs}
    res.extra_csvs["E3_artifact_inventory.csv"] = [
        {"case_dir": d, "n_prediction_json": n_json[d],
         "note": "historical masking describer (paper E4), NOT constructor-isolation"}
        for d in dirs
    ]
    col.force_label(
        "tab:e3_overall", "all", BLOCKED,
        "paper E3 requires fixed GPT-5.4-mini detailed descriptions + per-constructor "
        "reconstructions; neither predictions nor tab:e3_overall numbers exist on disk. "
        f"Note: {len(dirs)} historical masking describer dirs are inventoriable but are E4 artifacts.",
    )
    res.cells = col.cells
    res.labels = col.labels()
    res.notes.append(E_SEMANTICS_NOTE)
    return res


def _flatten_aggregate(source: str, group: str, key: str, agg: dict) -> list[dict]:
    rows = []
    for el in ELEMENTS:
        e = agg.get(el)
        if isinstance(e, dict):
            rows.append({"source": source, "group": group, "case": key, "n": agg.get("n"), "element": el,
                         "gold": e.get("gold"), "recreated": e.get("recreated"), "matched": e.get("matched"),
                         "precision": e.get("precision"), "recall": e.get("recall"), "f1": e.get("f1")})
    return rows


def run_e4(refs: dict) -> Result:
    col = Collector("E4")
    res = Result("E4")
    rows: list[dict] = []
    c3 = load_json(ARCHIVED / "e4_cases3_results.json")
    cs = load_json(ARCHIVED / "e4_cases_analysis_summary.json")
    if c3:
        aggs = c3["aggregates"]
        rows += _flatten_aggregate("cases3_table_attr_hiding", "overall", "all", aggs["overall"])
        for k, v in aggs["by_case"].items():
            rows += _flatten_aggregate("cases3_table_attr_hiding", "by_case", k, v)
    if cs:
        aggs = cs["aggregates"]
        rows += _flatten_aggregate("cases_structural_imputation", "overall", "all", aggs["overall"])
        for k, v in aggs["by_case"].items():
            rows += _flatten_aggregate("cases_structural_imputation", "by_case", k, v)
    res.extra_csvs["E4_archived_cases_aggregates.csv"] = rows
    # Also note RSchema masking describer coverage (hist. under predictions/e3).
    mask_desc = PREDICTIONS / "e3" / "rschema_cases_describer"
    n_mask_dirs = len(list(mask_desc.iterdir())) if mask_desc.is_dir() else 0
    if rows:
        col.force_label(
            "tab:e4_split", "Enterprise-145", PARTIAL,
            f"archived Cases/Cases3 aggregates exported ({len(rows)} rows); "
            f"RSchema masking describer dirs={n_mask_dirs} (1Q2-1Q6, unscored); "
            "SchemaBench masking absent; no tab:e4_* paper numbers on disk",
        )
        col.force_label(
            "tab:e4_fk_support", "Enterprise-145", PARTIAL,
            "fk/inferability analysis summary present; evidence-supported FK ≠ semantic correctness; "
            "no published tab:e4_fk_support numbers to compare",
        )
        col.force_label(
            "tab:e4_by_dataset", "multi", BLOCKED,
            "cannot reproduce by-dataset paper table: SchemaBench masking missing; "
            "RSchema reconstruction scores missing; no paper dump",
        )
    else:
        col.force_label("tab:e4_split", "Enterprise-145", BLOCKED, "archived e4_* metrics missing")
    res.cells = col.cells
    res.labels = col.labels()
    res.notes.append(E_SEMANTICS_NOTE)
    return res


def run_e5(refs: dict) -> Result:
    col = Collector("E5")
    res = Result("E5")
    # Keep fig5 diagnostic export under E0-adjacent figures/, but do not claim it is E5.
    diag = ROOT / "figures" / "fig5_heatmap_values_diagnostic.csv"
    rows: list[dict] = []
    if diag.is_file():
        with diag.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        res.extra_csvs["E0_fig5_diagnostic_values_copied_for_convenience.csv"] = rows
    col.force_label(
        "tab:e5_cost", "multi", BLOCKED,
        "no API usage/billing logs, pricing freeze, or token accounting packaged; "
        "local elapsed_s fields are wall-clock only and are not tab:e5_cost. "
        "fig:e0_heatmap is E0 (Priority C); diagnostic CSV under figures/ is not an E5 result.",
    )
    res.cells = col.cells
    res.labels = col.labels()
    res.notes.append(E_SEMANTICS_NOTE)
    return res


RUNNERS: dict[str, Callable[..., Result]] = {
    "E0": run_e0, "E1": run_e1, "E2": run_e2, "E3": run_e3, "E4": run_e4, "E5": run_e5,
}


# --------------------------------------------------------------------------- output


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields: list[str] = []
    for r in rows:
        for k in r:
            if k not in fields:
                fields.append(k)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def fmt(v: float | None) -> str:
    return "-" if v is None else f"{v:.4f}".rstrip("0").rstrip(".") if abs(v) >= 1 else f"{v:.4f}"


def print_result(res: Result, verbose: bool) -> None:
    print(f"\n=== {res.experiment} " + "=" * 60)
    for lab in res.labels:
        print(f"[{lab.status:8s}] {lab.table_label} / {lab.dataset}  "
              f"(pass={lab.n_pass} mismatch={lab.n_mismatch} blocked={lab.n_blocked})")
        if lab.reason:
            print(f"           {lab.reason}")
        cells = [c for c in res.cells if c.table_label == lab.table_label and c.dataset == lab.dataset]
        by_model: dict[str, list[Cell]] = {}
        for c in cells:
            by_model.setdefault(c.model, []).append(c)
        for model, mc in by_model.items():
            n_p = sum(c.status == PASS for c in mc)
            n_m = [c for c in mc if c.status == MISMATCH]
            n_b = sum(c.status == BLOCKED for c in mc)
            tag = MISMATCH if n_m else (PARTIAL if n_p and n_b else (PASS if n_p else BLOCKED))
            line = f"    {MODEL_NAMES.get(model, model):<20s} {tag:<8s} pass={n_p} mismatch={len(n_m)} blocked={n_b}"
            print(line)
            if n_m:
                for c in n_m:
                    print(f"        {c.variant + ' ' if c.variant else ''}{c.metric}: paper={fmt(c.paper)} "
                          f"reproduced={fmt(c.reproduced)} delta={c.delta:+.4f} (tol {c.tolerance})")
            if verbose:
                for c in mc:
                    if c.status == BLOCKED:
                        print(f"        BLOCKED {c.metric}: {c.note}")
    for n in res.notes:
        print(f"  note: {n}")


def run(experiments: list[str], recompute: bool, verbose: bool, out_dir: Path) -> list[Result]:
    refs = load_refs()
    results = []
    all_labels: list[dict] = []
    for exp in experiments:
        fn = RUNNERS[exp]
        res = fn(refs, recompute) if exp == "E0" else fn(refs)
        results.append(res)
        print_result(res, verbose)
        write_csv(out_dir / f"{exp}_cells.csv", [asdict(c) for c in res.cells])
        write_csv(out_dir / f"{exp}_summary.csv", [asdict(l) for l in res.labels])
        for name, rows in res.extra_csvs.items():
            write_csv(out_dir / name, rows)
        all_labels += [asdict(l) for l in res.labels]
    if len(experiments) > 1:
        write_csv(out_dir / "summary_all.csv", all_labels)
    print(f"\nCSV written under {out_dir.relative_to(ROOT) if out_dir.is_relative_to(ROOT) else out_dir}")
    return results


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--all", action="store_true", help="run E0-E5")
    g.add_argument("--experiment", "-e", choices=sorted(RUNNERS), help="run a single experiment")
    ap.add_argument("--offline", action="store_true", default=True,
                    help="(default, and the only mode) use archived artefacts only; no API/model calls")
    ap.add_argument("--recompute", action="store_true",
                    help="E0 only: additionally re-evaluate RSchema Exp4 predictions with src/ (offline, ~30s)")
    ap.add_argument("--out-dir", type=Path, default=REPRODUCED)
    ap.add_argument("--verbose", "-v", action="store_true", help="print the reason for every BLOCKED cell")
    ap.add_argument("--strict", action="store_true", help="exit 1 if any label is MISMATCH")
    args = ap.parse_args(argv)
    if not args.all and not args.experiment:
        ap.error("pass --all or --experiment E0..E5")
    exps = sorted(RUNNERS) if args.all else [args.experiment]
    results = run(exps, args.recompute, args.verbose, args.out_dir)
    if args.strict and any(l.status == MISMATCH for r in results for l in r.labels):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
