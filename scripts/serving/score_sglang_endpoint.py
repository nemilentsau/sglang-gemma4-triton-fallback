from __future__ import annotations

import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, cast
from urllib import request

from scripts.ticket_triage import (
    ChatExample,
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


def build_chat_payload(*, prompt: str, max_new_tokens: int) -> dict[str, object]:
    return {
        "model": "default",
        "messages": [
            {
                "role": "user",
                "content": build_generation_prompt(prompt),
            }
        ],
        "max_tokens": max_new_tokens,
        "temperature": 0,
    }


def extract_chat_text(response_json: object) -> str:
    if not isinstance(response_json, dict):
        raise ValueError("SGLang chat response must be an object")
    response_obj = cast(dict[str, object], response_json)
    choices = response_obj.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ValueError("SGLang chat response must contain choices")
    choice = cast(list[object], choices)[0]
    if not isinstance(choice, dict):
        raise ValueError("SGLang chat choice must be an object")
    choice_obj = cast(dict[str, object], choice)
    message = choice_obj.get("message")
    if not isinstance(message, dict):
        raise ValueError("SGLang chat choice must contain a message")
    message_obj = cast(dict[str, object], message)
    content = message_obj.get("content")
    if not isinstance(content, str):
        raise ValueError("SGLang chat message must contain string content")
    return content


def extract_completion_tokens(response_json: object) -> int | None:
    if not isinstance(response_json, dict):
        return None
    response_obj = cast(dict[str, object], response_json)
    usage = response_obj.get("usage")
    if not isinstance(usage, dict):
        return None
    usage_obj = cast(dict[str, object], usage)
    completion_tokens = usage_obj.get("completion_tokens")
    if isinstance(completion_tokens, int):
        return completion_tokens
    return None


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


def timed_post_json(url: str, payload: dict[str, object]) -> tuple[object, float]:
    start_seconds = time.perf_counter()
    response_json = post_json(url, payload)
    return response_json, time.perf_counter() - start_seconds


def latency_summary(latencies: list[float]) -> dict[str, float]:
    if not latencies:
        return {
            "min": 0.0,
            "p50": 0.0,
            "p95": 0.0,
            "p99": 0.0,
            "max": 0.0,
        }
    ordered = sorted(latencies)

    def percentile(value: float) -> float:
        index = round((len(ordered) - 1) * value)
        return ordered[index]

    return {
        "min": ordered[0],
        "p50": percentile(0.50),
        "p95": percentile(0.95),
        "p99": percentile(0.99),
        "max": ordered[-1],
    }


def timing_summary(
    *,
    total_seconds: float,
    request_count: int,
    example_count: int,
    max_concurrency: int,
    warmup_request_count: int,
    request_latencies: list[float],
    completion_tokens: list[int],
) -> dict[str, Any]:
    total_completion_tokens = sum(completion_tokens)
    return {
        "total_seconds": total_seconds,
        "request_count": request_count,
        "warmup_request_count": warmup_request_count,
        "example_count": example_count,
        "max_concurrency": max_concurrency,
        "avg_request_seconds": total_seconds / request_count if request_count else 0.0,
        "requests_per_second": request_count / total_seconds if total_seconds else 0.0,
        "examples_per_second": example_count / total_seconds if total_seconds else 0.0,
        "request_latency_seconds": latency_summary(request_latencies),
        "completion_tokens": total_completion_tokens,
        "completion_tokens_per_second": (
            total_completion_tokens / total_seconds if total_seconds else 0.0
        ),
    }


def render_result(
    *,
    base_url: str,
    split: Path,
    api: str,
    lora_name: str | None,
    examples: list[Any],
    outputs: list[str],
    total_seconds: float,
    request_count: int,
    max_concurrency: int,
    warmup_request_count: int,
    request_latencies: list[float],
    completion_tokens: list[int],
) -> dict[str, Any]:
    metrics = score_outputs(examples, outputs)
    return {
        "base_url": base_url,
        "split": str(split),
        "api": api,
        "lora_name": lora_name,
        "metrics": metrics.to_dict(),
        "timing": timing_summary(
            total_seconds=total_seconds,
            request_count=request_count,
            example_count=len(examples),
            max_concurrency=max_concurrency,
            warmup_request_count=warmup_request_count,
            request_latencies=request_latencies,
            completion_tokens=completion_tokens,
        ),
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


def run_chat_request(
    *,
    url: str,
    example: ChatExample,
    max_new_tokens: int,
) -> tuple[str, float, int | None]:
    response_json, latency_seconds = timed_post_json(
        url,
        build_chat_payload(prompt=example.prompt, max_new_tokens=max_new_tokens),
    )
    return (
        extract_chat_text(response_json),
        latency_seconds,
        extract_completion_tokens(response_json),
    )


def run_chat_requests(
    *,
    url: str,
    examples: list[ChatExample],
    max_new_tokens: int,
    max_concurrency: int,
) -> tuple[list[str], list[float], list[int]]:
    outputs = [""] * len(examples)
    latencies = [0.0] * len(examples)
    completion_tokens: list[int] = []

    with ThreadPoolExecutor(max_workers=max_concurrency) as executor:
        futures = {
            executor.submit(
                run_chat_request,
                url=url,
                example=example,
                max_new_tokens=max_new_tokens,
            ): index
            for index, example in enumerate(examples)
        }
        for future in as_completed(futures):
            index = futures[future]
            output, latency_seconds, tokens = future.result()
            outputs[index] = output
            latencies[index] = latency_seconds
            if tokens is not None:
                completion_tokens.append(tokens)

    return outputs, latencies, completion_tokens


def score_endpoint(
    *,
    base_url: str,
    split: Path,
    api: str,
    lora_name: str | None,
    batch_size: int,
    max_new_tokens: int,
    max_examples: int | None,
    max_concurrency: int,
    warmup_examples: int,
) -> dict[str, Any]:
    if batch_size < 1:
        raise ValueError("batch_size must be at least 1")
    if max_concurrency < 1:
        raise ValueError("max_concurrency must be at least 1")
    if max_examples is not None and max_examples < 1:
        raise ValueError("max_examples must be at least 1 when set")
    if warmup_examples < 0:
        raise ValueError("warmup_examples cannot be negative")

    examples = load_chat_examples(split)
    if max_examples is not None:
        examples = examples[:max_examples]
    outputs: list[str] = []
    request_count = 0
    warmup_request_count = 0
    request_latencies: list[float] = []
    completion_tokens: list[int] = []

    if api == "generate":
        url = f"{base_url.rstrip('/')}/generate"
        start_seconds = time.perf_counter()
        for start in range(0, len(examples), batch_size):
            batch = examples[start : start + batch_size]
            prompts = [build_generation_prompt(example.prompt) for example in batch]
            response_json, latency_seconds = timed_post_json(
                url,
                build_payload(
                    prompts=prompts,
                    lora_name=lora_name,
                    max_new_tokens=max_new_tokens,
                ),
            )
            request_count += 1
            request_latencies.append(latency_seconds)
            outputs.extend(extract_texts(response_json))
    elif api == "chat":
        url = f"{base_url.rstrip('/')}/v1/chat/completions"
        if warmup_examples > 0:
            warmup = examples[:warmup_examples]
            run_chat_requests(
                url=url,
                examples=warmup,
                max_new_tokens=max_new_tokens,
                max_concurrency=max_concurrency,
            )
            warmup_request_count = len(warmup)
        start_seconds = time.perf_counter()
        outputs, request_latencies, completion_tokens = run_chat_requests(
            url=url,
            examples=examples,
            max_new_tokens=max_new_tokens,
            max_concurrency=max_concurrency,
        )
        request_count = len(examples)
    else:
        raise ValueError(f"Unsupported API: {api}")

    total_seconds = time.perf_counter() - start_seconds
    return render_result(
        base_url=base_url,
        split=split,
        api=api,
        lora_name=lora_name,
        examples=examples,
        outputs=outputs,
        total_seconds=total_seconds,
        request_count=request_count,
        max_concurrency=max_concurrency if api == "chat" else 1,
        warmup_request_count=warmup_request_count,
        request_latencies=request_latencies,
        completion_tokens=completion_tokens,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score a running SGLang endpoint.")
    parser.add_argument("--base-url", default="http://127.0.0.1:30000")
    parser.add_argument("--split", type=Path, default=Path("fixtures/ticket-triage/test.jsonl"))
    parser.add_argument("--api", choices=("generate", "chat"), default="generate")
    parser.add_argument("--lora-name", default="ticket-triage")
    parser.add_argument("--base-model", action="store_true", help="Score without LoRA.")
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--max-new-tokens", type=int, default=96)
    parser.add_argument("--max-examples", type=int, default=None)
    parser.add_argument("--max-concurrency", type=int, default=8)
    parser.add_argument("--warmup-examples", type=int, default=0)
    parser.add_argument("--output-json", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = score_endpoint(
        base_url=args.base_url,
        split=args.split,
        api=args.api,
        lora_name=None if args.base_model else args.lora_name,
        batch_size=args.batch_size,
        max_new_tokens=args.max_new_tokens,
        max_examples=args.max_examples,
        max_concurrency=args.max_concurrency,
        warmup_examples=args.warmup_examples,
    )
    rendered = json.dumps(result, indent=2, sort_keys=False)
    if args.output_json is not None:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
