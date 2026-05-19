#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

BASE_URL="${BASE_URL:-http://127.0.0.1:30000}"
LORA_NAME="${LORA_NAME:-ticket-triage}"
OUTPUT_JSON="${OUTPUT_JSON:-runs/gemma4-e2b-sglang-native-lora-test.json}"

uv run --no-sync python -m scripts.serving.score_sglang_endpoint \
  --base-url "$BASE_URL" \
  --split fixtures/ticket-triage/test.jsonl \
  --lora-name "$LORA_NAME" \
  --output-json "$OUTPUT_JSON" \
  "$@"
