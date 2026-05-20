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
    validator = function_body(script, "validate_scene_first_pass_with_owner", "validate_scene_runtime")
    build_scenes = function_body(script, "handle_build_scenes", "handle_scene_qc")

    require("scene_validator.py" in validator, "validator wrapper does not call scene_validator.py")
    require("--json" in validator, "validator wrapper does not request JSON output")
    require(
        "SCENE_VALIDATOR_GATE" in validator and "SCENE_VALIDATOR_REASON" in validator,
        "validator wrapper does not expose classified failure fields",
    )

    require(
        'validate_scene_first_pass_with_owner "$new_scene"' in build_scenes,
        "handle_build_scenes does not call scene validator owner",
    )
    require(
        '"$SCENE_VALIDATOR_GATE"' in build_scenes and '"$SCENE_VALIDATOR_REASON"' in build_scenes,
        "handle_build_scenes does not pass validator classification to repair wrapper",
    )
    require(
        'runtime_validate_scene_with_preconditions "$new_scene" "$scene_class"' in build_scenes,
        "runtime dry-run gate was removed from handle_build_scenes",
    )

    removed_direct_calls = [
        'validate_scene_template_structure "$new_scene"',
        'validate_scene_imports "$new_scene"',
        'validate_voiceover_sync "$new_scene"',
        'validate_scene_semantics "$new_scene"',
        '$PYTHON_BIN -m py_compile "$new_scene"',
    ]
    for call in removed_direct_calls:
        require(call not in build_scenes, f"handle_build_scenes still has direct duplicate gate: {call}")

    require(
        "repair_build_scene_first_pass_failure" in build_scenes,
        "build_scenes repair wrapper was removed",
    )
    print("OK")


if __name__ == "__main__":
    main()
