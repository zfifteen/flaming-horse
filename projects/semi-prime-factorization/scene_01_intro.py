from manim import *
import numpy as np

# Python 3.13 Compatibility Patch
import manim_voiceover_plus.services.base as base

original_set_transcription = base.SpeechService.set_transcription


def patched_set_transcription(self, model=None, kwargs=None):
    if model is None:
        self.transcription_model = None
        self.whisper_model = None
        return
    original_set_transcription(self, model=model, kwargs=kwargs)


base.SpeechService.set_transcription = patched_set_transcription

# Voiceover Imports
from manim_voiceover_plus import VoiceoverScene
from manim_voiceover_plus.services.elevenlabs import ElevenLabsService
from elevenlabs import VoiceSettings

# Import Shared Configuration
from voice_config import VOICE_ID, MODEL_ID, VOICE_SETTINGS
from narration_script import SCRIPT

# LOCKED CONFIGURATION (DO NOT MODIFY)
config.frame_height = 10
config.frame_width = 10 * 16 / 9
config.pixel_height = 1440
config.pixel_width = 2560


# Safe Positioning Helper
def safe_position(mobject, max_y=4.0, min_y=-4.0):
    """Ensure mobject stays within safe bounds after positioning"""
    top = mobject.get_top()[1]
    bottom = mobject.get_bottom()[1]
    if top > max_y:
        mobject.shift(DOWN * (top - max_y))
    elif bottom < min_y:
        mobject.shift(UP * (min_y - bottom))
    return mobject


# Scene Class
class Scene01Intro(VoiceoverScene):
    def construct(self):
        # ELEVENLABS ONLY - NO FALLBACK - FAIL LOUD
        self.set_speech_service(
            ElevenLabsService(
                voice_id=VOICE_ID,
                model_id=MODEL_ID,
                voice_settings=VOICE_SETTINGS,
                transcription_model=None,
            )
        )

        # Animation Sequence
        # Timing budget: Calculate BEFORE writing animations
        # Example: 0.4 + 0.3 + 0.3 = 1.0 ✓

        with self.voiceover(text=SCRIPT["intro"]) as tracker:
            # Title (ALWAYS use UP * 3.8, NEVER .to_edge(UP))
            title = Text("Semi-Prime Numbers", font_size=48, weight=BOLD)
            title.move_to(UP * 3.8)
            # Text must never take longer than 2 seconds to display.
            slot = tracker.duration * 0.3
            self.play(Write(title), run_time=min(2.0, max(0.3, slot)))
            self.wait(max(0.0, slot - min(2.0, max(0.3, slot))))

            # Subtitle with safe positioning
            subtitle = Text("Introduction", font_size=32)
            subtitle.next_to(title, DOWN, buff=0.5)
            safe_position(subtitle)  # ALWAYS call after .next_to()
            slot = tracker.duration * 0.2
            self.play(FadeIn(subtitle), run_time=min(2.0, max(0.3, slot)))
            self.wait(max(0.0, slot - min(2.0, max(0.3, slot))))

            # Examples of semi-primes
            examples = VGroup(
                MathTex(r"4 = 2 \times 2", font_size=36),
                MathTex(r"6 = 2 \times 3", font_size=36),
                MathTex(r"9 = 3 \times 3", font_size=36),
            ).arrange(DOWN, buff=0.5)
            examples.move_to(ORIGIN)
            safe_position(examples)
            slot = tracker.duration * 0.5
            self.play(FadeIn(examples), run_time=min(2.0, max(0.3, slot)))
            self.wait(max(0.0, slot - min(2.0, max(0.3, slot))))
