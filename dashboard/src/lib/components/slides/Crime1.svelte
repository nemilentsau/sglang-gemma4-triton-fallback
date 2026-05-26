<script lang="ts">
  // Crime #1 — the adapter that wouldn't load.
  import EvidenceCard from '$lib/components/EvidenceCard.svelte';
  import { evidence } from '$lib/data/evidence';
  import { environment } from '$lib/data/runResults';
</script>

<section class="slide">
  <header class="head">
    <p class="kicker mono"><span class="rec" aria-hidden="true"></span>CRIME #1</p>
    <h2>The adapter that<br /><span class="fail">wouldn&rsquo;t load</span></h2>
    <p class="symptom">
      We pass <code>--lora-paths ticket-triage=&hellip;</code>. The server dies
      <strong>before</strong> it ever reports ready.
    </p>
  </header>

  <div class="grid">
    <div class="exhibit">
      <EvidenceCard label="sglang server (startup)" tone="fail" text={evidence.loraError} />
    </div>

    <ol class="investigation" aria-label="Investigation notes">
      <li>
        <span class="tag mono">01</span>
        <div class="note">
          <p>PEFT wrote keys shaped like:</p>
          <EvidenceCard label="adapter checkpoint key" tone="neutral" text={evidence.adapterKeyShape} />
        </div>
      </li>
      <li>
        <span class="tag mono">02</span>
        <div class="note">
          <p>
            Note the triple nesting: <code>model.model.language_model</code>.
            Gemma&nbsp;4&rsquo;s language tower sits inside a multimodal wrapper.
          </p>
        </div>
      </li>
      <li>
        <span class="tag mono">03</span>
        <div class="note">
          <p>
            SGLang {environment.sglang}&rsquo;s LoRA loader can&rsquo;t place <code>lora_A</code> at the
            key shape it expects for this structure. (We&rsquo;d already been forced off
            regex / <code>all-linear</code> <code>target_modules</code> by an SGLang
            constraint, onto explicit module names &mdash; and even those don&rsquo;t load.)
          </p>
        </div>
      </li>
    </ol>
  </div>

  <p class="verdict">
    <span class="verdict-tag mono">VERDICT</span>
    Native LoRA on Gemma&nbsp;4 E2B: <span class="amber">dead on arrival.</span>
  </p>
</section>

<style>
  .slide {
    height: 100%;
    padding: 7vh 9vw;
    display: grid;
    align-content: center;
    gap: 1.8rem;
  }

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
    font-size: clamp(2rem, 4.4vw, 3.6rem);
    line-height: 1;
    letter-spacing: -0.02em;
    font-weight: 660;
    margin: 0 0 1rem;
  }
  .fail { color: var(--fail); font-style: italic; }
  .amber { color: var(--accent); }

  .symptom {
    margin: 0;
    max-width: 62ch;
    font-size: clamp(1rem, 1.5vw, 1.3rem);
    line-height: 1.5;
    color: var(--ink-dim);
  }
  .symptom strong { color: var(--fail); font-weight: 700; }

  code {
    color: var(--accent);
    background: rgba(224, 168, 94, 0.08);
    padding: 0.05em 0.4em;
    border-radius: 4px;
    font-size: 0.9em;
    font-family: var(--mono);
  }

  .grid {
    display: grid;
    grid-template-columns: 0.85fr 1.15fr;
    gap: 2.6vw;
    align-items: start;
  }

  .investigation {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  .investigation li {
    display: flex;
    gap: 0.9rem;
    align-items: flex-start;
  }
  .tag {
    flex-shrink: 0;
    color: var(--fail);
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    border: 1px solid var(--line);
    border-radius: 6px;
    padding: 0.25rem 0.45rem;
    margin-top: 0.1rem;
  }
  .note { flex: 1; min-width: 0; }
  .note p {
    margin: 0 0 0.6rem;
    font-size: clamp(0.95rem, 1.35vw, 1.18rem);
    line-height: 1.5;
    color: var(--ink);
  }
  .note p:last-child { margin-bottom: 0; }

  .verdict {
    margin: 0.4rem 0 0;
    display: flex;
    align-items: baseline;
    gap: 1rem;
    font-size: clamp(1.1rem, 1.9vw, 1.6rem);
    font-weight: 600;
    color: var(--ink);
    border-top: 1px solid var(--line);
    padding-top: 1.3rem;
  }
  .verdict-tag {
    flex-shrink: 0;
    color: var(--accent);
    font-size: 0.72rem;
    letter-spacing: 0.22em;
    align-self: center;
    border: 1px solid var(--accent);
    border-radius: 6px;
    padding: 0.3rem 0.6rem;
  }

  @media (max-width: 880px) {
    .grid { grid-template-columns: 1fr; gap: 1.6rem; }
    .verdict { flex-direction: column; gap: 0.6rem; }
  }
</style>
