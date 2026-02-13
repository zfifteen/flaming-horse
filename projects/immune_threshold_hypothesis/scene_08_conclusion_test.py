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
class Scene08ConclusionTest(VoiceoverScene):
    def construct(self):
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # ── Animation Sequence ─────────────────────────────────────
        # Timing budget: 0.1 + 0.1 + 0.1 + 0.1 + 0.2 + 0.1 + 0.1 + 0.1 = 1.0 ✓

        with self.voiceover(text=SCRIPT["conclusion_test"]) as tracker:
            # Split timelines
            top_axes = Axes(x_range=[2025, 2028, 1], y_range=[0, 100, 20]).move_to(
                LEFT * 3 + UP * 1
            )
            top_label = Text("Threshold Model Correct", font_size=20).next_to(
                top_axes, UP
            )
            safe_position(top_label)

            bottom_axes = Axes(x_range=[2025, 2028, 1], y_range=[0, 100, 20]).move_to(
                LEFT * 3 + DOWN * 1
            )
            bottom_label = Text("Standard Model Correct", font_size=20).next_to(
                bottom_axes, UP
            )
            safe_position(bottom_label)
            top_points = [
                top_axes.coords_to_point(x, y)
                for x, y in [(2025, 40), (2026, 55), (2027, 70), (2028, 85)]
            ]
            top_line = VMobject().set_points_as_corners(top_points).set_stroke(RED, 3)

            bottom_axes = Axes(x_range=[2025, 2028, 1], y_range=[0, 100, 20]).move_to(
                LEFT * 3 + DOWN * 1
            )
            bottom_label = Text("Standard Model Correct", font_size=20).next_to(
                bottom_axes, UP
            )
            bottom_points = [
                bottom_axes.coords_to_point(x, y)
                for x, y in [(2025, 40), (2026, 42), (2027, 44), (2028, 46)]
            ]
            bottom_line = (
                VMobject().set_points_as_corners(bottom_points).set_stroke(BLUE, 3)
            )

            self.play(
                Create(top_axes),
                Create(bottom_axes),
                Write(top_label),
                Write(bottom_label),
                run_time=tracker.duration * 0.1,
            )
            self.play(
                Create(top_line), Create(bottom_line), run_time=tracker.duration * 0.1
            )

            # Clock/calendar
            clock = Text("2025 → 2026 → 2027 → 2028", font_size=24).move_to(
                RIGHT * 3 + UP * 1
            )
            safe_position(clock)
            self.play(Write(clock), run_time=tracker.duration * 0.1)

            # Window text
            window_text = Text(
                "Next 36 months: Decisive data window", font_size=22
            ).move_to(ORIGIN)
            safe_position(window_text)
            self.play(Write(window_text), run_time=tracker.duration * 0.1)

            # Gauges
            gauge1 = Rectangle(width=2, height=0.5, color=GREEN).move_to(
                RIGHT * 3 + DOWN * 1
            )
            label1 = Text("Ages 25-54 incidence", font_size=16).next_to(gauge1, DOWN)
            gauge2 = Rectangle(width=2, height=0.5, color=GREEN).next_to(
                gauge1, DOWN, buff=0.5
            )
            label2 = Text("Melanoma/Lymphoma rates", font_size=16).next_to(gauge2, DOWN)
            gauge3 = Rectangle(width=2, height=0.5, color=GREEN).next_to(
                gauge2, DOWN, buff=0.5
            )
            label3 = Text("Treatment expenditure trajectory", font_size=16).next_to(
                gauge3, DOWN
            )
            safe_position(label1)
            safe_position(label2)
            safe_position(label3)

            self.play(
                Create(gauge1),
                Create(gauge2),
                Create(gauge3),
                Write(label1),
                Write(label2),
                Write(label3),
                run_time=tracker.duration * 0.2,
            )

            # Pulse
            self.play(
                gauge1.animate.set_color(YELLOW),
                gauge2.animate.set_color(YELLOW),
                gauge3.animate.set_color(YELLOW),
                run_time=tracker.duration * 0.1,
            )

            # Final
            final_text = Text("Either way, we'll know.", font_size=28).move_to(DOWN * 3)
            safe_position(final_text)
            self.play(Write(final_text), run_time=tracker.duration * 0.1)
            self.wait(tracker.duration * 0.1)