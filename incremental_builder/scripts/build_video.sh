#!/usr/bin/env bash
set -euo pipefail

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

# ElevenLabs config (checked in final_render phase, not at startup)
export ELEVENLABS_API_KEY="${ELEVENLABS_API_KEY:-}"
VOICE_ID="rBgRd5IfS6iqrGfuhlKR"
MODEL_ID="eleven_multilingual_v2"

# ─── Lock File Management ────────────────────────────────────────────

acquire_lock() {
  if [[ -f "$LOCK_FILE" ]]; then
    local lock_pid
    lock_pid=$(cat "$LOCK_FILE")
    if kill -0 "$lock_pid" 2>/dev/null; then
      echo "❌ Build already running (PID: $lock_pid)" >&2
      exit 1
    else
      echo "⚠️  Stale lock file found, removing..." >&2
      rm -f "$LOCK_FILE"
    fi
  fi
  echo $$ > "$LOCK_FILE"
  echo "🔒 Lock acquired (PID: $$)" | tee -a "$LOG_FILE"
}

release_lock() {
  rm -f "$LOCK_FILE"
  echo "🔓 Lock released" | tee -a "$LOG_FILE"
}

trap release_lock EXIT INT TERM

# ─── State Management ────────────────────────────────────────────────

get_phase() {
  python3 -c "import json; print(json.load(open('${STATE_FILE}'))['phase'])"
}

get_run_count() {
  python3 -c "import json; print(json.load(open('${STATE_FILE}'))['run_count'])"
}

increment_run_count() {
  python3 <<EOF
import json
from datetime import datetime
with open('${STATE_FILE}', 'r') as f:
    state = json.load(f)
state['run_count'] += 1
state['updated_at'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
with open('${STATE_FILE}', 'w') as f:
    json.dump(state, f, indent=2)
EOF
}

backup_state() {
  if [[ -f "$STATE_FILE" ]]; then
    cp "$STATE_FILE" "$STATE_BACKUP"
    echo "💾 State backed up" | tee -a "$LOG_FILE"
  fi
}

validate_state() {
  python3 <<EOF
import json
import sys

required_fields = ['project_name', 'phase', 'created_at', 'updated_at', 
                   'run_count', 'scenes', 'current_scene_index', 
                   'errors', 'history', 'flags']

try:
    with open('${STATE_FILE}', 'r') as f:
        state = json.load(f)
    
    for field in required_fields:
        if field not in state:
            print(f"❌ Missing required field: {field}", file=sys.stderr)
            sys.exit(1)
    
    valid_phases = ['plan', 'review', 'narration', 'build_scenes', 
                    'final_render', 'assemble', 'complete', 'error']
    if state['phase'] not in valid_phases:
        print(f"❌ Invalid phase: {state['phase']}", file=sys.stderr)
        sys.exit(1)
    
    print("✅ State file valid")
except json.JSONDecodeError as e:
    print(f"❌ Invalid JSON: {e}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"❌ Validation error: {e}", file=sys.stderr)
    sys.exit(1)
EOF
}

# ═══════════════════════════════════════════════════════════════
# Validation Functions
# ═══════════════════════════════════════════════════════════════

validate_scene_imports() {
  local scene_file="$1"
  
  echo "→ Validating imports in ${scene_file}..." | tee -a "$LOG_FILE"
  
  cd "$PROJECT_DIR"
  
  # Static validation - check for common import mistakes
  echo "  Checking import syntax..." | tee -a "$LOG_FILE"
  
  # Check for manimvoiceoverplus (no separators) - WRONG
  if grep -q "from manimvoiceoverplus import" "$scene_file" || \
     grep -q "import manimvoiceoverplus" "$scene_file"; then
    echo "✗ ERROR: Scene uses 'manimvoiceoverplus' (no separators)" | tee -a "$LOG_FILE"
    echo "  Should be 'manim_voiceover_plus' (with underscores)" | tee -a "$LOG_FILE"
    return 1
  fi
  
  # Check for manim-voiceover-plus (hyphens) - WRONG
  if grep -q "from manim-voiceover-plus import" "$scene_file" || \
     grep -q "import manim-voiceover-plus" "$scene_file"; then
    echo "✗ ERROR: Scene uses 'manim-voiceover-plus' (hyphens)" | tee -a "$LOG_FILE"
    echo "  Should be 'manim_voiceover_plus' (with underscores)" | tee -a "$LOG_FILE"
    return 1
  fi
  
  # Check for correct pattern
  if grep -q "from manim_voiceover_plus import" "$scene_file" || \
     grep -q "import manim_voiceover_plus" "$scene_file"; then
    echo "✓ Import names are correct (manim_voiceover_plus)" | tee -a "$LOG_FILE"
  else
    echo "⚠ WARNING: No manim_voiceover_plus imports found" | tee -a "$LOG_FILE"
  fi
  
  # Try Python import validation, but don't fail if environment issue
  echo "  Attempting Python syntax check..." | tee -a "$LOG_FILE"
  python3 -c "
import sys
sys.path.insert(0, '.')
try:
    with open('${scene_file}', 'r') as f:
        compile(f.read(), '${scene_file}', 'exec')
    print('✓ Python syntax valid')
except SyntaxError as e:
    print(f'✗ Syntax error: {e}')
    sys.exit(1)
" 2>&1 | tee -a "$LOG_FILE"
  
  local syntax_result=${PIPESTATUS[0]}
  if [[ $syntax_result -ne 0 ]]; then
    echo "✗ ERROR: Scene has syntax errors" | tee -a "$LOG_FILE"
    return 1
  fi
  
  echo "✓ Import validation passed" | tee -a "$LOG_FILE"
  return 0
}

validate_voiceover_sync() {
  local scene_file="$1"
  
  echo "→ Validating voiceover sync in ${scene_file}..." | tee -a "$LOG_FILE"
  
  # Check for hardcoded narration text
  if grep -q 'voiceover(text="' "$scene_file" || grep -q "voiceover(text='" "$scene_file"; then
    echo "✗ ERROR: Scene uses hardcoded narration text instead of SCRIPT dictionary" | tee -a "$LOG_FILE"
    echo "Found at:" | tee -a "$LOG_FILE"
    grep -n 'voiceover(text=' "$scene_file" | tee -a "$LOG_FILE"
    return 1
  fi
  
  # Check for f-string narration
  if grep -q 'voiceover(text=f"' "$scene_file" || grep -q "voiceover(text=f'" "$scene_file"; then
    echo "✗ ERROR: Scene uses f-string narration instead of SCRIPT dictionary" | tee -a "$LOG_FILE"
    echo "Found at:" | tee -a "$LOG_FILE"
    grep -n 'voiceover(text=f' "$scene_file" | tee -a "$LOG_FILE"
    return 1
  fi
  
  # Check for tracker.duration usage (warning only)
  if ! grep -q 'tracker\.duration' "$scene_file"; then
    echo "⚠ WARNING: Scene may not use tracker.duration for synchronization" | tee -a "$LOG_FILE"
    echo "This can cause voiceover/animation desync" | tee -a "$LOG_FILE"
    # Don't fail, just warn
  fi
  
  # Check: ElevenLabs production path is not empty
  if grep -q "if os.getenv.*MANIM_VOICE_PROD" "$scene_file"; then
    echo "  - Checking ElevenLabs production path..." | tee -a "$LOG_FILE"
    
    # Look for 'pass' statement in the production block (within 5 lines)
    if grep -A 5 "if os.getenv.*MANIM_VOICE_PROD" "$scene_file" | grep -q "^\s*pass\s*$"; then
      echo "    ✗ ERROR: ElevenLabs production path is empty (just 'pass')" | tee -a "$LOG_FILE"
      echo "    This will cause production renders to fall back to gTTS!" | tee -a "$LOG_FILE"
      return 1
    fi
    
    # Verify ElevenLabsService is actually initialized
    if ! grep -A 8 "if os.getenv.*MANIM_VOICE_PROD" "$scene_file" | grep -q "ElevenLabsService"; then
      echo "    ✗ ERROR: ElevenLabs production path missing service initialization" | tee -a "$LOG_FILE"
      return 1
    fi
    
    echo "    ✓ ElevenLabs production path implemented" | tee -a "$LOG_FILE"
  fi
  
  echo "✓ Voiceover sync checks passed" | tee -a "$LOG_FILE"
  return 0
}

# ─── Agent Invocation ────────────────────────────────────────────────

invoke_agent() {
  local phase="$1"
  local run_num="$2"
  
  echo "[Run $run_num] Phase: $phase — invoking agent..." | tee -a "$LOG_FILE"
  
  # Change to project directory for agent execution
  cd "$PROJECT_DIR"
  
  # Create a temporary prompt file
  local prompt_file="${PROJECT_DIR}/.agent_prompt_${phase}.md"
  cat > "$prompt_file" <<EOF
$(cat "${SCRIPT_DIR}/system_prompt.md")

───────────────────────────────────────────────────────────────

CURRENT TASK:

You are executing phase: ${phase}

Working directory: ${PROJECT_DIR}

Files available in this directory:
$(ls -1 "$PROJECT_DIR" 2>/dev/null || echo "  (empty)")

Reference documentation has been attached to this message:
- manim_content_pipeline.md
- manim_voiceover.md  
- manim_template.py.txt
- manim_config_guide.md

The current project_state.json has also been attached.

INSTRUCTIONS:
1. Read project_state.json to understand the current state
2. Execute ONLY the ${phase} phase tasks as defined in the system prompt above
3. Generate any required files in the current directory
4. Update project_state.json with results and advance to the next phase
5. If errors occur, set flags.needs_human_review = true and log to errors array

Begin execution now.
EOF
  
  # Invoke OpenCode with Grok - message must come after all options
  opencode run --model "xai/grok-code-fast-1" \
    --file "$prompt_file" \
    --file "${SCRIPT_DIR}/reference_docs/manim_content_pipeline.md" \
    --file "${SCRIPT_DIR}/reference_docs/manim_voiceover.md" \
    --file "${SCRIPT_DIR}/reference_docs/manim_template.py.txt" \
    --file "${SCRIPT_DIR}/reference_docs/manim_config_guide.md" \
    --file "$STATE_FILE" \
    -- \
    "Read the first attached file (.agent_prompt_${phase}.md) which contains your complete instructions. Execute the ${phase} phase as described. All reference documentation and the current project state are also attached." \
    2>&1 | tee -a "$LOG_FILE"
  
  # Clean up prompt file
  rm -f "$prompt_file"
  
  local exit_code=${PIPESTATUS[0]}
  
  if [[ $exit_code -ne 0 ]]; then
    echo "❌ Agent invocation failed with exit code: $exit_code" | tee -a "$LOG_FILE"
    return 1
  fi
  
  echo "[Run $run_num] Agent completed phase: $phase" | tee -a "$LOG_FILE"
}

# ─── Phase Handlers ──────────────────────────────────────────────────

handle_init() {
  echo "🎬 Initializing project..." | tee -a "$LOG_FILE"
  invoke_agent "init" "$(get_run_count)"
}

handle_plan() {
  echo "📝 Planning video..." | tee -a "$LOG_FILE"
  invoke_agent "plan" "$(get_run_count)"
}

handle_review() {
  echo "🔍 Reviewing plan..." | tee -a "$LOG_FILE"
  invoke_agent "review" "$(get_run_count)"
}

handle_narration() {
  echo "🎙️  Generating narration scripts..." | tee -a "$LOG_FILE"
  invoke_agent "narration" "$(get_run_count)"
}

handle_build_scenes() {
  echo "🎨 Building scenes..." | tee -a "$LOG_FILE"
  
  # Get list of scene files BEFORE agent runs
  cd "$PROJECT_DIR"
  local before_files=$(ls scene_*.py 2>/dev/null | sort)
  
  # Invoke agent to generate/update scene
  invoke_agent "build_scenes" "$(get_run_count)"
  
  # Get list of scene files AFTER agent runs
  local after_files=$(ls scene_*.py 2>/dev/null | sort)
  
  # Find the new or modified file (simple diff)
  local new_scene=""
  for scene_file in $after_files; do
    if ! echo "$before_files" | grep -q "$scene_file"; then
      new_scene="$scene_file"
      break
    fi
  done
  
  # If no new file detected, check if agent updated state to indicate completion
  if [[ -z "$new_scene" ]]; then
    local current_phase=$(get_phase)
    if [[ "$current_phase" != "build_scenes" ]]; then
      echo "Agent advanced phase. Proceeding..." | tee -a "$LOG_FILE"
      return 0
    fi
    # Try to get most recently modified scene file
    new_scene=$(ls -t scene_*.py 2>/dev/null | head -1)
  fi
  
  if [[ -z "$new_scene" ]]; then
    echo "⚠ WARNING: No scene file detected after agent run" | tee -a "$LOG_FILE"
    return 0
  fi
  
  echo "→ Detected scene file: $new_scene" | tee -a "$LOG_FILE"
  
  # VALIDATION GATE 1: Check imports
  if ! validate_scene_imports "$new_scene"; then
    echo "✗ Import validation failed. Logging error..." | tee -a "$LOG_FILE"
    python3 <<PYEOF
import json
with open('${STATE_FILE}', 'r') as f:
    state = json.load(f)
state['errors'].append("Scene ${new_scene} failed import validation. Check module names - use manim_voiceover_plus with underscores.")
# Don't set needs_human_review - let agent retry
with open('${STATE_FILE}', 'w') as f:
    json.dump(state, f, indent=2)
PYEOF
    return 1
  fi
  
  # VALIDATION GATE 2: Check voiceover sync patterns
  if ! validate_voiceover_sync "$new_scene"; then
    echo "✗ Sync validation failed. Logging error..." | tee -a "$LOG_FILE"
    python3 <<PYEOF
import json
with open('${STATE_FILE}', 'r') as f:
    state = json.load(f)
state['errors'].append("Scene ${new_scene} uses hardcoded narration text. Must use SCRIPT dictionary.")
# Don't set needs_human_review - let agent retry
with open('${STATE_FILE}', 'w') as f:
    json.dump(state, f, indent=2)
PYEOF
    return 1
  fi
  
  echo "✓ Validation passed for $new_scene" | tee -a "$LOG_FILE"
  
  # Agent has already updated the state, validation complete
  return 0
}

handle_final_render() {
  echo "🎬 Final render with ElevenLabs..." | tee -a "$LOG_FILE"
  export MANIM_VOICE_PROD=1
  invoke_agent "final_render" "$(get_run_count)"
}

handle_assemble() {
  echo "🎞️  Assembling final video..." | tee -a "$LOG_FILE"
  invoke_agent "assemble" "$(get_run_count)"
  
  # NEW: Run quality control
  echo "" | tee -a "$LOG_FILE"
  echo "═══════════════════════════════════════════" | tee -a "$LOG_FILE"
  echo "Running quality control on final video..." | tee -a "$LOG_FILE"
  echo "═══════════════════════════════════════════" | tee -a "$LOG_FILE"
  
  if [[ -x "${SCRIPT_DIR}/qc_final_video.sh" ]]; then
    "${SCRIPT_DIR}/qc_final_video.sh" "${PROJECT_DIR}/final_video.mp4" "$PROJECT_DIR"
    if [[ $? -ne 0 ]]; then
      echo "✗ QC FAILED! Video has quality issues." | tee -a "$LOG_FILE"
      python3 <<PYEOF
import json
with open('${STATE_FILE}', 'r') as f:
    state = json.load(f)
state['phase'] = 'error'
state['errors'].append('Final video failed quality control - check audio/video sync')
state['flags']['needs_human_review'] = True
with open('${STATE_FILE}', 'w') as f:
    json.dump(state, f, indent=2)
PYEOF
      return 1
    fi
    echo "✓ QC passed!" | tee -a "$LOG_FILE"
  else
    echo "⚠ WARNING: qc_final_video.sh not found or not executable." | tee -a "$LOG_FILE"
    echo "This is DANGEROUS - video may have quality issues!" | tee -a "$LOG_FILE"
  fi
  
  # Only advance to complete if QC passes
  echo "✓ Advancing to complete phase." | tee -a "$LOG_FILE"
  python3 <<PYEOF
import json
with open('${STATE_FILE}', 'r') as f:
    state = json.load(f)
state['phase'] = 'complete'
with open('${STATE_FILE}', 'w') as f:
    json.dump(state, f, indent=2)
PYEOF
}

handle_complete() {
  echo "✅ Video build complete!" | tee -a "$LOG_FILE"
  echo "�� Final video: ${PROJECT_DIR}/final_video.mp4"
  exit 0
}

# ─── Main Loop ───────────────────────────────────────────────────────

main() {
  if [[ ! -d "$PROJECT_DIR" ]]; then
    echo "❌ Project directory not found: $PROJECT_DIR" >&2
    exit 1
  fi
  
  if [[ ! -f "$STATE_FILE" ]]; then
    echo "❌ State file not found: $STATE_FILE" >&2
    echo "Run: ./new_project.sh <project_name> to create a new project" >&2
    exit 1
  fi
  
  acquire_lock
  
  echo "════════════════════════════════════════════════════════════════" | tee -a "$LOG_FILE"
  echo "🚀 Starting Incremental Manim Video Builder" | tee -a "$LOG_FILE"
  echo "📁 Project: $PROJECT_DIR" | tee -a "$LOG_FILE"
  echo "⏰ Started: $(date)" | tee -a "$LOG_FILE"
  echo "════════════════════════════════════════════════════════════════" | tee -a "$LOG_FILE"
  
  local iteration=0
  while [[ $iteration -lt $MAX_RUNS ]]; do
    iteration=$((iteration + 1))
    
    backup_state
    
    if ! validate_state; then
      echo "❌ State validation failed. Restoring backup..." >&2
      [[ -f "$STATE_BACKUP" ]] && cp "$STATE_BACKUP" "$STATE_FILE"
      exit 1
    fi
    
    local current_phase
    current_phase=$(get_phase)
    
    echo "" | tee -a "$LOG_FILE"
    echo "────────────────────────────────────────────────────────────────" | tee -a "$LOG_FILE"
    echo "Iteration: $iteration/$MAX_RUNS" | tee -a "$LOG_FILE"
    echo "Current phase: $current_phase" | tee -a "$LOG_FILE"
    echo "────────────────────────────────────────────────────────────────" | tee -a "$LOG_FILE"
    
    case "$current_phase" in
      init) handle_init ;;
      plan) handle_plan ;;
      review) handle_review ;;
      narration) handle_narration ;;
      build_scenes) handle_build_scenes ;;
      final_render) handle_final_render ;;
      assemble) handle_assemble ;;
      complete) handle_complete ;;
      *) echo "❌ Unknown phase: $current_phase" >&2; exit 1 ;;
    esac
    
    increment_run_count
    
    local needs_review
    needs_review=$(python3 -c "import json; print(json.load(open('${STATE_FILE}'))['flags'].get('needs_human_review', False))")
    
    if [[ "$needs_review" == "True" ]]; then
      echo "⚠️  Human review required. Pausing build loop." | tee -a "$LOG_FILE"
      echo "Check $STATE_FILE for details" | tee -a "$LOG_FILE"
      exit 0
    fi
  done
  
  echo "⚠️  Maximum iterations ($MAX_RUNS) reached. Stopping." | tee -a "$LOG_FILE"
  exit 1
}

main "$@"
