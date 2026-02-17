#!/usr/bin/env python3
"""Standalone script to validate scene content as a build gate."""

import subprocess
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/validate_scene_content.py <project_dir>")
        sys.exit(1)

    project_dir = Path(sys.argv[1])
    if not project_dir.exists():
        print(f"Project directory {project_dir} does not exist")
        sys.exit(1)

    # Run pytest on the scene content tests
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_scene_content.py::test_no_planning_text_in_scenes",
            "tests/test_scene_content.py::test_horizontal_bounds",
            "tests/test_scene_content.py::test_stage_direction_blacklist",
            "tests/test_scene_content.py::test_no_runtime_passed_to_play_next",
            "tests/test_scene_content.py::test_no_long_waits",
            f"--project_dir={project_dir}",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("Scene content validation failed:")
        print(result.stdout)
        print(result.stderr)
        sys.exit(1)

    print("Scene content validation passed.")


if __name__ == "__main__":
    main()
