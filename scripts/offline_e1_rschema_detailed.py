#!/usr/bin/env python3
"""Offline E1 RSchema detailed metrics from archived per_record JSONL."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "metrics" / "reproduced"
OUT.mkdir(parents=True, exist_ok=True)

import sacrebleu
from rouge_score import rouge_scorer

PAPER = {
    "codellama13b": {"bleu4": 16.35, "rougeL": 0.232, "scr": 0.928},
    "llama31": {"bleu4": 24.21, "rougeL": 0.262, "scr": 0.756},
    "deepseek": {"bleu4": 13.70, "rougeL": 0.223, "scr": 0.971},
}

rouge = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
rows = []
for model, paper in PAPER.items():
    path = ROOT / "results/metrics/archived/e1_rschema_per_record" / f"per_record_{model}.jsonl"
    refs, hyps, scrs = [], [], []
    with path.open() as f:
        for line in f:
            o = json.loads(line)
            refs.append(o.get("gold_nl") or "")
            hyps.append(o.get("hyp_nl") or "")
            scrs.append(float(o["schema_coverage"]))
    bleu = sacrebleu.corpus_bleu(hyps, [[r] for r in refs]).score
    rl = sum(rouge.score(r, h)["rougeL"].fmeasure for r, h in zip(refs, hyps)) / len(refs)
    scr = sum(scrs) / len(scrs)
    row = {
        "model": model,
        "n": len(refs),
        "bleu4": bleu,
        "rougeL": rl,
        "scr": scr,
        "match_bleu": abs(bleu - paper["bleu4"]) < 0.005,
        "match_rouge": abs(rl - paper["rougeL"]) < 0.0005,
        "match_scr": abs(scr - paper["scr"]) < 0.0005,
    }
    rows.append(row)
    print(model, {k: row[k] for k in ("bleu4", "rougeL", "scr", "match_bleu", "match_rouge", "match_scr")})

(OUT / "E1_rschema_detailed_offline.json").write_text(json.dumps(rows, indent=2) + "\n")
print("wrote", OUT / "E1_rschema_detailed_offline.json")
