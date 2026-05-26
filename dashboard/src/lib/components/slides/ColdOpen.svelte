<script lang="ts">
  // Title card — opening frame of the case file.
  import { environment } from '$lib/data/runResults';
</script>

<section class="slide">
  <div class="vignette" aria-hidden="true"></div>
  <div class="grain" aria-hidden="true"></div>

  <div class="frame">
    <p class="eyebrow mono">
      <span class="rec" aria-hidden="true"></span>
      CASE FILE · SGLANG {environment.sglang} · GEMMA 4 E2B
    </p>

    <h1 class="headline">
      We just wanted to<br />serve a <span class="amber">fine-tuned</span> model.
    </h1>

    <p class="subhead">
      It took three tries to get one request answered.<br />
      Here&rsquo;s the investigation.
    </p>
  </div>

  <div class="stamp mono" aria-hidden="true">
    <span class="stamp-line">CLASSIFIED</span>
    <span class="stamp-sub">CASE NO. 0512-E2B</span>
  </div>

  <p class="footer mono">→ / space to advance · o for overview</p>
</section>

<style>
  .slide {
    position: relative;
    height: 100%;
    padding: 8vh 9vw;
    display: grid;
    align-content: center;
    overflow: hidden;
  }

  .vignette {
    position: absolute;
    inset: 0;
    pointer-events: none;
    background:
      radial-gradient(120% 90% at 50% 40%, transparent 38%, rgba(0, 0, 0, 0.55) 100%),
      radial-gradient(60% 50% at 18% 22%, rgba(224, 168, 94, 0.05), transparent 70%);
  }
  .grain {
    position: absolute;
    inset: 0;
    pointer-events: none;
    opacity: 0.5;
    background-image:
      repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(255, 255, 255, 0.012) 2px, rgba(255, 255, 255, 0.012) 3px);
  }

  .frame {
    position: relative;
    z-index: 1;
    max-width: min(90vw, 60rem);
  }

  .eyebrow {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    color: var(--accent);
    font-size: clamp(0.7rem, 1vw, 0.95rem);
    letter-spacing: 0.32em;
    text-transform: uppercase;
    margin: 0 0 2.2rem;
    opacity: 0;
    animation: rise 0.7s 0.1s cubic-bezier(0.2, 0.7, 0.2, 1) forwards;
  }
  .rec {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: var(--fail);
    box-shadow: 0 0 10px var(--fail);
    animation: blink 1.4s steps(1) infinite;
  }

  .headline {
    font-size: clamp(2.6rem, 5.6vw, 5rem);
    line-height: 1.0;
    letter-spacing: -0.02em;
    font-weight: 680;
    margin: 0;
    text-wrap: balance;
    opacity: 0;
    animation: rise 0.9s 0.28s cubic-bezier(0.2, 0.7, 0.2, 1) forwards;
  }
  .amber {
    color: var(--accent);
    font-style: italic;
  }

  .subhead {
    margin: 2.4rem 0 0;
    font-size: clamp(1.05rem, 1.8vw, 1.6rem);
    line-height: 1.45;
    color: var(--ink-dim);
    max-width: 40ch;
    opacity: 0;
    animation: rise 0.9s 0.5s cubic-bezier(0.2, 0.7, 0.2, 1) forwards;
  }

  /* Cursor after subhead */
  .subhead::after {
    content: '';
    display: inline-block;
    width: 0.6ch;
    height: 1.05em;
    margin-left: 0.25ch;
    transform: translateY(0.15em);
    background: var(--accent);
    animation: blink 1.1s steps(1) infinite;
  }

  .stamp {
    position: absolute;
    right: 6vw;
    top: 50%;
    z-index: 1;
    transform: translateY(-50%) rotate(-9deg);
    border: 2px solid rgba(229, 86, 75, 0.5);
    border-radius: 6px;
    padding: 0.7rem 1.4rem;
    text-align: center;
    color: rgba(229, 86, 75, 0.62);
    letter-spacing: 0.18em;
    opacity: 0;
    animation: stampIn 0.4s 1s cubic-bezier(0.3, 1.6, 0.5, 1) forwards;
  }
  .stamp-line {
    display: block;
    font-size: clamp(1.1rem, 2.1vw, 1.9rem);
    font-weight: 700;
  }
  .stamp-sub {
    display: block;
    margin-top: 0.3rem;
    font-size: 0.65rem;
    letter-spacing: 0.3em;
    color: rgba(229, 86, 75, 0.45);
  }

  .footer {
    position: absolute;
    left: 9vw;
    bottom: 7vh;
    z-index: 1;
    color: var(--ink-dim);
    font-size: 0.85rem;
    letter-spacing: 0.08em;
    opacity: 0;
    animation: fadeIn 0.8s 1.2s forwards;
  }

  @keyframes rise {
    from { opacity: 0; transform: translateY(18px); }
    to { opacity: 1; transform: translateY(0); }
  }
  @keyframes fadeIn { to { opacity: 1; } }
  @keyframes blink { 0%, 50% { opacity: 1; } 50.01%, 100% { opacity: 0.15; } }
  @keyframes stampIn {
    from { opacity: 0; transform: translateY(-50%) rotate(-9deg) scale(1.4); }
    to { opacity: 1; transform: translateY(-50%) rotate(-9deg) scale(1); }
  }

  @media (max-width: 760px) {
    .stamp { display: none; }
  }

  @media (prefers-reduced-motion: reduce) {
    .eyebrow, .headline, .subhead, .footer, .stamp { animation: none; opacity: 1; }
    .stamp { transform: translateY(-50%) rotate(-9deg); }
    .rec, .subhead::after { animation: none; }
  }
</style>
