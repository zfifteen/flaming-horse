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
class Scene04AmbiguousData(VoiceoverScene):
    def construct(self):
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # ── Animation Sequence ─────────────────────────────────────
        # Timing budget: 0.3 + 0.4 + 0.3 = 1.0

        with self.voiceover(text=SCRIPT["ambiguous_data"]) as tracker:
            # Title
            title = Text("Ambiguous Data", font_size=48, weight=BOLD)
            title.move_to(UP * 3.8)
            self.play(Write(title), run_time=tracker.duration * 0.3)

            # Simple bar chart with yellow shaded zone
            axes = Axes(x_range=[0, 10, 1], y_range=[0, 5, 1])
            axes.move_to(ORIGIN)
            bar = Rectangle(width=1, height=3, color=GRAY)
            bar.move_to(axes.coords_to_point(5, 1.5))
            zone = Rectangle(width=8, height=1, color=YELLOW, fill_opacity=0.5)
            zone.move_to(axes.coords_to_point(5, 2.5))
            self.play(
                Create(axes), FadeIn(bar), FadeIn(zone), run_time=tracker.duration * 0.4
            )

            # Animate data points bouncing
            point = Dot(color=BLUE)
            point.move_to(bar.get_top())
            question = Text("?", color=RED, font_size=48)
            question.next_to(point, UP)
            self.play(
                AnimationGroup(
                    point.animate.shift(UP * 0.5),
                    point.animate.shift(DOWN * 0.5),
                    lag_ratio=0.5,
                ),
                FadeIn(question),
                run_time=tracker.duration * 0.3,
            )