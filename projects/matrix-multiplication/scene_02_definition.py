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
from manim_voiceover_plus.services.elevenlabs import ElevenLabsService
from elevenlabs import VoiceSettings

# Import Shared Configuration
from voice_config import VOICE_ID, MODEL_ID, VOICE_SETTINGS
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
class Scene02Definition(VoiceoverScene):
    def construct(self):
        # ELEVENLABS ONLY - NO FALLBACK - FAIL LOUD
        self.set_speech_service(
            ElevenLabsService(
                voice_id=VOICE_ID,
                model_id=MODEL_ID,
                voice_settings=VOICE_SETTINGS,
                transcription_model=None,
            )
        )

        # Animation Sequence
        # Timing budget: 0.3 + 0.2 + 0.3 + 0.2 = 1.0 ✓
        with self.voiceover(text=SCRIPT["definition"]) as tracker:
            # Slot 1: Show matrices A and B with dimensions (30%)
            slot1 = tracker.duration * 0.3
            matrix_A = Matrix([["a", "b"], ["c", "d"]], v_buff=0.8, h_buff=1.0)
            matrix_A_label = MathTex("A", font_size=48).next_to(matrix_A, LEFT)
            safe_position(matrix_A_label)
            A_group = VGroup(matrix_A_label, matrix_A)
            # Keep matrices comfortably separated so braces/labels don't collide
            A_group.move_to(LEFT * 3.8 + UP * 1.2)
            matrix_B = Matrix(
                [["e", "f", "g"], ["h", "i", "j"]], v_buff=0.8, h_buff=1.0
            )
            matrix_B_label = MathTex("B", font_size=48).next_to(matrix_B, LEFT)
            safe_position(matrix_B_label)
            B_group = VGroup(matrix_B_label, matrix_B)
            B_group.move_to(RIGHT * 3.4 + UP * 1.2)
            dim_A = Text("2×2", font_size=24).next_to(A_group, DOWN, buff=0.2)
            safe_position(dim_A)
            dim_B = Text("2×3", font_size=24).next_to(B_group, DOWN, buff=0.2)
            safe_position(dim_B)
            play_text_in_slot(self, FadeIn(VGroup(A_group, dim_A)), slot1 * 0.5)
            play_text_in_slot(self, FadeIn(VGroup(B_group, dim_B)), slot1 * 0.5)

            # Slot 2: Highlight dimensions compatibility (20%)
            slot2 = tracker.duration * 0.2

            # Clear the dimension labels before braces to avoid stacking text
            # under the matrices.
            transition = slot2 * 0.25
            remainder = slot2 - transition
            play_in_slot(self, FadeOut(VGroup(dim_A, dim_B)), transition)

            col_brace_A = Brace(matrix_A, direction=DOWN, buff=0.1)
            safe_position(col_brace_A)
            col_text_A = Text("2 columns", font_size=24)
            col_text_A.next_to(col_brace_A, DOWN, buff=0.15)
            safe_position(col_text_A)

            # Put the row brace on the OUTER side to avoid colliding with the B label
            row_brace_B = Brace(matrix_B, direction=RIGHT, buff=0.1)
            safe_position(row_brace_B)
            row_text_B = Text("2 rows", font_size=24)
            row_text_B.next_to(row_brace_B, RIGHT, buff=0.15)
            safe_position(row_text_B)
            play_text_in_slot(
                self,
                AnimationGroup(
                    Create(col_brace_A),
                    FadeIn(col_text_A),
                    Create(row_brace_B),
                    FadeIn(row_text_B),
                    lag_ratio=0.1,
                ),
                remainder,
            )

            # Slot 3: Highlight row and column for dot product (30%)
            slot3 = tracker.duration * 0.3
            row_highlight = SurroundingRectangle(
                matrix_A.get_rows()[0], color=YELLOW, buff=0.1
            )
            col_entries = VGroup(
                matrix_B.get_entries()[0], matrix_B.get_entries()[3]
            )  # e and h
            col_highlight = SurroundingRectangle(col_entries, color=YELLOW, buff=0.1)
            play_text_in_slot(
                self,
                AnimationGroup(Create(row_highlight), Create(col_highlight)),
                slot3,
            )

            # Slot 4: Show dot product calculation (20%)
            slot4 = tracker.duration * 0.2
            dot_prod = MathTex(r"a \cdot e + b \cdot h", font_size=36)
            dot_prod.move_to(DOWN * 1.5)
            play_text_in_slot(self, Write(dot_prod), slot4)
