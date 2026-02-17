#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(realpath "${SCRIPT_DIR}/..")"
ENV_FILE="${REPO_ROOT}/.env"

if [[ -f "${ENV_FILE}" ]]; then
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
fi

if [[ -z "${XAI_API_KEY:-}" ]]; then
  echo "❌ XAI_API_KEY is not set in the environment." >&2
  echo "   Please set it in .env or export XAI_API_KEY=your_key" >&2
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
