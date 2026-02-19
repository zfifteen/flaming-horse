#!/usr/bin/env bash
# Verify all required dependencies before running pipeline

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(realpath "${SCRIPT_DIR}/..")"
ENV_FILE="${REPO_ROOT}/.env"
MIN_MANIM_VERSION="${MIN_MANIM_VERSION:-0.18.0}"

usage() {
  cat <<EOF
Usage:
  $0 [--project-dir <project_dir>]

Checks:
  - System dependencies (python3, manim, ffmpeg, sox)
  - Python packages (manim, manim_voiceover_plus)
  - Required env var (XAI_API_KEY)
  - Manim minimum version (>= ${MIN_MANIM_VERSION})
  - Voice reference/template consistency

Examples:
  $0
  $0 --project-dir projects/my_video
EOF
}

PROJECT_DIR=""
while [[ ${#} -gt 0 ]]; do
  case "${1}" in
    --project-dir)
      PROJECT_DIR="${2:-}"
      if [[ -z "${PROJECT_DIR}" ]]; then
        echo "✗ Missing value for --project-dir"
        usage
        exit 1
      fi
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "✗ Unknown argument: ${1}"
      usage
      exit 1
      ;;
  esac
done

# Source .env for environment variables (e.g., FLAMING_HORSE_VOICE_REF_DIR)
if [[ -f "${ENV_FILE}" ]]; then
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
fi

errors=0
warnings=0
PYTHON_BIN="python3"

echo "Checking dependencies..."
echo ""

# Required API key for harness phases
if [[ -n "${XAI_API_KEY:-}" ]]; then
  echo "✓ XAI_API_KEY is set"
else
  echo "✗ XAI_API_KEY is not set (required for harness execution)"
  errors=$((errors+1))
fi

# Python
if command -v "${PYTHON_BIN}" >/dev/null; then
  version=$("${PYTHON_BIN}" --version | awk '{print $2}')
  python_minor=$("${PYTHON_BIN}" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
  echo "✓ Python $version"
else
  echo "✗ Python 3 not found"
  errors=$((errors+1))
fi

# pip/python interpreter alignment check (common source of false negatives)
if command -v pip >/dev/null && command -v "${PYTHON_BIN}" >/dev/null; then
  pip_python_minor=$(pip --version 2>/dev/null | awk 'match($0, /\(python [0-9]+\.[0-9]+\)/) { v=substr($0, RSTART+8, RLENGTH-9); print v }')
  if [[ -n "${pip_python_minor}" && "${pip_python_minor}" != "${python_minor:-}" ]]; then
    echo "⚠ pip/python mismatch: pip targets Python ${pip_python_minor}, ${PYTHON_BIN} is Python ${python_minor}"
    echo "  Use '${PYTHON_BIN} -m pip install ...' to install into the checked interpreter."
    warnings=$((warnings+1))
  fi
fi

# Manim
if command -v manim >/dev/null; then
  manim_output=$(manim --version 2>/dev/null | head -1 || echo "unknown")
  manim_version=$(echo "$manim_output" | grep -Eo '[0-9]+(\.[0-9]+){1,2}' | head -1 || true)
  if [[ -n "${manim_version}" ]] && "${PYTHON_BIN}" - "${manim_version}" "${MIN_MANIM_VERSION}" <<'PY'
import sys

def parse(v: str) -> tuple[int, int, int]:
    parts = [int(p) for p in v.split(".")]
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])

current = parse(sys.argv[1])
minimum = parse(sys.argv[2])
sys.exit(0 if current >= minimum else 1)
PY
  then
    echo "✓ Manim $manim_version (>= ${MIN_MANIM_VERSION})"
  else
    if [[ -z "${manim_version}" ]]; then
      echo "✗ Manim version not detectable (${manim_output})"
    else
      echo "✗ Manim $manim_version is below required ${MIN_MANIM_VERSION}"
    fi
    errors=$((errors+1))
  fi
else
  echo "✗ Manim not found (install: pip install manim)"
  errors=$((errors+1))
fi

# FFmpeg
if command -v ffmpeg >/dev/null; then
  version=$(ffmpeg -version 2>&1 | head -1 | awk '{print $3}')
  echo "✓ FFmpeg $version"
else
  echo "✗ FFmpeg not found (install: brew install ffmpeg)"
  errors=$((errors+1))
fi

# Sox
if command -v sox >/dev/null; then
  version=$(sox --version 2>&1 | head -1 | grep -Eo '[0-9]+(\.[0-9]+)+' | head -1 || true)
  version="${version:-unknown}"
  echo "✓ Sox $version"
else
  echo "✗ Sox not found (install: brew install sox)"
  errors=$((errors+1))
fi

# Voice template assets used by new_project.sh
voice_template_dir="${VOICE_REF_TEMPLATE_DIR:-${REPO_ROOT}/assets/voice_ref}"
if [[ -f "${voice_template_dir}/ref.wav" && -f "${voice_template_dir}/ref.txt" ]]; then
  if [[ -s "${voice_template_dir}/ref.txt" ]]; then
    echo "✓ Voice template assets (${voice_template_dir})"
  else
    echo "✗ Voice template ref.txt is empty (${voice_template_dir}/ref.txt)"
    errors=$((errors+1))
  fi
else
  echo "✗ Voice template missing (need ${voice_template_dir}/ref.wav and ref.txt)"
  errors=$((errors+1))
fi

# Optional project-level voice config consistency checks
if [[ -n "${PROJECT_DIR}" ]]; then
  if [[ "${PROJECT_DIR}" = /* ]]; then
    PROJECT_DIR_ABS="${PROJECT_DIR}"
  else
    PROJECT_DIR_ABS="$("${PYTHON_BIN}" -c 'import os,sys; print(os.path.abspath(sys.argv[1]))' "${PROJECT_DIR}")"
  fi

  if [[ ! -d "${PROJECT_DIR_ABS}" ]]; then
    echo "✗ Project directory not found: ${PROJECT_DIR_ABS}"
    errors=$((errors+1))
  else
    if "${PYTHON_BIN}" "${SCRIPT_DIR}/voice_ref_mediator.py" --check "${PROJECT_DIR_ABS}" >/dev/null 2>&1; then
      echo "✓ Project voice references resolve (${PROJECT_DIR_ABS})"
    else
      echo "✗ Project voice references invalid (${PROJECT_DIR_ABS})"
      errors=$((errors+1))
    fi

    if [[ -f "${PROJECT_DIR_ABS}/voice_clone_config.json" ]]; then
      if "${PYTHON_BIN}" - "${PROJECT_DIR_ABS}/voice_clone_config.json" <<'PY'
import json
import sys

cfg = json.load(open(sys.argv[1], encoding="utf-8"))
required = ("model_id", "device", "dtype", "ref_audio", "ref_text")
missing = [k for k in required if not cfg.get(k)]
if missing:
    raise SystemExit(f"missing keys: {', '.join(missing)}")
if cfg.get("model_id") != "Qwen/Qwen3-TTS-12Hz-1.7B-Base":
    raise SystemExit("model_id must be Qwen/Qwen3-TTS-12Hz-1.7B-Base")
if str(cfg.get("device")).lower() != "cpu":
    raise SystemExit("device must be cpu")
if str(cfg.get("dtype")).lower() != "float32":
    raise SystemExit("dtype must be float32")
PY
      then
        echo "✓ Project voice_clone_config.json policy-compatible"
      else
        echo "✗ Project voice_clone_config.json is not policy-compatible"
        errors=$((errors+1))
      fi
    else
      echo "✗ Missing project voice_clone_config.json (${PROJECT_DIR_ABS}/voice_clone_config.json)"
      errors=$((errors+1))
    fi
  fi
fi

# Python packages
if "${PYTHON_BIN}" -c "import manim" 2>/dev/null; then
  echo "✓ manim package"
else
  echo "✗ manim package not installed for ${PYTHON_BIN} (install: ${PYTHON_BIN} -m pip install manim)"
  errors=$((errors+1))
fi

if "${PYTHON_BIN}" -c "import manim_voiceover_plus" 2>/dev/null; then
  echo "✓ manim-voiceover-plus package"
else
  echo "✗ manim-voiceover-plus not installed for ${PYTHON_BIN} (install: ${PYTHON_BIN} -m pip install manim-voiceover-plus)"
  errors=$((errors+1))
fi

echo ""
if [[ $errors -eq 0 ]]; then
  if [[ $warnings -gt 0 ]]; then
    echo "✅ All required dependencies satisfied ($warnings warning(s)) - ready to build videos"
  else
    echo "✅ All dependencies satisfied - ready to build videos"
  fi
  exit 0
else
  if [[ $warnings -gt 0 ]]; then
    echo "❌ $errors missing dependencies ($warnings warning(s)) - see docs/guides/INSTALLATION.md"
  else
    echo "❌ $errors missing dependencies - see docs/guides/INSTALLATION.md"
  fi
  exit 1
fi
