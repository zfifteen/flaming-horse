"""Single integration point for TTS backend model calls.

Backends:
- qwen: legacy local qwen_tts (default)
- mlx:  MLX subprocess service via flaming_horse_voice/mlx_tts_service.py

Backend is selected with environment variable:
  FLAMING_HORSE_TTS_BACKEND=qwen|mlx
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

import torch


DEFAULT_MLX_PYTHON = "/Users/velocityworks/qwen3-tts-local/mlx_env312/bin/python"
DEFAULT_MLX_MODEL_ID = "mlx-community/Qwen3-TTS-12Hz-0.6B-Base-4bit"


def _backend() -> str:
    raw = os.environ.get("FLAMING_HORSE_TTS_BACKEND", "qwen").strip().lower()
    if raw not in {"qwen", "mlx"}:
        raise ValueError(
            f"Unsupported FLAMING_HORSE_TTS_BACKEND={raw!r}. Expected 'qwen' or 'mlx'."
        )
    return raw


def _mlx_python() -> str:
    return os.environ.get("FLAMING_HORSE_MLX_PYTHON", DEFAULT_MLX_PYTHON).strip()


def _mlx_service_script() -> str:
    configured = os.environ.get("FLAMING_HORSE_MLX_SERVICE_SCRIPT", "").strip()
    if configured:
        return configured
    repo_root = Path(__file__).resolve().parents[1]
    return str(repo_root / "flaming_horse_voice" / "mlx_tts_service.py")


def _mlx_model_id(model_source: str | None) -> str:
    override = os.environ.get("FLAMING_HORSE_MLX_MODEL_ID", "").strip()
    if override:
        return override
    if isinstance(model_source, str) and model_source.strip():
        source = model_source.strip()
        if source.startswith("mlx-community/"):
            return source
    return DEFAULT_MLX_MODEL_ID


def _run_mlx_generation(
    *,
    model_source: str,
    text: str,
    ref_audio: str,
    ref_text: str,
):
    mlx_python = _mlx_python()
    service_script = _mlx_service_script()
    segments = [{"id": "seg", "text": text}]

    env = os.environ.copy()
    env["MLX_REF_AUDIO"] = str(ref_audio)
    env["MLX_REF_TEXT"] = str(ref_text)
    env.setdefault(
        "MLX_OUTPUT_DIR", str(Path.cwd() / "media" / "voiceovers" / "mlx_tmp")
    )

    cmd = [
        mlx_python,
        service_script,
        json.dumps(segments),
        _mlx_model_id(model_source),
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=600,
        env=env,
    )
    if result.returncode != 0:
        raise RuntimeError(f"MLX generation failed: {result.stderr.strip()}")

    lines = [ln.strip() for ln in result.stdout.splitlines() if ln.strip()]
    if not lines:
        raise RuntimeError("MLX generation returned empty output")

    try:
        payload = json.loads(lines[-1])
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"MLX generation returned invalid JSON: {exc}") from exc

    if not payload:
        raise RuntimeError("MLX generation returned no audio paths")
    path = payload[0].get("path")
    if not isinstance(path, str) or not path.strip():
        raise RuntimeError("MLX generation payload missing audio path")
    audio_path = Path(path)
    if not audio_path.is_absolute():
        audio_path = Path.cwd() / audio_path
    if not audio_path.exists():
        raise FileNotFoundError(f"MLX output path not found: {audio_path}")

    import numpy as np
    import soundfile as sf

    wav, sr = sf.read(str(audio_path), dtype="float32")
    wav_arr = np.asarray(wav, dtype=np.float32)
    if wav_arr.ndim > 1:
        wav_arr = wav_arr[:, 0]
    return [wav_arr], int(sr)


def _dtype_from_string(dtype_str: str) -> Any:
    dtype_map = {
        "float16": torch.float16,
        "bfloat16": torch.bfloat16,
        "float32": torch.float32,
    }
    if dtype_str not in dtype_map:
        raise ValueError(f"Unsupported dtype: {dtype_str}")
    return dtype_map[dtype_str]


def load_model(model_source: str, device: str, dtype_str: str):
    """Load backend model handle with consistent input handling."""
    if _backend() == "mlx":
        return {
            "backend": "mlx",
            "model_source": str(model_source),
            "device": str(device),
            "dtype": str(dtype_str),
        }

    from qwen_tts import Qwen3TTSModel  # type: ignore

    return Qwen3TTSModel.from_pretrained(
        str(model_source),
        device_map=device,
        dtype=_dtype_from_string(dtype_str),
    )


def build_voice_clone_prompt(model, ref_audio: str, ref_text: str):
    """Build backend prompt context for cloning."""
    if isinstance(model, dict) and model.get("backend") == "mlx":
        return {
            "backend": "mlx",
            "model_source": str(model.get("model_source") or ""),
            "ref_audio": str(ref_audio),
            "ref_text": str(ref_text),
        }

    if not hasattr(model, "create_voice_clone_prompt"):
        raise RuntimeError("Loaded model does not support create_voice_clone_prompt")

    return model.create_voice_clone_prompt(
        ref_audio=str(ref_audio),
        ref_text=str(ref_text),
        x_vector_only_mode=False,
    )


def generate_voice_clone(model, text: str, language: str, voice_clone_prompt):
    """Generate cloned voice waveform via selected backend."""
    if (
        isinstance(voice_clone_prompt, dict)
        and voice_clone_prompt.get("backend") == "mlx"
    ):
        return _run_mlx_generation(
            model_source=str(voice_clone_prompt.get("model_source") or ""),
            text=text,
            ref_audio=str(voice_clone_prompt.get("ref_audio") or ""),
            ref_text=str(voice_clone_prompt.get("ref_text") or ""),
        )

    if not hasattr(model, "generate_voice_clone"):
        raise RuntimeError("Loaded model does not support generate_voice_clone")

    return model.generate_voice_clone(
        text=text,
        language=language,
        voice_clone_prompt=voice_clone_prompt,
    )
