# Serving Scripts

These scripts reproduce the SGLang behavior this repo is about:

1. native LoRA serving fails before readiness
2. merged-model serving passes with Triton attention
3. the same merged model fails with FlashInfer after readiness

Run setup and training first:

```bash
. scripts/setup/gradient-env.sh
scripts/setup/install-sglang.sh
scripts/training/download-model.sh
scripts/training/train-lora.sh --max-train-examples 16 --epochs 1 --log-every-steps 4
scripts/training/merge-lora.sh
scripts/setup/install-sglang.sh
```

## Native LoRA Failure

```bash
BATCH_SIZE=8 STARTUP_TIMEOUT_SECONDS=900 \
  scripts/serving/run-sglang-native-lora-check.sh
```

The recorded run failed before readiness while loading adapter weights.

## Processor Metadata

Check the merged model:

```bash
scripts/serving/check-processor-configs.sh \
  models/gemma4-e2b-it-ticket-triage-merged/905e84b50c4d2a365ebde34e685027578e6728db
```

Repair from the source model if needed:

```bash
scripts/serving/repair-processor-configs.sh \
  models/gemma4-e2b-it/905e84b50c4d2a365ebde34e685027578e6728db \
  models/gemma4-e2b-it-ticket-triage-merged/905e84b50c4d2a365ebde34e685027578e6728db
```

## Triton Pass

```bash
CONTEXT_LENGTH=8192 STARTUP_TIMEOUT_SECONDS=900 \
  scripts/serving/run-merged-sglang-check.sh \
  models/gemma4-e2b-it-ticket-triage-merged/905e84b50c4d2a365ebde34e685027578e6728db
```

`serve-merged-sglang.sh` defaults to:

```bash
--attention-backend triton \
--sampling-backend pytorch \
--disable-cuda-graph
```

The check waits for `/model_info`, calls `/v1/chat/completions`, and verifies
non-empty assistant message content.

## FlashInfer Failure

```bash
ATTENTION_BACKEND=flashinfer \
CONTEXT_LENGTH=8192 STARTUP_TIMEOUT_SECONDS=900 \
  scripts/serving/run-merged-sglang-check.sh \
  models/gemma4-e2b-it-ticket-triage-merged/905e84b50c4d2a365ebde34e685027578e6728db
```

The recorded FlashInfer run reached readiness, then failed during paged prefill.
