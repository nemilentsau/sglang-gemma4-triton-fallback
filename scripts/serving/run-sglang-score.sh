#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

usage() {
  cat >&2 <<'EOF'
Usage:
  scripts/serving/run-sglang-score.sh MODEL_DIR

Starts SGLang, waits for /model_info, scores the ticket-triage split through
/v1/chat/completions, writes score JSON under runs/, and stops the server.

Environment:
  MODEL_LABEL=gemma4-model
  BASE_URL=http://127.0.0.1:30000
  STARTUP_TIMEOUT_SECONDS=900
  MAX_EVAL_EXAMPLES=unset
  MAX_NEW_TOKENS=96
  MAX_CONCURRENCY=8
  WARMUP_EXAMPLES=8
  ATTENTION_BACKEND=triton
EOF
}

MODEL_DIR="${1:-${MODEL_DIR:-}}"
if [[ -z "$MODEL_DIR" ]]; then
  usage
  exit 2
fi

MODEL_LABEL="${MODEL_LABEL:-gemma4-model}"
BASE_URL="${BASE_URL:-http://127.0.0.1:30000}"
STARTUP_TIMEOUT_SECONDS="${STARTUP_TIMEOUT_SECONDS:-900}"
RUN_DIR="${RUN_DIR:-runs/${MODEL_LABEL}-score-$(date -u +%Y%m%dT%H%M%SZ)}"
SERVER_LOG="${SERVER_LOG:-${RUN_DIR}/server.log}"
SCORE_JSON="${SCORE_JSON:-${RUN_DIR}/score.json}"

mkdir -p "$RUN_DIR"

if ! command -v curl >/dev/null 2>&1; then
  echo "curl is required for the SGLang readiness check." >&2
  exit 1
fi

scripts/serving/serve-sglang-model.sh "$MODEL_DIR" >"$SERVER_LOG" 2>&1 &
SERVER_PID="$!"

cleanup() {
  if kill -0 "$SERVER_PID" >/dev/null 2>&1; then
    kill "$SERVER_PID" >/dev/null 2>&1 || true
    wait "$SERVER_PID" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

deadline=$((SECONDS + STARTUP_TIMEOUT_SECONDS))
until curl -fsS "${BASE_URL}/model_info" >/dev/null 2>&1; do
  if ! kill -0 "$SERVER_PID" >/dev/null 2>&1; then
    echo "SGLang server exited before becoming ready. Last log lines:" >&2
    tail -n 120 "$SERVER_LOG" >&2 || true
    exit 1
  fi

  if (( SECONDS >= deadline )); then
    echo "Timed out waiting for ${BASE_URL}/model_info. Last log lines:" >&2
    tail -n 120 "$SERVER_LOG" >&2 || true
    exit 1
  fi

  sleep 5
done

OUTPUT_JSON="$SCORE_JSON" BASE_URL="$BASE_URL" scripts/serving/score-sglang-chat.sh

echo "Server log: $SERVER_LOG"
echo "Score JSON: $SCORE_JSON"
