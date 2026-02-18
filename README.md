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
# Canonical user entrypoint (create/resume + full build):
./scripts/create_video.sh my_video --topic "Standing waves explained visually"
```

Final output:
- `projects/my_video/final_video.mp4`

Advanced/manual flow (optional):

```bash
./scripts/new_project.sh my_video --topic "Standing waves explained visually"
./scripts/build_video.sh projects/my_video
```

## First-Run Checklist

1. Install dependencies (system + Python): `docs/INSTALLATION.md`
2. Verify environment: `./scripts/check_dependencies.sh`
3. Confirm `.env` contains required API settings for harness execution
4. Run `./scripts/create_video.sh <project_name> --topic "..."`

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

**LLM Provider Configuration:**
- `LLM_PROVIDER` - Provider name (XAI or MINIMAX)
- `{PROVIDER}_API_KEY` - Provider-specific API key
- `{PROVIDER}_BASE_URL` - Provider-specific endpoint (optional)
- `{PROVIDER}_MODEL` - Provider-specific model (optional)

See `.env.example` for full configuration.

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
# Canonical user entrypoint (recommended)
./scripts/create_video.sh my_video --topic "Standing waves explained visually"

# Validate environment
./scripts/check_dependencies.sh

# Precache voiceovers explicitly (optional; pipeline can invoke this phase)
python3 scripts/precache_voiceovers_qwen.py projects/my_video

# Manual phase reset (advanced)
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
