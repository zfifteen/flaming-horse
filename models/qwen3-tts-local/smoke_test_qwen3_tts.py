import os
from pathlib import Path
import time

# Reduce surprise disk usage
os.environ.setdefault("HF_HOME", str(Path.home() / ".cache" / "huggingface"))
os.environ.setdefault("HF_HUB_ENABLE_HF_TRANSFER", "1")

# Useful for Apple Silicon ops that may be unsupported on MPS
os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")

import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel

OUT_DIR = Path(__file__).resolve().parent / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_ID = os.environ.get("QWEN_TTS_MODEL", "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice")
SPEAKER = os.environ.get("QWEN_TTS_SPEAKER", "Ryan")
LANG = os.environ.get("QWEN_TTS_LANG", "English")
TEXT = os.environ.get(
    "QWEN_TTS_TEXT",
    "This is a local Qwen3 TTS smoke test running on an Apple Silicon Mac.",
)
INSTRUCT = os.environ.get("QWEN_TTS_INSTRUCT", "")

# Optional generation knobs (useful for making larger models finish faster)
MAX_NEW_TOKENS = int(os.environ.get("QWEN_TTS_MAX_NEW_TOKENS", "512"))
TOP_P = float(os.environ.get("QWEN_TTS_TOP_P", "0.95"))
TEMPERATURE = float(os.environ.get("QWEN_TTS_TEMPERATURE", "0.8"))
DO_SAMPLE = os.environ.get("QWEN_TTS_DO_SAMPLE", "1").strip().lower() not in {
    "0",
    "false",
    "no",
}
REPETITION_PENALTY = float(os.environ.get("QWEN_TTS_REPETITION_PENALTY", "1.05"))

# On Mac, prefer MPS if available
DEVICE = os.environ.get(
    "QWEN_TTS_DEVICE", "mps" if torch.backends.mps.is_available() else "cpu"
)
DTYPE = os.environ.get("QWEN_TTS_DTYPE", "float16")

dtype_map = {
    "float16": torch.float16,
    "bfloat16": torch.bfloat16,
    "float32": torch.float32,
}
if DTYPE not in dtype_map:
    raise SystemExit(
        f"Unsupported QWEN_TTS_DTYPE={DTYPE!r}; use one of {list(dtype_map)}"
    )

print(f"torch={torch.__version__} mps_available={torch.backends.mps.is_available()}")
print(f"model={MODEL_ID}")
print(f"device={DEVICE} dtype={DTYPE} speaker={SPEAKER} lang={LANG}")
print(
    f"gen: max_new_tokens={MAX_NEW_TOKENS} do_sample={DO_SAMPLE} top_p={TOP_P} temperature={TEMPERATURE} repetition_penalty={REPETITION_PENALTY}"
)
if INSTRUCT:
    print(f"instruct={INSTRUCT!r}")

t0 = time.perf_counter()
model = Qwen3TTSModel.from_pretrained(
    MODEL_ID,
    device_map=DEVICE,
    dtype=dtype_map[DTYPE],
)
t1 = time.perf_counter()
print(f"loaded model in {t1 - t0:.1f}s")

t2 = time.perf_counter()
wavs, sr = model.generate_custom_voice(
    text=TEXT,
    language=LANG,
    speaker=SPEAKER,
    instruct=(INSTRUCT if INSTRUCT else None),
    max_new_tokens=MAX_NEW_TOKENS,
    do_sample=DO_SAMPLE,
    top_p=TOP_P,
    temperature=TEMPERATURE,
    repetition_penalty=REPETITION_PENALTY,
)
t3 = time.perf_counter()
print(f"generated audio in {t3 - t2:.1f}s")

out = OUT_DIR / "custom_voice.wav"
sf.write(out, wavs[0], sr)
print(f"wrote: {out} (sr={sr}, samples={len(wavs[0])})")
