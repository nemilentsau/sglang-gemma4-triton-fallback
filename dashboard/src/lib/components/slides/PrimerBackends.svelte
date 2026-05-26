<script lang="ts">
  // Concept primer 4 — swappable attention backends.
</script>

<section class="slide">
  <div class="grid">
    <div class="left">
      <p class="kicker mono">EXHIBIT D · THE ENGINE</p>
      <h2>Attention backends:<br /><span class="amber">swappable engines</span></h2>

      <p class="body">
        The heaviest math in a transformer is <em>attention</em>. SGLang lets you pick
        the kernel that runs it &mdash; <strong>Triton</strong> or
        <strong>FlashInfer</strong> &mdash; with one flag:
        <code>--attention-backend</code>. They should be interchangeable.
      </p>
    </div>

    <div class="socket-wrap" role="img" aria-label="One attention socket accepting either the Triton or FlashInfer engine module">
      <div class="socket">
        <span class="socket-label mono">--attention-backend</span>
        <div class="modules">
          <div class="module a">
            <span class="m-pins" aria-hidden="true"></span>
            <span class="m-name mono">Triton</span>
          </div>
          <span class="slash mono" aria-hidden="true">/</span>
          <div class="module b">
            <span class="m-pins" aria-hidden="true"></span>
            <span class="m-name mono">FlashInfer</span>
          </div>
        </div>
        <span class="socket-foot mono">ONE SOCKET · PICK ONE</span>
      </div>
    </div>
  </div>

  <div class="keyidea">
    <span class="ki-tag mono">⚠ HOLD THAT THOUGHT</span>
    <p>
      But a model <em>feature</em> &mdash; like Gemma&nbsp;4&rsquo;s bidirectional
      attention over image tokens &mdash; may only be implemented on
      <strong>one</strong> backend.
    </p>
  </div>
</section>

<style>
  .slide {
    height: 100%;
    padding: 8vh 9vw;
    display: grid;
    align-content: center;
    gap: 2.4rem;
  }

  .grid {
    display: grid;
    grid-template-columns: 1.3fr 1fr;
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
    font-size: clamp(2.2rem, 5vw, 4rem);
    line-height: 1;
    letter-spacing: -0.02em;
    font-weight: 660;
    margin: 0 0 1.4rem;
  }
  .amber { color: var(--accent); font-style: italic; }

  .body {
    max-width: 50ch;
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
    font-size: 0.92em;
    white-space: nowrap;
  }

  .socket-wrap { display: flex; justify-content: center; }
  .socket {
    border: 1px dashed var(--line);
    border-radius: 16px;
    background: linear-gradient(180deg, var(--bg-elev), rgba(20, 22, 27, 0.4));
    padding: 1.6rem 1.6rem 1.2rem;
    width: 100%;
    max-width: 420px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.1rem;
  }
  .socket-label {
    color: var(--accent);
    font-size: 0.78rem;
    letter-spacing: 0.06em;
  }
  .modules {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    width: 100%;
    justify-content: center;
  }
  .module {
    flex: 1;
    border: 1px solid var(--line);
    border-radius: 10px;
    background: var(--bg);
    padding: 1.1rem 0.5rem 0.9rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.7rem;
    position: relative;
    transition: border-color 0.3s, box-shadow 0.3s;
  }
  .module:hover {
    border-color: var(--accent);
    box-shadow: 0 0 0 1px var(--accent), 0 10px 30px -16px var(--accent);
  }
  .m-pins {
    width: 60%;
    height: 6px;
    border-radius: 2px;
    background-image: repeating-linear-gradient(90deg, var(--accent) 0 3px, transparent 3px 7px);
    opacity: 0.7;
  }
  .m-name { font-size: clamp(0.95rem, 1.7vw, 1.25rem); color: var(--ink); }
  .slash { color: var(--ink-dim); font-size: 1.4rem; }
  .socket-foot { color: var(--ink-dim); font-size: 0.64rem; letter-spacing: 0.22em; }

  .keyidea {
    border: 1px solid var(--accent);
    border-radius: 14px;
    background: rgba(224, 168, 94, 0.05);
    padding: 1.5rem 1.8rem;
    display: flex;
    align-items: baseline;
    gap: 1.6rem;
    box-shadow: 0 0 50px -28px var(--accent) inset;
  }
  .ki-tag {
    flex-shrink: 0;
    color: var(--accent);
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    padding-top: 0.2rem;
  }
  .keyidea p {
    margin: 0;
    font-size: clamp(1.1rem, 1.8vw, 1.55rem);
    line-height: 1.4;
    color: var(--ink);
  }
  .keyidea em { color: var(--accent); font-style: italic; }
  .keyidea strong { color: var(--accent); }

  @media (max-width: 860px) {
    .grid { grid-template-columns: 1fr; gap: 2.4rem; }
    .keyidea { flex-direction: column; gap: 0.8rem; }
  }
</style>
