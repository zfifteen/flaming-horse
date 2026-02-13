import ast
import hashlib
import json
from pathlib import Path

from manim_voiceover_plus.defaults import DEFAULT_VOICEOVER_CACHE_DIR
from manim_voiceover_plus.services.base import SpeechService


class QwenCachedService(SpeechService):
    @staticmethod
    def _load_script(script_path: Path) -> dict:
        try:
            tree = ast.parse(
                script_path.read_text(encoding="utf-8"), filename=str(script_path)
            )
        except (OSError, SyntaxError, ValueError):
            return {}
        for node in tree.body:
            if not isinstance(node, ast.Assign):
                continue
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "SCRIPT":
                    try:
                        value = ast.literal_eval(node.value)
                    except (ValueError, TypeError):
                        return {}
                    return value if isinstance(value, dict) else {}
        return {}

    def __init__(
        self,
        project_dir,
        cache_dir,
        cache_index,
        text_index,
        transcription_model=None,
        **kwargs,
    ):
        self.project_dir = project_dir
        self.cache_index = cache_index
        self.text_index = text_index
        super().__init__(
            cache_dir=str(cache_dir),
            transcription_model=transcription_model,
            **kwargs,
        )

    @classmethod
    def from_project(cls, project_dir):
        project_dir = Path(project_dir).resolve()
        cache_dir = project_dir / "media" / DEFAULT_VOICEOVER_CACHE_DIR / "qwen"
        config_path = project_dir / "voice_clone_config.json"
        if config_path.exists():
            try:
                config = json.loads(config_path.read_text(encoding="utf-8"))
                output_dir = config.get("output_dir")
                if output_dir:
                    output_path = Path(output_dir).expanduser()
                    cache_dir = (
                        output_path
                        if output_path.is_absolute()
                        else project_dir / output_dir
                    )
            except (json.JSONDecodeError, OSError):
                pass
        cache_file = cache_dir / "cache.json"
        cache_index = {}
        text_index = {}
        if cache_file.exists():
            for entry in json.loads(cache_file.read_text(encoding="utf-8")):
                key = entry.get("narration_key")
                audio_file = entry.get("audio_file")
                text = entry.get("text")
                if key and audio_file:
                    cache_index[key] = audio_file
                if text and audio_file:
                    normalized = " ".join(str(text).split())
                    text_index[normalized] = audio_file
        else:
            script_path = project_dir / "narration_script.py"
            if script_path.exists():
                for key, text in cls._load_script(script_path).items():
                    audio_file = f"{key}.mp3"
                    if (cache_dir / audio_file).exists():
                        cache_index[key] = audio_file
                        normalized = " ".join(str(text).split())
                        text_index[normalized] = audio_file

        if not cache_index:
            raise FileNotFoundError(
                f"Missing Qwen cache index: {cache_file}. Fallback lookup in narration_script.py also found no cached audio. Run precache step first."
            )

        return cls(
            project_dir=project_dir,
            cache_dir=cache_dir,
            cache_index=cache_index,
            text_index=text_index,
        )

    def _narration_key(self, input_data):
        return input_data.get("narration_key")

    def generate_from_text(
        self, text: str, cache_dir: str = None, path: str = None
    ) -> dict:
        input_data = {"input_text": text}

        narration_key = None
        if path:
            narration_key = Path(path).stem
        if narration_key is None:
            narration_key = self._narration_key(input_data)
        audio_file = None
        if narration_key:
            audio_file = self.cache_index.get(narration_key)
        if not audio_file:
            normalized = " ".join(text.split())
            audio_file = self.text_index.get(normalized)

        if not audio_file:
            raise FileNotFoundError(
                "Missing cached audio for narration text. Run precache step first."
            )
        cache_dir_path = Path(self.cache_dir)
        audio_path = cache_dir_path / audio_file

        if not audio_path.exists():
            raise FileNotFoundError(f"Cached audio file not found: {audio_path}")

        # Create a stable hash like the base service expects.
        data_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]
        return {
            "input_text": text,
            "input_data": {
                "input_text": text,
                "service": "qwen_cached",
                "config": {
                    "cache_dir": str(cache_dir_path),
                },
                "narration_key": narration_key,
            },
            "original_audio": audio_file,
            "final_audio": audio_file,
            "data_hash": data_hash,
            "cached": True,
        }
