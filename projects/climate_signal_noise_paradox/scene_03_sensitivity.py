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
class Scene03Sensitivity(VoiceoverScene):
    def construct(self):
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # ── Animation Sequence ─────────────────────────────────────
        # Timing budget: title 0.10 + scenario_a 0.30 + cross 0.10 + scenario_b 0.30 + highlight 0.10 + wait 0.10 = 1.0

        with self.voiceover(text=SCRIPT["sensitivity"]) as tracker:
            # Title
            title = Text(
                "Beyond Simple Sensitivity Tuning",
                font_size=44,
                weight=BOLD,
            )
            title.move_to(UP * 3.8)
            self.play(Write(title), run_time=tracker.duration * 0.10)

            # LEFT SIDE: "If ECS too high" scenario
            left_header = Text(
                "If ECS Too High", font_size=24, color=RED_B, weight=BOLD
            )
            left_header.move_to(LEFT * 4.2 + UP * 2.5)

            # Trend arrow (overpredicted)
            left_trend_label = Text("Forced Trend", font_size=18, color=WHITE)
            left_trend_label.move_to(LEFT * 4.2 + UP * 1.5)
            left_trend_arrow = Arrow(
                LEFT * 5.5 + UP * 0.8,
                LEFT * 2.9 + UP * 0.8,
                color=RED,
                stroke_width=6,
            )
            left_trend_text = Text("Overpredicted", font_size=16, color=RED)
            left_trend_text.next_to(left_trend_arrow, UP, buff=0.1)

            # Signal arrow (also overpredicted)
            left_signal_label = Text("Predictable Signal", font_size=18, color=WHITE)
            left_signal_label.move_to(LEFT * 4.2 + DOWN * 0.2)
            left_signal_arrow = Arrow(
                LEFT * 5.5 + DOWN * 0.8,
                LEFT * 2.9 + DOWN * 0.8,
                color=RED,
                stroke_width=6,
            )
            left_signal_text = Text("Also Overpredicted", font_size=16, color=RED)
            left_signal_text.next_to(left_signal_arrow, UP, buff=0.1)

            left_group = VGroup(
                left_header,
                left_trend_label,
                left_trend_arrow,
                left_trend_text,
                left_signal_label,
                left_signal_arrow,
                left_signal_text,
            )

            # Divider
            divider = DashedLine(UP * 3.0, DOWN * 3.5, color=GRAY, dash_length=0.15)
            divider.move_to(ORIGIN)

            self.play(
                FadeIn(left_group, shift=RIGHT * 0.3),
                Create(divider),
                run_time=tracker.duration * 0.30,
            )

            # Cross out left scenario
            cross = Cross(left_group, stroke_color=RED, stroke_width=6)
            wrong_label = Text("NOT what we see", font_size=20, color=RED, weight=BOLD)
            wrong_label.move_to(LEFT * 4.2 + DOWN * 2.2)
            safe_position(wrong_label)

            self.play(
                Create(cross),
                Write(wrong_label),
                run_time=tracker.duration * 0.10,
            )

            # RIGHT SIDE: What actually happens
            right_header = Text(
                "What Actually Happens", font_size=24, color=GREEN_B, weight=BOLD
            )
            right_header.move_to(RIGHT * 4.2 + UP * 2.5)

            right_trend_label = Text("Forced Trend", font_size=18, color=WHITE)
            right_trend_label.move_to(RIGHT * 4.2 + UP * 1.5)
            right_trend_arrow = Arrow(
                RIGHT * 2.9 + UP * 0.8,
                RIGHT * 5.5 + UP * 0.8,
                color=RED,
                stroke_width=6,
            )
            right_trend_text = Text("Overpredicted", font_size=16, color=RED)
            right_trend_text.next_to(right_trend_arrow, UP, buff=0.1)

            right_signal_label = Text("Predictable Signal", font_size=18, color=WHITE)
            right_signal_label.move_to(RIGHT * 4.2 + DOWN * 0.2)
            right_signal_arrow = Arrow(
                RIGHT * 2.9 + DOWN * 0.8,
                RIGHT * 3.8 + DOWN * 0.8,
                color=GREEN,
                stroke_width=6,
            )
            right_signal_text = Text("Underpredicted ~3x", font_size=16, color=GREEN)
            right_signal_text.next_to(right_signal_arrow, UP, buff=0.1)

            right_group = VGroup(
                right_header,
                right_trend_label,
                right_trend_arrow,
                right_trend_text,
                right_signal_label,
                right_signal_arrow,
                right_signal_text,
            )

            check = Text("This IS what we see", font_size=20, color=GREEN, weight=BOLD)
            check.move_to(RIGHT * 4.2 + DOWN * 2.2)
            safe_position(check)

            self.play(
                FadeIn(right_group, shift=LEFT * 0.3),
                Write(check),
                run_time=tracker.duration * 0.30,
            )

            # Highlight the asymmetry
            highlight_box = SurroundingRectangle(
                VGroup(right_signal_arrow, right_signal_text),
                color=YELLOW,
                buff=0.2,
            )
            self.play(Create(highlight_box), run_time=tracker.duration * 0.10)

            self.wait(tracker.duration * 0.10)