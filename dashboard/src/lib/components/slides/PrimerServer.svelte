<script lang="ts">
  // Concept primer 1 — what an inference server is.
</script>

<section class="slide">
  <header class="head">
    <p class="kicker mono">EXHIBIT A · THE CAST</p>
    <h2>First, the cast:<br /><span class="amber">an inference server</span></h2>
  </header>

  <p class="body">
    You have model weights. An app wants answers over HTTP. You don&rsquo;t call
    <code>model(...)</code> in production &mdash; you put an <em>inference server</em>
    in between. It batches requests, manages GPU memory (the <em>KV cache</em>), and
    exposes an OpenAI-style <code>/v1/chat/completions</code> API.
  </p>

  <div class="diagram" role="img" aria-label="App sends a request to an inference server, which talks to the GPU and weights">
    <div class="node app">
      <span class="node-label mono">CLIENT</span>
      <span class="node-name">App</span>
      <span class="node-sub mono">HTTP request</span>
    </div>

    <div class="arrow" aria-hidden="true"><span class="line"></span><span class="head-tip"></span></div>

    <div class="node server">
      <span class="node-label mono">THE MIDDLEMAN</span>
      <span class="node-name">Inference server</span>
      <span class="node-sub mono">batch · KV cache · API</span>
    </div>

    <div class="arrow" aria-hidden="true"><span class="line"></span><span class="head-tip"></span></div>

    <div class="node gpu">
      <span class="node-label mono">HARDWARE</span>
      <span class="node-name">GPU + weights</span>
      <span class="node-sub mono">the actual math</span>
    </div>
  </div>
</section>

<style>
  .slide {
    height: 100%;
    padding: 9vh 9vw;
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

  .body {
    max-width: 62ch;
    font-size: clamp(1.05rem, 1.6vw, 1.45rem);
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

  .diagram {
    display: flex;
    align-items: stretch;
    gap: 0.5rem;
    margin-top: 0.6rem;
  }
  .node {
    flex: 1;
    border: 1px solid var(--line);
    border-radius: 12px;
    background: var(--bg-elev);
    padding: 1.4rem 1.3rem;
    display: flex;
    flex-direction: column;
    gap: 0.45rem;
    position: relative;
    opacity: 0;
    animation: pop 0.55s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
  }
  .node.app { animation-delay: 0.05s; }
  .node.server {
    animation-delay: 0.35s;
    border-color: var(--accent);
    box-shadow: 0 0 0 1px rgba(224, 168, 94, 0.25), 0 12px 40px -18px rgba(224, 168, 94, 0.5);
    flex: 1.4;
  }
  .node.gpu { animation-delay: 0.65s; }

  .node-label {
    font-size: 0.62rem;
    letter-spacing: 0.22em;
    color: var(--ink-dim);
  }
  .server .node-label { color: var(--accent); }
  .node-name {
    font-size: clamp(1.1rem, 1.9vw, 1.7rem);
    font-weight: 620;
    letter-spacing: -0.01em;
  }
  .node-sub {
    font-size: 0.78rem;
    color: var(--ink-dim);
  }

  .arrow {
    align-self: center;
    display: flex;
    align-items: center;
    flex: 0 0 56px;
    opacity: 0;
    animation: fadeIn 0.5s forwards;
  }
  .diagram .arrow:nth-of-type(2) { animation-delay: 0.28s; }
  .diagram .arrow:nth-of-type(4) { animation-delay: 0.58s; }
  .arrow .line {
    height: 2px;
    flex: 1;
    background: linear-gradient(90deg, var(--line), var(--accent));
  }
  .arrow .head-tip {
    width: 0; height: 0;
    border-top: 5px solid transparent;
    border-bottom: 5px solid transparent;
    border-left: 8px solid var(--accent);
  }

  @keyframes pop {
    from { opacity: 0; transform: translateY(14px) scale(0.97); }
    to { opacity: 1; transform: translateY(0) scale(1); }
  }
  @keyframes fadeIn { to { opacity: 1; } }

  @media (max-width: 820px) {
    .diagram { flex-direction: column; }
    .arrow { transform: rotate(90deg); flex-basis: 36px; }
    .node.server { flex: 1; }
  }

  @media (prefers-reduced-motion: reduce) {
    .node, .arrow { animation: none; opacity: 1; }
  }
</style>
