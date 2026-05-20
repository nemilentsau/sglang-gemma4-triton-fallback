# Reproduce Failure And Workaround

This is the shortest path to verify the repo's core claim:

1. native SGLang LoRA serving fails before readiness
2. merging the adapter outside SGLang avoids the native LoRA loader
3. the merged model serves through SGLang with Triton attention

For environment details, use [../scripts/setup/README.md](../scripts/setup/README.md).
For the full runbook, including baseline and post-merge scoring, use
[verification.md](verification.md).

## 1. Setup

```bash
scripts/setup/setup-paperspace.sh
```

Expected:

- CUDA driver API reports `13000` through `/usr/local/cuda/compat`
- `sglang==0.5.12` imports successfully

## 2. Build The Adapter

```bash
scripts/training/download-model.sh

scripts/training/train-lora.sh \
  --max-train-examples 16 \
  --epochs 1 \
  --log-every-steps 4
```

Training refreshes the uv environment, so reinstall SGLang before serving:

```bash
scripts/setup/install-sglang.sh
```

## 3. Reproduce Native LoRA Failure

```bash
BATCH_SIZE=8 STARTUP_TIMEOUT_SECONDS=900 \
  scripts/serving/run-sglang-native-lora-check.sh
```

Expected: SGLang exits before `/model_info` readiness while loading the adapter.
The confirmed failure is:

```text
RuntimeError: Failed to load LoRA adapter ticket-triage:
'base_model.model.model.language_model.layers.15.self_attn.v_proj.lora_A.weight'
```

## 4. Merge The Adapter

```bash
scripts/training/merge-lora.sh
```

Training/merge commands can refresh the uv environment, so reinstall SGLang
again before serving:

```bash
scripts/setup/install-sglang.sh
```

## 5. Verify Merged Triton Path

Check processor metadata:

```bash
scripts/serving/check-processor-configs.sh \
  models/gemma4-e2b-it-ticket-triage-merged/905e84b50c4d2a365ebde34e685027578e6728db
```

Run the merged smoke test:

```bash
CONTEXT_LENGTH=8192 STARTUP_TIMEOUT_SECONDS=900 \
  scripts/serving/run-merged-sglang-check.sh \
  models/gemma4-e2b-it-ticket-triage-merged/905e84b50c4d2a365ebde34e685027578e6728db
```

Expected:

- SGLang reaches `/model_info`
- `/v1/chat/completions` returns non-empty assistant content
- the command prints `Gemma 4 SGLang smoke test complete`

## Optional FlashInfer Failure

```bash
ATTENTION_BACKEND=flashinfer \
CONTEXT_LENGTH=8192 STARTUP_TIMEOUT_SECONDS=900 \
  scripts/serving/run-merged-sglang-check.sh \
  models/gemma4-e2b-it-ticket-triage-merged/905e84b50c4d2a365ebde34e685027578e6728db
```

Expected: `/model_info` becomes ready, then the chat-completions request fails
during FlashInfer paged prefill.
