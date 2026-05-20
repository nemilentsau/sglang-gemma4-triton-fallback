# Observed Results

Date: 2026-05-19

For the latest local run summary and metrics, see
[run-results/2026-05-20.md](run-results/2026-05-20.md).

## Artifact

- Base model: `google/gemma-4-E2B-it`
- Revision: `905e84b50c4d2a365ebde34e685027578e6728db`
- Source path:
  `models/gemma4-e2b-it/905e84b50c4d2a365ebde34e685027578e6728db`
- Adapter path:
  `adapters/google-gemma-4-e2b-it-ticket-triage-lora/905e84b50c4d2a365ebde34e685027578e6728db`
- Merged path:
  `models/gemma4-e2b-it-ticket-triage-merged/905e84b50c4d2a365ebde34e685027578e6728db`

## Environment

- GPU: NVIDIA RTX A6000, 49140 MiB
- Driver: 550.144.03
- Torch CUDA: 13.0
- SGLang: `0.5.12`
- Torch: `2.11.0+cu130`
- Training Transformers: `5.8.1`
- Serving Transformers after SGLang install: `5.6.0`
- PEFT: `0.19.1`
- FlashInfer: `0.6.11.post1`
- cuDNN: `nvidia-cudnn-cu13==9.19.0.56`

## Native LoRA Failure

Command:

```bash
BATCH_SIZE=8 STARTUP_TIMEOUT_SECONDS=900 \
  scripts/serving/run-sglang-native-lora-check.sh
```

First, an adapter with regex target modules failed because SGLang only accepts
the string target modules `all` or `all-linear`.

After regenerating the adapter with explicit language-tower target module names,
SGLang failed while loading adapter weights:

```text
Failed to load LoRA adapter ticket-triage:
'base_model.model.model.language_model.layers.15.self_attn.v_proj.lora_A.weight'
```

The repro keeps this path so future SGLang versions can be checked against the
same adapter shape.

## Triton Merge-and-Serve Pass

Command:

```bash
CONTEXT_LENGTH=8192 STARTUP_TIMEOUT_SECONDS=900 \
  scripts/serving/run-merged-sglang-check.sh \
  models/gemma4-e2b-it-ticket-triage-merged/905e84b50c4d2a365ebde34e685027578e6728db
```

Result:

```text
Gemma 4 SGLang smoke test complete
Server log: runs/gemma4-merged-sglang-20260519T203652Z/server.log
```

The serving defaults were:

```bash
--attention-backend triton \
--sampling-backend pytorch \
--disable-cuda-graph
```

The smoke test used `/v1/chat/completions` because the raw `/generate` endpoint
returned empty text for this Gemma 4 E2B prompt shape.

## FlashInfer Backend Failure

Command:

```bash
ATTENTION_BACKEND=flashinfer \
CONTEXT_LENGTH=8192 STARTUP_TIMEOUT_SECONDS=900 \
  scripts/serving/run-merged-sglang-check.sh \
  models/gemma4-e2b-it-ticket-triage-merged/905e84b50c4d2a365ebde34e685027578e6728db
```

Result: `/model_info` became ready, then the chat-completions smoke test hit a
server-side scheduler failure and the client saw:

```text
http.client.RemoteDisconnected: Remote end closed connection without response
```

Relevant server log excerpt:

```text
Bidirectional attention for image tokens requires TritonAttnBackend.
Falling back to causal attention, which may degrade image quality.

RuntimeError: Error in function 'BatchPrefillWithPagedKVCacheDispatched'
FlashInfer Internal Error: Invalid configuration :
NUM_MMA_Q=1 NUM_MMA_D_QK=32 NUM_MMA_D_VO=32 NUM_MMA_KV=1
NUM_WARPS_Q=4 NUM_WARPS_KV=1
```

Conclusion: for this Gemma 4 E2B merged artifact on the recovered CUDA 13
SGLang 0.5.12 stack, FlashInfer was not a working replacement for Triton
attention.
