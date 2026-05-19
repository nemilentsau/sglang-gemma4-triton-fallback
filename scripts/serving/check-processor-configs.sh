#!/usr/bin/env bash
set -euo pipefail

MODEL_DIR="${1:-${MODEL_DIR:-}}"

if [[ -z "$MODEL_DIR" ]]; then
  echo "Usage: scripts/serving/check-processor-configs.sh MODEL_DIR" >&2
  exit 2
fi

if [[ ! -d "$MODEL_DIR" ]]; then
  echo "Model directory not found: $MODEL_DIR" >&2
  exit 1
fi

missing=0
for file in processor_config.json; do
  if [[ -s "${MODEL_DIR}/${file}" ]]; then
    echo "present: ${file}"
  else
    echo "missing: ${file}"
    missing=1
  fi
done

for file in preprocessor_config.json; do
  if [[ -s "${MODEL_DIR}/${file}" ]]; then
    echo "present optional: ${file}"
  else
    echo "missing optional: ${file}"
  fi
done

exit "$missing"
