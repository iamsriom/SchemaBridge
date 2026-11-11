#!/usr/bin/env python3
"""Classify every Table V MISMATCH cell of ``audit/E0_PAPER_COMPARISON.csv`` (offline).

Cause codes
  A different prediction snapshot        B different gold reference
  C different parser / normalisation     D different aggregation method
  E different metric definition          F genuine defect in current evaluator
  G manuscript copied from older result  H rounding / precision only

``CauseCode`` is the *technical* cause of the Paper-vs-Genuine gap.  ``G`` is recorded as a
secondary tag in ``Evidence`` (``also_G``) whenever the manuscript value equals the value of the
historical (Exp3/Exp4) evaluator re-run on the same byte-identical predictions.

Inputs (all produced offline by the audit scripts)
  audit/E0_PAPER_COMPARISON.csv                       mismatching cells + Paper
  results/metrics/reproduced/E0_TABLE_V_FINAL.csv     Genuine (current evaluator, full precision)
  audit/e0_table_v_mismatch/historical_rerun_cells.csv  Historical evaluator re-run
  audit/e0_table_v_mismatch/ablation_waterfall.csv    current code, toggled one factor at a time
  audit/e0_table_v_mismatch/ablation_p1.csv           genuine protocol + JSON-metadata structure
  audit/e0_table_v_mismatch/evaluator_at_commit_b626767_table_v.csv  Table V by the evaluator at repo commit b626767
  audit/e0_table_v_mismatch/counterfactual_parser_fixes.csv  genuine protocol + diagnostic parser fixes

Decision rules (applied in order; thresholds are explicit constants below)
  1. nGED / Hall: Paper == Historical and the names-only (nGED) or Hall4 toggle moves the value
     by >= EPS_PROTOCOL                       -> E
  2. RSchema Domain: Paper == Historical and the Domain-gold toggle (synthetic 518 -> DDL 381)
     moves the value by >= EPS_PROTOCOL       -> B
  3. |Paper - Genuine| <= EPS_ROUND            -> H   (genuine lies within 1e-4 of the paper's
     printed rounding interval; P1 / Historical noted as secondary evidence)
  4. Row-level: the JSON-metadata-structure re-score (P1) reproduces >=3 Paper cells of the row AND
     every schema whose JSON table list != DDL table list is a schema whose DDL the current parser
     truncates (header count > parsed tables)  -> F (parser swallows tables; paper used JSON tables)
  5. P1 reproduces the Paper cell but the row is not purely F2 truncation -> C (prediction-structure source)
  6. Defect counterfactual: cf = whichever of {fix F1+F2+F3, fix F1+F2+F3+F5} lands closer to the paper.
     share = (cf - g) / (p - g).  F1-F3 are defects the historical evaluator did not have; F5 (escaped
     newlines) hurts both evaluators differently.  If 0.5 <= share <= 1.5 and |cf-g| >= EPS_DEFECT -> F
  7. otherwise                                 -> C
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.normalization import normalize_rschema_name as nn  # noqa: E402
from src.schema_parser import metadata_from_ddl  # noqa: E402

AUD = ROOT / "audit"
D = AUD / "e0_table_v_mismatch"
PRED = ROOT / "results" / "predictions" / "e0"
PRED_DIR = {
    ("RSchema", "CodeLlama-13B"): "rschema_exp4_codellama13b",
    ("RSchema", "Llama-3.1-8B"): "rschema_exp4_llama31",
    ("RSchema", "DeepSeek-Coder-6.7B"): "rschema_exp4_deepseek",
    ("RSchema", "Claude Sonnet 4.6"): "rschema_exp4_claude_sonnet_4_6",
    ("RSchema", "GPT-5.4-mini"): "rschema_exp4_gpt_5_4_mini",
    ("SchemaBench", "CodeLlama-13B"): "schemabench_exp2_codellama13b",
    ("SchemaBench", "Llama-3.1-8B"): "schemabench_exp2_llama31",
    ("SchemaBench", "DeepSeek-Coder-6.7B"): "schemabench_exp2_deepseek",
    ("SchemaBench", "Claude Sonnet 4.6"): "schemabench_exp2_claude_sonnet_4_6",
    ("SchemaBench", "GPT-5.4-mini"): "schemabench_exp2_gpt_5_4_mini",
}
EPS_PAPER_MATCH = 0.0005   # 3-dp match
EPS_HIST = 0.0015          # paper == historical: 3-dp rounding + vendored PYTHONHASHSEED tie-break noise (~5e-4 each)
EPS_PROTOCOL = 0.01
EPS_ROUND = 0.0006
EPS_DEFECT = 0.001
HEADER = re.compile(r"CREATE\s+TABLE", re.IGNORECASE)
METRIC_NAME = {"nged": "nGED", "halluc": "Hall4", "tables": "Tables F1", "attributes": "Attr F1",
               "domain": "Domain F1", "entity": "Entity F1", "referential": "Ref F1"}


def load(path, key=("dataset", "model")):
    return {tuple(r[k] for k in key): r for r in csv.DictReader(open(path))}


def structure_stats(ds, model):
    """(#schemas JSON tables != DDL tables, #schemas DDL loses tables, #both)."""
    dis = lost = both = 0
    for p in (PRED / PRED_DIR[(ds, model)]).glob("[0-9][0-9][0-9][0-9].json"):
        x = json.loads(p.read_text(encoding="utf-8"))
        ddl = x.get("ddl") or ""
        parsed = metadata_from_ddl(ddl)["tables"]
        jt = (x.get("metadata") or {}).get("tables") or []
        df = {nn(t) for t in parsed} != {nn(t) for t in jt}
        ls = len(HEADER.findall(ddl)) > len(parsed)
        dis += df
        lost += ls
        both += df and ls
    return dis, lost, both


def main() -> int:
    comp = [r for r in csv.DictReader(open(AUD / "E0_PAPER_COMPARISON.csv"))
            if r["Table"] == "V" and r["Status"] == "MISMATCH"]
    gen = load(ROOT / "results/metrics/reproduced/E0_TABLE_V_FINAL.csv")
    hist = load(D / "historical_rerun_cells.csv")
    wf = {(r["dataset"], r["model"], r["step"]): r for r in csv.DictReader(open(D / "ablation_waterfall.csv"))}
    p1 = load(D / "ablation_p1.csv")
    old = load(D / "evaluator_at_commit_b626767_table_v.csv")
    cfs = {(r["variant"], r["dataset"], r["model"]): r
           for r in csv.DictReader(open(D / "counterfactual_parser_fixes.csv"))}
    stats = {k: structure_stats(*k) for k in PRED_DIR}

    # row-level: does P1 reproduce >= 3 paper cells and are all JSON!=DDL schemas F2-truncated?
    manu = json.load(open(AUD / "E0_CURRENT_MANUSCRIPT_VALUES.json"))["tab:e0_overall"]
    metrics = list(METRIC_NAME)
    row_f2 = {}
    for (ds, m), (dis, lost, both) in stats.items():
        n_p1 = sum(abs(round(float(p1[(ds, m)][k]), 3) - manu[f"{ds}|{m}"][k]) <= EPS_PAPER_MATCH + 1e-9
                   for k in metrics)
        row_f2[(ds, m)] = (n_p1 >= 3 and dis > 0 and dis == both, n_p1)

    out = []
    for r in comp:
        ds, m, k = r["Dataset"], r["Model"], r["Metric"]
        paper = float(r["Paper"])
        g = float(gen[(ds, m)][k])
        h = float(hist[(ds, m)]["halluc_5dim_micro_mean" if k == "halluc" else k])
        w2 = float(wf[(ds, m, "W2_ddl_authoritative")][k])
        w3 = float(wf[(ds, m, "W3_names_only_nged")][k])
        w4 = float(wf[(ds, m, "W4_domain_ddl_gold")][k])
        w5 = float(wf[(ds, m, "W5_hall4_genuine")][k])
        q = float(p1[(ds, m)][k])
        cf123 = float(cfs[("fix_F1_F2_F3", ds, m)][k])
        cf1235 = float(cfs[("fix_F1_F2_F3_F5", ds, m)][k])
        cf = min((cf123, cf1235), key=lambda v: abs(v - paper))
        assert abs(w5 - g) < 5e-7, (ds, m, k, w5, g)  # waterfall end-state == genuine
        e_comp = (w3 - w2) if k == "nged" else (w5 - w4) if k == "halluc" else 0.0
        b_comp = (w4 - w3) if (k in ("domain", "halluc") and ds == "RSchema") else 0.0
        struct = w2 - h
        diff = paper - g
        paper_eq_hist = abs(h - paper) <= EPS_HIST
        paper_eq_p1 = abs(round(q, 3) - paper) <= EPS_PAPER_MATCH + 1e-9
        dis, lost, both = stats[(ds, m)]
        row_is_f2, n_p1 = row_f2[(ds, m)]

        tags = []
        if paper_eq_hist:
            tags.append("also_G")
        if abs(float(old[(ds, m)][k]) - paper) <= EPS_PAPER_MATCH + 1e-9:
            tags.append("paper==evaluator@b626767")
        if abs(cf1235 - g) >= 0.005:
            tags.append(f"current_value_affected_by_parser_defects(F1-3,5 fix moves it {cf1235 - g:+.4f})")

        if paper_eq_hist and k in ("nged", "halluc") and abs(e_comp) >= EPS_PROTOCOL:
            code = "E"
            why = (f"metric definition: {'typed attribute labels (name,type,nullable; RSchema gold synthetic varchar NOT NULL) -> names-only' if k == 'nged' else 'Hall = mean of 5 micro rates incl. Domain -> Hall4 (T,A,E,R)'}"
                   f" shifts {e_comp:+.4f}")
            if k == "halluc" and abs(b_comp) >= 0.005:
                why += f"; Domain-gold swap (synthetic 518 -> DDL 381) shifts Hall5 {b_comp:+.4f}"
        elif paper_eq_hist and k == "domain" and ds == "RSchema" and abs(b_comp) >= EPS_PROTOCOL:
            code = "B"
            why = (f"gold reference: Domain scored vs synthetic varchar(255) NOT NULL logical gold (518 schemas) in paper/historical; "
                   f"current uses real DDL gold (381 schemas) -> {b_comp:+.4f}")
        elif abs(diff) <= EPS_ROUND:
            code = "H"
            why = (f"rounding/precision: genuine {g:.6f} is {abs(diff) - 0.0005:+.6f} outside the paper's 3-dp interval"
                   + (f"; JSON-structure re-score P1={q:.4f} also reproduces paper (secondary C)" if paper_eq_p1 else ""))
        elif row_is_f2 and paper_eq_p1 or (row_is_f2 and abs(q - paper) <= 0.002):
            code = "F"
            why = (f"parser defect F2: {lost} schemas have unterminated CREATE TABLE bodies (missing ')' before ENGINE) -> current "
                   f"DDL-authoritative parse drops later tables; paper used prediction-JSON table list (P1={q:.4f} vs paper {paper:.3f}); "
                   f"defect-fixed cfF1235={cf1235:.4f}")
        elif paper_eq_p1 and not row_is_f2:
            code = "C"
            why = (f"prediction-structure source: paper reproduced by genuine protocol with prediction-JSON metadata structure "
                   f"(P1={q:.4f}; row reproduced {n_p1}/7); current DDL-authoritative={g:.4f}; JSON!=DDL table list in {dis} schemas "
                   f"({lost} with DDL table loss)")
        else:
            d_cf = cf - g
            share = (cf - g) / (paper - g) if paper != g else 0.0
            if abs(d_cf) >= EPS_DEFECT and 0.5 <= share <= 1.5:
                code = "F"
                why = (f"parser defects F1/F2/F3(/F5) explain {share:.0%} of the gap: fixing them moves current {d_cf:+.4f} toward paper "
                       f"(gap {diff:+.4f}); hist->current structure residual {struct:+.4f}")
            else:
                code = "C"
                if paper_eq_p1:
                    why = (f"prediction-structure source / parser revision: paper reproduced by genuine protocol with JSON-metadata structure "
                           f"(P1={q:.4f}); current DDL-authoritative={g:.4f}; JSON!=DDL table list in {dis} schemas")
                elif paper_eq_hist:
                    why = (f"parser: legacy (hist {h:.4f}) -> robust parser (current {w2:.4f} typed/synthetic baseline), structure residual {struct:+.4f}; "
                           f"incl. vendored PYTHONHASHSEED tie-break noise +/-5e-4")
                else:
                    why = (f"parser revision not reproducible from repo history (hist {h:.4f}, P1 {q:.4f}, cf {cf:.4f}); "
                           f"paper lies between legacy and robust parser states")
        evidence = (f"{why}; hist={h:.4f}; W2typed={w2:.4f}; P1={q:.4f}; cfF123={cf123:.4f}; cfF1235={cf1235:.4f}"
                    + (f"; {';'.join(tags)}" if tags else ""))
        out.append({
            "Dataset": ds, "Model": m, "Metric": METRIC_NAME[k],
            "Paper": f"{paper:.3f}", "Historical": f"{h:.4f}", "Genuine": f"{g:.6f}",
            "Diff_Paper_Genuine": f"{diff:+.6f}", "CauseCode": code, "Evidence": evidence,
        })

    fields = ["Dataset", "Model", "Metric", "Paper", "Historical", "Genuine", "Diff_Paper_Genuine", "CauseCode", "Evidence"]
    dst = AUD / "E0_TABLE_V_MISMATCH_CLASSIFICATION.csv"
    with dst.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(out)
    dist = defaultdict(int)
    also_g = 0
    for o in out:
        dist[o["CauseCode"]] += 1
        also_g += "also_G" in o["Evidence"]
    print(f"wrote {dst} ({len(out)} cells)  generated {date.today()}")
    print("distribution:", dict(sorted(dist.items())), "| paper==historical (also_G):", also_g)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
