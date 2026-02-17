# qwen3-tts-local

Local MLX-based Qwen3-TTS runtime used by Flaming Horse.

This directory is the local TTS backend workspace. It is responsible for model loading, voice-clone synthesis, and helper scripts for testing/experiments.

## Current Production Target

- Runtime: MLX on Apple Silicon
- Primary model: `mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit`
- Python env for MLX runtime: `/Users/velocityworks/IdeaProjects/flaming-horse/models/qwen3-tts-local/mlx_env312/bin/python`
- Reference voice used by Flaming Horse: `/Users/velocityworks/IdeaProjects/flaming-horse/assets/voice_ref_2`

## Directory Overview

- `docs/`
  - Guides and migration notes.
  - See `docs/upgrade_install_guide.md` for the validated upgrade runbook.

- `mlx_env312/`
  - Main MLX virtual environment used for production runs.

- `mlx_env/`
  - Older MLX environment (legacy).

- `.venv/`
  - General Python environment used by some helper scripts.

- `mlx_tts_service.py`
  - Main subprocess service script that generates audio via MLX.
  - Accepts JSON segments and model id, returns output paths/durations.

- `generate_long_clone.py`
  - Long-form helper that calls `mlx_tts_service.py`.

- `generate_long_audio.py`, `voice_clone_from_ref.py`
  - Additional experimentation/utility scripts.

- `run.sh`
  - Convenience launcher for local tests.

- `voice_ref/` and `ref/`
  - Local reference samples for stand-alone script usage.

- `outputs/`, `mlx_outputs/`
  - Generated audio artifacts from local runs.

## How Flaming Horse Uses This Directory

Flaming Horse points at this repo through environment variables:

- `FLAMING_HORSE_TTS_BACKEND=mlx`
- `FLAMING_HORSE_MLX_PYTHON=/Users/velocityworks/IdeaProjects/flaming-horse/models/qwen3-tts-local/mlx_env312/bin/python`
- `FLAMING_HORSE_MLX_MODEL_ID=mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit`

Flaming Horse resolves reference audio via:

- `FLAMING_HORSE_VOICE_REF_DIR=/Users/velocityworks/IdeaProjects/flaming-horse/assets/voice_ref_2`

## Quick Verification

### 1) Verify MLX GPU device

```bash
/Users/velocityworks/IdeaProjects/flaming-horse/models/qwen3-tts-local/mlx_env312/bin/python -c "import mlx.core as mx; print(mx.default_device())"
```

Expected:

- `Device(gpu, 0)`

### 2) Warm model with a short generation

```bash
/Users/velocityworks/IdeaProjects/flaming-horse/models/qwen3-tts-local/mlx_env312/bin/python -m mlx_audio.tts.generate \
  --model mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit \
  --text "MLX warmup check"
```

### 3) Service-level test from Flaming Horse root

```bash
cd /Users/velocityworks/IdeaProjects/flaming-horse
MLX_REF_AUDIO=/Users/velocityworks/IdeaProjects/flaming-horse/assets/voice_ref_2/ref.wav \
MLX_OUTPUT_DIR=/Users/velocityworks/IdeaProjects/flaming-horse/generated/standing-waves/media/voiceovers/mlx_tmp \
/Users/velocityworks/IdeaProjects/flaming-horse/models/qwen3-tts-local/mlx_env312/bin/python flaming_horse_voice/mlx_tts_service.py \
  '[{"id":"smoke","text":"MLX service smoke test"}]' \
  mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit
```

## Notes

- This runtime should be executed in a normal macOS environment with Metal available.
- In restricted sandboxes/containers, MLX may fail during Metal initialization.
