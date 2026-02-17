import os
import time
from pathlib import Path

import numpy as np
import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel


def _silence(seconds: float, sr: int) -> np.ndarray:
    n = int(max(0.0, seconds) * sr)
    return np.zeros((n,), dtype=np.float32)


def main() -> int:
    # Sensible defaults for Apple Silicon.
    os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")

    model_id = os.environ.get("QWEN_TTS_MODEL", "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice")
    speaker = os.environ.get("QWEN_TTS_SPEAKER", "Ryan")
    language = os.environ.get("QWEN_TTS_LANG", "English")
    device = os.environ.get(
        "QWEN_TTS_DEVICE", "mps" if torch.backends.mps.is_available() else "cpu"
    )
    dtype_str = os.environ.get("QWEN_TTS_DTYPE", "bfloat16")
    max_new_tokens = int(os.environ.get("QWEN_TTS_MAX_NEW_TOKENS", "384"))

    # Try to keep the model from drifting into other languages.
    instruct = os.environ.get(
        "QWEN_TTS_INSTRUCT",
        "Speak in clear English only. Do not switch languages.",
    )
    do_sample = os.environ.get("QWEN_TTS_DO_SAMPLE", "0").strip().lower() not in {
        "0",
        "false",
        "no",
    }
    repetition_penalty = float(os.environ.get("QWEN_TTS_REPETITION_PENALTY", "1.05"))
    temperature = float(os.environ.get("QWEN_TTS_TEMPERATURE", "0.7"))
    top_p = float(os.environ.get("QWEN_TTS_TOP_P", "0.9"))

    target_seconds = float(
        os.environ.get("QWEN_TTS_TARGET_SECONDS", "150")
    )  # ~2.5 minutes
    gap_seconds = float(os.environ.get("QWEN_TTS_GAP_SECONDS", "0.25"))

    dtype_map = {
        "float16": torch.float16,
        "bfloat16": torch.bfloat16,
        "float32": torch.float32,
    }
    if dtype_str not in dtype_map:
        raise SystemExit(
            f"Unsupported QWEN_TTS_DTYPE={dtype_str!r}; use one of {list(dtype_map)}"
        )

    out_dir = Path(__file__).resolve().parent / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "long_custom_voice.wav"

    # Topic: short mini-lecture with clear segmentation.
    segments = [
        "Today I want to share a simple way to build better habits, without relying on willpower.",
        "The key idea is to design your environment so the right action becomes the easy action.",
        "Start by picking one habit that takes less than two minutes. Something tiny, like opening a notebook, or drinking a glass of water.",
        "When a habit is small, you lower the friction. And friction is what usually decides whether you follow through.",
        "Next, attach that habit to something you already do. For example: after you make coffee, you write one sentence. After you brush your teeth, you stretch for thirty seconds.",
        "This is called an anchor. Anchors turn vague intentions into a concrete moment in your day.",
        "Now make it obvious. Put the notebook on your keyboard. Put the water bottle on the counter. Remove the step where you have to remember.",
        "And make it satisfying. Give yourself a tiny win at the end. Check a box. Move a bead on a string. Mark a streak on a calendar.",
        "Your brain learns from consequences, not from plans. If it feels good, even in a small way, you are more likely to repeat it.",
        "A quick note about motivation: it comes after action more often than before. If you wait to feel ready, you might wait forever.",
        "So focus on showing up. Your only job is to be the kind of person who starts.",
        'If you miss a day, don"t make it a story about who you are. Make it a data point. Get back to it on the next anchor.',
        'Over time, small habits compound. They don"t just change what you do. They change what you believe about yourself.',
        "And that's the real payoff: a reliable system that keeps working on the days when your energy is low.",
        "To wrap up: choose a two-minute habit, attach it to an anchor, make it obvious, make it satisfying, and repeat.",
        "Do that for two weeks, and you'll have something stronger than motivation: you'll have momentum.",
    ]

    print(
        f"torch={torch.__version__} mps_available={torch.backends.mps.is_available()}"
    )
    print(f"model={model_id}")
    print(f"device={device} dtype={dtype_str} speaker={speaker} lang={language}")
    print(f"target_seconds={target_seconds} max_new_tokens={max_new_tokens}")
    print(
        f"gen: do_sample={do_sample} top_p={top_p} temperature={temperature} repetition_penalty={repetition_penalty}"
    )
    print(f"instruct={instruct!r}")

    t0 = time.perf_counter()
    model = Qwen3TTSModel.from_pretrained(
        model_id,
        device_map=device,
        dtype=dtype_map[dtype_str],
    )
    print(f"loaded model in {time.perf_counter() - t0:.1f}s")

    wav_parts: list[np.ndarray] = []
    sr_out: int = -1
    total_samples = 0

    for i, text in enumerate(segments, start=1):
        if sr_out > 0 and (total_samples / sr_out) >= target_seconds:
            break

        t_seg = time.perf_counter()
        wavs, sr = model.generate_custom_voice(
            text=text,
            language=language,
            speaker=speaker,
            instruct=instruct,
            max_new_tokens=max_new_tokens,
            do_sample=do_sample,
            top_p=top_p,
            temperature=temperature,
            repetition_penalty=repetition_penalty,
        )
        wav = wavs[0]

        if sr_out <= 0:
            sr_out = int(sr)
        elif int(sr) != sr_out:
            raise RuntimeError(f"Sample rate changed unexpectedly: {sr_out} -> {sr}")

        # Ensure float32 for concatenation.
        wav = np.asarray(wav, dtype=np.float32)

        # Append a short pause so it sounds like paragraphs.
        wav_parts.append(wav)
        wav_parts.append(_silence(gap_seconds, sr_out))

        total_samples += len(wav)
        dur = total_samples / sr_out
        print(
            f"[{i:02d}/{len(segments)}] +{len(wav) / sr_out:.1f}s (segment in {time.perf_counter() - t_seg:.1f}s) -> total {dur:.1f}s"
        )

    if not wav_parts or sr_out <= 0:
        raise RuntimeError("No audio generated")

    final = np.concatenate(wav_parts, axis=0)

    # Write as 16-bit PCM WAV for max compatibility.
    sf.write(out_path, final, sr_out, subtype="PCM_16")
    print(f"wrote: {out_path} (duration={len(final) / sr_out:.1f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
