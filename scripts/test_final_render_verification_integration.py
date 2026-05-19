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
    final_render = function_body(script, "handle_final_render", "handle_assemble")

    require(
        "verify_scene_video.py" in final_render,
        "final_render verification does not call verify_scene_video.py",
    )
    require(
        "record_scene_rendered.py" in final_render,
        "final_render state recording does not call record_scene_rendered.py",
    )
    forbidden_inline = [
        "-select_streams a:0",
        "audio_stream=",
        '"audio_present": True',
        "file_size=$(stat",
    ]
    for token in forbidden_inline:
        require(token not in final_render, f"final_render still contains inline verification detail: {token}")

    print("OK")


if __name__ == "__main__":
    main()
