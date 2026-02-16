"""
DEPRECATED: Legacy ElevenLabs voice configuration

This file is from the matrix-multiplication project created before the migration
to Qwen voice clone (February 2026). It is preserved for historical reference only.

The project has been completed and this configuration is no longer used.

Current voice policy: All new projects use local Qwen voice clone with cached audio.
See docs/VOICE_POLICY.md for current requirements.
"""

# Historical ElevenLabs configuration (no longer used)
# The following configuration was used during the ElevenLabs era:

from elevenlabs import VoiceSettings

# Big D's cloned voice - DO NOT CHANGE
VOICE_ID = "rBgRd5IfS6iqrGfuhlKR"
MODEL_ID = "eleven_multilingual_v2"

VOICE_SETTINGS = VoiceSettings(
    stability=0.5, similarity_boost=0.75, style=0.0, use_speaker_boost=True
)
