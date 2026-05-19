# Setup Scripts

These scripts prepare the Paperspace Gradient environment used by this repro.
Run them before downloading the model, training the adapter, or starting
SGLang.

## Paperspace Gradient Notebook

Create a Paperspace Gradient notebook with these Advanced Options.

Repository:

```text
Workspace URL: https://github.com/nemilentsau/sglang-gemma4-triton-fallback.git
Ref: main
Username: blank
Password: blank
```

Container:

```text
Container Name: lmsysorg/sglang:v0.5.12-cu130-runtime
Registry username: blank
Registry password: blank
```

Start command:

```bash
bash -lc 'python3 -m pip install --no-cache-dir jupyterlab && exec jupyter lab --allow-root --ip=0.0.0.0 --port=8888 --no-browser --ServerApp.trust_xheaders=True --ServerApp.disable_check_xsrf=False --ServerApp.allow_remote_access=True --ServerApp.allow_origin="*" --ServerApp.allow_credentials=True'
```

The `Ref` field must be a branch or tag name such as `main`. Do not paste a
GitHub `/tree/...` URL.

## Enter The Repo

Open a notebook terminal:

```bash
cd /notebooks/sglang-gemma4-triton-fallback
```

Run the setup script:

```bash
scripts/setup/setup-paperspace.sh
```

That script:

- sources `scripts/setup/gradient-env.sh`
- verifies the CUDA driver API through `scripts/setup/verify-cuda-env.sh`
- installs the uv environment
- installs `sglang==0.5.12`
- verifies torch/SGLang import and CUDA state

## Install Python Dependencies

If you need to run the pieces manually, use:

```bash
scripts/setup/verify-cuda-env.sh
uv sync --extra dev --extra train --extra model --extra download
scripts/setup/install-sglang.sh
```

Train and merge scripts run `uv sync` for their own dependency groups, so install
SGLang after training and again after merging if the uv environment was
refreshed:

```bash
scripts/setup/install-sglang.sh
```

The install script verifies that `sglang.launch_server` imports and prints the
key package versions, including `sglang`, `torch`, `transformers`, `peft`, and
`nvidia-cudnn-cu13`.

## Hugging Face Access

Set `HF_TOKEN` before downloading if Hugging Face requires gated model access:

```bash
read -rsp "HF token: " HF_TOKEN && echo
export HF_TOKEN
```

Do not paste tokens into scripts or commit them.

## Restart Recovery

A Paperspace restart can keep the checkout, model files, adapters, and run logs
while losing shell state and the uv environment. Recover with:

```bash
cd /notebooks/sglang-gemma4-triton-fallback
scripts/setup/setup-paperspace.sh
```

Then rerun the relevant serving check from [../serving](../serving/README.md).
