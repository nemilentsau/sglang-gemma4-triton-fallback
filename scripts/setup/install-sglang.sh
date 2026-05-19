#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
source "${REPO_ROOT}/scripts/setup/gradient-env.sh"

SGLANG_PACKAGE="${SGLANG_PACKAGE:-sglang==0.5.12}"

uv sync --extra dev --extra train --extra model
uv pip install --prerelease=allow "$SGLANG_PACKAGE"

uv run --no-sync python - <<'PY'
from __future__ import annotations

from importlib import import_module, metadata

import_module("sglang.launch_server")

for package in ("sglang", "distro", "torch", "transformers", "peft", "nvidia-cudnn-cu13"):
    try:
        print(f"{package}=={metadata.version(package)}")
    except metadata.PackageNotFoundError:
        print(f"{package}=not-installed")
PY
