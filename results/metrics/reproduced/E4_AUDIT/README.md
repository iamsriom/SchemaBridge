# E4 PRIMARY release

Verified manuscript tables for **masking / inferability** (`tab:e4_split`, `tab:e4_recovery`).

| Path | Role |
|---|---|
| `E4_FINAL_VERIFICATION_REPORT.md` | Full audit |
| `metrics/E4_SPLIT_PRIMARY.csv` | Split recalls |
| `metrics/E4_RECOVERY_PRIMARY.csv` | Recovery Direct/RT/Retention |
| `latex/tab_e4_split_corrected.tex` | Camera-ready Split |
| `latex/tab_e4_recovery_corrected.tex` | Camera-ready Recovery |
| `latex/INTERPRETATION_EVIDENCE_GUIDED.tex` | Evidence-guided paragraph |
| `latex/PAPER_CORRECTIONS_MINIMAL.tex` | Overleaf drop-in |
| `provenance/E4_SOURCE_INVENTORY.md` | Private prediction paths |

**Domain:** joint data-type family + nullability (pooled). Legacy Exp5 `domain_facts` is not PRIMARY.

Reproduce offline: `python3 experiments/E4/evaluate.py && python3 experiments/E4/generate_tables.py`
