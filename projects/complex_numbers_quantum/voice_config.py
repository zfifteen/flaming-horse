"""
Voice configuration for ElevenLabs TTS
LOCKED - Do not modify after narration phase
"""

from elevenlabs import VoiceSettings

# Big D's cloned voice - DO NOT CHANGE
VOICE_ID = "rBgRd5IfS6iqrGfuhlKR"
MODEL_ID = "eleven_multilingual_v2"

VOICE_SETTINGS = VoiceSettings(
    stability=0.5, similarity_boost=0.75, style=0.0, use_speaker_boost=True
)
