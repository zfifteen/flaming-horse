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
REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REF_AUDIO = REPO_ROOT / "assets" / "voice_ref" / "ref.wav"
MODEL_ID = os.environ.get(
    "MLX_MODEL_ID",
    sys.argv[2] if len(sys.argv) > 2 else "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit",
)
REF_AUDIO = os.environ.get(
    "MLX_REF_AUDIO", str(DEFAULT_REF_AUDIO)
)
REF_TEXT = os.environ.get("MLX_REF_TEXT", "").strip()
MODEL = None


def resolve_output_dir() -> Path:
    output_dir = Path(os.environ.get("MLX_OUTPUT_DIR", "mlx_outputs"))
    output_dir.mkdir(exist_ok=True, parents=True)
    return output_dir


def get_model():
    global MODEL
    if MODEL is None:
        MODEL = load_model(MODEL_ID)
    return MODEL


def resolve_ref_audio(ref_audio: str) -> Path:
    ref_audio_path = Path(ref_audio)
    if not ref_audio_path.exists():
        raise ValueError(
            "Missing MLX reference audio. Set MLX_REF_AUDIO to an existing file."
        )
    if not ref_audio_path.is_file():
        raise ValueError(f"MLX_REF_AUDIO is not a file: {ref_audio_path}")
    return ref_audio_path


def cache_key(text: str, ref_audio_path: Path) -> str:
    try:
        ref_hash = hashlib.md5(ref_audio_path.read_bytes()).hexdigest()[:8]
    except OSError as exc:
        raise ValueError(f"Unable to read MLX reference audio: {ref_audio_path}") from exc
    return hashlib.md5(f"{MODEL_ID}:{text}:{ref_hash}".encode()).hexdigest()


def resolve_ref_text(ref_audio: str, ref_text: str = "") -> str:
    configured = ref_text.strip()
    if configured:
        return configured

    transcript_path = Path(ref_audio).with_suffix(".txt")
    if not transcript_path.exists():
        raise ValueError(
            "Missing MLX reference transcript. Set MLX_REF_TEXT or create "
            f"{transcript_path} next to MLX_REF_AUDIO."
        )

    resolved = transcript_path.read_text(encoding="utf-8").strip()
    if not resolved:
        raise ValueError(f"MLX reference transcript is empty: {transcript_path}")
    return resolved


def synthesize_batch(
    segments: list[dict],
) -> list[dict]:  # Returns [{"id": "seg1", "path": str, "duration": float}]
    results = []
    ref_audio_path = resolve_ref_audio(REF_AUDIO)
    ref_text = resolve_ref_text(str(ref_audio_path), REF_TEXT)
    output_dir = resolve_output_dir()
    model = get_model()
    for seg in segments:
        key = cache_key(seg["text"], ref_audio_path)
        cached_path = output_dir / f"{key}.wav"
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
        out_prefix = output_dir / seg["id"]
        generate_audio(
            model=model,
            text=seg["text"],
            ref_audio=str(ref_audio_path),
            ref_text=ref_text,
            file_prefix=str(out_prefix),
            audio_format="wav",
            join_audio=True,  # Single WAV, no chunks
            verbose=True,  # Timings
        )
        wav_path = output_dir / f"{seg['id']}_000.wav"
        if not wav_path.exists():
            direct_path = output_dir / f"{seg['id']}.wav"
            if direct_path.exists():
                wav_path = direct_path
            else:
                candidates = sorted(output_dir.glob(f"{seg['id']}*.wav"))
                if not candidates:
                    raise FileNotFoundError(
                        f"No output for prefix {seg['id']} in {output_dir}"
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
        # MLX >=0.30 prefers mx.clear_cache(); keep backward compatibility.
        if hasattr(mx, "clear_cache"):
            mx.clear_cache()
        elif hasattr(mx, "metal") and hasattr(mx.metal, "clear_cache"):
            mx.metal.clear_cache()
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
