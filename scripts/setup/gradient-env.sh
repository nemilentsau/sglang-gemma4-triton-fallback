# Source this file before running torch or SGLang in a Paperspace Gradient
# CUDA 13 notebook.
export PATH="${HOME}/.local/bin:${PATH}"
export UV_LINK_MODE="${UV_LINK_MODE:-copy}"
export LD_LIBRARY_PATH="/usr/local/cuda/compat:/usr/local/cuda/lib64:${LD_LIBRARY_PATH:-}"
export EXPECTED_CUDA_DRIVER_API="${EXPECTED_CUDA_DRIVER_API:-13000}"
export EXPECTED_TORCH_CUDA="${EXPECTED_TORCH_CUDA:-13.0}"
export EXPECTED_SGLANG_VERSION="${EXPECTED_SGLANG_VERSION:-0.5.12}"
export MIN_COMPUTE_CAPABILITY="${MIN_COMPUTE_CAPABILITY:-7.5}"
