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
class Scene03FundamentalTheorem(VoiceoverScene):
    def construct(self):
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # ── Animation Sequence ─────────────────────────────────────
        # Timing budget: 0.20 + 0.25 + 0.25 + 0.05 + 0.15 + 0.10 = 1.00

        with self.voiceover(text=SCRIPT["fundamental_theorem"]) as tracker:
            # ── Stage A: Title (0.20) ─────────────────────────────
            title = Text(
                "Fundamental Theorem of Algebra",
                font_size=44,
                color=GOLD,
                weight=BOLD,
            )
            title.move_to(UP * 3.8)

            self.play(Write(title), run_time=2)

            # ── Stage B: Polynomial (0.25) ────────────────────────
            poly = MathTex(
                "P(z) = z^{4} + z^{3} - z^{2} + z - 1",
                font_size=42,
                color=WHITE,
            )
            poly.move_to(UP * 2)

            self.play(Write(poly), run_time=2)

            # ── Stage C: Complex Plane with Roots (0.25) ──────────
            plane = NumberPlane(
                x_range=(-2, 2, 0.5),
                y_range=(-2, 2, 0.5),
                x_length=6,
                y_length=6,
                background_line_style={
                    "stroke_color": GRAY,
                    "stroke_width": 1,
                    "stroke_opacity": 0.3,
                },
                faded_line_style={
                    "stroke_color": GRAY,
                    "stroke_width": 0.5,
                    "stroke_opacity": 0.15,
                },
            )
            plane.move_to(DOWN * 1.2)

            # Roots (approximate for the polynomial)
            root_positions = [
                (1.17, 0),
                (-0.18, 1.09),
                (-0.18, -1.09),
                (-0.81, 0),
            ]
            root_dots = VGroup()
            root_labels = VGroup()
            root_colors = [GREEN, TEAL, TEAL, GREEN]

            for i, (rx, ry) in enumerate(root_positions):
                dot = Dot(
                    plane.c2p(rx, ry),
                    color=root_colors[i],
                    radius=0.1,
                )
                root_dots.add(dot)
                label = MathTex(
                    f"z_{{{i + 1}}}",
                    font_size=24,
                    color=root_colors[i],
                )
                label.next_to(dot, UR, buff=0.15)
                root_labels.add(label)

            plane_group = VGroup(plane, root_dots, root_labels)

            self.play(
                FadeIn(plane),
                run_time=tracker.duration * 0.10,
            )
            self.play(
                *[FadeIn(dot, scale=0.5) for dot in root_dots],
                *[FadeIn(label) for label in root_labels],
                run_time=tracker.duration * 0.15,
            )

            # ── Stage D: Fade Polynomial (0.05) ──────────────────
            self.play(
                FadeOut(poly),
                run_time=tracker.duration * 0.05,
            )

            # ── Stage E: Universal Language (0.15) ────────────────
            universal = Text(
                "A Universal Language",
                font_size=40,
                color=BLUE,
                weight=BOLD,
            )
            universal.move_to(UP * 2)

            # Glow the root dots
            self.play(
                Write(universal),
                *[dot.animate.scale(1.5).set_color(YELLOW) for dot in root_dots],
                run_time=2,
            )

            # ── Stage F: Hold (0.10) ─────────────────────────────
            self.wait(tracker.duration * 0.10)