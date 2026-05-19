#!/usr/bin/env python3
import json
import subprocess
import tempfile
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "ensure_voice_cache.py"


def _run(project_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            "python3",
            str(SCRIPT_PATH),
            "--project-dir",
            str(project_dir),
            "--check",
            "--json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )


class EnsureVoiceCacheTests(unittest.TestCase):
    def test_reports_missing_default_cache_index(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)

            result = _run(project_dir)

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["reason"], "cache index missing")
            self.assertTrue(payload["cache_index"].endswith("media/voiceovers/qwen/cache.json"))

    def test_uses_configured_output_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            (project_dir / "voice_clone_config.json").write_text(
                json.dumps({"output_dir": "custom_voice_cache"}) + "\n",
                encoding="utf-8",
            )
            cache_dir = project_dir / "custom_voice_cache"
            cache_dir.mkdir()
            (cache_dir / "cache.json").write_text("[]\n", encoding="utf-8")

            result = _run(project_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(Path(payload["cache_index"]), (cache_dir / "cache.json").resolve())

    def test_rejects_malformed_cache_index(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            cache_dir = project_dir / "media" / "voiceovers" / "qwen"
            cache_dir.mkdir(parents=True)
            (cache_dir / "cache.json").write_text("{bad json", encoding="utf-8")

            result = _run(project_dir)

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["ok"])
            self.assertIn("cache index is not valid JSON", payload["reason"])

    def test_rejects_non_list_cache_index(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            cache_dir = project_dir / "media" / "voiceovers" / "qwen"
            cache_dir.mkdir(parents=True)
            (cache_dir / "cache.json").write_text("{}\n", encoding="utf-8")

            result = _run(project_dir)

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["reason"], "cache index root must be a list")


if __name__ == "__main__":
    unittest.main()
