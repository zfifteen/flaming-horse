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
    # First apply vertical bounds to all elements
    for mob in mobjects:
        top = mob.get_top()[1]
        bottom = mob.get_bottom()[1]
        if top > max_y:
            mob.shift(DOWN * (top - max_y))
        elif bottom < min_y:
            mob.shift(UP * (min_y - bottom))

    # Check horizontal overlap between all pairs
    for i, mob_a in enumerate(mobjects):
        for mob_b in mobjects[i + 1 :]:
            a_left = mob_a.get_left()[0]
            a_right = mob_a.get_right()[0]
            b_left = mob_b.get_left()[0]
            b_right = mob_b.get_right()[0]

            # If bounding boxes overlap on x-axis
            if not (a_right < b_left or b_right < a_left):
                # Shift the second element right
                overlap = (a_right - b_left) if a_right > b_left else (b_right - a_left)
                mob_b.shift(RIGHT * (overlap + min_horizontal_spacing))

    return list(mobjects)


# Scene Class
class Scene03Proof(VoiceoverScene):
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
        # Timing budget: 0.2 + 0.2 + 0.3 + 0.2 + 0.1 = 1.0

        with self.voiceover(text=SCRIPT["proof"]) as tracker:
            # Title
            title = Text("Visual Proof", font_size=48, weight=BOLD)
            title.move_to(UP * 3.8)
            self.play(Write(title), run_time=tracker.duration * 0.2)

            # Triangle
            triangle = Polygon(
                np.array([0, 0, 0]),
                np.array([3, 0, 0]),
                np.array([0, 4, 0]),
                color=BLUE,
            )
            triangle.move_to(ORIGIN)
            self.play(Create(triangle), run_time=tracker.duration * 0.2)

            # Squares
            square_a = Square(side_length=3, color=RED).next_to(
                triangle, DOWN, buff=0.5
            )
            square_b = Square(side_length=4, color=GREEN).next_to(
                triangle, LEFT, buff=0.5
            )
            square_c = Square(side_length=5, color=YELLOW).move_to(
                triangle.get_center() + np.array([2, 2, 0])
            )

            safe_layout(square_a, square_b, square_c)
            self.play(
                Create(square_a),
                Create(square_b),
                Create(square_c),
                run_time=tracker.duration * 0.3,
            )

            # Area texts
            area_a = Text("3² = 9", font_size=32).next_to(square_a, DOWN, buff=0.1)
            area_b = Text("4² = 16", font_size=32).next_to(square_b, DOWN, buff=0.1)
            area_c = Text("5² = 25", font_size=32).next_to(square_c, DOWN, buff=0.1)

            safe_layout(area_a, area_b, area_c)
            self.play(
                Write(area_a),
                Write(area_b),
                Write(area_c),
                run_time=tracker.duration * 0.2,
            )

            self.wait(tracker.duration * 0.1)
