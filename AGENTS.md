# Agent Instructions

This repository is a focused repro for Gemma 4 E2B serving on SGLang.

## Scope

- Keep the story centered on Gemma 4 E2B merge-and-serve.
- Keep native LoRA only as a failure path to reproduce.
- Keep the Triton versus FlashInfer backend behavior explicit.
- Use only small synthetic fixtures.

## Out Of Scope

- Do not add unrelated serving variants or claims.
- Do not add benchmark claims unless the benchmark command and logs are added in
  the same change.
- Do not claim a compatibility path works unless the serving smoke test actually
  ran against that served model.

## Startup

- Read `scripts/setup/README.md` before changing setup or dependency scripts.
- CUDA 13 on this box depends on the CUDA compatibility libraries because the
  host driver is otherwise too old.
- Ensure compatibility is installed first, then source
  `scripts/setup/gradient-env.sh` so `/usr/local/cuda/compat` is first in
  `LD_LIBRARY_PATH`.
- Run `scripts/setup/verify-cuda-env.sh` before any `uv sync`, SGLang install,
  training, merge, or serving command.
- Use the existing setup scripts; do not add a new install path unless the
  existing scripts cannot express the required order.

## Tooling

- Use `uv` for Python dependency management and command execution.
- Run Python commands through `uv run`.
- Keep generated model weights, adapters, and run logs out of git.

## Checks

Before claiming repo work is complete, run:

```bash
uv run ruff check .
uv run pyright
uv run pytest -v
git diff --check
jq empty fixtures/ticket-triage/schema.json fixtures/ticket-triage/*.jsonl
bash -n scripts/setup/*.sh scripts/training/*.sh scripts/serving/*.sh
```
