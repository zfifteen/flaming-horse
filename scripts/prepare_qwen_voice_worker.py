#!/usr/bin/env python3
"""Worker for scripts/prepare_qwen_voice.py.

Runs inside the Qwen environment specified by voice_clone_config.json.qwen_python.
Outputs progress to stderr and final JSON to stdout.
"""

from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
from transformers.utils import logging as hf_logging

from qwen_tts_mediator import (
    build_voice_clone_prompt,
    generate_voice_clone,
    load_model,
)


def eprint(msg: str) -> None:
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()


def main() -> int:
    # Keep HF/transformers warnings from polluting progress output.
    hf_logging.set_verbosity_error()
    eprint(f"→ Python: {sys.executable}")
    payload = json.loads(sys.stdin.read() or "{}")
    backend = os.environ.get("FLAMING_HORSE_TTS_BACKEND", "qwen").strip().lower()
    model_source = payload.get("model_source")
    device = payload.get("device")
    dtype_str = payload.get("dtype")
    language = payload.get("language")
    ref_audio = payload.get("ref_audio")
    ref_text = payload.get("ref_text")
    dry_run = bool(payload.get("dry_run", True))
    dry_run_text = payload.get("dry_run_text", "Warmup.")
    for k in (
        "model_source",
        "device",
        "dtype",
        "language",
        "ref_audio",
        "ref_text",
    ):
        if not payload.get(k):
            raise SystemExit(f"missing required field: {k}")

    timings = {}

    eprint(f"→ Loading TTS backend model ({backend})")
    t0 = time.perf_counter()
    try:
        model = load_model(str(model_source), str(device), str(dtype_str))
    except Exception as e:
        eprint(f"ERROR: Failed to load TTS backend model ({backend})")
        eprint(f"  Exception: {type(e).__name__}: {e}")
        eprint("  sys.path (first 5):")
        for p in sys.path[:5]:
            eprint(f"    - {p}")
        raise
    timings["model_load_seconds"] = round(time.perf_counter() - t0, 3)
    eprint(f"✓ Loaded model in {timings['model_load_seconds']:.3f}s")

    eprint(f"→ Building voice clone prompt ({backend})")
    t1 = time.perf_counter()
    voice_clone_prompt = build_voice_clone_prompt(
        model,
        ref_audio=str(ref_audio),
        ref_text=str(ref_text),
    )
    timings["prompt_build_seconds"] = round(time.perf_counter() - t1, 3)
    eprint(f"✓ Prompt built in {timings['prompt_build_seconds']:.3f}s")

    if dry_run:
        eprint("→ Dry-run generation")
        t2 = time.perf_counter()
        wavs, sr = generate_voice_clone(
            model,
            text=str(dry_run_text),
            language=str(language),
            voice_clone_prompt=voice_clone_prompt,
        )
        timings["dry_run_generate_seconds"] = round(time.perf_counter() - t2, 3)
        wav = np.asarray(wavs[0], dtype=np.float32)
        timings["dry_run_audio_seconds"] = float(len(wav) / float(sr)) if sr else 0.0
        eprint(
            f"✓ Dry-run ok ({timings['dry_run_audio_seconds']:.2f}s audio) in {timings['dry_run_generate_seconds']:.3f}s"
        )

    print(json.dumps(timings))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
