"""
Mock Qwen voice service for unblocked video generation.

This service generates dummy audio files (silent audio with appropriate duration)
so the video rendering pipeline can proceed without requiring cached Qwen assets.

Usage:
    Set FLAMING_HORSE_MOCK_VOICE=1 environment variable to use this service.
    
The service will:
- Generate silent audio segments based on text length
- Cache them like real voice generation
- Allow the full video pipeline to complete successfully
"""

import hashlib
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from manim_voiceover_plus.services.base import SpeechService


class QwenMockService(SpeechService):
    """Mock voice service that generates silent audio for testing/unblocking."""

    def __init__(
        self,
        cache_dir=None,
        transcription_model=None,
        words_per_second=2.5,
        **kwargs,
    ):
        """
        Args:
            words_per_second: Controls audio duration (default 2.5 = ~150 WPM)
        """
        self.words_per_second = words_per_second
        super().__init__(
            cache_dir=cache_dir,
            transcription_model=transcription_model,
            **kwargs,
        )

    def generate_from_text(
        self, text: str, cache_dir: str = None, path: str = None, **kwargs
    ) -> dict[str, Any]:
        """Generate dummy audio file with duration based on text length."""
        
        # Calculate duration based on word count
        word_count = len(text.split())
        duration = max(0.5, word_count / self.words_per_second)
        
        # Use provided path or generate cache key
        if path:
            output_path = Path(cache_dir or self.cache_dir) / Path(path).name
        else:
            # Generate a hash-based filename like real service
            text_hash = hashlib.md5(text.encode()).hexdigest()[:12]
            output_path = Path(cache_dir or self.cache_dir) / f"mock_{text_hash}.mp3"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate silent audio using sox
        # Format: sox -n -r 48000 -c 1 output.mp3 trim 0.0 <duration>
        try:
            subprocess.run(
                [
                    "sox",
                    "-n",  # null input (generate)
                    "-r", "48000",  # 48kHz sample rate
                    "-c", "1",  # mono
                    str(output_path),
                    "trim", "0.0", str(duration),
                ],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            # Fallback: create a tiny silent MP3 if sox fails
            # This ensures the pipeline never gets blocked
            print(f"Warning: sox failed, creating minimal audio: {e}")
            self._create_minimal_audio(output_path, duration)
        except FileNotFoundError:
            print("Warning: sox not found, creating minimal audio")
            self._create_minimal_audio(output_path, duration)
        
        return {
            "input_text": text,
            "input_data": {"text": text},
            "original_audio": str(output_path),
            "final_audio": str(output_path),
            "word_boundaries": self._generate_mock_word_boundaries(text, duration),
        }

    def _create_minimal_audio(self, output_path: Path, duration: float):
        """Create a minimal silent audio file using ffmpeg as fallback."""
        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-f", "lavfi",
                    "-i", f"anullsrc=r=48000:cl=mono",
                    "-t", str(duration),
                    "-q:a", "9",
                    "-acodec", "libmp3lame",
                    "-y",
                    str(output_path),
                ],
                check=True,
                capture_output=True,
                stderr=subprocess.DEVNULL,
            )
        except Exception as e:
            # Last resort: create empty file
            # Manim might complain but won't crash
            print(f"Warning: Could not generate audio, creating empty file: {e}")
            output_path.touch()

    def _generate_mock_word_boundaries(
        self, text: str, total_duration: float
    ) -> list[dict]:
        """Generate fake word timing data for compatibility."""
        words = text.split()
        if not words:
            return []
        
        time_per_word = total_duration / len(words)
        boundaries = []
        
        for i, word in enumerate(words):
            start = i * time_per_word
            end = (i + 1) * time_per_word
            boundaries.append({
                "word": word,
                "start": start,
                "end": end,
            })
        
        return boundaries


def create_mock_service(**kwargs):
    """Factory function for creating mock service instances."""
    return QwenMockService(**kwargs)
