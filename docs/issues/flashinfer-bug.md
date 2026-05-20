# Issue draft: FlashInfer

**Target repo:** `sgl-project/sglang`
**Title:** `[Bug] Gemma 4 E2B merged model fails with FlashInfer paged prefill invalid configuration`
**Labels:** `Bug` (auto)

---

### Checklist
- [x] I searched related issues but found no solution.
- [x] The bug persists in the latest version available to me (0.5.12).
- [x] Environment info and a minimal reproducible demo are provided below.
- [x] This is a bug report, not a general question.
- [x] English.

### Describe the bug

A merged Gemma 4 E2B model (base + PEFT LoRA adapter merged outside SGLang) starts cleanly under SGLang 0.5.12 with `--attention-backend flashinfer` and reaches `/model_info` readiness, but the first `/v1/chat/completions` request fails inside FlashInfer paged-prefill with `Invalid configuration`. The same merged model on the same box serves successfully with `--attention-backend triton`.

The server log emits this warning at startup before the crash, which appears load-bearing:

```text
Bidirectional attention for image tokens requires TritonAttnBackend.
Falling back to causal attention, which may degrade image quality.
```

That suggests Gemma 4's vision attention path is implemented only for the Triton backend, and the FlashInfer fallback then crashes during paged prefill. The crash may be a downstream effect of that fallback rather than an independent FlashInfer kernel bug, but I want to flag it because the server reaches readiness, which makes the failure surprising and only observable on the first real request.

### Reproduction

Full repro (commands, fixtures, expected outputs): https://github.com/nemilentsau/sglang-gemma4-triton-fallback — specifically [docs/verification.md#10-verify-flashinfer-failure](https://github.com/nemilentsau/sglang-gemma4-triton-fallback/blob/main/docs/verification.md#10-verify-flashinfer-failure).

Minimal command (after the merge step in the linked repo):

```bash
ATTENTION_BACKEND=flashinfer \
CONTEXT_LENGTH=8192 STARTUP_TIMEOUT_SECONDS=900 \
  scripts/serving/run-merged-sglang-check.sh \
  models/gemma4-e2b-it-ticket-triage-merged/905e84b50c4d2a365ebde34e685027578e6728db
```

**Expected:** SGLang reaches `/model_info` and `/v1/chat/completions` returns non-empty assistant content (as it does with Triton attention).

**Actual:** `/model_info` becomes ready, then the chat-completions request fails. Client sees:

```text
http.client.RemoteDisconnected: Remote end closed connection without response
```

Server log excerpt:

```text
Bidirectional attention for image tokens requires TritonAttnBackend.
Falling back to causal attention, which may degrade image quality.

RuntimeError: Error in function 'BatchPrefillWithPagedKVCacheDispatched'
FlashInfer Internal Error: Invalid configuration :
NUM_MMA_Q=1 NUM_MMA_D_QK=32 NUM_MMA_D_VO=32 NUM_MMA_KV=1
NUM_WARPS_Q=4 NUM_WARPS_KV=1
```

The merged Triton path on the same artifact passes — for this run that means the chat-completions smoke test and a 200-example synthetic-fixture scoring run documented in the linked repo. It is not a benchmark.

### Environment

Local stack (full details in [docs/observed-results.md](https://github.com/nemilentsau/sglang-gemma4-triton-fallback/blob/main/docs/observed-results.md)):

- SGLang: `0.5.12`
- Torch: `2.11.0+cu130`
- Transformers (serving): `5.6.0`
- PEFT: `0.19.1`
- FlashInfer: `0.6.11.post1`
- cuDNN: `nvidia-cudnn-cu13==9.19.0.56`
- CUDA driver API: `13000` via `/usr/local/cuda/compat`
- GPU: NVIDIA RTX A6000 (49140 MiB, sm_86), driver `550.144.03`
- Container: `lmsysorg/sglang:v0.5.12-cu130-runtime` on Paperspace Gradient

Model: `google/gemma-4-E2B-it` revision `905e84b50c4d2a365ebde34e685027578e6728db`, merged with a tiny synthetic PEFT LoRA adapter (rank 8, 16-example fixture — the fixture is synthetic and *not* a benchmark; it exists only to produce a reproducible serving artifact).

### Note on scope

The FlashInfer kernel `Invalid configuration` is hardware-sensitive (sm_86 selects a different kernel set than sm_90), so this exact failure may not reproduce on H100. The "FlashInfer not a working replacement for Triton on Gemma 4 E2B" conclusion is for this hardware/driver/stack combination only.
