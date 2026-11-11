# E0 Verification Report

**Branch:** `icde2027-e0-verified`  
**Updated:** 2026-11-11 (parser F1–F6 repair)  
**Experiment status:** **PARTIAL**

## Executive verdict (post-repair)

| Layer | Status |
|---|---|
| Direct predictions (757) | VERIFIED_FROM_PREDICTIONS (hash-identical originals) |
| Evaluator protocol | Matches manuscript (micro F1, Domain-381, Hall4, names-only nGED) |
| DDL parser | F1–F6 **fixed**; independent audit tests PASS |
| Table V vs locked targets | **70/70 PASS** against `E0_CURRENT_MANUSCRIPT_VALUES.json` (scientifically recommended) |
| Table VI Direct | Equals Table V RSchema |
| Table VI prompting | PASS_ARCHIVE (54) provisional; REGENERATED_NEW_RUN in progress on GPUs |
| SchemaAgent | Excluded |

Previous hybrid manuscript values preserved in `audit/E0_PREVIOUS_HYBRID_MANUSCRIPT_VALUES.json`.  
Cell-level file: `audit/E0_PAPER_COMPARISON.csv`.  
Mismatch root-cause audit: `audit/E0_TABLE_V_DIAGNOSTIC.md`.  
Manuscript edits: `audit/E0_MANUSCRIPT_CORRECTIONS.md`.  
Repair log: `audit/E0_PR3_REPAIR_LOG.md`.

---


## Prior report (pre-parser-repair)

See git history at `d0eed4a` for the pre-repair 29/70 PASS analysis.
