#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
source "${REPO_ROOT}/scripts/setup/gradient-env.sh"

REVISION="${REVISION:-905e84b50c4d2a365ebde34e685027578e6728db}"
BASE_MODEL_DIR="${BASE_MODEL_DIR:-models/gemma4-e2b-it/${REVISION}}"
ADAPTER_DIR="${ADAPTER_DIR:-adapters/google-gemma-4-e2b-it-ticket-triage-lora/${REVISION}}"
LORA_NAME="${LORA_NAME:-ticket-triage}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-30000}"
CONTEXT_LENGTH="${CONTEXT_LENGTH:-8192}"
ATTENTION_BACKEND="${ATTENTION_BACKEND:-triton}"
SAMPLING_BACKEND="${SAMPLING_BACKEND:-pytorch}"
DISABLE_CUDA_GRAPH="${DISABLE_CUDA_GRAPH:-1}"

if [[ ! -d "$BASE_MODEL_DIR" ]]; then
  echo "Base model directory not found: $BASE_MODEL_DIR" >&2
  echo "Run scripts/training/download-model.sh first." >&2
  exit 1
fi

if [[ ! -d "$ADAPTER_DIR" ]]; then
  echo "Adapter directory not found: $ADAPTER_DIR" >&2
  echo "Run scripts/training/train-lora.sh first." >&2
  exit 1
fi

if ! uv run --no-sync python -c 'from importlib import import_module; import_module("sglang.launch_server")' >/dev/null 2>&1; then
  echo "SGLang launch server is not importable in the uv environment." >&2
  echo "Run scripts/setup/install-sglang.sh on the cloud box first." >&2
  exit 1
fi

launch_args=(
  uv run --no-sync python -m sglang.launch_server
  --model-path "$BASE_MODEL_DIR"
  --host "$HOST"
  --port "$PORT"
  --context-length "$CONTEXT_LENGTH"
  --attention-backend "$ATTENTION_BACKEND"
  --sampling-backend "$SAMPLING_BACKEND"
  --enable-lora
  --lora-paths "${LORA_NAME}=${ADAPTER_DIR}"
  --max-loras-per-batch 2
  --log-level info
)

if [[ "$DISABLE_CUDA_GRAPH" != "0" ]]; then
  launch_args+=(--disable-cuda-graph)
fi

exec "${launch_args[@]}" "$@"
