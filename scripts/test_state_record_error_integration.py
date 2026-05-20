#!/usr/bin/env python3
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_VIDEO = REPO_ROOT / "scripts" / "build_video.sh"
UPDATER = REPO_ROOT / "scripts" / "update_project_state.py"


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
    build_video = BUILD_VIDEO.read_text(encoding="utf-8")
    updater = UPDATER.read_text(encoding="utf-8")
    build_scenes = function_body(build_video, "handle_build_scenes", "handle_scene_qc")

    require(
        'choices=["normalize", "apply", "record-error"]' in updater,
        "update_project_state.py does not expose record-error mode",
    )
    require("def record_error(" in updater, "record_error function missing")
    require("--needs-human-review" in updater, "record-error cannot set human review")
    require("--history-action" in updater, "record-error cannot record action")

    require(
        '--mode record-error \\' in build_scenes,
        "invalid scene id path does not use update_project_state.py record-error",
    )
    require(
        "--history-action invalid_scene_id" in build_scenes,
        "invalid scene id path does not record a deterministic history action",
    )
    require(
        'state.setdefault("errors", []).append("build_scenes failed: scene id must match' not in build_scenes,
        "invalid scene id path still mutates state inline",
    )

    print("OK")


if __name__ == "__main__":
    main()
