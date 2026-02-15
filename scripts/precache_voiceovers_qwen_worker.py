import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf

from qwen_tts_mediator import build_voice_clone_prompt, generate_voice_clone, load_model


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

    output_dir.mkdir(parents=True, exist_ok=True)

    print("→ Loading Qwen model", file=sys.stderr)
    t0 = time.perf_counter()
    model = load_model(str(model_source), str(device), str(dtype_str))
    print(f"✓ Loaded model in {time.perf_counter() - t0:.1f}s", file=sys.stderr)

    print("→ Building voice clone prompt", file=sys.stderr)
    t1 = time.perf_counter()
    voice_clone_prompt = build_voice_clone_prompt(
        model,
        ref_audio=str(ref_audio),
        ref_text=ref_text,
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
        wavs, sr = generate_voice_clone(
            model,
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
