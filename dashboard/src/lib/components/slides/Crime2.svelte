<script lang="ts">
  // Crime #2 — the server that lied about being ready.
  import EvidenceCard from '$lib/components/EvidenceCard.svelte';
  import { evidence } from '$lib/data/evidence';
</script>

<section class="slide">
  <header class="head">
    <p class="kicker mono"><span class="rec" aria-hidden="true"></span>CRIME #2</p>
    <h2>The server that lied<br /><span class="fail">about being ready</span></h2>
    <p class="setup">
      So we merged the adapter into the base weights (more on that next) and served the
      merged model with the default-ish <strong>FlashInfer</strong> backend. This time the
      server <em>reaches readiness</em> &mdash; <code>/model_info</code> says it&rsquo;s up.
    </p>
    <p class="twist">
      Then the very first real <code>/v1/chat/completions</code> request kills it.
    </p>
  </header>

  <ol class="sequence" aria-label="Evidence sequence">
    <li>
      <span class="step mono">A</span>
      <EvidenceCard label="startup warning (load-bearing!)" tone="warn" text={evidence.flashinferWarning} />
    </li>
    <li class="arrow" aria-hidden="true">↓</li>
    <li>
      <span class="step mono">B</span>
      <EvidenceCard label="first request → crash" tone="fail" text={evidence.flashinferError} />
    </li>
    <li class="arrow" aria-hidden="true">↓</li>
    <li>
      <span class="step mono">C</span>
      <EvidenceCard label="what the client sees" tone="fail" text={evidence.clientDisconnect} />
    </li>
  </ol>

  <div class="rootcause">
    <span class="rc-tag mono">ROOT CAUSE</span>
    <p>
      Gemma&nbsp;4&rsquo;s bidirectional image attention is implemented <strong>only</strong>
      for Triton. FlashInfer falls back to causal attention, then crashes in paged prefill.
      The lesson writes itself: <em>readiness &ne; working.</em>
    </p>
  </div>
</section>

<style>
  .slide {
    height: 100%;
    padding: 6vh 8vw;
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-areas: 'head sequence' 'rootcause sequence';
    align-content: center;
    align-items: start;
    column-gap: 4vw;
    row-gap: 1.6rem;
  }
  .head { grid-area: head; }
  .sequence { grid-area: sequence; }
  .rootcause { grid-area: rootcause; }

  .kicker {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    color: var(--fail);
    letter-spacing: 0.28em;
    font-size: 0.8rem;
    margin: 0 0 0.8rem;
  }
  .rec {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--fail);
    box-shadow: 0 0 8px var(--fail);
  }
  h2 {
    font-size: clamp(1.9rem, 4vw, 3.3rem);
    line-height: 1;
    letter-spacing: -0.02em;
    font-weight: 660;
    margin: 0 0 1.1rem;
  }
  .fail { color: var(--fail); font-style: italic; }

  .setup, .twist {
    max-width: 52ch;
    font-size: clamp(0.98rem, 1.45vw, 1.25rem);
    line-height: 1.5;
    margin: 0;
  }
  .setup { color: var(--ink-dim); }
  .setup strong, .twist code { color: var(--ink); }
  .twist {
    margin-top: 1rem;
    color: var(--ink);
    font-weight: 600;
    border-left: 3px solid var(--fail);
    padding-left: 1rem;
  }
  .twist code { color: var(--fail); }

  code {
    color: var(--accent);
    background: rgba(224, 168, 94, 0.08);
    padding: 0.05em 0.4em;
    border-radius: 4px;
    font-size: 0.88em;
    font-family: var(--mono);
    white-space: nowrap;
  }

  .sequence {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  .sequence > li:not(.arrow) {
    position: relative;
    padding-left: 2.2rem;
  }
  .step {
    position: absolute;
    left: 0;
    top: 0;
    width: 1.5rem;
    height: 1.5rem;
    display: grid;
    place-content: center;
    color: var(--fail);
    border: 1px solid var(--fail);
    border-radius: 50%;
    font-size: 0.72rem;
    font-weight: 700;
  }
  .arrow {
    color: var(--ink-dim);
    font-size: 1.1rem;
    padding-left: 0.55rem;
    line-height: 1;
  }

  .rootcause {
    align-self: start;
    border: 1px solid var(--accent);
    border-radius: 14px;
    background: rgba(224, 168, 94, 0.05);
    padding: 1.3rem 1.6rem;
    box-shadow: 0 0 50px -28px var(--accent) inset;
    display: flex;
    flex-direction: column;
    gap: 0.7rem;
  }
  .rc-tag {
    color: var(--accent);
    font-size: 0.72rem;
    letter-spacing: 0.2em;
  }
  .rootcause p {
    margin: 0;
    font-size: clamp(1rem, 1.5vw, 1.3rem);
    line-height: 1.45;
    color: var(--ink);
  }
  .rootcause strong { color: var(--accent); }
  .rootcause em { color: var(--accent); font-style: italic; font-weight: 600; }

  @media (max-width: 920px) {
    .slide {
      grid-template-columns: 1fr;
      grid-template-areas: 'head' 'sequence' 'rootcause';
      row-gap: 1.6rem;
    }
    code { white-space: normal; }
  }
</style>
