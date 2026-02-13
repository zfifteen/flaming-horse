import importlib
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _install_voiceover_stubs():
    defaults = types.ModuleType("manim_voiceover_plus.defaults")
    defaults.DEFAULT_VOICEOVER_CACHE_DIR = "voiceovers"
    sys.modules["manim_voiceover_plus.defaults"] = defaults

    base = types.ModuleType("manim_voiceover_plus.services.base")

    class SpeechService:
        def __init__(self, cache_dir, transcription_model=None, **kwargs):
            self.cache_dir = cache_dir

    base.SpeechService = SpeechService
    sys.modules["manim_voiceover_plus.services.base"] = base


class TestQwenCachedService(unittest.TestCase):
    def setUp(self):
        _install_voiceover_stubs()
        qwen_cached = importlib.import_module("flaming_horse_voice.qwen_cached")
        self.QwenCachedService = qwen_cached.QwenCachedService

    def test_uses_configured_output_dir_without_cache_index(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            (project / "voice_clone_config.json").write_text(
                json.dumps({"output_dir": "media/voiceovers"}), encoding="utf-8"
            )
            (project / "media" / "voiceovers").mkdir(parents=True)
            (project / "media" / "voiceovers" / "intro.mp3").write_bytes(b"")
            (project / "narration_script.py").write_text(
                'SCRIPT = {"intro": "Hello world"}', encoding="utf-8"
            )

            service = self.QwenCachedService.from_project(project)
            self.assertEqual(
                Path(service.cache_dir),
                project / "media" / "voiceovers",
            )
            self.assertEqual(service.cache_index["intro"], "intro.mp3")
            self.assertEqual(
                service.text_index["Hello world"],
                "intro.mp3",
            )

    def test_uses_cache_json_when_present(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            cache_dir = project / "media" / "voiceovers" / "qwen"
            cache_dir.mkdir(parents=True)
            (cache_dir / "cache.json").write_text(
                json.dumps(
                    [
                        {
                            "narration_key": "intro",
                            "text": "Hello",
                            "audio_file": "intro.mp3",
                        }
                    ]
                ),
                encoding="utf-8",
            )

            service = self.QwenCachedService.from_project(project)
            self.assertEqual(service.cache_index["intro"], "intro.mp3")
            self.assertEqual(service.text_index["Hello"], "intro.mp3")


if __name__ == "__main__":
    unittest.main()
