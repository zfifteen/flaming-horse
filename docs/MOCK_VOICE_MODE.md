# Mock Voice Mode

## Overview

Mock voice mode allows you to generate videos without setting up the Qwen voice cloning system. This is useful for:

- **Rapid Development**: Test scene animations without voice setup overhead
- **CI/CD Pipelines**: Run automated tests without model dependencies
- **Framework Development**: Work on video pipeline without voice infrastructure
- **Emergency Fallback**: Generate videos when voice services are temporarily unavailable

## Quick Start

### Enable Mock Mode

```bash
# Option 1: Environment variable (global)
export FLAMING_HORSE_MOCK_VOICE=1
./scripts/create_video.sh my_video --topic "Test video"

# Option 2: Command flag (per-invocation)
./scripts/create_video.sh my_video --topic "Test video" --mock

# Option 3: In code (programmatic)
from flaming_horse_voice.service_factory import get_speech_service
service = get_speech_service(project_dir, force_mock=True)
```

### What You Get

- **Silent Audio**: Dummy audio segments with duration based on text length (~2.5 words/second)
- **Full Pipeline**: Complete video generation from plan through final render
- **Same Structure**: Identical project structure and output format as real voice
- **Fast Iteration**: No model loading, no GPU/CPU inference delays

## Architecture

### Components

```
flaming_horse_voice/
├── qwen_cached.py      # Real voice service (requires Qwen setup)
├── qwen_mock.py        # Mock voice service (dummy audio)
└── service_factory.py  # Intelligent selection logic

scripts/
├── prepare_qwen_voice.py     # Real voice preparation
├── prepare_voice_service.py  # Unified preparation (auto-selects)
└── create_video.sh           # Entry point (respects mock mode)
```

### Selection Logic

The service factory automatically chooses between real and mock:

1. **Check `force_mock` parameter** (programmatic override)
2. **Check `FLAMING_HORSE_MOCK_VOICE` environment variable**
3. **Check availability** of Qwen cache and narration script
4. **Fallback to mock** if real service unavailable
5. **Return appropriate service instance**

### Audio Generation

Mock service generates silent audio using:

1. **Primary method**: Sox (if available)
   ```bash
   sox -n -r 48000 -c 1 output.mp3 trim 0.0 <duration>
   ```

2. **Fallback method**: FFmpeg
   ```bash
   ffmpeg -f lavfi -i anullsrc=r=48000:cl=mono -t <duration> output.mp3
   ```

3. **Last resort**: Empty file (pipeline continues)

### Duration Calculation

```python
word_count = len(text.split())
duration = max(0.5, word_count / 2.5)  # ~150 WPM reading speed
```

This ensures:
- Animations sync properly with "voice" timing
- Natural pacing (not too fast, not too slow)
- Minimum 0.5s for very short phrases

## Usage Examples

### Testing Scene Animations

```bash
# Create test project with mock voice
export FLAMING_HORSE_MOCK_VOICE=1
./scripts/new_project.sh test_scenes
cd projects/test_scenes

# Generate scene files (mock voice will be used automatically)
./scripts/build_video.sh .
```

### CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Test Video Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: pip install manim manim-voiceover-plus
      
      - name: Test video generation (mock voice)
        env:
          FLAMING_HORSE_MOCK_VOICE: 1
        run: |
          ./scripts/create_video.sh test_build \
            --topic "Test the video pipeline"
      
      - name: Verify output
        run: test -f projects/test_build/final_video.mp4
```

### Mixed Mode Development

```bash
# Develop with mock voice (fast iteration)
export FLAMING_HORSE_MOCK_VOICE=1
./scripts/build_video.sh projects/my_video

# Final render with real voice
unset FLAMING_HORSE_MOCK_VOICE
./scripts/build_video.sh projects/my_video --force
```

### Programmatic Usage

```python
from pathlib import Path
from flaming_horse_voice.service_factory import get_speech_service

project_dir = Path("projects/my_video")

# Auto-detect (respects environment + availability)
service = get_speech_service(project_dir)

# Force mock
service = get_speech_service(project_dir, force_mock=True)

# Force real
service = get_speech_service(project_dir, force_mock=False)

# Use in scene
audio = service.generate_from_text("Hello, world!")
print(audio["final_audio"])  # Path to generated MP3
```

## Limitations

### What Mock Mode **Does**

✅ Generate silent audio with proper duration
✅ Complete video pipeline execution
✅ Scene timing and synchronization
✅ Final MP4 assembly
✅ Identical project structure

### What Mock Mode **Doesn't Do**

❌ Generate actual speech/narration
❌ Voice cloning or personality
❌ Audio processing/effects
❌ Transcript alignment
❌ Phoneme boundaries

### When to Use Real Voice

- Final production renders
- Client/public presentations
- Testing voice-specific features
- Quality assurance
- Publishing to YouTube/social media

## Troubleshooting

### Mock Mode Not Activating

```bash
# Verify environment variable
echo $FLAMING_HORSE_MOCK_VOICE
# Should print: 1

# Check service selection
python3 -c "
import os
os.environ['FLAMING_HORSE_MOCK_VOICE'] = '1'
from flaming_horse_voice.service_factory import get_speech_service
service = get_speech_service('projects/test')
print(type(service).__name__)
"
# Should print: QwenMockService
```

### Audio Generation Fails

```bash
# Check if sox is installed
which sox
# If not: brew install sox (macOS) or apt install sox (Linux)

# Check if ffmpeg is installed
which ffmpeg
# If not: brew install ffmpeg (macOS) or apt install ffmpeg (Linux)

# Last resort: empty files are created, pipeline continues
```

### Video Has No Audio

This is **expected behavior** in mock mode. The audio tracks contain silence.

To add real voice:
```bash
unset FLAMING_HORSE_MOCK_VOICE
python3 scripts/precache_voiceovers_qwen.py projects/my_video
python3 scripts/build_video.sh projects/my_video
```

### Performance Still Slow

Mock mode only affects **voice generation**. Scene rendering (Manim) still takes time.

To speed up rendering:
```bash
# Lower quality for testing
manim render scene.py SceneClass -ql  # Low quality
manim render scene.py SceneClass -qm  # Medium quality

# Skip rendering, just check scene structure
python3 -c "from scene_01_intro import Scene01Intro; print('OK')"
```

## FAQ

**Q: Will my videos sound weird with mock voice?**
A: They will have **no narration** (silent audio). This is intentional for testing.

**Q: Can I mix real and mock in one project?**
A: No. Voice mode is set per build. Re-run with different mode to switch.

**Q: Does mock mode affect scene code?**
A: No. Scenes are identical. Only the audio generation backend changes.

**Q: Is mock mode as fast as real voice?**
A: Mock is **much faster** (no model loading, no inference). Ideal for iteration.

**Q: Can I use mock for production?**
A: Not recommended. Videos will have no narration. Use real voice for final output.

**Q: What if I forget to disable mock mode?**
A: You'll get silent videos. Always verify audio before publishing.

**Q: How do I permanently disable mock mode?**
```bash
unset FLAMING_HORSE_MOCK_VOICE
# Or remove from ~/.bashrc, ~/.zshrc, etc.
```

## Integration with Existing Projects

Mock mode works seamlessly with existing projects:

```bash
# Existing project with real voice cache
ls projects/my_video/media/voiceovers/qwen/
# cache.json  narration_01.mp3  narration_02.mp3  ...

# Run with mock (ignores existing cache)
export FLAMING_HORSE_MOCK_VOICE=1
./scripts/build_video.sh projects/my_video

# New mock audio generated in same directory
ls projects/my_video/media/voiceovers/qwen/
# cache.json  narration_01.mp3  mock_abc123.mp3  mock_def456.mp3  ...
```

Mock files are named `mock_<hash>.mp3` to avoid conflicts.

## Contributing

To extend mock voice functionality:

1. **Add new audio generation method**: Edit `flaming_horse_voice/qwen_mock.py`
2. **Modify selection logic**: Edit `flaming_horse_voice/service_factory.py`
3. **Update tests**: Add test cases for new behavior
4. **Document changes**: Update this file

## See Also

- [Voice Service Policy](VOICE_POLICY.md) - Real voice configuration
- [Manim Voiceover Guide](../reference_docs/manim_voiceover.md) - Integration details
- [Build Pipeline](../AGENTS.md) - Full build workflow
