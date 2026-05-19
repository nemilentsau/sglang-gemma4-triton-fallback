# SGLang Gemma 4 Triton Fallback Repro

This repo is a runnable repro for a Gemma 4 LoRA serving failure in SGLang and
the recovery path that worked in the tested stack:

> `sglang==0.5.12` fails to serve the `google/gemma-4-E2B-it` LoRA adapter
> natively on the tested CUDA 13 stack. Merging the adapter into standalone
> model weights avoids SGLang's native LoRA loader, but the merged model still
> needs `--attention-backend triton` to pass the serving smoke test.

The repo gives you the smallest end-to-end path that demonstrates that behavior:

1. download the pinned Gemma 4 E2B snapshot
2. train a tiny synthetic PEFT LoRA adapter
3. reproduce the native LoRA adapter-loading failure
4. merge the adapter outside SGLang
5. serve the merged model with Triton attention
6. reproduce the FlashInfer failure by changing one environment variable

The useful takeaway is the full failure chain: native LoRA adapter serving fails
first, merge-and-serve is the workaround, and Triton attention is still required
for the merged serving path.

## Why Triton

Gemma 4 goes through SGLang's multimodal Gemma serving path. The observed server
log says:

```text
Bidirectional attention for image tokens requires TritonAttnBackend.
Falling back to causal attention, which may degrade image quality.
```

When `ATTENTION_BACKEND=flashinfer` is selected, SGLang reaches `/model_info`,
then the first chat-completions smoke test fails in FlashInfer paged prefill:

```text
RuntimeError: Error in function 'BatchPrefillWithPagedKVCacheDispatched'
FlashInfer Internal Error: Invalid configuration :
NUM_MMA_Q=1 NUM_MMA_D_QK=32 NUM_MMA_D_VO=32 NUM_MMA_KV=1
NUM_WARPS_Q=4 NUM_WARPS_KV=1
```

With `ATTENTION_BACKEND=triton`, the same merged artifact passes the
chat-completions smoke test. That is the core repro.

## Tested Stack

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
| Merged model with Triton | Passed chat-completions smoke test |
| Merged model with FlashInfer | Reached readiness, then failed during paged prefill |

See [docs/observed-results.md](docs/observed-results.md) for the run notes and
log excerpts.

## Repository Layout

```text
fixtures/ticket-triage/     Synthetic chat fixture used to create adapter behavior
scripts/download-model.sh   Download the pinned Gemma 4 E2B snapshot
scripts/train-lora.sh       Train the small PEFT LoRA adapter
scripts/run-sglang-native-lora-check.sh
                            Reproduce native LoRA loading failure
scripts/merge-lora.sh       Merge the adapter into standalone weights
scripts/serve-merged-sglang.sh
                            Start SGLang with Triton fallback defaults
scripts/run-merged-sglang-check.sh
                            Start server, wait for /model_info, run smoke test
scripts/smoke-test.sh       Validate OpenAI-compatible chat completions
```

Generated model weights, adapters, and run logs are ignored.

## Environment

Use `uv` and a CUDA-capable Linux machine. The recorded run used the SGLang
CUDA 13 runtime container on Paperspace. In that environment, source the CUDA
compatibility settings before running torch or SGLang:

```bash
. scripts/gradient-env.sh
```

Install the Python environment:

```bash
uv sync --extra dev --extra train --extra model --extra download
```

Set `HF_TOKEN` before downloading if Hugging Face requires gated model access.

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

Reproduce the native LoRA failure:

```bash
BATCH_SIZE=8 STARTUP_TIMEOUT_SECONDS=900 \
  scripts/run-sglang-native-lora-check.sh
```

Merge the adapter:

```bash
scripts/merge-lora.sh
```

Reinstall SGLang before serving if the merge command refreshed the uv
environment:

```bash
scripts/install-sglang.sh
```

Check or repair Gemma processor metadata:

```bash
scripts/check-processor-configs.sh \
  models/gemma4-e2b-it-ticket-triage-merged/905e84b50c4d2a365ebde34e685027578e6728db

scripts/repair-processor-configs.sh \
  models/gemma4-e2b-it/905e84b50c4d2a365ebde34e685027578e6728db \
  models/gemma4-e2b-it-ticket-triage-merged/905e84b50c4d2a365ebde34e685027578e6728db
```

Run the Triton serving check:

```bash
CONTEXT_LENGTH=8192 STARTUP_TIMEOUT_SECONDS=900 \
  scripts/run-merged-sglang-check.sh \
  models/gemma4-e2b-it-ticket-triage-merged/905e84b50c4d2a365ebde34e685027578e6728db
```

The runner starts SGLang, waits for `/model_info`, calls
`/v1/chat/completions`, and verifies non-empty assistant message content.

Reproduce the FlashInfer failure:

```bash
ATTENTION_BACKEND=flashinfer \
CONTEXT_LENGTH=8192 STARTUP_TIMEOUT_SECONDS=900 \
  scripts/run-merged-sglang-check.sh \
  models/gemma4-e2b-it-ticket-triage-merged/905e84b50c4d2a365ebde34e685027578e6728db
```

The recorded FlashInfer run reached readiness, then failed the chat-completions
smoke test during paged prefill.
