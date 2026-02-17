![Flaming Horse Banner](assets/flaming_horse_readme_banner.jpeg)

# Flaming Horse

Turn a topic into a polished narrated Manim video with a deterministic, production-minded pipeline.

What you get:
- End-to-end orchestration from topic to `final_video.mp4`
- Reliable phase progression with explicit state tracking in `project_state.json`
- Scene validation and QC passes before final assembly
- Cached local Qwen voice clone integration for consistent narration
- Retry/self-heal loops that pause only when human review is required

Built for:
- Math explainers and technical education videos
- Repeatable, scriptable video generation workflows
- Teams that want clear artifacts, logs, and recoverable state

## Quick Start

Start here for first-time setup and your first build:

```bash
# 1) Create a project (topic recommended at creation time)
./scripts/new_project.sh my_video --topic "Standing waves explained visually"

# 2) Build end-to-end
./scripts/build_video.sh projects/my_video

# Optional: set/override topic at build time
./scripts/build_video.sh projects/my_video --topic "Standing waves explained visually"
```

Final output:
- `projects/my_video/final_video.mp4`

## First-Run Checklist

1. Install dependencies (system + Python): `docs/INSTALLATION.md`
2. Verify environment: `./scripts/check_dependencies.sh`
3. Confirm `.env` contains required API settings for harness execution
4. Run `new_project.sh` with a topic
5. Run `build_video.sh` on that project

## Pipeline Phases

The orchestrator (`scripts/build_video.sh`) runs one phase at a time and advances deterministically:

`plan -> review -> narration -> build_scenes -> scene_qc -> precache_voiceovers -> final_render -> assemble -> complete`

Notes:
- Projects created by `new_project.sh` start at `plan`.
- The loop pauses when `project_state.json.flags.needs_human_review` becomes `true`.

## Voice Policy (Mandatory)

Flaming Horse uses cached local Qwen voice clone audio only.

- Required model: `Qwen/Qwen3-TTS-12Hz-1.7B-Base`
- Required project config: `voice_clone_config.json`
- Required reference assets: `assets/voice_ref/ref.wav` and `assets/voice_ref/ref.txt`
- No fallback TTS services

See `docs/VOICE_POLICY.md` for full policy.

## Installation and Environment

1. Install system + Python dependencies.
2. Ensure voice reference assets exist.
3. Verify prerequisites.

```bash
./scripts/check_dependencies.sh
```

Detailed setup: `docs/INSTALLATION.md`

## Configuration

### Agent/harness

The orchestrator calls the Python harness (`python3 -m harness`) for agent phases.
Configure behavior via environment variables (typically in `.env`):

- `XAI_API_KEY` (required by harness)
- `AGENT_MODEL` (default in orchestrator is `xai/grok-4-1-fast`)
- `AGENT_TEMPERATURE` (optional)

Harness details: `harness/README.md`

### Voice backend

Primary backend is Qwen cached voice.
The pipeline also recognizes `FLAMING_HORSE_TTS_BACKEND` for backend routing in current scripts.

## Project Structure

A generated project directory typically looks like:

```text
projects/my_video/
├── project_state.json
├── plan.json
├── narration_script.py
├── scene_01_intro.py
├── scene_02_*.py
├── scene_qc_report.md
├── build.log
├── errors.log
├── media/
│   └── voiceovers/
├── assets/
│   └── voice_ref/
│       ├── ref.wav
│       └── ref.txt
├── voice_clone_config.json
└── final_video.mp4
```

## Common Commands

```bash
# Validate environment
./scripts/check_dependencies.sh

# Precache voiceovers explicitly (optional; pipeline can invoke this phase)
python3 scripts/precache_voiceovers_qwen.py projects/my_video

# Reset project phase manually
./scripts/reset_phase.sh projects/my_video narration
```

## Documentation

- `AGENTS.md`
- `docs/reference_docs/phase_plan.md`
- `docs/reference_docs/phase_narration.md`
- `docs/reference_docs/phase_scenes.md`
- `docs/reference_docs/visual_helpers.md`
- `docs/reference_docs/topic_visual_patterns.md`
- `tests/README.md`

## License

MIT License.
