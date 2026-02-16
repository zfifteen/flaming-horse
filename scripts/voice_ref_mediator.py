#!/usr/bin/env python3
"""Voice reference resolver - single source of truth for ref audio/text paths.

This module provides a mediator pattern to resolve voice reference paths,
allowing easy switching between reference samples via FLAMING_HORSE_VOICE_REF_DIR.

Precedence:
  1. FLAMING_HORSE_VOICE_REF_DIR (if set in environment)
  2. voice_clone_config.json ref_audio / ref_text (fallback)

All paths returned are absolute Path objects.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_REF_AUDIO = "ref.wav"
DEFAULT_REF_TEXT = "ref.txt"


@dataclass
class VoiceRef:
    """Resolved voice reference paths."""

    ref_audio: Path
    ref_text: Path


def resolve_voice_ref(project_dir: Path, cfg: dict[str, Any]) -> VoiceRef:
    """Resolve voice reference paths from environment or config.

    Args:
        project_dir: Absolute path to the project directory.
        cfg: Parsed voice_clone_config.json dictionary.

    Returns:
        VoiceRef with absolute paths to ref_audio and ref_text.

    Raises:
        ValueError: If required files are missing or ref_text is empty.
    """
    env_ref_dir = os.environ.get("FLAMING_HORSE_VOICE_REF_DIR", "").strip()

    if env_ref_dir:
        # Env var takes precedence - treat as base directory
        base_dir = Path(env_ref_dir).expanduser()
        if not base_dir.is_absolute():
            base_dir = (project_dir / base_dir).resolve()

        ref_audio = base_dir / DEFAULT_REF_AUDIO
        ref_text = base_dir / DEFAULT_REF_TEXT
    else:
        # Fall back to voice_clone_config.json paths
        ref_audio_rel = cfg.get("ref_audio", "").strip()
        ref_text_rel = cfg.get("ref_text", "").strip()

        if not ref_audio_rel or not ref_text_rel:
            raise ValueError(
                "voice_clone_config.json must define ref_audio and ref_text "
                "(or set FLAMING_HORSE_VOICE_REF_DIR)"
            )

        ref_audio = (project_dir / ref_audio_rel).resolve()
        ref_text = (project_dir / ref_text_rel).resolve()

    # Validate
    if not ref_audio.exists():
        raise ValueError(f"Missing ref audio: {ref_audio}")
    if not ref_text.exists():
        raise ValueError(f"Missing ref text: {ref_text}")

    ref_text_content = ref_text.read_text(encoding="utf-8").strip()
    if not ref_text_content:
        raise ValueError(f"Ref text is empty: {ref_text}")

    return VoiceRef(ref_audio=ref_audio, ref_text=ref_text)


def check_voice_ref_exists(
    project_dir: Path | None = None, cfg: dict[str, Any] | None = None
) -> tuple[bool, str]:
    """Check if voice reference exists (for shell scripts).

    Returns:
        (exists: bool, error_message: str)
    """
    # First check: if FLAMING_HORSE_VOICE_REF_DIR is set, validate that directly
    env_ref_dir = os.environ.get("FLAMING_HORSE_VOICE_REF_DIR", "").strip()
    if env_ref_dir:
        base_dir = Path(env_ref_dir).expanduser()
        ref_audio = base_dir / "ref.wav"
        ref_text = base_dir / "ref.txt"
        if not ref_audio.exists():
            return False, f"Missing ref audio: {ref_audio}"
        if not ref_text.exists():
            return False, f"Missing ref text: {ref_text}"
        if not ref_text.read_text(encoding="utf-8").strip():
            return False, f"Ref text is empty: {ref_text}"
        return True, ""

    # Second check: if cfg provided, use that
    if cfg is not None and project_dir is not None:
        try:
            resolve_voice_ref(project_dir, cfg)
            return True, ""
        except ValueError as e:
            return False, str(e)

    # Third check: try to load from project if not provided
    if project_dir is None:
        return False, "No project_dir and no FLAMING_HORSE_VOICE_REF_DIR"

    config_path = project_dir / "voice_clone_config.json"
    if not config_path.exists():
        return False, f"Missing voice_clone_config.json: {config_path}"

    import json

    try:
        cfg = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception as e:
        return False, f"Invalid voice_clone_config.json: {e}"

    try:
        resolve_voice_ref(project_dir, cfg)
        return True, ""
    except ValueError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Error resolving voice ref: {e}"


if __name__ == "__main__":
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(description="Resolve voice reference paths")
    parser.add_argument("project_dir", nargs="?", default=".", help="Project directory")
    parser.add_argument("--check", action="store_true", help="Just check if refs exist")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()

    # First check: if FLAMING_HORSE_VOICE_REF_DIR is set, validate that directly
    # (skip loading voice_clone_config.json)
    env_ref_dir = os.environ.get("FLAMING_HORSE_VOICE_REF_DIR", "").strip()
    if env_ref_dir:
        base_dir = Path(env_ref_dir).expanduser()
        ref_audio = base_dir / "ref.wav"
        ref_text = base_dir / "ref.txt"
        if args.check:
            if (
                ref_audio.exists()
                and ref_text.exists()
                and ref_text.read_text(encoding="utf-8").strip()
            ):
                print("OK")
                sys.exit(0)
            else:
                print(
                    f"ERROR: Missing or empty ref files in {env_ref_dir}",
                    file=sys.stderr,
                )
                sys.exit(1)
        # Not --check mode: continue to normal resolution
        print(f"ref_audio={ref_audio}")
        print(f"ref_text={ref_text}")
        sys.exit(0)

    # Standard path: require voice_clone_config.json
    config_path = project_dir / "voice_clone_config.json"

    if not config_path.exists():
        print(f"ERROR: Missing voice_clone_config.json: {config_path}", file=sys.stderr)
        sys.exit(1)

    cfg = json.loads(config_path.read_text(encoding="utf-8"))

    if args.check:
        exists, error = check_voice_ref_exists(project_dir, cfg)
        if exists:
            print("OK")
            sys.exit(0)
        else:
            print(f"ERROR: {error}", file=sys.stderr)
            sys.exit(1)

    try:
        refs = resolve_voice_ref(project_dir, cfg)
        print(f"ref_audio={refs.ref_audio}")
        print(f"ref_text={refs.ref_text}")
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
