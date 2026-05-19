#!/usr/bin/env python3
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_VIDEO = REPO_ROOT / "scripts" / "build_video.sh"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def function_body(script: str, name: str, next_name: str) -> str:
    start = script.find(f"{name}() {{")
    require(start >= 0, f"{name} not found")
    end = script.find(f"\n{next_name}() {{", start)
    require(end >= 0, f"{next_name} not found after {name}")
    return script[start:end]


def main() -> None:
    script = BUILD_VIDEO.read_text(encoding="utf-8")
    build_scenes = function_body(script, "handle_build_scenes", "handle_scene_qc")

    require(
        'resolve_scene_metadata.py" --project-dir "$PROJECT_DIR"' in build_scenes,
        "handle_build_scenes does not use resolve_scene_metadata.py",
    )
    require(
        "def camel_from_scene_id" not in build_scenes,
        "handle_build_scenes still carries inline class-name inference",
    )
    require(
        'print(f"{scene_id}|{scene_id}.py|{scene_class}|{narration_key}")' not in build_scenes,
        "handle_build_scenes still carries inline metadata pipe output",
    )
    require(
        "IFS='|' read -r scene_id scene_file scene_class narration_key" in build_scenes,
        "handle_build_scenes pipe contract changed unexpectedly",
    )
    print("OK")


if __name__ == "__main__":
    main()
