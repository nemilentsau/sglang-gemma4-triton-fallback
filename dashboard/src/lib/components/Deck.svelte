<script lang="ts">
  import { fade } from 'svelte/transition';
  import { deck, slides } from '$lib/stores/deck';

  import ColdOpen from './slides/ColdOpen.svelte';
  import PrimerServer from './slides/PrimerServer.svelte';
  import PrimerSglang from './slides/PrimerSglang.svelte';
  import PrimerLora from './slides/PrimerLora.svelte';
  import PrimerBackends from './slides/PrimerBackends.svelte';
  import Mission from './slides/Mission.svelte';
  import Crime1 from './slides/Crime1.svelte';
  import Crime2 from './slides/Crime2.svelte';
  import Solution from './slides/Solution.svelte';
  import Evidence from './slides/Evidence.svelte';
  import Lessons from './slides/Lessons.svelte';

  const components: Record<string, any> = {
    'cold-open': ColdOpen,
    'primer-server': PrimerServer,
    'primer-sglang': PrimerSglang,
    'primer-lora': PrimerLora,
    'primer-backends': PrimerBackends,
    'mission': Mission,
    'crime1': Crime1,
    'crime2': Crime2,
    'solution': Solution,
    'evidence': Evidence,
    'lessons': Lessons
  };

  const Current = $derived(components[slides[$deck.index].id]);
</script>

<div class="stage">
  {#if $deck.overview}
    <div class="overview">
      {#each slides as s, i}
        <button class="thumb" class:active={i === $deck.index} onclick={(e) => { e.stopPropagation(); deck.goto(i); }}>
          <span class="num mono">{String(i + 1).padStart(2, '0')}</span>
          <span class="ttl">{s.title}</span>
        </button>
      {/each}
    </div>
  {:else}
    {#key $deck.index}
      <div class="slide-wrap" in:fade={{ duration: 250 }}>
        <Current />
      </div>
    {/key}
  {/if}

  <div class="rail">
    {#each slides as s, i}
      <button
        class="dot"
        class:on={i <= $deck.index}
        aria-label={s.title}
        onclick={(e) => { e.stopPropagation(); deck.goto(i); }}
      ></button>
    {/each}
    <span class="counter mono">{$deck.index + 1} / {slides.length}</span>
  </div>
</div>

<style>
  .stage { position: fixed; inset: 0; }
  .slide-wrap { position: absolute; inset: 0; }
  .rail {
    position: fixed; left: 0; right: 0; bottom: 0;
    display: flex; gap: 0.5rem; align-items: center;
    padding: 0.8rem 1.2rem; background: linear-gradient(transparent, rgba(0,0,0,.4));
  }
  .dot { width: 26px; height: 4px; border: 0; border-radius: 2px; background: var(--line); cursor: pointer; padding: 0; }
  .dot.on { background: var(--accent); }
  .counter { margin-left: auto; color: var(--ink-dim); font-size: 0.85rem; }
  .overview {
    position: absolute; inset: 0; padding: 5vh 5vw 8vh;
    display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 1rem; align-content: start; overflow: auto;
  }
  .thumb {
    text-align: left; background: var(--bg-elev); border: 1px solid var(--line);
    border-radius: 10px; padding: 1.1rem; color: var(--ink); cursor: pointer;
    display: flex; flex-direction: column; gap: 0.5rem;
  }
  .thumb.active { border-color: var(--accent); }
  .num { color: var(--accent); font-size: 0.8rem; }
  .ttl { font-size: 1.05rem; }
</style>
