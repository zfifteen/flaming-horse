# Legacy Projects Archive

This directory contains configuration files from projects created before the migration to Qwen voice clone (February 2026).

## Contents

### `matrix-multiplication_voice_config.py`

**Original Location:** `projects/matrix-multiplication/voice_config.py`

**Status:** Archived - Contains obsolete ElevenLabs imports

**Why Archived:** This file imports `elevenlabs` module which is no longer a dependency and would cause `ModuleNotFoundError` if imported. The matrix-multiplication project is complete and this configuration is preserved only for historical reference.

**Note:** The completed project video and all scene files remain in `projects/matrix-multiplication/`. Only the legacy voice configuration has been moved to prevent import errors.

## Current Voice Policy

All new projects use **Qwen voice clone only** with cached audio and no network TTS services. See `docs/VOICE_POLICY.md` for current requirements.
