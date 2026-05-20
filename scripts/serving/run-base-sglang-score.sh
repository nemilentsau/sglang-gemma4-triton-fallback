#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

REVISION="${REVISION:-905e84b50c4d2a365ebde34e685027578e6728db}"
BASE_MODEL_DIR="${1:-${BASE_MODEL_DIR:-models/gemma4-e2b-it/${REVISION}}}"

MODEL_LABEL="${MODEL_LABEL:-gemma4-base}" \
  scripts/serving/run-sglang-score.sh "$BASE_MODEL_DIR"
