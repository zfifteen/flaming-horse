import os
import time
from pathlib import Path

import numpy as np
import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel


def main() -> int:
    # Slow-but-stable defaults.
    os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")

    model_id = os.environ.get("QWEN_TTS_MODEL", "Qwen/Qwen3-TTS-12Hz-1.7B-Base")
    device = os.environ.get("QWEN_TTS_DEVICE", "cpu")
    dtype_str = os.environ.get("QWEN_TTS_DTYPE", "float32")

    ref_audio = os.environ.get(
        "QWEN_TTS_REF_AUDIO",
        str(Path(__file__).resolve().parent / "ref" / "ref_voice_elevenlabs.wav"),
    )
    ref_text = os.environ.get("QWEN_TTS_REF_TEXT", "")

    text = os.environ.get(
        "QWEN_TTS_TEXT",
        "This is a voice clone test. If this works, the voice should sound like the reference speaker.",
    )
    language = os.environ.get("QWEN_TTS_LANG", "English")

    dtype_map = {
        "float16": torch.float16,
        "bfloat16": torch.bfloat16,
        "float32": torch.float32,
    }
    if dtype_str not in dtype_map:
        raise SystemExit(
            f"Unsupported QWEN_TTS_DTYPE={dtype_str!r}; use one of {list(dtype_map)}"
        )

    if not ref_text.strip():
        raise SystemExit(
            "QWEN_TTS_REF_TEXT is required for voice clone (unless using x_vector_only_mode). "
            "Set it to the transcript of the reference audio."
        )

    out_dir = Path(__file__).resolve().parent / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "voice_clone.wav"

    print(
        f"torch={torch.__version__} mps_available={torch.backends.mps.is_available()}"
    )
    print(f"model={model_id}")
    print(f"device={device} dtype={dtype_str}")
    print(f"ref_audio={ref_audio}")
    print(f"ref_text_len={len(ref_text)}")

    t0 = time.perf_counter()
    model = Qwen3TTSModel.from_pretrained(
        model_id,
        device_map=device,
        dtype=dtype_map[dtype_str],
    )
    print(f"loaded model in {time.perf_counter() - t0:.1f}s")

    t1 = time.perf_counter()
    wavs, sr = model.generate_voice_clone(
        text=text,
        language=language,
        ref_audio=ref_audio,
        ref_text=ref_text,
    )
    print(f"generated in {time.perf_counter() - t1:.1f}s")

    wav = np.asarray(wavs[0], dtype=np.float32)
    sf.write(out_path, wav, sr, subtype="PCM_16")
    print(f"wrote: {out_path} (sr={sr}, seconds={len(wav) / sr:.2f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
