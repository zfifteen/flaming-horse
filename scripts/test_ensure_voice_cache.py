#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "ensure_voice_cache.py"
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import ensure_voice_cache


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


def _write_script(project_dir: Path, entries: dict[str, str] | None = None) -> None:
    payload = entries if entries is not None else {"scene_01": "Narration"}
    (project_dir / "narration_script.py").write_text(
        "SCRIPT = " + repr(payload) + "\n",
        encoding="utf-8",
    )


def _write_cache_entry(cache_dir: Path, audio_file: str = "scene_01.mp3") -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    (cache_dir / audio_file).write_bytes(b"fake mp3")
    (cache_dir / "cache.json").write_text(
        json.dumps(
            [
                {
                    "narration_key": "scene_01",
                    "text": "Narration",
                    "audio_file": audio_file,
                }
            ]
        )
        + "\n",
        encoding="utf-8",
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
            _write_script(project_dir)
            _write_cache_entry(cache_dir)

            result = _run(project_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(Path(payload["cache_index"]), (cache_dir / "cache.json").resolve())

    def test_partial_cache_missing_script_key_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            _write_script(
                project_dir,
                {
                    "scene_01": "Narration one",
                    "scene_02": "Narration two",
                },
            )
            cache_dir = project_dir / "media" / "voiceovers" / "qwen"
            _write_cache_entry(cache_dir)

            result = _run(project_dir)

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["reason"], "cache missing required narration key: scene_02")

    def test_text_index_can_satisfy_script_key(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            _write_script(project_dir, {"scene_01": "Narration by text"})
            cache_dir = project_dir / "media" / "voiceovers" / "qwen"
            cache_dir.mkdir(parents=True, exist_ok=True)
            (cache_dir / "voice.mp3").write_bytes(b"fake mp3")
            (cache_dir / "cache.json").write_text(
                json.dumps([{"text": "Narration by text", "audio_file": "voice.mp3"}]),
                encoding="utf-8",
            )

            result = _run(project_dir)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])

    def test_empty_cache_index_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            _write_script(project_dir)
            cache_dir = project_dir / "media" / "voiceovers" / "qwen"
            cache_dir.mkdir(parents=True)
            (cache_dir / "cache.json").write_text("[]\n", encoding="utf-8")

            result = _run(project_dir)

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["reason"], "cache index contains no entries")

    def test_missing_audio_file_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            _write_script(project_dir)
            cache_dir = project_dir / "media" / "voiceovers" / "qwen"
            cache_dir.mkdir(parents=True)
            (cache_dir / "cache.json").write_text(
                json.dumps([{"narration_key": "scene_01", "audio_file": "scene_01.mp3"}]),
                encoding="utf-8",
            )

            result = _run(project_dir)

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertIn("audio file missing", payload["reason"])

    def test_rejects_absolute_audio_file_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            _write_script(project_dir)
            cache_dir = project_dir / "media" / "voiceovers" / "qwen"
            cache_dir.mkdir(parents=True)
            outside_audio = project_dir / "outside.mp3"
            outside_audio.write_bytes(b"fake mp3")
            (cache_dir / "cache.json").write_text(
                json.dumps(
                    [
                        {
                            "narration_key": "scene_01",
                            "text": "Narration",
                            "audio_file": str(outside_audio),
                        }
                    ]
                ),
                encoding="utf-8",
            )

            result = _run(project_dir)

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(
                payload["reason"],
                f"cache entry 0 audio file must be relative: {outside_audio}",
            )

    def test_rejects_audio_file_path_that_escapes_cache_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            _write_script(project_dir)
            cache_dir = project_dir / "media" / "voiceovers" / "qwen"
            cache_dir.mkdir(parents=True)
            outside_audio = cache_dir.parent / "outside.mp3"
            outside_audio.write_bytes(b"fake mp3")
            (cache_dir / "cache.json").write_text(
                json.dumps(
                    [
                        {
                            "narration_key": "scene_01",
                            "text": "Narration",
                            "audio_file": "../outside.mp3",
                        }
                    ]
                ),
                encoding="utf-8",
            )

            result = _run(project_dir)

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(
                payload["reason"],
                "cache entry 0 audio file escapes cache directory: ../outside.mp3",
            )

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

    def test_voice_config_read_error_reports_structured_failure(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            (project_dir / "voice_clone_config.json").write_text("{}", encoding="utf-8")

            with mock.patch.object(
                ensure_voice_cache.Path,
                "read_text",
                side_effect=OSError("permission denied"),
            ):
                payload = ensure_voice_cache.check_voice_cache(project_dir)

            self.assertFalse(payload["ok"])
            self.assertIn("voice_clone_config.json could not be read", payload["reason"])
            self.assertIn("permission denied", payload["reason"])

    def test_cache_index_read_error_reports_structured_failure(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            cache_dir = project_dir / "media" / "voiceovers" / "qwen"
            cache_dir.mkdir(parents=True)
            cache_index = cache_dir / "cache.json"
            cache_index.write_text("[]", encoding="utf-8")
            _write_script(project_dir)

            original_read_text = ensure_voice_cache.Path.read_text

            def read_text(path: Path, *args, **kwargs):
                if path.name == "cache.json":
                    raise OSError("transient IO")
                return original_read_text(path, *args, **kwargs)

            with mock.patch.object(ensure_voice_cache.Path, "read_text", read_text):
                payload = ensure_voice_cache.check_voice_cache(project_dir)

            self.assertFalse(payload["ok"])
            self.assertEqual(payload["reason"], "cache index could not be read: transient IO")

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
