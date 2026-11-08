# Release readiness checklist

**Verdict: NOT READY FOR PUBLIC RELEASE**

| Check | Result |
|---|---|
| Secrets in repo | **WARN** — do not ship `/data/*_api.txt`; SchemaBridge tree itself has no key files copied |
| Absolute `/data` hardcodes in release scripts | Partially mitigated via `SCHEMABRIDGE_ROOT` + relative configs; **symlinked predictions still point at `/data/...`** and will break off-machine without packaging preds |
| Large accidental files | Predictions not duplicated (symlinks); HF caches not under SchemaBridge |
| Licences | MIT LICENSE present; SchemaBench/HF and Enterprise redistribution terms **must** be documented before public upload |
| README honesty | Experiments E3–E5 paper semantics documented as BLOCKED/PARTIAL |
| Offline metrics without API keys | **PASS** for archived comparisons |
| Deterministic offline reproduce | **PASS** (two-run CSV checksum match) |
| pytest | **PASS** (143) |
| Critical experiments reproducible | **FAIL** (E0 incomplete; E3/E5 blocked; E4 partial) |
| Manuscript present | **FAIL** |

## Before any public release

1. Bundle or host prediction tarballs with relative manifests (replace `/data` symlinks)  
2. Obtain/release closed-model predictions or remove those rows from paper + tables  
3. Resolve Llama E0 and SchemaBench Table V discrepancies  
4. Add dataset licence files  
5. Place camera-ready PDF/LaTeX under `paper/` for artifact mapping  
6. Complete E3/E4/E5 or drop claims  

Until then: internal research archive only.
