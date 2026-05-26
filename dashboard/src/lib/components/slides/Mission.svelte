<script lang="ts">
  // The mission — the intended happy path.
</script>

<section class="slide">
  <header class="head">
    <p class="kicker mono">THE BRIEF · OBJECTIVE</p>
    <h2>The mission: serve a<br /><span class="amber">fine-tuned Gemma&nbsp;4</span></h2>
  </header>

  <p class="body">
    We trained a LoRA adapter on <strong>Gemma&nbsp;4 E2B</strong> for
    <em>ticket triage</em> &mdash; read a support ticket, emit JSON
    (<code>route</code>, <code>severity</code>, <code>macro</code>,
    <code>product_code</code>). Goal: serve it on SGLang and answer requests.
  </p>

  <ol class="flow" aria-label="Intended happy path: train adapter, load in SGLang, call the API">
    <li class="step">
      <span class="step-num mono">STEP 1</span>
      <span class="step-text">Train LoRA adapter</span>
    </li>
    <li class="connector" aria-hidden="true"></li>
    <li class="step">
      <span class="step-num mono">STEP 2</span>
      <span class="step-text">Load in SGLang</span>
      <code>--lora-paths</code>
    </li>
    <li class="connector" aria-hidden="true"></li>
    <li class="step">
      <span class="step-num mono">STEP 3</span>
      <span class="step-text">Call the API</span>
      <code>/v1/chat/completions</code>
    </li>
  </ol>

  <p class="footer">That&rsquo;s the plan. The plan does not survive contact with the loader.</p>
</section>

<style>
  .slide {
    height: 100%;
    padding: 8vh 9vw;
    display: grid;
    align-content: center;
    gap: 2.1rem;
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
  .body em { color: var(--ink); font-style: normal; }
  .body strong { color: var(--ink); font-weight: 600; }
  code {
    color: var(--accent);
    background: rgba(224, 168, 94, 0.08);
    padding: 0.05em 0.4em;
    border-radius: 4px;
    font-size: 0.9em;
    white-space: nowrap;
  }

  .flow {
    list-style: none;
    margin: 0.3rem 0 0;
    padding: 0;
    display: flex;
    align-items: stretch;
    gap: 0;
  }
  .step {
    flex: 1;
    border: 1px solid var(--line);
    border-radius: 12px;
    background: var(--bg-elev);
    padding: 1.3rem 1.4rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    position: relative;
    z-index: 1;
  }
  .step-num { color: var(--accent); font-size: 0.66rem; letter-spacing: 0.22em; }
  .step-text {
    font-size: clamp(1.1rem, 1.9vw, 1.55rem);
    font-weight: 620;
    letter-spacing: -0.01em;
  }
  .step code { align-self: flex-start; }

  .connector {
    flex: 0 0 42px;
    align-self: center;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--line));
    position: relative;
  }
  .connector::after {
    content: '';
    position: absolute;
    right: -1px; top: 50%;
    transform: translateY(-50%);
    width: 0; height: 0;
    border-top: 5px solid transparent;
    border-bottom: 5px solid transparent;
    border-left: 8px solid var(--accent);
    opacity: 0.6;
  }

  .footer {
    margin: 0.6rem 0 0;
    color: var(--ink-dim);
    font-size: clamp(0.95rem, 1.4vw, 1.2rem);
    font-style: italic;
    letter-spacing: 0.01em;
  }

  @media (max-width: 820px) {
    .flow { flex-direction: column; }
    .connector { width: 2px; height: 32px; flex-basis: 32px; align-self: center; background: linear-gradient(180deg, var(--accent), var(--line)); }
    .connector::after { right: 50%; top: auto; bottom: -1px; transform: translateX(50%); border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 8px solid var(--accent); border-bottom: 0; }
  }
</style>
