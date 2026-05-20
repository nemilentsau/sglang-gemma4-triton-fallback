#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
source "${REPO_ROOT}/scripts/setup/gradient-env.sh"

REVISION="${REVISION:-905e84b50c4d2a365ebde34e685027578e6728db}"
BASE_MODEL_DIR="${BASE_MODEL_DIR:-models/gemma4-e2b-it/${REVISION}}"
ADAPTER_DIR="${ADAPTER_DIR:-adapters/google-gemma-4-e2b-it-ticket-triage-lora/${REVISION}}"
MERGED_MODEL_DIR="${MERGED_MODEL_DIR:-models/gemma4-e2b-it-ticket-triage-merged/${REVISION}}"

if [[ ! -d "$BASE_MODEL_DIR" ]]; then
  echo "Base model directory not found: $BASE_MODEL_DIR" >&2
  exit 1
fi

if [[ ! -d "$ADAPTER_DIR" ]]; then
  echo "Adapter directory not found: $ADAPTER_DIR" >&2
  echo "Run scripts/training/train-lora.sh first." >&2
  exit 1
fi

uv run --extra train python -m scripts.training.merge_gemma4_lora \
  --base-model-dir "$BASE_MODEL_DIR" \
  --adapter-dir "$ADAPTER_DIR" \
  --output-dir "$MERGED_MODEL_DIR" \
  "$@"
