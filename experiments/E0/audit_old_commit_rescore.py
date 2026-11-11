#!/usr/bin/env python3
"""Re-score Table V with the evaluator checked out at an OLD commit (audit only).

Setup (outside the repo):  git archive <commit> src experiments configs scripts datasets | tar -x -C /tmp/wt
then symlink datasets/rschema, datasets/schemabench, results/predictions and run this file with
``root`` pointing at the extracted tree.  Used for commit b626767 (2026-11-10 14:05): that evaluator
(``ensure_prediction_metadata`` = prediction-JSON metadata preferred) reproduces 35/35 manuscript cells
of RSchema CodeLlama/Llama/DeepSeek and SchemaBench CodeLlama/Llama.  Result:
audit/e0_table_v_mismatch/evaluator_at_commit_b626767_table_v.csv
"""
import sys, csv, importlib.util
root='/tmp/e0audit/wt_b626767'
sys.path.insert(0, root)
spec = importlib.util.spec_from_file_location('rgt', root+'/experiments/E0/reproduce_genuine_tables.py')
rgt = importlib.util.module_from_spec(spec); spec.loader.exec_module(rgt)
from src.evaluator import load_jsonl
import inspect
print(inspect.signature(rgt.evaluate_direct_rschema), inspect.signature(rgt.evaluate_direct_schemabench))
logical=[r for r in load_jsonl(rgt.GOLD_LOGICAL['RSchema']) if r.get('id')]
ddl={r['id']:r for r in load_jsonl(rgt.GOLD_DDL['RSchema']) if r.get('id')}
sb=[r for r in load_jsonl(rgt.GOLD_DDL['SchemaBench']) if r.get('id')]
rows=[]
for ds in ('RSchema','SchemaBench'):
    for model,pdir in rgt.DIRECT[ds].items():
        res=rgt.evaluate_direct_rschema(pdir,logical,ddl) if ds=='RSchema' else rgt.evaluate_direct_schemabench(pdir,sb)
        rows.append({'dataset':ds,'model':model,**{k:f"{res[k]:.6f}" for k in ('nged','halluc','tables','attributes','domain','entity','referential')}})
        print(ds,model,rows[-1]['nged'],flush=True)
w=csv.DictWriter(open('/tmp/e0audit/old_b626767_table_v.csv','w',newline=''),fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
