# Training Scripts

These scripts build the local artifacts used by the repro:

1. download the pinned Gemma 4 E2B snapshot
2. train a tiny synthetic PEFT LoRA adapter
3. merge the adapter into standalone model weights

Run setup first:

```bash
scripts/setup/setup-paperspace.sh
```

## Download The Pinned Model

```bash
scripts/training/download-model.sh
```

Defaults:

- model: `google/gemma-4-E2B-it`
- revision: `905e84b50c4d2a365ebde34e685027578e6728db`
- output: `models/gemma4-e2b-it/905e84b50c4d2a365ebde34e685027578e6728db`

Set `HF_TOKEN` first if the model requires gated access.

## Train The Adapter

```bash
scripts/training/train-lora.sh \
  --max-train-examples 16 \
  --epochs 1 \
  --log-every-steps 4
```

The trainer targets Gemma 4 language-tower linear modules and writes the adapter
under:

```text
adapters/google-gemma-4-e2b-it-ticket-triage-lora/905e84b50c4d2a365ebde34e685027578e6728db
```

## Merge The Adapter

Install SGLang after training if you plan to run serving checks. The training
script refreshes the uv environment, so rerun:

```bash
scripts/setup/install-sglang.sh
```

Merge the adapter:

```bash
scripts/training/merge-lora.sh
```

The merged model is written under:

```text
models/gemma4-e2b-it-ticket-triage-merged/905e84b50c4d2a365ebde34e685027578e6728db
```

After merging, run the serving checks in [../serving](../serving/README.md).
