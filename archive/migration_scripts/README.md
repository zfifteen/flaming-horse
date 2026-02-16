# Migration Scripts Archive

This directory contains one-time migration scripts that were used during the transition from ElevenLabs to Qwen voice clone.

## Contents

### `migrate_voiceover_to_qwen.py`

**Status:** Completed - No longer needed for active development

**Purpose:** One-time migration script used to convert existing scene files from ElevenLabs voice service to the local Qwen voice clone system.

**Date:** Migration completed February 2026

**What it does:**
- Replaces ElevenLabs imports with cached Qwen service imports
- Updates `set_speech_service()` calls to use `get_speech_service()`
- Removes `voice_config.py` dependencies from scene files
- Updates comments to reflect new voice policy

**Note:** This script references ElevenLabs patterns as part of its search-and-replace logic. These references are intentional and do not indicate active ElevenLabs usage in the codebase.

## Why Archived?

These scripts served their purpose during the migration phase and are no longer needed for day-to-day development. They are preserved here for:

1. Historical reference
2. Documentation of the migration process
3. Potential future migrations to other voice services

## Current Voice Policy

The repository now uses **Qwen voice clone only** with no network TTS services. See `docs/VOICE_POLICY.md` for details.
