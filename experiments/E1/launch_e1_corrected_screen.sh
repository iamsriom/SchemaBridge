#!/usr/bin/env bash
# Optional multi-GPU launcher for E1 Detailed (Prompt B) reproduction.
# Does not require exactly six GPUs; adjust CUDA_VISIBLE_DEVICES to your hardware.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

PY="${PYTHON:-python3}"
LOGDIR="${E1_LOGDIR:-audit/e1_verification/full_gpu_run}"
mkdir -p "$LOGDIR" results/predictions/e1_corrected

export TOKENIZERS_PARALLELISM=false
export SCHEMABRIDGE_DATA_ROOT="${SCHEMABRIDGE_DATA_ROOT:-$ROOT}"

if [[ -z "${HF_TOKEN:-}" && -f "${ROOT}/huggingface_api.txt" ]]; then
  # Local convenience only; never commit this file.
  export HF_TOKEN="$(tr -d ' \n' <"${ROOT}/huggingface_api.txt")"
fi

echo "===== $(date -u +%Y-%m-%dT%H:%M:%SZ) E1 START =====" | tee -a "$LOGDIR/progress.log"
command -v nvidia-smi >/dev/null && nvidia-smi --query-gpu=index,name,memory.total,memory.used --format=csv | tee -a "$LOGDIR/progress.log" || true
"$PY" -V | tee -a "$LOGDIR/progress.log"

echo "----- dry-run plan -----" | tee -a "$LOGDIR/progress.log"
"$PY" experiments/E1/run_e1_corrected_gpu.py --dataset all --model all --dry-run | tee -a "$LOGDIR/progress.log"

echo "----- reuse prior valid preds (optional archives) -----" | tee -a "$LOGDIR/progress.log"
"$PY" experiments/E1/run_e1_corrected_gpu.py --dataset all --model all --reuse-only | tee -a "$LOGDIR/reuse.log"

# Example 6×T4 allocation used in the verified run. Override freely.
CL_GPUS="${CL_GPUS:-0,1}"
LL_GPUS="${LL_GPUS:-2,3}"
DS_GPUS="${DS_GPUS:-4,5}"

for DS in RSchema SchemaBench; do
  echo "=== Generating gaps for $DS ===" | tee -a "$LOGDIR/progress.log"
  CUDA_VISIBLE_DEVICES="$CL_GPUS" "$PY" experiments/E1/run_e1_corrected_gpu.py \
    --dataset "$DS" --model codellama13b --generate \
    >"$LOGDIR/gen_${DS}_codellama13b.log" 2>&1 &
  PID_CL=$!
  CUDA_VISIBLE_DEVICES="$LL_GPUS" "$PY" experiments/E1/run_e1_corrected_gpu.py \
    --dataset "$DS" --model llama31 --generate \
    >"$LOGDIR/gen_${DS}_llama31.log" 2>&1 &
  PID_LL=$!
  CUDA_VISIBLE_DEVICES="$DS_GPUS" "$PY" experiments/E1/run_e1_corrected_gpu.py \
    --dataset "$DS" --model deepseek --generate \
    >"$LOGDIR/gen_${DS}_deepseek.log" 2>&1 &
  PID_DS=$!
  wait "$PID_CL"; EC_CL=$?
  wait "$PID_LL"; EC_LL=$?
  wait "$PID_DS"; EC_DS=$?
  echo "EXIT $DS codellama=$EC_CL llama=$EC_LL deepseek=$EC_DS" | tee -a "$LOGDIR/progress.log"
done

echo "----- optional NF4 OOM recovery -----" | tee -a "$LOGDIR/progress.log"
for MODEL in codellama13b llama31 deepseek; do
  "$PY" experiments/E1/recover_oom_4bit.py --dataset SchemaBench --model "$MODEL" \
    | tee -a "$LOGDIR/recover_${MODEL}.log" || true
done

echo "----- evaluate -----" | tee -a "$LOGDIR/progress.log"
"$PY" experiments/E1/evaluate_e1_corrected.py --bertscore-device "${BERTSCORE_DEVICE:-cuda:0}" \
  | tee -a "$LOGDIR/evaluate.log"

echo "===== $(date -u +%Y-%m-%dT%H:%M:%SZ) E1 END =====" | tee -a "$LOGDIR/progress.log"
