"""Voice service factory for strict cached pipeline audio."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def get_speech_service(project_dir):
    """Create the strict cached speech service or fail."""
    project_dir = Path(project_dir).resolve()
    cfg_path = project_dir / "voice_clone_config.json"
    if not cfg_path.exists():
        raise FileNotFoundError(f"Missing voice config: {cfg_path}")

    repo_root = Path(__file__).resolve().parents[1]
    scripts_dir = repo_root / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))

    from tts_backend_config import selected_tts_backend

    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    _backend = selected_tts_backend(cfg)

    # Validate backend/config consistency before returning the backend-neutral
    # cache reader. MLX generation writes the same cache.json/mp3 format as Qwen.
    from flaming_horse_voice.qwen_cached import QwenCachedService

    return QwenCachedService.from_project(project_dir)
