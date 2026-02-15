#!/usr/bin/env python3
"""Prepare strict cached Qwen voice service for a project."""

import argparse
import subprocess
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Prepare cached Qwen voice service for a project"
    )
    parser.add_argument("--project-dir", required=True, help="Project directory")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-preparation even if already ready",
    )
    return parser.parse_args()


def prepare_qwen_service(project_dir: Path, force: bool) -> int:
    script_dir = Path(__file__).parent
    prepare_qwen = script_dir / "prepare_qwen_voice.py"

    if not prepare_qwen.exists():
        print(
            f"ERROR: prepare_qwen_voice.py not found: {prepare_qwen}", file=sys.stderr
        )
        return 2

    cmd = [sys.executable, str(prepare_qwen), "--project-dir", str(project_dir)]
    if force:
        cmd.append("--force")

    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except Exception as exc:
        print(f"ERROR: Failed to run prepare_qwen_voice.py: {exc}", file=sys.stderr)
        return 2


def main() -> int:
    args = parse_args()
    project_dir = Path(args.project_dir).resolve()

    if not project_dir.exists():
        print(f"ERROR: Project directory not found: {project_dir}", file=sys.stderr)
        return 2

    print("→ Preparing cached Qwen voice service")
    return prepare_qwen_service(project_dir, args.force)


if __name__ == "__main__":
    raise SystemExit(main())
