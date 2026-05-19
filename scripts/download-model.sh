#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

MODEL_ID="${MODEL_ID:-google/gemma-4-E2B-it}"
REVISION="${REVISION:-905e84b50c4d2a365ebde34e685027578e6728db}"
LOCAL_DIR="${LOCAL_DIR:-models/gemma4-e2b-it/${REVISION}}"

echo "Downloading ${MODEL_ID}@${REVISION}"
echo "Target: ${LOCAL_DIR}"

if [[ -n "${HF_TOKEN:-}" ]]; then
  echo "Auth: HF_TOKEN from environment"
else
  echo "Auth: anonymous"
fi

uv run --no-sync python - "$MODEL_ID" "$REVISION" "$LOCAL_DIR" <<'PY'
from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

from huggingface_hub import HfApi, snapshot_download

model_id = sys.argv[1]
revision = sys.argv[2]
local_dir = Path(sys.argv[3])
token = os.environ.get("HF_TOKEN")

local_dir.mkdir(parents=True, exist_ok=True)

api = HfApi(token=token)
info = api.model_info(repo_id=model_id, revision=revision)
snapshot_path = snapshot_download(
    repo_id=model_id,
    revision=revision,
    local_dir=local_dir,
    token=token,
)

root = Path(snapshot_path)
files = sorted(
    str(path.relative_to(root))
    for path in root.rglob("*")
    if path.is_file() and ".cache" not in path.parts
)

manifest = {
    "model_id": model_id,
    "requested_revision": revision,
    "resolved_sha": info.sha,
    "local_dir": str(local_dir),
    "downloaded_at_utc": datetime.now(UTC).isoformat(),
    "file_count": len(files),
    "files": files,
}

(local_dir / "download-manifest.json").write_text(
    json.dumps(manifest, indent=2, sort_keys=False) + "\n",
    encoding="utf-8",
)

print(f"Downloaded snapshot to {local_dir}")
print(f"Resolved SHA: {info.sha}")
print(f"Files: {len(files)}")
print(f"Manifest: {local_dir / 'download-manifest.json'}")
PY
