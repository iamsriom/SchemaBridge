#!/usr/bin/env python3
"""Write verified E4 LaTeX tables into results/metrics/reproduced/E4_AUDIT/latex/."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "metrics" / "reproduced" / "E4_AUDIT" / "latex"
OUT.mkdir(parents=True, exist_ok=True)

SPLIT = r"""% Verified tab:e4_split — joint Domain, pooled Enterprise+SchemaBench+RSchema
\begin{table*}[t]
\centering
\small
\caption{\textbf{Inferable vs.\ non-inferable masked information (E4 Split).}
Empirical recalls from Direct GPT-4o-mini reconstruction, pooled across Enterprise-145, SchemaBench, and RSchema; gold counts in parentheses. Domain uses joint data-type and nullability matching per column. Weak-inferable labels are aggregated with non-inferable. Entity/Referential gold counts are Direct evaluation-row micro denominators (see Table~\ref{tab:e4_recovery} for unique paired populations).}
\label{tab:e4_split}
\begin{tabular}{lrr}
\toprule
\textbf{Masked dimension} & \textbf{Inferable recall (Gold $N$)} & \textbf{Non-inferable recall (Gold $N$)} \\
\midrule
MT Tables       & 0.350 (2{,}555) & 0.197 (4{,}272) \\
MA Attributes   & 0.611 (9{,}254) & 0.187 (42{,}594) \\
MD Domain       & 0.196 (8{,}578) & 0.451 (36{,}669) \\
ME Entity       & 0.871 (2{,}161) & 0.447 (2{,}608) \\
MR Referential  & 0.687 (4{,}214) & 0.288 (1{,}246) \\
\bottomrule
\end{tabular}
\end{table*}
"""

RECOVERY = r"""% Verified tab:e4_recovery — paired Direct/RT, per-element describer averaging
\begin{table*}[t]
\centering
\small
\caption{\textbf{Direct vs.\ round-trip recovery of inferable masked elements (E4 Recovery).}
Gold $N$ is the number of unique heuristic-inferable gold elements in the paired Direct/RT population. Direct is GPT-4o-mini reconstruction from masked DDL; RT averages match indicators over available Schema2Text describers per element, then micro-averages across elements. Retention $=\mathrm{RT}/\mathrm{Direct}$ (full precision before 3\,d.p.\ rounding). Domain uses joint type+nullability matching. Entity and Referential Gold $N$ differ from Table~\ref{tab:e4_split} because Split micro-counts duplicate Direct evaluation rows while Recovery deduplicates.}
\label{tab:e4_recovery}
\begin{tabular}{lrrrr}
\toprule
\textbf{Dimension} & \textbf{Gold $N$} & \textbf{Direct} & \textbf{RT} & \textbf{Retention} \\
\midrule
MT Tables      & 2{,}555 & 0.350 & 0.120 & 0.344 \\
MA Attributes  & 9{,}254 & 0.611 & 0.487 & 0.797 \\
MD Domain      & 8{,}578 & 0.196 & 0.049 & 0.251 \\
ME Entity      & 2{,}087 & 0.877 & 0.624 & 0.712 \\
MR Referential & 4{,}197 & 0.688 & 0.444 & 0.645 \\
\bottomrule
\end{tabular}
\end{table*}
"""

INTERPRETATION = r"""% Drop-in for the Evidence-guided reconstruction paragraph (E4)
\paragraph{Evidence-guided reconstruction}
Table~\ref{tab:e4_split} shows that inferable elements are recovered more frequently than non-inferable ones for tables, attributes, entity constraints, and foreign keys. Recovery is strongest for inferable entity constraints, whereas table recovery remains difficult even when structural cues are available. The substantial gaps for attributes and foreign keys suggest that visible structural evidence helps reconstruct missing schema information. Domain exhibits the opposite trend, with lower recall for inferable than non-inferable elements under joint data-type and nullability matching. Overall, recovery remains incomplete, and the heuristic classification does not establish whether successful predictions arise from logical reasoning or learned design conventions.
"""

PAPER = r"""% Minimal Overleaf drop-in for E4 tables + interpretation
% Replace existing tab:e4_split / tab:e4_recovery and the Evidence-guided paragraph.
\input{tab_e4_split_corrected}
\input{tab_e4_recovery_corrected}
""" + "\n" + INTERPRETATION


def main() -> int:
    (OUT / "tab_e4_split_corrected.tex").write_text(SPLIT, encoding="utf-8")
    (OUT / "tab_e4_recovery_corrected.tex").write_text(RECOVERY, encoding="utf-8")
    (OUT / "INTERPRETATION_EVIDENCE_GUIDED.tex").write_text(INTERPRETATION, encoding="utf-8")
    (OUT / "PAPER_CORRECTIONS_MINIMAL.tex").write_text(
        PAPER + "\n% Full table bodies are in tab_e4_*_corrected.tex\n", encoding="utf-8"
    )
    print(f"Wrote LaTeX under {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
