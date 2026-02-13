import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

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
from flaming_horse_voice import get_speech_service

# ── Import Shared Configuration ────────────────────────────────────
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
class Scene05AgeInversion(VoiceoverScene):
    def construct(self):
        # Cached Qwen voiceover (precache required)
        self.set_speech_service(get_speech_service(Path(__file__).resolve().parent))

        # ── Animation Sequence ─────────────────────────────────────
        # Timing budget: 0.1 + 0.1 + 0.2 + 0.1 + 0.2 + 0.3 = 1.0 ✓

        with self.voiceover(text=SCRIPT["age_inversion"]) as tracker:
            # Projection graphs
            axes1 = Axes(x_range=[2025, 2028, 1], y_range=[0, 100, 20]).move_to(
                LEFT * 3
            )
            label1 = Text("Standard Model Prediction", font_size=20).next_to(axes1, UP)
            safe_position(label1)
            standard_points = [
                axes1.coords_to_point(x, y)
                for x, y in [(2025, 30), (2026, 35), (2027, 40), (2028, 45)]
            ]
            standard_line = (
                VMobject().set_points_as_corners(standard_points).set_stroke(BLUE, 3)
            )

            axes2 = Axes(x_range=[2025, 2028, 1], y_range=[0, 100, 20]).move_to(
                RIGHT * 3
            )
            label2 = Text("Threshold Model Prediction", font_size=20).next_to(axes2, UP)
            safe_position(label2)
            threshold_points = [
                axes2.coords_to_point(x, y)
                for x, y in [(2025, 40), (2026, 50), (2027, 65), (2028, 80)]
            ]
            threshold_line = (
                VMobject().set_points_as_corners(threshold_points).set_stroke(RED, 3)
            )

            self.play(
                Create(axes1),
                Create(axes2),
                Write(label1),
                Write(label2),
                run_time=tracker.duration * 0.1,
            )
            self.play(
                Create(standard_line),
                Create(threshold_line),
                run_time=tracker.duration * 0.1,
            )

            # Cancer type bars
            immune_sensitive = Rectangle(width=1, height=3, color=RED).move_to(
                LEFT * 3 + DOWN * 2
            )
            immune_evasive = Rectangle(width=1, height=1, color=BLUE).move_to(
                RIGHT * 3 + DOWN * 2
            )
            sensitive_label = Text("Immune-Sensitive Cancers", font_size=20).next_to(
                immune_sensitive, DOWN
            )
            evasive_label = Text("Immune-Evasive Cancers", font_size=20).next_to(
                immune_evasive, DOWN
            )
            safe_position(sensitive_label)
            safe_position(evasive_label)

            self.play(
                Create(immune_sensitive),
                Create(immune_evasive),
                Write(sensitive_label),
                Write(evasive_label),
                run_time=tracker.duration * 0.2,
            )

            # Divergence
            immune_sensitive2 = Rectangle(width=1, height=5, color=RED).move_to(
                LEFT * 3 + DOWN * 2
            )
            immune_evasive2 = Rectangle(width=1, height=1.5, color=BLUE).move_to(
                RIGHT * 3 + DOWN * 2
            )
            self.play(
                Transform(immune_sensitive, immune_sensitive2),
                Transform(immune_evasive, immune_evasive2),
                run_time=tracker.duration * 0.1,
            )

            # Data
            data_text = Text(
                "Melanoma <50: Stable to +3% annually\nLymphomas: Disproportionate acceleration noted",
                font_size=18,
            ).move_to(ORIGIN + DOWN * 3)
            safe_position(data_text)
            self.play(Write(data_text), run_time=tracker.duration * 0.2)
            self.wait(tracker.duration * 0.3)