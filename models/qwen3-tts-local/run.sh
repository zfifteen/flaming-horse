#!/usr/bin/env bash
set -euo pipefail

VENV_DIR="$(cd "$(dirname "$0")" && pwd)/.venv"
PY="$VENV_DIR/bin/python"

if [[ ! -x "$PY" ]]; then
  echo "Missing venv at $VENV_DIR" >&2
  echo "Recreate with: python3.12 -m venv $VENV_DIR" >&2
  exit 1
fi

# Reasonable defaults for Apple Silicon.
export PYTORCH_ENABLE_MPS_FALLBACK="${PYTORCH_ENABLE_MPS_FALLBACK:-1}"

# Model defaults: change per your needs.
export QWEN_TTS_MODEL="${QWEN_TTS_MODEL:-Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice}"
export QWEN_TTS_DEVICE="${QWEN_TTS_DEVICE:-mps}"

# MPS float16 can produce NaNs in sampling on some setups; bfloat16 is safer.
export QWEN_TTS_DTYPE="${QWEN_TTS_DTYPE:-bfloat16}"

# Keep generation bounded so smoke tests finish quickly.
export QWEN_TTS_MAX_NEW_TOKENS="${QWEN_TTS_MAX_NEW_TOKENS:-256}"

# Encourage stable, single-language output.
export QWEN_TTS_DO_SAMPLE="${QWEN_TTS_DO_SAMPLE:-0}"
export QWEN_TTS_TEMPERATURE="${QWEN_TTS_TEMPERATURE:-0.7}"
export QWEN_TTS_TOP_P="${QWEN_TTS_TOP_P:-0.9}"
export QWEN_TTS_REPETITION_PENALTY="${QWEN_TTS_REPETITION_PENALTY:-1.05}"
export QWEN_TTS_INSTRUCT="${QWEN_TTS_INSTRUCT:-Speak in clear English only. Do not switch languages.}"

"$PY" "$(cd "$(dirname "$0")" && pwd)/smoke_test_qwen3_tts.py"
