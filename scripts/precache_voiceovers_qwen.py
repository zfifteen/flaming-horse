import argparse
import json
import os
import subprocess
import sys
import threading
from pathlib import Path


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


def _generate_silent_mp3(path: Path, duration: float = 3.0) -> None:
    """Generate a silent MP3 file using ffmpeg."""
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"anullsrc=r=24000:cl=mono",
            "-t", str(duration),
            "-codec:a", "libmp3lame",
            "-b:a", "192k",
            str(path),
        ],
        check=True,
        capture_output=True,
    )


def _mock_precache(project_dir: Path) -> int:
    """Generate silent audio files and cache.json for mock mode."""
    cfg = load_config(project_dir)
    script = load_script(project_dir)
    output_dir_rel = cfg.get("output_dir", "media/voiceovers/qwen")
    cache_dir = (project_dir / output_dir_rel).resolve()
    cache_dir.mkdir(parents=True, exist_ok=True)

    import time

    entries = []
    for key, text in script.items():
        audio_file = f"{key}.mp3"
        audio_path = cache_dir / audio_file
        if not audio_path.exists():
            # Estimate ~1 second per 2.5 words of narration, minimum 2s
            word_count = len(text.split())
            duration = max(2.0, word_count / 2.5)
            print(f"  → Generating silent audio: {audio_file} ({duration:.1f}s)")
            _generate_silent_mp3(audio_path, duration)
        else:
            print(f"  ✓ Cache hit: {audio_file}")
            duration = 3.0  # default

        entries.append({
            "narration_key": key,
            "text": text,
            "audio_file": audio_file,
            "model_id": "mock",
            "ref_audio": "mock",
            "ref_text": "mock",
            "duration_seconds": duration,
            "created_at": time.time(),
        })

    cache_index = cache_dir / "cache.json"
    cache_index.write_text(json.dumps(entries, indent=2), encoding="utf-8")
    print(f"✓ Mock cache index: {cache_index} ({len(entries)} entries)")
    return 0


def main() -> int:
    args = parse_args()
    project_dir = Path(args.project_dir).resolve()

    # Mock mode: generate silent audio files instead of calling Qwen
    if os.environ.get("MOCK_QWEN") == "1":
        return _mock_precache(project_dir)

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
        raise ValueError("voice_clone_config.json must define qwen_python")

    if not ref_audio or not ref_text_path:
        raise ValueError(
            "ref_audio and ref_text must be set in voice_clone_config.json"
        )

    ref_audio_path = (project_dir / ref_audio).resolve()
    ref_text = ensure_ref_text((project_dir / ref_text_path).resolve())

    cache_dir = (project_dir / output_dir).resolve()
    cache_dir.mkdir(parents=True, exist_ok=True)

    cache_index_path = cache_dir / "cache.json"
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
