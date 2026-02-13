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
class Scene03Computation(VoiceoverScene):
    def construct(self):
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # Animation Sequence
        # Timing budget: 0.1 + 0.15 + 0.1 + 0.35 + 0.2 + 0.1 = 1.0 ✓
        with self.voiceover(text=SCRIPT["computation"]) as tracker:
            # Title
            title = Text("Step-by-Step Computation", font_size=48, weight=BOLD)
            title.move_to(UP * 3.8)
            play_text_in_slot(self, Write(title), tracker.duration * 0.1)

            # Show matrices A and B
            A_label = MathTex(r"A =", font_size=36)
            A_mat = Matrix(
                [["1", "2", "3"], ["4", "5", "6"]],
                v_buff=0.9,
                h_buff=1.0,
            )
            A_group = VGroup(A_label, A_mat).arrange(RIGHT, buff=0.3)
            A_group.move_to(LEFT * 3 + UP * 0.6)
            safe_position(A_group)

            B_label = MathTex(r"B =", font_size=36)
            B_mat = Matrix(
                [["4", "7"], ["1", "8"], ["2", "9"]],
                v_buff=0.9,
                h_buff=1.0,
            )
            B_group = VGroup(B_label, B_mat).arrange(RIGHT, buff=0.3)
            B_group.move_to(RIGHT * 3 + UP * 0.6)
            safe_position(B_group)

            play_in_slot(self, FadeIn(A_group, B_group), tracker.duration * 0.15)

            # Result matrix placeholder
            C_label = MathTex(r"C = A\times B =", font_size=36)
            C_mat = Matrix([["?", "?"], ["?", "?"]], v_buff=0.9, h_buff=1.0)
            C_group = VGroup(C_label, C_mat).arrange(RIGHT, buff=0.3)
            C_group.move_to(DOWN * 1.6)
            safe_position(C_group)
            play_in_slot(self, FadeIn(C_group), tracker.duration * 0.1)

            # Cell (1,1)
            slot_cell_11 = tracker.duration * 0.35
            a_row0 = A_mat.get_rows()[0]
            b_col0 = VGroup(
                B_mat.get_entries()[0], B_mat.get_entries()[2], B_mat.get_entries()[4]
            )
            row_highlight = SurroundingRectangle(a_row0, color=BLUE, buff=0.1)
            col_highlight = SurroundingRectangle(b_col0, color=RED, buff=0.1)
            calc = MathTex(r"1\cdot 4 + 2\cdot 1 + 3\cdot 2 = 12", font_size=36)
            calc.next_to(C_group, DOWN, buff=0.35)
            safe_position(calc)

            self.play(
                Create(row_highlight),
                Create(col_highlight),
                run_time=slot_cell_11 * 0.25,
            )
            self.play(FadeIn(calc), run_time=slot_cell_11 * 0.35)

            c_entries = C_mat.get_entries()
            self.play(
                Transform(
                    c_entries[0],
                    MathTex("12", font_size=36).move_to(c_entries[0].get_center()),
                ),
                run_time=slot_cell_11 * 0.25,
            )
            self.wait(
                max(
                    0.0,
                    slot_cell_11
                    - (slot_cell_11 * 0.25 + slot_cell_11 * 0.35 + slot_cell_11 * 0.25),
                )
            )

            # Cell (1,2)
            slot_cell_12 = tracker.duration * 0.2
            b_col1 = VGroup(
                B_mat.get_entries()[1], B_mat.get_entries()[3], B_mat.get_entries()[5]
            )
            col_highlight_2 = SurroundingRectangle(b_col1, color=RED, buff=0.1)
            calc_2 = MathTex(r"1\cdot 7 + 2\cdot 8 + 3\cdot 9 = 50", font_size=36)
            calc_2.move_to(calc)
            self.play(
                Transform(col_highlight, col_highlight_2), run_time=slot_cell_12 * 0.35
            )
            self.play(Transform(calc, calc_2), run_time=slot_cell_12 * 0.35)
            self.play(
                Transform(
                    c_entries[1],
                    MathTex("50", font_size=36).move_to(c_entries[1].get_center()),
                ),
                run_time=slot_cell_12 * 0.3,
            )

            # Finish remaining entries quickly, reinforcing "same rule" (no indexing hacks)
            slot_finish = tracker.duration * 0.1
            self.play(
                FadeOut(row_highlight),
                FadeOut(col_highlight),
                run_time=slot_finish * 0.3,
            )
            self.play(
                Transform(
                    c_entries[2],
                    MathTex("33", font_size=36).move_to(c_entries[2].get_center()),
                ),
                Transform(
                    c_entries[3],
                    MathTex("122", font_size=36).move_to(c_entries[3].get_center()),
                ),
                run_time=slot_finish * 0.7,
            )