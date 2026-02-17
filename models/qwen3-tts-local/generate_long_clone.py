import os
import time
from pathlib import Path

import numpy as np
import json
import subprocess
import soundfile as sf


def _silence(seconds: float, sr: int) -> np.ndarray:
    n = int(max(0.0, seconds) * sr)
    return np.zeros((n,), dtype=np.float32)


def main() -> int:
# MLX service path
MLX_PYTHON = "/Users/velocityworks/IdeaProjects/flaming-horse/models/qwen3-tts-local/mlx_env/bin/python"
SERVICE_SCRIPT = "mlx_tts_service.py"
MODEL_ID = os.environ.get("MLX_MODEL", "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit")

ref_audio = os.environ.get(
    "QWEN_TTS_REF_AUDIO",
    str(Path(__file__).resolve().parent / "ref" / "ref_voice_elevenlabs.wav"),
)
ref_text = os.environ.get("QWEN_TTS_REF_TEXT", "")

language = os.environ.get("QWEN_TTS_LANG", "English")
target_seconds = float(os.environ.get("QWEN_TTS_TARGET_SECONDS", "180"))
gap_seconds = float(os.environ.get("QWEN_TTS_GAP_SECONDS", "0.25"))

if not ref_text.strip():
    raise SystemExit(
        "QWEN_TTS_REF_TEXT is required for voice clone. "
        "Set it to the transcript of the reference audio."
    )

out_dir = Path(__file__).resolve().parent / "outputs"
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / "long_voice_clone.wav"

segments = [
    "In this short talk, we will build a calm, practical plan for learning any new skill.",
    "First, choose one skill and define it in a single sentence. Clarity reduces hesitation.",
    "Second, break the skill into three layers: input, practice, and feedback.",
    "Input means reading, watching, or listening to excellent examples.",
    "Practice means doing small, deliberate reps that feel slightly uncomfortable.",
    "Feedback means checking your work against a clear standard and adjusting.",
    "Now, pick a daily minimum. Ten minutes is enough, as long as it is consistent.",
    "Schedule those ten minutes at a reliable time so you don’t have to decide each day.",
    "If you miss a day, do not reset. Simply continue with the next session.",
    "This creates a system that is resilient, rather than one that breaks under pressure.",
    "As you improve, raise the difficulty one small step at a time.",
    "Keep a simple log of what you practiced and what you learned. That log becomes a map.",
    "Once a week, review the map and choose one specific thing to refine next.",
    "This prevents random effort and focuses your energy on the highest leverage moves.",
    "Finally, celebrate progress, not perfection. A steady rhythm beats a dramatic sprint.",
    "Over a few months, that rhythm compounds into real mastery, and it feels surprisingly natural.",
    "If you want, you can now pause this audio and write your three layers on paper.",
    "When you are ready, start with ten minutes today. That is enough to begin.",
]

print(f"Using MLX model={MODEL_ID}")
print(f"ref_audio={ref_audio}")
print(f"target_seconds={target_seconds}")

t0 = time.perf_counter()
# Build segments list for service
segments_list = [{"id": f"seg{i}", "text": text} for i, text in enumerate(segments, 1)]
segments_json = json.dumps(segments_list)

t_gen_total = time.perf_counter()
# Call MLX service via subprocess
cmd = [MLX_PYTHON, SERVICE_SCRIPT, segments_json, MODEL_ID]
result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
if result.returncode != 0:
    raise RuntimeError(f"MLX service failed: {result.stderr}")
paths_data = json.loads(result.stdout.strip())

wav_parts: list[np.ndarray] = []
sr_out = 24000  # Assume 24kHz from MLX
total_samples = 0

for data in paths_data:
    if total_samples / sr_out >= target_seconds:
        break
    wav_path = Path(data["path"])
    wav, sr = sf.read(wav_path)
    if sr != sr_out:
        raise RuntimeError(f"Sample rate mismatch: {sr} vs {sr_out}")
    wav = np.asarray(wav, dtype=np.float32)
    wav_parts.append(wav)
    wav_parts.append(_silence(gap_seconds, sr_out))
    total_samples += len(wav)
    dur = total_samples / sr_out
    print(f"[{data['id']}] +{len(wav) / sr_out:.1f}s (from_cache={data['from_cache']}) -> total {dur:.1f}s")

if not wav_parts:
    raise RuntimeError("No audio generated")

final = np.concatenate(wav_parts, axis=0)
sf.write(out_path, final, sr_out, subtype="PCM_16")
print(f"wrote: {out_path} (duration={len(final) / sr_out:.1f}s)")
print(f"total generation wall time: {time.perf_counter() - t_gen_total:.1f}s")
return 0


if __name__ == "__main__":
    raise SystemExit(main())
