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
class Scene07PolicyImplication(VoiceoverScene):
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
        # Timing budget: 0.1 + 0.1 + 0.1 + 0.2 + 0.1 + 0.2 + 0.1 = 1.0 ✓

        with self.voiceover(text=SCRIPT["policy_implication"]) as tracker:
            # Gauge reappears
            gauge_bg = Rectangle(width=6, height=0.5, color=WHITE).move_to(ORIGIN)
            gauge_fill = Rectangle(width=4.8, height=0.5, color=RED).move_to(
                gauge_bg.get_left() + RIGHT * 2.4
            )
            gauge_needle = Line(start=ORIGIN, end=UP * 0.5, color=RED).move_to(
                gauge_bg.get_left() + RIGHT * 2.6
            )
            threshold_mark = Line(start=DOWN * 0.3, end=UP * 0.3, color=YELLOW).move_to(
                gauge_bg.get_left() + RIGHT * 3.75
            )
            self.play(
                Create(gauge_bg),
                Create(gauge_fill),
                Create(gauge_needle),
                Create(threshold_mark),
                run_time=tracker.duration * 0.1,
            )

            # Policy lever
            policy_text = Text(
                "Policy Lever: Reduce per-capita burden < 2.0", font_size=24
            ).move_to(UP * 2)
            safe_position(policy_text)
            self.play(Write(policy_text), run_time=tracker.duration * 0.1)

            # Slider
            slider_line = Line(start=LEFT * 3, end=RIGHT * 3, color=WHITE).move_to(
                DOWN * 1
            )
            slider_dot = Dot(radius=0.1, color=BLUE).move_to(slider_line.get_right())
            slider_label = Text("Booster Frequency", font_size=20).next_to(
                slider_line, DOWN
            )
            safe_position(slider_label)
            self.play(
                Create(slider_line),
                FadeIn(slider_dot),
                Write(slider_label),
                run_time=tracker.duration * 0.1,
            )

            # Adjust slider
            self.play(
                slider_dot.animate.move_to(slider_line.get_left() + RIGHT * 1.5),
                gauge_needle.animate.move_to(gauge_bg.get_left() + RIGHT * 2.0),
                gauge_fill.animate.set_width(2.0),
                run_time=tracker.duration * 0.2,
            )

            # Screening
            screening_text = Text("Aggressive Early Screening", font_size=24).move_to(
                DOWN * 2
            )
            safe_position(screening_text)
            self.play(Write(screening_text), run_time=tracker.duration * 0.1)

            # Trajectory forks
            no_intervention = (
                VMobject()
                .set_points_as_corners(
                    [LEFT * 2 + UP * 1, ORIGIN + UP * 1, RIGHT * 2 + UP * 2]
                )
                .set_stroke(RED, 3)
            )
            intervention = (
                VMobject()
                .set_points_as_corners(
                    [LEFT * 2 + DOWN * 1, ORIGIN + DOWN * 1, RIGHT * 2 + DOWN * 0.5]
                )
                .set_stroke(GREEN, 3)
            )
            no_label = Text("No Intervention", font_size=20).next_to(
                no_intervention, RIGHT
            )
            int_label = Text("Threshold-Aware Intervention", font_size=20).next_to(
                intervention, RIGHT
            )
            safe_position(no_label)
            safe_position(int_label)
            self.play(
                Create(no_intervention),
                Create(intervention),
                Write(no_label),
                Write(int_label),
                run_time=tracker.duration * 0.2,
            )

            # Final text
            final_text = Text(
                "Self-sustaining regime requires active intervention", font_size=22
            ).move_to(ORIGIN)
            safe_position(final_text)
            self.play(Write(final_text), run_time=tracker.duration * 0.1)
