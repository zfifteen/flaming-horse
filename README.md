# Flaming Horse

A bash-driven compiler pipeline that transforms a single text prompt into a fully rendered, narrated Manim video — no manual coding, no approval loops, no intervention required.

## What This Actually Does

Flaming Horse is not a prompt wrapper. It is a state-machine orchestrator (`build_video.sh`) that drives an AI agent through a seven-phase production pipeline:

```
plan → review → narration → build_scenes → final_render → assemble → complete
```

Each phase generates concrete artifacts. The orchestrator validates them, catches errors, and advances — or retries — automatically. The output is `final_video.mp4` with synchronized ElevenLabs voiceover.

## Two Commands. One Video.

```bash
# Create a new project
./scripts/new_project.sh my_video

# Build from prompt (agent runs autonomously to completion)
./scripts/build_video.sh projects/my_video
```

That's it. The agent reads `AGENTS.md` (a 700-line system prompt), receives all reference documentation, and executes each phase until `final_video.mp4` is produced or an error triggers the `needs_human_review` flag.

## How the Pipeline Works

### Phase 1: `plan`
Analyzes the topic, breaks it into 3–8 scenes, estimates narration word counts at 150 wpm, and flags animation complexity. Outputs `plan.json`.

### Phase 2: `review`
Validates the plan for technical feasibility — checks narrative flow, flags unsupported Manim features, verifies timing allows for both narration and animation.

### Phase 3: `narration`
Generates `narration_script.py` (a segment-indexed `SCRIPT` dictionary) and `voice_config.py` with locked ElevenLabs settings. Voice ID is hardcoded to a specific cloned voice.

### Phase 4: `build_scenes`
Generates Manim scene files one at a time using `scaffold_scene.py`. Each scene passes through two validation gates before advancing:
- **Import validation** — catches common module naming errors (`manim_voiceover_plus` vs hyphens/no separators)
- **Voiceover sync validation** — rejects hardcoded narration text, enforces `SCRIPT` dictionary usage

### Phase 5: `final_render`
Renders each scene with `manim render` at 1440p60. Mandatory verification checks: file exists, non-zero size, duration within 5% of estimate, audio track present.

### Phase 6: `assemble`
Concatenates scenes via `ffmpeg` using auto-generated `scenes.txt`. Runs `qc_final_video.sh` for quality control. Verifies total duration matches sum of scene durations.

### Phase 7: `complete`
Confirms `final_video.mp4` exists and logs completion.

## What Makes This Different from Prompting an LLM Directly

A single LLM prompt cannot:

- Orchestrate a multi-phase state machine with persistent `project_state.json`
- Validate imports against known-broken patterns before rendering
- Enforce voiceover sync rules (no hardcoded narration, timing budget ≤ 1.0)
- Execute `manim render` and verify output files actually exist with audio
- Call ElevenLabs with a locked voice configuration
- Concatenate scenes with `ffmpeg` and run QC on the assembled output
- Retry on failure with error logging and state backup/restore
- Halt with `needs_human_review` when errors exceed retry capacity

`build_video.sh` does all of this in a loop with up to 50 iterations, lock file management, and trap-based cleanup.

## Architecture

```
flaming-horse/
├── AGENTS.md                    # 700-line agent system prompt (v2.1)
├── scripts/
│   ├── build_video.sh           # Main orchestrator (527 lines)
│   ├── new_project.sh           # Project scaffolding
│   ├── scaffold_scene.py        # Scene file generator
│   ├── generate_scenes_txt.py   # Automated ffmpeg concat file builder
│   ├── qc_final_video.sh        # Post-assembly quality control
│   ├── reset_phase.sh           # Phase reset utility
│   ├── validate_scaffold.sh     # Scaffold validation
│   ├── test_scaffold_scene.py   # Tests
│   └── test_generate_scenes_txt.py
├── reference_docs/
│   ├── manim_config_guide.md    # Positioning rules, safe zones, 1440p config
│   ├── manim_content_pipeline.md # 5-stage content pipeline reference
│   ├── manim_voiceover.md       # ElevenLabs integration patterns
│   └── manim_template.py.txt    # Locked scene template
├── projects/                    # Self-contained video projects (12 and counting)
├── concepts/                    # Research concept documents
├── example_project/             # Template with example artifacts
└── docs/
```

## Agent Configuration

The agent is pre-configured in `invoke_agent()` inside `build_video.sh`. It shells out to:

```bash
opencode run --model "xai/grok-code-fast-1" \
  --file "$prompt_file" \
  --file "reference_docs/manim_content_pipeline.md" \
  --file "reference_docs/manim_voiceover.md" \
  --file "reference_docs/manim_template.py.txt" \
  --file "reference_docs/manim_config_guide.md" \
  --file "$STATE_FILE" \
  -- "Read the first attached file... Execute the ${phase} phase as described."
```

The agent receives the full system prompt (`AGENTS.md`), all four reference documents, the current project directory listing, and `project_state.json` — every invocation. There is nothing for the user to configure.

To swap the underlying model, change one line in `invoke_agent()`. The rest of the pipeline is model-agnostic.

## Technical Details

### Locked Configuration
All scenes render at 2560×1440 (1440p) with a 10×17.78 Manim frame (25% larger than default). These values are locked in every scene template and cannot be modified by the agent.

### Voice Configuration
- **Service**: ElevenLabs only — no fallback, no dev mode
- **Voice ID**: `rBgRd5IfS6iqrGfuhlKR` (cloned voice)
- **Model**: `eleven_multilingual_v2`
- If ElevenLabs fails, the build fails. This is intentional.

### Validation Gates
- `validate_scene_imports()` — static analysis for module naming errors + Python syntax check
- `validate_voiceover_sync()` — rejects hardcoded narration, checks for `tracker.duration` usage, verifies ElevenLabs production path
- Post-render verification — file existence, size, duration match, audio track presence
- `qc_final_video.sh` — final quality control on assembled output

### Error Handling
- State backup before every iteration
- Errors logged to `project_state.json` errors array
- `needs_human_review` flag pauses the build loop
- Lock file management prevents concurrent builds
- Max 50 iterations before forced stop

## Requirements

- **macOS** (bash scripts assume macOS paths and tools)
- **Python 3.13+** with Manim CE installed
- **ffmpeg** and **sox** via Homebrew
- **opencode** CLI with a configured AI model
- **ElevenLabs API key** set as `ELEVENLABS_API_KEY`

## Projects

The `projects/` directory contains 12 self-contained video projects spanning math, physics, and climate science — each with its own plan, narration scripts, scene files, and state tracking.

## License

MIT
