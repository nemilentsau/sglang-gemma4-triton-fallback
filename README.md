# Gemma 4 on SGLang: Triton Fallback

This repository is a minimal, standalone repro for the Gemma 4 E2B serving path
we found while testing LoRA adapters on SGLang.

The short version:

- Native LoRA loading fails for `google/gemma-4-E2B-it` on the tested
  `sglang==0.5.12` stack.
- Merging the adapter outside SGLang produces a servable Hugging Face artifact.
- That merged artifact still needs the Triton attention backend. With
  FlashInfer, SGLang reaches `/model_info`, then the chat-completions smoke test
  fails during paged prefill.
- The working path is unquantized merge-and-serve with:

```bash
--attention-backend triton \
--sampling-backend pytorch \
--disable-cuda-graph
```

This is not a benchmark and not a general Gemma 4 support matrix. It is a small
reproduction of one compatibility story: Gemma 4 E2B, a tiny synthetic LoRA
adapter, SGLang 0.5.12, CUDA 13, and the backend setting that made serving work.

## Tested Result

Recorded on 2026-05-19:

| Item | Value |
| --- | --- |
| Base model | `google/gemma-4-E2B-it` |
| Revision | `905e84b50c4d2a365ebde34e685027578e6728db` |
| SGLang | `sglang==0.5.12` |
| Torch | `torch==2.11.0+cu130` |
| FlashInfer | `flashinfer-python==0.6.11.post1` |
| GPU | NVIDIA RTX A6000, 49140 MiB |
| CUDA driver API | 13000 through `/usr/local/cuda/compat` |
| Native LoRA | Failed before readiness |
| Merge-and-serve with Triton | Passed chat-completions smoke test |
| Merge-and-serve with FlashInfer | Reached readiness, then failed during paged prefill |

The FlashInfer failure log included:

```text
Bidirectional attention for image tokens requires TritonAttnBackend.
Falling back to causal attention, which may degrade image quality.

RuntimeError: Error in function 'BatchPrefillWithPagedKVCacheDispatched'
FlashInfer Internal Error: Invalid configuration :
NUM_MMA_Q=1 NUM_MMA_D_QK=32 NUM_MMA_D_VO=32 NUM_MMA_KV=1
NUM_WARPS_Q=4 NUM_WARPS_KV=1
```

See [docs/observed-results.md](docs/observed-results.md) for the fuller run
notes.

## Repository Layout

```text
fixtures/ticket-triage/     Tiny synthetic chat fixture used to create adapter behavior
scripts/download-model.sh   Download the pinned Gemma 4 E2B snapshot
scripts/train-lora.sh       Train the small PEFT LoRA adapter
scripts/run-sglang-native-lora-check.sh
                            Show the native LoRA failure path
scripts/merge-lora.sh       Merge the adapter into standalone weights
scripts/serve-merged-sglang.sh
                            Start SGLang with the Triton fallback defaults
scripts/run-merged-sglang-check.sh
                            Start server, wait for /model_info, run smoke test
scripts/smoke-test.sh       Validate OpenAI-compatible chat completions
```

Generated model weights, adapters, and run logs are intentionally ignored.

## Environment

The commands assume `uv` and a CUDA-capable Linux machine. The recorded run used
the SGLang CUDA 13 runtime container on Paperspace. If you are using the same
kind of notebook, source the compatibility environment before running torch or
SGLang:

```bash
. scripts/gradient-env.sh
```

Install the Python environment:

```bash
uv sync --extra dev --extra train --extra model --extra download
```

If the Gemma model requires gated Hugging Face access in your environment, set
`HF_TOKEN` before downloading.

## Reproduce

Download the pinned model:

```bash
scripts/download-model.sh
```

Train the small adapter:

```bash
scripts/train-lora.sh \
  --max-train-examples 16 \
  --epochs 1 \
  --log-every-steps 4
```

Install SGLang after training. The training command runs `uv sync`, so install
the serving package after the adapter is created:

```bash
scripts/install-sglang.sh
```

Try native LoRA in SGLang:

```bash
BATCH_SIZE=8 STARTUP_TIMEOUT_SECONDS=900 \
  scripts/run-sglang-native-lora-check.sh
```

The recorded run failed before readiness while loading adapter weights. That is
the reason this repo carries the merge-and-serve path.

Merge the adapter:

```bash
scripts/merge-lora.sh
```

Reinstall SGLang before serving if the merge command refreshed the uv
environment:

```bash
scripts/install-sglang.sh
```

Check or repair the Gemma processor metadata:

```bash
scripts/check-processor-configs.sh \
  models/gemma4-e2b-it-ticket-triage-merged/905e84b50c4d2a365ebde34e685027578e6728db

scripts/repair-processor-configs.sh \
  models/gemma4-e2b-it/905e84b50c4d2a365ebde34e685027578e6728db \
  models/gemma4-e2b-it-ticket-triage-merged/905e84b50c4d2a365ebde34e685027578e6728db
```

Run the working Triton fallback check:

```bash
CONTEXT_LENGTH=8192 STARTUP_TIMEOUT_SECONDS=900 \
  scripts/run-merged-sglang-check.sh \
  models/gemma4-e2b-it-ticket-triage-merged/905e84b50c4d2a365ebde34e685027578e6728db
```

The runner starts SGLang, waits for `/model_info`, calls
`/v1/chat/completions`, and verifies that the assistant message content is
non-empty.

To reproduce the backend failure, override the attention backend:

```bash
ATTENTION_BACKEND=flashinfer \
CONTEXT_LENGTH=8192 STARTUP_TIMEOUT_SECONDS=900 \
  scripts/run-merged-sglang-check.sh \
  models/gemma4-e2b-it-ticket-triage-merged/905e84b50c4d2a365ebde34e685027578e6728db
```

The recorded FlashInfer run reached readiness, then failed the chat-completions
smoke test.

## What This Does Not Claim

- It does not claim Gemma 4 native LoRA is impossible.
- It does not claim the adapter is useful for production.
- It does not measure throughput.
- It does not generalize beyond the pinned model, SGLang stack, and commands
  recorded here.

Every compatibility statement in this repo should be tied to an actual command
and a log excerpt.
