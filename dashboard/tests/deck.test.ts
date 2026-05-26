import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { deck, slides } from '../src/lib/stores/deck';

beforeEach(() => deck.goto(0));

describe('deck store', () => {
  it('exposes the ordered slide registry', () => {
    expect(slides.length).toBe(11);
    expect(slides[0].id).toBe('cold-open');
    expect(slides[slides.length - 1].id).toBe('lessons');
  });

  it('starts at slide 0 with overview closed', () => {
    expect(get(deck).index).toBe(0);
    expect(get(deck).overview).toBe(false);
  });

  it('advances and goes back', () => {
    deck.next();
    expect(get(deck).index).toBe(1);
    deck.prev();
    expect(get(deck).index).toBe(0);
  });

  it('clamps at the first slide (prev is a no-op)', () => {
    deck.prev();
    expect(get(deck).index).toBe(0);
  });

  it('clamps at the last slide (next is a no-op)', () => {
    deck.goto(slides.length - 1);
    deck.next();
    expect(get(deck).index).toBe(slides.length - 1);
  });

  it('goto clamps out-of-range values', () => {
    deck.goto(999);
    expect(get(deck).index).toBe(slides.length - 1);
    deck.goto(-5);
    expect(get(deck).index).toBe(0);
  });

  it('toggles overview', () => {
    deck.toggleOverview();
    expect(get(deck).overview).toBe(true);
    deck.toggleOverview();
    expect(get(deck).overview).toBe(false);
  });

  it('goto closes the overview', () => {
    deck.toggleOverview();
    deck.goto(3);
    expect(get(deck).overview).toBe(false);
    expect(get(deck).index).toBe(3);
  });
});
