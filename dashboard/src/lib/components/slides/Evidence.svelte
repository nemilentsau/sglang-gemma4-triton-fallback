<script lang="ts">
  // The evidence room — the data payoff. Charts animate on mount.
  import BarChart from '$lib/components/charts/BarChart.svelte';
  import LatencyChart from '$lib/components/charts/LatencyChart.svelte';
  import { runResults, environment } from '$lib/data/runResults';

  const { base, merged } = runResults;
</script>

<section class="slide">
  <header class="head">
    <p class="kicker mono">EXHIBIT E · THE PAYOFF</p>
    <h2>The evidence room:<br /><span class="amber">it actually serves</span></h2>
  </header>

  <div class="charts">
    <figure class="chart">
      <figcaption class="chart-cap mono">Throughput (req/s)</figcaption>
      <BarChart
        unit=" req/s"
        data={[
          { label: base.label, value: base.reqPerSec, color: 'var(--ink-dim)' },
          { label: merged.label, value: merged.reqPerSec, color: 'var(--accent)' }
        ]}
      />
    </figure>

    <figure class="chart">
      <figcaption class="chart-cap mono">Latency (seconds)</figcaption>
      <LatencyChart
        series={[
          { name: base.label, color: 'var(--ink-dim)', latency: base.latency },
          { name: merged.label, color: 'var(--accent)', latency: merged.latency }
        ]}
      />
    </figure>
  </div>

  <div class="readout">
    <p class="stat">
      Both runs: <strong>{merged.validJson.valid}/{merged.validJson.total} valid JSON.</strong>
      Merged is faster: <span class="amber">{merged.reqPerSec} vs {base.reqPerSec} req/s</span>,
      p50 <span class="amber">{merged.latency.p50}s vs {base.latency.p50}s.</span>
    </p>
    <p class="caveat">
      Exact-match accuracy is {merged.exactMatch.matched}/{merged.exactMatch.total} by design
      &mdash; this is a synthetic fixture with no real task-training signal. The point is
      <em>serving behavior</em>, not task scores.
    </p>
  </div>

  <p class="env mono">
    {environment.gpu} · SGLang {environment.sglang} · Torch {environment.torch} ·
    FlashInfer {environment.flashinfer} · {environment.runDate}
  </p>
</section>

<style>
  .slide {
    height: 100%;
    padding: 5vh 7vw;
    display: grid;
    align-content: center;
    gap: 1.5rem;
  }

  .kicker {
    color: var(--accent);
    letter-spacing: 0.28em;
    font-size: 0.78rem;
    margin: 0 0 0.7rem;
  }
  h2 {
    font-size: clamp(1.8rem, 3.6vw, 3rem);
    line-height: 1;
    letter-spacing: -0.02em;
    font-weight: 660;
    margin: 0;
  }
  .amber { color: var(--accent); font-style: italic; }

  .charts {
    display: grid;
    grid-template-columns: 0.85fr 1.15fr;
    gap: 4vw;
    align-items: end;
  }
  .chart { margin: 0; }
  .chart-cap {
    color: var(--ink-dim);
    font-size: 0.72rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--line);
  }

  .readout {
    display: flex;
    flex-direction: column;
    gap: 0.55rem;
  }
  .stat {
    margin: 0;
    font-size: clamp(1rem, 1.5vw, 1.35rem);
    line-height: 1.4;
    color: var(--ink);
  }
  .stat strong { color: var(--pass); font-weight: 700; }
  .stat .amber { font-style: normal; font-weight: 600; }
  .caveat {
    margin: 0;
    font-size: clamp(0.88rem, 1.2vw, 1.05rem);
    line-height: 1.45;
    color: var(--ink-dim);
    max-width: 90ch;
  }
  .caveat em { color: var(--ink); font-style: italic; }

  .env {
    margin: 0;
    color: var(--ink-dim);
    font-size: 0.74rem;
    letter-spacing: 0.04em;
    opacity: 0.85;
    border-top: 1px solid var(--line);
    padding-top: 0.9rem;
  }

  @media (max-width: 900px) {
    .charts { grid-template-columns: 1fr; gap: 2.5rem; }
  }
</style>
