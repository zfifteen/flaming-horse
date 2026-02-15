#!/usr/bin/env python3
"""
Voice cache validator to skip unnecessary precaching operations.

This script checks if the voice cache is valid and up-to-date with the
narration script, avoiding redundant TTS generation.

Usage:
    python3 voice_cache_validator.py <project_dir>

Exit codes:
    0 - Cache is valid and up-to-date
    1 - Cache is missing or stale (needs regeneration)
"""

import sys
import json
import hashlib
from pathlib import Path


def compute_narration_hash(narration_file: Path) -> str:
    """Compute a hash of the narration script content."""
    if not narration_file.exists():
        return ""

    # Read narration script and extract SCRIPT dictionary content
    content = narration_file.read_text(encoding="utf-8")

    # Hash the entire content for simplicity
    # Could be more sophisticated by parsing only SCRIPT dict
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def check_cache_validity(project_dir: Path) -> bool:
    """
    Check if voice cache is valid and matches current narration.

    Returns:
        True if cache is valid and up-to-date
        False if cache needs regeneration
    """
    narration_file = project_dir / "narration_script.py"
    cache_index = project_dir / "media" / "voiceovers" / "qwen" / "cache.json"
    cache_hash_file = project_dir / "media" / "voiceovers" / "qwen" / ".cache_hash"

    # If cache doesn't exist, it needs generation
    if not cache_index.exists():
        print("❌ Cache index missing")
        return False

    # If narration doesn't exist, cache is invalid
    if not narration_file.exists():
        print("❌ Narration script missing")
        return False

    # Load cache index to verify it's valid JSON and has entries.
    # Canonical format is a non-empty LIST of entry dictionaries.
    try:
        with open(cache_index, "r") as f:
            cache_data = json.load(f)

        if not isinstance(cache_data, list):
            print("❌ Cache index is not a valid list")
            return False

        if len(cache_data) == 0:
            print("❌ Cache index is empty")
            return False

        for i, entry in enumerate(cache_data):
            if not isinstance(entry, dict):
                print(f"❌ Cache entry {i} is not an object")
                return False

            # Support both cache schemas found in this pipeline:
            # 1) Precache schema: narration_key + text + audio_file
            # 2) Runtime metadata schema: input_text + final_audio
            audio_file = entry.get("audio_file") or entry.get("final_audio")
            text = entry.get("text") or entry.get("input_text")

            if not isinstance(audio_file, str) or not audio_file:
                print(f"❌ Cache entry {i} missing audio file field")
                return False
            if not isinstance(text, str) or not text:
                print(f"❌ Cache entry {i} missing text field")
                return False

    except (json.JSONDecodeError, IOError) as e:
        print(f"❌ Cache index read error: {e}")
        return False

    # Check if narration has changed since last cache
    current_hash = compute_narration_hash(narration_file)

    if cache_hash_file.exists():
        cached_hash = cache_hash_file.read_text(encoding="utf-8").strip()
        if cached_hash == current_hash:
            print("✓ Voice cache is valid and up-to-date")
            return True
        else:
            print("❌ Narration script has changed since last cache")
            return False
    else:
        # Hash file doesn't exist, assume cache might be stale
        # Save current hash for next check
        cache_hash_file.parent.mkdir(parents=True, exist_ok=True)
        cache_hash_file.write_text(current_hash, encoding="utf-8")

        # If cache exists but hash file doesn't, assume it's valid
        # (backward compatibility)
        print("⚠ Cache hash file missing, created for future checks")
        return True


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    project_dir = Path(sys.argv[1])

    if not project_dir.exists():
        print(f"Error: Project directory not found: {project_dir}", file=sys.stderr)
        sys.exit(1)

    if check_cache_validity(project_dir):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
