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
    """Ensure multiple mobjects don't overlap and stay within safe bounds."""
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


# Timing Helpers
def play_in_slot(
    scene, animation, slot, *, max_run_time=None, min_run_time=0.3, **play_kwargs
):
    """Play an animation, then wait to fill the remaining slot time.

    Args:
        scene: The Manim scene (typically `self`)
        animation: A Manim Animation instance (e.g., Write(title))
        slot: Total time budget for this beat (seconds)
        max_run_time: Optional cap for the animation portion (seconds)
        min_run_time: Minimum perceptible animation time (seconds)
        **play_kwargs: Passed to scene.play(...)
    """
    slot = float(slot)
    if slot <= 0:
        return

    run_time = slot
    if max_run_time is not None:
        run_time = min(run_time, float(max_run_time))
    run_time = max(float(min_run_time), run_time)
    run_time = min(run_time, slot)

    scene.play(animation, run_time=run_time, **play_kwargs)
    remaining = slot - run_time
    if remaining > 1e-6:
        scene.wait(remaining)


def play_text_in_slot(
    scene, animation, slot, *, max_text_seconds=2.0, min_run_time=0.3, **play_kwargs
):
    """Text animations must complete quickly; fill the rest with waits."""
    return play_in_slot(
        scene,
        animation,
        slot,
        max_run_time=max_text_seconds,
        min_run_time=min_run_time,
        **play_kwargs,
    )


# Scene Class
class Scene06Recap(VoiceoverScene):
    def construct(self):
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # Animation Sequence
        # Timing budget: Calculate BEFORE writing animations
        # 0.2 + 0.2 + 0.2 + 0.2 + 0.2 = 1.0 ✓
        with self.voiceover(text=SCRIPT["recap"]) as tracker:
            # Title
            title = Text("Summary and Key Takeaways", font_size=48, weight=BOLD)
            title.move_to(UP * 3.8)
            play_text_in_slot(self, Write(title), tracker.duration * 0.2)

            # Key formula highlight
            formula = MathTex(
                r"C_{ij} = \sum_{k} A_{ik} B_{kj}", font_size=48, color=GOLD
            )
            formula.next_to(title, DOWN, buff=0.8)
            safe_position(formula)
            play_text_in_slot(self, Write(formula), tracker.duration * 0.2)

            # Dimensional requirements
            dims = Text("Rows(A) × Columns(B)", font_size=32, color=BLUE)
            dims.next_to(formula, DOWN, buff=0.5)
            safe_position(dims)
            play_text_in_slot(self, FadeIn(dims), tracker.duration * 0.2)

            # Geometric interpretation
            geom = Text("Linear Transformations", font_size=32, color=GREEN)
            geom.next_to(dims, DOWN, buff=0.5)
            safe_position(geom)
            play_text_in_slot(self, FadeIn(geom), tracker.duration * 0.2)

            # Final transformation demo
            # Remove the recap bullets before introducing the final demo,
            # so we don't end up with overlapping layers of text/matrices.
            play_in_slot(
                self,
                FadeOut(VGroup(formula, dims, geom)),
                tracker.duration * 0.05,
                min_run_time=0.3,
            )

            matrix_a = Matrix([["1", "2"], ["3", "4"]], v_buff=0.8, h_buff=1.0)
            matrix_a.scale(0.8).move_to(LEFT * 3)
            arrow = MathTex(r"\times", font_size=36).next_to(matrix_a, RIGHT, buff=0.5)
            matrix_b = Matrix([["5", "6"], ["7", "8"]], v_buff=0.8, h_buff=1.0)
            matrix_b.scale(0.8).next_to(arrow, RIGHT, buff=0.5)
            equals = MathTex(r"=", font_size=36).next_to(matrix_b, RIGHT, buff=0.5)
            matrix_c = Matrix([["19", "22"], ["43", "50"]], v_buff=0.8, h_buff=1.0)
            matrix_c.scale(0.8).next_to(equals, RIGHT, buff=0.5)

            demo_group = VGroup(matrix_a, arrow, matrix_b, equals, matrix_c)
            demo_group.move_to(ORIGIN)
            safe_position(demo_group)
            play_in_slot(self, FadeIn(demo_group), tracker.duration * 0.2)