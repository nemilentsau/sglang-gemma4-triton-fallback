<script lang="ts">
  import { onMount } from 'svelte';
  // Grouped bars: for each percentile (p50/p95/p99), one bar per series.
  let { series = [] }:
    { series?: { name: string; color: string; latency: { p50: number; p95: number; p99: number } }[] } = $props();

  let mounted = $state(false);
  onMount(() => { mounted = true; });

  const percentiles = ['p50', 'p95', 'p99'] as const;
  const top = $derived(
    Math.max(1, ...series.flatMap((s) => [s.latency.p50, s.latency.p95, s.latency.p99])) * 1.2
  );
</script>

<div class="chart-wrap">
  <!-- Horizontal grid lines for scale context -->
  <div class="grid" aria-hidden="true">
    {#each [0.75, 0.5, 0.25] as frac}
      <div class="gridline" style="bottom:{frac * 100}%"></div>
    {/each}
  </div>
  <div class="groups">
    {#each percentiles as p}
      <div class="group">
        <div class="bars">
          {#each series as s}
            <div class="track">
              <div
                class="bar"
                style="height:{mounted ? (s.latency[p] / top) * 100 : 0}%; background:{s.color}"
                title="{s.name} {p}: {s.latency[p]}s"
              ></div>
            </div>
          {/each}
        </div>
        <div class="plabel mono">{p}</div>
      </div>
    {/each}
  </div>
</div>

<div class="legend">
  {#each series as s}
    <span class="key"><span class="dot" style="background:{s.color}"></span>{s.name}</span>
  {/each}
</div>

<style>
  .chart-wrap {
    position: relative;
  }
  .grid {
    position: absolute;
    inset: 0;
    bottom: 2rem; /* above the plabel area */
    pointer-events: none;
  }
  .gridline {
    position: absolute;
    left: 0;
    right: 0;
    height: 1px;
    background: var(--line);
    opacity: 0.5;
  }
  .groups { display: flex; gap: 2.5rem; align-items: flex-end; height: 280px; position: relative; }
  .group { flex: 1; display: flex; flex-direction: column; align-items: center; height: 100%; }
  .bars { flex: 1; display: flex; gap: 0.6rem; align-items: flex-end; }
  .track { display: flex; align-items: flex-end; height: 100%; }
  .bar {
    width: 36px;
    border-radius: 5px 5px 0 0;
    transition: height 900ms cubic-bezier(.2,.7,.2,1);
    /* Subtle top highlight for depth */
    box-shadow: inset 0 2px 0 rgba(255, 255, 255, 0.1);
  }
  .plabel { margin-top: 0.6rem; color: var(--ink-dim); }
  .legend { display: flex; gap: 1.5rem; margin-top: 1.2rem; justify-content: center; }
  .key { display: inline-flex; align-items: center; gap: 0.5rem; color: var(--ink-dim); font-size: 0.9rem; }
  .dot { width: 12px; height: 12px; border-radius: 3px; display: inline-block; }
</style>
