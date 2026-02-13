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


class Scene04Example(VoiceoverScene):
    def construct(self):
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        with self.voiceover(text=SCRIPT["example"]) as tracker:
            title = Text("Worked Example", font_size=52, weight=BOLD)
            title.move_to(UP * 3.8)
            self.play(Write(title), run_time=tracker.duration * 0.12)

            equation = MathTex(r"x^2 - 5x + 6 = 0", font_size=58)
            equation.move_to(UP * 2.2)
            self.play(Write(equation), run_time=tracker.duration * 0.1)

            coeffs = Text("a = 1   b = -5   c = 6", font_size=34, color=YELLOW)
            coeffs.next_to(equation, DOWN, buff=0.5)
            safe_position(coeffs)
            self.play(FadeIn(coeffs), run_time=tracker.duration * 0.08)

            formula = MathTex(
                r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}",
                font_size=52,
            )
            formula.move_to(DOWN * 0.3)
            self.play(Write(formula), run_time=tracker.duration * 0.12)

            substituted = MathTex(
                r"x = \frac{-(-5) \pm \sqrt{(-5)^2 - 4(1)(6)}}{2(1)}",
                font_size=46,
            )
            substituted.move_to(DOWN * 1.0)
            safe_position(substituted)
            self.play(
                TransformFromCopy(formula, substituted),
                run_time=tracker.duration * 0.12,
            )

            discriminant = MathTex(
                r"b^2 - 4ac = 25 - 24 = 1", font_size=46, color=ORANGE
            )
            discriminant.move_to(DOWN * 3.1)
            self.play(Write(discriminant), run_time=tracker.duration * 0.1)

            self.play(
                FadeOut(formula),
                FadeOut(substituted),
                FadeOut(discriminant),
                FadeOut(coeffs),
                run_time=tracker.duration * 0.06,
            )

            split_left = MathTex(r"x = \frac{5 + 1}{2} = 3", font_size=54, color=GREEN)
            split_right = MathTex(r"x = \frac{5 - 1}{2} = 2", font_size=54, color=BLUE)
            split_left.move_to(LEFT * 3.5 + DOWN * 0.6)
            split_right.move_to(RIGHT * 3.5 + DOWN * 0.6)
            safe_layout(split_left, split_right)
            self.play(
                FadeIn(split_left),
                FadeIn(split_right),
                run_time=tracker.duration * 0.12,
            )

            check_left = MathTex(r"3^2 - 5(3) + 6 = 0", font_size=40)
            check_right = MathTex(r"2^2 - 5(2) + 6 = 0", font_size=40)
            check_left.next_to(split_left, DOWN, buff=0.4)
            safe_position(check_left)
            check_right.next_to(split_right, DOWN, buff=0.4)
            safe_position(check_right)
            safe_layout(check_left, check_right)
            self.play(
                FadeIn(check_left),
                FadeIn(check_right),
                run_time=tracker.duration * 0.08,
            )