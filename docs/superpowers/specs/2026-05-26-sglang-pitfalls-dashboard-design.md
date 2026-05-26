# Design: "The Gemma 4 Serving Mystery" — SvelteKit presentation dashboard

**Date:** 2026-05-26
**Status:** Approved (arc + tone), pending spec review

## Goal

A live-presentable dashboard that explains the SGLang serving pitfalls documented in
this repo to an audience that **knows what an LLM is but has never heard of SGLang**.
The deck teaches the necessary concepts from scratch, then walks the audience through
the two failures we hit and the working fix, framed as a detective story, with real
charts from our recorded run.

## Audience & framing decisions (confirmed)

- **Use:** Live presentation walkthrough — keyboard/click-driven, slide-like, one idea per view, big type.
- **Depth:** Teach the concepts. Assume zero serving knowledge (explain inference server, SGLang, LoRA adapter, attention backend before any pitfall).
- **Tone:** Detective story — symptom → investigation → root cause → fix, with real error logs shown as "evidence."
- **Data:** Feature real benchmark numbers as interactive charts.

## Tech & mechanics

- **Framework:** SvelteKit, single client-rendered route (`/`). Static-buildable (`adapter-static`) so it can be served as plain files or run via `npm run dev`.
- **Slide controller:** a Svelte store tracking `currentSlide`. Navigation:
  - `→` / `Space` / click-right → next; `←` → previous.
  - `o` → overview grid (thumbnails, click to jump).
  - `Esc` → close overview.
  - Bottom progress rail + section dots reflect position.
- **Charts:** hand-built inline-SVG Svelte components (no chart library) so they animate on slide-enter and match the theme. Bar charts (throughput) and grouped bars / dot plot (latency percentiles).
- **Data:** baked-in TypeScript module holding the real figures (no fetch, no backend):
  - Base: total 39.90s, 5.01 req/s, p50 1.55s, p95 1.87s, p99 1.98s, 216.54 completion tok/s.
  - Merged+Triton: total 33.26s, 6.01 req/s, p50 1.27s, p95 1.74s, p99 1.85s, 194.18 completion tok/s.
  - Both: 200/200 valid JSON (100%); 0/200 exact match (by design — synthetic fixture).
  - Environment: RTX A6000 (sm_86), SGLang 0.5.12, Torch 2.11.0+cu130, FlashInfer 0.6.11.post1.
- **No backend, no model calls, no auth.** Purely static presentation reading baked-in data.

## Visual design

- Detective / "case file" aesthetic on a terminal-grade dark canvas.
- Monospace family for logs, error messages, and command snippets; a clean sans for prose headings.
- Restrained noir accent (single warm/amber highlight) plus status colors: red = fail, amber = misleading/partial, green = pass.
- Real SGLang stack traces and warnings rendered in a "evidence card" treatment (monospace, framed, line-highlighted on the load-bearing line).
- Big type, generous spacing, one idea per slide. Slide-enter transitions (fade/translate); chart elements animate in.

## Narrative arc (slide sequence)

The 8-beat arc is preserved; beat 2 (the concept primer) is split into a short
mini-sequence of its own slides.

1. **Cold open** — title card: "We just wanted to serve a fine-tuned model. It took three tries." Sets the detective tone.

2. **The cast (concept primer — split into a few slides):**
   - 2a. **The inference server** — what sits between model weights and an API endpoint; why you don't just call `model(...)` in prod.
   - 2b. **What SGLang is** — one popular such server; where it fits in the stack.
   - 2c. **LoRA adapters** — fine-tuning as a small "patch" on a base model; "native LoRA" vs "merge then serve."
   - 2d. **Attention backends** — Triton vs FlashInfer as swappable engines under the hood; the idea that model *features* (e.g. image/bidirectional attention) may only be supported on some backends.
   - Diagram-driven, no drama yet.

3. **The mission** — the goal: serve a LoRA-tuned Gemma 4 E2B for ticket triage. Show the intended happy path (train adapter → load in SGLang → call API).

4. **Crime #1: the adapter that wouldn't load** — symptom: server dies *before* readiness. Evidence: real `RuntimeError: Failed to load LoRA adapter ticket-triage: '...language_model.layers.15.self_attn.v_proj.lora_A.weight'`. Investigation: Gemma 4's triple-nested `base_model.model.model.language_model...` key names vs what SGLang's loader expects; the earlier rejected `all`/`all-linear` `target_modules` attempt. Verdict.

5. **Crime #2: the server that lied** — the trickier one: merged model + FlashInfer *reaches readiness*, then dies on the **first real request**. Evidence: the load-bearing warning "Bidirectional attention for image tokens requires TritonAttnBackend. Falling back to causal attention..." then `FlashInfer Internal Error: Invalid configuration : NUM_MMA_Q=1 ...`. Root cause: Gemma 4's vision (bidirectional) attention is implemented only for the Triton backend; the FlashInfer fallback crashes in paged prefill. Emphasize: "readiness ≠ working."

6. **The solution** — the working recipe: merge the adapter outside SGLang (transformers) + pin `--attention-backend triton`. Three-path comparison panel:
   - Native LoRA → ❌ fails before readiness
   - Merged + FlashInfer → ⚠️ ready, then crashes on first request
   - Merged + Triton → ✅ passes smoke test + full scoring run

7. **The evidence room (charts)** — interactive charts from the real run: base vs merged throughput (req/s) and p50/p95/p99 latency; the 200/200 valid-JSON result. Honest caveat that exact-match is 0% by design (synthetic fixture, no task training signal). Environment footnote.

8. **Lessons / takeaways** — transferable morals: "readiness ≠ working"; backend support varies by model feature; adapter key conventions are fragile across loaders; when native LoRA fights you, merge-and-serve is a reliable escape hatch. Link back to the repo and the two issue drafts.

## Component structure

- `src/routes/+page.svelte` — mounts the deck, wires keyboard/click navigation, renders the active slide + chrome (progress rail, overview toggle).
- `src/lib/stores/deck.ts` — slide index store + next/prev/goto/overview actions; ordered slide registry.
- `src/lib/components/Deck.svelte` — layout shell, transition handling, progress rail, overview grid.
- `src/lib/components/slides/*.svelte` — one component per slide (Cold open, primer 2a–2d, Mission, Crime1, Crime2, Solution, Evidence, Lessons). Each is self-contained and independently understandable.
- `src/lib/components/EvidenceCard.svelte` — reusable framed monospace log/error block with optional highlighted line.
- `src/lib/components/PathBadge.svelte` — the ❌/⚠️/✅ status badge used in the comparison panel.
- `src/lib/components/charts/BarChart.svelte`, `LatencyChart.svelte` — inline-SVG, animate on mount.
- `src/lib/data/runResults.ts` — the baked-in figures + environment metadata, typed.
- `src/lib/data/evidence.ts` — the real log/error strings (LoRA RuntimeError, FlashInfer warning + Invalid configuration), centralized so slides stay clean.

## Error handling / edge cases

- Navigation clamps at first/last slide: no wrap-around; advancing past the last (or before the first) slide is a no-op.
- Resize: layout is responsive but optimized for a 16:9 projector; verify legibility down to a laptop screen.
- Overview grid must be reachable and dismissable purely by keyboard.

## Testing

- Component-level: deck store advances/clamps correctly (unit test on `deck.ts`).
- A lightweight Playwright smoke check: load `/`, press `→` through all slides without console errors, open/close overview. (Playwright MCP is available in this environment.)
- Manual: present at 16:9, confirm type legibility and that charts animate.

## Out of scope (YAGNI)

- No backend, no live model inference, no API calls, no auth.
- No CMS/markdown-driven slides — slides are hand-authored Svelte components for full design control.
- No speaker-notes view or remote-control sync (single-screen live presentation only).
- No unrelated refactoring of the existing Python repo.
