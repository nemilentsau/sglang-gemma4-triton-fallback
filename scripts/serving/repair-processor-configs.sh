#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage:
  scripts/serving/repair-processor-configs.sh SOURCE_MODEL_DIR MERGED_MODEL_DIR

Copies Gemma VLM processor metadata into a merged model directory.

Required file:
  processor_config.json

Optional file, copied when present:
  preprocessor_config.json
EOF
}

SOURCE_MODEL_DIR="${1:-${SOURCE_MODEL_DIR:-}}"
MERGED_MODEL_DIR="${2:-${MERGED_MODEL_DIR:-}}"

if [[ -z "$SOURCE_MODEL_DIR" || -z "$MERGED_MODEL_DIR" ]]; then
  usage
  exit 2
fi

if [[ ! -d "$SOURCE_MODEL_DIR" ]]; then
  echo "Source model directory not found: $SOURCE_MODEL_DIR" >&2
  exit 1
fi

if [[ ! -d "$MERGED_MODEL_DIR" ]]; then
  echo "Merged model directory not found: $MERGED_MODEL_DIR" >&2
  exit 1
fi

required_files=(processor_config.json)
optional_files=(preprocessor_config.json)

for file in "${required_files[@]}"; do
  source_path="${SOURCE_MODEL_DIR}/${file}"
  if [[ ! -s "$source_path" ]]; then
    echo "Required processor config missing from source: $source_path" >&2
    exit 1
  fi
done

for file in "${required_files[@]}" "${optional_files[@]}"; do
  if [[ ! -e "${SOURCE_MODEL_DIR}/${file}" ]]; then
    continue
  fi
  cp "${SOURCE_MODEL_DIR}/${file}" "${MERGED_MODEL_DIR}/${file}"
done

for file in "${required_files[@]}"; do
  target_path="${MERGED_MODEL_DIR}/${file}"
  if [[ ! -s "$target_path" ]]; then
    echo "Processor config copy failed: $target_path" >&2
    exit 1
  fi
done

echo "Copied Gemma processor configs into: $MERGED_MODEL_DIR"
