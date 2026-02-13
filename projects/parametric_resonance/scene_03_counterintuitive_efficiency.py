import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import *
import numpy as np

# ── Python 3.13 Compatibility Patch ────────────────────────────────
import manim_voiceover_plus.services.base as base

original_set_transcription = base.SpeechService.set_transcription


def patched_set_transcription(self, model=None, kwargs=None):
    if model is None:
        self.transcription_model = None
        self.whisper_model = None
        return
    original_set_transcription(self, model=model, kwargs=kwargs)


base.SpeechService.set_transcription = patched_set_transcription

# ── Voiceover Imports ──────────────────────────────────────────────
from manim_voiceover_plus import VoiceoverScene
from flaming_horse_voice import get_speech_service

# ── Import Shared Configuration ────────────────────────────────────
from narration_script import SCRIPT

# ── LOCKED CONFIGURATION (DO NOT MODIFY) ───────────────────────────
config.frame_height = 10
config.frame_width = 10 * 16 / 9
config.pixel_height = 1440
config.pixel_width = 2560


# ── Safe Positioning Helper ────────────────────────────────────────
def safe_position(mobject, max_y=4.0, min_y=-4.0):
    """Ensure mobject stays within safe bounds after positioning"""
    top = mobject.get_top()[1]
    bottom = mobject.get_bottom()[1]
    if top > max_y:
        mobject.shift(DOWN * (top - max_y))
    elif bottom < min_y:
        mobject.shift(UP * (min_y - bottom))
    return mobject


# ── Scene Class ────────────────────────────────────────────────────
class Scene03CounterintuitiveEfficiency(VoiceoverScene):
    def construct(self):
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # ── Animation Sequence ─────────────────────────────────────
        with self.voiceover(text=SCRIPT["efficiency"]) as tracker:
            # Bar for weak pressure right frequency
            bar1 = Rectangle(width=1, height=4, color=GREEN, fill_opacity=0.8)
            bar1.move_to(LEFT * 3 + UP * 2)
            label1 = Text("Weak P, Right f\nHigh Efficiency", font_size=24, color=GREEN)
            label1.next_to(bar1, DOWN)
            safe_position(label1)

            # Bar for strong pressure wrong frequency
            bar2 = Rectangle(width=1, height=1, color=RED, fill_opacity=0.8)
            bar2.move_to(RIGHT * 3 + UP * 0.5)
            label2 = Text("Strong P, Wrong f\nLow Efficiency", font_size=24, color=RED)
            label2.next_to(bar2, DOWN)
            safe_position(label2)

            self.play(Create(bar1), Write(label1), run_time=tracker.duration * 0.5)
            self.play(Create(bar2), Write(label2), run_time=tracker.duration * 0.5)