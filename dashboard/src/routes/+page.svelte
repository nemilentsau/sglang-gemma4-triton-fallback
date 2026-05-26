<script lang="ts">
  import { onMount } from 'svelte';
  import Deck from '$lib/components/Deck.svelte';
  import { deck } from '$lib/stores/deck';

  function onKey(e: KeyboardEvent) {
    if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {
      e.preventDefault(); deck.next();
    } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
      e.preventDefault(); deck.prev();
    } else if (e.key === 'o' || e.key === 'O') {
      deck.toggleOverview();
    } else if (e.key === 'Escape') {
      deck.toggleOverview();
    }
  }

  onMount(() => {
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  });
</script>

<svelte:head><title>The Gemma 4 Serving Mystery</title></svelte:head>

<main onclick={() => deck.next()} oncontextmenu={(e) => { e.preventDefault(); deck.prev(); }}>
  <Deck />
</main>

<style>
  main { height: 100%; cursor: pointer; }
</style>
