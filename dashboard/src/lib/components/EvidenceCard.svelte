<script lang="ts">
  // A framed monospace block for showing real logs/errors as "evidence".
  // `label` is the little caption (e.g. "server.log"); `text` is the body.
  // `tone` colors the frame: 'fail' | 'warn' | 'neutral'.
  let { label = 'evidence', text = '', tone = 'neutral' }:
    { label?: string; text?: string; tone?: 'fail' | 'warn' | 'neutral' } = $props();

  const border = $derived(
    tone === 'fail' ? 'var(--fail)' : tone === 'warn' ? 'var(--warn)' : 'var(--line)'
  );
</script>

<figure class="evidence" style="--frame:{border}">
  <figcaption>
    <span class="dot"></span>{label}
  </figcaption>
  <pre class="mono">{text}</pre>
</figure>

<style>
  .evidence {
    margin: 0;
    border: 1px solid var(--frame);
    border-left: 3px solid var(--frame);
    border-radius: 8px;
    background: var(--bg-elev);
    overflow: hidden;
    /* Subtle scanline texture for that "terminal output" feel */
    background-image:
      repeating-linear-gradient(
        0deg,
        transparent,
        transparent 23px,
        rgba(255, 255, 255, 0.012) 23px,
        rgba(255, 255, 255, 0.012) 24px
      );
  }
  figcaption {
    display: flex;
    align-items: center;
    gap: 0.45rem;
    font-family: var(--mono);
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--ink-dim);
    padding: 0.4rem 0.8rem;
    border-bottom: 1px solid var(--line);
    background: rgba(0, 0, 0, 0.2);
    /* Background image resets here so caption area is clean */
    background-image: none;
    background-color: rgba(0, 0, 0, 0.25);
  }
  .dot {
    display: inline-block;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--frame);
    flex-shrink: 0;
    /* Glow on the tone color dot */
    box-shadow: 0 0 5px var(--frame);
  }
  pre {
    margin: 0;
    padding: 1rem;
    font-size: 0.95rem;
    line-height: 1.5;
    color: var(--ink);
    white-space: pre-wrap;
    word-break: break-word;
    /* Ensure pre area itself has no background override */
    background: transparent;
  }
</style>
