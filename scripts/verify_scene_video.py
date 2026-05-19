#!/usr/bin/env python3
"""Verify a rendered scene MP4 exists and has an audio stream when ffprobe is available."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


def scene_video_path(project_dir: Path, scene_id: str, class_name: str) -> Path:
    return project_dir / "media" / "videos" / scene_id / "1440p60" / f"{class_name}.mp4"


def _result(ok: bool, video_path: Path, reason: str, audio_checked: bool) -> dict[str, Any]:
    return {
        "ok": ok,
        "video_path": str(video_path),
        "reason": reason,
        "audio_checked": audio_checked,
    }


def verify_scene_video(project_dir: Path, scene_id: str, class_name: str) -> dict[str, Any]:
    video_path = scene_video_path(project_dir, scene_id, class_name)
    if not video_path.exists():
        return _result(False, video_path, "render output missing", False)
    if video_path.stat().st_size <= 0:
        return _result(False, video_path, "render output empty", False)

    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return _result(True, video_path, "ffprobe not found; skipped audio verification", False)

    probe = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=codec_type",
            "-of",
            "csv=p=0",
            str(video_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if not probe.stdout.strip():
        return _result(False, video_path, "no audio stream detected", True)
    return _result(True, video_path, "render output verified", True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--scene-id", required=True)
    parser.add_argument("--class-name", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = verify_scene_video(args.project_dir, args.scene_id, args.class_name)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result["ok"]:
        if result["audio_checked"]:
            print(f"Render output verified: {result['video_path']}")
        else:
            print(f"WARNING: {result['reason']}: {result['video_path']}")
    else:
        print(f"{result['reason']}: {result['video_path']}", file=sys.stderr)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
