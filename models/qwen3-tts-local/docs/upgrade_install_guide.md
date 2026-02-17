# Qwen3-TTS MLX Upgrade Guide (Validated for Flaming Horse)

Last validated: 2026-02-16
Host: MacBookPro18,2 (M1 Max, 32 GB RAM)

This guide upgrades from:
- `mlx-community/Qwen3-TTS-12Hz-0.6B-Base-4bit`

to:
- `mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit`

This is MLX-only. No non-MLX fallback is used.

## 1. Required Paths

- Qwen local repo: `/Users/velocityworks/IdeaProjects/flaming-horse/models/qwen3-tts-local`
- MLX python: `/Users/velocityworks/IdeaProjects/flaming-horse/models/qwen3-tts-local/mlx_env312/bin/python`
- Flaming Horse repo: `/Users/velocityworks/IdeaProjects/flaming-horse`
- Voice reference set to use: `/Users/velocityworks/IdeaProjects/flaming-horse/assets/voice_ref_2`

## 2. Verify MLX Runtime

```bash
/Users/velocityworks/IdeaProjects/flaming-horse/models/qwen3-tts-local/mlx_env312/bin/python -c "import mlx.core as mx; print(mx.default_device())"
```

Expected output:
- `Device(gpu, 0)`

If this fails with Metal/NSRange errors, run outside restricted sandbox/containers.

## 3. Ensure Upgraded Model Is Cached

```bash
/Users/velocityworks/IdeaProjects/flaming-horse/models/qwen3-tts-local/mlx_env312/bin/python -m mlx_audio.tts.generate \
  --model mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit \
  --text "MLX model warmup check"
```

This pulls model files on first run.

Optional cache check:

```bash
ls -la ~/.cache/huggingface/hub/models--mlx-community--Qwen3-TTS-12Hz-1.7B-Base-8bit/snapshots
```

## 4. Flaming Horse Configuration

### 4.1 Environment (`.env`)

In `/Users/velocityworks/IdeaProjects/flaming-horse/.env`:

```bash
export FLAMING_HORSE_TTS_BACKEND=mlx
export FLAMING_HORSE_MLX_PYTHON=/Users/velocityworks/IdeaProjects/flaming-horse/models/qwen3-tts-local/mlx_env312/bin/python
export FLAMING_HORSE_MLX_MODEL_ID=mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit
export FLAMING_HORSE_VOICE_REF_DIR=/Users/velocityworks/IdeaProjects/flaming-horse/assets/voice_ref_2
```

### 4.2 Runtime Defaults Updated in Flaming Horse Code

These defaults should point to `1.7B-Base-8bit`:

- `scripts/qwen_tts_mediator.py`
- `scripts/prepare_qwen_voice.py`
- `flaming_horse_voice/mlx_cached.py`
- `flaming_horse_voice/mlx_tts_service.py`

## 5. Project Voice Config

For generated projects, set model + references in each `voice_clone_config.json`.

Validated working pattern:

```json
{
  "qwen_python": "~/IdeaProjects/flaming-horse/models/qwen3-tts-local/.venv/bin/python",
  "model_id": "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit",
  "device": "cpu",
  "dtype": "float32",
  "language": "English",
  "ref_audio": "../../assets/voice_ref_2/ref.wav",
  "ref_text": "../../assets/voice_ref_2/ref.txt",
  "output_dir": "media/voiceovers/qwen"
}
```

Notes:
- `qwen_python` remains required by current scripts, even with MLX backend.
- Actual MLX synthesis uses `FLAMING_HORSE_MLX_PYTHON` when backend is `mlx`.

## 6. End-to-End Validation (Flaming Horse)

From `/Users/velocityworks/IdeaProjects/flaming-horse`:

### 6.1 Warmup/prepare

```bash
FLAMING_HORSE_TTS_BACKEND=mlx \
FLAMING_HORSE_VOICE_REF_DIR=/Users/velocityworks/IdeaProjects/flaming-horse/assets/voice_ref_2 \
/Users/velocityworks/IdeaProjects/flaming-horse/models/qwen3-tts-local/.venv/bin/python scripts/prepare_qwen_voice.py \
  --project-dir generated/standing-waves --force
```

Expected signals:
- `Preparing voice backend: mlx`
- `Model: mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit`
- `Voice backend prepared (mlx)`

### 6.2 Precache narration

```bash
FLAMING_HORSE_TTS_BACKEND=mlx \
FLAMING_HORSE_VOICE_REF_DIR=/Users/velocityworks/IdeaProjects/flaming-horse/assets/voice_ref_2 \
/Users/velocityworks/IdeaProjects/flaming-horse/models/qwen3-tts-local/.venv/bin/python scripts/precache_voiceovers_qwen.py \
  generated/standing-waves
```

Expected result:
- Cache hit lines or generated mp3 entries
- Updated cache index under `media/voiceovers/qwen/cache.json`

### 6.3 Build

```bash
./scripts/build_video.sh generated/standing-waves
```

## 7. Known Warnings (Observed, Non-Blocking)

The following can appear and still succeed:
- tokenizer regex warning from Transformers/Mistral tokenizer logic
- model type warning from `mlx_audio`

These warnings did not block generation in the validated run.

## 8. Troubleshooting

### Crash: `NSRangeException` in MLX / Metal init

Cause:
- Running in restricted sandbox where Metal device is unavailable.

Fix:
- Run unsandboxed in normal macOS Terminal environment.
- Re-test with:

```bash
/Users/velocityworks/IdeaProjects/flaming-horse/models/qwen3-tts-local/mlx_env312/bin/python -c "import mlx.core as mx; print(mx.default_device())"
```

### `ModuleNotFoundError: voice_ref_mediator`

Cause:
- Running `prepare_qwen_voice.py` from a context where `scripts/` is not in `PYTHONPATH`.

Fix:
- Run from Flaming Horse repo root using the normal command shown in Section 6.

## 9. Summary of the Successful Upgrade

- Backend remains MLX-only.
- Model upgraded to `mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit`.
- Flaming Horse env and runtime defaults updated.
- Reference audio source standardized to `assets/voice_ref_2`.
- Prepare + precache + synthesis were validated successfully.
