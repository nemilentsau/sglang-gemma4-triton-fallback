#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
source "${REPO_ROOT}/scripts/setup/gradient-env.sh"

BASE_URL="${BASE_URL:-http://127.0.0.1:30000}"
OUTPUT_JSON="${OUTPUT_JSON:-runs/gemma4-e2b-sglang-chat-score.json}"
MAX_NEW_TOKENS="${MAX_NEW_TOKENS:-96}"
MAX_CONCURRENCY="${MAX_CONCURRENCY:-8}"
WARMUP_EXAMPLES="${WARMUP_EXAMPLES:-8}"
SPLIT="${SPLIT:-fixtures/ticket-triage/test.jsonl}"

args=(
  uv run --no-sync python -m scripts.serving.score_sglang_endpoint
  --base-url "$BASE_URL"
  --split "$SPLIT"
  --api chat
  --base-model
  --max-new-tokens "$MAX_NEW_TOKENS"
  --max-concurrency "$MAX_CONCURRENCY"
  --warmup-examples "$WARMUP_EXAMPLES"
  --output-json "$OUTPUT_JSON"
)

if [[ -n "${MAX_EVAL_EXAMPLES:-}" ]]; then
  args+=(--max-examples "$MAX_EVAL_EXAMPLES")
fi

exec "${args[@]}" "$@"
