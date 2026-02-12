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
class Scene02StandardModelFails(VoiceoverScene):
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
        # Timing budget: Axes 0.1, Catch-up 0.15, Expected 0.1, Actual 0.1, Divergence 0.1, Fade 0.1, Pulse 0.1, Treatment 0.15 = 1.0

        with self.voiceover(text=SCRIPT["standard_fails"]) as tracker:
            # Graph axes
            axes = (
                Axes(
                    x_range=[2015, 2030, 5],
                    y_range=[0, 100, 20],
                    axis_config={"color": WHITE},
                )
                .scale(0.8)
                .move_to(ORIGIN)
            )
            x_label = Text("Year", font_size=20).next_to(axes.x_axis, DOWN)
            safe_position(x_label)
            y_label = Text("Incidence", font_size=20).next_to(axes.y_axis, LEFT)
            safe_position(y_label)
            self.play(
                Create(axes),
                Write(x_label),
                Write(y_label),
                run_time=tracker.duration * 0.1,
            )

            # Catch-up model line
            catch_up_points = [
                axes.coords_to_point(x, y)
                for x, y in [(2015, 20), (2020, 30), (2021, 60), (2025, 40), (2030, 25)]
            ]
            catch_up_line = (
                VMobject().set_points_as_corners(catch_up_points).set_stroke(BLUE, 3)
            )
            catch_up_label = Text("CATCH-UP MODEL", font_size=24).move_to(UP * 3.8)
            self.play(
                Create(catch_up_line),
                Write(catch_up_label),
                run_time=tracker.duration * 0.15,
            )

            # Expected label
            expected_label = Text("Expected return to baseline", font_size=20).next_to(
                catch_up_line, RIGHT, buff=1
            )
            safe_position(expected_label)
            self.play(Write(expected_label), run_time=tracker.duration * 0.1)

            # Actual data line
            actual_points = [
                axes.coords_to_point(x, y)
                for x, y in [(2015, 20), (2020, 30), (2021, 60), (2025, 75), (2030, 90)]
            ]
            actual_line = (
                VMobject().set_points_as_corners(actual_points).set_stroke(RED, 3)
            )
            actual_label = Text("ACTUAL DATA", font_size=24).next_to(
                catch_up_label, RIGHT
            )
            safe_position(actual_label)
            self.play(
                Create(actual_line),
                Write(actual_label),
                run_time=tracker.duration * 0.1,
            )

            # Divergence
            self.wait(tracker.duration * 0.1)

            # Fade catch-up
            self.play(
                catch_up_line.animate.set_opacity(0.3),
                catch_up_label.animate.set_opacity(0.3),
                expected_label.animate.set_opacity(0.3),
                run_time=tracker.duration * 0.1,
            )

            # Pulse actual and acceleration
            acceleration_text = Text(
                "ACCELERATION", font_size=32, color=YELLOW
            ).next_to(actual_line, UP)
            safe_position(acceleration_text)
            self.play(
                actual_line.animate.set_stroke(width=8),
                Write(acceleration_text),
                run_time=tracker.duration * 0.1,
            )

            # Treatment expenditure
            treatment_points = [
                axes.coords_to_point(x, y)
                for x, y in [(2015, 10), (2020, 20), (2021, 35), (2025, 50), (2030, 65)]
            ]
            treatment_line = (
                VMobject().set_points_as_corners(treatment_points).set_stroke(GREEN, 3)
            )
            treatment_label = Text("Treatment Expenditure", font_size=20).next_to(
                treatment_line, RIGHT
            )
            safe_position(treatment_label)
            self.play(
                Create(treatment_line),
                Write(treatment_label),
                run_time=tracker.duration * 0.15,
            )
