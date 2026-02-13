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
class Scene02Paradox(VoiceoverScene):
    def construct(self):
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # ── Animation Sequence ─────────────────────────────────────
        # Timing budget: title 0.08 + axes 0.12 + bars 0.25 + labels 0.10 + factor 0.20 + conclusion 0.15 + wait 0.10 = 1.0

        with self.voiceover(text=SCRIPT["paradox"]) as tracker:
            # Title
            title = Text(
                "The Signal-to-Noise Paradox",
                font_size=44,
                weight=BOLD,
            )
            title.move_to(UP * 3.8)
            self.play(Write(title), run_time=tracker.duration * 0.08)

            # Bar chart axes
            ax = Axes(
                x_range=[0, 3, 1],
                y_range=[0, 1.0, 0.2],
                x_length=8,
                y_length=5,
                axis_config={"include_numbers": False, "include_tip": False},
            )
            ax.move_to(DOWN * 0.5)

            # Y-axis labels
            y_labels = VGroup()
            for val in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
                lbl = Text(f"{val:.1f}", font_size=16)
                lbl.next_to(ax.c2p(0, val), LEFT, buff=0.2)
                y_labels.add(lbl)

            y_title = Text("Correlation", font_size=20, color=WHITE)
            y_title.next_to(ax, LEFT, buff=0.6)
            y_title.rotate(90 * DEGREES)
            safe_position(y_title)

            self.play(
                Create(ax),
                FadeIn(y_labels),
                Write(y_title),
                run_time=tracker.duration * 0.12,
            )

            # Bar 1: Model-Observation correlation ~0.6 (left)
            bar1_height = 0.6
            bar1 = Rectangle(
                width=1.8,
                height=bar1_height * 5,  # scale to axis
                fill_color=GREEN,
                fill_opacity=0.8,
                stroke_color=WHITE,
                stroke_width=2,
            )
            bar1.move_to(ax.c2p(1, bar1_height / 2))

            bar1_label = Text("Model vs\nObservation", font_size=18, color=WHITE)
            bar1_label.next_to(bar1, DOWN, buff=0.2)
            safe_position(bar1_label)

            bar1_val = Text("~0.6", font_size=28, color=GREEN, weight=BOLD)
            bar1_val.next_to(bar1, UP, buff=0.15)
            safe_position(bar1_val)

            # Bar 2: Ensemble cross-correlation ~0.2 (right)
            bar2_height = 0.2
            bar2 = Rectangle(
                width=1.8,
                height=bar2_height * 5,
                fill_color=RED,
                fill_opacity=0.8,
                stroke_color=WHITE,
                stroke_width=2,
            )
            bar2.move_to(ax.c2p(2, bar2_height / 2))

            bar2_label = Text("Ensemble\nMembers", font_size=18, color=WHITE)
            bar2_label.next_to(bar2, DOWN, buff=0.2)
            safe_position(bar2_label)

            bar2_val = Text("~0.2", font_size=28, color=RED, weight=BOLD)
            bar2_val.next_to(bar2, UP, buff=0.15)
            safe_position(bar2_val)

            self.play(
                GrowFromEdge(bar1, DOWN),
                Write(bar1_val),
                run_time=tracker.duration * 0.125,
            )
            self.play(
                GrowFromEdge(bar2, DOWN),
                Write(bar2_val),
                run_time=tracker.duration * 0.125,
            )

            self.play(
                FadeIn(bar1_label),
                FadeIn(bar2_label),
                run_time=tracker.duration * 0.10,
            )

            # Factor of 3 highlight
            brace = Brace(VGroup(bar1, bar2), UP, color=YELLOW)
            factor_text = Text(
                "3x more predictable\nthan models expect",
                font_size=24,
                color=YELLOW,
                weight=BOLD,
            )
            factor_text.next_to(brace, UP, buff=0.2)
            safe_position(factor_text)

            # Animated arrow between bars
            compare_arrow = Arrow(
                bar1.get_right() + UP * 0.5,
                bar2.get_left() + UP * 0.5,
                color=YELLOW,
                stroke_width=4,
            )

            self.play(
                GrowFromCenter(brace),
                Write(factor_text),
                GrowArrow(compare_arrow),
                run_time=tracker.duration * 0.20,
            )

            # Conclusion line
            conclusion = Text(
                "Real atmosphere is far more predictable",
                font_size=22,
                color=BLUE_B,
            )
            conclusion.move_to(DOWN * 3.5)
            safe_position(conclusion)

            self.play(Write(conclusion), run_time=tracker.duration * 0.15)

            self.wait(tracker.duration * 0.10)