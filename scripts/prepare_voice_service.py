#!/usr/bin/env python3
"""
Unified voice service preparation with mock fallback.

This script provides a single entry point for voice preparation that
automatically chooses between real Qwen service and mock service.

Usage:
    # Real service (requires Qwen setup)
    python prepare_voice_service.py --project-dir projects/my_video
    
    # Mock service (no setup needed)
    FLAMING_HORSE_MOCK_VOICE=1 python prepare_voice_service.py --project-dir projects/my_video
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser(
        description="Prepare voice service (real or mock) for a project"
    )
    p.add_argument("--project-dir", required=True, help="Project directory")
    p.add_argument(
        "--force",
        action="store_true",
        help="Force re-preparation even if already ready",
    )
    p.add_argument(
        "--mock",
        action="store_true",
        help="Force mock service (overrides environment)",
    )
    return p.parse_args()


def should_use_mock(args):
    """Determine if mock service should be used."""
    if args.mock:
        return True
    
    mock_env = os.environ.get("FLAMING_HORSE_MOCK_VOICE", "").lower()
    return mock_env in ("1", "true", "yes")


def prepare_mock_service(project_dir: Path, force: bool) -> int:
    """
    Prepare mock voice service by creating ready.json.
    
    Mock service doesn't need actual model warmup, so we just create
    the ready marker immediately.
    """
    output_dir = project_dir / "media" / "voiceovers" / "qwen"
    output_dir.mkdir(parents=True, exist_ok=True)
    ready_path = output_dir / "ready.json"
    
    if ready_path.exists() and not force:
        try:
            existing = json.loads(ready_path.read_text(encoding="utf-8"))
            if existing.get("service_type") == "mock":
                print(f"✓ Mock voice service already prepared: {ready_path}")
                return 0
        except Exception:
            pass
    
    # Create ready.json for mock service
    ready = {
        "service_type": "mock",
        "prepared_at": time.time(),
        "prepared_in_seconds": 0.0,
        "note": "Mock voice service uses dummy audio for testing/development",
    }
    
    ready_path.write_text(json.dumps(ready, indent=2) + "\n", encoding="utf-8")
    print(f"✓ Mock voice service prepared: {ready_path}")
    print(f"  Using FLAMING_HORSE_MOCK_VOICE mode")
    print(f"  Videos will have silent audio segments")
    
    return 0


def prepare_real_service(project_dir: Path, force: bool) -> int:
    """
    Prepare real Qwen voice service by delegating to prepare_qwen_voice.py.
    """
    script_dir = Path(__file__).parent
    prepare_qwen = script_dir / "prepare_qwen_voice.py"
    
    if not prepare_qwen.exists():
        print(f"ERROR: prepare_qwen_voice.py not found: {prepare_qwen}", file=sys.stderr)
        return 2
    
    cmd = [
        sys.executable,
        str(prepare_qwen),
        "--project-dir", str(project_dir),
    ]
    
    if force:
        cmd.append("--force")
    
    # Delegate to real preparation script
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except Exception as e:
        print(f"ERROR: Failed to run prepare_qwen_voice.py: {e}", file=sys.stderr)
        return 2


def main() -> int:
    args = parse_args()
    project_dir = Path(args.project_dir).resolve()
    
    if not project_dir.exists():
        print(f"ERROR: Project directory not found: {project_dir}", file=sys.stderr)
        return 2
    
    use_mock = should_use_mock(args)
    
    if use_mock:
        print("→ Preparing MOCK voice service")
        return prepare_mock_service(project_dir, args.force)
    else:
        print("→ Preparing REAL Qwen voice service")
        return prepare_real_service(project_dir, args.force)


if __name__ == "__main__":
    raise SystemExit(main())
