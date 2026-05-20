# Docs

- [verification.md](verification.md): canonical runbook for verifying the repo
  claims in order, including timed base and merged scoring runs.
- [reproduce-failure.md](reproduce-failure.md): shortest path to reproduce the
  native LoRA failure and merged Triton workaround.
- [observed-results.md](observed-results.md): dated environment details, run
  results, and log excerpts from the recorded repro.
- [run-results/2026-05-20.md](run-results/2026-05-20.md): latest tracked
  metrics summary from the local run. Raw `score.json` files are intentionally
  tracked under `runs/`; server logs stay ignored.
- [issues/](issues/): ready-to-file SGLang issue drafts for the native LoRA
  loader failure and FlashInfer request-time failure.
