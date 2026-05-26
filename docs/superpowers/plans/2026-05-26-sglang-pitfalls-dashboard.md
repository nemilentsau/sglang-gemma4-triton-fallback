# SGLang Pitfalls Presentation Dashboard — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a live-presentable SvelteKit slide deck (a "case file" detective story) that teaches an LLM-literate-but-SGLang-naive audience the two Gemma 4 serving pitfalls in this repo and the working fix, with real charts from the recorded run.

**Architecture:** A single static-rendered SvelteKit route hosts a keyboard/click-driven deck. A Svelte store (`deck.ts`) owns the current slide index and an ordered slide registry. Each slide is a self-contained component under `src/lib/components/slides/`. Real figures and real log/error strings live in typed data modules (`src/lib/data/`) so slides stay presentational. Charts are hand-built inline-SVG components (no chart library). The whole app builds to static files via `@sveltejs/adapter-static`.

**Tech Stack:** SvelteKit (Svelte 5 runes), TypeScript, Vite, `@sveltejs/adapter-static`, Vitest (unit), Playwright via the environment's Playwright MCP (smoke). The app lives in `dashboard/` so it stays isolated from the Python repo.

**Visual design note for the executor:** Slide-authoring tasks (Tasks 7–14) produce real, complete content (the headings, copy, and the actual error/log strings are all specified here), but the *visual polish* — exact spacing, motion, the noir/case-file treatment — should be done with the `frontend-design` skill invoked at the start of each slide-authoring task. The structure and content in this plan are the contract; the styling is yours to make excellent within the dark / monospace / single-amber-accent theme.

---

## File Structure

Created under `dashboard/`:

- `dashboard/package.json`, `svelte.config.js`, `vite.config.ts`, `tsconfig.json`, `.npmrc` — project config.
- `dashboard/src/app.html`, `src/app.css` — shell + global theme tokens.
- `dashboard/src/routes/+layout.ts` — disables SSR (`prerender = true`, `ssr = false` not needed; static prerender of one page).
- `dashboard/src/routes/+page.svelte` — mounts `Deck`, wires global keyboard/click handlers.
- `dashboard/src/lib/stores/deck.ts` — slide index store + `next`/`prev`/`goto`/`toggleOverview` + ordered slide registry metadata.
- `dashboard/src/lib/data/runResults.ts` — baked-in benchmark figures + environment metadata (typed).
- `dashboard/src/lib/data/evidence.ts` — real SGLang log/error strings.
- `dashboard/src/lib/components/Deck.svelte` — layout shell, slide transition, progress rail, overview grid.
- `dashboard/src/lib/components/EvidenceCard.svelte` — framed monospace log/error block with optional highlighted line.
- `dashboard/src/lib/components/PathBadge.svelte` — ❌/⚠️/✅ status badge.
- `dashboard/src/lib/components/charts/BarChart.svelte` — inline-SVG bar chart, animates on mount.
- `dashboard/src/lib/components/charts/LatencyChart.svelte` — inline-SVG grouped-bar latency chart.
- `dashboard/src/lib/components/slides/*.svelte` — one component per slide (13 slides).
- `dashboard/tests/deck.test.ts` — Vitest unit tests for the store.
- `dashboard/tests/data.test.ts` — Vitest unit tests for data invariants.
- `dashboard/README.md` — how to run/build/present.

Slide components (registry order):
1. `ColdOpen.svelte`
2. `PrimerServer.svelte`
3. `PrimerSglang.svelte`
4. `PrimerLora.svelte`
5. `PrimerBackends.svelte`
6. `Mission.svelte`
7. `Crime1.svelte`
8. `Crime2.svelte`
9. `Solution.svelte`
10. `Evidence.svelte`
11. `Lessons.svelte`

(11 slide components; the deck has 11 slides — the 8-beat arc with beat 2 expanded into 4 primer slides: 1 + 4 + 1 + 1 + 1 + 1 + 1 + 1 = 11.)

---

## Task 1: Scaffold the SvelteKit app

**Files:**
- Create: `dashboard/package.json`
- Create: `dashboard/.npmrc`
- Create: `dashboard/svelte.config.js`
- Create: `dashboard/vite.config.ts`
- Create: `dashboard/tsconfig.json`
- Create: `dashboard/src/app.html`
- Create: `dashboard/src/app.css`
- Create: `dashboard/src/routes/+layout.ts`
- Create: `dashboard/src/routes/+page.svelte` (temporary placeholder)
- Modify: `.gitignore` (root)

- [ ] **Step 1: Create `dashboard/package.json`**

```json
{
  "name": "sglang-pitfalls-dashboard",
  "version": "0.0.1",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite dev",
    "build": "vite build",
    "preview": "vite preview",
    "check": "svelte-kit sync && svelte-check --tsconfig ./tsconfig.json",
    "test": "vitest run"
  },
  "devDependencies": {
    "@sveltejs/adapter-static": "^3.0.6",
    "@sveltejs/kit": "^2.8.0",
    "@sveltejs/vite-plugin-svelte": "^4.0.0",
    "svelte": "^5.1.0",
    "svelte-check": "^4.0.0",
    "typescript": "^5.6.0",
    "vite": "^5.4.0",
    "vitest": "^2.1.0"
  }
}
```

- [ ] **Step 2: Create `dashboard/.npmrc`**

```
engine-strict=false
```

- [ ] **Step 3: Create `dashboard/svelte.config.js`**

```js
import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter({ fallback: 'index.html' }),
    prerender: { entries: ['*'] }
  }
};

export default config;
```

- [ ] **Step 4: Create `dashboard/vite.config.ts`**

```ts
import { sveltekit } from '@sveltejs/vite-plugin-svelte';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit()],
  test: {
    include: ['tests/**/*.test.ts'],
    environment: 'node'
  }
});
```

- [ ] **Step 5: Create `dashboard/tsconfig.json`**

```json
{
  "extends": "./.svelte-kit/tsconfig.json",
  "compilerOptions": {
    "allowJs": true,
    "checkJs": true,
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "skipLibCheck": true,
    "sourceMap": true,
    "strict": true,
    "moduleResolution": "bundler"
  }
}
```

- [ ] **Step 6: Create `dashboard/src/app.html`**

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%sveltekit.assets%/favicon.png" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    %sveltekit.head%
  </head>
  <body data-sveltekit-preload-data="hover">
    <div style="display: contents">%sveltekit.body%</div>
  </body>
</html>
```

- [ ] **Step 7: Create `dashboard/src/app.css` (theme tokens)**

```css
:root {
  --bg: #0c0d10;
  --bg-elev: #14161b;
  --ink: #e8e6df;
  --ink-dim: #9a978d;
  --accent: #e0a85e;        /* noir amber */
  --fail: #e5564b;
  --warn: #d9a441;
  --pass: #5fb87a;
  --mono: ui-monospace, "SF Mono", "JetBrains Mono", Menlo, monospace;
  --sans: "Inter", system-ui, -apple-system, sans-serif;
  --line: #23262e;
}

* { box-sizing: border-box; }

html, body {
  margin: 0;
  height: 100%;
  background: var(--bg);
  color: var(--ink);
  font-family: var(--sans);
  -webkit-font-smoothing: antialiased;
}

code, pre, .mono { font-family: var(--mono); }
```

- [ ] **Step 8: Create `dashboard/src/routes/+layout.ts`**

```ts
export const prerender = true;
export const ssr = false;
```

- [ ] **Step 9: Create temporary `dashboard/src/routes/+page.svelte`**

```svelte
<h1>SGLang pitfalls deck — scaffold OK</h1>
```

- [ ] **Step 10: Add `dashboard/` ignores to root `.gitignore`**

Append these lines to `/Users/andreinemilentsau/Projects/sglang-gemma4-triton-fallback/.gitignore`:

```
# Dashboard (SvelteKit) build/deps
dashboard/node_modules/
dashboard/.svelte-kit/
dashboard/build/
```

- [ ] **Step 11: Install deps and verify dev build works**

Run:
```bash
cd dashboard && npm install && npm run build
```
Expected: install completes; `npm run build` finishes with "✓ built" and writes `dashboard/build/index.html`. If `adapter-static` complains about prerendering, confirm `+layout.ts` exists with `prerender = true`.

- [ ] **Step 12: Commit**

```bash
cd /Users/andreinemilentsau/Projects/sglang-gemma4-triton-fallback
git add dashboard/package.json dashboard/.npmrc dashboard/svelte.config.js dashboard/vite.config.ts dashboard/tsconfig.json dashboard/src .gitignore
git commit -m "chore: scaffold SvelteKit dashboard app"
```

---

## Task 2: Baked-in run data module

**Files:**
- Create: `dashboard/src/lib/data/runResults.ts`
- Test: `dashboard/tests/data.test.ts`

- [ ] **Step 1: Write the failing test**

```ts
// dashboard/tests/data.test.ts
import { describe, it, expect } from 'vitest';
import { runResults, environment } from '../src/lib/data/runResults';

describe('runResults', () => {
  it('has base and merged runs with the recorded throughput', () => {
    expect(runResults.base.reqPerSec).toBe(5.01);
    expect(runResults.merged.reqPerSec).toBe(6.01);
  });

  it('records p50/p95/p99 latency for both runs', () => {
    expect(runResults.base.latency).toEqual({ p50: 1.55, p95: 1.87, p99: 1.98 });
    expect(runResults.merged.latency).toEqual({ p50: 1.27, p95: 1.74, p99: 1.85 });
  });

  it('records 200/200 valid JSON for both runs', () => {
    expect(runResults.base.validJson).toEqual({ valid: 200, total: 200 });
    expect(runResults.merged.validJson).toEqual({ valid: 200, total: 200 });
  });

  it('names the test environment', () => {
    expect(environment.gpu).toContain('A6000');
    expect(environment.sglang).toBe('0.5.12');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd dashboard && npx vitest run tests/data.test.ts`
Expected: FAIL — cannot resolve `../src/lib/data/runResults`.

- [ ] **Step 3: Write `dashboard/src/lib/data/runResults.ts`**

```ts
export interface Latency {
  p50: number;
  p95: number;
  p99: number;
}

export interface RunResult {
  label: string;
  totalSeconds: number;
  reqPerSec: number;
  latency: Latency;
  completionTokPerSec: number;
  validJson: { valid: number; total: number };
  exactMatch: { matched: number; total: number };
}

export const runResults: { base: RunResult; merged: RunResult } = {
  base: {
    label: 'Base Gemma 4 E2B',
    totalSeconds: 39.9,
    reqPerSec: 5.01,
    latency: { p50: 1.55, p95: 1.87, p99: 1.98 },
    completionTokPerSec: 216.54,
    validJson: { valid: 200, total: 200 },
    exactMatch: { matched: 0, total: 200 }
  },
  merged: {
    label: 'Merged + Triton',
    totalSeconds: 33.26,
    reqPerSec: 6.01,
    latency: { p50: 1.27, p95: 1.74, p99: 1.85 },
    completionTokPerSec: 194.18,
    validJson: { valid: 200, total: 200 },
    exactMatch: { matched: 0, total: 200 }
  }
};

export const environment = {
  gpu: 'NVIDIA RTX A6000 (sm_86, 49140 MiB)',
  sglang: '0.5.12',
  torch: '2.11.0+cu130',
  flashinfer: '0.6.11.post1',
  runDate: '2026-05-20'
};
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd dashboard && npx vitest run tests/data.test.ts`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add dashboard/src/lib/data/runResults.ts dashboard/tests/data.test.ts
git commit -m "feat: add baked-in run-results data module"
```

---

## Task 3: Evidence strings module

**Files:**
- Create: `dashboard/src/lib/data/evidence.ts`
- Test: `dashboard/tests/data.test.ts` (extend)

- [ ] **Step 1: Add failing tests to `dashboard/tests/data.test.ts`**

Append:
```ts
import { evidence } from '../src/lib/data/evidence';

describe('evidence', () => {
  it('contains the native LoRA RuntimeError with the lora_A key', () => {
    expect(evidence.loraError).toContain('Failed to load LoRA adapter');
    expect(evidence.loraError).toContain('lora_A.weight');
  });

  it('contains the FlashInfer bidirectional-attention warning', () => {
    expect(evidence.flashinferWarning).toContain('TritonAttnBackend');
  });

  it('contains the FlashInfer invalid-configuration error', () => {
    expect(evidence.flashinferError).toContain('Invalid configuration');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd dashboard && npx vitest run tests/data.test.ts`
Expected: FAIL — cannot resolve `../src/lib/data/evidence`.

- [ ] **Step 3: Write `dashboard/src/lib/data/evidence.ts`**

```ts
export const evidence = {
  loraError: `RuntimeError: Failed to load LoRA adapter ticket-triage:
'base_model.model.model.language_model.layers.15.self_attn.v_proj.lora_A.weight'`,

  flashinferWarning: `Bidirectional attention for image tokens requires TritonAttnBackend.
Falling back to causal attention, which may degrade image quality.`,

  flashinferError: `FlashInfer Internal Error: Invalid configuration :
NUM_MMA_Q=1 NUM_MMA_D_QK=32 NUM_MMA_D_VO=32 NUM_MMA_KV=1
NUM_WARPS_Q=4 NUM_WARPS_KV=1`,

  // The PEFT-generated key shape that SGLang's loader could not place.
  adapterKeyShape: `base_model.model.model.language_model.layers.<N>.self_attn.{q,k,v,o}_proj.lora_{A,B}.weight`,

  // The client-side symptom of crime #2.
  clientDisconnect: `http.client.RemoteDisconnected: Remote end closed connection without response`
};
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd dashboard && npx vitest run tests/data.test.ts`
Expected: PASS (7 tests total).

- [ ] **Step 5: Commit**

```bash
git add dashboard/src/lib/data/evidence.ts dashboard/tests/data.test.ts
git commit -m "feat: add real SGLang evidence strings module"
```

---

## Task 4: Deck store with slide registry

**Files:**
- Create: `dashboard/src/lib/stores/deck.ts`
- Test: `dashboard/tests/deck.test.ts`

- [ ] **Step 1: Write the failing test**

```ts
// dashboard/tests/deck.test.ts
import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { deck, slides } from '../src/lib/stores/deck';

beforeEach(() => deck.goto(0));

describe('deck store', () => {
  it('exposes the ordered slide registry', () => {
    expect(slides.length).toBe(11);
    expect(slides[0].id).toBe('cold-open');
    expect(slides[slides.length - 1].id).toBe('lessons');
  });

  it('starts at slide 0 with overview closed', () => {
    expect(get(deck).index).toBe(0);
    expect(get(deck).overview).toBe(false);
  });

  it('advances and goes back', () => {
    deck.next();
    expect(get(deck).index).toBe(1);
    deck.prev();
    expect(get(deck).index).toBe(0);
  });

  it('clamps at the first slide (prev is a no-op)', () => {
    deck.prev();
    expect(get(deck).index).toBe(0);
  });

  it('clamps at the last slide (next is a no-op)', () => {
    deck.goto(slides.length - 1);
    deck.next();
    expect(get(deck).index).toBe(slides.length - 1);
  });

  it('goto clamps out-of-range values', () => {
    deck.goto(999);
    expect(get(deck).index).toBe(slides.length - 1);
    deck.goto(-5);
    expect(get(deck).index).toBe(0);
  });

  it('toggles overview', () => {
    deck.toggleOverview();
    expect(get(deck).overview).toBe(true);
    deck.toggleOverview();
    expect(get(deck).overview).toBe(false);
  });

  it('goto closes the overview', () => {
    deck.toggleOverview();
    deck.goto(3);
    expect(get(deck).overview).toBe(false);
    expect(get(deck).index).toBe(3);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd dashboard && npx vitest run tests/deck.test.ts`
Expected: FAIL — cannot resolve `../src/lib/stores/deck`.

- [ ] **Step 3: Write `dashboard/src/lib/stores/deck.ts`**

```ts
import { writable } from 'svelte/store';

export interface SlideMeta {
  id: string;
  title: string;     // short label for the overview grid + progress rail
  section: 'open' | 'primer' | 'mission' | 'crime' | 'fix' | 'data' | 'close';
}

export const slides: SlideMeta[] = [
  { id: 'cold-open',       title: 'Cold open',            section: 'open' },
  { id: 'primer-server',   title: 'Inference server',     section: 'primer' },
  { id: 'primer-sglang',   title: 'What is SGLang',       section: 'primer' },
  { id: 'primer-lora',     title: 'LoRA adapters',        section: 'primer' },
  { id: 'primer-backends', title: 'Attention backends',   section: 'primer' },
  { id: 'mission',         title: 'The mission',          section: 'mission' },
  { id: 'crime1',          title: 'Crime #1: LoRA load',  section: 'crime' },
  { id: 'crime2',          title: 'Crime #2: ready lie',  section: 'crime' },
  { id: 'solution',        title: 'The solution',         section: 'fix' },
  { id: 'evidence',        title: 'Evidence room',        section: 'data' },
  { id: 'lessons',         title: 'Lessons',              section: 'close' }
];

interface DeckState {
  index: number;
  overview: boolean;
}

const clamp = (n: number) => Math.max(0, Math.min(slides.length - 1, n));

function createDeck() {
  const { subscribe, update, set } = writable<DeckState>({ index: 0, overview: false });
  return {
    subscribe,
    next: () => update((s) => ({ ...s, index: clamp(s.index + 1) })),
    prev: () => update((s) => ({ ...s, index: clamp(s.index - 1) })),
    goto: (i: number) => set({ index: clamp(i), overview: false }),
    toggleOverview: () => update((s) => ({ ...s, overview: !s.overview }))
  };
}

export const deck = createDeck();
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd dashboard && npx vitest run tests/deck.test.ts`
Expected: PASS (8 tests).

- [ ] **Step 5: Commit**

```bash
git add dashboard/src/lib/stores/deck.ts dashboard/tests/deck.test.ts
git commit -m "feat: add deck store with slide registry and clamped navigation"
```

---

## Task 5: Shared presentational components (EvidenceCard, PathBadge)

**Files:**
- Create: `dashboard/src/lib/components/EvidenceCard.svelte`
- Create: `dashboard/src/lib/components/PathBadge.svelte`

> Invoke the `frontend-design` skill before styling these — they set the visual vocabulary (the "evidence" log frame and the status badge) reused across slides.

- [ ] **Step 1: Create `dashboard/src/lib/components/EvidenceCard.svelte`**

```svelte
<script lang="ts">
  // A framed monospace block for showing real logs/errors as "evidence".
  // `label` is the little caption (e.g. "server.log"); `text` is the body.
  // `tone` colors the frame: 'fail' | 'warn' | 'neutral'.
  let { label = 'evidence', text = '', tone = 'neutral' }:
    { label?: string; text?: string; tone?: 'fail' | 'warn' | 'neutral' } = $props();

  const border = $derived(
    tone === 'fail' ? 'var(--fail)' : tone === 'warn' ? 'var(--warn)' : 'var(--line)'
  );
</script>

<figure class="evidence" style="--frame:{border}">
  <figcaption>{label}</figcaption>
  <pre class="mono">{text}</pre>
</figure>

<style>
  .evidence {
    margin: 0;
    border: 1px solid var(--frame);
    border-radius: 8px;
    background: var(--bg-elev);
    overflow: hidden;
  }
  figcaption {
    font-family: var(--mono);
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--ink-dim);
    padding: 0.4rem 0.8rem;
    border-bottom: 1px solid var(--line);
  }
  pre {
    margin: 0;
    padding: 1rem;
    font-size: 0.95rem;
    line-height: 1.5;
    color: var(--ink);
    white-space: pre-wrap;
    word-break: break-word;
  }
</style>
```

- [ ] **Step 2: Create `dashboard/src/lib/components/PathBadge.svelte`**

```svelte
<script lang="ts">
  // Status badge for the three serving paths.
  let { status = 'pass', label = '' }:
    { status?: 'fail' | 'warn' | 'pass'; label?: string } = $props();

  const glyph = $derived(status === 'fail' ? '✕' : status === 'warn' ? '!' : '✓');
  const color = $derived(
    status === 'fail' ? 'var(--fail)' : status === 'warn' ? 'var(--warn)' : 'var(--pass)'
  );
</script>

<span class="badge" style="--c:{color}">
  <span class="glyph">{glyph}</span>{label}
</span>

<style>
  .badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-family: var(--mono);
    font-size: 0.95rem;
    color: var(--c);
    border: 1px solid var(--c);
    border-radius: 999px;
    padding: 0.3rem 0.9rem;
  }
  .glyph { font-weight: 700; }
</style>
```

- [ ] **Step 3: Type-check**

Run: `cd dashboard && npm run check`
Expected: 0 errors (warnings about unused CSS are acceptable).

- [ ] **Step 4: Commit**

```bash
git add dashboard/src/lib/components/EvidenceCard.svelte dashboard/src/lib/components/PathBadge.svelte
git commit -m "feat: add EvidenceCard and PathBadge shared components"
```

---

## Task 6: Chart components (BarChart, LatencyChart)

**Files:**
- Create: `dashboard/src/lib/components/charts/BarChart.svelte`
- Create: `dashboard/src/lib/components/charts/LatencyChart.svelte`

> Invoke `frontend-design` before styling; charts must animate on mount and match the theme.

- [ ] **Step 1: Create `dashboard/src/lib/components/charts/BarChart.svelte`**

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  // Simple vertical bar chart. `data` is an array of {label, value, color?}.
  let { data = [], unit = '', max = 0 }:
    { data?: { label: string; value: number; color?: string }[]; unit?: string; max?: number } = $props();

  let mounted = $state(false);
  onMount(() => { mounted = true; });

  const top = $derived(max || Math.max(1, ...data.map((d) => d.value)) * 1.15);
</script>

<div class="bars">
  {#each data as d}
    <div class="col">
      <div class="track">
        <div
          class="bar"
          style="height:{mounted ? (d.value / top) * 100 : 0}%; background:{d.color ?? 'var(--accent)'}"
        ></div>
      </div>
      <div class="val mono">{d.value}{unit}</div>
      <div class="lbl">{d.label}</div>
    </div>
  {/each}
</div>

<style>
  .bars { display: flex; gap: 2rem; align-items: flex-end; height: 320px; }
  .col { display: flex; flex-direction: column; align-items: center; flex: 1; height: 100%; }
  .track { flex: 1; width: 64px; display: flex; align-items: flex-end; }
  .bar { width: 100%; border-radius: 6px 6px 0 0; transition: height 900ms cubic-bezier(.2,.7,.2,1); }
  .val { margin-top: 0.6rem; color: var(--ink); font-size: 1.1rem; }
  .lbl { color: var(--ink-dim); font-size: 0.9rem; margin-top: 0.25rem; text-align: center; }
</style>
```

- [ ] **Step 2: Create `dashboard/src/lib/components/charts/LatencyChart.svelte`**

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  // Grouped bars: for each percentile (p50/p95/p99), one bar per series.
  let { series = [] }:
    { series?: { name: string; color: string; latency: { p50: number; p95: number; p99: number } }[] } = $props();

  let mounted = $state(false);
  onMount(() => { mounted = true; });

  const percentiles = ['p50', 'p95', 'p99'] as const;
  const top = $derived(
    Math.max(1, ...series.flatMap((s) => [s.latency.p50, s.latency.p95, s.latency.p99])) * 1.2
  );
</script>

<div class="groups">
  {#each percentiles as p}
    <div class="group">
      <div class="bars">
        {#each series as s}
          <div class="track">
            <div
              class="bar"
              style="height:{mounted ? (s.latency[p] / top) * 100 : 0}%; background:{s.color}"
              title="{s.name} {p}: {s.latency[p]}s"
            ></div>
          </div>
        {/each}
      </div>
      <div class="plabel mono">{p}</div>
    </div>
  {/each}
</div>

<div class="legend">
  {#each series as s}
    <span class="key"><span class="dot" style="background:{s.color}"></span>{s.name}</span>
  {/each}
</div>

<style>
  .groups { display: flex; gap: 2.5rem; align-items: flex-end; height: 280px; }
  .group { flex: 1; display: flex; flex-direction: column; align-items: center; height: 100%; }
  .bars { flex: 1; display: flex; gap: 0.6rem; align-items: flex-end; }
  .track { display: flex; align-items: flex-end; height: 100%; }
  .bar { width: 36px; border-radius: 5px 5px 0 0; transition: height 900ms cubic-bezier(.2,.7,.2,1); }
  .plabel { margin-top: 0.6rem; color: var(--ink-dim); }
  .legend { display: flex; gap: 1.5rem; margin-top: 1.2rem; justify-content: center; }
  .key { display: inline-flex; align-items: center; gap: 0.5rem; color: var(--ink-dim); font-size: 0.9rem; }
  .dot { width: 12px; height: 12px; border-radius: 3px; display: inline-block; }
</style>
```

- [ ] **Step 3: Type-check**

Run: `cd dashboard && npm run check`
Expected: 0 errors.

- [ ] **Step 4: Commit**

```bash
git add dashboard/src/lib/components/charts
git commit -m "feat: add BarChart and LatencyChart inline-SVG-style chart components"
```

---

## Task 7: Deck shell + page wiring

**Files:**
- Create: `dashboard/src/lib/components/Deck.svelte`
- Modify: `dashboard/src/routes/+page.svelte`
- Create (placeholders for all 11 slides so imports resolve): `dashboard/src/lib/components/slides/*.svelte`

> Invoke `frontend-design` before styling the shell (progress rail, overview grid, transitions).

- [ ] **Step 1: Create placeholder slide components so the registry resolves**

Create each of these 11 files with a minimal body (they will be filled in later tasks). Example for `ColdOpen.svelte`; create the analogous file for every slide id:

```svelte
<!-- dashboard/src/lib/components/slides/ColdOpen.svelte -->
<section class="slide"><h1>Cold open</h1></section>
<style>.slide{height:100%;display:grid;place-content:center;padding:6vw;}</style>
```

Files to create (same placeholder pattern, heading = the slide title):
`ColdOpen.svelte`, `PrimerServer.svelte`, `PrimerSglang.svelte`, `PrimerLora.svelte`, `PrimerBackends.svelte`, `Mission.svelte`, `Crime1.svelte`, `Crime2.svelte`, `Solution.svelte`, `Evidence.svelte`, `Lessons.svelte`.

- [ ] **Step 2: Create `dashboard/src/lib/components/Deck.svelte`**

```svelte
<script lang="ts">
  import { fade } from 'svelte/transition';
  import { deck, slides } from '$lib/stores/deck';

  import ColdOpen from './slides/ColdOpen.svelte';
  import PrimerServer from './slides/PrimerServer.svelte';
  import PrimerSglang from './slides/PrimerSglang.svelte';
  import PrimerLora from './slides/PrimerLora.svelte';
  import PrimerBackends from './slides/PrimerBackends.svelte';
  import Mission from './slides/Mission.svelte';
  import Crime1 from './slides/Crime1.svelte';
  import Crime2 from './slides/Crime2.svelte';
  import Solution from './slides/Solution.svelte';
  import Evidence from './slides/Evidence.svelte';
  import Lessons from './slides/Lessons.svelte';

  const components: Record<string, any> = {
    'cold-open': ColdOpen,
    'primer-server': PrimerServer,
    'primer-sglang': PrimerSglang,
    'primer-lora': PrimerLora,
    'primer-backends': PrimerBackends,
    'mission': Mission,
    'crime1': Crime1,
    'crime2': Crime2,
    'solution': Solution,
    'evidence': Evidence,
    'lessons': Lessons
  };

  const Current = $derived(components[slides[$deck.index].id]);
</script>

<div class="stage">
  {#if $deck.overview}
    <div class="overview">
      {#each slides as s, i}
        <button class="thumb" class:active={i === $deck.index} onclick={() => deck.goto(i)}>
          <span class="num mono">{String(i + 1).padStart(2, '0')}</span>
          <span class="ttl">{s.title}</span>
        </button>
      {/each}
    </div>
  {:else}
    {#key $deck.index}
      <div class="slide-wrap" in:fade={{ duration: 250 }}>
        <Current />
      </div>
    {/key}
  {/if}

  <div class="rail">
    {#each slides as s, i}
      <button
        class="dot"
        class:on={i <= $deck.index}
        aria-label={s.title}
        onclick={() => deck.goto(i)}
      ></button>
    {/each}
    <span class="counter mono">{$deck.index + 1} / {slides.length}</span>
  </div>
</div>

<style>
  .stage { position: fixed; inset: 0; }
  .slide-wrap { position: absolute; inset: 0; }
  .rail {
    position: fixed; left: 0; right: 0; bottom: 0;
    display: flex; gap: 0.5rem; align-items: center;
    padding: 0.8rem 1.2rem; background: linear-gradient(transparent, rgba(0,0,0,.4));
  }
  .dot { width: 26px; height: 4px; border: 0; border-radius: 2px; background: var(--line); cursor: pointer; padding: 0; }
  .dot.on { background: var(--accent); }
  .counter { margin-left: auto; color: var(--ink-dim); font-size: 0.85rem; }
  .overview {
    position: absolute; inset: 0; padding: 5vh 5vw 8vh;
    display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 1rem; align-content: start; overflow: auto;
  }
  .thumb {
    text-align: left; background: var(--bg-elev); border: 1px solid var(--line);
    border-radius: 10px; padding: 1.1rem; color: var(--ink); cursor: pointer;
    display: flex; flex-direction: column; gap: 0.5rem;
  }
  .thumb.active { border-color: var(--accent); }
  .num { color: var(--accent); font-size: 0.8rem; }
  .ttl { font-size: 1.05rem; }
</style>
```

- [ ] **Step 3: Wire `dashboard/src/routes/+page.svelte`**

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import Deck from '$lib/components/Deck.svelte';
  import { deck } from '$lib/stores/deck';

  function onKey(e: KeyboardEvent) {
    if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {
      e.preventDefault(); deck.next();
    } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
      e.preventDefault(); deck.prev();
    } else if (e.key === 'o' || e.key === 'O') {
      deck.toggleOverview();
    } else if (e.key === 'Escape') {
      deck.toggleOverview();
    }
  }

  onMount(() => {
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  });
</script>

<svelte:head><title>The Gemma 4 Serving Mystery</title></svelte:head>

<main onclick={() => deck.next()} oncontextmenu={(e) => { e.preventDefault(); deck.prev(); }}>
  <Deck />
</main>

<style>
  main { height: 100%; cursor: pointer; }
</style>
```

Note: left-click advances, right-click goes back. Buttons in the rail/overview call `deck.goto` and use `stopPropagation` is unnecessary because `goto` is the desired result either way; if a click on a rail dot also triggers `main`'s onclick, add `onclick={(e)=>{e.stopPropagation();deck.goto(i)}}` in `Deck.svelte` rail/thumb handlers.

- [ ] **Step 4: Apply stopPropagation to rail/overview buttons in `Deck.svelte`**

Update the two handlers in `Deck.svelte`:
```svelte
<button class="thumb" ... onclick={(e) => { e.stopPropagation(); deck.goto(i); }}>
```
```svelte
<button class="dot" ... onclick={(e) => { e.stopPropagation(); deck.goto(i); }}></button>
```

- [ ] **Step 5: Verify dev server renders and navigation works**

Run: `cd dashboard && npm run build`
Expected: build succeeds. Then manually `npm run dev`, open the URL, press `→`/`←`/`o`/`Esc`, confirm slides change and overview opens/closes. (Full automated smoke test is Task 15.)

- [ ] **Step 6: Commit**

```bash
git add dashboard/src/lib/components/Deck.svelte dashboard/src/routes/+page.svelte dashboard/src/lib/components/slides
git commit -m "feat: add deck shell, keyboard/click navigation, and slide placeholders"
```

---

## Tasks 8–14: Author the slides

Each slide task: invoke `frontend-design` for visual polish, then replace the placeholder with the real content specified below. After each, run `cd dashboard && npm run check` (expect 0 errors) and `npm run build` (expect success), then commit with `git add dashboard/src/lib/components/slides/<File>.svelte && git commit -m "feat: author <slide> slide"`.

All copy below is the actual content — not a summary to paraphrase. Slides may add tasteful supporting microcopy but must include the specified headings, claims, and (where noted) the exact data/evidence imports.

### Task 8: Cold open + the four primer slides

- [ ] **`ColdOpen.svelte`** — Title card.
  - Eyebrow (mono, amber): `CASE FILE · SGLANG 0.5.12 · GEMMA 4 E2B`
  - Headline: **"We just wanted to serve a fine-tuned model."**
  - Subhead: "It took three tries to get one request answered. Here's the investigation."
  - Footer hint (mono, dim): `→ / space to advance · o for overview`

- [ ] **`PrimerServer.svelte`** — "The inference server."
  - Heading: **"First, the cast: an inference server"**
  - Body: "You have model weights. An app wants answers over HTTP. You don't call `model(...)` in production — you put an *inference server* in between. It batches requests, manages GPU memory (the KV cache), and exposes an OpenAI-style `/v1/chat/completions` API."
  - Include a simple 3-box diagram: `App → [Inference server] → GPU + weights`.

- [ ] **`PrimerSglang.svelte`** — "What SGLang is."
  - Heading: **"SGLang is one such server"**
  - Body: "SGLang is a popular open-source inference server — think vLLM's cousin. It's fast, supports many model families, and is what we're serving Gemma 4 on. Version here: **0.5.12** on a CUDA 13 stack."
  - Callout: "If you've used vLLM or TGI, SGLang plays the same role."

- [ ] **`PrimerLora.svelte`** — "LoRA adapters."
  - Heading: **"LoRA: fine-tuning as a small patch"**
  - Body: "Instead of retraining all of a model's weights, LoRA trains tiny low-rank matrices (`lora_A`, `lora_B`) bolted onto specific layers. The result is a small *adapter* file. Two ways to serve it:"
  - Two labeled options:
    - **Native LoRA** — hand the adapter to the server, keep base + adapter separate at runtime.
    - **Merge then serve** — fold the adapter into the base weights first, serve one plain model.
  - Foreshadow (dim): "Remember these two options. One of them is a trap."

- [ ] **`PrimerBackends.svelte`** — "Attention backends."
  - Heading: **"Attention backends: swappable engines"**
  - Body: "The heaviest math in a transformer is *attention*. SGLang lets you pick the kernel that runs it — **Triton** or **FlashInfer** — with one flag: `--attention-backend`. They should be interchangeable."
  - Key idea card (amber border): "But a model *feature* — like Gemma 4's bidirectional attention over image tokens — may only be implemented on **one** backend. Hold that thought."

### Task 9: Mission slide

- [ ] **`Mission.svelte`** — "The mission."
  - Heading: **"The mission: serve a fine-tuned Gemma 4"**
  - Body: "We trained a LoRA adapter on Gemma 4 E2B for **ticket triage** — read a support ticket, emit JSON (`route`, `severity`, `macro`, `product_code`). Goal: serve it on SGLang and answer requests."
  - Intended happy path as a 3-step flow: `Train LoRA adapter → Load in SGLang (--lora-paths) → Call /v1/chat/completions`.
  - Footer (dim): "That's the plan. The plan does not survive contact with the loader."

### Task 10: Crime #1

- [ ] **`Crime1.svelte`** — uses `evidence.loraError` and `evidence.adapterKeyShape`.
  - Section tag (mono, red): `CRIME #1`
  - Heading: **"The adapter that wouldn't load"**
  - Symptom line: "We pass `--lora-paths ticket-triage=…`. The server dies **before** it ever reports ready."
  - `<EvidenceCard label="sglang server (startup)" tone="fail" text={evidence.loraError} />`
  - Investigation (2–3 bullets):
    - "PEFT wrote keys shaped like:" then `<EvidenceCard label="adapter checkpoint key" tone="neutral" text={evidence.adapterKeyShape} />`
    - "Note the triple nesting: `model.model.language_model`. Gemma 4's language tower sits inside a multimodal wrapper."
    - "SGLang 0.5.12's LoRA loader can't place `lora_A` at the key shape it expects for this structure. (We'd already been forced off regex / `all-linear` `target_modules` by an SGLang constraint, onto explicit module names — and even those don't load.)"
  - Verdict (amber): "Native LoRA on Gemma 4 E2B: dead on arrival."

### Task 11: Crime #2

- [ ] **`Crime2.svelte`** — uses `evidence.flashinferWarning`, `evidence.flashinferError`, `evidence.clientDisconnect`.
  - Section tag (mono, red): `CRIME #2`
  - Heading: **"The server that lied about being ready"**
  - Setup: "So we merged the adapter into the base weights (more on that next) and served the merged model with the default-ish **FlashInfer** backend. This time the server **reaches readiness** — `/model_info` says it's up."
  - Twist: "Then the very first real `/v1/chat/completions` request kills it."
  - Evidence sequence (in order):
    - `<EvidenceCard label="startup warning (load-bearing!)" tone="warn" text={evidence.flashinferWarning} />`
    - `<EvidenceCard label="first request → crash" tone="fail" text={evidence.flashinferError} />`
    - `<EvidenceCard label="what the client sees" tone="fail" text={evidence.clientDisconnect} />`
  - Root cause (amber card): "Gemma 4's bidirectional image attention is implemented **only** for Triton. FlashInfer falls back to causal attention, then crashes in paged prefill. The lesson writes itself: **readiness ≠ working.**"

### Task 12: Solution

- [ ] **`Solution.svelte`** — uses `PathBadge`.
  - Heading: **"The recipe that works"**
  - Two-line fix, shown as commands (mono / EvidenceCard with tone neutral):
    - `# 1. Merge the adapter outside SGLang (transformers)`
    - `# 2. Serve the merged model, pin Triton`
    - `sglang ... --attention-backend triton`
  - Three-path comparison panel using `PathBadge`:
    - `<PathBadge status="fail" label="Native LoRA — fails before readiness" />`
    - `<PathBadge status="warn" label="Merged + FlashInfer — ready, then crashes on first request" />`
    - `<PathBadge status="pass" label="Merged + Triton — passes smoke test + full scoring run" />`
  - Caption: "Two flags and one merge step stand between 'mysterious crash' and 'it just works.'"

### Task 13: Evidence room (charts)

- [ ] **`Evidence.svelte`** — imports `runResults`, `environment`, `BarChart`, `LatencyChart`.
  - Heading: **"The evidence room: it actually serves"**
  - Throughput `BarChart`:
    ```svelte
    <BarChart
      unit=" req/s"
      data={[
        { label: runResults.base.label, value: runResults.base.reqPerSec, color: 'var(--ink-dim)' },
        { label: runResults.merged.label, value: runResults.merged.reqPerSec, color: 'var(--accent)' }
      ]}
    />
    ```
  - Latency `LatencyChart`:
    ```svelte
    <LatencyChart
      series={[
        { name: runResults.base.label, color: 'var(--ink-dim)', latency: runResults.base.latency },
        { name: runResults.merged.label, color: 'var(--accent)', latency: runResults.merged.latency }
      ]}
    />
    ```
  - Stat line: "Both runs: **200/200 valid JSON.** Merged is faster: **6.01 vs 5.01 req/s**, p50 **1.27s vs 1.55s**."
  - Honesty caveat (dim): "Exact-match accuracy is 0/200 by design — this is a synthetic fixture with no real task-training signal. The point is *serving behavior*, not task scores."
  - Environment footnote (mono, dim): build from `environment`: `{environment.gpu} · SGLang {environment.sglang} · Torch {environment.torch} · FlashInfer {environment.flashinfer} · {environment.runDate}`.

### Task 14: Lessons

- [ ] **`Lessons.svelte`** — closing slide.
  - Heading: **"What this case teaches"**
  - Four takeaways (as cards):
    1. **Readiness ≠ working.** A server can pass health checks and still die on the first real request.
    2. **Backend support is per-feature.** "Triton vs FlashInfer" isn't just speed — model features like Gemma 4's image attention may exist on only one.
    3. **Adapter key conventions are fragile.** PEFT's key names and a server's loader expectations can silently disagree, especially for multimodal models with nested towers.
    4. **Merge-and-serve is the escape hatch.** When native LoRA fights you, merging outside the server + pinning the supported backend is the reliable path.
  - Footer link (mono): "Repro, scripts, and the two SGLang issue drafts: `docs/issues/native-lora-bug.md`, `docs/issues/flashinfer-bug.md`."

---

## Task 15: Playwright smoke test + final verification

**Files:** none created (uses the Playwright MCP tools available in this environment).

- [ ] **Step 1: Build and start a preview server**

Run:
```bash
cd dashboard && npm run build && npm run preview -- --port 4173 &
```
Expected: preview server serving `build/` at `http://localhost:4173`.

- [ ] **Step 2: Drive the deck with Playwright MCP**

Using the Playwright MCP browser tools:
1. `browser_navigate` to `http://localhost:4173`.
2. `browser_snapshot` — confirm the Cold open headline "We just wanted to serve a fine-tuned model." is present.
3. Press `ArrowRight` 10 times (`browser_press_key`), snapshotting periodically — confirm reaching the Lessons slide ("What this case teaches").
4. `browser_console_messages` — assert there are **no error-level** console messages across the run.
5. Press `o` — confirm the overview grid appears (11 thumbnails). Press `Escape` — confirm it closes.

Expected: all assertions hold; zero console errors.

- [ ] **Step 3: Run the full unit suite**

Run: `cd dashboard && npm run test`
Expected: all Vitest tests pass (data + deck suites).

- [ ] **Step 4: Type-check**

Run: `cd dashboard && npm run check`
Expected: 0 errors.

- [ ] **Step 5: Write `dashboard/README.md`**

```markdown
# The Gemma 4 Serving Mystery — presentation dashboard

A SvelteKit slide deck explaining the SGLang 0.5.12 Gemma 4 E2B serving pitfalls
documented in this repo, for an audience that knows LLMs but not SGLang.

## Run it

```bash
cd dashboard
npm install
npm run dev      # live, for editing
# or
npm run build && npm run preview   # static build, for presenting
```

## Present it

- `→` / `Space` — next slide
- `←` — previous slide
- left-click — next · right-click — previous
- `o` — overview grid (click a thumbnail to jump) · `Esc` — close overview

11 slides: cold open → 4-part concept primer → mission → two "crimes" → the fix →
charts from the 2026-05-20 run → lessons.
```

- [ ] **Step 6: Stop the preview server**

Run: `kill %1 2>/dev/null || true`

- [ ] **Step 7: Commit**

```bash
git add dashboard/README.md
git commit -m "docs: add dashboard README; verified build, tests, and smoke run"
```

---

## Self-Review (completed)

- **Spec coverage:** Tech/mechanics → Tasks 1, 4, 7. Data + charts → Tasks 2, 6, 13. Evidence strings → Task 3. Visual tone → frontend-design invoked per slide task. All 11 slides (8-beat arc with 4-part primer) → Tasks 8–14. Testing (store unit, data unit, Playwright smoke) → Tasks 2, 3, 4, 15. Out-of-scope items (no backend/auth/CMS) honored — no such tasks exist. ✓
- **Placeholder scan:** Slide tasks carry real copy and the actual error/log strings via the `evidence`/`runResults` modules; no "TBD"/"add appropriate X". The Task 7 slide placeholders are explicitly temporary and replaced in Tasks 8–14. ✓
- **Type consistency:** `deck.next/prev/goto/toggleOverview`, `slides[].id/title/section`, `runResults.base/merged`, `RunResult` fields (`reqPerSec`, `latency.p50/p95/p99`, `validJson`), `evidence.loraError/flashinferWarning/flashinferError/adapterKeyShape/clientDisconnect`, and component props (`EvidenceCard{label,text,tone}`, `PathBadge{status,label}`, `BarChart{data,unit,max}`, `LatencyChart{series}`) are used consistently across tasks. ✓
- **Slide count:** registry = 11; Deck `components` map = 11 keys; Playwright presses ArrowRight 10× to traverse 11 slides. Consistent. ✓
```
