# manim-voiceover Integration Guide

## Scope

This repository supports one voice path only:

- Local cached Qwen voice clone
- `Qwen/Qwen3-TTS-12Hz-1.7B-Base`
- CPU `float32`
- Project-local reference assets:
  - `assets/voice_ref/ref.wav`
  - `assets/voice_ref/ref.txt`

If cache is missing, fail the build and run the precache step.

## Mandatory Rules

- Use `manim_voiceover_plus` with `VoiceoverScene`.
- Use `flaming_horse_voice.get_speech_service(...)` for all scenes.
- Keep narration in `narration_script.py` and reference via `SCRIPT["key"]`.
- Keep duration sync based on `tracker.duration`.
- Do not add network TTS or fallback providers.
- Do not add optional alignment extras or cloud features.

## Minimal Scene Pattern

```python
from manim import *
from pathlib import Path
from manim_voiceover_plus import VoiceoverScene
from flaming_horse_voice import get_speech_service
from narration_script import SCRIPT

ref_path = Path("assets/voice_ref/ref.wav")
if not ref_path.exists():
    raise FileNotFoundError("Run precache_voice.sh before building.")

config.frame_height = 10
config.frame_width = 10 * 16/9
config.pixel_height = 1440
config.pixel_width = 2560

class Scene01Intro(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))
        with self.voiceover(text=SCRIPT["intro"]) as tracker:
            title = Text("Title", font_size=48).move_to(UP * 3.8)
            self.play(Write(title), run_time=min(1.5, tracker.duration * 0.2))
            self.wait(max(0.0, tracker.duration * 0.1))
```

## Precache Expectations

The precache step writes audio files and an index to:

- `media/voiceovers/qwen/`
- `media/voiceovers/qwen/cache.json`

Final render should start only after cache coverage is complete for all narration keys.

## Troubleshooting

- Missing `cache.json`: run the precache phase first.
- Missing audio for a narration key: regenerate cache for all keys in `SCRIPT`.
- Import error for voice service: verify `PYTHONPATH` includes repo root during render.
