#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

echo "🧪 CLI help smoke tests"

assert_contains() {
  local haystack="$1"
  local needle="$2"
  local label="$3"
  if [[ "${haystack}" == *"${needle}"* ]]; then
    echo "✅ ${label}"
  else
    echo "❌ ${label}" >&2
    echo "   Missing: ${needle}" >&2
    exit 1
  fi
}

help_out="$(bash scripts/help.sh)"
create_out="$(bash scripts/create_video.sh --help)"
build_out="$(bash scripts/build_video.sh --help 2>&1)"
new_out="$(bash scripts/new_project.sh --help)"

assert_contains "${help_out}" "./scripts/create_video.sh" "help.sh shows canonical entrypoint"
assert_contains "${create_out}" "./scripts/help.sh" "create_video --help points to help.sh"
assert_contains "${build_out}" "Recommended user entrypoint" "build_video --help includes entrypoint guidance"
assert_contains "${build_out}" "./scripts/help.sh" "build_video --help points to help.sh"
assert_contains "${new_out}" "./scripts/help.sh" "new_project --help points to help.sh"

echo "✅ CLI help smoke tests passed"
