#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
source "${REPO_ROOT}/scripts/setup/gradient-env.sh"

python3 - <<'PY'
from __future__ import annotations

import ctypes
import os
import sys

expected = int(os.environ.get("EXPECTED_CUDA_DRIVER_API", "13000"))
version = ctypes.c_int()
rc = ctypes.CDLL("libcuda.so.1").cuDriverGetVersion(ctypes.byref(version))
print(f"cuDriverGetVersion rc={rc} version={version.value}")

if rc != 0:
    raise SystemExit(f"cuDriverGetVersion failed with rc={rc}")

if version.value != expected:
    raise SystemExit(
        f"Expected CUDA driver API {expected}, got {version.value}. "
        "Check LD_LIBRARY_PATH and /usr/local/cuda/compat."
    )

sys.exit(0)
PY

if [[ -x ".venv/bin/python" ]]; then
  .venv/bin/python - <<'PY'
from __future__ import annotations

import os

try:
    import torch
except ModuleNotFoundError:
    print("torch not installed in .venv; skipping torch CUDA check")
else:
    expected = os.environ.get("EXPECTED_TORCH_CUDA", "13.0")
    actual = torch.version.cuda
    available = torch.cuda.is_available()
    print(f"torch cuda: {actual}")
    print(f"cuda available: {available}")
    if actual != expected:
        raise SystemExit(f"Expected torch CUDA {expected}, got {actual}")
    if not available:
        raise SystemExit("torch.cuda.is_available() returned false")
PY
else
  echo ".venv not found; skipping torch CUDA check"
fi

echo "CUDA compatibility environment verified"
