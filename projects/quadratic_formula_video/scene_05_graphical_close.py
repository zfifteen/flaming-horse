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


class Scene05GraphicalClose(VoiceoverScene):
    def construct(self):
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        with self.voiceover(text=SCRIPT["closing"]) as tracker:
            title = Text("Solutions = X-Intercepts", font_size=52, weight=BOLD)
            title.move_to(UP * 3.8)
            self.play(Write(title), run_time=tracker.duration * 0.2)

            axes = Axes(
                x_range=[-1, 6, 1],
                y_range=[-1, 7, 1],
                x_length=8.5,
                y_length=4.2,
                tips=False,
            )
            axes.shift(DOWN * 0.8)
            parabola = axes.plot(lambda x: x**2 - 5 * x + 6, color=BLUE)
            self.play(Create(axes), Create(parabola), run_time=tracker.duration * 0.35)

            dot_left = Dot(axes.c2p(2, 0, 0), color=YELLOW)
            dot_right = Dot(axes.c2p(3, 0, 0), color=YELLOW)
            label_left = MathTex(r"x=2", font_size=42, color=YELLOW)
            label_right = MathTex(r"x=3", font_size=42, color=YELLOW)
            label_left.next_to(dot_left, DOWN, buff=0.3)
            safe_position(label_left)
            label_right.next_to(dot_right, DOWN, buff=0.3)
            safe_position(label_right)
            safe_layout(label_left, label_right)
            self.play(
                FadeIn(dot_left),
                FadeIn(dot_right),
                FadeIn(label_left),
                FadeIn(label_right),
                run_time=tracker.duration * 0.35,
            )

            caption = Text("Two real roots", font_size=32, color=GREEN)
            caption.move_to(DOWN * 3.4)
            self.play(FadeIn(caption), run_time=tracker.duration * 0.1)