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
class Scene06FrequencyDownconversion(VoiceoverScene):
    def construct(self):
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # ── Animation Sequence ─────────────────────────────────────
        with self.voiceover(text=SCRIPT["downconversion"]) as tracker:
            # Frequency axis
            axes = Axes(x_range=(0, 10), y_range=(0, 1), x_length=8, y_length=2)
            x_label = Text("Frequency", font_size=24).next_to(axes, DOWN)
            safe_position(x_label)

            # High frequency
            high = Text("MHz Ion Physics", font_size=24).move_to(
                axes.c2p(8, 0.5) + UP * 0.5
            )
            arrow = Arrow(axes.c2p(8, 0.5), axes.c2p(2, 0.5), color=YELLOW)
            low = Text("kHz Modulators", font_size=24).move_to(
                axes.c2p(2, 0.5) + DOWN * 0.5
            )
            safe_position(low)

            self.play(Create(axes), Write(x_label), run_time=tracker.duration * 0.3)
            self.play(Write(high), run_time=tracker.duration * 0.2)
            self.play(Create(arrow), run_time=tracker.duration * 0.2)
            self.play(Write(low), run_time=tracker.duration * 0.3)