#!/usr/bin/env python3
"""
Test precache_voiceovers_qwen.py mock fallback functionality.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

# Add repo root to path to import the precache module
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from precache_voiceovers_qwen import (
    check_qwen_env_available,
    generate_mock_cache,
)


class TestQwenEnvCheck(unittest.TestCase):
    """Test the Qwen environment availability check."""

    def test_check_qwen_env_returns_false_for_none(self):
        """Should return False for None python path."""
        self.assertFalse(check_qwen_env_available(None))

    def test_check_qwen_env_returns_false_for_empty_string(self):
        """Should return False for empty string."""
        self.assertFalse(check_qwen_env_available(""))

    def test_check_qwen_env_returns_false_for_nonexistent_path(self):
        """Should return False for non-existent Python path."""
        self.assertFalse(check_qwen_env_available("/nonexistent/python"))

    def test_check_qwen_env_returns_false_for_python_without_qwen(self):
        """Should return False for Python that can't import qwen_tts."""
        # Use the system Python which likely doesn't have qwen_tts
        self.assertFalse(check_qwen_env_available(sys.executable))


class TestMockCacheGeneration(unittest.TestCase):
    """Test mock cache generation."""

    def test_generate_mock_cache_creates_files(self):
        """Should create audio files and cache entries."""
        with tempfile.TemporaryDirectory() as td:
            output_dir = Path(td) / "media" / "voiceovers" / "qwen"
            
            script = {
                "intro": "Hello world, this is a test.",
                "main": "This is a longer test with more words to test duration.",
            }
            
            entries = generate_mock_cache(
                script,
                output_dir,
                "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
                "/tmp/ref.wav",
                "reference text",
            )
            
            # Check that entries were created
            self.assertEqual(len(entries), 2)
            
            # Check intro entry
            intro_entry = next(e for e in entries if e["narration_key"] == "intro")
            self.assertEqual(intro_entry["text"], script["intro"])
            self.assertEqual(intro_entry["model_id"], "Qwen/Qwen3-TTS-12Hz-1.7B-Base")
            self.assertIn("duration_seconds", intro_entry)
            self.assertGreater(intro_entry["duration_seconds"], 0)
            
            # Check that audio files were created
            self.assertTrue((output_dir / intro_entry["audio_file"]).exists())
            self.assertGreater((output_dir / intro_entry["audio_file"]).stat().st_size, 0)

    def test_generate_mock_cache_calculates_duration_from_word_count(self):
        """Should calculate appropriate duration based on word count."""
        with tempfile.TemporaryDirectory() as td:
            output_dir = Path(td) / "media" / "voiceovers" / "qwen"
            
            # Test with known word counts
            script = {
                "short": "hello",  # 1 word
                "long": " ".join(["word"] * 25),  # 25 words
            }
            
            entries = generate_mock_cache(
                script,
                output_dir,
                "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
                "/tmp/ref.wav",
                "reference text",
            )
            
            short_entry = next(e for e in entries if e["narration_key"] == "short")
            long_entry = next(e for e in entries if e["narration_key"] == "long")
            
            # Short should be min duration (0.5s)
            self.assertAlmostEqual(short_entry["duration_seconds"], 0.5, places=1)
            
            # Long should be ~10s (25 words / 2.5 words/sec)
            self.assertAlmostEqual(long_entry["duration_seconds"], 10.0, places=1)


class TestFullPrecacheFlow(unittest.TestCase):
    """Test the full precache flow with mock mode."""

    def test_full_precache_with_missing_qwen_env(self):
        """Should complete successfully with mock mode when Qwen env is missing."""
        with tempfile.TemporaryDirectory() as td:
            project_dir = Path(td) / "test_project"
            project_dir.mkdir()
            
            # Create minimal project structure
            (project_dir / "voice_clone_config.json").write_text(
                json.dumps({
                    "qwen_python": "/nonexistent/python",
                    "ref_audio": "assets/voice_ref/ref.wav",
                    "ref_text": "assets/voice_ref/ref.txt",
                }),
                encoding="utf-8",
            )
            
            (project_dir / "narration_script.py").write_text(
                'SCRIPT = {"intro": "Hello world"}',
                encoding="utf-8",
            )
            
            # Create ref files
            ref_dir = project_dir / "assets" / "voice_ref"
            ref_dir.mkdir(parents=True)
            (ref_dir / "ref.wav").write_bytes(b"fake audio")
            (ref_dir / "ref.txt").write_text("reference text", encoding="utf-8")
            
            # Run precache (this should use mock mode)
            from precache_voiceovers_qwen import main as precache_main
            old_argv = sys.argv
            try:
                sys.argv = ["precache_voiceovers_qwen.py", str(project_dir)]
                result = precache_main()
                
                # Should succeed
                self.assertEqual(result, 0)
                
                # Check cache was created
                cache_file = project_dir / "media" / "voiceovers" / "qwen" / "cache.json"
                self.assertTrue(cache_file.exists())
                
                cache = json.loads(cache_file.read_text(encoding="utf-8"))
                self.assertEqual(len(cache), 1)
                self.assertEqual(cache[0]["narration_key"], "intro")
                self.assertEqual(cache[0]["text"], "Hello world")
                
                # Check audio file exists
                audio_file = project_dir / "media" / "voiceovers" / "qwen" / cache[0]["audio_file"]
                self.assertTrue(audio_file.exists())
                self.assertGreater(audio_file.stat().st_size, 0)
            finally:
                sys.argv = old_argv


if __name__ == "__main__":
    unittest.main()
