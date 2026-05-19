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
    assert "scripts/setup/setup-paperspace.sh" in readme


def test_setup_scripts_are_executable_setup_entrypoints() -> None:
    setup = read_repo_file("scripts/setup/setup-paperspace.sh")
    verify = read_repo_file("scripts/setup/verify-cuda-env.sh")
    setup_readme = read_repo_file("scripts/setup/README.md")

    assert "scripts/setup/verify-cuda-env.sh" in setup
    assert "scripts/setup/install-sglang.sh" in setup
    assert "cuDriverGetVersion" in verify
    assert "scripts/setup/setup-paperspace.sh" in setup_readme
    assert "python3 - <<'PY'" not in setup_readme


def test_training_scripts_source_cuda_environment() -> None:
    train = read_repo_file("scripts/training/train-lora.sh")
    merge = read_repo_file("scripts/training/merge-lora.sh")

    assert 'source "${REPO_ROOT}/scripts/setup/gradient-env.sh"' in train
    assert 'source "${REPO_ROOT}/scripts/setup/gradient-env.sh"' in merge


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
