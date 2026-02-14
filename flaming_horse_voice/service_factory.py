"""
Voice service factory with intelligent mock fallback.

Automatically selects between real Qwen voice service and mock service
based on environment variables and availability of cached assets.
"""

import os
from pathlib import Path


def get_speech_service(project_dir, force_mock=None):
    """Get appropriate speech service (real or mock).
    
    Args:
        project_dir: Path to project directory
        force_mock: If True, always use mock. If False, never use mock.
                   If None (default), auto-detect based on environment.
    
    Returns:
        SpeechService instance (QwenCachedService or QwenMockService)
    """
    project_dir = Path(project_dir).resolve()
    
    # Check force_mock override first
    if force_mock is True:
        return _create_mock_service(project_dir)
    
    # Check environment variable
    if os.environ.get("FLAMING_HORSE_MOCK_VOICE", "").lower() in ("1", "true", "yes"):
        print("→ Using mock voice service (FLAMING_HORSE_MOCK_VOICE=1)")
        return _create_mock_service(project_dir)
    
    # If force_mock=False, don't auto-detect
    if force_mock is False:
        return _create_real_service(project_dir)
    
    # Auto-detect: check if real service assets are available
    cache_file = project_dir / "media" / "voiceovers" / "qwen" / "cache.json"
    narration_script = project_dir / "narration_script.py"
    
    has_cache = cache_file.exists()
    has_script = narration_script.exists()
    
    if not has_cache or not has_script:
        print(f"→ Auto-detected missing assets, using mock voice service")
        print(f"  Cache exists: {has_cache}")
        print(f"  Script exists: {has_script}")
        return _create_mock_service(project_dir)
    
    # Try to create real service
    try:
        return _create_real_service(project_dir)
    except (FileNotFoundError, ImportError, Exception) as e:
        print(f"→ Real service unavailable ({e}), falling back to mock")
        return _create_mock_service(project_dir)


def _create_mock_service(project_dir):
    """Create mock voice service."""
    from flaming_horse_voice.qwen_mock import QwenMockService
    
    cache_dir = project_dir / "media" / "voiceovers" / "qwen"
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    return QwenMockService(
        cache_dir=str(cache_dir),
        words_per_second=2.5,  # ~150 WPM reading speed
    )


def _create_real_service(project_dir):
    """Create real Qwen cached service."""
    from flaming_horse_voice.qwen_cached import QwenCachedService
    
    return QwenCachedService.from_project(project_dir)
