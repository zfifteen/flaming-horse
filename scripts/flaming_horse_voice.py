import json
from pathlib import Path
from manim_voiceover_plus.services.base import SpeechService
from manim_voiceover_plus.services.audio import AudioFileReader


class CachedQwenService(SpeechService):
    def __init__(self, project_dir: Path):
        super().__init__()
        self.project_dir = project_dir
        config_path = project_dir / "voice_clone_config.json"
        self.config = json.load(config_path.open(encoding="utf-8"))
        cache_path = project_dir / self.config["output_dir"] / "cache.json"
        self.cache = {
            e["narration_key"]: e for e in json.load(cache_path.open(encoding="utf-8"))
        }
        self.audio_reader = AudioFileReader()

    def generate_speech(self, text):
        # Find matching cache entry by text (exact match)
        for key, entry in self.cache.items():
            if entry["text"] == text:
                audio_path = (
                    self.project_dir / self.config["output_dir"] / entry["audio_file"]
                )
                audio = self.audio_reader.read(str(audio_path))
                return audio, entry["duration_seconds"]
        raise ValueError(f"No cached audio for text: {text[:50]}...")


def get_speech_service(project_dir: Path):
    return CachedQwenService(project_dir)
