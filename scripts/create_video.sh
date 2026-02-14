#!/usr/bin/env bash
set -euo pipefail

# Force offline mode for all HuggingFace/Transformers usage in this pipeline.
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export TOKENIZERS_PARALLELISM=false

usage() {
  cat <<'EOF'
Usage:
  ./scripts/create_video.sh <project_name> [--topic "..."] [--projects-dir <dir>] [--build-args "..."] [--mock]

Examples:
  ./scripts/create_video.sh semi_prime_factorization --topic "Create a video about factoring semi primes"
  ./scripts/create_video.sh my-video --topic "Explain hash functions" --build-args "--topic 'ignored'"
  ./scripts/create_video.sh test_video --topic "Test video" --mock

Options:
  --mock              Use mock voice service (dummy audio, no Qwen setup needed)

Notes:
  - This script is a thin wrapper around:
      1) scripts/new_project.sh
      2) scripts/build_video.sh
  - For reliability, it also warms up the voice service once before building.
  - --build-args is parsed like a shell command line (quotes supported).
  - You can also provide the topic via VIDEO_TOPIC.
  - PROJECTS_BASE_DIR sets the default for --projects-dir when omitted.
  - If the project already exists (has project_state.json), this script resumes it and does NOT reinitialize state.
  - Set FLAMING_HORSE_MOCK_VOICE=1 to use mock voice service globally.
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(realpath "${SCRIPT_DIR}/..")"
ENV_FILE="${REPO_ROOT}/.env"

if [[ -f "${ENV_FILE}" ]]; then
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
fi

PROJECT_NAME="${1:-}"
if [[ -z "${PROJECT_NAME}" ]]; then
  usage >&2
  exit 1
fi
if [[ "${PROJECT_NAME}" == "-h" ]] || [[ "${PROJECT_NAME}" == "--help" ]]; then
  usage
  exit 0
fi
shift

TOPIC=""
PROJECTS_DIR="${PROJECTS_BASE_DIR:-./projects}"
BUILD_ARGS_STR=""
USE_MOCK=0
INITIAL_PWD="$(pwd)"

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
    --build-args)
      BUILD_ARGS_STR="${2:-}"
      if [[ -z "${BUILD_ARGS_STR}" ]]; then
        echo "❌ Missing value for --build-args" >&2
        usage >&2
        exit 1
      fi
      shift 2
      ;;
    --mock)
      USE_MOCK=1
      shift
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

if [[ "${PROJECTS_DIR}" = /* ]]; then
  PROJECTS_DIR_RAW="${PROJECTS_DIR}"
else
  PROJECTS_DIR_RAW="${INITIAL_PWD}/${PROJECTS_DIR}"
fi
PROJECTS_DIR="$(python3 -c 'import os,sys; print(os.path.abspath(sys.argv[1]))' "${PROJECTS_DIR_RAW}")"

PROJECT_DIR="${PROJECTS_DIR%/}/${PROJECT_NAME}"
STATE_FILE="${PROJECT_DIR}/project_state.json"

TOPIC="${TOPIC:-${VIDEO_TOPIC:-}}"

RESUME_MODE=0
if [[ -f "${STATE_FILE}" ]]; then
  RESUME_MODE=1
fi

if [[ $RESUME_MODE -eq 0 && -d "${PROJECT_DIR}" && ! -f "${STATE_FILE}" ]]; then
  echo "❌ Project directory exists but no project_state.json found:" >&2
  echo "   ${PROJECT_DIR}" >&2
  echo "   Cannot safely resume or initialize over an unknown directory." >&2
  exit 1
fi

if [[ $RESUME_MODE -eq 0 && -z "${TOPIC}" ]]; then
  echo "❌ No topic provided for new project." >&2
  echo "   Provide --topic \"...\" or set VIDEO_TOPIC." >&2
  exit 1
fi

# Set mock voice mode if requested
if [[ $USE_MOCK -eq 1 ]]; then
  export FLAMING_HORSE_MOCK_VOICE=1
  echo "→ Mock voice mode enabled (FLAMING_HORSE_MOCK_VOICE=1)"
fi

if [[ $RESUME_MODE -eq 1 ]]; then
  echo "→ Existing project detected; resuming without reinitialization: ${PROJECT_DIR}"
else
  "${SCRIPT_DIR}/new_project.sh" "${PROJECT_NAME}" --topic "${TOPIC}" --projects-dir "${PROJECTS_DIR}"
fi

echo ""
echo "═══════════════════════════════════════════"
echo "Preparing voice service"
echo "═══════════════════════════════════════════"

python3 "${SCRIPT_DIR}/prepare_voice_service.py" --project-dir "${PROJECT_DIR}"
echo "✓ Voice service preparation complete"

BUILD_ARGS=()
if [[ -n "${BUILD_ARGS_STR}" ]]; then
  while IFS= read -r -d '' arg; do
    BUILD_ARGS+=("$arg")
  done < <(BUILD_ARGS_STR="${BUILD_ARGS_STR}" python3 - <<'PY'
import os
import shlex
import sys

s = os.environ.get("BUILD_ARGS_STR", "")
args = shlex.split(s)
if args:
    sys.stdout.write("\0".join(args) + "\0")
PY
)
fi

exec "${SCRIPT_DIR}/build_video.sh" "${PROJECT_DIR}" "${BUILD_ARGS[@]}"
