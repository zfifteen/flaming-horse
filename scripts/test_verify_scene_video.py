#!/usr/bin/env python3
import json
import os
import sys
import subprocess
import tempfile
from pathlib import Path
from unittest import mock
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "verify_scene_video.py"
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import verify_scene_video


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


def _write_failing_ffprobe(bin_dir: Path, stderr: str) -> None:
    path = bin_dir / "ffprobe"
    path.write_text(
        f"#!/usr/bin/env bash\nprintf '%s\\n' {stderr!r} >&2\nexit 42\n",
        encoding="utf-8",
    )
    path.chmod(0o755)


def _write_python3_link(bin_dir: Path) -> None:
    python_path = bin_dir / "python3"
    python_path.symlink_to(Path(sys.executable))


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

    def test_video_stat_error_reports_structured_failure(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)

            with mock.patch.object(verify_scene_video.Path, "exists", return_value=True), mock.patch.object(
                verify_scene_video.Path,
                "stat",
                side_effect=OSError("permission denied"),
            ):
                payload = verify_scene_video.verify_scene_video(project_dir, "scene_01", "Scene01")

            self.assertFalse(payload["ok"])
            self.assertIn("render output inaccessible", payload["reason"])
            self.assertIn("permission denied", payload["reason"])

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

    def test_ffprobe_missing_skips_audio_verification(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            video = project_dir / "media/videos/scene_01/1440p60/Scene01.mp4"
            video.parent.mkdir(parents=True)
            video.write_bytes(b"fake mp4")
            bin_dir = project_dir / "bin"
            bin_dir.mkdir()
            _write_python3_link(bin_dir)
            old_path = os.environ.get("PATH", "")
            try:
                os.environ["PATH"] = str(bin_dir)
                result = _run(project_dir)
            finally:
                os.environ["PATH"] = old_path

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["audio_checked"])
            self.assertIsNone(payload["audio_present"])
            self.assertEqual(payload["reason"], "ffprobe not found; skipped audio verification")

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
            self.assertTrue(payload["audio_checked"])
            self.assertFalse(payload["audio_present"])

    def test_ffprobe_failure_is_distinct_from_missing_audio(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            video = project_dir / "media/videos/scene_01/1440p60/Scene01.mp4"
            video.parent.mkdir(parents=True)
            video.write_bytes(b"fake mp4")
            bin_dir = project_dir / "bin"
            bin_dir.mkdir()
            _write_failing_ffprobe(bin_dir, "invalid data found when processing input")
            old_path = os.environ.get("PATH", "")
            try:
                os.environ["PATH"] = f"{bin_dir}:{old_path}"
                result = _run(project_dir)
            finally:
                os.environ["PATH"] = old_path

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertIn("ffprobe failed: invalid data found", payload["reason"])
            self.assertTrue(payload["audio_checked"])
            self.assertIsNone(payload["audio_present"])

    def test_ffprobe_os_error_reports_structured_failure(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            video = project_dir / "media/videos/scene_01/1440p60/Scene01.mp4"
            video.parent.mkdir(parents=True)
            video.write_bytes(b"fake mp4")

            with mock.patch.object(verify_scene_video.shutil, "which", return_value="/bad/ffprobe"), mock.patch.object(
                verify_scene_video.subprocess,
                "run",
                side_effect=OSError("exec failed"),
            ):
                payload = verify_scene_video.verify_scene_video(project_dir, "scene_01", "Scene01")

            self.assertFalse(payload["ok"])
            self.assertEqual(payload["reason"], "ffprobe could not run: exec failed")
            self.assertTrue(payload["audio_checked"])
            self.assertIsNone(payload["audio_present"])


if __name__ == "__main__":
    unittest.main()
