from pathlib import Path

from scripts.ticket_triage import (
    build_generation_prompt,
    load_chat_examples,
    parse_json_object,
    score_outputs,
)


def test_load_chat_examples_reads_fixture() -> None:
    examples = load_chat_examples(Path("fixtures/ticket-triage/test.jsonl"))

    assert len(examples) == 200
    assert set(examples[0].expected) == {"route", "severity", "macro", "product_code"}


def test_build_generation_prompt_demands_schema_only_json() -> None:
    prompt = build_generation_prompt("Route this ticket.")

    assert "Return only JSON" in prompt
    assert '"product_code"' in prompt


def test_parse_json_object_accepts_prefixed_json() -> None:
    assert parse_json_object('answer: {"route":"billing"}') == {"route": "billing"}


def test_score_outputs_counts_exact_match_and_fields() -> None:
    examples = load_chat_examples(Path("fixtures/ticket-triage/test.jsonl"))[:1]
    metrics = score_outputs(examples, [examples[0].target_json])

    assert metrics.total == 1
    assert metrics.valid_json == 1
    assert metrics.exact_match == 1
    assert metrics.field_accuracy == 1.0
