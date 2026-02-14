# Setting Up Qwen3 TTS for Real Voice Synthesis

## Quick Start (Mock Mode)

If you just want to test the video pipeline without real voice synthesis, you don't need to do anything. The precache script will automatically detect the missing Qwen environment and generate silent audio files.

## Setting Up Real Qwen Voice Clone

To use actual voice synthesis with the Qwen3 TTS model, follow these steps:

### 1. Create a Python Environment

```bash
# Create a directory for Qwen setup
mkdir -p ~/qwen3-tts-local
cd ~/qwen3-tts-local

# Create a virtual environment
python3 -m venv .venv

# Activate the environment
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
# Activate the virtual environment
source ~/qwen3-tts-local/.venv/bin/activate

# Install required packages
pip install torch transformers soundfile

# Install qwen_tts package
# TODO: The qwen-tts package may not be publicly available yet.
# Check Hugging Face documentation or use the official installation method:
# pip install git+https://github.com/QwenLM/qwen-tts.git
pip install qwen-tts
```

### 3. Verify Installation

```bash
# Test that qwen_tts can be imported
~/qwen3-tts-local/.venv/bin/python -c "import qwen_tts; print('✓ qwen_tts installed')"
```

### 4. Download the Model

The model will be automatically downloaded from Hugging Face on first use. To pre-download:

```bash
~/qwen3-tts-local/.venv/bin/python -c "
from qwen_tts import Qwen3TTSModel
print('Downloading model...')
model = Qwen3TTSModel.from_pretrained(
    'Qwen/Qwen3-TTS-12Hz-1.7B-Base',
    device_map='cpu',
)
print('✓ Model downloaded successfully')
"
```

This will download ~1.7GB to `~/.cache/huggingface/hub/`.

### 5. Verify Configuration

Check that your project's `voice_clone_config.json` points to the correct Python:

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

### 6. Test Voice Generation

```bash
python3 scripts/precache_voiceovers_qwen.py projects/<your-project>
```

If successful, you should see:
```
→ Loading Qwen model
✓ Loaded model in X.Xs
→ Building voice clone prompt
✓ Prompt built in X.Xs
✓ Generated intro (X.XXs) in X.Xs
...
✓ Updated cache index: <path>/cache.json
```

## Troubleshooting

### "Qwen Python environment unavailable"

This means one of:
- The Python path in `voice_clone_config.json` doesn't exist
- The Python environment can't import `qwen_tts`
- The `qwen_python` field is missing from config

The script will automatically fall back to mock mode (silent audio).

### Model Download Hangs

If the model download hangs or fails:
1. Check your internet connection
2. Verify Hugging Face is accessible
3. Try downloading manually with the script above
4. Check disk space (~2GB needed)

### Out of Memory

If you get OOM errors:
- Ensure `device` is set to `"cpu"` in config
- Ensure `dtype` is set to `"float32"` (not float16 or bfloat16)
- Close other applications to free RAM
- The model needs ~4GB RAM minimum

## Mock Mode vs Real Voice

| Feature | Mock Mode | Real Voice |
|---------|-----------|------------|
| Setup Required | None | Qwen environment + model download |
| Generation Time | ~1s per narration | ~5-10s per narration |
| Audio Quality | Silent | Synthesized speech |
| Disk Space | ~1-2MB per narration | ~100-500KB per narration |
| Use Case | Testing, development | Production videos |

## Reference

- Model: [Qwen/Qwen3-TTS-12Hz-1.7B-Base](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base)
- Size: ~1.7GB
- License: Check Hugging Face model card
