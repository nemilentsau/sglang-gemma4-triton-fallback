from __future__ import annotations

import argparse
import json
import random
import re
from dataclasses import asdict, dataclass
from importlib import import_module
from pathlib import Path
from typing import Any

from scripts.ticket_triage import build_generation_prompt, load_chat_examples

DEFAULT_MODEL_ID = "google/gemma-4-E2B-it"
DEFAULT_REVISION = "905e84b50c4d2a365ebde34e685027578e6728db"
DEFAULT_LOCAL_MODEL_DIR = Path("models/gemma4-e2b-it") / DEFAULT_REVISION
DEFAULT_TARGET_MODULES = (
    r".*language_model.*(q_proj|k_proj|v_proj|o_proj|gate_proj|up_proj|down_proj)$"
)


@dataclass(frozen=True)
class TrainConfig:
    base_model_dir: Path
    model_id: str
    revision: str
    train_split: Path
    val_split: Path
    output_dir: Path
    seed: int
    epochs: int
    learning_rate: float
    batch_size: int
    gradient_accumulation_steps: int
    max_train_examples: int | None
    max_length: int
    lora_rank: int
    lora_alpha: int
    lora_dropout: float
    target_modules: str | list[str]
    log_every_steps: int


def default_output_dir(model_id: str, revision: str) -> Path:
    safe_model_id = model_id.lower().replace("/", "-")
    return Path("adapters") / f"{safe_model_id}-ticket-triage-lora" / revision


def parse_target_modules(value: str) -> str | list[str]:
    if value.startswith("regex:"):
        pattern = value.removeprefix("regex:")
        if not pattern:
            raise ValueError("target module regex must not be empty")
        return pattern
    if value.startswith(".*") or value.startswith("^"):
        return value
    modules = [part.strip() for part in value.split(",") if part.strip()]
    if not modules:
        raise ValueError("at least one target module is required")
    return modules


def _load_training_deps() -> tuple[Any, Any, Any]:
    try:
        torch = import_module("torch")
        transformers = import_module("transformers")
        peft = import_module("peft")
    except ModuleNotFoundError as exc:
        raise SystemExit("Missing training dependencies. Run: uv sync --extra train") from exc
    return torch, transformers, peft


def _set_seed(torch: Any, seed: int) -> None:
    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def _apply_chat_template(
    tokenizer: Any,
    messages: list[dict[str, str]],
    *,
    add_generation_prompt: bool,
) -> str:
    kwargs: dict[str, object] = {
        "tokenize": False,
        "add_generation_prompt": add_generation_prompt,
    }
    try:
        return str(tokenizer.apply_chat_template(messages, **kwargs, enable_thinking=False))
    except TypeError:
        return str(tokenizer.apply_chat_template(messages, **kwargs))


def _tokenize_example(
    tokenizer: Any,
    prompt: str,
    target_json: str,
    max_length: int,
) -> dict[str, Any]:
    user_content = build_generation_prompt(prompt)
    user_messages = [{"role": "user", "content": user_content}]
    full_messages = [*user_messages, {"role": "assistant", "content": target_json}]

    prefix_text = _apply_chat_template(tokenizer, user_messages, add_generation_prompt=True)
    full_text = _apply_chat_template(tokenizer, full_messages, add_generation_prompt=False)
    if tokenizer.eos_token:
        full_text += tokenizer.eos_token

    tokenized = tokenizer(full_text, truncation=True, max_length=max_length)
    prefix = tokenizer(prefix_text, truncation=True, max_length=max_length)
    labels = list(tokenized["input_ids"])
    prefix_len = min(len(prefix["input_ids"]), len(labels))
    labels[:prefix_len] = [-100] * prefix_len
    tokenized["labels"] = labels
    return tokenized


def _collate_batch(torch: Any, tokenizer: Any, batch: list[dict[str, Any]]) -> dict[str, Any]:
    pad_id = (
        tokenizer.pad_token_id
        if tokenizer.pad_token_id is not None
        else tokenizer.eos_token_id
    )
    max_len = max(len(item["input_ids"]) for item in batch)
    input_ids: list[list[int]] = []
    attention_mask: list[list[int]] = []
    labels: list[list[int]] = []

    for item in batch:
        pad = max_len - len(item["input_ids"])
        input_ids.append([*item["input_ids"], *([pad_id] * pad)])
        attention_mask.append([*item["attention_mask"], *([0] * pad)])
        labels.append([*item["labels"], *([-100] * pad)])

    return {
        "input_ids": torch.tensor(input_ids, dtype=torch.long),
        "attention_mask": torch.tensor(attention_mask, dtype=torch.long),
        "labels": torch.tensor(labels, dtype=torch.long),
    }


def _auto_model_class(transformers: Any) -> Any:
    if hasattr(transformers, "AutoModelForImageTextToText"):
        return transformers.AutoModelForImageTextToText
    return transformers.AutoModelForCausalLM


def _build_metadata(
    config: TrainConfig,
    *,
    train_examples: int,
    val_examples: int,
) -> dict[str, object]:
    data = asdict(config)
    for key in ("base_model_dir", "train_split", "val_split", "output_dir"):
        data[key] = str(data[key])
    data["train_examples"] = train_examples
    data["val_examples"] = val_examples
    return data


def _expand_target_modules(model: Any, target_modules: str | list[str]) -> str | list[str]:
    if not isinstance(target_modules, str):
        return target_modules
    pattern = re.compile(target_modules)
    expanded = [
        name
        for name, module in model.named_modules()
        if pattern.fullmatch(name) and type(module).__name__ == "Linear"
    ]
    if not expanded:
        raise ValueError(f"target module regex matched no Linear modules: {target_modules}")
    return expanded


def train(config: TrainConfig) -> None:
    torch, transformers, peft = _load_training_deps()
    _set_seed(torch, config.seed)

    tokenizer = transformers.AutoTokenizer.from_pretrained(config.base_model_dir)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model_cls = _auto_model_class(transformers)
    model = model_cls.from_pretrained(
        config.base_model_dir,
        torch_dtype="auto",
        device_map="auto",
    )
    if hasattr(model, "gradient_checkpointing_enable"):
        model.gradient_checkpointing_enable()

    target_modules = _expand_target_modules(model, config.target_modules)
    lora_config = peft.LoraConfig(
        r=config.lora_rank,
        lora_alpha=config.lora_alpha,
        lora_dropout=config.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=target_modules,
    )
    model = peft.get_peft_model(model, lora_config)
    model.train()

    train_examples = load_chat_examples(config.train_split)
    if config.max_train_examples is not None:
        train_examples = train_examples[: config.max_train_examples]
    if not train_examples:
        raise ValueError("training split produced no examples")
    val_examples = load_chat_examples(config.val_split)
    tokenized = [
        _tokenize_example(tokenizer, example.prompt, example.target_json, config.max_length)
        for example in train_examples
    ]
    optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate)
    device = next(model.parameters()).device
    step = 0

    for epoch in range(config.epochs):
        random.shuffle(tokenized)
        running_loss = 0.0
        optimizer.zero_grad(set_to_none=True)
        for index in range(0, len(tokenized), config.batch_size):
            batch_items = tokenized[index : index + config.batch_size]
            batch = _collate_batch(torch, tokenizer, batch_items)
            batch = {key: value.to(device) for key, value in batch.items()}
            output = model(**batch)
            loss = output.loss / config.gradient_accumulation_steps
            loss.backward()
            running_loss += float(loss.detach().cpu()) * config.gradient_accumulation_steps
            if (step + 1) % config.gradient_accumulation_steps == 0:
                optimizer.step()
                optimizer.zero_grad(set_to_none=True)
            step += 1
            if config.log_every_steps > 0 and step % config.log_every_steps == 0:
                print(
                    f"epoch={epoch + 1} step={step} "
                    f"loss={float(loss.detach().cpu()) * config.gradient_accumulation_steps:.4f}",
                    flush=True,
                )
        print(f"epoch={epoch + 1} loss={running_loss / len(tokenized):.4f}")

    if step % config.gradient_accumulation_steps:
        optimizer.step()
        optimizer.zero_grad(set_to_none=True)

    config.output_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(config.output_dir)
    tokenizer.save_pretrained(config.output_dir)
    metadata = _build_metadata(
        config,
        train_examples=len(train_examples),
        val_examples=len(val_examples),
    )
    (config.output_dir / "training-manifest.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    print(f"Saved LoRA adapter to {config.output_dir}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train Gemma 4 LoRA on ticket-triage.")
    parser.add_argument("--base-model-dir", type=Path, default=DEFAULT_LOCAL_MODEL_DIR)
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument("--revision", default=DEFAULT_REVISION)
    parser.add_argument(
        "--train-split",
        type=Path,
        default=Path("fixtures/ticket-triage/train.jsonl"),
    )
    parser.add_argument("--val-split", type=Path, default=Path("fixtures/ticket-triage/val.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=4)
    parser.add_argument("--max-train-examples", type=int, default=64)
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument("--lora-rank", type=int, default=8)
    parser.add_argument("--lora-alpha", type=int, default=16)
    parser.add_argument("--lora-dropout", type=float, default=0.05)
    parser.add_argument("--target-modules", default=DEFAULT_TARGET_MODULES)
    parser.add_argument("--log-every-steps", type=int, default=5)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir or default_output_dir(args.model_id, args.revision)
    config = TrainConfig(
        base_model_dir=args.base_model_dir,
        model_id=args.model_id,
        revision=args.revision,
        train_split=args.train_split,
        val_split=args.val_split,
        output_dir=output_dir,
        seed=args.seed,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        batch_size=args.batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        max_train_examples=args.max_train_examples,
        max_length=args.max_length,
        lora_rank=args.lora_rank,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        target_modules=parse_target_modules(args.target_modules),
        log_every_steps=args.log_every_steps,
    )
    train(config)


if __name__ == "__main__":
    main()
