#!/usr/bin/env python3
import json
import subprocess
import tempfile
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "resolve_scene_metadata.py"


def _write_state(project_dir: Path, state: dict) -> None:
    (project_dir / "project_state.json").write_text(json.dumps(state), encoding="utf-8")


def _run(project_dir: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["python3", str(SCRIPT_PATH), "--project-dir", str(project_dir), *extra],
        capture_output=True,
        text=True,
        check=False,
    )


class ResolveSceneMetadataTests(unittest.TestCase):
    def test_resolves_current_scene_with_inferred_class(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            _write_state(
                project_dir,
                {
                    "current_scene_index": 0,
                    "scenes": [{"id": "scene_01_intro", "narration_key": "intro"}],
                },
            )

            result = _run(project_dir, "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["has_scene"])
            self.assertEqual(payload["scene_id"], "scene_01_intro")
            self.assertEqual(payload["file"], "scene_01_intro.py")
            self.assertEqual(payload["class_name"], "Scene01Intro")
            self.assertEqual(payload["narration_key"], "intro")

    def test_respects_existing_file_and_class_name(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            _write_state(
                project_dir,
                {
                    "current_scene_index": 1,
                    "scenes": [
                        {"id": "scene_01"},
                        {
                            "id": "scene_02",
                            "file": "custom_scene.py",
                            "class_name": "CustomScene",
                        },
                    ],
                },
            )

            result = _run(project_dir, "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["file"], "custom_scene.py")
            self.assertEqual(payload["class_name"], "CustomScene")
            self.assertEqual(payload["narration_key"], "scene_02")

    def test_reports_no_scene_when_index_is_past_end(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            _write_state(project_dir, {"current_scene_index": 2, "scenes": [{"id": "scene_01"}]})

            result = _run(project_dir, "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["has_scene"])
            self.assertEqual(payload["scene_index"], 2)

    def test_pipe_output_matches_build_script_contract(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            _write_state(project_dir, {"current_scene_index": 0, "scenes": [{"id": "scene_03_gap"}]})

            result = _run(project_dir)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "scene_03_gap|scene_03_gap.py|Scene03Gap|scene_03_gap")


if __name__ == "__main__":
    unittest.main()
