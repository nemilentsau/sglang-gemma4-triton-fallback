<script lang="ts">
  // The recipe that works — the resolution.
  import PathBadge from '$lib/components/PathBadge.svelte';
</script>

<section class="slide">
  <header class="head">
    <p class="kicker mono">THE FIX · CASE CLOSED</p>
    <h2>The recipe that<br /><span class="amber">works</span></h2>
  </header>

  <div class="grid">
    <figure class="terminal">
      <figcaption class="mono"><span class="dot" aria-hidden="true"></span>the fix</figcaption>
      <pre class="mono"><span class="cmt"># 1. Merge the adapter outside SGLang (transformers)</span>
<span class="cmt"># 2. Serve the merged model, pin Triton</span>
<span class="prompt">sglang</span> ... <span class="flag">--attention-backend</span> <span class="val">triton</span></pre>
    </figure>

    <div class="paths" aria-label="Three serving paths compared">
      <span class="paths-tag mono">THREE PATHS · ONE SURVIVES</span>
      <PathBadge status="fail" label="Native LoRA — fails before readiness" />
      <span class="rail" aria-hidden="true"></span>
      <PathBadge status="warn" label="Merged + FlashInfer — ready, then crashes on first request" />
      <span class="rail" aria-hidden="true"></span>
      <PathBadge status="pass" label="Merged + Triton — passes smoke test + full scoring run" />
    </div>
  </div>

  <p class="caption">
    Two flags and one merge step stand between <em>&ldquo;mysterious crash&rdquo;</em> and
    <span class="amber">&ldquo;it just works.&rdquo;</span>
  </p>
</section>

<style>
  .slide {
    height: 100%;
    padding: 7vh 9vw;
    display: grid;
    align-content: center;
    gap: 2.2rem;
  }

  .kicker {
    color: var(--accent);
    letter-spacing: 0.28em;
    font-size: 0.8rem;
    margin: 0 0 0.9rem;
  }
  h2 {
    font-size: clamp(2.2rem, 5vw, 4rem);
    line-height: 1;
    letter-spacing: -0.02em;
    font-weight: 660;
    margin: 0;
  }
  .amber { color: var(--accent); font-style: italic; }

  .grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 3vw;
    align-items: center;
  }

  .terminal {
    margin: 0;
    border: 1px solid var(--line);
    border-radius: 10px;
    background: var(--bg-elev);
    overflow: hidden;
    box-shadow: 0 24px 60px -40px #000;
  }
  .terminal figcaption {
    display: flex;
    align-items: center;
    gap: 0.45rem;
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--ink-dim);
    padding: 0.5rem 0.9rem;
    border-bottom: 1px solid var(--line);
    background: rgba(0, 0, 0, 0.25);
  }
  .terminal .dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--pass);
    box-shadow: 0 0 5px var(--pass);
  }
  .terminal pre {
    margin: 0;
    padding: 1.3rem 1.2rem;
    font-size: clamp(0.85rem, 1.2vw, 1.05rem);
    line-height: 1.7;
    color: var(--ink);
    white-space: pre-wrap;
    word-break: break-word;
  }
  .cmt { color: var(--ink-dim); }
  .prompt { color: var(--ink); font-weight: 700; }
  .flag { color: var(--accent); }
  .val { color: var(--pass); font-weight: 600; }

  .paths {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 0;
  }
  .paths-tag {
    color: var(--ink-dim);
    font-size: 0.68rem;
    letter-spacing: 0.2em;
    margin-bottom: 1rem;
  }
  .rail {
    width: 1px;
    height: 1.1rem;
    margin: 0.45rem 0 0.45rem 1rem;
    background: var(--line);
  }

  .caption {
    margin: 0;
    font-size: clamp(1.05rem, 1.7vw, 1.5rem);
    line-height: 1.45;
    color: var(--ink-dim);
    max-width: 56ch;
  }
  .caption em { color: var(--ink); font-style: italic; }
  .caption .amber { font-style: italic; }

  @media (max-width: 880px) {
    .grid { grid-template-columns: 1fr; gap: 2rem; }
  }
</style>
