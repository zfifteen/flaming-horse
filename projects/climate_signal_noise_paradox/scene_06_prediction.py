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
class Scene06Prediction(VoiceoverScene):
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
        # Timing budget: title 0.06 + prediction_a 0.30 + arrow 0.08 + prediction_b 0.30 + converse 0.16 + wait 0.10 = 1.0

        with self.voiceover(text=SCRIPT["prediction"]) as tracker:
            # Title
            title = Text(
                "The Falsifiable Prediction",
                font_size=44,
                weight=BOLD,
                color=YELLOW,
            )
            title.move_to(UP * 3.8)
            self.play(Write(title), run_time=tracker.duration * 0.06)

            # Prediction A: Resolve paradox -> reduces warming bias
            pred_a_box = RoundedRectangle(
                width=6.5,
                height=2.2,
                corner_radius=0.3,
                fill_color=GREEN_E,
                fill_opacity=0.4,
                stroke_color=GREEN,
                stroke_width=3,
            )
            pred_a_box.move_to(LEFT * 0.0 + UP * 1.8)

            pred_a_header = Text("Prediction A", font_size=22, color=GREEN, weight=BOLD)
            pred_a_header.move_to(pred_a_box.get_top() + DOWN * 0.35)

            pred_a_line1 = Text(
                "Resolve S/N paradox for winter NAO",
                font_size=18,
                color=WHITE,
            )
            pred_a_line1.move_to(pred_a_box.get_center() + UP * 0.1)

            pred_a_line2 = Text(
                "ensemble cross-corr matches model-obs corr",
                font_size=16,
                color=GRAY_B,
            )
            pred_a_line2.next_to(pred_a_line1, DOWN, buff=0.15)
            safe_position(pred_a_line2)

            self.play(
                FadeIn(pred_a_box),
                Write(pred_a_header),
                Write(pred_a_line1),
                Write(pred_a_line2),
                run_time=tracker.duration * 0.15,
            )

            # Result arrow
            result_arrow = Arrow(
                pred_a_box.get_bottom(),
                pred_a_box.get_bottom() + DOWN * 1.2,
                color=GREEN,
                stroke_width=5,
            )
            result_text = Text(
                "Tropical warming bias\nreduced by at least 40%",
                font_size=22,
                color=GREEN,
                weight=BOLD,
            )
            result_text.next_to(result_arrow, DOWN, buff=0.2)
            safe_position(result_text)

            no_tuning = Text(
                "WITHOUT any additional tuning",
                font_size=18,
                color=YELLOW,
            )
            no_tuning.next_to(result_text, DOWN, buff=0.2)
            safe_position(no_tuning)

            self.play(
                GrowArrow(result_arrow),
                Write(result_text),
                run_time=tracker.duration * 0.15,
            )

            self.play(
                Write(no_tuning),
                run_time=tracker.duration * 0.08,
            )

            # Fade and show converse
            self.play(
                FadeOut(pred_a_box),
                FadeOut(pred_a_header),
                FadeOut(pred_a_line1),
                FadeOut(pred_a_line2),
                FadeOut(result_arrow),
                FadeOut(result_text),
                FadeOut(no_tuning),
                run_time=tracker.duration * 0.06,
            )

            # Converse prediction
            conv_box = RoundedRectangle(
                width=7.5,
                height=3.5,
                corner_radius=0.3,
                fill_color=RED_E,
                fill_opacity=0.4,
                stroke_color=RED,
                stroke_width=3,
            )
            conv_box.move_to(DOWN * 0.3)

            conv_header = Text("Conversely", font_size=24, color=RED_B, weight=BOLD)
            conv_header.move_to(conv_box.get_top() + DOWN * 0.4)

            conv_line1 = Text(
                "If a model closes the tropical hotspot gap",
                font_size=20,
                color=WHITE,
            )
            conv_line1.move_to(conv_box.get_center() + UP * 0.4)

            conv_line2 = Text(
                "through ECS reduction alone",
                font_size=18,
                color=RED_C,
            )
            conv_line2.next_to(conv_line1, DOWN, buff=0.2)

            conv_line3 = Text(
                "but retains the signal-to-noise paradox...",
                font_size=18,
                color=RED_C,
            )
            conv_line3.next_to(conv_line2, DOWN, buff=0.2)

            conv_result = Text(
                "It has NOT fixed the underlying problem",
                font_size=22,
                color=RED,
                weight=BOLD,
            )
            conv_result.next_to(conv_line3, DOWN, buff=0.3)
            safe_position(conv_result)

            fail_label = Text(
                "Will fail at a different diagnostic",
                font_size=18,
                color=YELLOW,
            )
            fail_label.next_to(conv_result, DOWN, buff=0.15)
            safe_position(fail_label)

            self.play(
                FadeIn(conv_box),
                Write(conv_header),
                run_time=tracker.duration * 0.04,
            )
            self.play(
                Write(conv_line1),
                Write(conv_line2),
                Write(conv_line3),
                run_time=tracker.duration * 0.18,
            )
            self.play(
                Write(conv_result),
                Write(fail_label),
                run_time=tracker.duration * 0.18,
            )

            self.wait(tracker.duration * 0.10)
