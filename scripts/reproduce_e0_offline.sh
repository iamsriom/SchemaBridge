#!/usr/bin/env bash
# Offline E0 reproduction: datasets + saved predictions → Tables V/VI + comparison status.
# No API keys or GPUs required.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 -m pip install -r requirements.txt
python3 -m pytest -q
python3 experiments/E0/reproduce_genuine_tables.py --write-gpm
python3 scripts/build_e0_paper_comparison.py

echo
echo "Wrote:"
echo "  results/metrics/reproduced/E0_TABLE_V_FINAL.{csv,json,tex}"
echo "  results/metrics/reproduced/E0_TABLE_VI_FINAL.{csv,json,tex}"
echo "  audit/E0_PAPER_COMPARISON.csv"
echo "Compare against: audit/E0_CURRENT_MANUSCRIPT_VALUES.json"
echo "Full report:     audit/E0_VERIFICATION_REPORT.md"
echo
echo "Note: Table VI One-shot/CoT/Few-shot use ARCHIVE_AGGREGATE when"
echo "per-schema PaperMethods results.jsonl trees are unavailable."
