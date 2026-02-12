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
class Scene04CumulativeBurden(VoiceoverScene):
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
        # Timing budget: 0.2 + 0.2 + 0.08*5 + 0.05 + 0.05 + 0.1 = 1.0 ✓

        with self.voiceover(text=SCRIPT["cumulative_burden"]) as tracker:
            # Equation
            equation = MathTex(
                r"(Cumulative Burden) \times (Current Cancer Rate) > 2.5 \times (Historical Ceiling)",
                font_size=32,
            )
            equation.move_to(UP * 2)
            self.play(Write(equation), run_time=tracker.duration * 0.2)

            # Gauge
            gauge_bg = Rectangle(width=6, height=0.5, color=WHITE).move_to(ORIGIN)
            gauge_fill = Rectangle(width=0, height=0.5, color=GREEN).move_to(
                gauge_bg.get_left()
            )
            gauge_needle = Line(start=ORIGIN, end=UP * 0.5, color=RED).move_to(
                gauge_bg.get_left()
            )
            threshold_mark = Line(start=DOWN * 0.3, end=UP * 0.3, color=YELLOW).move_to(
                gauge_bg.get_left() + RIGHT * 3.75
            )  # 2.5/2.5 *3 = wait, width 6, so 2.5x at 3.75
            threshold_text = Text("2.5x Threshold", font_size=20).next_to(
                threshold_mark, UP
            )
            safe_position(threshold_text)
            self.play(
                Create(gauge_bg),
                Create(threshold_mark),
                Write(threshold_text),
                run_time=tracker.duration * 0.2,
            )

            # Needle movement
            years = [2019, 2020, 2021, 2022, 2023, 2024]
            positions = [0, 0.5, 1.5, 2.1, 2.8, 3.2]  # scaled
            previous_year_text = None
            for year, pos in zip(years[1:], positions[1:]):
                year_text = Text(str(year), font_size=24).next_to(gauge_bg, DOWN)
                safe_position(year_text)
                animations = [
                    gauge_needle.animate.move_to(gauge_bg.get_left() + RIGHT * pos),
                    gauge_fill.animate.set_width(pos * 2),
                    Write(year_text),
                ]
                if previous_year_text:
                    animations.append(FadeOut(previous_year_text))
                self.play(*animations, run_time=tracker.duration * 0.08)
                previous_year_text = year_text

            # Cross threshold
            self.play(
                gauge_needle.animate.move_to(gauge_bg.get_left() + RIGHT * 4),
                gauge_fill.animate.set_width(4),
                gauge_fill.animate.set_color(RED),
                run_time=tracker.duration * 0.05,
            )

            # Regime shift
            regime_text = Text(
                "Self-sustaining regime", font_size=28, color=RED
            ).move_to(DOWN * 2)
            safe_position(regime_text)
            self.play(Write(regime_text), run_time=tracker.duration * 0.05)
            self.wait(tracker.duration * 0.1)
