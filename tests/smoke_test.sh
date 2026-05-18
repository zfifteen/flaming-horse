#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(realpath "${SCRIPT_DIR}/..")"
ENV_FILE="${REPO_ROOT}/.env"

_grok_cli_env_set=0
if [[ -n "${GROK_CLI:-}" ]]; then
  _grok_cli_env_set=1
  _grok_cli_env="${GROK_CLI}"
fi

if [[ -f "${ENV_FILE}" ]]; then
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
fi
if [[ ${_grok_cli_env_set} -eq 1 ]]; then
  GROK_CLI="${_grok_cli_env}"
fi

if [[ -n "${GROK_CLI:-}" ]]; then
  GROK_BIN="${GROK_CLI}"
else
  GROK_BIN="$(command -v grok || true)"
fi

if [[ -z "${GROK_BIN}" || ! -x "${GROK_BIN}" ]]; then
  echo "❌ grok CLI is not available." >&2
  echo "   Add grok to PATH or set GROK_CLI=/absolute/path/to/grok" >&2
  exit 1
fi

grok_models_status=0
grok_models_output="$("${GROK_BIN}" models 2>&1)" || grok_models_status=$?
if [[ "${grok_models_status}" -ne 0 || "${grok_models_output}" != *"grok-build"* ]]; then
  echo "❌ grok CLI is not logged in or cannot list required model grok-build." >&2
  echo "   Run: grok login" >&2
  if [[ -n "${grok_models_output}" ]]; then
    echo "${grok_models_output}" >&2
  fi
  exit 1
fi

PROJECTS_DIR="${PROJECTS_BASE_DIR:-./projects}"
if [[ "${PROJECTS_DIR}" != /* ]]; then
  PROJECTS_DIR="${REPO_ROOT}/${PROJECTS_DIR}"
fi
PROJECTS_DIR="$(python3 -c 'import os,sys; print(os.path.abspath(sys.argv[1]))' "${PROJECTS_DIR}")"

ORIGINAL_PROJECT_NAME="smoke-test"
counter=1
PROJECT_NAME="${ORIGINAL_PROJECT_NAME}"
PROJECT_DIR="${PROJECTS_DIR}/${PROJECT_NAME}"
while [[ -d "$PROJECT_DIR" ]]; do
    PROJECT_NAME="${ORIGINAL_PROJECT_NAME}-${counter}"
    PROJECT_DIR="${PROJECTS_DIR}/${PROJECT_NAME}"
    ((counter++))
done

./scripts/create_video.sh "$PROJECT_NAME" --topic "Create a tiny video for testing that include three full scenes: Intro, Content and Conclusion (create your own titles). Make the narration a few quotes from the movie The Matrix."
