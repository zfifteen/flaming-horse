"""Voice service factory for strict cached Qwen usage."""

from pathlib import Path


def get_speech_service(project_dir):
    """Create strict cached Qwen speech service or fail."""
    project_dir = Path(project_dir).resolve()

    from flaming_horse_voice.qwen_cached import QwenCachedService

    return QwenCachedService.from_project(project_dir)
