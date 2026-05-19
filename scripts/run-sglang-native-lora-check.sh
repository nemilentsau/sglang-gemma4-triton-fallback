#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

BASE_URL="${BASE_URL:-http://127.0.0.1:30000}"
LORA_NAME="${LORA_NAME:-ticket-triage}"
STARTUP_TIMEOUT_SECONDS="${STARTUP_TIMEOUT_SECONDS:-900}"
RUN_DIR="${RUN_DIR:-runs/gemma4-e2b-sglang-native-lora-$(date -u +%Y%m%dT%H%M%SZ)}"
SERVER_LOG="${SERVER_LOG:-${RUN_DIR}/server.log}"
SCORE_JSON="${SCORE_JSON:-${RUN_DIR}/score.json}"
BATCH_SIZE="${BATCH_SIZE:-32}"

mkdir -p "$RUN_DIR"

if ! command -v curl >/dev/null 2>&1; then
  echo "curl is required for the SGLang readiness check." >&2
  exit 1
fi

scripts/serve-sglang-native-lora.sh >"$SERVER_LOG" 2>&1 &
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

OUTPUT_JSON="$SCORE_JSON" LORA_NAME="$LORA_NAME" BASE_URL="$BASE_URL" \
  scripts/score-sglang-native-lora.sh --batch-size "$BATCH_SIZE"

echo "Server log: $SERVER_LOG"
echo "Score JSON: $SCORE_JSON"
