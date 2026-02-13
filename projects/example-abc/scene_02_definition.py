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
class Scene02Definition(VoiceoverScene):
    def construct(self):
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # Animation Sequence
        # Timing budget: 0.3 + 0.7 = 1.0

        with self.voiceover(text=SCRIPT["definition"]) as tracker:
            # Title
            title = Text("Definition", font_size=42)
            title.move_to(UP * 3.8)
            slot = tracker.duration * 0.3
            self.play(Write(title), run_time=min(2.0, max(0.3, slot)))
            self.wait(max(0.0, slot - min(2.0, max(0.3, slot))))

            # Input-output diagram
            input_text = Text("Input (any size)", font_size=24)
            input_text.move_to(LEFT * 3)
            arrow = Arrow(LEFT * 1.5, RIGHT * 1.5, buff=0)
            hash_box = Rectangle(width=2, height=1, color=YELLOW)
            hash_box.move_to(ORIGIN)
            hash_text = Text("Hash Function", font_size=20)
            hash_text.move_to(hash_box.get_center())
            output_text = Text("Output (fixed size)", font_size=24)
            output_text.move_to(RIGHT * 3)

            diagram = VGroup(input_text, arrow, hash_box, hash_text, output_text)
            safe_position(diagram)

            slot = tracker.duration * 0.7
            self.play(FadeIn(diagram), run_time=min(2.0, max(0.3, slot)))
            self.wait(max(0.0, slot - min(2.0, max(0.3, slot))))