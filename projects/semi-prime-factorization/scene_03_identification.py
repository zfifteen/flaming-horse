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
class Scene03Identification(VoiceoverScene):
    def construct(self):
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # Animation Sequence

        with self.voiceover(text=SCRIPT["identification"]) as tracker:
            # Title
            title = Text("Identifying Semi-Primes", font_size=48, weight=BOLD)
            title.move_to(UP * 3.8)
            slot = tracker.duration * 0.2
            self.play(Write(title), run_time=min(2.0, max(0.3, slot)))
            self.wait(max(0.0, slot - min(2.0, max(0.3, slot))))

            # Subtitle
            subtitle = Text("Trial Division Method", font_size=32)
            subtitle.next_to(title, DOWN, buff=0.5)
            safe_position(subtitle)
            slot = tracker.duration * 0.15
            self.play(FadeIn(subtitle), run_time=min(2.0, max(0.3, slot)))
            self.wait(max(0.0, slot - min(2.0, max(0.3, slot))))

            # Show example: check 15
            number = MathTex("15", font_size=48)
            number.move_to(ORIGIN)
            slot = tracker.duration * 0.2
            self.play(Write(number), run_time=min(2.0, max(0.3, slot)))
            self.wait(max(0.0, slot - min(2.0, max(0.3, slot))))

            # Divide by 3
            division = MathTex(r"15 \div 3 = 5", font_size=36)
            division.next_to(number, DOWN, buff=0.5)
            safe_position(division)
            slot = tracker.duration * 0.25
            self.play(Write(division), run_time=min(2.0, max(0.3, slot)))
            self.wait(max(0.0, slot - min(2.0, max(0.3, slot))))

            # Result
            result = MathTex(r"15 = 3 \times 5", font_size=36)
            result.next_to(division, DOWN, buff=0.5)
            safe_position(result)
            slot = tracker.duration * 0.2
            self.play(Write(result), run_time=min(2.0, max(0.3, slot)))
            self.wait(max(0.0, slot - min(2.0, max(0.3, slot))))