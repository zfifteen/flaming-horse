# Voice Contract

Audience: Local coding agents working on voice preparation, voice caching, Manim voiceover service integration, and final render.

Purpose: Define the current local cached voice path used by pipeline scenes.

## Voice Policy

Pipeline scenes must use local cached voice audio.

They must not introduce:

1. gTTS.
2. Azure TTS.
3. OpenAI TTS.
4. pyttsx3.
5. Network TTS fallback services.
6. Development-mode placeholder voice paths.

Missing required cached audio should fail with an actionable error.

## Current Runtime Components

Voice setup and synthesis path:

1. `scripts/new_project.sh` writes `voice_clone_config.json`.
2. `scripts/new_project.sh` copies `assets/voice_ref/ref.wav` and `assets/voice_ref/ref.txt`.
3. `scripts/create_video.sh` calls `scripts/prepare_voice_service.py`.
4. `scripts/prepare_voice_service.py` calls `scripts/prepare_qwen_voice.py`.
5. `scripts/precache_voiceovers_qwen.py` generates cached narration audio.
6. `flaming_horse_voice/service_factory.py` returns the render-time cached speech service.
7. `scene_*.py` calls `get_speech_service(Path(__file__).resolve().parent)`.

Voice reference resolution is owned by:

```text
scripts/voice_ref_mediator.py
```

## Backend Selection

Current mainline contains both Qwen and MLX-related code.

The default project config produced by `scripts/new_project.sh` is Qwen-shaped:

```json
{
  "qwen_python": "...",
  "model_id": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
  "device": "cpu",
  "dtype": "float32",
  "output_dir": "media/voiceovers/qwen"
}
```

`scripts/qwen_tts_mediator.py` can route generation through:

```text
FLAMING_HORSE_TTS_BACKEND=qwen
FLAMING_HORSE_TTS_BACKEND=mlx
```

Do not infer a completed backend migration from the presence of MLX files alone. Verify the active runtime path before changing voice behavior.

## Cache Path

The current state-transition and render path expects:

```text
projects/<project_name>/media/voiceovers/qwen/cache.json
```

Scene audio is expected at:

```text
projects/<project_name>/media/voiceovers/qwen/<scene_id>.mp3
```

This path name may be legacy when MLX generation is selected through the mediator. Treat path naming and backend selection as separate facts unless the code has been changed to unify them.

## Render-Time Service

Scaffolded scenes use:

```python
from flaming_horse_voice import get_speech_service
self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))
```

The speech service must resolve cached audio by narration key or exact normalized narration text. It must not silently synthesize from an external network service during render.

## Final Render And QC

`scripts/build_video.sh` ensures voice cache availability before runtime validation and final render.

`scripts/qc_final_video.sh` checks:

1. Final video exists.
2. Final video has audio.
3. Audio/video duration ratio.
4. Silent gaps.
5. Per-scene audio ratio.

QC failure may route the project back to `build_scenes`.

## Execution-Relevant Drift

If this document diverges from `scripts/new_project.sh`, `scripts/prepare_voice_service.py`, `scripts/precache_voiceovers_qwen.py`, `scripts/qwen_tts_mediator.py`, `flaming_horse_voice/service_factory.py`, or `scripts/build_video.sh`, runtime code wins for current behavior. Stop and ask before changing execution based on the document.
