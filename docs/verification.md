# Verification Runbook

Run these commands in order to verify the repo claims.

For Paperspace, CUDA compatibility, and `uv` setup details, see
[scripts/setup/README.md](../scripts/setup/README.md).

## 1. Setup

```bash
scripts/setup/setup-paperspace.sh
```

Expected:

- CUDA driver API reports `13000` through `/usr/local/cuda/compat`
- `torch.cuda.is_available()` is true after the uv environment is installed
- `sglang==0.5.12` imports successfully

## 2. Download The Pinned Model

```bash
scripts/training/download-model.sh
```

Expected:

- model snapshot is written under
  `models/gemma4-e2b-it/905e84b50c4d2a365ebde34e685027578e6728db`
- `download-manifest.json` records the resolved snapshot

Set `HF_TOKEN` first if Hugging Face requires gated model access.

## 3. Score The Base Model

```bash
CONTEXT_LENGTH=8192 STARTUP_TIMEOUT_SECONDS=900 \
  scripts/serving/run-base-sglang-score.sh
```

Expected:

- SGLang reaches `/model_info`
- score JSON is written under `runs/gemma4-base-score-*/score.json`
- score JSON includes `metrics` and `timing`
- timing records `max_concurrency`, warmup request count, request throughput,
  latency percentiles, and completion-token throughput when usage is returned

Defaults are `MAX_CONCURRENCY=8` and `WARMUP_EXAMPLES=8`. Use the same values
for base and merged runs. For a shorter first pass, add `MAX_EVAL_EXAMPLES=32`.

## 4. Train The Adapter

```bash
scripts/training/train-lora.sh \
  --max-train-examples 16 \
  --epochs 1 \
  --log-every-steps 4
```

Expected:

- adapter is written under
  `adapters/google-gemma-4-e2b-it-ticket-triage-lora/905e84b50c4d2a365ebde34e685027578e6728db`

Training refreshes the uv environment. Reinstall SGLang before serving checks:

```bash
scripts/setup/install-sglang.sh
```

## 5. Verify Native LoRA Failure

```bash
BATCH_SIZE=8 STARTUP_TIMEOUT_SECONDS=900 \
  scripts/serving/run-sglang-native-lora-check.sh
```

Expected:

- SGLang exits before `/model_info` readiness
- the server log shows adapter loading failure

This is the failure path kept for future SGLang compatibility checks.

## 6. Merge The Adapter

```bash
scripts/training/merge-lora.sh
```

Expected:

- merged model is written under
  `models/gemma4-e2b-it-ticket-triage-merged/905e84b50c4d2a365ebde34e685027578e6728db`

Reinstall SGLang again if the merge refreshed the uv environment:

```bash
scripts/setup/install-sglang.sh
```

## 7. Check Processor Metadata

```bash
scripts/serving/check-processor-configs.sh \
  models/gemma4-e2b-it-ticket-triage-merged/905e84b50c4d2a365ebde34e685027578e6728db
```

If the required processor config is missing, repair from the source model:

```bash
scripts/serving/repair-processor-configs.sh \
  models/gemma4-e2b-it/905e84b50c4d2a365ebde34e685027578e6728db \
  models/gemma4-e2b-it-ticket-triage-merged/905e84b50c4d2a365ebde34e685027578e6728db
```

Expected:

- `processor_config.json` is present in the merged model directory

## 8. Score The Merged Model With Triton

```bash
CONTEXT_LENGTH=8192 STARTUP_TIMEOUT_SECONDS=900 \
  scripts/serving/run-merged-sglang-score.sh
```

Expected:

- SGLang reaches `/model_info`
- score JSON is written under `runs/gemma4-merged-score-*/score.json`
- score JSON includes `metrics` and `timing`

Use the same `MAX_EVAL_EXAMPLES`, `MAX_CONCURRENCY`, and `WARMUP_EXAMPLES`
values as the base-model run when comparing timing.

## 9. Verify Triton Smoke Test

```bash
CONTEXT_LENGTH=8192 STARTUP_TIMEOUT_SECONDS=900 \
  scripts/serving/run-merged-sglang-check.sh \
  models/gemma4-e2b-it-ticket-triage-merged/905e84b50c4d2a365ebde34e685027578e6728db
```

Expected:

- SGLang reaches `/model_info`
- `/v1/chat/completions` returns non-empty assistant content
- the command prints `Gemma 4 SGLang smoke test complete`

The merged serving script defaults to:

```bash
--attention-backend triton \
--sampling-backend pytorch \
--disable-cuda-graph
```

## 10. Verify FlashInfer Failure

```bash
ATTENTION_BACKEND=flashinfer \
CONTEXT_LENGTH=8192 STARTUP_TIMEOUT_SECONDS=900 \
  scripts/serving/run-merged-sglang-check.sh \
  models/gemma4-e2b-it-ticket-triage-merged/905e84b50c4d2a365ebde34e685027578e6728db
```

Expected:

- SGLang reaches `/model_info`
- the chat-completions smoke test fails during FlashInfer paged prefill

Recorded failures are documented in [observed-results.md](observed-results.md)
and [run-results/2026-05-20.md](run-results/2026-05-20.md).
