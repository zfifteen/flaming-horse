# Installation Guide

## Prerequisites

- Python 3.8 or higher
- 8GB+ RAM (16GB recommended for Qwen model)
- FFmpeg and Sox for media processing
- LaTeX (for mathematical typesetting)

## Step 1: System Dependencies

### macOS
```bash
brew install ffmpeg sox
brew install --cask mactex-no-gui
```

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install ffmpeg sox texlive-latex-base texlive-fonts-recommended
```

## Step 2: Python Packages

```bash
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist, install manually:
```bash
pip install manim manim-voiceover-plus transformers torch
```

## Step 3: Voice Reference Assets

Create voice reference for Qwen voice cloning:

```bash
mkdir -p assets/voice_ref
```

1. Record a 5-10 second voice sample (clear audio, minimal background noise)
2. Save as `assets/voice_ref/ref.wav` (16kHz mono WAV preferred)
3. Create `assets/voice_ref/ref.txt` with exact transcript of the audio

Example `ref.txt`:
```
Hello, this is my voice sample for video narration. The quality matters.
```

## Step 4: Qwen Model Download

First run will download the Qwen TTS model (~3GB):

```bash
python3 -c "from scripts.qwen_tts_mediator import load_model; load_model()"
```

Model will be cached in `~/.cache/huggingface/`.

## Step 5: Verify Installation

```bash
./scripts/check_dependencies.sh
```

All checks should pass (✓) before creating videos.

## Troubleshooting

**Issue:** Manim import errors
- **Fix:** Ensure `manim` package installed, not `manimlib` (different project)

**Issue:** LaTeX rendering fails
- **Fix:** Install full LaTeX distribution (mactex or texlive-full)

**Issue:** Qwen model download fails
- **Fix:** Check internet connection, disk space (need 5GB free)

**Issue:** Voice reference not found
- **Fix:** Verify `assets/voice_ref/ref.wav` and `ref.txt` exist and are readable
