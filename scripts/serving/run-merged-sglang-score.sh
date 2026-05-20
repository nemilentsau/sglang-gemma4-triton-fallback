#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

REVISION="${REVISION:-905e84b50c4d2a365ebde34e685027578e6728db}"
MERGED_MODEL_DIR="${1:-${MERGED_MODEL_DIR:-models/gemma4-e2b-it-ticket-triage-merged/${REVISION}}}"

MODEL_LABEL="${MODEL_LABEL:-gemma4-merged}" \
  scripts/serving/run-sglang-score.sh "$MERGED_MODEL_DIR"
