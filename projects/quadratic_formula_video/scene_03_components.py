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


def safe_layout(*mobjects, min_horizontal_spacing=0.5, max_y=4.0, min_y=-4.0):
    """
    Ensure multiple mobjects don't overlap and stay within safe bounds.

    Call this on VGroups or multiple sibling elements after positioning.

    Args:
        *mobjects: Variable number of mobjects to validate
        min_horizontal_spacing: Minimum x-axis gap between elements (default 0.5)
        max_y: Maximum safe y-coordinate (default 4.0)
        min_y: Minimum safe y-coordinate (default -4.0)

    Returns:
        List of adjusted mobjects
    """
    for mob in mobjects:
        top = mob.get_top()[1]
        bottom = mob.get_bottom()[1]
        if top > max_y:
            mob.shift(DOWN * (top - max_y))
        elif bottom < min_y:
            mob.shift(UP * (min_y - bottom))

    for i, mob_a in enumerate(mobjects):
        for mob_b in mobjects[i + 1 :]:
            a_left = mob_a.get_left()[0]
            a_right = mob_a.get_right()[0]
            b_left = mob_b.get_left()[0]
            b_right = mob_b.get_right()[0]

            if not (a_right < b_left or b_right < a_left):
                overlap = (a_right - b_left) if a_right > b_left else (b_right - a_left)
                mob_b.shift(RIGHT * (overlap + min_horizontal_spacing))

    return list(mobjects)


class Scene03Components(VoiceoverScene):
    def construct(self):
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        with self.voiceover(text=SCRIPT["components"]) as tracker:
            title = Text("What Each Part Means", font_size=52, weight=BOLD)
            title.move_to(UP * 3.8)
            self.play(Write(title), run_time=tracker.duration * 0.18)

            equation = MathTex(r"ax^2 + bx + c = 0", font_size=58)
            equation.move_to(UP * 1.8)
            self.play(Write(equation), run_time=tracker.duration * 0.16)

            a_label = Text("a: coefficient of x^2", font_size=32, color=YELLOW)
            b_label = Text("b: coefficient of x", font_size=32, color=GREEN)
            c_label = Text("c: constant term", font_size=32, color=BLUE)

            a_label.move_to(LEFT * 4.9 + DOWN * 0.1)
            b_label.move_to(LEFT * 4.7 + DOWN * 1.1)
            c_label.move_to(LEFT * 4.6 + DOWN * 2.1)
            safe_layout(a_label, b_label, c_label)
            self.play(
                FadeIn(a_label),
                FadeIn(b_label),
                FadeIn(c_label),
                run_time=tracker.duration * 0.2,
            )

            formula = MathTex(r"b^2 - 4ac", font_size=58, color=ORANGE)
            formula.move_to(RIGHT * 3.8 + DOWN * 0.3)
            disc_label = Text("discriminant", font_size=32, color=ORANGE)
            disc_label.next_to(formula, DOWN, buff=0.4)
            safe_position(disc_label)
            self.play(Write(formula), run_time=tracker.duration * 0.16)
            self.play(FadeIn(disc_label), run_time=tracker.duration * 0.1)

            plus_label = Text("plus", font_size=32, color=TEAL)
            minus_label = Text("minus", font_size=32, color=TEAL)
            plus_label.move_to(RIGHT * 2.4 + DOWN * 2.7)
            minus_label.move_to(RIGHT * 4.9 + DOWN * 2.7)
            safe_layout(plus_label, minus_label)
            arc = CurvedArrow(
                plus_label.get_top() + UP * 0.2,
                minus_label.get_top() + UP * 0.2,
                angle=0.8,
            )

            self.play(
                FadeIn(plus_label),
                FadeIn(minus_label),
                Create(arc),
                run_time=tracker.duration * 0.2,
            )