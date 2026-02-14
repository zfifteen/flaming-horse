#!/usr/bin/env bash
set -euo pipefail

# Force offline mode for all HuggingFace/Transformers usage in this pipeline.
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export TOKENIZERS_PARALLELISM=false

# ─── Configuration ───────────────────────────────────────────────────
if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  echo "Usage: $0 <project_dir> [--topic \"<video topic>\"] [--max-runs N]" >&2
  exit 0
fi

PROJECT_DIR_INPUT="${1:-.}" # Original input, could be relative
shift || true

# Optional topic injection (primarily for plan phase)
TOPIC_OVERRIDE=""
MAX_RUNS=50
MAX_RUNS_EXPLICIT=0
while [[ ${#} -gt 0 ]]; do
  case "${1}" in
    --topic)
      TOPIC_OVERRIDE="${2:-}"
      if [[ -z "${TOPIC_OVERRIDE}" ]]; then
        echo "❌ Missing value for --topic" >&2
        exit 1
      fi
      shift 2
      ;;
    --max-runs)
      MAX_RUNS="${2:-}"
      if [[ -z "${MAX_RUNS}" ]]; then
        echo "❌ Missing value for --max-runs" >&2
        exit 1
      fi
      if ! [[ "${MAX_RUNS}" =~ ^[0-9]+$ ]]; then
        echo "❌ --max-runs must be an integer" >&2
        exit 1
      fi
      MAX_RUNS_EXPLICIT=1
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 <project_dir> [--topic \"<video topic>\"] [--max-runs N]" >&2
      exit 0
      ;;
    *)
      echo "❌ Unknown argument: ${1}" >&2
      echo "Usage: $0 <project_dir> [--topic \"<video topic>\"] [--max-runs N]" >&2
      exit 1
      ;;
  esac
done

INITIAL_PWD="$(pwd)"
PROJECT_DIR="$(realpath "${INITIAL_PWD}/${PROJECT_DIR_INPUT}")" # Absolute path to project directory

STATE_FILE="${PROJECT_DIR}/project_state.json"
STATE_BACKUP="${PROJECT_DIR}/.state_backup.json"
LOCK_FILE="${PROJECT_DIR}/.build.lock"
LOG_FILE="${PROJECT_DIR}/build.log"


# Reference docs (relative to script location)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REFERENCE_DOCS=(
  "${SCRIPT_DIR}/../reference_docs/manim_content_pipeline.md"
  "${SCRIPT_DIR}/../reference_docs/manim_voiceover.md"
  "${SCRIPT_DIR}/../reference_docs/manim_template.py.txt"
  "${SCRIPT_DIR}/../reference_docs/manim_config_guide.md"
)


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
  normalize_state_json >/dev/null 2>&1 || true
  python3 -c "import json; print(json.load(open('${STATE_FILE}'))['phase'])"
}

get_run_count() {
  normalize_state_json >/dev/null 2>&1 || true
  python3 -c "import json; print(json.load(open('${STATE_FILE}'))['run_count'])"
}

increment_run_count() {
  normalize_state_json >/dev/null 2>&1 || true
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
  normalize_state_json >/dev/null 2>&1 || true
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

    # Optional, but if present must be a string or null.
    if 'topic' in state and state['topic'] is not None and not isinstance(state['topic'], str):
        print("❌ Invalid type for 'topic' (must be string or null)", file=sys.stderr)
        sys.exit(1)
    
    valid_phases = [
        'init',
        'plan',
        'review',
        'narration',
        'build_scenes',
        'precache_voiceovers',
        'final_render',
        'assemble',
        'complete',
        'error',
    ]
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

normalize_state_json() {
  # Deterministically repair + schema-normalize state after any agent run.
  # This is the single safety net against malformed JSON / missing fields.
  python3 "${SCRIPT_DIR}/update_project_state.py" \
    --project-dir "${PROJECT_DIR}" \
    --mode normalize \
    >/dev/null
}

apply_state_phase() {
  # Deterministically apply phase transitions based on artifacts on disk.
  # The agent is allowed to write plan.json / narration_script.py / scenes,
  # but this script owns project_state.json.
  local phase="$1"
  python3 "${SCRIPT_DIR}/update_project_state.py" \
    --project-dir "${PROJECT_DIR}" \
    --mode apply \
    --phase "${phase}" \
    >/dev/null
}

ensure_topic_present_for_plan() {
  local phase="$1"
  [[ "$phase" == "plan" ]] || return 0

  normalize_state_json >/dev/null 2>&1 || true

  local topic
  topic=$(python3 - <<PY
import json
try:
    state = json.load(open("${STATE_FILE}", "r"))
except Exception:
    state = {}
topic = state.get("topic")
print("" if topic is None else str(topic))
PY
)

  if [[ -z "${TOPIC_OVERRIDE}" && -z "${topic}" ]]; then
    echo "❌ No video topic set for plan phase." | tee -a "$LOG_FILE" >&2
    echo "   Set it when creating the project:" | tee -a "$LOG_FILE" >&2
    echo "     ./scripts/new_project.sh <name> --topic \"...\"" | tee -a "$LOG_FILE" >&2
    echo "   Or override at build time:" | tee -a "$LOG_FILE" >&2
    echo "     ./scripts/build_video.sh ${PROJECT_DIR} --topic \"...\"" | tee -a "$LOG_FILE" >&2
    return 1
  fi

  return 0
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
  
  # Check: Qwen cached voice service is used
  if grep -q "VoiceoverScene" "$scene_file"; then
    if ! grep -q "get_speech_service" "$scene_file"; then
      echo "    ✗ ERROR: Scene missing cached Qwen voice service" | tee -a "$LOG_FILE"
      return 1
    fi
  fi
  
  echo "✓ Voiceover sync checks passed" | tee -a "$LOG_FILE"
  return 0
}

# ─── Agent Invocation ────────────────────────────────────────────────

invoke_agent() {
  local phase="$1"
  local run_num="$2"

  if ! ensure_topic_present_for_plan "$phase"; then
    python3 - <<PY
import json
from datetime import datetime

with open("${STATE_FILE}", "r") as f:
    state = json.load(f)

state.setdefault("errors", []).append("Phase plan failed: No video topic set. Provide project_state.json.topic or pass --topic.")
state.setdefault("flags", {})["needs_human_review"] = True
state["updated_at"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
state.setdefault("history", []).append({
    "phase": "plan",
    "action": "failed",
    "reason": "No video topic set",
    "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
})

with open("${STATE_FILE}", "w") as f:
    json.dump(state, f, indent=2)
PY
    return 1
  fi

  # If a topic override was provided, persist it into state so the agent can rely on project_state.json.
  if [[ "$phase" == "plan" && -n "${TOPIC_OVERRIDE}" ]]; then
    STATE_FILE="${STATE_FILE}" TOPIC_OVERRIDE_FOR_PY="${TOPIC_OVERRIDE}" python3 - <<'PY'
import json
import os
from datetime import datetime

state_file = os.environ["STATE_FILE"]
topic = os.environ["TOPIC_OVERRIDE_FOR_PY"]

with open(state_file, "r") as f:
    state = json.load(f)

state["topic"] = topic
state["updated_at"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

with open(state_file, "w") as f:
    json.dump(state, f, indent=2)
PY
  fi

  # Load topic from state (if present), overridden by CLI flag.
  local topic_from_state
  normalize_state_json >/dev/null 2>&1 || true
  topic_from_state=$(python3 - <<PY
import json
try:
    state = json.load(open("${STATE_FILE}", "r"))
except Exception:
    state = {}
topic = state.get("topic")
if topic is None:
    print("")
else:
    print(str(topic))
PY
)
  local topic
  topic="${TOPIC_OVERRIDE:-${topic_from_state}}"
  
  echo "[Run $run_num] Phase: $phase — invoking agent..." | tee -a "$LOG_FILE"
  
  # Change to project directory for agent execution
  cd "$PROJECT_DIR"
  
  # Create a temporary prompt file
  local prompt_file=".agent_prompt_${phase}.md"
  cat > "$prompt_file" <<EOF
$(cat "${SCRIPT_DIR}/../AGENTS.md")

───────────────────────────────────────────────────────────────

CURRENT TASK:

You are executing phase: ${phase}

Working directory: ${PROJECT_DIR}

Repo root (scripts live here): ${SCRIPT_DIR}/..
Scene scaffold script (absolute path): ${SCRIPT_DIR}/scaffold_scene.py

Files available in this directory:
$(ls -1 "$PROJECT_DIR" 2>/dev/null || echo "  (empty)")

Video topic (if set): ${topic}

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
4. Do NOT edit project_state.json. The build pipeline owns state updates.
   Only generate the required artifacts for the phase (plan.json, narration_script.py, scene_*.py).
5. If errors occur, do NOT edit state; instead, explain what failed in plain text.

IMPORTANT PATH NOTE:
- Your working directory is the project directory, which does NOT contain a ./scripts folder.
- If you need to scaffold a scene, run the scaffold tool via the absolute path above, e.g.:
  python3 "${SCRIPT_DIR}/scaffold_scene.py" --project . --scene-id <scene_id> --class-name <ClassName> --narration-key <key>

TOPIC REQUIREMENT:
- For the plan phase, you MUST use the provided video topic (above). If it is empty, fail the phase with an error explaining how to set it.

Begin execution now.
EOF
  
  # Invoke OpenCode with Grok - message must come after all options
  # TODO Replace this with an option to select from available models configured in OpenCode
  opencode run --model "xai/grok-code-fast-1" \
    --file "$prompt_file" \
    --file "${SCRIPT_DIR}/../reference_docs/manim_content_pipeline.md" \
    --file "${SCRIPT_DIR}/../reference_docs/manim_voiceover.md" \
    --file "${SCRIPT_DIR}/../reference_docs/manim_template.py.txt" \
    --file "${SCRIPT_DIR}/../reference_docs/manim_config_guide.md" \
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

  # Agent may have corrupted state JSON; normalize before applying plan.
  normalize_state_json || true

  # Reliability: some model outputs print JSON but don't write plan.json.
  # If plan.json is missing, recover the latest plan object from build.log.
  cd "$PROJECT_DIR"
  if [[ ! -f "plan.json" ]]; then
    python3 - <<'PY' 2>&1 | tee -a "$LOG_FILE"
import json
from pathlib import Path

log_path = Path('build.log')
if not log_path.exists():
    raise SystemExit('plan.json missing and build.log not found')

raw = log_path.read_text(encoding='utf-8', errors='replace')
decoder = json.JSONDecoder()

best = None
best_pos = -1

for i, ch in enumerate(raw):
    if ch != '{':
        continue
    try:
        obj, end = decoder.raw_decode(raw[i:])
    except json.JSONDecodeError:
        continue
    if not isinstance(obj, dict):
        continue
    if not isinstance(obj.get('scenes'), list) or not obj.get('scenes'):
        continue
    # Minimal required keys
    if not obj.get('title') or not obj.get('topic_summary'):
        continue
    best = obj
    best_pos = i

if not best:
    raise SystemExit('plan.json missing and no valid plan JSON object found in build.log')

Path('plan.json').write_text(json.dumps(best, indent=2) + '\n', encoding='utf-8')
print('✓ Recovered plan.json from build.log')
PY
  fi
  
  # Deterministically apply plan.json into project_state.json.
  apply_state_phase "plan" || true
}

handle_review() {
  echo "🔍 Reviewing plan (deterministic checks)..." | tee -a "$LOG_FILE"

  normalize_state_json || true

  cd "$PROJECT_DIR"
  if [[ ! -f "plan.json" ]]; then
    echo "❌ plan.json missing; cannot review." | tee -a "$LOG_FILE" >&2
    python3 - <<PY
import json
from datetime import datetime

with open("${STATE_FILE}", "r") as f:
    state = json.load(f)

state.setdefault("errors", []).append("review failed: plan.json missing")
state.setdefault("flags", {})["needs_human_review"] = True
state["updated_at"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

with open("${STATE_FILE}", "w") as f:
    json.dump(state, f, indent=2)
PY
    return 1
  fi

  # Minimal structural validation of plan.json.
  python3 - <<'PY' 2>&1 | tee -a "$LOG_FILE"
import json
from pathlib import Path

plan = json.loads(Path('plan.json').read_text(encoding='utf-8'))
if not isinstance(plan, dict):
    raise SystemExit('plan.json must be an object')
scenes = plan.get('scenes')
if not isinstance(scenes, list) or not scenes:
    raise SystemExit('plan.json.scenes missing/empty')
for i, s in enumerate(scenes):
    if not isinstance(s, dict):
        raise SystemExit(f'scene[{i}] must be an object')
    for k in ('id','title','narration_key'):
        if not s.get(k):
            raise SystemExit(f'scene[{i}] missing {k}')
print('✓ plan.json structure looks valid')
PY

  # Deterministically advance state.
  apply_state_phase "review" || true
}

handle_narration() {
  echo "🎙️  Generating narration scripts..." | tee -a "$LOG_FILE"
  invoke_agent "narration" "$(get_run_count)"

  normalize_state_json || true

  # Reliability: some model outputs print SCRIPT but don't write narration_script.py.
  # If narration_script.py is missing, recover it from build.log.
  cd "$PROJECT_DIR"
  if [[ ! -f "narration_script.py" ]]; then
    python3 - <<'PY' 2>&1 | tee -a "$LOG_FILE"
import re
from pathlib import Path

log_path = Path('build.log')
if not log_path.exists():
    raise SystemExit('narration_script.py missing and build.log not found')

raw = log_path.read_text(encoding='utf-8', errors='replace')
idx = raw.rfind('SCRIPT = {')
if idx < 0:
    raise SystemExit('narration_script.py missing and SCRIPT block not found in build.log')

tail = raw[idx:]
lines = tail.splitlines()
out_lines = []
brace_open = False
for ln in lines:
    if not brace_open:
        if ln.strip().startswith('SCRIPT = {'):
            brace_open = True
            out_lines.append('SCRIPT = {')
        continue
    # In-script lines
    out_lines.append(ln)
    if ln.strip() == '}':
        break

script_text = "\n".join(out_lines).strip() + "\n"
if not script_text.endswith('}\n'):
    raise SystemExit('Failed to recover full SCRIPT dict from build.log')

content = (
    '"""\n'
    'Narration script (recovered)\n'
    '"""\n\n'
    + script_text
)

try:
    compile(content, 'narration_script.py', 'exec')
except SyntaxError as e:
    raise SystemExit(f'Recovered narration_script.py is invalid Python: {e}')

Path('narration_script.py').write_text(content, encoding='utf-8')
print('✓ Recovered narration_script.py from build.log')
PY
  fi

  # Post-step: ensure narration_script.py is valid Python.
  # Some agent outputs have been observed to include stray XML-like artifacts.
  cd "$PROJECT_DIR"
  python3 - <<'PY'
import re
from pathlib import Path

path = Path("narration_script.py")
if not path.exists():
    raise SystemExit(0)

src = path.read_text(encoding="utf-8")

def is_valid(code: str) -> bool:
    try:
        compile(code, str(path), "exec")
        return True
    except SyntaxError:
        return False

if is_valid(src):
    raise SystemExit(0)

lines = src.splitlines(True)
patterns = [
    re.compile(r"^\s*</?content>\s*$"),
    re.compile(r"^\s*<parameter\b.*>\s*$"),
    re.compile(r"^\s*</parameter>\s*$"),
]

cleaned = [ln for ln in lines if not any(p.match(ln.rstrip("\n")) for p in patterns)]
cleaned_src = "".join(cleaned)

if cleaned_src != src and is_valid(cleaned_src):
    path.write_text(cleaned_src, encoding="utf-8")
    print("✓ Sanitized narration_script.py (removed stray markup)")
else:
    print("⚠ WARNING: narration_script.py has syntax errors (manual fix may be required)")
PY

  # Deterministically advance state once narration_script.py exists.
  apply_state_phase "narration" || true
}

handle_precache_voiceovers() {
  echo "🎙️  Precaching Qwen voiceovers..." | tee -a "$LOG_FILE"
  cd "$PROJECT_DIR"
  if [[ ! -f "voice_clone_config.json" ]]; then
    echo "✗ ERROR: voice_clone_config.json missing in project" | tee -a "$LOG_FILE"
    return 1
  fi
  if [[ ! -f "assets/voice_ref/ref.wav" || ! -f "assets/voice_ref/ref.txt" ]]; then
    echo "✗ ERROR: Missing voice reference assets in assets/voice_ref" | tee -a "$LOG_FILE"
    return 1
  fi
  echo "→ Running precache script" | tee -a "$LOG_FILE"
  python3 "${SCRIPT_DIR}/precache_voiceovers_qwen.py" "$PROJECT_DIR" 2>&1 | tee -a "$LOG_FILE"

  # Deterministically advance if cache index exists.
  normalize_state_json || true
  apply_state_phase "precache_voiceovers" || true
}

handle_build_scenes() {
  echo "🎨 Building scenes..." | tee -a "$LOG_FILE"
  
  # Get list of scene files BEFORE agent runs
  cd "$PROJECT_DIR"
  local before_files=$(ls scene_*.py 2>/dev/null | sort)
  
  # Invoke agent to generate/update scene
  invoke_agent "build_scenes" "$(get_run_count)"

  # Agent may have produced malformed JSON edits; normalize before reading/writing state.
  normalize_state_json || true
  
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
  
  # If no new file detected, try most recently modified scene file.
  if [[ -z "$new_scene" ]]; then
    new_scene=$(ls -t scene_*.py 2>/dev/null | head -1)
  fi
  
  if [[ -z "$new_scene" ]]; then
    echo "⚠ WARNING: No scene file detected after agent run" | tee -a "$LOG_FILE"

    # Still attempt a deterministic state update (no-op if scene not ready yet).
    apply_state_phase "build_scenes" || true
    return 0
  fi
  
  echo "→ Detected scene file: $new_scene" | tee -a "$LOG_FILE"
  
  # VALIDATION GATE 1: Check imports
  if ! validate_scene_imports "$new_scene"; then
    echo "✗ Import validation failed. Logging error..." | tee -a "$LOG_FILE"
    normalize_state_json || true
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
    normalize_state_json || true
    python3 <<PYEOF
import json
with open('${STATE_FILE}', 'r') as f:
    state = json.load(f)
state['errors'].append("Scene ${new_scene} failed voiceover sync validation. Must use SCRIPT dictionary and cached Qwen voice service.")
# Don't set needs_human_review - let agent retry
with open('${STATE_FILE}', 'w') as f:
    json.dump(state, f, indent=2)
PYEOF
    return 1
  fi
  
  echo "✓ Validation passed for $new_scene" | tee -a "$LOG_FILE"
  
  # Deterministically mark this scene built and advance index/phase.
  apply_state_phase "build_scenes" || true

  return 0
}

handle_final_render() {
  echo "🎬 Final render with cached Qwen voiceover..." | tee -a "$LOG_FILE"
  export MANIM_VOICE_PROD=1
  # Ensure repo-root packages (e.g. flaming_horse_voice) are importable when
  # manim runs from inside the project directory.
  local repo_root
  repo_root="$(realpath "${SCRIPT_DIR}/..")"
  export PYTHONPATH="${repo_root}:${SCRIPT_DIR}:${PYTHONPATH:-}"

  # Clear prior final_render-related errors so the loop can proceed.
  # Keep unrelated errors intact.
  python3 - <<PY
import json
from datetime import datetime

with open("${STATE_FILE}", "r") as f:
    state = json.load(f)

errors = state.get("errors", [])
state["errors"] = [
    e for e in errors
    if not (
        isinstance(e, str)
        and (
            e.startswith("final_render failed")
            or e.startswith("final_render verification failed")
        )
    )
]
state.setdefault("flags", {})["needs_human_review"] = False
state["updated_at"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

with open("${STATE_FILE}", "w") as f:
    json.dump(state, f, indent=2)
PY

  trap 'release_lock' EXIT INT TERM

  cd "$PROJECT_DIR"

  # Ensure Qwen cache exists (precache step). If missing, generate it now.
  if [[ ! -f "media/voiceovers/qwen/cache.json" ]]; then
    echo "→ Missing Qwen cache index; running precache step..." | tee -a "$LOG_FILE"
    if ! handle_precache_voiceovers; then
      echo "❌ Precaching voiceovers failed; cannot render." | tee -a "$LOG_FILE" >&2
      python3 - <<PY
import json
from datetime import datetime

with open("${STATE_FILE}", "r") as f:
    state = json.load(f)
state.setdefault("errors", []).append("final_render failed: precache_voiceovers failed")
state.setdefault("flags", {})["needs_human_review"] = True
state["updated_at"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
with open("${STATE_FILE}", "w") as f:
    json.dump(state, f, indent=2)
PY
      exit 1
    fi
  fi

  # Best-effort repair: ensure scene metadata needed for rendering exists.
  # (Some agents forget to persist scene file/class_name into project_state.json.)
  python3 - <<'PY'
import json
import os
import re
from datetime import datetime

state_file = os.environ.get("STATE_FILE")
project_dir = os.environ.get("PROJECT_DIR")
if not state_file or not project_dir:
    raise SystemExit(0)

with open(state_file, "r") as f:
    state = json.load(f)

scenes = state.get("scenes") or []
changed = False
notes = []

def infer_class_name(scene_path: str) -> str | None:
    try:
        with open(scene_path, "r") as sf:
            txt = sf.read()
    except OSError:
        return None
    # Prefer VoiceoverScene pattern.
    m = re.search(r"^class\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(\s*VoiceoverScene\s*\)\s*:\s*$", txt, re.M)
    if m:
        return m.group(1)
    # Fallback: first class definition.
    m = re.search(r"^class\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(.*\)\s*:\s*$", txt, re.M)
    if m:
        return m.group(1)
    return None

for s in scenes:
    scene_id = s.get("id")
    if not scene_id:
        continue

    # Infer file as <id>.py if missing.
    if not s.get("file"):
        candidate = f"{scene_id}.py"
        candidate_path = os.path.join(project_dir, candidate)
        if os.path.exists(candidate_path):
            s["file"] = candidate
            changed = True
            notes.append(f"set file for {scene_id} -> {candidate}")

    # Infer class name by parsing the scene file if missing.
    if not s.get("class_name") and s.get("file"):
        scene_path = os.path.join(project_dir, s["file"])
        class_name = infer_class_name(scene_path)
        if class_name:
            s["class_name"] = class_name
            changed = True
            notes.append(f"set class_name for {scene_id} -> {class_name}")

if changed:
    state["updated_at"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    state.setdefault("history", []).append(
        {
            "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            "phase": "final_render",
            "action": "Repaired missing scene metadata in state: " + "; ".join(notes),
        }
    )
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)
PY

  local manim_bin
  manim_bin=$(command -v manim)
  if [[ -z "$manim_bin" ]]; then
    echo "❌ manim not found in PATH" | tee -a "$LOG_FILE" >&2
    exit 1
  fi

  # Render scenes sequentially from state (do not trust agent output)
  # Output format: scene_id|file|class_name|estimated_duration
  local scene_lines
  scene_lines=$(python3 - <<PY
import json
from pathlib import Path

state = json.load(open("${STATE_FILE}", "r"))
scenes = state.get("scenes", [])
if not scenes:
    raise SystemExit(1)

missing = []

for s in scenes:
    scene_id = s.get("id")
    file_ = s.get("file")
    class_name = s.get("class_name")
    est = s.get("estimated_duration") or "0s"
    if not scene_id or not file_ or not class_name:
        missing.append({
            "id": scene_id,
            "file": file_,
            "class_name": class_name,
        })
        continue
    print(f"{scene_id}|{file_}|{class_name}|{est}")

if missing:
    import sys
    print("Missing required scene metadata in project_state.json (need id, file, class_name):", file=sys.stderr)
    for m in missing:
        print(f"  - id={m.get('id')!r} file={m.get('file')!r} class_name={m.get('class_name')!r}", file=sys.stderr)
    raise SystemExit(2)
PY
)
  local scene_extract_rc=$?

  if [[ $scene_extract_rc -eq 2 ]]; then
    echo "❌ final_render cannot start: project_state.json is missing scene 'file' and/or 'class_name'." | tee -a "$LOG_FILE" >&2
    echo "   Fix: rebuild scenes so state includes metadata, or ensure scene files exist as <scene_id>.py and declare class <...>(VoiceoverScene)." | tee -a "$LOG_FILE" >&2
    python3 - <<PY
import json
from datetime import datetime

with open("${STATE_FILE}", "r") as f:
    state = json.load(f)
state.setdefault("errors", []).append("final_render failed: missing scene file/class_name metadata in state")
state.setdefault("flags", {})["needs_human_review"] = True
state["updated_at"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
with open("${STATE_FILE}", "w") as f:
    json.dump(state, f, indent=2)
PY
    exit 1
  fi

  if [[ -z "$scene_lines" ]]; then
    echo "❌ No scenes found in state for final_render" | tee -a "$LOG_FILE" >&2
    exit 1
  fi

  # Helper: verify a rendered scene video exists and has audio
  verify_scene_video() {
    local scene_id="$1"
    local class_name="$2"
    local video_path="media/videos/${scene_id}/1440p60/${class_name}.mp4"

    if [[ ! -f "$video_path" ]]; then
      echo "✗ Render output missing: $video_path" | tee -a "$LOG_FILE" >&2
      return 1
    fi
    if [[ ! -s "$video_path" ]]; then
      echo "✗ Render output empty: $video_path" | tee -a "$LOG_FILE" >&2
      return 1
    fi
    if ! command -v ffprobe >/dev/null 2>&1; then
      echo "⚠ WARNING: ffprobe not found; skipping audio verification" | tee -a "$LOG_FILE"
      return 0
    fi
    local audio_stream
    audio_stream=$(ffprobe -v error -select_streams a:0 -show_entries stream=codec_type -of csv=p=0 "$video_path" 2>/dev/null || true)
    if [[ -z "$audio_stream" ]]; then
      echo "✗ No audio stream detected: $video_path" | tee -a "$LOG_FILE" >&2
      return 1
    fi
    return 0
  }

  update_state_rendered() {
    local scene_id="$1"
    local class_name="$2"
    local est_duration="$3"

    local video_path="media/videos/${scene_id}/1440p60/${class_name}.mp4"
    local file_size
    file_size=$(stat -f%z "$video_path" 2>/dev/null || echo 0)
    local duration_sec="0"
    if command -v ffprobe >/dev/null 2>&1; then
      duration_sec=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$video_path" 2>/dev/null || echo 0)
    fi

    python3 - <<PY
import json
from datetime import datetime

scene_id = "${scene_id}"
class_name = "${class_name}"
video_file = "${video_path}"
file_size = int("${file_size}") if "${file_size}".isdigit() else 0
duration = float("${duration_sec}" or 0)

with open("${STATE_FILE}", "r") as f:
    state = json.load(f)

for s in state.get("scenes", []):
    if s.get("id") == scene_id:
        s["status"] = "rendered"
        s["video_file"] = video_file
        s["verification"] = {
            "file_size_bytes": file_size,
            "duration_seconds": duration,
            "audio_present": True,
            "verified_at": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        }
        break

with open("${STATE_FILE}", "w") as f:
    json.dump(state, f, indent=2)
PY
  }

  echo "→ Rendering scenes sequentially (Qwen cached)" | tee -a "$LOG_FILE"

  while IFS='|' read -r scene_id scene_file scene_class est_duration; do
    [[ -n "$scene_id" ]] || continue

    # If the output already exists and verifies, don't re-render.
    if verify_scene_video "$scene_id" "$scene_class"; then
      update_state_rendered "$scene_id" "$scene_class" "$est_duration"
      echo "✓ Already rendered + verified: $scene_id" | tee -a "$LOG_FILE"
      continue
    fi

    # Clean stale/corrupted partials from interrupted renders.
    # These files are intermediate and safe to delete.
    local partial_dir="media/videos/${scene_id}/1440p60/partial_movie_files/${scene_class}"
    local out_video="media/videos/${scene_id}/1440p60/${scene_class}.mp4"
    if [[ -d "$partial_dir" ]]; then
      echo "→ Removing stale partials: $partial_dir" | tee -a "$LOG_FILE"
      rm -rf "$partial_dir"
    fi
    if [[ -f "$out_video" ]]; then
      echo "→ Removing stale output: $out_video" | tee -a "$LOG_FILE"
      rm -f "$out_video"
    fi

    echo "" | tee -a "$LOG_FILE"
    echo "$ manim render $scene_file $scene_class -qh" | tee -a "$LOG_FILE"

    # Retry a small number of times on transient voiceover errors
    local attempt=0
    local max_attempts=5
    local backoff=10
    local ok=0
    while [[ $attempt -lt $max_attempts ]]; do
      attempt=$((attempt + 1))

      if "$manim_bin" render "$scene_file" "$scene_class" -qh 2>&1 | tee -a "$LOG_FILE"; then
        ok=1
        break
      fi

      # If it looks like a transient voiceover error, wait and retry
      if tail -n 200 "$LOG_FILE" | grep -q "too_many_concurrent_requests"; then
        echo "⚠ Voiceover concurrency limit hit; retrying in ${backoff}s (attempt ${attempt}/${max_attempts})" | tee -a "$LOG_FILE"
        sleep "$backoff"
        backoff=$((backoff * 2))
        continue
      fi

      break
    done

    if [[ $ok -ne 1 ]]; then
      echo "❌ Render failed for $scene_id ($scene_class)" | tee -a "$LOG_FILE" >&2
      python3 - <<PY
import json
from datetime import datetime

scene_id = "${scene_id}"

with open("${STATE_FILE}", "r") as f:
    state = json.load(f)

state["errors"].append(f"final_render failed for {scene_id}: see build.log")
state["flags"]["needs_human_review"] = True
state["updated_at"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

with open("${STATE_FILE}", "w") as f:
    json.dump(state, f, indent=2)
PY
      exit 1
    fi

    if ! verify_scene_video "$scene_id" "$scene_class"; then
      echo "❌ Verification failed for $scene_id ($scene_class)" | tee -a "$LOG_FILE" >&2
      python3 - <<PY
import json
from datetime import datetime

scene_id = "${scene_id}"

with open("${STATE_FILE}", "r") as f:
    state = json.load(f)

state["errors"].append(f"final_render verification failed for {scene_id}: missing/invalid mp4 or audio")
state["flags"]["needs_human_review"] = True
state["updated_at"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

with open("${STATE_FILE}", "w") as f:
    json.dump(state, f, indent=2)
PY
      exit 1
    fi

    update_state_rendered "$scene_id" "$scene_class" "$est_duration"
    echo "✓ Rendered + verified: $scene_id" | tee -a "$LOG_FILE"
  done <<< "$scene_lines"

  # Advance to assemble
  python3 - <<PY
import json
from datetime import datetime
with open("${STATE_FILE}", "r") as f:
    state = json.load(f)
state["phase"] = "assemble"
state["updated_at"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
state["history"].append("Phase final_render: Rendered and verified all scenes (scripted), advancing to assemble")
with open("${STATE_FILE}", "w") as f:
    json.dump(state, f, indent=2)
PY

}

handle_assemble() {
  echo "🎞️  Assembling final video..." | tee -a "$LOG_FILE"

  cd "$PROJECT_DIR"

  # Generate scenes.txt from state (script is in repo root)
  python3 "${SCRIPT_DIR}/generate_scenes_txt.py" "$PROJECT_DIR" 2>&1 | tee -a "$LOG_FILE"

  if [[ ! -f "${PROJECT_DIR}/scenes.txt" ]]; then
    echo "❌ scenes.txt not created" | tee -a "$LOG_FILE" >&2
    exit 1
  fi

  # Build ffmpeg concat filter inputs from scenes.txt
  mapfile -t scene_files < <(sed -n "s/^file '\(.*\)'$/\1/p" "${PROJECT_DIR}/scenes.txt")
  if [[ ${#scene_files[@]} -eq 0 ]]; then
    echo "❌ scenes.txt is empty" | tee -a "$LOG_FILE" >&2
    exit 1
  fi

  # Verify all input scene files exist before assembling
  local missing=0
  for f in "${scene_files[@]}"; do
    if [[ ! -f "$PROJECT_DIR/$f" ]]; then
      echo "❌ Missing scene video: $f" | tee -a "$LOG_FILE" >&2
      missing=1
    fi
  done
  if [[ $missing -ne 0 ]]; then
    python3 - <<PY
import json
from datetime import datetime
with open("${STATE_FILE}", "r") as f:
    state = json.load(f)
state["errors"].append("Assemble failed: one or more scene video files are missing")
state["flags"]["needs_human_review"] = True
state["updated_at"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
with open("${STATE_FILE}", "w") as f:
    json.dump(state, f, indent=2)
PY
    exit 1
  fi

  # Assemble with concat filter + audio timestamp normalization (no -c copy)
  local ffmpeg_inputs=()
  local filter_inputs=""
  local n=${#scene_files[@]}
  for i in $(seq 0 $((n - 1))); do
    ffmpeg_inputs+=( -i "${PROJECT_DIR}/${scene_files[$i]}" )
    filter_inputs+="[${i}:v:0][${i}:a:0]"
  done
  local filter_complex
  filter_complex="${filter_inputs}concat=n=${n}:v=1:a=1[v][a];[a]aresample=async=1:first_pts=0[aout]"

  echo "$ ffmpeg (concat filter) -> final_video.mp4" | tee -a "$LOG_FILE"
  ffmpeg -y \
    "${ffmpeg_inputs[@]}" \
    -filter_complex "$filter_complex" \
    -map "[v]" -map "[aout]" \
    -c:v libx264 -pix_fmt yuv420p -crf 18 -preset medium \
    -c:a aac -b:a 192k -ar 48000 \
    -movflags +faststart \
    "${PROJECT_DIR}/final_video.mp4" \
    2>&1 | tee -a "$LOG_FILE"

  if [[ ! -s "${PROJECT_DIR}/final_video.mp4" ]]; then
    echo "❌ final_video.mp4 not created or empty" | tee -a "$LOG_FILE" >&2
    exit 1
  fi

  # Update phase (QC still runs below)
  python3 - <<PY
import json
from datetime import datetime
with open("${STATE_FILE}", "r") as f:
    state = json.load(f)
state["updated_at"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
state["history"].append("Phase assemble: Assembled final_video.mp4 (scripted)")
with open("${STATE_FILE}", "w") as f:
    json.dump(state, f, indent=2)
PY
  
  # NEW: Run quality control
  echo "" | tee -a "$LOG_FILE"
  echo "═══════════════════════════════════════════" | tee -a "$LOG_FILE"
  echo "Running quality control on final video..." | tee -a "$LOG_FILE"
  echo "═══════════════════════════════════════════" | tee -a "$LOG_FILE"
  
  if [[ -x "${SCRIPT_DIR}/qc_final_video.sh" ]]; then
    if ! "${SCRIPT_DIR}/qc_final_video.sh" "${PROJECT_DIR}/final_video.mp4" "$PROJECT_DIR"; then
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

  # Immediately exit this run so the main loop doesn't increment run_count and
  # start a new iteration against the now-complete state.
  handle_complete
}

handle_complete() {
  echo "✅ Video build complete!" | tee -a "$LOG_FILE"
  echo "Final video: ${PROJECT_DIR}/final_video.mp4" | tee -a "$LOG_FILE"
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

    # Repair + normalize state (never trust agent edits).
    if ! normalize_state_json; then
      echo "❌ State file could not be normalized." | tee -a "$LOG_FILE" >&2
      echo "   See: $STATE_FILE" | tee -a "$LOG_FILE" >&2
      [[ -f "$STATE_BACKUP" ]] && echo "   Backup: $STATE_BACKUP" | tee -a "$LOG_FILE" >&2
      exit 1
    fi

    if ! validate_state; then
      echo "❌ State validation failed. Restoring backup..." >&2
      [[ -f "$STATE_BACKUP" ]] && cp "$STATE_BACKUP" "$STATE_FILE"
      exit 1
    fi

    backup_state
    
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
      precache_voiceovers) handle_precache_voiceovers ;;
      final_render) handle_final_render ;;
      assemble) handle_assemble ;;
      complete) handle_complete ;;
      *) echo "❌ Unknown phase: $current_phase" >&2; exit 1 ;;
    esac

    # Post-phase: normalize state and deterministically apply phase transition.
    if ! normalize_state_json; then
      echo "❌ Phase produced an invalid/un-normalizable state file; restoring last backup." | tee -a "$LOG_FILE" >&2
      [[ -f "$STATE_BACKUP" ]] && cp "$STATE_BACKUP" "$STATE_FILE"
      exit 1
    fi

    # The agent may have advanced phase in its output; ignore that and apply
    # deterministic state transition for the phase that was just executed.
    apply_state_phase "$current_phase" || true

    # Normalize again in case apply_phase repaired missing keys, etc.
    normalize_state_json || true
    
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
