<script lang="ts">
  // Concept primer 2 — what SGLang is.
</script>

<section class="slide">
  <div class="grid">
    <div class="left">
      <p class="kicker mono">EXHIBIT B · THE TOOL</p>
      <h2>SGLang is <span class="amber">one such server</span></h2>

      <p class="body">
        SGLang is a popular open-source inference server &mdash; think vLLM&rsquo;s
        cousin. It&rsquo;s fast, supports many model families, and is what we&rsquo;re
        serving Gemma&nbsp;4 on.
      </p>

      <div class="version">
        <span class="vlabel mono">VERSION ON FILE</span>
        <span class="vval mono">SGLang <strong>0.5.12</strong></span>
        <span class="vsub mono">on a CUDA 13 stack</span>
      </div>
    </div>

    <aside class="callout">
      <span class="callout-tag mono">FAMILIAR FACE?</span>
      <p>
        If you&rsquo;ve used <code>vLLM</code> or <code>TGI</code>,
        SGLang plays the same role.
      </p>
    </aside>
  </div>
</section>

<style>
  .slide {
    height: 100%;
    padding: 9vh 9vw;
    display: grid;
    align-content: center;
  }

  .grid {
    display: grid;
    grid-template-columns: 1.55fr 1fr;
    gap: 4vw;
    align-items: center;
  }

  .kicker {
    color: var(--accent);
    letter-spacing: 0.28em;
    font-size: 0.8rem;
    margin: 0 0 0.9rem;
  }
  h2 {
    font-size: clamp(2.4rem, 5.5vw, 4.4rem);
    line-height: 1;
    letter-spacing: -0.02em;
    font-weight: 660;
    margin: 0 0 1.6rem;
  }
  .amber { color: var(--accent); font-style: italic; }

  .body {
    max-width: 46ch;
    font-size: clamp(1.05rem, 1.6vw, 1.45rem);
    line-height: 1.55;
    color: var(--ink-dim);
    margin: 0 0 2.2rem;
  }

  .version {
    display: inline-flex;
    flex-direction: column;
    gap: 0.4rem;
    border-left: 3px solid var(--accent);
    padding: 0.3rem 0 0.3rem 1.2rem;
  }
  .vlabel { font-size: 0.66rem; letter-spacing: 0.24em; color: var(--ink-dim); }
  .vval { font-size: clamp(1.3rem, 2.4vw, 2rem); color: var(--ink); }
  .vval strong { color: var(--accent); }
  .vsub { font-size: 0.82rem; color: var(--ink-dim); }

  .callout {
    border: 1px solid var(--line);
    border-radius: 14px;
    background: var(--bg-elev);
    padding: 1.8rem;
    position: relative;
    box-shadow: 0 24px 60px -30px rgba(0, 0, 0, 0.8);
  }
  .callout::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 14px;
    padding: 1px;
    background: linear-gradient(160deg, rgba(224, 168, 94, 0.4), transparent 55%);
    -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
    mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    pointer-events: none;
  }
  .callout-tag {
    display: block;
    color: var(--accent);
    font-size: 0.68rem;
    letter-spacing: 0.24em;
    margin-bottom: 0.9rem;
  }
  .callout p {
    margin: 0;
    font-size: clamp(1.15rem, 1.9vw, 1.6rem);
    line-height: 1.4;
    color: var(--ink);
  }
  code {
    color: var(--accent);
    background: rgba(224, 168, 94, 0.08);
    padding: 0.05em 0.4em;
    border-radius: 4px;
    font-size: 0.9em;
    font-family: var(--mono);
  }

  @media (max-width: 860px) {
    .grid { grid-template-columns: 1fr; gap: 2.4rem; }
  }
</style>
