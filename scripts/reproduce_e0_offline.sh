#!/usr/bin/env bash
# Offline E0 reproduction from private prediction dumps.
# No API keys or GPUs required.
#
# Usage:
#   PRED_ROOT=/path/to/e0-predictions bash scripts/reproduce_e0_offline.sh
#   bash scripts/reproduce_e0_offline.sh /path/to/e0-predictions
#
# Default PRED_ROOT: results/predictions/e0  (gitignored)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PRED_ROOT="${1:-${PRED_ROOT:-$ROOT/results/predictions/e0}}"

python3 -m pip install -r requirements.txt
python3 -m pytest -q
python3 experiments/E0/reproduce_genuine_tables.py --validate-only --skip-pytest

if [[ ! -d "$PRED_ROOT" ]]; then
  echo "PRED_ROOT missing: $PRED_ROOT" >&2
  echo "Place verified Direct dumps there (see experiments/E0/README.md) or pass --pred-root." >&2
  exit 2
fi

python3 experiments/E0/reproduce_genuine_tables.py \
  --pred-root "$PRED_ROOT" \
  --write-gpm --skip-pytest --strict

if [[ -f scripts/build_e0_paper_comparison.py ]]; then
  python3 scripts/build_e0_paper_comparison.py || true
fi

echo
echo "Wrote (local, gitignored):"
echo "  results/metrics/reproduced/E0_TABLE_V_FINAL.{csv,json,tex}"
echo "  results/metrics/reproduced/E0_TABLE_VI_FINAL.{csv,json,tex}"
echo
echo "Note: Table VI One-shot/CoT/Few-shot stay ARCHIVE/BLOCKED without PaperMethods trees."
