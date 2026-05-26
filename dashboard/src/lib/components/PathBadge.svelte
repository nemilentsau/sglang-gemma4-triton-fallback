<script lang="ts">
  // Status badge for the three serving paths.
  let { status = 'pass', label = '' }:
    { status?: 'fail' | 'warn' | 'pass'; label?: string } = $props();

  const glyph = $derived(status === 'fail' ? '✕' : status === 'warn' ? '!' : '✓');
  const color = $derived(
    status === 'fail' ? 'var(--fail)' : status === 'warn' ? 'var(--warn)' : 'var(--pass)'
  );
</script>

<span class="badge" style="--c:{color}">
  <span class="glyph">{glyph}</span>{label}
</span>

<style>
  .badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-family: var(--mono);
    font-size: 0.95rem;
    color: var(--c);
    border: 1px solid var(--c);
    border-radius: 999px;
    padding: 0.3rem 0.9rem;
    /* Subtle glow halo matching the status tone */
    box-shadow:
      0 0 0 1px rgba(0, 0, 0, 0.4),
      inset 0 0 12px rgba(255, 255, 255, 0.03),
      0 0 8px color-mix(in srgb, var(--c) 25%, transparent);
    background: color-mix(in srgb, var(--c) 8%, var(--bg-elev));
    letter-spacing: 0.03em;
    transition: box-shadow 0.2s ease;
  }
  .badge:hover {
    box-shadow:
      0 0 0 1px rgba(0, 0, 0, 0.4),
      inset 0 0 16px rgba(255, 255, 255, 0.04),
      0 0 16px color-mix(in srgb, var(--c) 35%, transparent);
  }
  .glyph {
    font-weight: 700;
    /* Slightly larger glyph for terminal-style clarity */
    font-size: 1.05em;
    line-height: 1;
  }
</style>
