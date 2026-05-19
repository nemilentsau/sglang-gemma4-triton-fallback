# Ticket Triage Fixture

This fixture gives the profiles a small task with an easy pass/fail check.

Each example is a short synthetic support ticket. The expected answer is a compact JSON object with four repo-specific fields:

- `route`
- `severity`
- `macro`
- `product_code`

The labels are intentionally artificial. A base instruction model can infer that a duplicate subscription charge is a billing issue, but it should not already know that this repo maps it to `BILLING_LEDGER`, `S2`, and `DUPLICATE_CHARGE_EXPLAIN`.

The fixture exists to make adapter behavior visible during serving tests, not to train a useful support model.

## Example

Input:

```text
Buyer says the same subscription renewal appears twice on their card.
```

Expected output:

```json
{
  "route": "BILLING_LEDGER",
  "severity": "S2",
  "macro": "DUPLICATE_CHARGE_EXPLAIN",
  "product_code": "SUBSCRIPTION_CORE"
}
```

## Files

- `schema.json` describes the expected output shape.
- `train.jsonl` contains the training split.
- `val.jsonl` contains held-out examples for tuning prompts or training settings.
- `test.jsonl` contains held-out examples for final smoke checks.

Regenerate the fixture with:

```bash
uv run python scripts/generate_ticket_triage.py --output-dir fixtures/ticket-triage --seed 17
```

The generated split is 1000 train examples, 100 validation examples, and 200 test examples.
The training split is balanced across the 10 ticket scenarios, with 100 examples
for each expected label combination.

The first real pass only needs enough variation to catch obvious serving regressions. It does not need to become a dataset project.
