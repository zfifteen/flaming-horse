#!/usr/bin/env python3
import subprocess
import tempfile
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "scaffold_scene.py"


class ScaffoldSceneTests(unittest.TestCase):
    def test_generates_scene_file_with_expected_content(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT_PATH),
                    "--project",
                    str(project_dir),
                    "--scene-id",
                    "scene_01_intro",
                    "--class-name",
                    "Scene01Intro",
                    "--narration-key",
                    "intro",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            scene_file = project_dir / "scene_01_intro.py"
            self.assertTrue(scene_file.exists())
            content = scene_file.read_text(encoding="utf-8")
            self.assertIn("class Scene01Intro(VoiceoverScene):", content)
            self.assertIn('with self.voiceover(text=SCRIPT["intro"]) as tracker:', content)
            self.assertIn("# TODO: Add animations here", content)
            self.assertIn("def safe_layout(*mobjects", content)

    def test_fails_without_force_when_scene_already_exists(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            scene_file = project_dir / "scene_01_intro.py"
            scene_file.write_text("existing content", encoding="utf-8")

            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT_PATH),
                    "--project",
                    str(project_dir),
                    "--scene-id",
                    "scene_01_intro",
                    "--class-name",
                    "Scene01Intro",
                    "--narration-key",
                    "intro",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("already exists", result.stderr)
            self.assertEqual(scene_file.read_text(encoding="utf-8"), "existing content")


if __name__ == "__main__":
    unittest.main()
