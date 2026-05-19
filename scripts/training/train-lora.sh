#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
source "${REPO_ROOT}/scripts/setup/gradient-env.sh"

REVISION="${REVISION:-905e84b50c4d2a365ebde34e685027578e6728db}"
BASE_MODEL_DIR="${BASE_MODEL_DIR:-models/gemma4-e2b-it/${REVISION}}"

if [[ ! -d "$BASE_MODEL_DIR" ]]; then
  echo "Base model directory not found: $BASE_MODEL_DIR" >&2
  echo "Run scripts/training/download-model.sh first." >&2
  exit 1
fi

uv sync --extra dev --extra train

uv run --extra train python -m scripts.training.train_gemma4_lora \
  --base-model-dir "$BASE_MODEL_DIR" \
  "$@"
