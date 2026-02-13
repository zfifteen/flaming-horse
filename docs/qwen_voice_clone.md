# Qwen Voice Clone Workflow

This repo uses local Qwen3 voice cloning. There are **no network TTS calls**. All narration audio is generated locally and cached before rendering.

## Setup (per project)

1) Place your reference assets:

- `projects/<project>/assets/voice_ref/ref.wav`
- `projects/<project>/assets/voice_ref/ref.txt`

`ref.txt` must match the spoken words in `ref.wav`.

2) Check `projects/<project>/voice_clone_config.json`

Defaults:

```json
{
  "qwen_python": "~/qwen3-tts-local/.venv/bin/python",
  "model_id": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
  "device": "cpu",
  "dtype": "float32",
  "language": "English",
  "ref_audio": "assets/voice_ref/ref.wav",
  "ref_text": "assets/voice_ref/ref.txt",
  "output_dir": "media/voiceovers/qwen"
}
```

## Precache audio

Run once per project (or after changing narration):

```bash
python3 scripts/precache_voiceovers_qwen.py projects/<project>
```

This writes:

- `projects/<project>/media/voiceovers/qwen/*.wav`
- `projects/<project>/media/voiceovers/qwen/cache.json`

If any file is missing during render, the build fails and tells you to run the precache step.

## Render

```bash
./scripts/build_video.sh projects/<project>
```

The renderer will use cached audio only. No network keys required.
