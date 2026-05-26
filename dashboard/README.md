# The Gemma 4 Serving Mystery — presentation dashboard

A SvelteKit slide deck explaining the SGLang 0.5.12 Gemma 4 E2B serving pitfalls
documented in this repo, framed as a detective story for an audience that knows
LLMs but has never heard of SGLang.

## Run it

```bash
cd dashboard
npm install
npm run dev      # live, for editing
# or
npm run build && npm run preview   # static build, for presenting
```

> If you rebuild while a `preview` server is already running, restart it —
> `vite preview` serves the assets it started with and won't pick up a new build.

## Present it

- `→` / `Space` — next slide
- `←` — previous slide
- left-click — next · right-click — previous
- `o` — overview grid (click a thumbnail to jump) · `Esc` — close overview

11 slides: cold open → 4-part concept primer (inference server → SGLang → LoRA →
attention backends) → mission → two "crimes" (the LoRA load failure, the
ready-but-crashing FlashInfer path) → the fix → charts from the 2026-05-20 run →
lessons.

## How it's built

- Static SvelteKit (`adapter-static`), Svelte 5 runes, TypeScript. No backend, no
  live model calls — the deck reads baked-in data.
- `src/lib/stores/deck.ts` — slide index + ordered registry.
- `src/lib/data/runResults.ts`, `evidence.ts` — the real benchmark numbers and the
  real SGLang log/error strings.
- `src/lib/components/slides/*.svelte` — one component per slide.
- `src/lib/components/charts/*` — hand-built bar/latency charts (no chart library).

## Test

```bash
npm run test     # vitest: deck store + data invariants
npm run check    # svelte-check type pass
```
