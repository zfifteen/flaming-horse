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

1. Install dependencies (system + Python): `docs/guides/INSTALLATION.md`
2. Verify environment: `./scripts/check_dependencies.sh`
3. Confirm `.env` contains required API settings for harness execution
4. Run `./scripts/create_video.sh <project_name> --topic "..."`

## Pipeline Phases

The orchestrator (`scripts/build_video.sh`) runs one phase at a time and advances deterministically:

`plan -> review -> narration -> training -> build_scenes -> scene_qc -> precache_voiceovers -> final_render -> assemble -> complete`

Notes:
- Projects created by `new_project.sh` start at `plan`.
- The loop pauses when `project_state.json.flags.needs_human_review` becomes `true`.

## Voice Policy (Mandatory)

Flaming Horse uses cached local Qwen voice clone audio only.

- Required model: `Qwen/Qwen3-TTS-12Hz-1.7B-Base`
- Required project config: `voice_clone_config.json`
- Required reference assets: `assets/voice_ref/ref.wav` and `assets/voice_ref/ref.txt`
- No fallback TTS services

See `docs/policies/VOICE_POLICY.md` for full policy.

## Installation and Environment

1. Install system + Python dependencies.
2. Ensure voice reference assets exist.
3. Verify prerequisites.

```bash
./scripts/check_dependencies.sh
```

Detailed setup: `docs/guides/INSTALLATION.md`

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

## Environment Variables Used

The following variables are present in `.env` and are actively used by the application/runtime scripts:

| Variable | Used by | Purpose |
| --- | --- | --- |
| `AGENT_MODEL` | `scripts/build_video.sh`, `harness/client.py` | Global fallback model selection for harness calls. |
| `PROJECTS_BASE_DIR` | `scripts/new_project.sh`, `scripts/create_video.sh`, `scripts/build_video.sh` | Default root directory for project creation/build paths. |
| `PROJECT_DEFAULT_NAME` | `scripts/build_video.sh` | Default project name when no project path is provided. |
| `PHASE_RETRY_LIMIT` | `scripts/build_video.sh` | Max retry attempts for phase/scene self-heal loops. |
| `PHASE_RETRY_BACKOFF_SECONDS` | `scripts/build_video.sh` | Sleep duration between retry attempts. |
| `HF_HUB_OFFLINE` | `scripts/build_video.sh`, `scripts/precache_voiceovers_qwen.py`, `scripts/prepare_qwen_voice.py` | Forces Hugging Face operations into offline mode. |
| `TRANSFORMERS_OFFLINE` | `scripts/build_video.sh`, `scripts/precache_voiceovers_qwen.py`, `scripts/prepare_qwen_voice.py` | Forces Transformers operations into offline mode. |
| `TOKENIZERS_PARALLELISM` | `scripts/build_video.sh`, `scripts/precache_voiceovers_qwen.py`, `scripts/prepare_qwen_voice.py` | Controls tokenizer parallelism behavior. |
| `PYTHON` | `scripts/create_video.sh`, `scripts/build_video.sh` | Python interpreter override (3.13 requirement checks and execution). |
| `PYTHON3` | `scripts/build_video.sh` | Secondary Python interpreter override fallback. |
| `PATH` | shell/runtime invocation of `manim`, `ffmpeg`, venv tools | Determines executable resolution during build and render steps. |
| `FLAMING_HORSE_TTS_BACKEND` | `scripts/prepare_voice_service.py`, `scripts/qwen_tts_mediator.py`, `scripts/precache_voiceovers_qwen*.py`, `scripts/prepare_qwen_voice*.py`, `scripts/build_video.sh` | Selects local cached TTS backend (`qwen` or `mlx`). |
| `FLAMING_HORSE_MLX_PYTHON` | `scripts/qwen_tts_mediator.py` | Python interpreter path for MLX TTS subprocess execution. |
| `FLAMING_HORSE_MLX_MODEL_ID` | `scripts/qwen_tts_mediator.py`, `scripts/prepare_qwen_voice.py` | Overrides MLX model identifier. |
| `FLAMING_HORSE_VOICE_REF_DIR` | `scripts/voice_ref_mediator.py`, `scripts/build_video.sh` | Overrides voice reference directory (`ref.wav`/`ref.txt`). |
| `LLM_PROVIDER` | `harness/client.py`, `scripts/build_video.sh` | Selects harness LLM provider (`XAI` or `MINIMAX`). |
| `XAI_API_KEY` | `harness/client.py`, `scripts/build_video.sh`, `scripts/check_dependencies.sh`, test scripts | xAI API authentication credential. |
| `MINIMAX_API_KEY` | `harness/client.py`, `scripts/build_video.sh` | MiniMax API authentication credential. |
| `XAI_BASE_URL` | `harness/client.py` | Optional xAI API endpoint override. |
| `MINIMAX_BASE_URL` | `harness/client.py` | Optional MiniMax API endpoint override. |
| `XAI_MODEL` | `harness/client.py` | Optional xAI model override. |
| `MINIMAX_MODEL` | `harness/client.py` | Optional MiniMax model override. |
