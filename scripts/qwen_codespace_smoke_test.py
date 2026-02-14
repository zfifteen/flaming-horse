#!/usr/bin/env python3
"""Qwen3 TTS smoke test for local/Codespaces CPU execution.

Purpose:
- Verify local model loading with qwen_tts.Qwen3TTSModel
- Enforce CPU + float32
- Generate a short audio clip
- Write outputs/custom_voice.wav
- Print effective knobs + elapsed time

Behavior:
- Exits non-zero on any failure.
- Uses `model.generate(...)` when available.
- Otherwise uses voice-clone flow (`create_voice_clone_prompt` +
    `generate_voice_clone`) and requires explicit reference assets via env vars.
"""

from __future__ import annotations

import inspect
import os
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf
import torch


def env_required(key: str) -> str:
    value = os.environ.get(key)
    if value is None or str(value).strip() == "":
        raise RuntimeError(f"Missing required env var: {key}")
    return str(value)


def parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def parse_model_output(output: Any) -> tuple[np.ndarray, int]:
    if isinstance(output, tuple) and len(output) == 2:
        wavs, sample_rate = output
    elif isinstance(output, dict):
        wavs = output.get("wavs") or output.get("audio") or output.get("waveforms")
        sample_rate = output.get("sample_rate") or output.get("sr")
    else:
        raise RuntimeError(
            "Unsupported generation output format from qwen_tts model. "
            f"Type: {type(output).__name__}"
        )

    if wavs is None or sample_rate is None:
        raise RuntimeError("Model output did not include waveform(s) and sample rate")

    if isinstance(wavs, np.ndarray):
        if wavs.ndim == 1:
            wav = wavs
        elif wavs.ndim >= 2:
            wav = wavs[0]
        else:
            raise RuntimeError(f"Unexpected wav ndarray shape: {wavs.shape}")
    elif isinstance(wavs, list):
        if not wavs:
            raise RuntimeError("Model returned empty audio list")
        wav = np.asarray(wavs[0], dtype=np.float32)
    else:
        wav = np.asarray(wavs, dtype=np.float32)

    return np.asarray(wav, dtype=np.float32), int(sample_rate)


def resolve_ref_assets() -> tuple[Path, str]:
    ref_audio_env = os.environ.get("QWEN_TTS_REF_AUDIO", "").strip()
    ref_text_env = os.environ.get("QWEN_TTS_REF_TEXT", "").strip()

    if not ref_audio_env or not ref_text_env:
        raise RuntimeError(
            "This qwen_tts runtime requires reference assets. Set both "
            "QWEN_TTS_REF_AUDIO and QWEN_TTS_REF_TEXT to explicit existing files."
        )

    ref_audio = Path(ref_audio_env).expanduser().resolve()
    ref_text_path = Path(ref_text_env).expanduser().resolve()

    if not ref_audio.exists():
        raise RuntimeError(f"Reference audio not found: {ref_audio}")
    if not ref_text_path.exists():
        raise RuntimeError(f"Reference transcript not found: {ref_text_path}")

    ref_text = ref_text_path.read_text(encoding="utf-8").strip()
    if not ref_text:
        raise RuntimeError(f"Reference transcript is empty: {ref_text_path}")

    return ref_audio, ref_text


def build_generation_kwargs(method, *, text: str, language: str, speaker: str, instruct: str,
                            max_new_tokens: int, do_sample: bool, temperature: float,
                            top_p: float, repetition_penalty: float) -> dict[str, Any]:
    signature = inspect.signature(method)
    params = signature.parameters
    accepts_var_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values())

    candidate = {
        "text": text,
        "language": language,
        "speaker": speaker,
        "instruct": instruct,
        "prompt": f"{instruct}\nSpeaker: {speaker}.",
        "max_new_tokens": max_new_tokens,
        "do_sample": do_sample,
        "temperature": temperature,
        "top_p": top_p,
        "repetition_penalty": repetition_penalty,
    }

    if accepts_var_kwargs:
        return candidate

    return {k: v for k, v in candidate.items() if k in params}


def main() -> int:
    model_id = env_required("QWEN_TTS_MODEL")
    device = env_required("QWEN_TTS_DEVICE")
    dtype_str = env_required("QWEN_TTS_DTYPE")

    max_new_tokens = int(env_required("QWEN_TTS_MAX_NEW_TOKENS"))
    do_sample = parse_bool(env_required("QWEN_TTS_DO_SAMPLE"))
    temperature = float(env_required("QWEN_TTS_TEMPERATURE"))
    top_p = float(env_required("QWEN_TTS_TOP_P"))
    repetition_penalty = float(env_required("QWEN_TTS_REPETITION_PENALTY"))

    instruct = env_required("QWEN_TTS_INSTRUCT")
    speaker = env_required("QWEN_TTS_SPEAKER")
    language = env_required("QWEN_TTS_LANG")
    text = env_required("QWEN_TTS_TEXT")

    if device != "cpu":
        raise RuntimeError(f"QWEN_TTS_DEVICE must be 'cpu', got: {device!r}")
    if dtype_str != "float32":
        raise RuntimeError(f"QWEN_TTS_DTYPE must be 'float32', got: {dtype_str!r}")

    dtype_map = {
        "float16": torch.float16,
        "bfloat16": torch.bfloat16,
        "float32": torch.float32,
    }
    if dtype_str not in dtype_map:
        raise RuntimeError(f"Unsupported dtype: {dtype_str}")

    t0 = time.perf_counter()

    from qwen_tts import Qwen3TTSModel  # type: ignore

    model = Qwen3TTSModel.from_pretrained(
        model_id,
        device_map=device,
        dtype=dtype_map[dtype_str],
    )

    if hasattr(model, "generate"):
        generate_method = getattr(model, "generate")
        kwargs = build_generation_kwargs(
            generate_method,
            text=text,
            language=language,
            speaker=speaker,
            instruct=instruct,
            max_new_tokens=max_new_tokens,
            do_sample=do_sample,
            temperature=temperature,
            top_p=top_p,
            repetition_penalty=repetition_penalty,
        )

        output = generate_method(**kwargs)
        wav, sample_rate = parse_model_output(output)
        generation_mode = "generate"
    else:
        if not hasattr(model, "create_voice_clone_prompt") or not hasattr(
            model, "generate_voice_clone"
        ):
            raise RuntimeError(
                "Installed qwen_tts package has neither model.generate(...) nor "
                "voice-clone methods."
            )

        ref_audio, ref_text = resolve_ref_assets()
        prompt = model.create_voice_clone_prompt(
            ref_audio=str(ref_audio),
            ref_text=ref_text,
            x_vector_only_mode=False,
        )
        wavs, sample_rate = model.generate_voice_clone(
            text=text,
            language=language,
            voice_clone_prompt=prompt,
        )
        wav = np.asarray(wavs[0], dtype=np.float32)
        generation_mode = "voice_clone"

    out_path = Path("outputs/custom_voice.wav")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(out_path, wav, sample_rate, subtype="PCM_16")

    elapsed = time.perf_counter() - t0

    print(f"model_id={model_id}")
    print(f"device={device}")
    print(f"dtype={dtype_str}")
    print(f"max_new_tokens={max_new_tokens}")
    print(f"do_sample={int(do_sample)}")
    print(f"temperature={temperature}")
    print(f"top_p={top_p}")
    print(f"repetition_penalty={repetition_penalty}")
    print(f"generation_mode={generation_mode}")
    print(f"elapsed_seconds={elapsed:.3f}")
    print(f"output={out_path}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)
