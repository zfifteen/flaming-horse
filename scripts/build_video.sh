#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(realpath "${SCRIPT_DIR}/..")"
ENV_FILE="${REPO_ROOT}/.env"

# Ensure repo-local modules (e.g. flaming_horse_voice) are importable in every
# phase when rendering from project directories.
export PYTHONPATH="${REPO_ROOT}:${SCRIPT_DIR}:${PYTHONPATH:-}"

if [[ -f "${ENV_FILE}" ]]; then
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
fi

AGENT_MODEL="${AGENT_MODEL:-xai/grok-4-1-fast}"
PROJECTS_BASE_DIR="${PROJECTS_BASE_DIR:-projects}"
PROJECT_DEFAULT_NAME="${PROJECT_DEFAULT_NAME:-default_video}"
MAX_RUNS="${MAX_RUNS:-50}"
PHASE_RETRY_LIMIT="${PHASE_RETRY_LIMIT:-3}"
PHASE_RETRY_BACKOFF_SECONDS="${PHASE_RETRY_BACKOFF_SECONDS:-2}"

# Force offline mode for all HuggingFace/Transformers usage in this pipeline.
HF_HUB_OFFLINE="${HF_HUB_OFFLINE:-1}"
TRANSFORMERS_OFFLINE="${TRANSFORMERS_OFFLINE:-1}"
TOKENIZERS_PARALLELISM="${TOKENIZERS_PARALLELISM:-false}"
export HF_HUB_OFFLINE
export TRANSFORMERS_OFFLINE
export TOKENIZERS_PARALLELISM

# ─── Configuration ───────────────────────────────────────────────────
if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  echo "Usage: $0 [project_dir] [--topic \"<video topic>\"] [--max-runs N]" >&2
  echo "  --max-runs N limits loop iterations (phase transitions), not full project completion." >&2
  exit 0
fi

PROJECT_DIR_INPUT="${1:-${PROJECTS_BASE_DIR}/${PROJECT_DEFAULT_NAME}}" # Original input, could be relative
shift || true

# Optional topic injection (primarily for plan phase)
TOPIC_OVERRIDE=""
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
      echo "Usage: $0 [project_dir] [--topic \"<video topic>\"] [--max-runs N]" >&2
      echo "  --max-runs N limits loop iterations (phase transitions), not full project completion." >&2
      exit 0
      ;;
    *)
      echo "❌ Unknown argument: ${1}" >&2
      echo "Usage: $0 [project_dir] [--topic \"<video topic>\"] [--max-runs N]" >&2
      echo "  --max-runs N limits loop iterations (phase transitions), not full project completion." >&2
      exit 1
      ;;
  esac
done

INITIAL_PWD="$(pwd)"
if [[ "${PROJECT_DIR_INPUT}" = /* ]]; then
  PROJECT_DIR_RAW="${PROJECT_DIR_INPUT}"
else
  PROJECT_DIR_RAW="${INITIAL_PWD}/${PROJECT_DIR_INPUT}"
fi
PROJECT_DIR="$(python3 -c 'import os,sys; print(os.path.abspath(sys.argv[1]))' "${PROJECT_DIR_RAW}")" # Absolute path to project directory

STATE_FILE="${PROJECT_DIR}/project_state.json"
STATE_BACKUP="${PROJECT_DIR}/.state_backup.json"
LOCK_FILE="${PROJECT_DIR}/.build.lock"
LOG_FILE="${PROJECT_DIR}/build.log"
ERROR_LOG="${PROJECT_DIR}/errors.log"
OPENCODE_SESSION_ID=""


# Prompt templates (relative to script location)
PROMPTS_DIR="${SCRIPT_DIR}/../prompts"
PHASE_PROMPT_MAIN_TEMPLATE="${PROMPTS_DIR}/phase_prompt.md"
PHASE_PROMPT_TEMPLATE="${PROMPTS_DIR}/phase_prompt_instructions.md"
PHASE_NARRATION_TEMPLATE="${PROMPTS_DIR}/phase_narration.md"
PHASE_BUILD_SCENES_TEMPLATE="${PROMPTS_DIR}/phase_build_scenes.md"
SCENE_FIX_TEMPLATE="${PROMPTS_DIR}/scene_fix_prompt.md"
SCENE_QC_TEMPLATE="${PROMPTS_DIR}/scene_qc_prompt.md"


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
        'scene_qc',
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

extract_opencode_session_id() {
  local output_file="$1"
  python3 - "$output_file" <<'PY'
import json
import sys

path = sys.argv[1]
with open(path, "r", encoding="utf-8", errors="replace") as f:
    for raw in f:
        line = raw.strip()
        if not line or not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except Exception:
            continue
        session_id = event.get("sessionID")
        if isinstance(session_id, str) and session_id.startswith("ses_"):
            print(session_id)
            break
PY
}

capture_opencode_session_id_if_missing() {
  local output_file="$1"
  if [[ -n "${OPENCODE_SESSION_ID}" ]]; then
    return 0
  fi

  local parsed_session_id
  parsed_session_id="$(extract_opencode_session_id "$output_file")"
  if [[ -n "$parsed_session_id" ]]; then
    OPENCODE_SESSION_ID="$parsed_session_id"
    echo "🔗 OpenCode session: ${OPENCODE_SESSION_ID}" | tee -a "$LOG_FILE"
  fi
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

is_retryable_phase() {
  local phase="$1"
  case "$phase" in
    init|plan|narration|build_scenes|scene_qc|final_render|assemble)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

get_retry_context_file() {
  local phase="$1"
  printf "%s/.agent_retry_%s.md" "$PROJECT_DIR" "$phase"
}

build_retry_context() {
  local phase="$1"
  local attempt="$2"
  local context_file
  context_file="$(get_retry_context_file "$phase")"

  python3 - <<PY > "$context_file"
import json
import re
from pathlib import Path
from datetime import datetime

phase = "${phase}"
attempt = int("${attempt}")
limit = int("${PHASE_RETRY_LIMIT}")
state_path = Path("${STATE_FILE}")
log_path = Path("${LOG_FILE}")

state_error = "(none)"
if state_path.exists():
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
        errors = state.get("errors") if isinstance(state.get("errors"), list) else []
        if errors:
            state_error = str(errors[-1])
    except Exception as exc:
        state_error = f"(failed to parse state error: {exc})"

log_excerpt = []
trace_blocks = []
if log_path.exists():
  lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()

  # Prefer full traceback blocks over keyword-only snippets.
  starts = [
    i for i, ln in enumerate(lines)
    if "Traceback (most recent call last)" in ln or "╭───────────────────── Traceback" in ln
  ]

  for start in starts[-2:]:
    hard_limit = min(len(lines), start + 280)
    end = hard_limit - 1
    for j in range(start + 1, hard_limit):
      stripped = lines[j].strip()
      # Rich traceback box end marker.
      if lines[j].startswith("╰"):
        end = j
        if j + 1 < len(lines) and lines[j + 1].strip():
          end = j + 1
        break
      # Plain traceback exception line.
      if stripped.startswith(("SyntaxError:", "TypeError:", "NameError:", "ImportError:",
                  "ModuleNotFoundError:", "FileNotFoundError:", "ValueError:",
                  "RuntimeError:", "Exception:")):
        end = j
        break

    block = lines[start:end + 1]
    if block:
      trace_blocks.append(block)

  if trace_blocks:
    for idx, block in enumerate(trace_blocks, start=1):
      log_excerpt.append(f"--- traceback {idx} ---")
      log_excerpt.extend(block)
  else:
    for line in lines[-220:]:
      if any(k in line for k in ["Syntax", "Traceback", "ERROR", "failed", "validation", "Exception"]):
        log_excerpt.append(line)
    if not log_excerpt:
      log_excerpt = lines[-80:]

print(f"Retry context for phase '{phase}'")
print(f"Attempt: {attempt}/{limit}")
print(f"Generated: {datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}")
print()
print("The previous attempt failed. Fix the failure and execute ONLY this same phase.")
print("Do not modify project_state.json.")
print()
print("Most recent state error:")
print(state_error)
print()
print("Recent build.log excerpt:")
for ln in log_excerpt[-220:]:
    print(ln)
PY
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

render_template_file() {
  local template_file="$1"
  local output_file="$2"
  shift 2

  python3 - "$template_file" "$output_file" "$@" <<'PY'
from pathlib import Path
import sys

template_path = Path(sys.argv[1])
output_path = Path(sys.argv[2])

text = template_path.read_text(encoding="utf-8")
for kv in sys.argv[3:]:
    key, value = kv.split("=", 1)
    text = text.replace("{{" + key + "}}", value)

output_path.write_text(text, encoding="utf-8")
PY
}

# ═══════════════════════════════════════════════════════════════
# Validation Functions
# ═══════════════════════════════════════════════════════════════

validate_scene_template_structure() {
  local scene_file="$1"

  echo "→ Validating template structure in ${scene_file}..." | tee -a "$LOG_FILE"

  local -a required_signatures=(
    "from narration_script import SCRIPT"
    "# LOCKED CONFIGURATION (DO NOT MODIFY)"
    "config.frame_height = 10"
    "config.frame_width = 10 * 16 / 9"
    "config.pixel_height = 1440"
    "config.pixel_width = 2560"
    "self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))"
    "# SLOT_START:scene_body"
    "# SLOT_END:scene_body"
  )

  local sig
  for sig in "${required_signatures[@]}"; do
    if ! grep -Fq "$sig" "$scene_file"; then
      echo "✗ ERROR: Scene is missing required scaffold signature: $sig" | tee -a "$LOG_FILE"
      return 1
    fi
  done

  if ! grep -Eq "with self\\.voiceover\\(text=SCRIPT\\[['\"][^'\"]+['\"]\\]\\) as tracker:" "$scene_file"; then
    echo "✗ ERROR: Scene missing required voiceover wrapper using SCRIPT key" | tee -a "$LOG_FILE"
    return 1
  fi

  python3 - <<PY \
    > >(tee -a "$LOG_FILE") \
    2> >(tee -a "$ERROR_LOG" | tee -a "$LOG_FILE" >&2)
from pathlib import Path

path = Path("${scene_file}")
text = path.read_text(encoding="utf-8", errors="replace")
start = text.find("# SLOT_START:scene_body")
end = text.find("# SLOT_END:scene_body")
if start < 0 or end < 0 or end < start:
    raise SystemExit("invalid slot marker order")
print("✓ Template structure checks passed")
PY

  local result=${PIPESTATUS[0]}
  if [[ $result -ne 0 ]]; then
    echo "✗ ERROR: Scene has invalid slot marker structure" | tee -a "$LOG_FILE"
    return 1
  fi

  return 0
}

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

  # Check for invalid Color import in Manim CE 0.19
  if grep -Eq "from[[:space:]]+manim\.utils\.color[[:space:]]+import[[:space:]]+Color" "$scene_file"; then
    echo "✗ ERROR: Invalid import 'from manim.utils.color import Color'" | tee -a "$LOG_FILE"
    echo "  Manim CE 0.19 does not expose Color there. Use built-in constants (e.g. BLUE) or set_color()." | tee -a "$LOG_FILE"
    return 1
  fi

  # Check for unsupported FadeIn kwargs that repeatedly break renders
  if grep -Eq "FadeIn\([^\n)]*lag_ratio[[:space:]]*=" "$scene_file"; then
    echo "✗ ERROR: FadeIn(..., lag_ratio=...) is unsupported in this Manim version" | tee -a "$LOG_FILE"
    echo "  Use LaggedStart(FadeIn(a), FadeIn(b), ..., lag_ratio=...) for staggered reveals." | tee -a "$LOG_FILE"
    return 1
  fi

  if grep -Eq "FadeIn\([^\n)]*scale_factor[[:space:]]*=" "$scene_file"; then
    echo "✗ ERROR: FadeIn(..., scale_factor=...) is unsupported in this Manim version" | tee -a "$LOG_FILE"
    echo "  Use FadeIn(mobject) only, then animate scaling separately if needed." | tee -a "$LOG_FILE"
    return 1
  fi

  # Check for escaped HTML operators that create Python syntax errors
  if grep -Eq "&lt;|&gt;" "$scene_file"; then
    echo "✗ ERROR: Scene contains escaped HTML operators (&lt;/&gt;)" | tee -a "$LOG_FILE"
    echo "  Replace with real Python operators (<, >, <=, >=)." | tee -a "$LOG_FILE"
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
" \
    > >(tee -a "$LOG_FILE") \
    2> >(tee -a "$ERROR_LOG" | tee -a "$LOG_FILE" >&2)
  
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
  
  # Check: cached voice service is used
  if grep -q "VoiceoverScene" "$scene_file"; then
    if ! grep -q "get_speech_service" "$scene_file"; then
      echo "    ✗ ERROR: Scene missing cached voice service" | tee -a "$LOG_FILE"
      return 1
    fi
  fi
  
  echo "✓ Voiceover sync checks passed" | tee -a "$LOG_FILE"
  return 0
}

validate_scene_runtime() {
  local scene_file="$1"
  local scene_class="$2"

  if [[ -z "$scene_class" ]]; then
    scene_class="$(infer_scene_class_name "$scene_file")"
  fi

  if [[ -z "$scene_class" ]]; then
    echo "✗ ERROR: Could not infer scene class name for runtime validation: ${scene_file}" | tee -a "$LOG_FILE"
    return 1
  fi

  local manim_bin
  manim_bin=$(command -v manim)
  if [[ -z "$manim_bin" ]]; then
    echo "✗ ERROR: manim not found in PATH for runtime validation" | tee -a "$LOG_FILE"
    return 1
  fi

  echo "→ Runtime validating ${scene_file} (${scene_class})..." | tee -a "$LOG_FILE"
  if ! "$manim_bin" render "$scene_file" "$scene_class" --dry_run \
    > >(tee -a "$LOG_FILE") \
    2> >(tee -a "$ERROR_LOG" | tee -a "$LOG_FILE" >&2); then
    echo "✗ Runtime validation failed for ${scene_file}" | tee -a "$LOG_FILE"
    return 1
  fi

  echo "✓ Runtime validation passed for ${scene_file}" | tee -a "$LOG_FILE"
  return 0
}

ensure_qwen_cache_index() {
  local cache_index="${PROJECT_DIR}/media/voiceovers/qwen/cache.json"
  if [[ -f "$cache_index" ]]; then
    return 0
  fi

  echo "→ Voice cache index missing; generating cache before runtime validation..." | tee -a "$LOG_FILE"
  if ! python3 "${SCRIPT_DIR}/precache_voiceovers_qwen.py" "$PROJECT_DIR" \
    > >(tee -a "$LOG_FILE") \
    2> >(tee -a "$ERROR_LOG" | tee -a "$LOG_FILE" >&2); then
    echo "✗ ERROR: Failed to generate voice cache index for runtime validation" | tee -a "$LOG_FILE"
    return 1
  fi

  if [[ ! -f "$cache_index" ]]; then
    echo "✗ ERROR: Precache finished but cache index still missing: $cache_index" | tee -a "$LOG_FILE"
    return 1
  fi

  echo "✓ Voice cache index ready for runtime validation" | tee -a "$LOG_FILE"
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

  local phase_specific_instruction=""
  local build_target_scene_id=""
  local build_target_scene_file=""
  local build_target_scene_class=""
  local build_target_narration_key=""
  local -a build_scene_file_arg=()
  local -a narration_file_arg=()
  if [[ "$phase" == "narration" ]]; then
    if [[ ! -f "$PHASE_NARRATION_TEMPLATE" ]]; then
      echo "❌ Missing prompt template: $PHASE_NARRATION_TEMPLATE" | tee -a "$LOG_FILE" >&2
      return 1
    fi
    phase_specific_instruction="$(cat "$PHASE_NARRATION_TEMPLATE")"
    if [[ -f "plan.json" ]]; then
      narration_file_arg=(--file "plan.json")
    fi
  fi

  if [[ "$phase" == "build_scenes" ]]; then
    if [[ ! -f "$PHASE_BUILD_SCENES_TEMPLATE" ]]; then
      echo "❌ Missing prompt template: $PHASE_BUILD_SCENES_TEMPLATE" | tee -a "$LOG_FILE" >&2
      return 1
    fi

    local build_scene_meta
    build_scene_meta=$(python3 - <<PY
import json
import re

def camel_from_scene_id(scene_id: str) -> str:
    m = re.match(r"^scene_(\d{2})_([a-z0-9_]+)$", scene_id)
    if not m:
        return ""
    num = m.group(1)
    slug = m.group(2)
    parts = [p for p in slug.split("_") if p]
    title = "".join(p.capitalize() for p in parts)
    return f"Scene{num}{title}" if title else f"Scene{num}"

state = json.load(open("${STATE_FILE}", "r"))
idx = int(state.get("current_scene_index") or 0)
scenes = state.get("scenes") or []
if not isinstance(scenes, list) or idx >= len(scenes):
    print("|||")
    raise SystemExit(0)

scene = scenes[idx] if isinstance(scenes[idx], dict) else {}
scene_id = str(scene.get("id") or "")
scene_file = f"{scene_id}.py" if scene_id else ""
scene_class = str(scene.get("class_name") or "")
if not scene_class:
    scene_class = camel_from_scene_id(scene_id)
narration_key = str(scene.get("narration_key") or scene_id)
print(f"{scene_id}|{scene_file}|{scene_class}|{narration_key}")
PY
)
    IFS='|' read -r build_target_scene_id build_target_scene_file build_target_scene_class build_target_narration_key <<< "$build_scene_meta"

    local rendered_build_template=".agent_prompt_${phase}.build.md"
    render_template_file \
      "$PHASE_BUILD_SCENES_TEMPLATE" \
      "$rendered_build_template" \
      "TARGET_SCENE_ID=${build_target_scene_id}" \
      "TARGET_SCENE_FILE=${build_target_scene_file}" \
      "TARGET_SCENE_CLASS=${build_target_scene_class}" \
      "TARGET_NARRATION_KEY=${build_target_narration_key}"
    phase_specific_instruction="$(cat "$rendered_build_template")"
    rm -f "$rendered_build_template"

    if [[ -n "$build_target_scene_file" && -f "$build_target_scene_file" ]]; then
      build_scene_file_arg=(--file "$build_target_scene_file")
    fi
  fi

  local retry_context_file
  retry_context_file="$(get_retry_context_file "$phase")"
  local retry_context_notice=""
  local -a retry_context_arg=()
  if [[ -s "$retry_context_file" ]]; then
    retry_context_notice=$'RETRY CONTEXT:\n- A retry context file is attached. Read it first and fix the exact failure before any new changes.\n'
    retry_context_arg=(--file "$retry_context_file")
  fi
  
  # Create a temporary prompt file
  local prompt_file=".agent_prompt_${phase}.md"
  if [[ ! -f "$PHASE_PROMPT_MAIN_TEMPLATE" ]]; then
    echo "❌ Missing prompt template: $PHASE_PROMPT_MAIN_TEMPLATE" | tee -a "$LOG_FILE" >&2
    return 1
  fi
  if [[ ! -f "$PHASE_PROMPT_TEMPLATE" ]]; then
    echo "❌ Missing prompt template: $PHASE_PROMPT_TEMPLATE" | tee -a "$LOG_FILE" >&2
    return 1
  fi

  local rendered_phase_template=".agent_prompt_${phase}.instructions.md"
  render_template_file \
    "$PHASE_PROMPT_TEMPLATE" \
    "$rendered_phase_template" \
    "PHASE=${phase}" \
    "SCAFFOLD_PATH=${SCRIPT_DIR}/scaffold_scene.py"
  local phase_instructions
  phase_instructions="$(cat "$rendered_phase_template")"
  rm -f "$rendered_phase_template"

  local files_list
  files_list="$(ls -1 "$PROJECT_DIR" 2>/dev/null || echo "  (empty)")"

  PHASE_PROMPT_MAIN_TEMPLATE_PATH="$PHASE_PROMPT_MAIN_TEMPLATE" \
  PHASE="$phase" \
  PROJECT_DIR="$PROJECT_DIR" \
  REPO_ROOT_HINT="${SCRIPT_DIR}/.." \
  SCAFFOLD_PATH="${SCRIPT_DIR}/scaffold_scene.py" \
  FILES_LIST="$files_list" \
  TOPIC="$topic" \
  PHASE_INSTRUCTIONS="$phase_instructions" \
  PHASE_SPECIFIC_REMINDER="$phase_specific_instruction" \
  RETRY_CONTEXT_NOTICE="$retry_context_notice" \
  python3 - <<'PY' > "$prompt_file"
from pathlib import Path
import os

text = Path(os.environ["PHASE_PROMPT_MAIN_TEMPLATE_PATH"]).read_text(encoding="utf-8")
for key in [
    "PHASE",
    "PROJECT_DIR",
    "REPO_ROOT_HINT",
    "SCAFFOLD_PATH",
    "FILES_LIST",
    "TOPIC",
    "PHASE_INSTRUCTIONS",
    "PHASE_SPECIFIC_REMINDER",
    "RETRY_CONTEXT_NOTICE",
]:
    text = text.replace("{{" + key + "}}", os.environ.get(key, ""))
print(text, end="")
PY
  
  # Invoke OpenCode - message must come after all options
  # TODO Replace this with an option to select from available models configured in OpenCode
  local -a opencode_session_args=()
  if [[ -n "${OPENCODE_SESSION_ID}" ]]; then
    opencode_session_args=(--session "${OPENCODE_SESSION_ID}")
  else
    opencode_session_args=(--format json)
  fi
  local opencode_output_file
  opencode_output_file="$(mktemp)"

  opencode run --agent manim-ce-scripting-expert --model "${AGENT_MODEL}" \
    "${opencode_session_args[@]}" \
    --file "$prompt_file" \
    --file "$STATE_FILE" \
    "${narration_file_arg[@]}" \
    "${build_scene_file_arg[@]}" \
    "${retry_context_arg[@]}" \
    -- \
    "Read the first attached file (.agent_prompt_${phase}.md) which contains your complete instructions. Execute the ${phase} phase as described. The current project state is also attached." \
    > >(tee -a "$LOG_FILE" | tee -a "$opencode_output_file") \
    2> >(tee -a "$LOG_FILE" | tee -a "$opencode_output_file" >&2)
  
  # Clean up prompt file
  rm -f "$prompt_file"
  
  local exit_code=${PIPESTATUS[0]}
  capture_opencode_session_id_if_missing "$opencode_output_file"
  rm -f "$opencode_output_file"
  
  if [[ $exit_code -ne 0 ]]; then
    echo "❌ Agent invocation failed with exit code: $exit_code" | tee -a "$LOG_FILE"
    return 1
  fi
  
  echo "[Run $run_num] Agent completed phase: $phase" | tee -a "$LOG_FILE"
}

scene_python_syntax_ok() {
  local scene_file="$1"
  cd "$PROJECT_DIR"
  python3 - <<PY >/dev/null 2>&1
import pathlib
path = pathlib.Path("${scene_file}")
if not path.exists():
    raise SystemExit(1)
compile(path.read_text(encoding="utf-8"), "${scene_file}", "exec")
PY
}

scene_python_syntax_error_excerpt() {
  local scene_file="$1"
  cd "$PROJECT_DIR"
  python3 - <<PY
import pathlib
import traceback

path = pathlib.Path("${scene_file}")
if not path.exists():
    print(f"Scene file missing: {path}")
    raise SystemExit(0)

src = path.read_text(encoding="utf-8", errors="replace")
try:
    compile(src, "${scene_file}", "exec")
    print("No syntax errors detected")
except SyntaxError as e:
    line = e.text.rstrip() if isinstance(e.text, str) else ""
    pointer = ""
    if isinstance(e.offset, int) and e.offset > 0:
        pointer = " " * (e.offset - 1) + "^"
    print(
        f"SyntaxError in {path.name}:{e.lineno}:{e.offset}: {e.msg}"
    )
    if line:
        print(line)
    if pointer:
        print(pointer)
except Exception as e:
    print(f"{type(e).__name__}: {e}")
    tb = traceback.format_exc().splitlines()[-12:]
    print("\n".join(tb))
PY
}

infer_scene_class_name() {
  local scene_file="$1"
  python3 - <<PY
import re
from pathlib import Path

path = Path("${scene_file}")
if not path.exists():
    print("")
    raise SystemExit(0)

try:
    txt = path.read_text(encoding="utf-8")
except Exception:
    print("")
    raise SystemExit(0)

m = re.search(r"^class\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(\s*VoiceoverScene\s*\)\s*:\s*$", txt, re.M)
if m:
    print(m.group(1))
    raise SystemExit(0)

m = re.search(r"^class\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(.*\)\s*:\s*$", txt, re.M)
if m:
    print(m.group(1))
else:
    print("")
PY
}

get_current_scene_id() {
  python3 - <<PY
import json

try:
    state = json.load(open("${STATE_FILE}", "r"))
except Exception:
    state = {}

idx = state.get("current_scene_index", 0)
scenes = state.get("scenes", [])
scene_id = ""
if isinstance(scenes, list) and len(scenes) > idx:
    scene_id = scenes[idx].get("id") or ""

print(scene_id)
PY
}

get_scene_narration_key() {
  local scene_id="$1"
  python3 - <<PY
import json

scene_id = "${scene_id}"
fallback = scene_id or "scene_01"

try:
    state = json.load(open("${STATE_FILE}", "r"))
except Exception:
    state = {}

key = ""
for scene in state.get("scenes", []):
    if isinstance(scene, dict) and scene.get("id") == scene_id:
        value = scene.get("narration_key")
        if isinstance(value, str) and value:
            key = value
        break

print(key or fallback)
PY
}

reset_scene_from_scaffold() {
  local scene_id="$1"
  local scene_file="$2"
  local scene_class="$3"

  if [[ -z "$scene_class" ]]; then
    scene_class="$(infer_scene_class_name "$scene_file")"
  fi
  if [[ -z "$scene_class" ]]; then
    scene_class="Scene$(basename "$scene_file" .py | tr -cd '[:alnum:]_')"
  fi

  local narration_key
  narration_key="$(get_scene_narration_key "$scene_id")"
  if [[ -z "$narration_key" ]]; then
    narration_key="$scene_id"
  fi

  local previous_file
  previous_file="${scene_file}.pre_scaffold_backup"
  if [[ -f "$scene_file" ]]; then
    cp "$scene_file" "$previous_file"
  fi

  if ! python3 "${SCRIPT_DIR}/scaffold_scene.py" \
    --project "$PROJECT_DIR" \
    --scene-id "$scene_file" \
    --class-name "$scene_class" \
    --narration-key "$narration_key" \
    --force \
    >/dev/null 2>&1; then
    echo "✗ ERROR: Failed to scaffold ${scene_file}" | tee -a "$LOG_FILE"
    rm -f "$previous_file"
    return 1
  fi

  if [[ -f "$previous_file" ]]; then
    python3 - <<PY
from pathlib import Path

old_path = Path("${previous_file}")
new_path = Path("${scene_file}")

old_text = old_path.read_text(encoding="utf-8", errors="replace")
new_text = new_path.read_text(encoding="utf-8", errors="replace")

def extract_slot(text, slot_name):
    start_tag = f"# SLOT_START:{slot_name}"
    end_tag = f"# SLOT_END:{slot_name}"
    start = text.find(start_tag)
    end = text.find(end_tag)
    if start < 0 or end < 0 or end < start:
        return None
    body_start = start + len(start_tag)
    return text[body_start:end]

slot = "scene_body"
old_slot = extract_slot(old_text, slot)
new_slot = extract_slot(new_text, slot)
if old_slot is not None and new_slot is not None:
    new_text = new_text.replace(new_slot, old_slot, 1)
    new_path.write_text(new_text, encoding="utf-8")
PY
    rm -f "$previous_file"
  fi

  echo "→ Scaffold reset complete for ${scene_file}" | tee -a "$LOG_FILE"
  return 0
}

extract_recent_error_excerpt() {
  local scene_file="$1"
  python3 - <<PY
from pathlib import Path
import re

log_path = Path("${LOG_FILE}")
if not log_path.exists():
    print("No build.log found")
    raise SystemExit(0)

lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
window = lines[-420:]

# Return the most recent traceback block if available.
starts = [
  i for i, ln in enumerate(window)
  if "Traceback (most recent call last)" in ln or "╭───────────────────── Traceback" in ln
]

if starts:
  start = starts[-1]
  hard_limit = min(len(window), start + 300)
  end = hard_limit - 1
  for j in range(start + 1, hard_limit):
    stripped = window[j].strip()
    if window[j].startswith("╰"):
      end = j
      if j + 1 < len(window) and window[j + 1].strip():
        end = j + 1
      break
    if re.match(r"^(SyntaxError|TypeError|NameError|ImportError|ModuleNotFoundError|FileNotFoundError|ValueError|RuntimeError|Exception):", stripped):
      end = j
      break
  snippet = window[start:end + 1]
  print("\n".join(snippet))
  raise SystemExit(0)

keywords = ["Traceback", "Error", "Exception", "failed", "Syntax", "Indentation"]
filtered = [ln for ln in window if ("${scene_file}" in ln) or any(k in ln for k in keywords)]
snippet = filtered[-180:] if filtered else window[-80:]
print("\n".join(snippet))
PY
}

invoke_scene_fix_agent() {
  local scene_id="$1"
  local scene_file="$2"
  local scene_class="$3"
  local failure_reason="$4"
  local attempt="$5"

  cd "$PROJECT_DIR"

  local prompt_file=".agent_prompt_fix_${scene_id}.md"
  if [[ ! -f "$SCENE_FIX_TEMPLATE" ]]; then
    echo "❌ Missing prompt template: $SCENE_FIX_TEMPLATE" | tee -a "$LOG_FILE" >&2
    return 1
  fi
  SCENE_FIX_TEMPLATE_PATH="$SCENE_FIX_TEMPLATE" \
  SCENE_ID="$scene_id" \
  SCENE_FILE="$scene_file" \
  SCENE_CLASS="$scene_class" \
  ATTEMPT="$attempt" \
  PHASE_RETRY_LIMIT="$PHASE_RETRY_LIMIT" \
  FAILURE_REASON="$failure_reason" \
  python3 - <<'PY' > "$prompt_file"
from pathlib import Path
import os

text = Path(os.environ["SCENE_FIX_TEMPLATE_PATH"]).read_text(encoding="utf-8")
for key in [
    "SCENE_ID",
    "SCENE_FILE",
    "SCENE_CLASS",
    "ATTEMPT",
    "PHASE_RETRY_LIMIT",
    "FAILURE_REASON",
]:
    text = text.replace("{{" + key + "}}", os.environ.get(key, ""))
print(text, end="")
PY

  local -a opencode_session_args=()
  if [[ -n "${OPENCODE_SESSION_ID}" ]]; then
    opencode_session_args=(--session "${OPENCODE_SESSION_ID}")
  else
    opencode_session_args=(--format json)
  fi
  local opencode_output_file
  opencode_output_file="$(mktemp)"

  opencode run --agent manim-ce-scripting-expert --model "${AGENT_MODEL}" \
    "${opencode_session_args[@]}" \
    --file "$prompt_file" \
    --file "$STATE_FILE" \
    --file "$scene_file" \
    -- \
    "Repair ${scene_file} for final_render. Execute only that targeted fix." \
    > >(tee -a "$LOG_FILE" | tee -a "$opencode_output_file") \
    2> >(tee -a "$LOG_FILE" | tee -a "$opencode_output_file" >&2)

  local exit_code=${PIPESTATUS[0]}
  capture_opencode_session_id_if_missing "$opencode_output_file"
  rm -f "$opencode_output_file"
  rm -f "$prompt_file"
  return $exit_code
}

repair_scene_until_valid() {
  local scene_id="$1"
  local scene_file="$2"
  local scene_class="$3"
  local reason="$4"

  local attempt=0
  while [[ $attempt -lt $PHASE_RETRY_LIMIT ]]; do
    attempt=$((attempt + 1))
    echo "🛠 Self-heal scene ${scene_id} attempt ${attempt}/${PHASE_RETRY_LIMIT}" | tee -a "$LOG_FILE"

    if ! reset_scene_from_scaffold "$scene_id" "$scene_file" "$scene_class"; then
      reason="Scaffold reset failed for ${scene_file}."
      continue
    fi

    if validate_scene_template_structure "$scene_file" && \
       validate_scene_imports "$scene_file" && \
       validate_voiceover_sync "$scene_file" && \
       validate_scene_runtime "$scene_file" "$scene_class"; then
      echo "✓ Self-heal reset produced a valid scene file: ${scene_file}" | tee -a "$LOG_FILE"
      return 0
    fi

    if ! invoke_scene_fix_agent "$scene_id" "$scene_file" "$scene_class" "$reason" "$attempt"; then
      reason="Agent repair invocation failed for ${scene_file}."
      continue
    fi

    if ! validate_scene_template_structure "$scene_file"; then
      reason="Scene failed template structure validation after repair."
      continue
    fi

    if ! scene_python_syntax_ok "$scene_file"; then
      reason="$(scene_python_syntax_error_excerpt "$scene_file")"
      continue
    fi

    if ! validate_scene_imports "$scene_file"; then
      reason="Scene failed import validation after repair."
      continue
    fi

    if ! validate_voiceover_sync "$scene_file"; then
      reason="Scene failed voiceover sync validation after repair."
      continue
    fi

    if ! validate_scene_runtime "$scene_file" "$scene_class"; then
      reason=$(extract_recent_error_excerpt "$scene_file")
      continue
    fi

    echo "✓ Self-heal produced a valid scene file: ${scene_file}" | tee -a "$LOG_FILE"
    return 0
  done

  echo "✗ Self-heal exhausted for ${scene_file}" | tee -a "$LOG_FILE"
  return 1
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
    python3 - <<'PY' \
      > >(tee -a "$LOG_FILE") \
      2> >(tee -a "$ERROR_LOG" | tee -a "$LOG_FILE" >&2)
import json
import re
from pathlib import Path
import re

log_path = Path('build.log')
if not log_path.exists():
    raise SystemExit('plan.json missing and build.log not found')

raw = log_path.read_text(encoding='utf-8', errors='replace')
decoder = json.JSONDecoder()

best = None
best_pos = -1

# Look for JSON blocks, possibly wrapped in ```json
json_blocks = re.findall(r'```json\s*(.*?)\s*```', raw, re.DOTALL)
if not json_blocks:
    json_blocks = [raw]  # Fallback to whole log if no markdown blocks

for block in json_blocks:
    for i, ch in enumerate(block):
        if ch != '{':
            continue
        try:
            obj, end = decoder.raw_decode(block[i:])
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict):
            continue
        scenes = obj.get('scenes')
        if not isinstance(scenes, list) or not scenes:
            continue
        # Flexible title/topic_summary: accept 'title', 'video_title', or add if missing
        title = obj.get('title') or obj.get('video_title') or obj.get('project_name') or 'Untitled Video'
        topic_summary = obj.get('topic_summary') or obj.get('core_insight') or 'Summary based on provided topic'
        obj['title'] = title
        obj['topic_summary'] = topic_summary
        # Ensure scenes have required fields if possible
        for scene in scenes:
            if not scene.get('id'):
                scene['id'] = f"scene_{len(scenes) - scenes.index(scene) + 1:02d}"
            if not scene.get('title'):
                scene['title'] = f"Scene {scene.get('id', 'Unknown')}"
            if not scene.get('narration_key'):
                scene['narration_key'] = f"{scene.get('id', 'unknown')}"
        best = obj
        best_pos = i
        break  # Take the first valid one
    if best:
        break

if not best:
    raise SystemExit('plan.json missing and no valid plan JSON object found in build.log')

Path('plan.json').write_text(json.dumps(best, indent=2) + '\n', encoding='utf-8')
print('✓ Recovered and normalized plan.json from build.log')
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
  python3 - <<'PY' \
    > >(tee -a "$LOG_FILE") \
    2> >(tee -a "$ERROR_LOG" | tee -a "$LOG_FILE" >&2)
import json
import re
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
    scene_id = str(s.get('id'))
    if not re.match(r'^scene_[0-9]{2}_[a-z0-9_]+$', scene_id):
        raise SystemExit(
            f"scene[{i}] invalid id '{scene_id}'; expected pattern scene_XX_slug (e.g., scene_01_intro)"
        )
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
    python3 - <<'PY' \
      > >(tee -a "$LOG_FILE") \
      2> >(tee -a "$ERROR_LOG" | tee -a "$LOG_FILE" >&2)
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
  echo "🎙️  Precaching voiceovers (backend: ${FLAMING_HORSE_TTS_BACKEND:-qwen})..." | tee -a "$LOG_FILE"
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
  python3 "${SCRIPT_DIR}/precache_voiceovers_qwen.py" "$PROJECT_DIR" \
    > >(tee -a "$LOG_FILE") \
    2> >(tee -a "$ERROR_LOG" | tee -a "$LOG_FILE" >&2)

  # Deterministically advance if cache index exists.
  normalize_state_json || true
  apply_state_phase "precache_voiceovers" || true
}

handle_build_scenes() {
  echo "🎨 Building scenes..." | tee -a "$LOG_FILE"
  normalize_state_json || true
  cd "$PROJECT_DIR"

  local scene_meta
  scene_meta=$(python3 - <<PY
import json
import re

def camel_from_scene_id(scene_id: str) -> str:
    m = re.match(r"^scene_(\d{2})_([a-z0-9_]+)$", scene_id)
    if not m:
        return ""
    num = m.group(1)
    slug = m.group(2)
    parts = [p for p in slug.split("_") if p]
    title = "".join(p.capitalize() for p in parts)
    return f"Scene{num}{title}" if title else f"Scene{num}"

state = json.load(open("${STATE_FILE}", "r"))
idx = int(state.get("current_scene_index") or 0)
scenes = state.get("scenes") or []
if not isinstance(scenes, list) or idx >= len(scenes):
    print("||||")
    raise SystemExit(0)

scene = scenes[idx] if isinstance(scenes[idx], dict) else {}
scene_id = str(scene.get("id") or "")
narration_key = str(scene.get("narration_key") or scene_id)
scene_class = str(scene.get("class_name") or "")
if not scene_class:
    scene_class = camel_from_scene_id(scene_id)

print(f"{scene_id}|{scene_id}.py|{scene_class}|{narration_key}")
PY
)

  local scene_id scene_file scene_class narration_key
  IFS='|' read -r scene_id scene_file scene_class narration_key <<< "$scene_meta"

  if [[ -z "$scene_id" || -z "$scene_file" || -z "$scene_class" ]]; then
    echo "✗ ERROR: Could not determine current scene metadata from project_state.json" | tee -a "$LOG_FILE" >&2
    return 1
  fi

  if [[ ! "$scene_id" =~ ^scene_[0-9]{2}_[a-z0-9_]+$ ]]; then
    echo "✗ ERROR: Invalid scene id format '${scene_id}'. Expected scene_XX_slug (e.g., scene_01_intro)." | tee -a "$LOG_FILE" >&2
    python3 - <<PY
import json
from datetime import datetime

with open("${STATE_FILE}", "r") as f:
    state = json.load(f)

state.setdefault("errors", []).append("build_scenes failed: scene id must match ^scene_[0-9]{2}_[a-z0-9_]+$")
state.setdefault("flags", {})["needs_human_review"] = True
state["updated_at"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

with open("${STATE_FILE}", "w") as f:
    json.dump(state, f, indent=2)
PY
    return 1
  fi

  if [[ ! -f "$scene_file" ]]; then
    echo "→ Scaffolding deterministic scene file: $scene_file" | tee -a "$LOG_FILE"
    if ! python3 "${SCRIPT_DIR}/scaffold_scene.py" \
      --project "$PROJECT_DIR" \
      --scene-id "$scene_id" \
      --class-name "$scene_class" \
      --narration-key "$narration_key" \
      --force \
      > >(tee -a "$LOG_FILE") \
      2> >(tee -a "$ERROR_LOG" | tee -a "$LOG_FILE" >&2); then
      echo "✗ ERROR: Failed to scaffold ${scene_file}" | tee -a "$LOG_FILE" >&2
      return 1
    fi
  else
    echo "→ Scene scaffold already exists: $scene_file" | tee -a "$LOG_FILE"
  fi

  invoke_agent "build_scenes" "$(get_run_count)"

  # Agent may have produced malformed JSON edits; normalize before reading/writing state.
  normalize_state_json || true

  local new_scene="$scene_file"
  echo "→ Target scene file: $new_scene" | tee -a "$LOG_FILE"

  if ! ensure_qwen_cache_index; then
    echo "✗ Cannot runtime-validate scenes without cached voice data" | tee -a "$LOG_FILE" >&2
    return 1
  fi

  if ! validate_scene_template_structure "$new_scene"; then
    echo "✗ Template structure validation failed for $new_scene. Attempting self-heal..." | tee -a "$LOG_FILE"
    local template_reason
    template_reason=$(extract_recent_error_excerpt "$new_scene")
    if ! repair_scene_until_valid "$scene_id" "$new_scene" "$scene_class" "$template_reason"; then
      echo "✗ Self-heal failed after template validation error in $new_scene" | tee -a "$LOG_FILE" >&2
      return 1
    fi
  fi

  # Syntax validation (Python) with self-heal on failure.
  if ! python3 -m py_compile "$new_scene" \
    > >(tee -a "$LOG_FILE") \
    2> >(tee -a "$ERROR_LOG" | tee -a "$LOG_FILE" >&2); then
    echo "✗ Syntax check failed for $new_scene. Attempting self-heal..." | tee -a "$LOG_FILE"
    local syntax_reason
    syntax_reason=$(scene_python_syntax_error_excerpt "$new_scene")
    if ! repair_scene_until_valid "$scene_id" "$new_scene" "$scene_class" "$syntax_reason"; then
      echo "✗ Self-heal failed after syntax error in $new_scene" | tee -a "$LOG_FILE" >&2
      return 1
    fi
  fi

  # VALIDATION GATE 1: Check imports
  if ! validate_scene_imports "$new_scene"; then
    echo "✗ Import validation failed for $new_scene. Attempting self-heal..." | tee -a "$LOG_FILE"
    local import_reason
    import_reason=$(extract_recent_error_excerpt "$new_scene")
    if ! repair_scene_until_valid "$scene_id" "$new_scene" "$scene_class" "$import_reason"; then
      echo "✗ Self-heal failed after import/API error in $new_scene" | tee -a "$LOG_FILE" >&2
      return 1
    fi
  fi
  
  # VALIDATION GATE 2: Check voiceover sync patterns
  if ! validate_voiceover_sync "$new_scene"; then
    echo "✗ Voiceover sync validation failed for $new_scene. Attempting self-heal..." | tee -a "$LOG_FILE"
    local sync_reason
    sync_reason=$(extract_recent_error_excerpt "$new_scene")
    if ! repair_scene_until_valid "$scene_id" "$new_scene" "$scene_class" "$sync_reason"; then
      echo "✗ Self-heal failed after sync error in $new_scene" | tee -a "$LOG_FILE" >&2
      return 1
    fi
  fi

  # Runtime validation gate: catch construct/animation API failures now,
  # before advancing to the next scene.
  if ! validate_scene_runtime "$new_scene" "$scene_class"; then
    echo "✗ Runtime validation failed for $new_scene. Attempting self-heal..." | tee -a "$LOG_FILE"
    local runtime_reason
    runtime_reason=$(extract_recent_error_excerpt "$new_scene")
    if ! repair_scene_until_valid "$scene_id" "$new_scene" "$scene_class" "$runtime_reason"; then
      echo "✗ Self-heal failed after runtime error in $new_scene" | tee -a "$LOG_FILE" >&2
      return 1
    fi
  fi

  echo "✓ Validation passed for $new_scene" | tee -a "$LOG_FILE"
  
  # Deterministically mark this scene built and advance index/phase.
  apply_state_phase "build_scenes" || true

  return 0
}

handle_scene_qc() {
  echo "🧪 Running scene QC pass..." | tee -a "$LOG_FILE"
  cd "$PROJECT_DIR"

  local qc_scene_files
  qc_scene_files=$(python3 - <<PY
import json
from pathlib import Path

state = json.load(open("${STATE_FILE}", "r"))
scenes = state.get("scenes") or []
files = []
for s in scenes:
    if not isinstance(s, dict):
        continue
    f = s.get("file")
    if isinstance(f, str) and f:
        files.append(f)

if not files:
    print("")
    raise SystemExit(0)

missing = [f for f in files if not Path(f).exists()]
if missing:
    print("MISSING:" + ",".join(missing))
else:
    print("\n".join(files))
PY
)

  if [[ -z "$qc_scene_files" ]]; then
    echo "❌ No scene files listed in project_state.json for QC" | tee -a "$LOG_FILE" >&2
    return 1
  fi

  if [[ "$qc_scene_files" == MISSING:* ]]; then
    echo "❌ QC cannot run; missing scene files: ${qc_scene_files#MISSING:}" | tee -a "$LOG_FILE" >&2
    return 1
  fi

  local prompt_file=".agent_prompt_scene_qc.md"
  if [[ ! -f "$SCENE_QC_TEMPLATE" ]]; then
    echo "❌ Missing prompt template: $SCENE_QC_TEMPLATE" | tee -a "$LOG_FILE" >&2
    return 1
  fi
  render_template_file \
    "$SCENE_QC_TEMPLATE" \
    "$prompt_file" \
    "PROJECT_DIR=${PROJECT_DIR}" \
    "STATE_FILE=${STATE_FILE}" \
    "SCENE_FILES=${qc_scene_files}"

  local -a opencode_session_args=()
  if [[ -n "${OPENCODE_SESSION_ID}" ]]; then
    opencode_session_args=(--session "${OPENCODE_SESSION_ID}")
  else
    opencode_session_args=(--format json)
  fi
  local opencode_output_file
  opencode_output_file="$(mktemp)"

  opencode run --agent manim-ce-scripting-expert --model "${AGENT_MODEL}" \
    "${opencode_session_args[@]}" \
    --file "$prompt_file" \
    --file "$STATE_FILE" \
    -- \
    "Read .agent_prompt_scene_qc.md and execute the QC pass. Patch the scene files listed from project_state.json and write scene_qc_report.md." \
    > >(tee -a "$LOG_FILE" | tee -a "$opencode_output_file") \
    2> >(tee -a "$LOG_FILE" | tee -a "$opencode_output_file" >&2)

  local exit_code=${PIPESTATUS[0]}
  capture_opencode_session_id_if_missing "$opencode_output_file"
  rm -f "$opencode_output_file"
  if [[ $exit_code -ne 0 ]]; then
    # Some environments do not expose the pinned xai model to opencode.
    # Fallback to the user's default configured model for this QC pass.
    if tail -n 120 "$LOG_FILE" | grep -q "ProviderModelNotFoundError"; then
      echo "⚠ Requested model unavailable for scene_qc; retrying with default model..." | tee -a "$LOG_FILE"
      local -a fallback_session_args=()
      if [[ -n "${OPENCODE_SESSION_ID}" ]]; then
        fallback_session_args=(--session "${OPENCODE_SESSION_ID}")
      else
        fallback_session_args=(--format json)
      fi
      local fallback_output_file
      fallback_output_file="$(mktemp)"

      opencode run --agent manim-ce-scripting-expert \
        "${fallback_session_args[@]}" \
        --file "$prompt_file" \
        --file "$STATE_FILE" \
        -- \
        "Read .agent_prompt_scene_qc.md and execute the QC pass. Patch the scene files listed from project_state.json and write scene_qc_report.md." \
        > >(tee -a "$LOG_FILE" | tee -a "$fallback_output_file") \
        2> >(tee -a "$LOG_FILE" | tee -a "$fallback_output_file" >&2)
      exit_code=${PIPESTATUS[0]}
      capture_opencode_session_id_if_missing "$fallback_output_file"
      rm -f "$fallback_output_file"
    fi
  fi

  rm -f "$prompt_file"

  if [[ $exit_code -ne 0 ]]; then
    echo "❌ Scene QC agent failed with exit code: $exit_code" | tee -a "$LOG_FILE"
    return 1
  fi

  if [[ ! -s "scene_qc_report.md" ]]; then
    echo "❌ scene_qc_report.md missing or empty after scene QC" | tee -a "$LOG_FILE" >&2
    return 1
  fi

  echo "✓ Scene QC complete: scene_qc_report.md" | tee -a "$LOG_FILE"
  apply_state_phase "scene_qc" || true
  return 0
}

handle_final_render() {
  echo "🎬 Final render with cached voiceover (backend: ${FLAMING_HORSE_TTS_BACKEND:-qwen})..." | tee -a "$LOG_FILE"
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

  # Ensure voice cache exists (precache step). If missing, generate it now.
  if [[ ! -f "media/voiceovers/qwen/cache.json" ]]; then
    echo "→ Missing voice cache index; running precache step..." | tee -a "$LOG_FILE"
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
  STATE_FILE="$STATE_FILE" PROJECT_DIR="$PROJECT_DIR" python3 - <<'PY'
import json
import os
import re
from datetime import datetime
from typing import Optional

state_file = os.environ.get("STATE_FILE")
project_dir = os.environ.get("PROJECT_DIR")
if not state_file or not project_dir:
    raise SystemExit(0)

with open(state_file, "r") as f:
    state = json.load(f)

scenes = state.get("scenes") or []
changed = False
notes = []

def infer_class_name(scene_path: str) -> Optional[str]:
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

  echo "→ Rendering scenes sequentially (cached voice backend: ${FLAMING_HORSE_TTS_BACKEND:-qwen})" | tee -a "$LOG_FILE"

  while IFS='|' read -r scene_id scene_file scene_class est_duration; do
    [[ -n "$scene_id" ]] || continue

    # Pre-render syntax gate with self-healing.
    if ! scene_python_syntax_ok "$scene_file"; then
      echo "⚠ Pre-render syntax check failed for ${scene_file}. Starting self-heal..." | tee -a "$LOG_FILE"
      local syntax_reason
      syntax_reason=$(extract_recent_error_excerpt "$scene_file")
      if ! repair_scene_until_valid "$scene_id" "$scene_file" "$scene_class" "$syntax_reason"; then
        echo "❌ Could not repair ${scene_file} after ${PHASE_RETRY_LIMIT} attempts" | tee -a "$LOG_FILE" >&2
        python3 - <<PY
import json
from datetime import datetime

with open("${STATE_FILE}", "r") as f:
    state = json.load(f)

state.setdefault("errors", []).append("final_render failed: scene ${scene_id} self-heal exhausted")
state.setdefault("flags", {})["needs_human_review"] = True
state["updated_at"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

with open("${STATE_FILE}", "w") as f:
    json.dump(state, f, indent=2)
PY
        exit 1
      fi
    fi

    # Pre-render guardrail: catch known invalid animations (e.g., ShowCreation).
    if grep -q "ShowCreation" "$scene_file"; then
      echo "⚠ Invalid animation detected (ShowCreation) in ${scene_file}. Starting self-heal..." | tee -a "$LOG_FILE"
      local invalid_reason
      invalid_reason="Invalid animation 'ShowCreation' detected. Use Create(...) for mobjects/curves." 
      if ! repair_scene_until_valid "$scene_id" "$scene_file" "$scene_class" "$invalid_reason"; then
        echo "❌ Could not repair ${scene_file} after ${PHASE_RETRY_LIMIT} attempts" | tee -a "$LOG_FILE" >&2
        python3 - <<PY
import json
from datetime import datetime

with open("${STATE_FILE}", "r") as f:
    state = json.load(f)

state.setdefault("errors", []).append("final_render failed: invalid animation in scene ${scene_id} (ShowCreation)")
state.setdefault("flags", {})["needs_human_review"] = True
state["updated_at"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

with open("${STATE_FILE}", "w") as f:
    json.dump(state, f, indent=2)
PY
        exit 1
      fi
    fi

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

    # Scene-level retry + self-heal loop with error feedback.
    local attempt=0
    local ok=0
    local failure_reason=""
    while [[ $attempt -lt $PHASE_RETRY_LIMIT ]]; do
      attempt=$((attempt + 1))

      local transient_attempt=0
      local transient_max_attempts=5
      local backoff=10
      local render_ok=0
      local render_log="${PROJECT_DIR}/render_log_${scene_id}.tmp"
      while [[ $transient_attempt -lt $transient_max_attempts ]]; do
        transient_attempt=$((transient_attempt + 1))

        if "$manim_bin" render "$scene_file" "$scene_class" -qh \
          > >(tee -a "$LOG_FILE" | tee "$render_log") \
          2> >(tee -a "$ERROR_LOG" | tee -a "$LOG_FILE" | tee -a "$render_log" >&2); then
          render_ok=1
          break
        fi

        # If it looks like a transient voiceover error, wait and retry.
        if tail -n 200 "$LOG_FILE" | grep -q "too_many_concurrent_requests"; then
          echo "⚠ Voiceover concurrency limit hit; retrying in ${backoff}s (attempt ${transient_attempt}/${transient_max_attempts})" | tee -a "$LOG_FILE"
          sleep "$backoff"
          backoff=$((backoff * 2))
          continue
        fi

        break
      done

      if [[ $render_ok -eq 1 ]]; then
        ok=1
        rm -f "$render_log"
        break
      fi

      failure_reason=$(tail -n 80 "$render_log" 2>/dev/null | grep -A8 -B4 -E "Traceback|NameError|ImportError|SyntaxError|Exception" || true)
      if [[ -z "$failure_reason" ]]; then
        failure_reason="Render failed for ${scene_id}; see build.log for details."
      fi

      if [[ $attempt -ge $PHASE_RETRY_LIMIT ]]; then
        break
      fi

      echo "⚠ Render failed for ${scene_id}; attempting self-heal (${attempt}/${PHASE_RETRY_LIMIT})" | tee -a "$LOG_FILE"
      if ! repair_scene_until_valid "$scene_id" "$scene_file" "$scene_class" "$failure_reason"; then
        break
      fi
    done

    if [[ $ok -ne 1 ]]; then
      echo "❌ Render failed for $scene_id ($scene_class)" | tee -a "$LOG_FILE" >&2
      python3 - <<PY
import json
from datetime import datetime

scene_id = "${scene_id}"
failure_reason = """${failure_reason}"""

with open("${STATE_FILE}", "r") as f:
    state = json.load(f)

state.setdefault("errors", []).append(f"final_render failed for {scene_id}: {failure_reason}")
state.setdefault("flags", {})["needs_human_review"] = False
state["phase"] = "build_scenes"
state["updated_at"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

for i, s in enumerate(state.get("scenes", [])):
    if s.get("id") == scene_id:
        state["current_scene_index"] = i
        s["status"] = "pending"
        break

state.setdefault("history", []).append({
    "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    "phase": "final_render",
    "scene": scene_id,
    "action": "revert_to_build_scenes",
    "reason": failure_reason,
})

with open("${STATE_FILE}", "w") as f:
    json.dump(state, f, indent=2)
PY
      rm -f "${PROJECT_DIR}/render_log_${scene_id}.tmp"
      return 1
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
  python3 "${SCRIPT_DIR}/generate_scenes_txt.py" "$PROJECT_DIR" \
    > >(tee -a "$LOG_FILE") \
    2> >(tee -a "$ERROR_LOG" | tee -a "$LOG_FILE" >&2)

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
state.setdefault("errors", []).append("Assemble incomplete: one or more scene video files are missing; routing back to final_render")
state.setdefault("flags", {})["needs_human_review"] = False
state["phase"] = "final_render"
state["updated_at"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
state.setdefault("history", []).append({
    "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    "phase": "assemble",
    "action": "Missing scene inputs detected; moved phase back to final_render",
})
with open("${STATE_FILE}", "w") as f:
    json.dump(state, f, indent=2)
PY
    return 0
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
  if ! ffmpeg -y \
    "${ffmpeg_inputs[@]}" \
    -filter_complex "$filter_complex" \
    -map "[v]" -map "[aout]" \
    -c:v libx264 -pix_fmt yuv420p -crf 18 -preset medium \
    -c:a aac -b:a 192k -ar 48000 \
    -movflags +faststart \
    "${PROJECT_DIR}/final_video.mp4" \
    > >(tee -a "$LOG_FILE") \
    2> >(tee -a "$LOG_FILE" >&2); then
    echo "❌ ffmpeg assembly command failed" | tee -a "$LOG_FILE" >&2
    python3 - <<PY
import json
from datetime import datetime
with open("${STATE_FILE}", "r") as f:
    state = json.load(f)
state.setdefault("errors", []).append("assemble failed: ffmpeg concat command failed")
state.setdefault("flags", {})["needs_human_review"] = False
state["updated_at"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
with open("${STATE_FILE}", "w") as f:
    json.dump(state, f, indent=2)
PY
    return 1
  fi

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

run_phase_once() {
  local phase="$1"
  local rc=0

  set +e
  case "$phase" in
    init) handle_init ;;
    plan) handle_plan ;;
    review) handle_review ;;
    narration) handle_narration ;;
    build_scenes) handle_build_scenes ;;
    scene_qc) handle_scene_qc ;;
    precache_voiceovers) handle_precache_voiceovers ;;
    final_render) handle_final_render ;;
    assemble) handle_assemble ;;
    complete) handle_complete ;;
    *) echo "❌ Unknown phase: $phase" >&2; rc=1 ;;
  esac
  rc=$?
  set -e
  return $rc
}

mark_retry_exhausted() {
  local phase="$1"

  python3 - <<PY
import json
from datetime import datetime

with open("${STATE_FILE}", "r") as f:
    state = json.load(f)

state.setdefault("errors", []).append(
    "Phase ${phase} failed after ${PHASE_RETRY_LIMIT} attempts: see build.log"
)
state.setdefault("flags", {})["needs_human_review"] = True
state["updated_at"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
state.setdefault("history", []).append(
    {
        "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        "phase": "${phase}",
        "action": "retry_exhausted",
        "reason": "self-healing attempts exhausted",
    }
)

with open("${STATE_FILE}", "w") as f:
    json.dump(state, f, indent=2)
PY
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
    
    local phase_ok=0
    local attempt=0
    local phase_retry_file
    phase_retry_file="$(get_retry_context_file "$current_phase")"

    while true; do
      attempt=$((attempt + 1))
      if [[ $attempt -gt 1 ]]; then
        echo "↻ Retry attempt ${attempt}/${PHASE_RETRY_LIMIT} for phase: $current_phase" | tee -a "$LOG_FILE"
      fi

      if run_phase_once "$current_phase"; then
        phase_ok=1
        rm -f "$phase_retry_file"
        break
      fi

      normalize_state_json || true
      local fail_needs_review
      fail_needs_review=$(python3 -c "import json; print(json.load(open('${STATE_FILE}'))['flags'].get('needs_human_review', False))")
      if [[ "$fail_needs_review" == "True" ]]; then
        break
      fi

      if ! is_retryable_phase "$current_phase"; then
        break
      fi

      if [[ $attempt -ge $PHASE_RETRY_LIMIT ]]; then
        break
      fi

      echo "⚠ Phase $current_phase failed (attempt ${attempt}/${PHASE_RETRY_LIMIT}). Preparing retry context for agent..." | tee -a "$LOG_FILE"
      build_retry_context "$current_phase" "$attempt"
      sleep "$PHASE_RETRY_BACKOFF_SECONDS"
    done

    if [[ $phase_ok -ne 1 ]]; then
      if is_retryable_phase "$current_phase"; then
        echo "❌ Phase $current_phase failed after ${PHASE_RETRY_LIMIT} attempts. Marking for human review." | tee -a "$LOG_FILE"
        mark_retry_exhausted "$current_phase"
      else
        echo "❌ Phase $current_phase failed (non-agent phase)." | tee -a "$LOG_FILE"
      fi

      normalize_state_json || true
      local needs_review_fail
      needs_review_fail=$(python3 -c "import json; print(json.load(open('${STATE_FILE}'))['flags'].get('needs_human_review', False))")
      if [[ "$needs_review_fail" == "True" ]]; then
        echo "⚠️  Human review required. Pausing build loop." | tee -a "$LOG_FILE"
        echo "Check $STATE_FILE for details" | tee -a "$LOG_FILE"
        exit 0
      fi

      exit 1
    fi

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
  
  local stopped_phase
  stopped_phase="$(get_phase)"
  echo "⚠️  Maximum iterations ($MAX_RUNS) reached. Stopping at phase: ${stopped_phase}." | tee -a "$LOG_FILE"
  echo "   Note: --max-runs counts phase-loop iterations, not full end-to-end completion." | tee -a "$LOG_FILE"
  exit 1
}

main "$@"
