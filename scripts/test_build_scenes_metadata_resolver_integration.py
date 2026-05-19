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
        '2> >(tee -a "$LOG_FILE" >&2)' in build_scenes,
        "handle_build_scenes does not preserve resolver stderr in build.log",
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
    required_idx = build_scenes.find('[[ -z "$scene_id" || -z "$scene_file" || -z "$narration_key" ]]')
    invalid_idx = build_scenes.find('[[ ! "$scene_id" =~ ^scene_[0-9]+(_[a-z0-9_]+)?$ ]]')
    class_idx = build_scenes.find('[[ -z "$scene_class" ]]')
    reconcile_idx = build_scenes.find('reconciled_narration_key="$(get_scene_narration_key "$scene_id")"')
    scaffold_idx = build_scenes.find('--narration-key "$narration_key"')
    require(required_idx > 0, "handle_build_scenes no longer checks required metadata")
    require(invalid_idx > required_idx, "invalid scene id check must follow required metadata check")
    require(class_idx > invalid_idx, "scene class check must run after invalid scene id recording")
    require(reconcile_idx > class_idx, "handle_build_scenes must reconcile narration_key after metadata validation")
    require(scaffold_idx > reconcile_idx, "handle_build_scenes must reconcile narration_key before scaffolding")
    print("OK")


if __name__ == "__main__":
    main()
