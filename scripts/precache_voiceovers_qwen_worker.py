import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
from qwen_tts import Qwen3TTSModel


def build_cache_entry(
    narration_key: str,
    text: str,
    audio_file: str,
    model_id: str,
    ref_audio: str,
    ref_text: str,
    duration: float,
    created_at: float,
) -> dict:
    return {
        "narration_key": narration_key,
        "text": text,
        "audio_file": audio_file,
        "model_id": model_id,
        "ref_audio": ref_audio,
        "ref_text": ref_text,
        "duration_seconds": duration,
        "created_at": created_at,
    }


def main() -> int:
    payload = json.loads(sys.stdin.read())

    model_id = payload["model_id"]
    model_source = payload.get("model_source") or model_id
    device = payload["device"]
    dtype_str = payload["dtype"]
    language = payload["language"]
    ref_audio = payload["ref_audio"]
    ref_text = payload["ref_text"]
    output_dir = Path(payload["output_dir"]).resolve()
    script = payload["script"]
    existing_by_key = payload["existing"]

    dtype_map = {
        "float16": torch.float16,
        "bfloat16": torch.bfloat16,
        "float32": torch.float32,
    }
    if dtype_str not in dtype_map:
        raise ValueError(f"Unsupported dtype: {dtype_str}")

    output_dir.mkdir(parents=True, exist_ok=True)

    print("→ Loading Qwen model", file=sys.stderr)
    t0 = time.perf_counter()
    model = Qwen3TTSModel.from_pretrained(
        str(model_source),
        device_map=device,
        dtype=dtype_map[dtype_str],
    )
    print(f"✓ Loaded model in {time.perf_counter() - t0:.1f}s", file=sys.stderr)

    print("→ Building voice clone prompt", file=sys.stderr)
    t1 = time.perf_counter()
    voice_clone_prompt = model.create_voice_clone_prompt(
        ref_audio=str(ref_audio),
        ref_text=ref_text,
        x_vector_only_mode=False,
    )
    print(f"✓ Prompt built in {time.perf_counter() - t1:.1f}s", file=sys.stderr)

    updated_entries = []
    for narration_key, text in script.items():
        existing = existing_by_key.get(narration_key)
        if existing:
            audio_file = existing.get("audio_file", "")
            if existing.get("text") == text and (output_dir / audio_file).exists():
                updated_entries.append(existing)
                print(f"✓ Cache hit: {narration_key}", file=sys.stderr)
                continue

        t_seg = time.perf_counter()
        wavs, sr = model.generate_voice_clone(
            text=text,
            language=language,
            voice_clone_prompt=voice_clone_prompt,
        )
        wav = np.asarray(wavs[0], dtype=np.float32)
        wav_path = output_dir / f"{narration_key}.wav"
        audio_file = f"{narration_key}.mp3"
        mp3_path = output_dir / audio_file
        sf.write(wav_path, wav, sr, subtype="PCM_16")
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(wav_path),
                "-ac",
                "1",
                "-ar",
                "24000",
                "-b:a",
                "192k",
                str(mp3_path),
            ],
            check=True,
            capture_output=True,
        )
        try:
            wav_path.unlink()
        except OSError:
            pass
        duration = float(len(wav) / sr)
        entry = build_cache_entry(
            narration_key,
            text,
            audio_file,
            model_id,
            str(ref_audio),
            ref_text,
            duration,
            time.time(),
        )
        updated_entries.append(entry)
        print(
            f"✓ Generated {narration_key} ({duration:.2f}s) in {time.perf_counter() - t_seg:.1f}s",
            file=sys.stderr,
        )

    print(json.dumps(updated_entries))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
