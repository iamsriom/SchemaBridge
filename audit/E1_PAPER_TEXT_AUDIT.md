# E1 Paper Text Audit

## Setup paragraph — required corrections

Replace any Setup that claims evaluation on “all 902 schemata” or RSchema \(N{=}518\) for E1 metrics.

**Recommended replacement LaTeX:**

```latex
\paragraph{Setup.}
We evaluate five describers---CodeLlama-13B-Instruct, Llama-3.1-8B-Instruct,
DeepSeek-Coder-6.7B-Instruct, Claude Sonnet~4.6, and GPT-5.4-mini---under the
basic and detailed Schema2Text prompts of §IV-D.
Enterprise-145 ($N{=}145$) is scored with SCR only, because it has no gold
natural-language descriptions.
RSchema is restricted to the $N{=}381$ instances with genuine DDL (the remaining
logical annotations lack executable DDL and are excluded from E1 metric
aggregation), and SchemaBench uses all $N{=}239$ pairs.
BLEU-4 is corpus SacreBLEU with single-reference layout
\texttt{corpus\_bleu(hyps,[refs])}; ROUGE-L $F_1$ and BERTScore-$F_1$
(RoBERTa-large, no IDF, no baseline rescaling) compare each description with
the gold requirement text; SCR is the macro-averaged fraction of normalized
source table and column identifiers mentioned in the description (§III-E).
```

## Metric / prompt wording

| Claim | Verdict | Action |
|---|---|---|
| Corpus BLEU-4 | Declared correctly; historical code used inverted sacrebleu refs | Keep declaration; ensure table uses corrected numbers |
| ROUGE-L macro F1 | Matches implementation | None |
| BERTScore-F1 / roberta-large | Matches `lang="en"` defaults | Optionally name checkpoint once |
| SCR = table∪column identifier mention | Matches code; substring match can false-positive | Optional footnote only if space |
| Basic = short summary; Detailed = exhaustive paragraph | Matches schema2text1 / schema2text2 | Do **not** cite repo `describer_detailed.txt` (5-section) as paper D |
| Gold NL for Enterprise | Absent — lexical metrics `--` | Keep |

## Discussion of SCR↑ / BLEU↓ under detailed prompting

**Keep.** Evidence: GPT-5.4-mini / Claude detailed outputs are ~4× longer, mention nearly all identifiers (SCR→0.999/1.000) without emitting raw `CREATE TABLE`, while gold NL is short requirements prose → BLEU/ROUGE fall. Same gold references used for B and D.

## Bolding

Verified winners (per dataset × column) match the verified table in `E1_VERIFIED_TABLE.tex`.  
User-brief SchemaBench Detailed open BLEU/ROUGE bolding assumed Llama 4.09/0.175; after correction Llama remains best on those columns (3.67 / 0.173).

## Do not change

- E0, E2–E5 sections/tables.
- Do not silently “fix” SCR substring semantics to force bold changes.
