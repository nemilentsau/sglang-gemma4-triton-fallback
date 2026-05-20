# SGLang Gemma 4 Triton Fallback Repro

This repo verifies one focused serving path for `google/gemma-4-E2B-it` on
SGLang:

1. native LoRA adapter serving fails for the trained adapter
2. merging the adapter outside SGLang avoids that loader path
3. the merged model serves successfully with Triton attention
4. the same merged model fails with FlashInfer attention

The goal is not to benchmark or compare serving systems. The goal is to keep a
small, repeatable repro for Gemma 4 E2B merge-and-serve behavior on the tested
CUDA 13 stack.

The useful takeaway is that merge-and-serve is the workaround, Triton is the
serving backend that passes, and FlashInfer remains a reproducible failure path.

## Expected Outcomes

| Path | Expected result |
| --- | --- |
| Native LoRA | Fails before readiness while loading adapter weights |
| Merged model with Triton | Passes the chat-completions smoke test |
| Merged model with FlashInfer | Reaches readiness, then fails during paged prefill |

See [docs/verification.md](docs/verification.md) for the commands that verify
each row, including timed baseline and post-merge scoring runs.

## Quick Start

On the Paperspace Gradient box, start with setup:

```bash
scripts/setup/setup-paperspace.sh
```

Then follow the end-to-end verification runbook in
[docs/verification.md](docs/verification.md).

Set `HF_TOKEN` before downloading if Hugging Face requires gated model access.

## What This Builds

The repro uses a tiny synthetic ticket-triage fixture to train a PEFT LoRA
adapter, then merges that adapter into standalone model weights.

Default artifact paths:

```text
models/gemma4-e2b-it/905e84b50c4d2a365ebde34e685027578e6728db
adapters/google-gemma-4-e2b-it-ticket-triage-lora/905e84b50c4d2a365ebde34e685027578e6728db
models/gemma4-e2b-it-ticket-triage-merged/905e84b50c4d2a365ebde34e685027578e6728db
```

Generated model weights, adapters, and run logs are ignored by git.

## Repo Map

```text
fixtures/ticket-triage/   Small synthetic fixture
scripts/setup/            Paperspace, CUDA compat, uv, and SGLang setup
scripts/training/         Model download, adapter training, adapter merge
scripts/serving/          Native LoRA and merged-model serving checks
docs/                     Verification runbook and observed run notes
```

Useful docs:

- [docs/verification.md](docs/verification.md): run the repro in order
- Reproduce the FlashInfer failure:
  [docs/verification.md#10-verify-flashinfer-failure](docs/verification.md#10-verify-flashinfer-failure)
- [docs/observed-results.md](docs/observed-results.md): dated logs and results
- [scripts/setup/README.md](scripts/setup/README.md): environment setup details
- [scripts/training/README.md](scripts/training/README.md): artifact build details
- [scripts/serving/README.md](scripts/serving/README.md): serving command details
