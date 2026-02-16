<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Scaffold Incremental Manim Video Builder

Please create the **Incremental Manim Video Builder** project scaffold on my filesystem. This is a bash-script-driven agentic loop system for building complex Manim videos iteratively.

## Requirements

1. **Create the project structure** in `~/manim_projects/incremental_builder/`
2. **Generate all core files** with complete, production-ready code
3. **Use local Qwen voice clone**: Cached audio from `Qwen/Qwen3-TTS-12Hz-1.7B-Base` model with voice reference in `assets/voice_ref/`
4. **Target macOS** (my MacBook environment)
5. **Follow the TECH-SPEC** provided below

***

## Project Structure to Create

```
~/manim_projects/incremental_builder/
├── build_video.sh              # Main orchestration script
├── README.md                   # Usage documentation
├── system_prompt.md            # Agent instructions template
├── example_project/            # Demo project for testing
│   └── .gitkeep
└── reference_docs/             # Symlinks to my Space files
    ├── manim_content_pipeline.md -> ~/path/to/space/manim_content_pipeline.md
    ├── manim_voiceover.md -> ~/path/to/space/manim_voiceover.md
    ├── manim_template.py.txt -> ~/path/to/space/manim_template.py.txt
    └── manim_config_guide.md -> ~/path/to/space/manim_config_guide.md
```

**Note**: For the reference_docs symlinks, please ask me for the actual paths to my Space files, or just create placeholder files with comments indicating they should be symlinked.

***

## Files to Generate

### 1. `build_video.sh`

Full bash script implementing:

- State machine loop (init → plan → review → narration → build_scenes → final_render → assemble → complete)
- Lock file mechanism (`.build.lock` with PID)
- JSON state file read/write (`project_state.json`)
- Agent invocation placeholder (with clear TODO showing where to add my actual agent CLI call)
- Error handling and logging to `build.log`
- Max 50 runs safety limit
- State backup before each run (`.state_backup.json`)
- Phase validation

**Key functions to include**:

- `get_phase()` - read current phase from state JSON
- `invoke_agent()` - placeholder that calls the AI agent with context
- `validate_state()` - check JSON structure after each run
- `backup_state()` - copy state file before modifications


### 2. `system_prompt.md`

The agent instruction template that gets injected on each run. Should include:

- Role definition (Manim video production agent)
- Phase-by-phase instructions
- Rules (locked config, safe positioning, VoiceoverScene patterns)
- Reference to the four reference docs
- State file structure explanation
- Example outputs for each phase


### 3. `README.md`

User documentation covering:

- What this system does
- Prerequisites (manim, manim-voiceover-plus, sox, ffmpeg, Qwen voice model and reference audio)
- Quick start guide
- How to create a new project
- How the state machine works
- Troubleshooting common issues
- File structure explanation


### 4. Example initial `project_state.json` template

Include a commented example showing all fields:

```json
{
  "project_name": "example_project",
  "phase": "plan",
  "created_at": "...",
  "updated_at": "...",
  "run_count": 1,
  "plan_file": null,
  "narration_file": null,
  "voice_config_file": null,
  "scenes": [],
  "current_scene_index": 0,
  "errors": [],
  "history": [],
  "flags": {
    "needs_human_review": false,
    "dry_run": false,
    "force_replan": false
  }
}
```


***

## Technical Details

### Bash Script Configuration Block

```bash
# ─── Configuration ───────────────────────────────────────────────────
PROJECT_DIR="${1:-.}"
STATE_FILE="${PROJECT_DIR}/project_state.json"
STATE_BACKUP="${PROJECT_DIR}/.state_backup.json"
LOCK_FILE="${PROJECT_DIR}/.build.lock"
LOG_FILE="${PROJECT_DIR}/build.log"
MAX_RUNS=50

# Reference docs (relative to script location)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REFERENCE_DOCS=(
  "${SCRIPT_DIR}/reference_docs/manim_content_pipeline.md"
  "${SCRIPT_DIR}/reference_docs/manim_voiceover.md"
  "${SCRIPT_DIR}/reference_docs/manim_template.py.txt"
  "${SCRIPT_DIR}/reference_docs/manim_config_guide.md"
)

# Qwen voice clone config
# Voice reference assets should be in assets/voice_ref/ref.wav and assets/voice_ref/ref.txt
export FLAMING_HORSE_TTS_BACKEND="qwen"
export HF_HUB_OFFLINE="1"
export TRANSFORMERS_OFFLINE="1"
```


### Agent Invocation Placeholder

```bash
invoke_agent() {
  local phase="$1"
  local run_num="$2"
  
  echo "[Run $run_num] Phase: $phase — invoking agent..." | tee -a "$LOG_FILE"
  
  # TODO: Replace this with your actual agent invocation
  # Example patterns:
  #
  # Option 1: CLI tool
  # ai-agent run \
  #   --system-prompt "${SCRIPT_DIR}/system_prompt.md" \
  #   --context-file "$STATE_FILE" \
  #   --context-files "${REFERENCE_DOCS[@]}" \
  #   --instruction "Execute phase: $phase" \
  #   --working-dir "$PROJECT_DIR"
  #
  # Option 2: API call
  # curl -X POST https://api.example.com/agent/run \
  #   -H "Authorization: Bearer $AGENT_API_KEY" \
  #   -d @"$STATE_FILE" \
  #   -d "phase=$phase" \
  #   -d "reference_docs=$(cat ${REFERENCE_DOCS[@]})"
  #
  # Option 3: Python script
  # python3 "${SCRIPT_DIR}/agent_runner.py" \
  #   --state "$STATE_FILE" \
  #   --phase "$phase" \
  #   --references "${REFERENCE_DOCS[@]}"
  
  echo "⚠️  TODO: Agent invocation not implemented. Add your agent call here." >&2
  echo "[Run $run_num] Agent completed phase: $phase" | tee -a "$LOG_FILE"
}
```


***

## Phase Instruction Templates

In `system_prompt.md`, include these per-phase instructions:

### Phase: `plan`

Generate `plan.json` with:

- Topic summary
- Scene breakdown (id, title, narration_key, animations, complexity, risk_flags)
- Estimated duration
- Target audience


### Phase: `review`

Validate `plan.json`:

- Check narrative coherence
- Verify animation feasibility (no unsupported Manim features)
- Estimate timing per scene
- Flag risks (3D, complex graphics, bookmark-dependent sync)
- Output validation report in state.history


### Phase: `narration`

Generate:

- `narration_script.py` with SCRIPT dict (one key per scene)
- `voice_config.py` with VOICE_ID, MODEL_ID, VOICE_SETTINGS constants


### Phase: `build_scenes`

For current scene (tracked by `current_scene_index`):

- Generate `scene_XX_name.py` using VoiceoverScene + template config
- Render with cached Qwen voice (precached audio required)
- If successful: mark scene `status: built`, increment index, stay in `build_scenes`
- If all scenes built: advance to `final_render`


### Phase: `final_render`

Re-render all scenes at production quality with `MANIM_VOICE_PROD=1` (cached Qwen voice, higher resolution/framerate)

### Phase: `assemble`

Generate `scenes.txt`, assemble with FFmpeg concat *filter* (NOT concat demuxer) and re-encode, then verify `final_video.mp4` has continuous audio timestamps (no large PTS gaps).

See: `docs/AUDIO_LESSONS_LEARNED.md`

***

## Additional Helper Scripts

Please also create these helper scripts:

### `new_project.sh`

```bash
#!/usr/bin/env bash
# Creates a new project directory with initialized state file
PROJECT_NAME="${1:?Usage: $0 <project_name>}"
PROJECT_DIR="${2:-./projects}/${PROJECT_NAME}"

mkdir -p "$PROJECT_DIR"
cat > "$PROJECT_DIR/project_state.json" <<EOF
{
  "project_name": "$PROJECT_NAME",
  "phase": "plan",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "updated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "run_count": 0,
  "plan_file": null,
  "narration_file": null,
  "voice_config_file": null,
  "scenes": [],
  "current_scene_index": 0,
  "errors": [],
  "history": [],
  "flags": {
    "needs_human_review": false,
    "dry_run": false,
    "force_replan": false
  }
}
EOF

echo "✅ Created project: $PROJECT_DIR"
echo "Next: ./build_video.sh $PROJECT_DIR"
```


### `reset_phase.sh`

```bash
#!/usr/bin/env bash
# Reset project to a specific phase (for debugging/iteration)
PROJECT_DIR="${1:?Usage: $0 <project_dir> <phase>}"
NEW_PHASE="${2:?Usage: $0 <project_dir> <phase>}"

python3 <<EOF
import json
with open('${PROJECT_DIR}/project_state.json', 'r') as f:
    state = json.load(f)
state['phase'] = '${NEW_PHASE}'
state['updated_at'] = '$(date -u +%Y-%m-%dT%H:%M:%SZ)'
with open('${PROJECT_DIR}/project_state.json', 'w') as f:
    json.dump(state, f, indent=2)
print(f"✅ Reset phase to: ${NEW_PHASE}")
EOF
```


***

## Validation

After scaffolding, please verify:

1. All scripts have execute permissions (`chmod +x *.sh`)
2. `build_video.sh` has proper error handling (set -euo pipefail)
3. Lock file cleanup trap is set
4. JSON operations use Python for reliability (not jq, to avoid dependency)
5. All file paths use variables, not hardcoded strings
6. Reference docs symlinks point to correct locations (or have placeholder comments)

***

## Final Checklist

- [ ] `build_video.sh` is complete and executable
- [ ] `system_prompt.md` has all phase instructions
- [ ] `README.md` has clear usage documentation
- [ ] `new_project.sh` and `reset_phase.sh` helpers are created
- [ ] Example `project_state.json` template is documented
- [ ] Reference docs directory structure exists
- [ ] All scripts follow macOS bash conventions
- [ ] Lock file mechanism is implemented correctly
- [ ] Logging to `build.log` works
- [ ] Agent invocation has clear TODO placeholder

***

Please create all files with complete, working code. I will then integrate my actual agent invocation mechanism into the `invoke_agent()` function placeholder.
