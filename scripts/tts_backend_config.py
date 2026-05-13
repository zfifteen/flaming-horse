"""Shared TTS backend configuration helpers."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any


VALID_BACKENDS = {"qwen", "mlx"}

DEFAULT_QWEN_PYTHON = (
    "~/IdeaProjects/flaming-horse/models/qwen3-tts-local/.venv/bin/python"
)
DEFAULT_QWEN_MODEL_ID = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"
DEFAULT_MLX_MODEL_ID = "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit"
DEFAULT_OUTPUT_DIR = "media/voiceovers/qwen"


def selected_tts_backend(cfg: dict[str, Any] | None = None) -> str:
    value = os.environ.get("FLAMING_HORSE_TTS_BACKEND", "").strip().lower()
    if not value and cfg is not None:
        configured = cfg.get("backend")
        if isinstance(configured, str):
            value = configured.strip().lower()
    if not value:
        value = "qwen"
    if value not in VALID_BACKENDS:
        raise ValueError(
            f"Invalid FLAMING_HORSE_TTS_BACKEND={value!r}. "
            "Expected 'qwen' or 'mlx'."
        )
    return value


def selected_model_id(cfg: dict[str, Any], backend: str) -> str:
    if backend == "mlx":
        override = os.environ.get("FLAMING_HORSE_MLX_MODEL_ID", "").strip()
        if override:
            return override
        configured = cfg.get("model_id")
        if isinstance(configured, str) and configured.startswith("mlx-community/"):
            return configured
        return DEFAULT_MLX_MODEL_ID

    configured = cfg.get("model_id")
    if isinstance(configured, str) and configured.strip():
        return configured.strip()
    return DEFAULT_QWEN_MODEL_ID


def selected_worker_python_raw(cfg: dict[str, Any], backend: str) -> str:
    if backend == "mlx":
        for key in ("FLAMING_HORSE_MLX_PYTHON", "PYTHON"):
            value = os.environ.get(key, "").strip()
            if value:
                return value
        configured = cfg.get("worker_python")
        if isinstance(configured, str) and configured.strip():
            return configured.strip()
        return sys.executable

    configured = cfg.get("qwen_python")
    if isinstance(configured, str) and configured.strip():
        return configured.strip()
    value = os.environ.get("FLAMING_HORSE_QWEN_PYTHON", "").strip()
    if value:
        return value
    return DEFAULT_QWEN_PYTHON


def expand_python_path(raw: str, cwd: Path | None = None) -> Path:
    path = Path(os.path.expanduser(raw))
    if path.is_absolute():
        return path
    base = cwd if cwd is not None else Path.cwd()
    return (base / path).absolute()


def selected_worker_python(cfg: dict[str, Any], backend: str) -> Path:
    return expand_python_path(selected_worker_python_raw(cfg, backend))


def selected_output_dir(cfg: dict[str, Any]) -> str:
    configured = cfg.get("output_dir")
    if isinstance(configured, str) and configured.strip():
        return configured.strip()
    return DEFAULT_OUTPUT_DIR
