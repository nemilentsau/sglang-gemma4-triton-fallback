#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:30000}"
MAX_NEW_TOKENS="${MAX_NEW_TOKENS:-48}"

if ! command -v curl >/dev/null 2>&1; then
  echo "curl is required for the SGLang smoke test." >&2
  exit 1
fi

curl -fsS "${BASE_URL}/model_info" >/dev/null

BASE_URL="$BASE_URL" MAX_NEW_TOKENS="$MAX_NEW_TOKENS" uv run --no-sync python - <<'PY'
from __future__ import annotations

import json
import os
from urllib import request

base_url = os.environ["BASE_URL"].rstrip("/")
max_new_tokens = int(os.environ["MAX_NEW_TOKENS"])
payload = {
    "model": "default",
    "messages": [
        {
            "role": "user",
            "content": "Return one short sentence about why smoke tests exist.",
        }
    ],
    "max_tokens": max_new_tokens,
    "temperature": 0,
}
req = request.Request(
    f"{base_url}/v1/chat/completions",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
)

with request.urlopen(req, timeout=300) as response:
    body = json.loads(response.read().decode("utf-8"))

if not isinstance(body, dict):
    raise SystemExit("SGLang chat response was not an object")

choices = body.get("choices")
if not isinstance(choices, list) or not choices:
    raise SystemExit("SGLang chat response did not contain choices")

choice = choices[0]
if not isinstance(choice, dict):
    raise SystemExit("SGLang chat choice was not an object")

message = choice.get("message")
if not isinstance(message, dict) or not isinstance(message.get("content"), str):
    raise SystemExit("SGLang chat response did not contain message content")

if message["content"].strip() == "":
    raise SystemExit("SGLang chat response returned empty content")

print("Gemma 4 SGLang smoke test complete")
PY
