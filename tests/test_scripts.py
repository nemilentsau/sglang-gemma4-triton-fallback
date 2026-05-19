from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_repo_file(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_merged_server_defaults_to_triton_fallback() -> None:
    script = read_repo_file("scripts/serve-merged-sglang.sh")

    assert 'ATTENTION_BACKEND="${ATTENTION_BACKEND:-triton}"' in script
    assert 'SAMPLING_BACKEND="${SAMPLING_BACKEND:-pytorch}"' in script
    assert 'DISABLE_CUDA_GRAPH="${DISABLE_CUDA_GRAPH:-1}"' in script
    assert "--disable-cuda-graph" in script
    assert 'source "${REPO_ROOT}/scripts/gradient-env.sh"' in script


def test_runner_uses_standalone_paths() -> None:
    script = read_repo_file("scripts/run-merged-sglang-check.sh")

    assert "scripts/serve-merged-sglang.sh" in script
    assert "scripts/smoke-test.sh" in script
    assert "profiles/gemma4" not in script


def test_native_lora_path_is_kept_as_failure_repro() -> None:
    script = read_repo_file("scripts/run-sglang-native-lora-check.sh")

    assert "scripts/serve-sglang-native-lora.sh" in script
    assert "scripts/score-sglang-native-lora.sh" in script
    assert "/model_info" in script


def test_readme_centers_backend_fallback_not_model_quality() -> None:
    readme = read_repo_file("README.md")

    assert "FlashInfer" in readme
    assert "Triton" in readme
    assert "not a benchmark" in readme
