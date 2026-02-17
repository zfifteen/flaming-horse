#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(realpath "${SCRIPT_DIR}/..")"
ENV_FILE="${REPO_ROOT}/.env"

if [[ -f "${ENV_FILE}" ]]; then
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
fi

usage() {
  cat <<EOF
Usage:
  $0 <project_name> [projects_dir]
  $0 <project_name> --topic "<video topic>" [--projects-dir <projects_dir>]

Environment:
  VIDEO_TOPIC can be used instead of --topic.
  PROJECTS_BASE_DIR sets the default project directory root.
  See ./scripts/help.sh for the full command guide.
EOF
}

PROJECT_NAME="${1:-}"
if [[ "${PROJECT_NAME}" == "-h" || "${PROJECT_NAME}" == "--help" ]]; then
  usage
  exit 0
fi
if [[ -z "${PROJECT_NAME}" ]]; then
  usage >&2
  exit 1
fi
shift

TOPIC=""
PROJECTS_DIR="${PROJECTS_BASE_DIR:-./projects}"
INITIAL_PWD="$(pwd)"

# Backwards compatible positional projects_dir support.
if [[ ${#} -gt 0 && "${1}" != --* ]]; then
  PROJECTS_DIR="${1}"
  shift
fi

while [[ ${#} -gt 0 ]]; do
  case "${1}" in
    --topic)
      TOPIC="${2:-}"
      if [[ -z "${TOPIC}" ]]; then
        echo "❌ Missing value for --topic" >&2
        usage >&2
        exit 1
      fi
      shift 2
      ;;
    --projects-dir)
      PROJECTS_DIR="${2:-}"
      if [[ -z "${PROJECTS_DIR}" ]]; then
        echo "❌ Missing value for --projects-dir" >&2
        usage >&2
        exit 1
      fi
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "❌ Unknown argument: ${1}" >&2
      usage >&2
      exit 1
      ;;
  esac
done

TOPIC="${TOPIC:-${VIDEO_TOPIC:-}}"

if [[ -n "${TOPIC}" && -f "${TOPIC}" ]]; then
  TOPIC_CONTENT=$(cat "${TOPIC}")
  if [[ -n "${TOPIC_CONTENT}" ]]; then
    TOPIC="${TOPIC_CONTENT}"
    echo "→ Loaded topic content from file: ${TOPIC}" | head -c 100  # Truncate for logging
  else
    echo "❌ Topic file is empty: ${TOPIC}" >&2
    exit 1
  fi
fi

TOPIC_JSON="null"
if [[ -n "${TOPIC}" ]]; then
  TOPIC_JSON="$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "${TOPIC}")"
fi

if [[ "${PROJECTS_DIR}" = /* ]]; then
  PROJECTS_DIR_RAW="${PROJECTS_DIR}"
else
  PROJECTS_DIR_RAW="${INITIAL_PWD}/${PROJECTS_DIR}"
fi
PROJECTS_DIR="$(python3 -c 'import os,sys; print(os.path.abspath(sys.argv[1]))' "${PROJECTS_DIR_RAW}")"

PROJECT_DIR="${PROJECTS_DIR}/${PROJECT_NAME}"

mkdir -p "$PROJECT_DIR"

# Default Qwen voice clone config (local, CPU float32)
mkdir -p "$PROJECT_DIR/assets/voice_ref"
cat > "$PROJECT_DIR/voice_clone_config.json" <<'EOF'
{
  "qwen_python": "~/IdeaProjects/flaming-horse/models/qwen3-tts-local/.venv/bin/python",
  "model_id": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
  "device": "cpu",
  "dtype": "float32",
  "language": "English",
  "ref_audio": "assets/voice_ref/ref.wav",
  "ref_text": "assets/voice_ref/ref.txt",
  "output_dir": "media/voiceovers/qwen"
}
EOF

# Seed per-project voice reference assets if missing.
# The voice pipeline requires these files to exist on disk.
#
# You can override the template directory via VOICE_REF_TEMPLATE_DIR.
ref_template_dir="${VOICE_REF_TEMPLATE_DIR:-${SCRIPT_DIR}/../assets/voice_ref}"
if [[ ! -f "$PROJECT_DIR/assets/voice_ref/ref.wav" || ! -f "$PROJECT_DIR/assets/voice_ref/ref.txt" ]]; then
  if [[ -f "$ref_template_dir/ref.wav" && -f "$ref_template_dir/ref.txt" ]]; then
    cp -a "$ref_template_dir/ref.wav" "$PROJECT_DIR/assets/voice_ref/ref.wav"
    cp -a "$ref_template_dir/ref.txt" "$PROJECT_DIR/assets/voice_ref/ref.txt"
  else
    echo "❌ Missing voice reference assets for Qwen voice clone." >&2
    echo "   Expected: $PROJECT_DIR/assets/voice_ref/ref.wav and ref.txt" >&2
    echo "   Provide a template dir via VOICE_REF_TEMPLATE_DIR, or place those files manually." >&2
    echo "   Tried template: $ref_template_dir" >&2
    exit 1
  fi
fi

cat > "$PROJECT_DIR/project_state.json" <<EOF
{
  "project_name": "$PROJECT_NAME",
  "topic": ${TOPIC_JSON},
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
echo "📝 State file: $PROJECT_DIR/project_state.json"
if [[ -n "${TOPIC}" ]]; then
  echo "🧠 Topic: ${TOPIC}"
fi
echo ""
echo "Next steps:"
echo "  1. Recommended: ./scripts/create_video.sh $PROJECT_NAME --topic \"...\""
echo "  2. Advanced/manual: ./scripts/build_video.sh $PROJECT_DIR"
