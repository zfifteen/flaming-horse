# Incremental Manim Video Builder

Agentic loop system for building Manim animations iteratively with synchronized voiceover.

## 🚨 CRITICAL: READ FIRST

**[VOICE SERVICE POLICY - MANDATORY READING →](docs/VOICE_POLICY.md)**

**TL;DR:** 
- ✅ ElevenLabs ONLY (voice ID: `rBgRd5IfS6iqrGfuhlKR`)
- ❌ NO gTTS, NO fallback, NO dev mode
- ⚠️ Violations = build failure

---

## Quick Start

```bash
cd ~/IdeaProjects/flaming-horse

# 1. Create a new project
./scripts/new_project.sh my_video

# 2. Configure agent in scripts/build_video.sh (edit invoke_agent function)

# 3. Run the build
./scripts/build_video.sh projects/my_video
```

## Project Structure

```
projects/my_video/
├── project_state.json       # State machine data
├── build.log                # Execution log
├── plan.json                # Generated video plan
├── narration_script.py      # Narration text
├── voice_config.py          # ElevenLabs settings
├── scenes/                  # Scene Python files
└── final_video.mp4          # Final output
```

## Project Organization

**Default Location**: Projects are created in `./projects/<project_name>/` relative to the repository root.

**Custom Location**: To use a different location:
```bash
./scripts/new_project.sh my_video /path/to/custom/location
./scripts/build_video.sh /path/to/custom/location/my_video
```

**Recommended structure**:
```
~/manim_projects/
├── gravity_anomalies/
├── calculus_intro/
└── physics_basics/
```

Create projects with:
```bash
./scripts/new_project.sh gravity_anomalies ~/manim_projects
./scripts/build_video.sh ~/manim_projects/gravity_anomalies
```

## State Machine Flow

```
init → plan → review → narration → build_scenes → final_render → assemble → complete
```

## Prerequisites

```bash
pip install manim manim-voiceover-plus
brew install sox ffmpeg
export ELEVENLABS_API_KEY="your_key"
```

## Helper Scripts

- `./scripts/new_project.sh <name> [location]` — Create new project
- `./scripts/reset_phase.sh <project_dir> <phase>` — Reset to specific phase
- `./scripts/validate_scaffold.sh` — Validate installation

**Note**: Projects must be created with `./scripts/new_project.sh` before running `./scripts/build_video.sh`. The `init` phase is not used in the build loop.

## Configuration

Edit `./scripts/build_video.sh` → `invoke_agent()` function to integrate your AI agent.

Voice: `rBgRd5IfS6iqrGfuhlKR` (ElevenLabs)
Model: `eleven_multilingual_v2`

See full documentation at the top of each script file.
