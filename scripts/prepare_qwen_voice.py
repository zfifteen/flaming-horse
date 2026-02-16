#!/usr/bin/env python3
"""Prepare (warm up) the local Qwen voice clone stack for a project.

This is a reliability step: it fails fast if the Qwen environment, model weights,
or reference assets are missing, before the main build pipeline runs.

It runs the expensive first-load steps (model load + prompt build).

Stamp file:
  <project>/<output_dir>/ready.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from subprocess import PIPE, Popen
from typing import Any

from voice_ref_mediator import resolve_voice_ref


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


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def selected_tts_backend() -> str:
    value = os.environ.get("FLAMING_HORSE_TTS_BACKEND", "qwen").strip().lower()
    if value not in {"qwen", "mlx"}:
        raise ValueError(
            f"Invalid FLAMING_HORSE_TTS_BACKEND={value!r}. Expected 'qwen' or 'mlx'."
        )
    return value


def selected_mlx_model_id(default_model_id: str) -> str:
    override = os.environ.get("FLAMING_HORSE_MLX_MODEL_ID", "").strip()
    if override:
        return override
    if default_model_id.startswith("mlx-community/"):
        return default_model_id
    return "mlx-community/Qwen3-TTS-12Hz-0.6B-Base-4bit"


def _hf_repo_id_to_cache_dirname(model_id: str) -> str | None:
    # HuggingFace hub cache layout:
    #   <HF_HOME>/hub/models--ORG--REPO
    if "/" not in model_id:
        return None
    org, repo = model_id.split("/", 1)
    if not org or not repo:
        return None
    return f"models--{org}--{repo}"


def find_hf_snapshot_dir(model_id: str) -> Path | None:
    """Find a local HF hub snapshot directory for a repo id.

    Returns a path like:
      ~/.cache/huggingface/hub/models--ORG--REPO/snapshots/<sha>
    """

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

    # Prefer the commit pointed to by refs/main (if present).
    ref_main = model_dir / "refs" / "main"
    if ref_main.exists():
        commit = ref_main.read_text(encoding="utf-8").strip()
        if commit:
            cand = snapshots_dir / commit
            if cand.exists():
                return cand

    # Otherwise, pick most recently modified snapshot.
    snapshots = [p for p in snapshots_dir.iterdir() if p.is_dir()]
    if not snapshots:
        return None
    snapshots.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return snapshots[0]


def compute_fingerprint(cfg: dict[str, Any], ref_audio: Path, ref_text: Path) -> str:
    payload = {
        "model_id": cfg.get("model_id", "Qwen/Qwen3-TTS-12Hz-1.7B-Base"),
        "device": cfg.get("device", "cpu"),
        "dtype": cfg.get("dtype", "float32"),
        "language": cfg.get("language", "English"),
        "ref_audio_sha256": sha256_file(ref_audio),
        "ref_text_sha256": sha256_file(ref_text),
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Warm up Qwen voice clone for a project")
    p.add_argument("--project-dir", required=True, help="Project directory")
    p.add_argument(
        "--force",
        action="store_true",
        help="Re-run warmup even if ready stamp matches",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    project_dir = Path(args.project_dir).resolve()
    cfg_path = project_dir / "voice_clone_config.json"
    if not cfg_path.exists():
        print(f"ERROR: Missing {cfg_path}", file=sys.stderr)
        return 2

    cfg = load_json(cfg_path)

    python_path_raw = cfg.get("qwen_python")
    if not python_path_raw or not isinstance(python_path_raw, str):
        print("ERROR: voice_clone_config.json must define qwen_python", file=sys.stderr)
        return 2

    # Do NOT call .resolve() here.
    # venv python binaries are often symlinks to the base interpreter; resolving
    # would bypass the venv and break imports (e.g. qwen_tts).
    python_path = Path(os.path.expanduser(python_path_raw))
    if not python_path.is_absolute():
        python_path = (Path.cwd() / python_path).absolute()
    if not python_path.exists():
        print(f"ERROR: qwen_python not found: {python_path}", file=sys.stderr)
        return 2

    backend = selected_tts_backend()
    model_id = cfg.get("model_id", "Qwen/Qwen3-TTS-12Hz-1.7B-Base")
    device = cfg.get("device", "cpu")
    dtype_str = cfg.get("dtype", "float32")

    if backend == "qwen" and (device != "cpu" or dtype_str != "float32"):
        print(
            "ERROR: This repo requires CPU float32 for Qwen voice clone. "
            f"Found device={device!r} dtype={dtype_str!r} in voice_clone_config.json",
            file=sys.stderr,
        )
        return 2

    try:
        refs = resolve_voice_ref(project_dir, cfg)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    ref_audio = refs.ref_audio
    ref_text = refs.ref_text

    print(f"  Ref WAV: {ref_audio}")
    print(f"  Ref TXT: {ref_text}")

    output_dir_rel = cfg.get("output_dir", "media/voiceovers/qwen")
    output_dir = (project_dir / str(output_dir_rel)).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    ready_path = output_dir / "ready.json"

    fingerprint = compute_fingerprint(cfg, ref_audio, ref_text)

    if ready_path.exists() and not args.force:
        try:
            existing = load_json(ready_path)
            if existing.get("fingerprint") == fingerprint:
                print(f"✓ Qwen voice already prepared: {ready_path}")
                return 0
        except Exception:
            # Corrupted stamp -> re-run.
            pass

    worker = (Path(__file__).parent / "prepare_qwen_voice_worker.py").resolve()
    if not worker.exists():
        print(f"ERROR: Missing worker script: {worker}", file=sys.stderr)
        return 2

    ref_text_str = ref_text.read_text(encoding="utf-8").strip()
    if not ref_text_str:
        print(f"ERROR: Empty ref text: {ref_text}", file=sys.stderr)
        return 2

    # Reliability: qwen backend assumes model is already installed/cached locally.
    # For mlx backend, mediator chooses model via env/config at runtime.
    model_source = str(model_id)
    model_display = str(model_id)
    if backend == "mlx":
        model_display = selected_mlx_model_id(str(model_id))
    if backend == "qwen":
        model_id_path = Path(str(model_id))
        if isinstance(model_id, str) and model_id_path.exists():
            model_source = str(model_id_path)
            model_display = model_source
        else:
            snap = (
                find_hf_snapshot_dir(str(model_id))
                if isinstance(model_id, str)
                else None
            )
            if snap is None:
                hf_home = Path(
                    os.environ.get(
                        "HF_HOME", str(Path.home() / ".cache" / "huggingface")
                    )
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
                return 2

            model_source = str(snap)
            model_display = f"{model_id} (cached)"

    payload = {
        "model_source": model_source,
        "device": device,
        "dtype": dtype_str,
        "language": cfg.get("language", "English"),
        "ref_audio": str(ref_audio),
        "ref_text": ref_text_str,
    }

    print(f"→ Preparing voice backend: {backend}")
    print(f"  Python: {python_path}")
    print(f"  Model:  {model_display}")

    env = os.environ.copy()
    # Reliability: enforce offline mode; model must already be cached locally.
    env.setdefault("HF_HUB_OFFLINE", "1")
    env.setdefault("TRANSFORMERS_OFFLINE", "1")
    env.setdefault("TOKENIZERS_PARALLELISM", "false")
    env["PYTHONUNBUFFERED"] = "1"

    t0 = time.perf_counter()
    proc = Popen(
        [str(python_path), str(worker)],
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        text=True,
        env=env,
    )

    assert proc.stdin is not None
    assert proc.stdout is not None
    assert proc.stderr is not None

    proc.stdin.write(json.dumps(payload))
    proc.stdin.close()

    # Stream worker stderr to our stderr so the user sees progress.
    stderr_lines: list[str] = []
    while True:
        line = proc.stderr.readline()
        if not line:
            break
        stderr_lines.append(line)
        if should_forward_worker_stderr(line):
            sys.stderr.write(line)
            sys.stderr.flush()

    stdout_text = proc.stdout.read()
    rc = proc.wait()
    if rc != 0:
        if stdout_text.strip():
            print(stdout_text, file=sys.stderr)
        if stderr_lines and not stderr_lines[-1].endswith("\n"):
            print("", file=sys.stderr)
        print("ERROR: Qwen voice preparation failed.", file=sys.stderr)
        return rc

    stdout_lines = [ln for ln in stdout_text.splitlines() if ln.strip()]
    if not stdout_lines:
        print("ERROR: Worker returned empty output.", file=sys.stderr)
        return 2

    try:
        result = json.loads(stdout_lines[-1])
    except json.JSONDecodeError:
        print("ERROR: Worker did not return valid JSON.", file=sys.stderr)
        print(stdout_text, file=sys.stderr)
        return 2

    ready = {
        "fingerprint": fingerprint,
        "model_id": model_id,
        "model_source": model_source,
        "device": device,
        "dtype": dtype_str,
        "ref_audio": str(ref_audio),
        "ref_text": str(ref_text),
        "offline": True,
        "timings": result,
        "prepared_in_seconds": round(time.perf_counter() - t0, 3),
        "prepared_at": time.time(),
    }

    ready_path.write_text(json.dumps(ready, indent=2) + "\n", encoding="utf-8")
    print(f"✓ Voice backend prepared ({backend}): {ready_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
