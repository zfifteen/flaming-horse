#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  ./scripts/create_video.sh <project_name> --topic "..." [--projects-dir <dir>] [--build-args "..."]

Examples:
  ./scripts/create_video.sh semi_prime_factorization --topic "Create a video about factoring semi primes"
  ./scripts/create_video.sh my-video --topic "Explain hash functions" --build-args "--topic 'ignored'"

Notes:
  - This script is a thin wrapper around:
      1) scripts/new_project.sh
      2) scripts/build_video.sh
  - For reliability, it also warms up the local Qwen voice clone once before building.
  - --build-args is parsed like a shell command line (quotes supported).
  - You can also provide the topic via VIDEO_TOPIC.
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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
PROJECTS_DIR="./projects"
BUILD_ARGS_STR=""

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
if [[ -z "${TOPIC}" ]]; then
  echo "❌ No topic provided." >&2
  echo "   Provide --topic \"...\" or set VIDEO_TOPIC." >&2
  exit 1
fi

PROJECT_DIR="${PROJECTS_DIR%/}/${PROJECT_NAME}"

"${SCRIPT_DIR}/new_project.sh" "${PROJECT_NAME}" --topic "${TOPIC}" --projects-dir "${PROJECTS_DIR}"

# Auto-detect mock mode: if the Qwen python path from voice_clone_config.json
# does not exist, enable MOCK_QWEN so the pipeline uses dummy audio instead
# of failing on the missing model.
if [[ -z "${MOCK_QWEN:-}" ]]; then
  _qwen_py=$(python3 -c "
import json, os, pathlib
cfg = json.load(open('${PROJECT_DIR}/voice_clone_config.json'))
p = cfg.get('qwen_python','')
print(os.path.expanduser(p) if p else '')
" 2>/dev/null || true)
  if [[ -z "${_qwen_py}" ]] || [[ ! -x "${_qwen_py}" ]]; then
    echo "⚠ Qwen python not found (${_qwen_py:-<unset>}); enabling MOCK_QWEN=1"
    export MOCK_QWEN=1
  fi
fi

echo ""
echo "═══════════════════════════════════════════"
echo "Warming up Qwen voice model (reliability)"
echo "═══════════════════════════════════════════"

python3 "${SCRIPT_DIR}/prepare_qwen_voice.py" --project-dir "${PROJECT_DIR}"
echo "✓ Qwen voice warm-up complete"

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
