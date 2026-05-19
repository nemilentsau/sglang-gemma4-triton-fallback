from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, cast
from urllib import request

from scripts.ticket_triage import (
    build_generation_prompt,
    load_chat_examples,
    parse_json_object,
    score_outputs,
)


def build_payload(
    *,
    prompts: list[str],
    lora_name: str | None,
    max_new_tokens: int,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "text": prompts,
        "sampling_params": {"max_new_tokens": max_new_tokens, "temperature": 0},
    }
    if lora_name is not None:
        payload["lora_path"] = [lora_name] * len(prompts)
    return payload


def extract_texts(response_json: object) -> list[str]:
    if not isinstance(response_json, list):
        raise ValueError("SGLang /generate response must be a list")
    texts: list[str] = []
    for item in cast(list[object], response_json):
        if not isinstance(item, dict):
            raise ValueError("SGLang /generate item must contain text")
        item_obj = cast(dict[str, object], item)
        text = item_obj.get("text")
        if not isinstance(text, str):
            raise ValueError("SGLang /generate item must contain text")
        texts.append(text)
    return texts


def post_json(url: str, payload: dict[str, object]) -> object:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=300) as response:
        return json.loads(response.read().decode("utf-8"))


def score_endpoint(
    *,
    base_url: str,
    split: Path,
    lora_name: str | None,
    batch_size: int,
    max_new_tokens: int,
) -> dict[str, Any]:
    examples = load_chat_examples(split)
    outputs: list[str] = []
    url = f"{base_url.rstrip('/')}/generate"

    for start in range(0, len(examples), batch_size):
        batch = examples[start : start + batch_size]
        prompts = [build_generation_prompt(example.prompt) for example in batch]
        response_json = post_json(
            url,
            build_payload(
                prompts=prompts,
                lora_name=lora_name,
                max_new_tokens=max_new_tokens,
            ),
        )
        outputs.extend(extract_texts(response_json))

    metrics = score_outputs(examples, outputs)
    return {
        "base_url": base_url,
        "split": str(split),
        "lora_name": lora_name,
        "metrics": metrics.to_dict(),
        "examples": [
            {
                "prompt": example.prompt,
                "expected": example.expected,
                "output": output,
                "parsed": parse_json_object(output),
            }
            for example, output in zip(examples, outputs, strict=True)
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score a running SGLang /generate endpoint.")
    parser.add_argument("--base-url", default="http://127.0.0.1:30000")
    parser.add_argument("--split", type=Path, default=Path("fixtures/ticket-triage/test.jsonl"))
    parser.add_argument("--lora-name", default="ticket-triage")
    parser.add_argument("--base-model", action="store_true", help="Score without LoRA.")
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--max-new-tokens", type=int, default=96)
    parser.add_argument("--output-json", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = score_endpoint(
        base_url=args.base_url,
        split=args.split,
        lora_name=None if args.base_model else args.lora_name,
        batch_size=args.batch_size,
        max_new_tokens=args.max_new_tokens,
    )
    rendered = json.dumps(result, indent=2, sort_keys=False)
    if args.output_json is not None:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
