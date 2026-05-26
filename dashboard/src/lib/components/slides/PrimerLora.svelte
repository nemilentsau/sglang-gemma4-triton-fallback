<script lang="ts">
  // Concept primer 3 — LoRA adapters and the two ways to serve them.
</script>

<section class="slide">
  <header class="head">
    <p class="kicker mono">EXHIBIT C · THE PATCH</p>
    <h2>LoRA: fine-tuning as a <span class="amber">small patch</span></h2>
  </header>

  <p class="body">
    Instead of retraining all of a model&rsquo;s weights, LoRA trains tiny low-rank
    matrices (<code>lora_A</code>, <code>lora_B</code>) bolted onto specific layers.
    The result is a small <em>adapter</em> file. Two ways to serve it:
  </p>

  <div class="options">
    <article class="option">
      <span class="opt-num mono">01</span>
      <h3>Native LoRA</h3>
      <p>Hand the adapter to the server, keep base + adapter separate at runtime.</p>
    </article>
    <article class="option">
      <span class="opt-num mono">02</span>
      <h3>Merge then serve</h3>
      <p>Fold the adapter into the base weights first, serve one plain model.</p>
    </article>
  </div>

  <p class="foreshadow mono">
    <span class="warn-dot" aria-hidden="true"></span>
    Remember these two options. One of them is a trap.
  </p>
</section>

<style>
  .slide {
    height: 100%;
    padding: 8vh 9vw;
    display: grid;
    align-content: center;
    gap: 1.9rem;
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

  .body {
    max-width: 64ch;
    font-size: clamp(1.05rem, 1.6vw, 1.4rem);
    line-height: 1.55;
    color: var(--ink-dim);
    margin: 0;
  }
  .body em { color: var(--ink); font-style: normal; border-bottom: 1px dotted var(--ink-dim); }
  code {
    color: var(--accent);
    background: rgba(224, 168, 94, 0.08);
    padding: 0.05em 0.4em;
    border-radius: 4px;
    font-size: 0.92em;
  }

  .options {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.4rem;
    margin-top: 0.4rem;
  }
  .option {
    border: 1px solid var(--line);
    border-radius: 14px;
    background: var(--bg-elev);
    padding: 1.8rem 1.8rem 1.9rem;
    position: relative;
    overflow: hidden;
  }
  .option::after {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    background: var(--line);
    transition: background 0.3s;
  }
  .option:hover::after { background: var(--accent); }
  .opt-num {
    color: var(--accent);
    font-size: 0.95rem;
    letter-spacing: 0.1em;
  }
  .option h3 {
    margin: 0.6rem 0 0.7rem;
    font-size: clamp(1.4rem, 2.4vw, 2rem);
    font-weight: 640;
    letter-spacing: -0.01em;
  }
  .option p {
    margin: 0;
    color: var(--ink-dim);
    font-size: clamp(0.98rem, 1.4vw, 1.25rem);
    line-height: 1.45;
  }

  .foreshadow {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    color: var(--warn);
    font-size: clamp(0.95rem, 1.4vw, 1.2rem);
    letter-spacing: 0.04em;
    margin: 0.6rem 0 0;
    opacity: 0.92;
  }
  .warn-dot {
    width: 8px; height: 8px;
    background: var(--warn);
    border-radius: 50%;
    box-shadow: 0 0 8px var(--warn);
    flex-shrink: 0;
    animation: pulse 1.8s ease-in-out infinite;
  }
  @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }

  @media (max-width: 760px) {
    .options { grid-template-columns: 1fr; }
  }
  @media (prefers-reduced-motion: reduce) {
    .warn-dot { animation: none; }
  }
</style>
