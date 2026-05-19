#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
source "${REPO_ROOT}/scripts/setup/gradient-env.sh"

scripts/setup/verify-cuda-env.sh
uv sync --extra dev --extra train --extra model --extra download
scripts/setup/install-sglang.sh
scripts/setup/verify-cuda-env.sh

echo "Paperspace setup complete"
