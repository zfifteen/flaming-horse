from pathlib import Path

from .service_factory import get_speech_service as _get_speech_service


def get_speech_service(project_dir=None):
    if project_dir is None:
        project_dir = Path.cwd()
    return _get_speech_service(Path(project_dir))
