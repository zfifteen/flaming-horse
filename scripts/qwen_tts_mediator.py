"""Single integration point for Qwen TTS model calls.

This module centralizes all direct usage of the qwen_tts API so callers do not
depend on model-specific method names or dtype wiring.
"""

from __future__ import annotations

from typing import Any

import torch


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
    """Load Qwen3TTSModel with consistent dtype/device handling."""
    from qwen_tts import Qwen3TTSModel  # type: ignore

    return Qwen3TTSModel.from_pretrained(
        str(model_source),
        device_map=device,
        dtype=_dtype_from_string(dtype_str),
    )


def build_voice_clone_prompt(model, ref_audio: str, ref_text: str):
    """Build voice clone prompt using the Qwen model API."""
    if not hasattr(model, "create_voice_clone_prompt"):
        raise RuntimeError("Loaded model does not support create_voice_clone_prompt")

    return model.create_voice_clone_prompt(
        ref_audio=str(ref_audio),
        ref_text=str(ref_text),
        x_vector_only_mode=False,
    )


def generate_voice_clone(model, text: str, language: str, voice_clone_prompt):
    """Generate cloned voice waveform using the Qwen model API."""
    if not hasattr(model, "generate_voice_clone"):
        raise RuntimeError("Loaded model does not support generate_voice_clone")

    return model.generate_voice_clone(
        text=text,
        language=language,
        voice_clone_prompt=voice_clone_prompt,
    )
