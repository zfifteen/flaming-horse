"""Shared TTS backend configuration helpers."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any


VALID_BACKENDS = {"qwen", "mlx"}

DEFAULT_QWEN_MODEL_ID = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"
DEFAULT_MLX_MODEL_ID = "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit"
DEFAULT_OUTPUT_DIR = "media/voiceovers/qwen"


def _non_empty(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    return ""


def _env_value(name: str) -> str:
    return os.environ.get(name, "").strip()


def selected_tts_backend(cfg: dict[str, Any] | None = None) -> str:
    env_backend = _env_value("FLAMING_HORSE_TTS_BACKEND").lower()
    cfg_backend = _non_empty((cfg or {}).get("backend")).lower()
    if env_backend and cfg_backend and env_backend != cfg_backend:
        raise ValueError(
            "TTS backend mismatch: FLAMING_HORSE_TTS_BACKEND="
            f"{env_backend!r} but voice_clone_config.json backend={cfg_backend!r}."
        )

    value = env_backend or cfg_backend
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
        env_model = _env_value("FLAMING_HORSE_MLX_MODEL_ID")
        if env_model:
            return env_model
        configured = _non_empty(cfg.get("model_id"))
        if configured:
            return configured
        return DEFAULT_MLX_MODEL_ID

    env_model = _env_value("FLAMING_HORSE_QWEN_MODEL_ID")
    if env_model:
        return env_model
    configured = _non_empty(cfg.get("model_id"))
    if configured:
        return configured
    return DEFAULT_QWEN_MODEL_ID


def selected_worker_python_raw(cfg: dict[str, Any], backend: str) -> str:
    if backend == "mlx":
        env_python = _env_value("FLAMING_HORSE_MLX_PYTHON")
        if env_python:
            return env_python
        configured = _non_empty(cfg.get("worker_python"))
        if configured:
            return configured
        raise ValueError(
            "Missing MLX worker Python. Set FLAMING_HORSE_MLX_PYTHON or "
            'voice_clone_config.json["worker_python"].'
        )

    env_python = _env_value("FLAMING_HORSE_QWEN_PYTHON")
    if env_python:
        return env_python
    configured = _non_empty(cfg.get("qwen_python"))
    if configured:
        return configured
    raise ValueError(
        "Missing Qwen worker Python. Set FLAMING_HORSE_QWEN_PYTHON or "
        'voice_clone_config.json["qwen_python"].'
    )


def expand_python_path(raw: str, cwd: Path | None = None) -> Path:
    path = Path(os.path.expanduser(raw))
    if path.is_absolute():
        return path
    base = cwd if cwd is not None else Path.cwd()
    return (base / path).absolute()


def selected_worker_python(cfg: dict[str, Any], backend: str) -> Path:
    return expand_python_path(selected_worker_python_raw(cfg, backend))


def selected_output_dir(cfg: dict[str, Any]) -> str:
    configured = _non_empty(cfg.get("output_dir"))
    if configured:
        return configured
    return DEFAULT_OUTPUT_DIR


def build_voice_clone_config(cfg: dict[str, Any] | None = None) -> dict[str, Any]:
    base = dict(cfg or {})
    backend = selected_tts_backend(base)
    worker_python = selected_worker_python_raw(base, backend)
    model_id = selected_model_id(base, backend)
    output_dir = selected_output_dir(base)

    qwen_python = (
        selected_worker_python_raw(base, "qwen")
        if backend == "qwen"
        else _non_empty(base.get("qwen_python")) or worker_python
    )

    return {
        "backend": backend,
        "worker_python": worker_python,
        "qwen_python": qwen_python,
        "model_id": model_id,
        "device": base.get("device", "cpu"),
        "dtype": base.get("dtype", "float32"),
        "language": base.get("language", "English"),
        "ref_audio": base.get("ref_audio", "assets/voice_ref/ref.wav"),
        "ref_text": base.get("ref_text", "assets/voice_ref/ref.txt"),
        "output_dir": output_dir,
    }


def write_voice_clone_config(output_path: Path) -> None:
    cfg = build_voice_clone_config({})
    output_path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Write a Flaming Horse voice_clone_config.json"
    )
    parser.add_argument("--write-voice-config", type=Path, required=True)
    args = parser.parse_args()
    write_voice_clone_config(args.write_voice_config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
