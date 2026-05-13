"""Voice service factory for strict cached pipeline audio."""

from __future__ import annotations

import os
from pathlib import Path


def get_speech_service(project_dir):
    """Create the strict cached speech service or fail."""
    project_dir = Path(project_dir).resolve()
    backend = os.environ.get("FLAMING_HORSE_TTS_BACKEND", "qwen").strip().lower()
    if backend not in {"qwen", "mlx"}:
        raise ValueError(
            f"Invalid FLAMING_HORSE_TTS_BACKEND={backend!r}. "
            "Expected 'qwen' or 'mlx'."
        )

    # The cache reader is backend-neutral. MLX generation writes the same
    # cache.json/mp3 format as the legacy Qwen path.
    from flaming_horse_voice.qwen_cached import QwenCachedService

    return QwenCachedService.from_project(project_dir)
