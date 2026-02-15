# Qwen3-TTS MLX Migration (Completed)

## Goal

Migrate flaming-horse voice generation from the legacy Qwen/PyTorch path to an MLX-backed path and validate the end-to-end video pipeline with real (non-mock) voice output.

## What Was Implemented

### 1) Voice service routing updated for MLX

- `flaming_horse_voice/__init__.py`
  - Changed `get_speech_service()` to use `service_factory` instead of directly instantiating `QwenCachedService`.
  - This enables runtime selection of `qwen` vs `mlx` via `FLAMING_HORSE_VOICE_SERVICE`.

- `flaming_horse_voice/service_factory.py`
  - Added explicit MLX-first behavior when `FLAMING_HORSE_VOICE_SERVICE=mlx`.
  - Prevented auto-fallback to mock when MLX is selected (MLX should synthesize on cache miss).

### 2) MLX cached speech service hardened

- `flaming_horse_voice/mlx_cached.py`
  - Updated `SERVICE_SCRIPT` to absolute module-adjacent path (`flaming_horse_voice/mlx_tts_service.py`).
  - Allowed startup with empty cache (no hard failure on missing `cache.json`).
  - Normalized subprocess output parsing: reads last non-empty line as JSON payload.
  - Added WAV -> MP3 conversion via `ffmpeg` before returning to `manim_voiceover_plus`.
    - `manim_voiceover_plus` uses mutagen MP3 duration parsing; this avoids `HeaderNotFoundError`.
  - Updated cache bookkeeping to store and serve `.mp3` files.
  - Set default MLX model for reliability during migration test:
    - `mlx-community/Qwen3-TTS-12Hz-0.6B-Base-4bit`
  - Updated MLX python path to the new Python 3.12 env:
    - `/Users/velocityworks/qwen3-tts-local/mlx_env312/bin/python`

### 3) MLX TTS subprocess service fixed for current mlx-audio behavior

- `flaming_horse_voice/mlx_tts_service.py`
  - Default model set to `0.6B-Base-4bit` for stable first-run availability.
  - Added output filename fallback logic:
    - Handles `seg_000.wav`, `seg.wav`, or first matching `seg*.wav`.
  - Retains hash-based cache naming.

### 4) Pipeline scripts updated to recognize MLX path

- `scripts/prepare_voice_service.py`
  - Added `prepare_mlx_service()`.
  - When `FLAMING_HORSE_VOICE_SERVICE=mlx`, writes:
    - `media/voiceovers/mlx/ready.json`
  - Keeps existing Qwen prepare path intact.

- `scripts/update_project_state.py`
  - `precache_voiceovers` now advances if **either**:
    - `media/voiceovers/qwen/cache.json` exists, or
    - `media/voiceovers/mlx/ready.json` exists.
  - Updated deterministic error messaging accordingly.

- `scripts/build_video.sh`
  - Exported repo-root `PYTHONPATH` early so generated scene files can import `flaming_horse_voice` when rendering from project directory.
  - `handle_precache_voiceovers()` now supports MLX path and writes MLX ready marker.
  - `handle_final_render()` now treats Qwen precache as required **only** for `qwen` service type.

## Environment Work Performed

Created a dedicated MLX Python 3.12 environment and installed required packages:

- Venv:
  - `/Users/velocityworks/qwen3-tts-local/mlx_env312`
- Installed:
  - `mlx-audio==0.3.1`
  - `mlx==0.30.6`
  - `transformers==5.0.0rc3`
  - `soundfile`, `scipy`, `sounddevice`, `numpy`, and transitive deps

Downloaded missing safetensors shards for the tested MLX model:

- `mlx-community/Qwen3-TTS-12Hz-0.6B-Base-4bit`

## Test Project and Validation

Project used:

- `/Users/velocityworks/IdeaProjects/flaming-horse-projects/test-mlx`

Scene rendering validated with MLX-backed audio generation and real audio stream.

Final assembled video:

- `/Users/velocityworks/IdeaProjects/flaming-horse-projects/test-mlx/media/test-mlx.mp4`

Verified streams:

- `video|92.816667`
- `audio|92.778000`

Generated voice cache entries (MP3):

- `/Users/velocityworks/IdeaProjects/flaming-horse-projects/test-mlx/media/voiceovers/qwen/*.mp3`

Note: the directory name `voiceovers/qwen` is legacy in the current pipeline and does not imply PyTorch generation; for this migration run, generation was performed by the MLX service.

## Commands Used (Key)

- End-to-end run (MLX):
  - `FLAMING_HORSE_VOICE_SERVICE=mlx ./scripts/create_video.sh test-mlx --topic "Create a short video performing speaking sounds check."`

- Direct scene render checks:
  - `FLAMING_HORSE_VOICE_SERVICE=mlx PYTHONPATH="<repo paths>" manim render scene_01.py Scene01Intro -qh`

- Final manual assembly for verified output:
  - `ffmpeg -f concat -safe 0 -i media/videos/concat_list.txt -c copy media/test-mlx.mp4`

## Current Status

Migration is functionally complete for flaming-horse MLX integration and validated with a real generated video including audio.

## Mediator Backend Flag (Step 2)

The pipeline workers now route synthesis through `scripts/qwen_tts_mediator.py`, which supports backend selection via:

- `FLAMING_HORSE_TTS_BACKEND=qwen` (default)
- `FLAMING_HORSE_TTS_BACKEND=mlx`

Optional MLX overrides:

- `FLAMING_HORSE_MLX_PYTHON` (default: `/Users/velocityworks/qwen3-tts-local/mlx_env312/bin/python`)
- `FLAMING_HORSE_MLX_MODEL_ID` (default: `mlx-community/Qwen3-TTS-12Hz-0.6B-Base-4bit`)
- `FLAMING_HORSE_MLX_SERVICE_SCRIPT` (default: repo `flaming_horse_voice/mlx_tts_service.py`)

If we want to finalize cleanup next, recommended follow-ups are:

1. Rename legacy `media/voiceovers/qwen` path to a neutral path (`voiceovers/primary` or `voiceovers/mlx`) to match runtime behavior.
2. Pin/lock the MLX env selection in project config to avoid accidental use of older Python envs.
3. Re-run one additional project (`matrix-multiplication`) as a regression pass under MLX.
