#!/usr/bin/env python3
import json
import os
import subprocess
import tempfile
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "record_scene_rendered.py"


def _write_fake_ffprobe(bin_dir: Path, stdout: str) -> None:
    path = bin_dir / "ffprobe"
    path.write_text(f"#!/usr/bin/env bash\nprintf '%s\\n' {stdout!r}\n", encoding="utf-8")
    path.chmod(0o755)


class RecordSceneRenderedTests(unittest.TestCase):
    def test_records_rendered_scene_metadata(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            (project_dir / "project_state.json").write_text(
                json.dumps({"scenes": [{"id": "scene_01"}]}) + "\n",
                encoding="utf-8",
            )
            video = project_dir / "media/videos/scene_01/1440p60/Scene01.mp4"
            video.parent.mkdir(parents=True)
            video.write_bytes(b"fake mp4")
            bin_dir = project_dir / "bin"
            bin_dir.mkdir()
            _write_fake_ffprobe(bin_dir, "12.5")
            old_path = os.environ.get("PATH", "")
            try:
                os.environ["PATH"] = f"{bin_dir}:{old_path}"
                result = subprocess.run(
                    [
                        "python3",
                        str(SCRIPT_PATH),
                        "--project-dir",
                        str(project_dir),
                        "--scene-id",
                        "scene_01",
                        "--class-name",
                        "Scene01",
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                )
            finally:
                os.environ["PATH"] = old_path

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            state = json.loads((project_dir / "project_state.json").read_text(encoding="utf-8"))
            scene = state["scenes"][0]
            self.assertEqual(scene["status"], "rendered")
            self.assertEqual(scene["video_file"], "media/videos/scene_01/1440p60/Scene01.mp4")
            self.assertEqual(scene["verification"]["file_size_bytes"], len(b"fake mp4"))
            self.assertEqual(scene["verification"]["duration_seconds"], 12.5)
            self.assertTrue(scene["verification"]["audio_present"])

    def test_missing_scene_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            (project_dir / "project_state.json").write_text(
                json.dumps({"scenes": []}) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT_PATH),
                    "--project-dir",
                    str(project_dir),
                    "--scene-id",
                    "scene_01",
                    "--class-name",
                    "Scene01",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("scene not found", result.stdout)


if __name__ == "__main__":
    unittest.main()
