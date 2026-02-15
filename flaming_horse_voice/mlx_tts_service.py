import hashlib
import json
import os
import sys
from pathlib import Path

import soundfile as sf
import mlx.core as mx  # For eval/cache
from mlx_audio.tts.generate import generate_audio
from mlx_audio.tts.utils import load_model

# Config (env overrides optional; backward-compatible defaults)
MODEL_ID = os.environ.get(
    "MLX_MODEL_ID",
    sys.argv[2] if len(sys.argv) > 2 else "mlx-community/Qwen3-TTS-12Hz-0.6B-Base-4bit",
)
REF_AUDIO = os.environ.get(
    "MLX_REF_AUDIO", "/Users/velocityworks/qwen3-tts-local/voice_ref/ref.wav"
)
REF_TEXT = os.environ.get(
    "MLX_REF_TEXT",
    Path(REF_AUDIO.replace(".wav", ".txt")).read_text(encoding="utf-8").strip(),
)
OUTPUT_DIR = Path(os.environ.get("MLX_OUTPUT_DIR", "mlx_outputs"))
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# Load once (in subprocess to isolate)
model = load_model(MODEL_ID)


def cache_key(text: str) -> str:
    ref_hash = hashlib.md5(Path(REF_AUDIO).read_bytes()).hexdigest()[:8]
    return hashlib.md5(f"{MODEL_ID}:{text}:{ref_hash}".encode()).hexdigest()


def synthesize_batch(
    segments: list[dict],
) -> list[dict]:  # Returns [{"id": "seg1", "path": str, "duration": float}]
    results = []
    for seg in segments:
        key = cache_key(seg["text"])
        cached_path = OUTPUT_DIR / f"{key}.wav"
        if cached_path.exists():
            duration = len(sf.read(cached_path)[0]) / 24000
            results.append(
                {
                    "id": seg["id"],
                    "path": str(cached_path),
                    "duration": duration,
                    "from_cache": True,
                }
            )
            continue
        out_prefix = OUTPUT_DIR / seg["id"]
        generate_audio(
            model=model,
            text=seg["text"],
            ref_audio=REF_AUDIO,
            ref_text=REF_TEXT,
            file_prefix=str(out_prefix),
            audio_format="wav",
            join_audio=True,  # Single WAV, no chunks
            verbose=True,  # Timings
        )
        wav_path = OUTPUT_DIR / f"{seg['id']}_000.wav"
        if not wav_path.exists():
            direct_path = OUTPUT_DIR / f"{seg['id']}.wav"
            if direct_path.exists():
                wav_path = direct_path
            else:
                candidates = sorted(OUTPUT_DIR.glob(f"{seg['id']}*.wav"))
                if not candidates:
                    raise FileNotFoundError(
                        f"No output for prefix {seg['id']} in {OUTPUT_DIR}"
                    )
                wav_path = candidates[0]
        # Rename to cache key
        cached_path = OUTPUT_DIR / f"{key}.wav"
        wav_path.rename(cached_path)
        duration = len(sf.read(cached_path)[0]) / 24000
        results.append(
            {
                "id": seg["id"],
                "path": str(cached_path),
                "duration": duration,
                "from_cache": False,
            }
        )
        mx.eval(model.parameters())  # Force eval
        if hasattr(mx, "metal") and hasattr(mx.metal, "clear_cache"):
            mx.metal.clear_cache()  # Memory hygiene
    return results


# Example usage (run via subprocess: mlx_env/bin/python mlx_tts_service.py '[json segments]')
if __name__ == "__main__":
    segments_str = (
        sys.argv[1]
        if len(sys.argv) > 1
        else json.dumps(
            [
                {
                    "id": "test1",
                    "text": "Matrix A times B yields C where C_ij = sum(A_ik * B_kj).",
                }
            ]
        )
    )
    segments = json.loads(segments_str)
    results = synthesize_batch(segments)
    print(
        json.dumps(
            [
                {
                    "id": r["id"],
                    "path": r["path"],
                    "duration": r["duration"],
                    "from_cache": r["from_cache"],
                }
                for r in results
            ]
        )
    )
