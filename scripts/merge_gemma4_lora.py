from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from importlib import import_module
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class MergeConfig:
    base_model_dir: Path
    adapter_dir: Path
    output_dir: Path
    torch_dtype: str


def _load_deps() -> tuple[Any, Any, Any]:
    try:
        torch = import_module("torch")
        transformers = import_module("transformers")
        peft = import_module("peft")
    except ModuleNotFoundError as exc:
        raise SystemExit("Missing merge dependencies. Run: uv sync --extra train") from exc
    return torch, transformers, peft


def _auto_model_class(transformers: Any) -> Any:
    if hasattr(transformers, "AutoModelForImageTextToText"):
        return transformers.AutoModelForImageTextToText
    return transformers.AutoModelForCausalLM


def _torch_dtype(torch: Any, value: str) -> Any:
    if value == "auto":
        return "auto"
    try:
        return getattr(torch, value)
    except AttributeError as exc:
        raise ValueError(f"unknown torch dtype: {value}") from exc


def _copy_processor(transformers: Any, base_model_dir: Path, output_dir: Path) -> list[str]:
    copied: list[str] = []
    if hasattr(transformers, "AutoProcessor"):
        try:
            processor = transformers.AutoProcessor.from_pretrained(base_model_dir)
        except Exception:
            processor = None
        if processor is not None:
            processor.save_pretrained(output_dir)

    for name in ("preprocessor_config.json", "processor_config.json"):
        if (output_dir / name).is_file():
            copied.append(name)
    return copied


def merge(config: MergeConfig) -> None:
    torch, transformers, peft = _load_deps()
    model_cls = _auto_model_class(transformers)
    dtype = _torch_dtype(torch, config.torch_dtype)

    tokenizer = transformers.AutoTokenizer.from_pretrained(config.base_model_dir)
    model = model_cls.from_pretrained(
        config.base_model_dir,
        torch_dtype=dtype,
        device_map="auto",
    )
    model = peft.PeftModel.from_pretrained(model, config.adapter_dir)
    merged = model.merge_and_unload()

    config.output_dir.mkdir(parents=True, exist_ok=True)
    merged.save_pretrained(config.output_dir, safe_serialization=True)
    tokenizer.save_pretrained(config.output_dir)
    processor_files = _copy_processor(transformers, config.base_model_dir, config.output_dir)

    data = asdict(config)
    for key in ("base_model_dir", "adapter_dir", "output_dir"):
        data[key] = str(data[key])
    data["merged_at_utc"] = datetime.now(UTC).isoformat()
    data["processor_files"] = processor_files
    (config.output_dir / "merge-manifest.json").write_text(
        json.dumps(data, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    print(f"Saved merged model to {config.output_dir}")
    print(f"Processor files in merged artifact: {', '.join(processor_files) or 'none'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge a Gemma 4 PEFT LoRA adapter.")
    parser.add_argument("--base-model-dir", type=Path, required=True)
    parser.add_argument("--adapter-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--torch-dtype", default="auto")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    merge(
        MergeConfig(
            base_model_dir=args.base_model_dir,
            adapter_dir=args.adapter_dir,
            output_dir=args.output_dir,
            torch_dtype=args.torch_dtype,
        )
    )


if __name__ == "__main__":
    main()
