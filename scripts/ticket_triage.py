from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, cast

EXPECTED_FIELDS = ("route", "severity", "macro", "product_code")


@dataclass(frozen=True)
class ChatExample:
    prompt: str
    expected: dict[str, str]

    @property
    def target_json(self) -> str:
        return json.dumps(self.expected, separators=(",", ":"), sort_keys=False)


@dataclass(frozen=True)
class ScoreMetrics:
    total: int
    valid_json: int
    exact_match: int
    field_matches: int
    field_total: int

    @property
    def exact_match_rate(self) -> float:
        return self.exact_match / self.total if self.total else 0.0

    @property
    def valid_json_rate(self) -> float:
        return self.valid_json / self.total if self.total else 0.0

    @property
    def field_accuracy(self) -> float:
        return self.field_matches / self.field_total if self.field_total else 0.0

    def to_dict(self) -> dict[str, int | float]:
        data: dict[str, int | float] = asdict(self)
        data["exact_match_rate"] = self.exact_match_rate
        data["valid_json_rate"] = self.valid_json_rate
        data["field_accuracy"] = self.field_accuracy
        return data


def _as_object(value: object, *, context: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{context}: expected object")
    return cast(dict[str, object], value)


def load_chat_examples(path: Path) -> list[ChatExample]:
    examples: list[ChatExample] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        record = _as_object(json.loads(line), context=f"{path}:{line_number}")
        messages_raw = record.get("messages")
        if not isinstance(messages_raw, list):
            raise ValueError(f"{path}:{line_number}: expected exactly two chat messages")
        messages = cast(list[object], messages_raw)
        if len(messages) != 2:
            raise ValueError(f"{path}:{line_number}: expected exactly two chat messages")

        user_message = _as_object(messages[0], context=f"{path}:{line_number}: user message")
        assistant_message = _as_object(
            messages[1],
            context=f"{path}:{line_number}: assistant message",
        )
        if user_message.get("role") != "user" or assistant_message.get("role") != "assistant":
            raise ValueError(f"{path}:{line_number}: expected user then assistant messages")

        prompt = user_message.get("content")
        expected_raw = assistant_message.get("content")
        if not isinstance(prompt, str) or not isinstance(expected_raw, str):
            raise ValueError(f"{path}:{line_number}: message content must be strings")

        expected = _as_object(
            json.loads(expected_raw),
            context=f"{path}:{line_number}: assistant content",
        )
        if set(expected) != set(EXPECTED_FIELDS):
            raise ValueError(f"{path}:{line_number}: assistant JSON does not match expected fields")
        if not all(isinstance(value, str) for value in expected.values()):
            raise ValueError(f"{path}:{line_number}: assistant JSON values must be strings")

        examples.append(ChatExample(prompt=prompt, expected=cast(dict[str, str], expected)))
    return examples


def parse_json_object(text: str) -> dict[str, Any] | None:
    decoder = json.JSONDecoder()
    start = text.find("{")
    while start != -1:
        try:
            parsed, _ = decoder.raw_decode(text[start:])
        except json.JSONDecodeError:
            start = text.find("{", start + 1)
            continue
        if isinstance(parsed, dict):
            return cast(dict[str, Any], parsed)
        start = text.find("{", start + 1)
    return None


def score_outputs(examples: list[ChatExample], outputs: list[str]) -> ScoreMetrics:
    if len(examples) != len(outputs):
        raise ValueError("examples and outputs must have the same length")

    valid_json = 0
    exact_match = 0
    field_matches = 0
    field_total = len(examples) * len(EXPECTED_FIELDS)

    for example, output in zip(examples, outputs, strict=True):
        parsed = parse_json_object(output)
        if parsed is None:
            continue
        valid_json += 1
        if parsed == example.expected:
            exact_match += 1
        for field in EXPECTED_FIELDS:
            if parsed.get(field) == example.expected[field]:
                field_matches += 1

    return ScoreMetrics(
        total=len(examples),
        valid_json=valid_json,
        exact_match=exact_match,
        field_matches=field_matches,
        field_total=field_total,
    )


def build_generation_prompt(user_prompt: str) -> str:
    schema_hint = (
        '{"route":"...","severity":"...","macro":"...",'
        '"product_code":"..."}'
    )
    return (
        f"{user_prompt}\n\n"
        "Return only JSON. Use exactly this shape and no prose:\n"
        f"{schema_hint}"
    )
