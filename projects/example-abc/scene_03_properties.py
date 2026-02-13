import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

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
from flaming_horse_voice import get_speech_service

# Import Shared Configuration
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
class Scene03Properties(VoiceoverScene):
    def construct(self):
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # Animation Sequence
        # Timing budget: 0.4 + 0.6 = 1.0

        with self.voiceover(text=SCRIPT["properties"]) as tracker:
            # Title
            title = Text("Key Properties", font_size=42)
            title.move_to(UP * 3.8)
            slot = tracker.duration * 0.4
            self.play(Write(title), run_time=min(2.0, max(0.3, slot)))
            self.wait(max(0.0, slot - min(2.0, max(0.3, slot))))

            # List properties
            prop1 = Text("• Deterministic: Same input → Same hash", font_size=28)
            prop1.move_to(UP * 1)
            prop2 = Text("• One-way: Can't reverse the process", font_size=28)
            prop2.next_to(prop1, DOWN, buff=0.5)
            safe_position(prop2)
            prop3 = Text(
                "• Avalanche effect: Small changes → Big differences", font_size=28
            )
            prop3.next_to(prop2, DOWN, buff=0.5)
            safe_position(prop3)

            props = VGroup(prop1, prop2, prop3)
            safe_position(props)

            slot = tracker.duration * 0.6
            self.play(FadeIn(props), run_time=min(2.0, max(0.3, slot)))
            self.wait(max(0.0, slot - min(2.0, max(0.3, slot))))