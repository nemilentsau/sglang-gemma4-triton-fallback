from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_repo_file(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_merged_server_defaults_to_triton_fallback() -> None:
    script = read_repo_file("scripts/serving/serve-merged-sglang.sh")

    assert 'ATTENTION_BACKEND="${ATTENTION_BACKEND:-triton}"' in script
    assert 'SAMPLING_BACKEND="${SAMPLING_BACKEND:-pytorch}"' in script
    assert 'DISABLE_CUDA_GRAPH="${DISABLE_CUDA_GRAPH:-1}"' in script
    assert "--disable-cuda-graph" in script
    assert 'source "${REPO_ROOT}/scripts/setup/gradient-env.sh"' in script


def test_runner_uses_standalone_paths() -> None:
    script = read_repo_file("scripts/serving/run-merged-sglang-check.sh")

    assert "scripts/serving/serve-merged-sglang.sh" in script
    assert "scripts/serving/smoke-test.sh" in script
    assert "profiles/gemma4" not in script


def test_readme_links_separated_script_folders() -> None:
    readme = read_repo_file("README.md")

    assert "scripts/setup/README.md" in readme
    assert "scripts/training/README.md" in readme
    assert "scripts/serving/README.md" in readme


def test_native_lora_path_is_kept_as_failure_repro() -> None:
    script = read_repo_file("scripts/serving/run-sglang-native-lora-check.sh")

    assert "scripts/serving/serve-sglang-native-lora.sh" in script
    assert "scripts/serving/score-sglang-native-lora.sh" in script
    assert "/model_info" in script


def test_readme_centers_backend_fallback_recipe() -> None:
    readme = read_repo_file("README.md")

    assert "FlashInfer" in readme
    assert "Triton" in readme
    assert "native LoRA adapter serving fails" in readme
    assert "merge-and-serve is the workaround" in readme
    assert "Reproduce the FlashInfer failure" in readme
