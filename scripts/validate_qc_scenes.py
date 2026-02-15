#!/usr/bin/env python3
"""Post-QC syntax validation gate.

Validates that all scene files from project_state.json compile without syntax errors.
Returns:
- Exit 0: All scenes valid
- Exit 1: Syntax errors found (details to stderr)
"""

import json
import py_compile
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_qc_scenes.py <project_dir>", file=sys.stderr)
        sys.exit(1)

    project_dir = Path(sys.argv[1])
    state_file = project_dir / "project_state.json"

    if not state_file.exists():
        print(f"State file not found: {state_file}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(state_file, "r") as f:
            state = json.load(f)
    except Exception as e:
        print(f"Failed to parse state file: {e}", file=sys.stderr)
        sys.exit(1)

    scenes = state.get("scenes", [])
    if not isinstance(scenes, list):
        print("Invalid scenes array in state", file=sys.stderr)
        sys.exit(1)

    failed_scenes = []

    for scene in scenes:
        if not isinstance(scene, dict):
            continue

        scene_file = scene.get("file")
        if not scene_file:
            continue

        scene_path = project_dir / scene_file
        if not scene_path.exists():
            print(f"Scene file missing: {scene_path}", file=sys.stderr)
            failed_scenes.append((scene_file, "File not found"))
            continue

        try:
            py_compile.compile(str(scene_path), doraise=True)
            print(f"✓ {scene_file}: syntax valid")
        except py_compile.PyCompileError as e:
            print(f"✗ {scene_file}: SYNTAX ERROR", file=sys.stderr)
            print(f"  {e}", file=sys.stderr)
            failed_scenes.append((scene_file, str(e)))

    if failed_scenes:
        print(f"\n✗ {len(failed_scenes)} scene(s) have syntax errors", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"\n✓ All {len(scenes)} scene files compile successfully")
        sys.exit(0)


if __name__ == "__main__":
    main()
