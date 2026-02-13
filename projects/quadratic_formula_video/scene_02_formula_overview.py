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


class Scene02FormulaOverview(VoiceoverScene):
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

        with self.voiceover(text=SCRIPT["formula"]) as tracker:
            title = Text("The Quadratic Formula", font_size=54, weight=BOLD)
            title.move_to(UP * 3.8)
            self.play(Write(title), run_time=tracker.duration * 0.2)

            equation = MathTex(r"ax^2 + bx + c = 0", font_size=56)
            equation.move_to(UP * 1.5)
            self.play(Write(equation), run_time=tracker.duration * 0.25)

            formula = MathTex(
                r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}",
                font_size=60,
            )
            formula.move_to(DOWN * 0.8)
            self.play(Write(formula), run_time=tracker.duration * 0.45)

            caption = Text("Works for any quadratic", font_size=32, color=YELLOW)
            caption.next_to(formula, DOWN, buff=0.5)
            safe_position(caption)
            self.play(FadeIn(caption), run_time=tracker.duration * 0.1)
