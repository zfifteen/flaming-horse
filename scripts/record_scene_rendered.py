#!/usr/bin/env python3
"""Record rendered scene metadata in project_state.json."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from verify_scene_video import verify_scene_video


def scene_video_path(project_dir: Path, scene_id: str, class_name: str) -> Path:
    return project_dir / "media" / "videos" / scene_id / "1440p60" / f"{class_name}.mp4"


def probe_duration(video_path: Path) -> float:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return 0.0
    result = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(video_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        return float((result.stdout or "0").strip() or "0")
    except ValueError:
        return 0.0


def record_scene_rendered(project_dir: Path, scene_id: str, class_name: str) -> None:
    project_dir = project_dir.resolve()
    state_file = project_dir / "project_state.json"
    video_path = scene_video_path(project_dir, scene_id, class_name)
    state = json.loads(state_file.read_text(encoding="utf-8"))
    matching_scene = None
    for scene in state.get("scenes", []):
        if scene.get("id") == scene_id:
            matching_scene = scene
            break
    if matching_scene is None:
        raise ValueError(f"scene not found in project_state.json: {scene_id}")

    verification = verify_scene_video(project_dir, scene_id, class_name)
    if not verification["ok"]:
        raise ValueError(f"render artifact is not ready: {verification['reason']}")
    file_size = video_path.stat().st_size
    duration = probe_duration(video_path)

    matching_scene["status"] = "rendered"
    matching_scene["video_file"] = str(video_path.relative_to(project_dir))
    matching_scene["verification"] = {
        "file_size_bytes": file_size,
        "duration_seconds": duration,
        "audio_present": bool(verification["audio_checked"]),
        "audio_checked": bool(verification["audio_checked"]),
        "verification_reason": verification["reason"],
        "verified_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    state_file.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--scene-id", required=True)
    parser.add_argument("--class-name", required=True)
    args = parser.parse_args()

    try:
        record_scene_rendered(args.project_dir, args.scene_id, args.class_name)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
