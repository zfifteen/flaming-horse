![Flaming Horse Banner](assets/flaming_horse_readme_banner.jpeg)

# Flaming Horse

**Transform ideas into professional math videos with a single prompt.**

Flaming Horse is an AI-powered video production system that generates complete Manim animations with synchronized professional voiceovers. Describe your concept, and watch as it builds publication-ready mathematical visualizations automatically.

## Why Flaming Horse?

### From Concept to Video in Minutes

Skip the tedious coding. Provide a description or mathematical concept, and Flaming Horse handles scene composition, animation sequencing, narration scripting, and voice synthesis.

### Professional Quality Output

- **Studio-grade voiceovers** powered by cached Qwen voice clones
- **Manim-native animations** with full mathematical typesetting
- **Multi-scene orchestration** with intelligent pacing and transitions
- **Production-ready exports** suitable for YouTube, courses, and presentations


### Built for Math Communicators

Whether you're an educator creating course content, a researcher presenting findings, or a content creator explaining complex topics, Flaming Horse eliminates the production bottleneck between your ideas and your audience.

## Quick Start

```bash
# Create your first project
./scripts/new_project.sh my_video

# Build from a prompt (configure your AI agent in build_video.sh)
./scripts/build_video.sh projects/my_video

# (Optional) Scaffold a new scene file before adding animations
./scripts/scaffold_scene.py \
  --project projects/my_video \
  --scene-id scene_01_intro \
  --class-name Scene01Intro \
  --narration-key intro
```

Your video appears in `projects/my_video/final_video.mp4`.

## How It Works

Flaming Horse uses an intelligent agentic workflow to decompose your concept into:

1. **Video plan** with scene breakdown and timing
2. **Narration script** synchronized to visual elements
3. **Scene generation** with Manim code for each segment
4. **Voice synthesis** with cached Qwen narration
5. **Final assembly** into a polished video

The system iterates until each component meets quality standards, then assembles everything into your final video.

## Installation

```bash
# Install dependencies
pip install manim manim-voiceover-plus
brew install sox ffmpeg

# Precache Qwen voiceovers
python3 scripts/precache_voiceovers_qwen.py projects/my_video
```

**Voice Requirements:** Flaming Horse uses cached Qwen voice clones configured via `voice_clone_config.json`. Run the precache step before building.

## Environment Setup

Before your first build:

```bash
# 1. Check dependencies
./scripts/check_dependencies.sh

# 2. Set up voice reference (one-time)
# Record a 5-10 second voice sample and place:
# - assets/voice_ref/ref.wav (audio file)
# - assets/voice_ref/ref.txt (transcript of audio)

# 3. Test Qwen model access
python3 -c "from scripts.qwen_tts_mediator import load_model; load_model()"
```

For detailed installation instructions, see [docs/INSTALLATION.md](docs/INSTALLATION.md).

## Configuration

Edit `./scripts/build_video.sh` to connect your preferred AI agent (Claude, GPT-4, Gemini, etc.) in the `invoke_agent()` function. The agent receives context about the current build phase and returns the appropriate output.

## Project Structure

Projects are self-contained and portable:

```
projects/my_video/
├── final_video.mp4          # Your finished video
├── plan.json                # Scene breakdown
├── narration_script.py      # Voice script
├── scenes/                  # Generated Manim code
└── project_state.json       # Build state
```


## Use Cases

- **Educational Content**: Lecture supplements, online courses, tutorial series
- **Research Communication**: Paper visualizations, conference presentations
- **Content Creation**: YouTube explainers, social media educational content
- **Corporate Training**: Technical onboarding, concept explanations


## Advanced Features

- **Custom project locations** for organizing video libraries
- **Phase reset capability** for iterative refinement
- **State machine persistence** for reliable long-running builds
- **Extensible agent integration** supporting any LLM provider


## Documentation

- [Voice Service Policy](docs/VOICE_POLICY.md) - Audio configuration details
- Script documentation - See inline comments in `./scripts/` directory


## Requirements

- Python 3.8+
- Manim Community Edition
- FFmpeg and Sox
- Cached Qwen voice clone assets


## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! This is an open-source project under active development. Feel free to submit issues, feature requests, or pull requests.

***

**Ready to create your first math video?** Start with `./scripts/new_project.sh` and bring your concepts to life.

***
