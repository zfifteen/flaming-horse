#!/usr/bin/env python3
import json
import subprocess
import tempfile
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "validate_scene_timing_budget.py"


def _write_cache(project_dir: Path, scene_id: str, duration: float) -> None:
    cache_dir = project_dir / "media" / "voiceovers" / "qwen"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / "cache.json"
    payload = [
        {
            "narration_key": scene_id,
            "duration_seconds": duration,
        }
    ]
    cache_path.write_text(json.dumps(payload), encoding="utf-8")


def _write_scene(scene_path: Path, body: str) -> None:
    scene_path.write_text(body, encoding="utf-8")


class TimingBudgetValidatorTests(unittest.TestCase):
    def test_pass_when_ratio_above_threshold(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            scene_id = "scene_01_intro"
            scene_file = project_dir / f"{scene_id}.py"
            _write_cache(project_dir, scene_id, 20.0)
            _write_scene(
                scene_file,
                """
class Dummy:
    def construct(self):
        self.play(FadeIn(title), run_time=tracker.duration * 0.5)
        self.wait(tracker.duration * 0.2)
""".strip(),
            )

            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT_PATH),
                    "--scene-file",
                    str(scene_file),
                    "--project-dir",
                    str(project_dir),
                    "--min-ratio",
                    "0.90",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

    def test_fail_when_ratio_below_threshold(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            scene_id = "scene_06_resistance_and_training"
            scene_file = project_dir / f"{scene_id}.py"
            _write_cache(project_dir, scene_id, 22.4)
            _write_scene(
                scene_file,
                """
class Dummy:
    def construct(self):
        self.play(FadeIn(a), run_time=tracker.duration * 0.97)
        self.wait(tracker.duration * 0.26)
""".strip(),
            )

            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT_PATH),
                    "--scene-file",
                    str(scene_file),
                    "--project-dir",
                    str(project_dir),
                    "--min-ratio",
                    "0.90",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
            self.assertIn("FAIL: projected timing exceeds narration budget", result.stdout)

    def test_auto_adjust_when_ratio_below_threshold(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            scene_id = "scene_06_resistance_and_training"
            scene_file = project_dir / f"{scene_id}.py"
            _write_cache(project_dir, scene_id, 22.4)
            _write_scene(
                scene_file,
                """
class Dummy:
    def construct(self):
        self.play(FadeIn(a), run_time=tracker.duration * 0.97)
        self.wait(tracker.duration * 0.26)
""".strip(),
            )

            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT_PATH),
                    "--scene-file",
                    str(scene_file),
                    "--project-dir",
                    str(project_dir),
                    "--min-ratio",
                    "0.90",
                    "--auto-adjust",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertIn("AUTO-ADJUST", result.stdout)
            updated = scene_file.read_text(encoding="utf-8")
            self.assertIn("run_time=", updated)

    def test_auto_adjust_preserves_slot_markers(self):
        """_apply_timing_scale must not strip # SLOT_START / SLOT_END comments.

        ast.unparse() silently discards all Python comments.  If those comments
        contain the scaffold slot markers required by _inject_body_into_scaffold
        (harness_responses/parser.py) the scene file is permanently broken for
        any future scene_repair pass.  This regression test guards that path.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            scene_id = "scene_03_markers"
            scene_file = project_dir / f"{scene_id}.py"
            _write_cache(project_dir, scene_id, 20.0)
            _write_scene(
                scene_file,
                """class Dummy:
    def construct(self):
        # SLOT_START:scene_body
        self.play(FadeIn(title), run_time=30.0)
        self.wait(5.0)
        # SLOT_END:scene_body
""",
            )

            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT_PATH),
                    "--scene-file",
                    str(scene_file),
                    "--project-dir",
                    str(project_dir),
                    "--min-ratio",
                    "0.90",
                    "--auto-adjust",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            updated = scene_file.read_text(encoding="utf-8")
            self.assertIn("# SLOT_START:scene_body", updated)
            self.assertIn("# SLOT_END:scene_body", updated)

    def test_indeterminate_for_unparsed_expression(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            scene_id = "scene_02_unknown_math"
            scene_file = project_dir / f"{scene_id}.py"
            _write_cache(project_dir, scene_id, 20.0)
            _write_scene(
                scene_file,
                """
class Dummy:
    def construct(self):
        self.play(FadeIn(a), run_time=custom_runtime())
""".strip(),
            )

            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT_PATH),
                    "--scene-file",
                    str(scene_file),
                    "--project-dir",
                    str(project_dir),
                    "--min-ratio",
                    "0.90",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 2, msg=result.stdout + result.stderr)
            self.assertIn("WARN: no explicit timing terms found", result.stdout)


if __name__ == "__main__":
    unittest.main()
