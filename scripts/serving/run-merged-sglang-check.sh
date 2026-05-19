#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

usage() {
  cat >&2 <<'EOF'
Usage:
  scripts/serving/run-merged-sglang-check.sh MERGED_MODEL_DIR

Starts the Gemma merged-model SGLang server, waits for /model_info, runs the
smoke test, and stores the server log under runs/.
EOF
}

MERGED_MODEL_DIR="${1:-${MERGED_MODEL_DIR:-}}"
if [[ -z "$MERGED_MODEL_DIR" ]]; then
  usage
  exit 2
fi

BASE_URL="${BASE_URL:-http://127.0.0.1:30000}"
STARTUP_TIMEOUT_SECONDS="${STARTUP_TIMEOUT_SECONDS:-900}"
RUN_DIR="${RUN_DIR:-runs/gemma4-merged-sglang-$(date -u +%Y%m%dT%H%M%SZ)}"
SERVER_LOG="${SERVER_LOG:-${RUN_DIR}/server.log}"

mkdir -p "$RUN_DIR"

if ! command -v curl >/dev/null 2>&1; then
  echo "curl is required for the SGLang readiness check." >&2
  exit 1
fi

scripts/serving/serve-merged-sglang.sh "$MERGED_MODEL_DIR" >"$SERVER_LOG" 2>&1 &
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

BASE_URL="$BASE_URL" scripts/serving/smoke-test.sh

echo "Server log: $SERVER_LOG"
