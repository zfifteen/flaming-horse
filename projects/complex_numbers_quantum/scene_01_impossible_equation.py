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
from manim_voiceover_plus.services.elevenlabs import ElevenLabsService
from elevenlabs import VoiceSettings

# ── Import Shared Configuration ────────────────────────────────────
from voice_config import VOICE_ID, MODEL_ID, VOICE_SETTINGS
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
class Scene01ImpossibleEquation(VoiceoverScene):
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

        # ── Animation Sequence ─────────────────────────────────────
        # Timing budget: 0.20 + 0.20 + 0.10 + 0.05 + 0.20 + 0.05 + 0.15 + 0.05 = 1.00

        with self.voiceover(text=SCRIPT["impossible_equation"]) as tracker:
            # ── Stage A: The Equation (0.20) ───────────────────────
            equation = MathTex("x^{2} + 1 = 0", font_size=72, color=WHITE)
            equation.move_to(UP * 1)

            self.play(Write(equation), run_time=2)

            # ── Stage B: Number Line with Failed Attempts (0.20) ──
            number_line = NumberLine(
                x_range=(-3, 3, 1),
                length=8,
                include_numbers=True,
                include_tip=True,
                label_direction=DOWN,
                color=BLUE,
            )
            number_line.move_to(DOWN * 1.5)

            attempt_dots = VGroup()
            for val in [-2, 1, 2]:
                dot = Dot(color=RED, radius=0.12)
                dot.move_to(number_line.n2p(val))
                attempt_dots.add(dot)

            cross_marks = VGroup()
            for dot in attempt_dots:
                cross = MathTex("\\times", font_size=36, color=RED)
                cross.next_to(dot, UP, buff=0.2)
                cross_marks.add(cross)

            stage_b = VGroup(number_line, attempt_dots, cross_marks)

            self.play(
                FadeIn(number_line),
                run_time=tracker.duration * 0.10,
            )
            self.play(
                *[FadeIn(dot, scale=0.5) for dot in attempt_dots],
                *[Write(cross) for cross in cross_marks],
                run_time=tracker.duration * 0.10,
            )

            # ── Stage C: Flash Equation Red (0.10) ────────────────
            self.play(
                equation.animate.set_color(RED),
                *[Flash(dot, color=RED, flash_radius=0.3) for dot in attempt_dots],
                run_time=tracker.duration * 0.10,
            )

            # ── Stage D: Fade Out Number Line (0.05) ──────────────
            self.play(
                FadeOut(stage_b),
                run_time=tracker.duration * 0.05,
            )

            # ── Stage E: Reveal i = sqrt(-1) (0.20) ──────────────
            equation_imag = MathTex("i = \\sqrt{-1}", font_size=60, color=GOLD)
            equation_imag.move_to(DOWN * 1)
            rectangle = SurroundingRectangle(equation_imag, color=GOLD, buff=0.25)

            self.play(
                equation.animate.set_color(WHITE),
                run_time=tracker.duration * 0.05,
            )
            self.play(
                Write(equation_imag),
                Create(rectangle),
                run_time=2,
            )

            # ── Stage F: Solution x = i (0.15) ────────────────────
            solution = MathTex("x = \\pm\\, i", font_size=54, color=GREEN)
            solution.move_to(DOWN * 2.8)
            safe_position(solution)

            self.play(
                equation.animate.set_color(GREEN),
                FadeIn(solution, shift=UP * 0.3),
                run_time=2,
            )

            # ── Stage G: Hold (0.05) ──────────────────────────────
            self.wait(tracker.duration * 0.05)
