# Issue draft: Native LoRA

**Target repo:** `sgl-project/sglang`
**Title:** `[Bug] Gemma 4 E2B native LoRA adapter load fails with missing lora_A weight`
**Labels:** `Bug` (auto)

---

### Checklist
- [x] I searched related issues but found no solution.
- [x] The bug persists in the latest version available to me (0.5.12).
- [x] Environment info and a minimal reproducible demo are provided below.
- [x] This is a bug report, not a general question.
- [x] English.

### Describe the bug

Loading a PEFT LoRA adapter trained against `google/gemma-4-E2B-it` into SGLang 0.5.12 via `--lora-paths` fails before `/model_info` readiness with a missing-weight `RuntimeError` for `lora_A` keys on language-tower attention projections.

The adapter was trained with PEFT against explicit Gemma 4 language-tower module names (after an earlier regex `target_modules` attempt was rejected by SGLang's `all` / `all-linear` constraint). The resulting adapter checkpoint contains weights of the form `base_model.model.model.language_model.layers.<N>.self_attn.{q,k,v,o}_proj.lora_{A,B}.weight`, but SGLang's loader fails to locate `lora_A` at the key shape it expects.

This appears to be a PEFT-key to SGLang-internal-name mapping mismatch specific to Gemma 4's `model.language_model.layers.*` nesting.

Merging the adapter into standalone weights outside SGLang and serving the merged model works with Triton attention. The FlashInfer request-time failure is tracked separately in this repo's `docs/issues/flashinfer-bug.md` draft.

### Reproduction

Full repro (commands, fixtures, expected outputs): https://github.com/nemilentsau/sglang-gemma4-triton-fallback — specifically [docs/reproduce-failure.md#3-reproduce-native-lora-failure](https://github.com/nemilentsau/sglang-gemma4-triton-fallback/blob/main/docs/reproduce-failure.md#3-reproduce-native-lora-failure).

Minimal command (after the training step in the linked repo):

```bash
BATCH_SIZE=8 STARTUP_TIMEOUT_SECONDS=900 \
  scripts/serving/run-sglang-native-lora-check.sh
```

That script invokes `sglang.launch_server` with `--lora-paths ticket-triage=adapters/google-gemma-4-e2b-it-ticket-triage-lora/905e84b50c4d2a365ebde34e685027578e6728db` against the pinned base model (`google/gemma-4-E2B-it` revision `905e84b50c4d2a365ebde34e685027578e6728db`).

**Expected:** SGLang reaches `/model_info` and the adapter serves.

**Actual:** SGLang exits before readiness with:

```text
RuntimeError: Failed to load LoRA adapter ticket-triage:
'base_model.model.model.language_model.layers.15.self_attn.v_proj.lora_A.weight'
```

Adapter details:
- Trained with PEFT `0.19.1`, rank 8, on a 16-example synthetic ticket-triage fixture (the fixture is intentionally synthetic and is *not* a quality benchmark — it exists only to produce a reproducible Gemma 4 LoRA adapter shape).
- `target_modules` was set to explicit language-tower names after `all-linear` and regex variants did not produce a loadable adapter.

### Environment

Local stack (full details in [docs/observed-results.md](https://github.com/nemilentsau/sglang-gemma4-triton-fallback/blob/main/docs/observed-results.md)):

- SGLang: `0.5.12`
- Torch: `2.11.0+cu130`
- Transformers (serving): `5.6.0`
- PEFT: `0.19.1`
- FlashInfer: `0.6.11.post1`
- cuDNN: `nvidia-cudnn-cu13==9.19.0.56`
- CUDA driver API: `13000` via `/usr/local/cuda/compat`
- GPU: NVIDIA RTX A6000 (49140 MiB), driver `550.144.03`
- Container: `lmsysorg/sglang:v0.5.12-cu130-runtime` on Paperspace Gradient

### Note on scope

This repro is narrow: synthetic 16-example fixture, single-GPU A6000, CUDA 13 compat layer. The merged-model Triton serving path that works is only verified for the chat-completions smoke test and a 200-example scoring run documented in the linked repo — not under sustained load.
