#!/usr/bin/env python3
"""Worker for scripts/prepare_qwen_voice.py.

Runs inside the Qwen environment specified by voice_clone_config.json.qwen_python.
Outputs progress to stderr and final JSON to stdout.
"""

from __future__ import annotations

import json
import sys
import time

import numpy as np
import torch
from transformers.utils import logging as hf_logging


def eprint(msg: str) -> None:
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()


def main() -> int:
    # Keep HF/transformers warnings from polluting progress output.
    hf_logging.set_verbosity_error()
    eprint(f"→ Python: {sys.executable}")
    payload = json.loads(sys.stdin.read() or "{}")
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

    dtype_map = {
        "float16": torch.float16,
        "bfloat16": torch.bfloat16,
        "float32": torch.float32,
    }
    if dtype_str not in dtype_map:
        raise SystemExit(f"unsupported dtype: {dtype_str}")

    try:
        from qwen_tts import Qwen3TTSModel  # type: ignore
    except Exception as e:
        eprint("ERROR: Failed to import qwen_tts inside Qwen environment")
        eprint(f"  Exception: {type(e).__name__}: {e}")
        eprint("  sys.path (first 5):")
        for p in sys.path[:5]:
            eprint(f"    - {p}")
        raise

    timings = {}

    eprint("→ Loading Qwen model")
    t0 = time.perf_counter()
    model = Qwen3TTSModel.from_pretrained(
        str(model_source),
        device_map=device,
        dtype=dtype_map[dtype_str],
    )
    timings["model_load_seconds"] = round(time.perf_counter() - t0, 3)
    eprint(f"✓ Loaded model in {timings['model_load_seconds']:.3f}s")

    eprint("→ Building voice clone prompt")
    t1 = time.perf_counter()
    voice_clone_prompt = model.create_voice_clone_prompt(
        ref_audio=str(ref_audio),
        ref_text=str(ref_text),
        x_vector_only_mode=False,
    )
    timings["prompt_build_seconds"] = round(time.perf_counter() - t1, 3)
    eprint(f"✓ Prompt built in {timings['prompt_build_seconds']:.3f}s")

    if dry_run:
        eprint("→ Dry-run generation")
        t2 = time.perf_counter()
        wavs, sr = model.generate_voice_clone(
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
