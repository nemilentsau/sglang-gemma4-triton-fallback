<script lang="ts">
  import { onMount } from 'svelte';
  // Simple vertical bar chart. `data` is an array of {label, value, color?}.
  let { data = [], unit = '', max = 0 }:
    { data?: { label: string; value: number; color?: string }[]; unit?: string; max?: number } = $props();

  let mounted = $state(false);
  onMount(() => { mounted = true; });

  const top = $derived(max || (Math.max(1, ...data.map((d) => d.value)) * 1.15));
</script>

<div class="chart-wrap">
  <!-- Horizontal grid lines for scale reference (4 lines) -->
  <div class="grid" aria-hidden="true">
    {#each [0.75, 0.5, 0.25] as frac}
      <div class="gridline" style="bottom:{frac * 100}%"></div>
    {/each}
  </div>
  <div class="bars">
    {#each data as d}
      <div class="col">
        <div class="track">
          <div
            class="bar"
            style="height:{mounted ? (d.value / top) * 100 : 0}%; background:{d.color ?? 'var(--accent)'}"
          ></div>
        </div>
        <div class="val mono">{d.value}{unit}</div>
        <div class="lbl">{d.label}</div>
      </div>
    {/each}
  </div>
</div>

<style>
  .chart-wrap {
    position: relative;
  }
  .grid {
    position: absolute;
    inset: 0;
    bottom: 3.2rem; /* below the val + lbl rows */
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
  .bars { display: flex; gap: 2rem; align-items: flex-end; height: 320px; position: relative; }
  .col { display: flex; flex-direction: column; align-items: center; flex: 1; height: 100%; }
  .track { flex: 1; width: 64px; display: flex; align-items: flex-end; }
  .bar {
    width: 100%;
    border-radius: 6px 6px 0 0;
    transition: height 900ms cubic-bezier(.2,.7,.2,1);
    /* Subtle top highlight on bars for depth */
    box-shadow: inset 0 2px 0 rgba(255, 255, 255, 0.12);
  }
  .val { margin-top: 0.6rem; color: var(--ink); font-size: 1.1rem; }
  .lbl { color: var(--ink-dim); font-size: 0.9rem; margin-top: 0.25rem; text-align: center; }
</style>
