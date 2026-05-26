import { describe, it, expect } from 'vitest';
import { runResults, environment } from '../src/lib/data/runResults';
import { evidence } from '../src/lib/data/evidence';

describe('runResults', () => {
  it('has base and merged runs with the recorded throughput', () => {
    expect(runResults.base.reqPerSec).toBe(5.01);
    expect(runResults.merged.reqPerSec).toBe(6.01);
  });

  it('records p50/p95/p99 latency for both runs', () => {
    expect(runResults.base.latency).toEqual({ p50: 1.55, p95: 1.87, p99: 1.98 });
    expect(runResults.merged.latency).toEqual({ p50: 1.27, p95: 1.74, p99: 1.85 });
  });

  it('records 200/200 valid JSON for both runs', () => {
    expect(runResults.base.validJson).toEqual({ valid: 200, total: 200 });
    expect(runResults.merged.validJson).toEqual({ valid: 200, total: 200 });
  });

  it('names the test environment', () => {
    expect(environment.gpu).toContain('A6000');
    expect(environment.sglang).toBe('0.5.12');
  });
});

describe('evidence', () => {
  it('contains the native LoRA RuntimeError with the lora_A key', () => {
    expect(evidence.loraError).toContain('Failed to load LoRA adapter');
    expect(evidence.loraError).toContain('lora_A.weight');
  });

  it('contains the FlashInfer bidirectional-attention warning', () => {
    expect(evidence.flashinferWarning).toContain('TritonAttnBackend');
  });

  it('contains the FlashInfer invalid-configuration error', () => {
    expect(evidence.flashinferError).toContain('Invalid configuration');
  });
});
