#!/usr/bin/env python3
"""Resolve Flaming Horse scene metadata from project_state.json."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def camel_from_scene_id(scene_id: str) -> str:
    m_simple = re.match(r"^scene_(\d+)$", scene_id)
    if m_simple:
        return f"Scene{m_simple.group(1)}"
    m = re.match(r"^scene_(\d+)_([a-z0-9_]+)$", scene_id)
    if not m:
        return ""
    num = m.group(1)
    slug = m.group(2)
    parts = [p for p in slug.split("_") if p]
    title = "".join(p.capitalize() for p in parts)
    return f"Scene{num}{title}" if title else f"Scene{num}"


def _load_state(project_dir: Path) -> dict[str, Any]:
    state_path = project_dir / "project_state.json"
    if not state_path.exists():
        raise ValueError(f"Project state file not found: {state_path}")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if not isinstance(state, dict):
        raise ValueError("project_state.json root must be an object")
    return state


def _required_non_empty_string(value: Any, field: str, scene_index: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"scene[{scene_index}].{field} must be a non-empty string")
    return value


def _optional_non_empty_string(value: Any, field: str, scene_index: int) -> str:
    if value is None:
        return ""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"scene[{scene_index}].{field} must be a non-empty string when present")
    return value


def resolve_scene_metadata(project_dir: Path, scene_index: int | None = None) -> dict[str, Any]:
    state = _load_state(project_dir)
    scenes = state.get("scenes") or []
    if not isinstance(scenes, list):
        raise ValueError("project_state.json scenes must be a list")

    idx = int(state.get("current_scene_index") or 0) if scene_index is None else scene_index
    if idx < 0:
        raise ValueError("scene index must be non-negative")
    if idx >= len(scenes):
        return {"has_scene": False, "scene_index": idx}

    raw_scene = scenes[idx]
    if not isinstance(raw_scene, dict):
        raise ValueError(f"scene[{idx}] must be an object")

    scene_id = _required_non_empty_string(raw_scene.get("id"), "id", idx)
    # build_scenes scaffolding and update_project_state.py both use <scene_id>.py.
    # Keep this resolver aligned with that runtime contract.
    scene_file = f"{scene_id}.py"
    narration_key = _optional_non_empty_string(raw_scene.get("narration_key"), "narration_key", idx) or scene_id
    scene_class = _optional_non_empty_string(raw_scene.get("class_name"), "class_name", idx)
    if not scene_class:
        scene_class = camel_from_scene_id(scene_id)

    return {
        "has_scene": True,
        "scene_index": idx,
        "scene_id": scene_id,
        "file": scene_file,
        "class_name": scene_class,
        "narration_key": narration_key,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resolve scene metadata from project state.")
    parser.add_argument("--project-dir", required=True, type=Path)
    parser.add_argument("--scene-index", type=int)
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        payload = resolve_scene_metadata(args.project_dir, args.scene_index)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(payload, indent=2))
    elif payload.get("has_scene"):
        print(
            "|".join(
                [
                    str(payload["scene_id"]),
                    str(payload["file"]),
                    str(payload["class_name"]),
                    str(payload["narration_key"]),
                ]
            )
        )
    else:
        print("__NO_SCENE__|||")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
