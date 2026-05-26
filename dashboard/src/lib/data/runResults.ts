export interface Latency {
  p50: number;
  p95: number;
  p99: number;
}

export interface RunResult {
  label: string;
  totalSeconds: number;
  reqPerSec: number;
  latency: Latency;
  completionTokPerSec: number;
  validJson: { valid: number; total: number };
  exactMatch: { matched: number; total: number };
}

export const runResults: { base: RunResult; merged: RunResult } = {
  base: {
    label: 'Base Gemma 4 E2B',
    totalSeconds: 39.9,
    reqPerSec: 5.01,
    latency: { p50: 1.55, p95: 1.87, p99: 1.98 },
    completionTokPerSec: 216.54,
    validJson: { valid: 200, total: 200 },
    exactMatch: { matched: 0, total: 200 }
  },
  merged: {
    label: 'Merged + Triton',
    totalSeconds: 33.26,
    reqPerSec: 6.01,
    latency: { p50: 1.27, p95: 1.74, p99: 1.85 },
    completionTokPerSec: 194.18,
    validJson: { valid: 200, total: 200 },
    exactMatch: { matched: 0, total: 200 }
  }
};

export const environment = {
  gpu: 'NVIDIA RTX A6000 (sm_86, 49140 MiB)',
  sglang: '0.5.12',
  torch: '2.11.0+cu130',
  flashinfer: '0.6.11.post1',
  runDate: '2026-05-20'
};
