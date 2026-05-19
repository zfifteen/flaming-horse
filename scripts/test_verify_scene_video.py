#!/usr/bin/env python3
import json
import os
import subprocess
import tempfile
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "verify_scene_video.py"


def _run(project_dir: Path, scene_id: str = "scene_01", class_name: str = "Scene01") -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            "python3",
            str(SCRIPT_PATH),
            "--project-dir",
            str(project_dir),
            "--scene-id",
            scene_id,
            "--class-name",
            class_name,
            "--json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def _write_fake_ffprobe(bin_dir: Path, stdout: str) -> None:
    path = bin_dir / "ffprobe"
    path.write_text(f"#!/usr/bin/env bash\nprintf '%s\\n' {stdout!r}\n", encoding="utf-8")
    path.chmod(0o755)


class VerifySceneVideoTests(unittest.TestCase):
    def test_missing_video_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = _run(Path(temp_dir))
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["reason"], "render output missing")

    def test_empty_video_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            video = project_dir / "media/videos/scene_01/1440p60/Scene01.mp4"
            video.parent.mkdir(parents=True)
            video.write_bytes(b"")

            result = _run(project_dir)

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["reason"], "render output empty")

    def test_audio_stream_passes_with_ffprobe(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            video = project_dir / "media/videos/scene_01/1440p60/Scene01.mp4"
            video.parent.mkdir(parents=True)
            video.write_bytes(b"fake mp4")
            bin_dir = project_dir / "bin"
            bin_dir.mkdir()
            _write_fake_ffprobe(bin_dir, "audio")
            old_path = os.environ.get("PATH", "")
            try:
                os.environ["PATH"] = f"{bin_dir}:{old_path}"
                result = _run(project_dir)
            finally:
                os.environ["PATH"] = old_path

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["audio_checked"])

    def test_missing_audio_stream_fails_with_ffprobe(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            video = project_dir / "media/videos/scene_01/1440p60/Scene01.mp4"
            video.parent.mkdir(parents=True)
            video.write_bytes(b"fake mp4")
            bin_dir = project_dir / "bin"
            bin_dir.mkdir()
            _write_fake_ffprobe(bin_dir, "")
            old_path = os.environ.get("PATH", "")
            try:
                os.environ["PATH"] = f"{bin_dir}:{old_path}"
                result = _run(project_dir)
            finally:
                os.environ["PATH"] = old_path

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["reason"], "no audio stream detected")


if __name__ == "__main__":
    unittest.main()
