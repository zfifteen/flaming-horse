# Qwen3-TTS MLX Migration

## Current Status

The voice pipeline now supports MLX generation through the normal user-facing entrypoint:

```bash
./scripts/create_video.sh <project_name> --topic "..."
```

The active backend flag is:

```bash
FLAMING_HORSE_TTS_BACKEND=mlx
```

Do not use the older `FLAMING_HORSE_VOICE_SERVICE=mlx` migration path. Do not manually assemble videos as a substitute for the scripted pipeline.

## Expected macOS Configuration

The local MLX path uses an explicit Python environment with MLX audio dependencies:

```bash
FLAMING_HORSE_TTS_BACKEND=mlx
FLAMING_HORSE_MLX_PYTHON=/absolute/path/to/python-with-mlx-audio
FLAMING_HORSE_MLX_MODEL_ID=mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit
HF_HUB_OFFLINE=1
TRANSFORMERS_OFFLINE=1
```

`scripts/create_video.sh` sources `.env` with exported environment semantics before calling child scripts, so these values are visible to project creation, voice preparation, voice precaching, render, and assembly.

## Runtime Shape

Project creation writes a backend-aware `voice_clone_config.json`:

```json
{
  "backend": "mlx",
  "worker_python": "/absolute/path/to/python-with-mlx-audio",
  "model_id": "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit",
  "output_dir": "media/voiceovers/qwen"
}
```

The `media/voiceovers/qwen` directory name is a legacy compatibility surface. Under MLX, it does not mean PyTorch Qwen generation. Legacy-imported configs may still contain `qwen_python`, but new MLX project configs do not synthesize it. The MLX worker writes the same `cache.json` and MP3 files expected by the strict cached render-time service.

Render-time scene audio remains cache-only. The service factory returns the strict cached service for both `qwen` and `mlx`; it does not synthesize during Manim rendering and does not fall back to another backend.

## Validation Snapshot

Normal-entrypoint smoke run:

```bash
./scripts/create_video.sh prime_numbers_mlx_smoke --topic "Prime numbers"
```

Confirmed through the scripted pipeline:

- MLX voice preparation loaded the configured backend and model.
- Voice precache generated `ready.json`, `cache.json`, and seven MP3 files under `media/voiceovers/qwen`.
- Final render consumed cached MLX-generated MP3 files.
- Assembly produced `generated/prime_numbers_mlx_smoke/final_video.mp4`.
- `ffprobe` reported H.264 video and AAC audio streams, both about 250.6 seconds.

The smoke run did not complete as a successful pipeline run because final QC detected a scene-level audio/video timing issue and rerouted to `build_scenes`. The subsequent scene repair loop produced truncated `SceneRepairResponse` JSON and was manually interrupted after a long API wait. That failure is in scene generation and repair behavior, not in MLX voice integration.

## Focused Checks

Current focused checks:

```bash
python3 -m py_compile scripts/tts_backend_config.py scripts/prepare_voice_service.py scripts/prepare_qwen_voice.py scripts/precache_voiceovers_qwen.py scripts/qwen_tts_mediator.py scripts/qwen_pipeline_preflight.py flaming_horse_voice/service_factory.py flaming_horse_voice/qwen_cached.py flaming_horse_voice/mlx_tts_service.py scripts/prepare_qwen_voice_worker.py
python3 scripts/test_tts_backend_config.py
python3 scripts/test_qwen_cached_service.py
python3 scripts/test_update_project_state.py
```

## Remaining Cleanup

The main naming debt is the legacy `qwen` cache path. Rename it only with a coordinated state-machine and render-time cache migration. Until then, treat the path as a compatibility directory, not as backend ownership.
