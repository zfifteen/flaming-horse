#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PHASES="$(python3 "${SCRIPT_DIR}/update_project_state.py" --print-phases | tr '\n' ' ' | sed 's/[[:space:]]\+$//')"

cat <<EOF
Flaming Horse CLI Help
======================

Canonical user entrypoint:
  ./scripts/create_video.sh <project_name> --topic "<video topic>" [--phase <target_phase>]

Common commands:
  ./scripts/create_video.sh <project_name> --topic "<video topic>"
    Create or resume a project, prepare voice service, and run the full pipeline.

  ./scripts/create_video.sh <project_name> --topic "<video topic>" --phase build_scenes
    Create/resume and stop after the requested phase is completed.

  ./scripts/check_dependencies.sh
    Validate environment prerequisites before running builds.

Advanced/manual commands:
  ./scripts/new_project.sh <project_name> --topic "<video topic>"
    Initialize project files/state only.

  ./scripts/build_video.sh projects/<project_name>
    Run/resume phase orchestration on an existing project.

  ./scripts/build_video.sh projects/<project_name> --phase build_scenes
    Run/resume and stop after the requested phase is completed.

  ./scripts/reset_phase.sh projects/<project_name> <phase>
    Manually reset project phase.

Phase values:
  ${PHASES}

More details:
  README.md
  docs/guides/INSTALLATION.md
EOF
