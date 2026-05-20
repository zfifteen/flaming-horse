#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "scene_validator.py"
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from scene_validator import validate_template_structure, validate_voiceover_sync


def _scene_text(body: str) -> str:
    return f"""
from pathlib import Path
from manim import *
from manim_voiceover import VoiceoverScene
from narration_script import SCRIPT
from flaming_horse_voice import get_speech_service

# LOCKED CONFIGURATION (DO NOT MODIFY)
config.frame_height = 10
config.frame_width = 10 * 16 / 9
config.pixel_height = 1440
config.pixel_width = 2560

class Scene01(VoiceoverScene):
    def construct(self):
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))
        with self.voiceover(text=SCRIPT["scene_01"]) as tracker:
            # SLOT_START:scene_body
{body}
            # SLOT_END:scene_body
""".lstrip()


def _write_scene(project_dir: Path, body: str, name: str = "scene_01.py") -> Path:
    scene_file = project_dir / name
    scene_file.write_text(_scene_text(body), encoding="utf-8")
    return scene_file


def _write_cache(project_dir: Path, scene_id: str, duration: float) -> None:
    cache_dir = project_dir / "media" / "voiceovers" / "qwen"
    cache_dir.mkdir(parents=True, exist_ok=True)
    payload = [{"narration_key": scene_id, "duration_seconds": duration}]
    (cache_dir / "cache.json").write_text(json.dumps(payload), encoding="utf-8")


def _run_validator(scene_file: Path, project_dir: Path | None = None) -> subprocess.CompletedProcess:
    cmd = ["python3", str(SCRIPT_PATH), "--scene-file", str(scene_file), "--json"]
    if project_dir is not None:
        cmd.extend(["--project-dir", str(project_dir)])
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


class SceneValidatorTests(unittest.TestCase):
    def test_valid_scene_passes_without_full_pipeline(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            scene_file = _write_scene(
                project_dir,
                '            title = Text("Prime gaps")\n'
                "            self.play(Write(title), run_time=min(1.0, tracker.duration * 0.2))",
            )

            result = _run_validator(scene_file)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            self.assertIsNone(payload["first_failed_gate"])
            self.assertEqual(payload["checks"][0]["gate"], "template_structure")

    def test_missing_scaffold_signature_fails_template_gate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            scene_file = _write_scene(
                project_dir,
                "            self.wait(tracker.duration * 0.1)",
            )
            text = scene_file.read_text(encoding="utf-8").replace(
                "# LOCKED CONFIGURATION (DO NOT MODIFY)\n",
                "",
            )
            scene_file.write_text(text, encoding="utf-8")

            result = _run_validator(scene_file)
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["first_failed_gate"], "template_structure")

    def test_template_structure_accepts_spaced_multiline_script_voiceover(self):
        scene_text = _scene_text(
            "            title = Text('Timing')\n"
            "            self.play(Write(title), run_time=tracker.duration * 0.2)"
        ).replace(
            'with self.voiceover(text=SCRIPT["scene_01"]) as tracker:',
            'with self.voiceover(\n            text = SCRIPT["scene_01"]\n        ) as tracker:',
        )

        result = validate_template_structure(scene_text)

        self.assertTrue(result.ok, result.message)

    def test_scene_body_contract_rejects_known_invalid_pattern(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            scene_file = _write_scene(
                project_dir,
                "            self.play(ShowCreation(Line()), run_time=tracker.duration * 0.2)",
            )

            result = _run_validator(scene_file)
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["first_failed_gate"], "scene_body_contract")
            self.assertIn("ShowCreation", payload["failure_summary"])

    def test_import_api_gate_rejects_full_scene_escaped_html(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            scene_file = _write_scene(
                project_dir,
                "            expr = MathTex('a &lt; b')\n"
                "            self.wait(tracker.duration * 0.1)",
            )

            result = _run_validator(scene_file)
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["first_failed_gate"], "import_api")
            self.assertIn("escaped HTML", payload["failure_summary"])

    def test_timing_budget_gate_uses_project_cache_when_available(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            scene_file = _write_scene(
                project_dir,
                "            title = Text('Timing')\n"
                "            self.play(Write(title), run_time=tracker.duration * 2.0)",
            )
            _write_cache(project_dir, "scene_01", 10.0)

            result = _run_validator(scene_file, project_dir)
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["first_failed_gate"], "timing_budget")
            self.assertIn("timing budget", payload["failure_summary"])

    def test_comment_only_full_scaffold_fails_python_syntax_before_scene_body_contract(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            scene_file = _write_scene(project_dir, "            # TODO")

            result = _run_validator(scene_file)
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["first_failed_gate"], "python_syntax")
            self.assertIn("expected an indented block", payload["failure_summary"])

    def test_missing_scene_file_returns_stable_json_failure(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            scene_file = project_dir / "missing_scene.py"

            result = _run_validator(scene_file)

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["first_failed_gate"], "scene_file")
            self.assertIn("could not be read", payload["failure_summary"])

    def test_voiceover_sync_rejects_hardcoded_text_with_spacing(self):
        scene_text = """
class Scene01:
    def construct(self):
        with self.voiceover(
            text = "Hardcoded narration"
        ) as tracker:
            self.wait(tracker.duration)
""".strip()

        result = validate_voiceover_sync(scene_text)

        self.assertFalse(result.ok)
        self.assertEqual(result.gate, "voiceover_sync")
        self.assertIn("hardcoded narration", result.message)

    def test_voiceover_sync_accepts_script_subscript_with_spacing(self):
        scene_text = """
class Scene01:
    def construct(self):
        with self.voiceover(
            text = SCRIPT["scene_01"]
        ) as tracker:
            self.wait(tracker.duration)
""".strip()

        result = validate_voiceover_sync(scene_text)

        self.assertTrue(result.ok, result.message)


if __name__ == "__main__":
    unittest.main()
