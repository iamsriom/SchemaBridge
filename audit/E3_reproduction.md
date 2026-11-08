# E3 reproduction — Constructor isolation

**Status: BLOCKED**

## Paper intent (from audit brief)

- Describer **fixed** to GPT-5.4-mini with **detailed** prompt
- Same NL description for every constructor on a given gold schema
- Vary constructors; report `tab:e3_overall` (nGED, Halluc, T/A/D/E/R)

## Local artifacts

| Required | Found? |
|---|---|
| Fixed GPT-5.4-mini detailed descriptions for 902 schemata | **NO** |
| Per-constructor reconstructions from those identical NLs | **NO** |
| Paper numerical dump for `tab:e3_overall` | **NO** (not in comparison.txt) |

## Naming collision

Historical folder `RSchema_ExpResults4/Experiment3/Case1Q*` is **masking/describer**, which maps to paper **E4**, not E3. Symlinked under `results/predictions/e3/` for migration history only — do not treat as constructor-isolation evidence.

## Correlation claim (nGED vs Domain F1 on RSchema)

Cannot recalculate under E3 protocol without fixed descriptions. Any historical Exp2/Exp4 correlations are **different experiments**.

## Verdict

**BLOCKED** — missing proprietary fixed descriptions and constructor outputs. Do not invent Domain/Entity scores.
