import argparse
import json
import os
import threading
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional


SUPPRESSED_STDERR_SUBSTRINGS = (
    "Warning: flash-attn is not installed.",
    "Will only run the manual PyTorch version.",
    "Please install flash-attn for faster inference.",
)


def should_forward_worker_stderr(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if any(token in stripped for token in SUPPRESSED_STDERR_SUBSTRINGS):
        return False
    # qwen_tts wraps this warning in lines of asterisks; hide those wrappers too.
    if set(stripped) == {"*"}:
        return False
    return True


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


def _hf_repo_id_to_cache_dirname(model_id: str) -> Optional[str]:
    if "/" not in model_id:
        return None
    org, repo = model_id.split("/", 1)
    if not org or not repo:
        return None
    return f"models--{org}--{repo}"


def find_hf_snapshot_dir(model_id: str) -> Optional[Path]:
    dirname = _hf_repo_id_to_cache_dirname(model_id)
    if not dirname:
        return None

    hf_home = Path(
        os.environ.get("HF_HOME", str(Path.home() / ".cache" / "huggingface"))
    )
    hub_dir = hf_home / "hub"
    model_dir = hub_dir / dirname
    snapshots_dir = model_dir / "snapshots"
    if not snapshots_dir.exists():
        return None

    ref_main = model_dir / "refs" / "main"
    if ref_main.exists():
        commit = ref_main.read_text(encoding="utf-8").strip()
        if commit:
            cand = snapshots_dir / commit
            if cand.exists():
                return cand

    snapshots = [p for p in snapshots_dir.iterdir() if p.is_dir()]
    if not snapshots:
        return None
    snapshots.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return snapshots[0]


def ensure_ref_text(ref_text_path: Path) -> str:
    if not ref_text_path.exists():
        raise FileNotFoundError(f"Missing ref text: {ref_text_path}")
    return ref_text_path.read_text(encoding="utf-8").strip()


def selected_tts_backend() -> str:
    value = os.environ.get("FLAMING_HORSE_TTS_BACKEND", "qwen").strip().lower()
    if value not in {"qwen", "mlx"}:
        raise ValueError(
            f"Invalid FLAMING_HORSE_TTS_BACKEND={value!r}. Expected 'qwen' or 'mlx'."
        )
    return value


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


def bootstrap_existing_entries_from_media(
    cache_dir: Path,
    script: dict,
    model_id: str,
    ref_audio: str,
    ref_text: str,
) -> dict:
    """Build synthetic cache entries from already-rendered mp3 files.

    This lets interrupted runs resume instead of regenerating every narration key
    when cache.json is missing.
    """
    by_key = {}
    now = time.time()
    for narration_key, text in script.items():
        audio_file = f"{narration_key}.mp3"
        if not (cache_dir / audio_file).exists():
            continue
        by_key[narration_key] = build_cache_entry(
            narration_key=narration_key,
            text=text,
            audio_file=audio_file,
            model_id=model_id,
            ref_audio=ref_audio,
            ref_text=ref_text,
            duration=0.0,
            created_at=now,
        )
    return by_key


def _stream_lines(
    stream,
    sink: list[str],
    writer,
    line_filter=None,
) -> None:
    for line in iter(stream.readline, ""):
        sink.append(line)
        if writer is None:
            continue
        if line_filter is not None and not line_filter(line):
            continue
        writer.write(line)
        writer.flush()


def main() -> int:
    args = parse_args()
    project_dir = Path(args.project_dir).resolve()

    cfg = load_config(project_dir)
    script = load_script(project_dir)

    backend = selected_tts_backend()
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

    if backend == "qwen" and (device != "cpu" or dtype_str != "float32"):
        raise ValueError(
            "This repo requires CPU float32 for Qwen voice clone. "
            f"Found device={device!r} dtype={dtype_str!r} in voice_clone_config.json"
        )

    model_source = str(model_id)
    if backend == "qwen":
        model_source = None
        if isinstance(model_id, str) and Path(model_id).exists():
            model_source = str(Path(model_id).resolve())
        elif isinstance(model_id, str):
            snap = find_hf_snapshot_dir(model_id)
            if snap is not None:
                model_source = str(snap)

        if not model_source:
            hf_home = Path(
                os.environ.get("HF_HOME", str(Path.home() / ".cache" / "huggingface"))
            )
            expected = _hf_repo_id_to_cache_dirname(str(model_id))
            expected_path = (
                (hf_home / "hub" / expected) if expected else (hf_home / "hub")
            )
            print(
                "ERROR: Qwen model snapshot not found in local HuggingFace cache.",
                file=sys.stderr,
            )
            print(f"  Model id: {model_id}", file=sys.stderr)
            print(f"  Looked under: {expected_path}", file=sys.stderr)
            print(
                "  Fix: run your model download/setup step outside the build, then retry.",
                file=sys.stderr,
            )
            raise SystemExit(2)

    ref_audio_path = (project_dir / ref_audio).resolve()
    ref_text = ensure_ref_text((project_dir / ref_text_path).resolve())

    cache_dir = (project_dir / output_dir).resolve()
    cache_dir.mkdir(parents=True, exist_ok=True)

    cache_index_path = cache_dir / "cache.json"
    existing_entries = []
    if cache_index_path.exists():
        existing_entries = json.loads(cache_index_path.read_text(encoding="utf-8"))

    existing_by_key = {e.get("narration_key"): e for e in existing_entries}
    if not existing_by_key:
        # Resume support: if prior run produced some mp3 files but never wrote
        # cache.json, infer minimal entries so those keys are treated as hits.
        existing_by_key = bootstrap_existing_entries_from_media(
            cache_dir=cache_dir,
            script=script,
            model_id=str(model_id),
            ref_audio=str(ref_audio_path),
            ref_text=ref_text,
        )
        if existing_by_key:
            print(
                f"→ Recovered {len(existing_by_key)} existing audio files from {cache_dir}",
                file=sys.stderr,
            )
    # If cache contains wav entries from older runs, regenerate.
    if any((e or {}).get("audio_file", "").endswith(".wav") for e in existing_entries):
        existing_by_key = {}

    payload = {
        "model_id": model_id,
        "model_source": model_source,
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
    env = os.environ.copy()
    env.setdefault("HF_HUB_OFFLINE", "1")
    env.setdefault("TRANSFORMERS_OFFLINE", "1")
    env.setdefault("TOKENIZERS_PARALLELISM", "false")
    env["PYTHONUNBUFFERED"] = "1"

    proc = subprocess.Popen(
        [os.path.expanduser(python_path), str(helper)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    assert proc.stdin is not None
    assert proc.stdout is not None
    assert proc.stderr is not None

    proc.stdin.write(json.dumps(payload))
    proc.stdin.close()

    stdout_lines: list[str] = []
    stderr_lines: list[str] = []
    t_out = threading.Thread(
        target=_stream_lines,
        args=(proc.stdout, stdout_lines, sys.stdout, should_forward_worker_stderr),
        daemon=True,
    )
    t_err = threading.Thread(
        target=_stream_lines,
        args=(proc.stderr, stderr_lines, sys.stderr, should_forward_worker_stderr),
        daemon=True,
    )
    t_out.start()
    t_err.start()

    returncode = proc.wait()
    t_out.join()
    t_err.join()

    worker_stdout = "".join(stdout_lines)
    worker_stderr = "".join(stderr_lines)

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
    
    # Save hash of narration script to track changes
    import hashlib
    narration_file = project_dir / "narration_script.py"
    if narration_file.exists():
        narration_hash = hashlib.sha256(
            narration_file.read_text(encoding='utf-8').encode('utf-8')
        ).hexdigest()
        hash_file = cache_dir / ".cache_hash"
        hash_file.write_text(narration_hash, encoding='utf-8')
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
