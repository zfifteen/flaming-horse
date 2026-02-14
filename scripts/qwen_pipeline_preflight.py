#!/usr/bin/env python3
"""Preflight validator for Flaming Horse + local Qwen cached voice pipeline.

Checks:
- project_dir + required files
- voice_clone_config.json policy (CPU + float32)
- qwen_python path
- reference assets and non-empty transcript
- local HF snapshot presence for model_id
- optional warmup (`prepare_qwen_voice.py`)
- optional precache (`precache_voiceovers_qwen.py`)
- cache artifacts and service load (`QwenCachedService.from_project`)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate and optionally execute Flaming Horse Qwen integration steps"
    )
    parser.add_argument("--project-dir", required=True, help="Project directory")
    parser.add_argument(
        "--run-prepare",
        action="store_true",
        help="Run scripts/prepare_qwen_voice.py after validation",
    )
    parser.add_argument(
        "--run-precache",
        action="store_true",
        help="Run scripts/precache_voiceovers_qwen.py after validation",
    )
    return parser.parse_args()


def fail(msg: str) -> None:
    raise RuntimeError(msg)


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON at {path}: {exc}")


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def hf_repo_id_to_cache_dirname(model_id: str) -> str | None:
    if "/" not in model_id:
        return None
    org, repo = model_id.split("/", 1)
    if not org or not repo:
        return None
    return f"models--{org}--{repo}"


def find_hf_snapshot_dir(model_id: str) -> Path | None:
    dirname = hf_repo_id_to_cache_dirname(model_id)
    if not dirname:
        return None

    hf_home = Path(os.environ.get("HF_HOME", str(Path.home() / ".cache" / "huggingface")))
    model_dir = hf_home / "hub" / dirname
    snapshots_dir = model_dir / "snapshots"
    if not snapshots_dir.exists():
        return None

    ref_main = model_dir / "refs" / "main"
    if ref_main.exists():
        commit = ref_main.read_text(encoding="utf-8").strip()
        if commit:
            candidate = snapshots_dir / commit
            if candidate.exists():
                return candidate

    snapshots = [p for p in snapshots_dir.iterdir() if p.is_dir()]
    if not snapshots:
        return None
    snapshots.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return snapshots[0]


def run_checked(cmd: list[str], *, cwd: Path) -> None:
    proc = subprocess.run(cmd, cwd=str(cwd), check=False)
    if proc.returncode != 0:
        fail(f"Command failed with exit code {proc.returncode}: {' '.join(cmd)}")


def ensure_cache_artifacts(project_dir: Path, output_dir_rel: str) -> tuple[Path, Path, list[Path]]:
    output_dir = (project_dir / output_dir_rel).resolve()
    cache_json = output_dir / "cache.json"
    if not cache_json.exists():
        fail(f"Missing cache index: {cache_json}")

    entries = load_json(cache_json)
    if not isinstance(entries, list) or not entries:
        fail(f"Cache index is empty/invalid: {cache_json}")

    mp3_files = sorted(output_dir.glob("*.mp3"))
    if not mp3_files:
        fail(f"No MP3 cache files found under: {output_dir}")

    return output_dir, cache_json, mp3_files


def main() -> int:
    args = parse_args()
    project_dir = Path(args.project_dir).resolve()
    repo_root = repo_root_from_script()

    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)

    if not project_dir.exists():
        fail(f"Project directory not found: {project_dir}")

    state_path = project_dir / "project_state.json"
    if not state_path.exists():
        fail(f"Missing project_state.json: {state_path}")

    cfg_path = project_dir / "voice_clone_config.json"
    if not cfg_path.exists():
        fail(f"Missing voice_clone_config.json: {cfg_path}")

    cfg = load_json(cfg_path)

    model_id = str(cfg.get("model_id", "Qwen/Qwen3-TTS-12Hz-1.7B-Base"))
    device = str(cfg.get("device", "cpu"))
    dtype_str = str(cfg.get("dtype", "float32"))
    qwen_python_raw = cfg.get("qwen_python")
    ref_audio_rel = cfg.get("ref_audio")
    ref_text_rel = cfg.get("ref_text")
    output_dir_rel = str(cfg.get("output_dir", "media/voiceovers/qwen"))

    if device != "cpu":
        fail(f"voice_clone_config.json requires device='cpu', got: {device!r}")
    if dtype_str != "float32":
        fail(f"voice_clone_config.json requires dtype='float32', got: {dtype_str!r}")

    if not isinstance(qwen_python_raw, str) or not qwen_python_raw.strip():
        fail("voice_clone_config.json missing required key: qwen_python")
    qwen_python = Path(os.path.expanduser(qwen_python_raw))
    if not qwen_python.is_absolute():
        qwen_python = (Path.cwd() / qwen_python).resolve()
    if not qwen_python.exists():
        fail(f"qwen_python path not found: {qwen_python}")

    if not isinstance(ref_audio_rel, str) or not isinstance(ref_text_rel, str):
        fail("voice_clone_config.json must define string ref_audio and ref_text")

    ref_audio = (project_dir / ref_audio_rel).resolve()
    ref_text = (project_dir / ref_text_rel).resolve()
    if not ref_audio.exists():
        fail(f"Missing reference audio: {ref_audio}")
    if not ref_text.exists():
        fail(f"Missing reference transcript: {ref_text}")
    if not ref_text.read_text(encoding="utf-8").strip():
        fail(f"Reference transcript is empty: {ref_text}")

    snapshot_dir = find_hf_snapshot_dir(model_id)
    if snapshot_dir is None:
        hf_home = Path(os.environ.get("HF_HOME", str(Path.home() / ".cache" / "huggingface")))
        fail(
            "Qwen model snapshot not found in local HuggingFace cache. "
            f"Model: {model_id} | Expected under: {hf_home / 'hub'}"
        )

    print("Preflight checks passed:")
    print(f"- project_dir={project_dir}")
    print(f"- model_id={model_id}")
    print(f"- device={device}")
    print(f"- dtype={dtype_str}")
    print(f"- qwen_python={qwen_python}")
    print(f"- hf_snapshot={snapshot_dir}")
    print(f"- ref_audio={ref_audio}")
    print(f"- ref_text={ref_text}")

    if args.run_prepare:
        print("\nRunning prepare_qwen_voice.py...")
        run_checked(
            [
                "python3",
                str(repo_root / "scripts" / "prepare_qwen_voice.py"),
                "--project-dir",
                str(project_dir),
            ],
            cwd=repo_root,
        )

    if args.run_precache:
        narration_script = project_dir / "narration_script.py"
        if not narration_script.exists():
            fail(
                "Cannot run precache: narration_script.py is missing. "
                "Run plan/review/narration phases first."
            )
        print("\nRunning precache_voiceovers_qwen.py...")
        run_checked(
            [
                "python3",
                str(repo_root / "scripts" / "precache_voiceovers_qwen.py"),
                str(project_dir),
            ],
            cwd=repo_root,
        )

    output_dir, cache_json, mp3_files = ensure_cache_artifacts(project_dir, output_dir_rel)

    try:
        from flaming_horse_voice import get_speech_service

        service = get_speech_service(project_dir)
        service_name = type(service).__name__
    except Exception as exc:  # noqa: BLE001
        fail(f"Failed to instantiate cached speech service: {type(exc).__name__}: {exc}")

    print("\nIntegration artifacts:")
    print(f"- output_dir={output_dir}")
    print(f"- cache_json={cache_json}")
    print(f"- mp3_count={len(mp3_files)}")
    print(f"- speech_service={service_name}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)
