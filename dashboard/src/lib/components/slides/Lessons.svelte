<script lang="ts">
  // What this case teaches — the calm close.
  const takeaways = [
    {
      lede: 'Readiness ≠ working.',
      body: 'A server can pass health checks and still die on the first real request.'
    },
    {
      lede: 'Backend support is per-feature.',
      body: '“Triton vs FlashInfer” isn’t just speed — model features like Gemma 4’s image attention may exist on only one.'
    },
    {
      lede: 'Adapter key conventions are fragile.',
      body: 'PEFT’s key names and a server’s loader expectations can silently disagree, especially for multimodal models with nested towers.'
    },
    {
      lede: 'Merge-and-serve is the escape hatch.',
      body: 'When native LoRA fights you, merging outside the server + pinning the supported backend is the reliable path.'
    }
  ];
</script>

<section class="slide">
  <header class="head">
    <p class="kicker mono">CASE CLOSED · DEBRIEF</p>
    <h2>What this case<br /><span class="amber">teaches</span></h2>
  </header>

  <ol class="cards" aria-label="Four takeaways">
    {#each takeaways as t, i}
      <li class="card">
        <span class="num mono">{(i + 1).toString().padStart(2, '0')}</span>
        <p class="lede">{t.lede}</p>
        <p class="body">{t.body}</p>
      </li>
    {/each}
  </ol>

  <p class="footer mono">
    Repro, scripts, and the two SGLang issue drafts:
    <span class="path">docs/issues/native-lora-bug.md</span>,
    <span class="path">docs/issues/flashinfer-bug.md</span>.
  </p>
</section>

<style>
  .slide {
    height: 100%;
    padding: 7vh 9vw;
    display: grid;
    align-content: center;
    gap: 2rem;
  }

  .kicker {
    color: var(--accent);
    letter-spacing: 0.28em;
    font-size: 0.8rem;
    margin: 0 0 0.9rem;
  }
  h2 {
    font-size: clamp(2.1rem, 4.6vw, 3.7rem);
    line-height: 1;
    letter-spacing: -0.02em;
    font-weight: 660;
    margin: 0;
  }
  .amber { color: var(--accent); font-style: italic; }

  .cards {
    list-style: none;
    margin: 0;
    padding: 0;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.2rem;
  }
  .card {
    position: relative;
    border: 1px solid var(--line);
    border-radius: 12px;
    background: var(--bg-elev);
    padding: 1.3rem 1.5rem 1.3rem 3.6rem;
    transition: border-color 0.25s;
  }
  .card:hover { border-color: var(--accent); }
  .num {
    position: absolute;
    left: 1.3rem;
    top: 1.3rem;
    color: var(--accent);
    font-size: 0.85rem;
    letter-spacing: 0.08em;
    opacity: 0.8;
  }
  .lede {
    margin: 0 0 0.4rem;
    font-size: clamp(1.05rem, 1.7vw, 1.4rem);
    font-weight: 660;
    letter-spacing: -0.01em;
    color: var(--ink);
  }
  .body {
    margin: 0;
    font-size: clamp(0.92rem, 1.3vw, 1.12rem);
    line-height: 1.45;
    color: var(--ink-dim);
  }

  .footer {
    margin: 0;
    color: var(--ink-dim);
    font-size: 0.8rem;
    letter-spacing: 0.04em;
    border-top: 1px solid var(--line);
    padding-top: 1.1rem;
  }
  .path {
    color: var(--accent);
    background: rgba(224, 168, 94, 0.08);
    padding: 0.05em 0.4em;
    border-radius: 4px;
  }

  @media (max-width: 880px) {
    .cards { grid-template-columns: 1fr; }
  }
</style>
