import argparse
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path


# Voice generation constants
WORDS_PER_SECOND = 2.5  # ~150 words per minute reading speed
MIN_DURATION_SECONDS = 0.5  # Minimum audio duration


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Precache Qwen3 voiceovers")
    parser.add_argument("project_dir", help="Project directory path")
    return parser.parse_args()


def load_script(project_dir: Path) -> dict:
    script_path = project_dir / "narration_script.py"
    if not script_path.exists():
        raise FileNotFoundError(f"Missing narration_script.py in {project_dir}")

    data = {}
    exec(script_path.read_text(encoding="utf-8"), data)
    script = data.get("SCRIPT")
    if not isinstance(script, dict):
        raise ValueError("SCRIPT not found or invalid in narration_script.py")
    return script


def load_config(project_dir: Path) -> dict:
    config_path = project_dir / "voice_clone_config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"Missing voice_clone_config.json in {project_dir}")
    return json.loads(config_path.read_text(encoding="utf-8"))


def ensure_ref_text(ref_text_path: Path) -> str:
    if not ref_text_path.exists():
        raise FileNotFoundError(f"Missing ref text: {ref_text_path}")
    return ref_text_path.read_text(encoding="utf-8").strip()


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


def check_qwen_env_available(python_path_str: str) -> bool:
    """Check if Qwen Python environment exists and is accessible."""
    if not python_path_str:
        return False
    
    python_path = Path(os.path.expanduser(python_path_str))
    if not python_path.exists():
        return False
    
    # Check if the Python can import qwen_tts
    try:
        result = subprocess.run(
            [str(python_path), "-c", "import qwen_tts"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def generate_mock_cache(
    script: dict,
    output_dir: Path,
    model_id: str,
    ref_audio: str,
    ref_text: str,
) -> list:
    """Generate mock cache entries with silent audio files."""
    import struct
    import wave
    
    print("→ Generating mock cache entries (Qwen environment unavailable)")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if ffmpeg is available
    ffmpeg_available = False
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            timeout=2,
        )
        ffmpeg_available = result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    entries = []
    for narration_key, text in script.items():
        # Calculate duration based on word count
        word_count = len(text.split())
        duration = max(MIN_DURATION_SECONDS, word_count / WORDS_PER_SECOND)
        
        # First create a WAV file using Python's wave module
        sample_rate = 24000
        num_samples = int(sample_rate * duration)
        wav_path = output_dir / f"{narration_key}.wav"
        
        try:
            with wave.open(str(wav_path), 'w') as wav_file:
                wav_file.setnchannels(1)  # mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                # Write silent samples
                for _ in range(num_samples):
                    wav_file.writeframes(struct.pack('<h', 0))
        except Exception as e:
            print(f"⚠ Warning: Failed to create WAV for {narration_key}: {e}")
            continue
        
        # Try to convert to MP3 if ffmpeg is available
        if ffmpeg_available:
            audio_file = f"{narration_key}.mp3"
            mp3_path = output_dir / audio_file
            try:
                subprocess.run(
                    [
                        "ffmpeg",
                        "-i", str(wav_path),
                        "-ac", "1",
                        "-ar", "24000",
                        "-b:a", "192k",
                        "-y",
                        str(mp3_path),
                    ],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                # Remove WAV file after successful conversion
                wav_path.unlink()
                print(f"✓ Generated mock audio: {narration_key} ({duration:.2f}s)")
            except subprocess.CalledProcessError as e:
                print(f"⚠ Warning: Failed to convert to MP3 for {narration_key}, using WAV")
                audio_file = f"{narration_key}.wav"
        else:
            # Use WAV file directly
            audio_file = f"{narration_key}.wav"
            print(f"✓ Generated mock audio (WAV): {narration_key} ({duration:.2f}s)")
        
        entry = build_cache_entry(
            narration_key,
            text,
            audio_file,
            model_id,
            ref_audio,
            ref_text,
            duration,
            time.time(),
        )
        entries.append(entry)
    
    return entries


def main() -> int:
    args = parse_args()
    project_dir = Path(args.project_dir).resolve()

    cfg = load_config(project_dir)
    script = load_script(project_dir)

    model_id = cfg.get("model_id", "Qwen/Qwen3-TTS-12Hz-1.7B-Base")
    device = cfg.get("device", "cpu")
    dtype_str = cfg.get("dtype", "float32")
    python_path = cfg.get("qwen_python")
    ref_audio = cfg.get("ref_audio")
    ref_text_path = cfg.get("ref_text")
    output_dir = cfg.get("output_dir", "media/voiceovers/qwen")

    if not python_path:
        print("⚠ Warning: voice_clone_config.json missing qwen_python, using mock mode")
        use_mock = True
    elif not check_qwen_env_available(python_path):
        print(f"⚠ Warning: Qwen Python environment unavailable at {python_path}")
        print("→ Falling back to mock mode (silent audio)")
        use_mock = True
    else:
        use_mock = False

    if not ref_audio or not ref_text_path:
        raise ValueError(
            "ref_audio and ref_text must be set in voice_clone_config.json"
        )

    ref_audio_path = (project_dir / ref_audio).resolve()
    ref_text = ensure_ref_text((project_dir / ref_text_path).resolve())

    cache_dir = (project_dir / output_dir).resolve()
    cache_dir.mkdir(parents=True, exist_ok=True)

    cache_index_path = cache_dir / "cache.json"
    
    # If using mock mode, generate mock cache and exit
    if use_mock:
        updated_entries = generate_mock_cache(
            script,
            cache_dir,
            model_id,
            str(ref_audio_path),
            ref_text,
        )
        cache_index_path.write_text(
            json.dumps(updated_entries, indent=2),
            encoding="utf-8",
        )
        print(f"✓ Updated cache index (mock): {cache_index_path}")
        print("ℹ️  Videos will use silent audio. To use real Qwen voice:")
        print(f"   1. Set up Qwen environment at: {python_path}")
        print(f"   2. Re-run: python3 scripts/precache_voiceovers_qwen.py {project_dir}")
        return 0
    
    # Real Qwen mode - proceed with worker
    existing_entries = []
    if cache_index_path.exists():
        existing_entries = json.loads(cache_index_path.read_text(encoding="utf-8"))

    existing_by_key = {e.get("narration_key"): e for e in existing_entries}
    # If cache contains wav entries from older runs, regenerate.
    if any((e or {}).get("audio_file", "").endswith(".wav") for e in existing_entries):
        existing_by_key = {}

    payload = {
        "model_id": model_id,
        "device": device,
        "dtype": dtype_str,
        "language": cfg.get("language", "English"),
        "ref_audio": str(ref_audio_path),
        "ref_text": ref_text,
        "output_dir": str(cache_dir),
        "script": script,
        "existing": existing_by_key,
    }

    helper = (Path(__file__).parent / "precache_voiceovers_qwen_worker.py").resolve()
    if not helper.exists():
        raise FileNotFoundError(f"Missing worker script: {helper}")

    # Stream worker progress (stderr) live so the pipeline doesn't look hung.
    proc = subprocess.Popen(
        [os.path.expanduser(python_path), str(helper)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert proc.stdin is not None
    assert proc.stdout is not None
    assert proc.stderr is not None

    worker_stdout_stream = proc.stdout
    proc.stdin.write(json.dumps(payload))
    proc.stdin.close()

    stdout_chunks: list[str] = []
    stderr_chunks: list[str] = []

    def _read_stdout() -> None:
        stdout_chunks.append(worker_stdout_stream.read())

    def _read_stderr() -> None:
        stderr_chunks.append(proc.stderr.read())

    t_stdout = threading.Thread(target=_read_stdout, daemon=True)
    t_stderr = threading.Thread(target=_read_stderr, daemon=True)

    t_stdout.start()
    t_stderr.start()

    returncode = proc.wait()

    t_stdout.join(timeout=5)
    t_stderr.join(timeout=5)

    worker_stdout = "".join(stdout_chunks)
    worker_stderr = "".join(stderr_chunks)

    if returncode != 0:
        if worker_stdout.strip():
            print(worker_stdout)
        if worker_stderr.strip():
            print(worker_stderr, file=sys.stderr)
        raise SystemExit(returncode)

    if not worker_stdout.strip():
        if worker_stderr.strip():
            print(worker_stderr, file=sys.stderr)
        raise SystemExit("Qwen precache worker returned empty output")

    # If worker logged to stdout, JSON may be on the last line.
    stdout_lines = [line for line in worker_stdout.splitlines() if line.strip()]
    json_text = stdout_lines[-1]
    try:
        updated_entries = json.loads(json_text)
    except json.JSONDecodeError:
        # Fall back to full stdout for debugging
        print(worker_stdout)
        raise

    cache_index_path.write_text(
        json.dumps(updated_entries, indent=2),
        encoding="utf-8",
    )
    print(f"✓ Updated cache index: {cache_index_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
