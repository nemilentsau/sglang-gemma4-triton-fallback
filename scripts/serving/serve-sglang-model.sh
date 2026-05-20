#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
source "${REPO_ROOT}/scripts/setup/gradient-env.sh"

usage() {
  cat >&2 <<'EOF'
Usage:
  scripts/serving/serve-sglang-model.sh MODEL_DIR [sglang args...]

Starts SGLang for a local Gemma 4 model directory.

Environment:
  HOST=127.0.0.1
  PORT=30000
  CONTEXT_LENGTH=8192
  ATTENTION_BACKEND=triton
  SAMPLING_BACKEND=pytorch
  DISABLE_CUDA_GRAPH=1
EOF
}

MODEL_DIR="${1:-${MODEL_DIR:-}}"
if [[ $# -gt 0 ]]; then
  shift
fi

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-30000}"
CONTEXT_LENGTH="${CONTEXT_LENGTH:-8192}"
ATTENTION_BACKEND="${ATTENTION_BACKEND:-triton}"
SAMPLING_BACKEND="${SAMPLING_BACKEND:-pytorch}"
DISABLE_CUDA_GRAPH="${DISABLE_CUDA_GRAPH:-1}"

if [[ -z "$MODEL_DIR" ]]; then
  usage
  exit 2
fi

if [[ ! -d "$MODEL_DIR" ]]; then
  echo "Model directory not found: $MODEL_DIR" >&2
  exit 1
fi

for file in processor_config.json; do
  if [[ ! -s "${MODEL_DIR}/${file}" ]]; then
    echo "Missing Gemma processor config: ${MODEL_DIR}/${file}" >&2
    echo "Repair merged artifacts with scripts/serving/repair-processor-configs.sh." >&2
    exit 1
  fi
done

if ! uv run --no-sync python -c 'from importlib import import_module; import_module("sglang.launch_server")' >/dev/null 2>&1; then
  echo "SGLang launch server is not importable in the uv environment." >&2
  echo "Install the model serving dependencies before starting Gemma 4." >&2
  exit 1
fi

launch_args=(
  uv run --no-sync python -m sglang.launch_server
  --model-path "$MODEL_DIR"
  --host "$HOST"
  --port "$PORT"
  --context-length "$CONTEXT_LENGTH"
  --attention-backend "$ATTENTION_BACKEND"
  --sampling-backend "$SAMPLING_BACKEND"
  --log-level info
)

if [[ "$DISABLE_CUDA_GRAPH" != "0" ]]; then
  launch_args+=(--disable-cuda-graph)
fi

exec "${launch_args[@]}" "$@"
