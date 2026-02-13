from pathlib import Path

from .qwen_cached import QwenCachedService


def get_speech_service(project_dir=None) -> QwenCachedService:
    if project_dir is None:
        project_dir = Path.cwd()
    return QwenCachedService.from_project(Path(project_dir))
