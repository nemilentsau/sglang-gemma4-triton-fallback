import { writable } from 'svelte/store';

export interface SlideMeta {
  id: string;
  title: string;     // short label for the overview grid + progress rail
  section: 'open' | 'primer' | 'mission' | 'crime' | 'fix' | 'data' | 'close';
}

export const slides: SlideMeta[] = [
  { id: 'cold-open',       title: 'Cold open',            section: 'open' },
  { id: 'primer-server',   title: 'Inference server',     section: 'primer' },
  { id: 'primer-sglang',   title: 'What is SGLang',       section: 'primer' },
  { id: 'primer-lora',     title: 'LoRA adapters',        section: 'primer' },
  { id: 'primer-backends', title: 'Attention backends',   section: 'primer' },
  { id: 'mission',         title: 'The mission',          section: 'mission' },
  { id: 'crime1',          title: 'Crime #1: LoRA load',  section: 'crime' },
  { id: 'crime2',          title: 'Crime #2: ready lie',  section: 'crime' },
  { id: 'solution',        title: 'The solution',         section: 'fix' },
  { id: 'evidence',        title: 'Evidence room',        section: 'data' },
  { id: 'lessons',         title: 'Lessons',              section: 'close' }
];

interface DeckState {
  index: number;
  overview: boolean;
}

const clamp = (n: number) => Math.max(0, Math.min(slides.length - 1, n));

function createDeck() {
  const { subscribe, update, set } = writable<DeckState>({ index: 0, overview: false });
  return {
    subscribe,
    next: () => update((s) => ({ ...s, index: clamp(s.index + 1) })),
    prev: () => update((s) => ({ ...s, index: clamp(s.index - 1) })),
    goto: (i: number) => set({ index: clamp(i), overview: false }),
    toggleOverview: () => update((s) => ({ ...s, overview: !s.overview }))
  };
}

export const deck = createDeck();
